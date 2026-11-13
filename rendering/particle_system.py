from __future__ import annotations

import math
from dataclasses import dataclass

import moderngl
import numpy as np

from generators.catalog import normalize_settings

_FULLSCREEN_VERTEX = """#version 330
in vec2 in_position;
in vec2 in_uv;
out vec2 v_uv;
void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

_SIMULATION_FRAGMENT = """#version 330
uniform sampler2D u_state;
uniform sampler2D u_metadata;
uniform sampler2D u_target;
uniform sampler2D u_emitter_source;
uniform sampler2D u_path_points;
uniform vec2 u_state_size;
uniform int u_particle_count;
uniform float u_delta;
uniform float u_time;
uniform int u_seed;
uniform int u_emitter_type;
uniform vec2 u_emitter_center;
uniform float u_emitter_radius;
uniform vec2 u_emitter_size;
uniform int u_direction;
uniform float u_lifetime;
uniform float u_emission_rate;
uniform float u_speed;
uniform float u_spread;
uniform vec2 u_acceleration;
uniform float u_turbulence;
uniform float u_turbulence_scale;
uniform int u_force_type;
uniform vec2 u_force_center;
uniform float u_force_strength;
uniform float u_force_radius;
uniform float u_drag;
uniform int u_source_enabled;
uniform int u_source_map_mode;
uniform float u_emitter_threshold;
uniform int u_emitter_sample_attempts;
uniform float u_emitter_sample_interval;
uniform int u_path_point_count;
uniform float u_reform_strength;
uniform vec2 u_source_texel_size;
uniform vec2 u_emitter_source_position;
uniform vec2 u_emitter_source_scale;
uniform float u_emitter_source_rotation;

// Keep the fullscreen quad UV attribute active in this program. The shared
// VBO/VAO binds both in_position and in_uv; using v_uv here prevents the GLSL
// linker from optimizing in_uv out before ModernGL creates the simulation VAO.
in vec2 v_uv;

layout(location = 0) out vec4 out_state;
layout(location = 1) out vec4 out_metadata;
layout(location = 2) out vec4 out_target;

uint hash_u32(uint value) {
    value ^= value >> 16;
    value *= 0x7feb352du;
    value ^= value >> 15;
    value *= 0x846ca68bu;
    value ^= value >> 16;
    return value;
}

float random_value(uint value) {
    return float(hash_u32(value) & 0x00ffffffu) / 16777216.0;
}

vec2 random_pair(uint value) {
    return vec2(
        random_value(value ^ 0x9e3779b9u),
        random_value(value ^ 0x85ebca6bu)
    );
}

vec2 sample_path(float amount) {
    float scaled = clamp(amount, 0.0, 1.0)
        * float(max(1, u_path_point_count - 1));
    int first_index = int(floor(scaled));
    int second_index = min(first_index + 1, u_path_point_count - 1);
    vec2 first_point = texture(
        u_path_points,
        vec2((float(first_index) + 0.5) / float(u_path_point_count), 0.5)
    ).rg;
    vec2 second_point = texture(
        u_path_points,
        vec2((float(second_index) + 0.5) / float(u_path_point_count), 0.5)
    ).rg;
    return mix(first_point, second_point, fract(scaled));
}

float source_signal(vec2 position) {
    vec2 source_uv = vec2(position.x, 1.0 - position.y);
    vec4 sample_color = texture(u_emitter_source, source_uv);
    if (u_source_map_mode == 1) {
        return sample_color.a;
    }
    float center_luma = dot(
        sample_color.rgb, vec3(0.2126, 0.7152, 0.0722)
    );
    if (u_source_map_mode == 2) {
        vec2 texel = max(u_source_texel_size, vec2(0.0001));
        float left_luma = dot(
            texture(
                u_emitter_source,
                clamp(source_uv - vec2(texel.x, 0.0), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float right_luma = dot(
            texture(
                u_emitter_source,
                clamp(source_uv + vec2(texel.x, 0.0), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float down_luma = dot(
            texture(
                u_emitter_source,
                clamp(source_uv - vec2(0.0, texel.y), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float up_luma = dot(
            texture(
                u_emitter_source,
                clamp(source_uv + vec2(0.0, texel.y), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        return clamp(
            length(vec2(right_luma - left_luma, up_luma - down_luma)) * 2.5,
            0.0,
            1.0
        );
    }
    return center_luma;
}

vec2 source_to_canvas(vec2 source_position) {
    vec2 local = (source_position - vec2(0.5)) * u_emitter_source_scale;
    float angle = radians(u_emitter_source_rotation);
    float c = cos(angle);
    float s = sin(angle);
    vec2 rotated = vec2(
        c * local.x - s * local.y,
        s * local.x + c * local.y
    );
    return u_emitter_source_position + rotated;
}

vec3 sample_source_target(uint key) {
    float best_signal = -1.0;
    vec2 best_position = u_emitter_center;
    for (int attempt = 0; attempt < 16; attempt++) {
        if (attempt >= u_emitter_sample_attempts) break;
        vec2 candidate = random_pair(
            key ^ uint(attempt + 1) * 0x27d4eb2du
        );
        float signal = source_signal(candidate);
        if (signal > best_signal) {
            best_signal = signal;
            best_position = candidate;
        }
        if (signal >= u_emitter_threshold) {
            best_position = candidate;
            best_signal = signal;
            break;
        }
    }
    float active = step(u_emitter_threshold, best_signal);
    return vec3(source_to_canvas(best_position), active);
}

void main() {
    ivec2 pixel = ivec2(gl_FragCoord.xy);
    int particle_index = pixel.y * int(u_state_size.x) + pixel.x;
    if (particle_index >= u_particle_count) {
        out_state = vec4(0.0);
        out_metadata = vec4(0.0);
        out_target = vec4(0.0);
        return;
    }

    // The fullscreen quad interpolates texel-centre UVs over this state target.
    // gl_FragCoord remains the integer particle index; v_uv is for texture reads.
    vec2 uv = v_uv;
    vec4 state = texture(u_state, uv);
    vec4 metadata = texture(u_metadata, uv);
    vec4 target_data = texture(u_target, uv);
    vec2 target_position = target_data.xy;
    float target_strength = target_data.z;
    float sample_phase = target_data.w;
    float age = metadata.x;
    float lifetime = metadata.y;
    float cycle = metadata.z;
    float size_variation = metadata.w;

    if (age >= lifetime || lifetime <= 0.0) {
        // Births are distributed over time instead of starting as one synchronized
        // burst. The rate is global to the system and divided across populations.
        uint emission_tick = uint(floor(u_time * 60.0 + 0.5));
        uint emission_key = uint(particle_index) * 0x9e3779b9u
            ^ emission_tick * 0x85ebca6bu ^ uint(u_seed);
        float spawn_probability = clamp(
            u_emission_rate * u_delta / max(float(u_particle_count), 1.0),
            0.0, 1.0
        );
        if (random_value(emission_key) >= spawn_probability) {
            age = max(age, lifetime);
            out_state = state;
            out_metadata = vec4(age, lifetime, cycle, size_variation);
            out_target = vec4(target_position, target_strength, sample_phase);
            return;
        }
        cycle += 1.0;
        uint key = uint(particle_index) * 0x9e3779b9u
            ^ uint(cycle) * 0x85ebca6bu ^ uint(u_seed);
        vec2 random_a = random_pair(key);
        vec2 random_b = random_pair(key ^ 0x68bc21ebu);
        vec2 position = u_emitter_center;
        vec2 path_tangent = vec2(0.0, 1.0);
        target_strength = 0.0;

        if (u_emitter_type == 1) {
            float angle = random_a.x * 6.2831853;
            position += vec2(cos(angle), sin(angle)) * u_emitter_radius;
        } else if (u_emitter_type == 2) {
            position += (random_a - vec2(0.5)) * u_emitter_size;
        } else if (u_emitter_type == 3 && u_path_point_count >= 2) {
            position = sample_path(random_a.x);
            vec2 before = sample_path(max(0.0, random_a.x - 0.01));
            vec2 after = sample_path(min(1.0, random_a.x + 0.01));
            vec2 tangent_delta = after - before;
            if (length(tangent_delta) > 0.0001) {
                path_tangent = normalize(tangent_delta);
            }
        } else if (u_emitter_type >= 4 && u_emitter_type <= 6
                && u_source_enabled == 1) {
            vec3 sampled_target = sample_source_target(key);
            position = sampled_target.xy;
            target_strength = sampled_target.z;
            if (target_strength < 0.5) {
                position = u_emitter_center;
                age = lifetime;
            }
        }

        target_position = position;
        sample_phase = floor(u_time / max(u_emitter_sample_interval, 0.1));
        vec2 radial = position - u_emitter_center;
        float angle = random_b.x * 6.2831853;
        vec2 random_direction = vec2(cos(angle), sin(angle));
        vec2 direction = random_direction;
        if (u_direction == 0) {
            direction = length(radial) > 0.0001 ? normalize(radial) : random_direction;
        } else if (u_direction == 2) {
            direction = vec2(0.0, 1.0);
        } else if (u_direction == 3) {
            direction = vec2(0.0, -1.0);
        } else if (u_direction == 4) {
            direction = vec2(-1.0, 0.0);
        } else if (u_direction == 5) {
            direction = vec2(1.0, 0.0);
        } else if (u_direction == 6 && u_emitter_type == 3) {
            direction = path_tangent;
        }

        vec2 velocity = direction * u_speed
            + (random_a - vec2(0.5)) * u_spread;
        float life_factor = 0.75 + random_b.y * 0.5;
        age = 0.0;
        lifetime = max(0.05, u_lifetime * life_factor);
        if (u_emitter_type >= 4 && u_emitter_type <= 6
                && target_strength < 0.5) {
            age = lifetime;
        }
        size_variation = random_value(key ^ 0x02e5be93u);
        state = vec4(position, velocity);
    } else {
        vec2 position = state.xy;
        vec2 velocity = state.zw;
        vec2 acceleration = u_acceleration;
        if (u_source_enabled == 1 && u_reform_strength > 0.0001) {
            float next_sample_phase = floor(
                u_time / max(u_emitter_sample_interval, 0.1)
            );
            if (next_sample_phase != sample_phase) {
                uint sample_key = uint(particle_index) * 0x9e3779b9u
                    ^ uint(cycle) * 0x85ebca6bu ^ uint(u_seed)
                    ^ uint(next_sample_phase) * 0xc2b2ae35u;
                vec3 sampled_target = sample_source_target(sample_key);
                target_position = sampled_target.xy;
                target_strength = sampled_target.z;
                sample_phase = next_sample_phase;
            }
        }
        if (u_reform_strength > 0.0001 && target_strength > 0.5) {
            acceleration += (target_position - position) * u_reform_strength;
        }

        if (u_turbulence > 0.0001) {
            float frequency = max(0.1, u_turbulence_scale);
            vec2 flow = vec2(
                sin(position.y * frequency * 6.2831853 + u_time * 1.7 + cycle),
                cos(position.x * frequency * 6.2831853 - u_time * 1.3 + cycle * 0.73)
            );
            acceleration += flow * u_turbulence;
        }

        if (u_force_type != 0 && u_force_strength > 0.0001) {
            vec2 delta = u_force_center - position;
            float distance_to_center = max(length(delta), 0.0001);
            float falloff = 1.0 - smoothstep(
                0.0,
                max(0.001, u_force_radius),
                distance_to_center
            );
            vec2 radial = delta / distance_to_center;
            if (u_force_type == 2) {
                radial = -radial;
            } else if (u_force_type == 3) {
                radial = vec2(-radial.y, radial.x);
            }
            acceleration += radial * u_force_strength * falloff;
        }

        velocity += acceleration * u_delta;
        velocity *= exp(-u_drag * u_delta);
        position += velocity * u_delta;
        age += u_delta;
        if (position.x < -0.25 || position.x > 1.25
                || position.y < -0.25 || position.y > 1.25) {
            age = lifetime;
        }
        state = vec4(position, velocity);
    }

    out_state = state;
    out_metadata = vec4(age, lifetime, cycle, size_variation);
    out_target = vec4(target_position, target_strength, sample_phase);
}
"""

_PARTICLE_VERTEX = """#version 330
uniform sampler2D u_state;
uniform sampler2D u_metadata;
uniform vec2 u_state_size;
uniform vec2 u_output_size;
uniform float u_particle_size;
uniform float u_population_scale;
uniform int u_size_curve;
uniform vec3 u_primary_color;
uniform vec3 u_secondary_color;

out vec2 v_quad_uv;
out vec3 v_color;
out float v_alpha;

const vec2 QUAD[4] = vec2[4](
    vec2(-1.0, -1.0),
    vec2( 1.0, -1.0),
    vec2(-1.0,  1.0),
    vec2( 1.0,  1.0)
);

void main() {
    int index = gl_InstanceID;
    int width = int(u_state_size.x);
    ivec2 pixel = ivec2(index % width, index / width);
    vec2 uv = (vec2(pixel) + vec2(0.5)) / u_state_size;
    vec4 state = texture(u_state, uv);
    vec4 metadata = texture(u_metadata, uv);
    float life = clamp(metadata.x / max(metadata.y, 0.0001), 0.0, 1.0);

    float size_curve = 1.0;
    if (u_size_curve == 1) {
        size_curve = smoothstep(0.0, 1.0, life);
    } else if (u_size_curve == 2) {
        size_curve = 1.0 - smoothstep(0.0, 1.0, life);
    } else if (u_size_curve == 3) {
        size_curve = 0.35 + 0.65 * (0.5 + 0.5 * sin(life * 6.2831853));
    }

    float radius = max(0.5, u_particle_size * u_population_scale
        * (0.65 + metadata.w * 0.7) * size_curve);
    vec2 corner = QUAD[gl_VertexID];
    vec2 clip_offset = corner * (2.0 * radius / max(u_output_size, vec2(1.0)));
    // Match the compositor's top-left source-texture sampling convention.
    vec2 clip_position = vec2(state.x * 2.0 - 1.0, 1.0 - state.y * 2.0);
    gl_Position = vec4(clip_position + clip_offset, 0.0, 1.0);
    v_quad_uv = corner * 0.5 + 0.5;

    float color_mix = fract(metadata.w * 0.73 + float(index % 13) * 0.037);
    v_color = mix(u_primary_color, u_secondary_color, color_mix);
    float fade_in = smoothstep(0.0, 0.08, life);
    float fade_out = 1.0 - smoothstep(0.72, 1.0, life);
    v_alpha = fade_in * fade_out;
}
"""

_PARTICLE_FRAGMENT = """#version 330
in vec2 v_quad_uv;
in vec3 v_color;
in float v_alpha;
out vec4 frag_color;

void main() {
    float radius = length(v_quad_uv - vec2(0.5)) * 2.0;
    float core = 1.0 - smoothstep(0.72, 1.0, radius);
    float halo = exp(-radius * 5.0) * 0.16;
    float alpha = clamp(max(core, halo) * v_alpha, 0.0, 1.0);
    if (alpha <= 0.001) {
        discard;
    }
    frag_color = vec4(v_color, alpha);
}
"""

_TRAIL_FRAGMENT = """#version 330
uniform sampler2D u_previous;
uniform float u_decay;
in vec2 v_uv;
out vec4 frag_color;

void main() {
    frag_color = texture(u_previous, v_uv) * u_decay;
}
"""


@dataclass
class _Population:
    count: int
    seed: int
    states: list[moderngl.Texture]
    metadata: list[moderngl.Texture]
    targets: list[moderngl.Texture]
    framebuffers: list[moderngl.Framebuffer]
    state_size: tuple[int, int]
    index: int = 0

    def release(self) -> None:
        for framebuffer in self.framebuffers:
            framebuffer.release()
        for texture in self.states + self.metadata + self.targets:
            texture.release()


class ParticleSystem2:
    """Deterministic GPU particle simulation with a strict bounded resource budget."""

    MAX_PARTICLES_PER_SYSTEM = 8192
    MAX_POPULATIONS = 4
    SIMULATION_WIDTH = 128
    FIXED_STEP = 1.0 / 60.0
    MAX_SUBSTEPS = 4
    OUTPUT_SCALE = 0.5

    def __init__(self, context: moderngl.Context, vertex_buffer: moderngl.Buffer) -> None:
        self.ctx = context
        self.simulation_program = context.program(
            vertex_shader=_FULLSCREEN_VERTEX,
            fragment_shader=_SIMULATION_FRAGMENT,
        )
        self.particle_program = context.program(
            vertex_shader=_PARTICLE_VERTEX,
            fragment_shader=_PARTICLE_FRAGMENT,
        )
        self.trail_program = context.program(
            vertex_shader=_FULLSCREEN_VERTEX,
            fragment_shader=_TRAIL_FRAGMENT,
        )
        self.simulation_vao = context.vertex_array(
            self.simulation_program,
            [(vertex_buffer, "2f 2f", "in_position", "in_uv")],
        )
        self.trail_vao = context.vertex_array(
            self.trail_program,
            [(vertex_buffer, "2f 2f", "in_position", "in_uv")],
        )
        self.particle_vao = context.vertex_array(self.particle_program, [])
        self.simulation_program["u_state"].value = 0
        self.simulation_program["u_metadata"].value = 1
        self.simulation_program["u_target"].value = 2
        self.simulation_program["u_emitter_source"].value = 3
        self.simulation_program["u_path_points"].value = 4
        self.particle_program["u_state"].value = 0
        self.particle_program["u_metadata"].value = 1
        self.trail_program["u_previous"].value = 0

        self.populations: list[_Population] = []
        self.emitter_stub = context.texture(
            (1, 1), 4, bytes((0, 0, 0, 0)), alignment=1, dtype="f1"
        )
        self.emitter_stub.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.path_stub = context.texture(
            (1, 1),
            2,
            np.asarray([[0.5, 0.5]], dtype=np.float32).tobytes(),
            alignment=1,
            dtype="f4",
        )
        self.path_stub.filter = (moderngl.NEAREST, moderngl.NEAREST)
        self.path_texture: moderngl.Texture | None = None
        self.path_signature: tuple[tuple[float, float], ...] | None = None
        self._active_emitter_source: moderngl.Texture | None = None
        self._active_emitter_source_transform = (
            (0.5, 0.5), (1.0, 1.0), 0.0
        )
        self.trail_textures: list[moderngl.Texture] = []
        self.trail_framebuffers: list[moderngl.Framebuffer] = []
        self.output_size = (0, 0)
        self.trail_index = 0
        self.accumulator = 0.0
        self.last_time: float | None = None
        self.signature: tuple[object, ...] | None = None
        self.last_error: str | None = None

    @staticmethod
    def _rgb(value: str) -> tuple[float, float, float]:
        try:
            hex_value = value.lstrip("#")
            if len(hex_value) == 8:
                hex_value = hex_value[:6]
            if len(hex_value) != 6:
                raise ValueError("Expected six-digit colour")
            return tuple(
                int(hex_value[offset:offset + 2], 16) / 255.0
                for offset in (0, 2, 4)
            )
        except (TypeError, ValueError):
            return (0.91, 0.89, 0.84)

    @property
    def texture(self) -> moderngl.Texture | None:
        if not self.trail_textures:
            return None
        return self.trail_textures[self.trail_index]

    def _release_populations(self) -> None:
        for population in self.populations:
            population.release()
        self.populations.clear()

    def _release_trails(self) -> None:
        for framebuffer in self.trail_framebuffers:
            framebuffer.release()
        for texture in self.trail_textures:
            texture.release()
        self.trail_framebuffers.clear()
        self.trail_textures.clear()
        self.output_size = (0, 0)
        self.trail_index = 0

    def _create_population(self, count: int, seed: int) -> _Population:
        width = self.SIMULATION_WIDTH
        height = max(1, math.ceil(count / width))
        size = (width, height)
        state_pixels = np.zeros((height, width, 4), dtype=np.float32)
        metadata_pixels = np.zeros((height, width, 4), dtype=np.float32)
        metadata_pixels[:, :, 0] = 2.0
        metadata_pixels[:, :, 1] = 0.5
        target_pixels = np.zeros((height, width, 4), dtype=np.float32)

        states = [
            self.ctx.texture(size, 4, state_pixels.tobytes(), alignment=1, dtype="f4"),
            self.ctx.texture(size, 4, state_pixels.tobytes(), alignment=1, dtype="f4"),
        ]
        metadata = [
            self.ctx.texture(
                size, 4, metadata_pixels.tobytes(), alignment=1, dtype="f4"
            ),
            self.ctx.texture(
                size, 4, metadata_pixels.tobytes(), alignment=1, dtype="f4"
            ),
        ]
        targets = [
            self.ctx.texture(
                size, 4, target_pixels.tobytes(), alignment=1, dtype="f4"
            ),
            self.ctx.texture(
                size, 4, target_pixels.tobytes(), alignment=1, dtype="f4"
            ),
        ]
        for texture in states + metadata + targets:
            texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            texture.repeat_x = False
            texture.repeat_y = False
        framebuffers = [
            self.ctx.framebuffer(
                color_attachments=[states[i], metadata[i], targets[i]]
            )
            for i in range(2)
        ]
        return _Population(
            count=count,
            seed=seed,
            states=states,
            metadata=metadata,
            targets=targets,
            framebuffers=framebuffers,
            state_size=size,
        )

    def _ensure_path_texture(self, path_points: list[list[float]]) -> None:
        signature = tuple(
            (float(point[0]), float(point[1])) for point in path_points[:64]
        )
        if signature == self.path_signature:
            return
        if self.path_texture is not None:
            self.path_texture.release()
            self.path_texture = None
        if len(signature) >= 2:
            pixels = np.asarray(signature, dtype=np.float32)
            self.path_texture = self.ctx.texture(
                (len(signature), 1),
                2,
                pixels.tobytes(),
                alignment=1,
                dtype="f4",
            )
            self.path_texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
            self.path_texture.repeat_x = False
            self.path_texture.repeat_y = False
        self.path_signature = signature

    def _ensure_populations(
            self,
            particle_count: int,
            population_count: int,
            seed: int,
            emitter_type: str,
            emitter_source_id: str,
            path_signature: tuple[tuple[float, float], ...],
    ) -> None:
        signature = (
            particle_count,
            population_count,
            seed,
            emitter_type,
            emitter_source_id,
            path_signature,
        )
        if self.signature == signature:
            return
        self._release_populations()
        base_count, remainder = divmod(particle_count, population_count)
        for index in range(population_count):
            count = base_count + (1 if index < remainder else 0)
            if count <= 0:
                continue
            population_seed = (seed + index * 104729) % (2 ** 31 - 1)
            self.populations.append(self._create_population(count, population_seed))
        self.signature = signature
        self.accumulator = 0.0
        self.last_time = None
        self.trail_index = 0
        for framebuffer in self.trail_framebuffers:
            framebuffer.clear(0.0, 0.0, 0.0, 0.0)

    def _ensure_trails(self, width: int, height: int) -> None:
        size = (
            max(1, int(round(width * self.OUTPUT_SCALE))),
            max(1, int(round(height * self.OUTPUT_SCALE))),
        )
        if self.output_size == size:
            return
        self._release_trails()
        for _ in range(2):
            texture = self.ctx.texture(size, 4, dtype="f1")
            texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            texture.repeat_x = False
            texture.repeat_y = False
            framebuffer = self.ctx.framebuffer(color_attachments=[texture])
            framebuffer.clear(0.0, 0.0, 0.0, 0.0)
            self.trail_textures.append(texture)
            self.trail_framebuffers.append(framebuffer)
        self.output_size = size
        self.trail_index = 0

    def _simulation_uniforms(
            self,
            population: _Population,
            settings: dict[str, object],
            time_seconds: float,
            delta: float,
            population_index: int,
    ) -> None:
        program = self.simulation_program
        center = tuple(float(value) for value in settings["emitter_center"])
        # Populations receive stable, small emitter offsets so they form distinct
        # streams without requiring duplicated settings or CPU-side particles.
        if len(self.populations) > 1:
            angle = population_index * 6.2831853 / len(self.populations)
            center = (
                max(0.0, min(1.0, center[0] + math.cos(angle) * 0.018)),
                max(0.0, min(1.0, center[1] + math.sin(angle) * 0.018)),
            )
        values = {
            "u_state": 0,
            "u_metadata": 1,
            "u_target": 2,
            "u_emitter_source": 3,
            "u_path_points": 4,
            "u_state_size": tuple(float(value) for value in population.state_size),
            "u_particle_count": population.count,
            "u_delta": float(delta),
            "u_time": float(time_seconds),
            "u_seed": int(population.seed),
            "u_emitter_type": {
                "point": 0,
                "circle": 1,
                "rectangle": 2,
                "path": 3,
                "video_luminance": 4,
                "image_silhouette": 5,
                "contour": 6,
            }.get(str(settings["emitter_type"]), 0),
            "u_source_enabled": int(
                settings["emitter_type"] in {
                    "video_luminance", "image_silhouette", "contour",
                }
                and self._active_emitter_source is not None
            ),
            "u_source_map_mode": (
                2 if settings["emitter_type"] == "contour"
                else {
                    "luminance": 0,
                    "alpha": 1,
                    "contour": 2,
                }.get(str(settings["emitter_map_mode"]), 0)
            ),
            "u_emitter_threshold": float(settings["emitter_threshold"]),
            "u_emitter_sample_attempts": int(settings["emitter_sample_attempts"]),
            "u_emitter_sample_interval": float(settings["emitter_sample_interval"]),
            "u_path_point_count": len(self.path_signature or ()),
            "u_reform_strength": float(settings["reform_strength"]),
            "u_source_texel_size": (
                1.0 / max(1, int(self._active_emitter_source.size[0]))
                if self._active_emitter_source is not None else 1.0,
                1.0 / max(1, int(self._active_emitter_source.size[1]))
                if self._active_emitter_source is not None else 1.0,
            ),
            "u_emitter_source_position": self._active_emitter_source_transform[0],
            "u_emitter_source_scale": self._active_emitter_source_transform[1],
            "u_emitter_source_rotation": self._active_emitter_source_transform[2],
            "u_emitter_center": center,
            "u_emitter_radius": float(settings["emitter_radius"]),
            "u_emitter_size": tuple(float(value) for value in settings["emitter_size"]),
            "u_direction": {
                "radial": 0,
                "random": 1,
                "up": 2,
                "down": 3,
                "left": 4,
                "right": 5,
                "tangent": 6,
            }.get(str(settings["direction"]), 0),
            "u_lifetime": float(settings["lifetime"]),
            "u_emission_rate": (
                float(settings["emission_rate"]) / max(1, len(self.populations))
            ),
            "u_speed": float(settings["speed"]) * (0.78 + population_index * 0.16),
            "u_spread": float(settings["spread"]),
            "u_acceleration": tuple(float(value) for value in settings["acceleration"]),
            "u_turbulence": float(settings["turbulence"]),
            "u_turbulence_scale": float(settings["turbulence_scale"]),
            "u_force_type": {
                "none": 0, "attract": 1, "repel": 2, "orbit": 3,
            }.get(str(settings["force_type"]), 0),
            "u_force_center": tuple(float(value) for value in settings["force_center"]),
            "u_force_strength": float(settings["force_strength"]),
            "u_force_radius": float(settings["force_radius"]),
            "u_drag": float(settings["drag"]),
        }
        for uniform, value in values.items():
            program[uniform].value = value

    def _step(
            self,
            settings: dict[str, object],
            time_seconds: float,
            delta: float,
    ) -> None:
        for index, population in enumerate(self.populations):
            write_index = 1 - population.index
            population.states[population.index].use(location=0)
            population.metadata[population.index].use(location=1)
            population.targets[population.index].use(location=2)
            (self._active_emitter_source or self.emitter_stub).use(location=3)
            (self.path_texture or self.path_stub).use(location=4)
            population.framebuffers[write_index].use()
            self.ctx.viewport = (0, 0, *population.state_size)
            self._simulation_uniforms(population, settings, time_seconds, delta, index)
            self.simulation_vao.render(mode=moderngl.TRIANGLE_STRIP)
            population.index = write_index

    def _draw_population(
            self,
            population: _Population,
            settings: dict[str, object],
            population_index: int,
    ) -> None:
        program = self.particle_program
        population.states[population.index].use(location=0)
        population.metadata[population.index].use(location=1)
        primary = self._rgb(str(settings["primary_color"]))
        secondary = self._rgb(str(settings["secondary_color"]))
        blend = population_index / max(1, len(self.populations) - 1)
        pop_color = tuple(
            primary[channel] * (1.0 - blend) + secondary[channel] * blend
            for channel in range(3)
        )
        accent_color = tuple(
            secondary[channel] * (1.0 - blend) + primary[channel] * blend
            for channel in range(3)
        )
        size_curve = {"constant": 0, "grow": 1, "shrink": 2, "pulse": 3}.get(
            str(settings["size_curve"]), 2
        )
        values = {
            "u_state_size": tuple(float(value) for value in population.state_size),
            "u_output_size": tuple(float(value) for value in self.output_size),
            "u_particle_size": float(settings["particle_size"]) * self.OUTPUT_SCALE,
            "u_population_scale": 0.9 + population_index * 0.12,
            "u_size_curve": size_curve,
            "u_primary_color": pop_color,
            "u_secondary_color": accent_color,
        }
        for uniform, value in values.items():
            program[uniform].value = value
        self.particle_vao.render(
            mode=moderngl.TRIANGLE_STRIP,
            vertices=4,
            instances=population.count,
        )

    def render(
            self,
            settings: dict[str, object],
            width: int,
            height: int,
            time_seconds: float,
            particle_limit: int | None = None,
            emitter_source: moderngl.Texture | None = None,
            emitter_source_transform: tuple[
                                          tuple[float, float], tuple[float, float], float
                                      ] | None = None,
    ) -> moderngl.Texture | None:
        normalized = normalize_settings("particle_system_2", settings)
        requested = int(normalized["particle_count"])
        if particle_limit is not None:
            requested = min(requested, max(0, int(particle_limit)))
        requested = min(requested, self.MAX_PARTICLES_PER_SYSTEM)
        if requested <= 0:
            return None

        self._ensure_path_texture(normalized["path_points"])
        self._active_emitter_source = emitter_source
        self._active_emitter_source_transform = (
                emitter_source_transform
                or ((0.5, 0.5), (1.0, 1.0), 0.0)
        )
        path_signature = self.path_signature or ()
        self._ensure_populations(
            requested,
            min(int(normalized["population_count"]), requested),
            int(normalized["seed"]),
            str(normalized["emitter_type"]),
            str(normalized["emitter_source_id"]),
            path_signature,
        )
        self._ensure_trails(width, height)

        now = max(0.0, float(time_seconds))
        if self.last_time is None:
            frame_delta = self.FIXED_STEP
        else:
            frame_delta = max(0.0, min(0.1, now - self.last_time))
        self.last_time = now
        self.accumulator = min(
            self.accumulator + frame_delta,
            self.FIXED_STEP * self.MAX_SUBSTEPS,
        )
        steps = 0
        while (
                self.accumulator >= self.FIXED_STEP
                and steps < self.MAX_SUBSTEPS
        ):
            self._step(normalized, now - self.accumulator, self.FIXED_STEP)
            self.accumulator -= self.FIXED_STEP
            steps += 1

        next_index = 1 - self.trail_index
        self.trail_framebuffers[next_index].use()
        self.ctx.viewport = (0, 0, *self.output_size)
        normalized_trail = float(normalized["trail"])
        if normalized_trail > 0.0001:
            self.trail_textures[self.trail_index].use(location=0)
            tail_seconds = 0.08 + normalized_trail * 2.4
            decay = math.exp(-max(frame_delta, 1.0 / 240.0) / tail_seconds)
            self.trail_program["u_decay"].value = decay
            self.trail_vao.render(mode=moderngl.TRIANGLE_STRIP)
        else:
            self.trail_framebuffers[next_index].clear(0.0, 0.0, 0.0, 0.0)

        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE_MINUS_SRC_ALPHA,
        )
        try:
            for index, population in enumerate(self.populations):
                self._draw_population(population, normalized, index)
        finally:
            self.ctx.disable(moderngl.BLEND)
        self.trail_index = next_index
        return self.trail_textures[self.trail_index]

    def release(self) -> None:
        self._release_populations()
        self._release_trails()
        self.simulation_vao.release()
        self.particle_vao.release()
        self.trail_vao.release()
        self.simulation_program.release()
        self.particle_program.release()
        self.trail_program.release()
        if self.path_texture is not None:
            self.path_texture.release()
            self.path_texture = None
        self.path_stub.release()
        self.emitter_stub.release()
