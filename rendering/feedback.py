from __future__ import annotations

import moderngl

from effects.settings import EffectSettings

_VERTEX_SHADER = """#version 330
in vec2 in_position;
in vec2 in_uv;
out vec2 v_uv;
void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

_FEEDBACK_FRAGMENT = """#version 330
uniform sampler2D u_current;
uniform sampler2D u_history;
uniform vec2 u_resolution;
uniform float u_time;
uniform int u_history_valid;
uniform float u_feedback_amount;
uniform float u_feedback_decay;
uniform float u_feedback_zoom;
uniform float u_feedback_rotation;
uniform vec2 u_feedback_translation;
uniform float u_feedback_color_shift;
uniform float u_feedback_distortion;
uniform float u_feedback_motion_warp;
uniform float u_feedback_datamosh;
uniform int u_feedback_blend_mode;

in vec2 v_uv;
out vec4 frag_color;

float luma(vec3 color) {
    return dot(color, vec3(0.2126, 0.7152, 0.0722));
}

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void main() {
    vec3 current = texture(u_current, v_uv).rgb;
    if (u_history_valid == 0 || u_feedback_amount <= 0.0001) {
        frag_color = vec4(current, 1.0);
        return;
    }

    vec2 centered = (v_uv - vec2(0.5)) / max(u_feedback_zoom, 0.001);
    float angle = radians(u_feedback_rotation);
    float c = cos(angle);
    float s = sin(angle);
    vec2 history_uv = vec2(
        c * centered.x - s * centered.y,
        s * centered.x + c * centered.y
    ) + vec2(0.5) - u_feedback_translation;

    history_uv += vec2(
        sin(v_uv.y * 28.0 + u_time * 1.7),
        cos(v_uv.x * 24.0 - u_time * 1.3)
    ) * u_feedback_distortion * 0.018;

    if (u_feedback_motion_warp > 0.0001) {
        vec2 texel = 1.0 / max(u_resolution, vec2(1.0));
        float gx = luma(texture(u_history, clamp(history_uv + vec2(texel.x, 0.0), vec2(0.0), vec2(1.0))).rgb)
            - luma(texture(u_history, clamp(history_uv - vec2(texel.x, 0.0), vec2(0.0), vec2(1.0))).rgb);
        float gy = luma(texture(u_history, clamp(history_uv + vec2(0.0, texel.y), vec2(0.0), vec2(1.0))).rgb)
            - luma(texture(u_history, clamp(history_uv - vec2(0.0, texel.y), vec2(0.0), vec2(1.0))).rgb);
        float temporal_delta = luma(current)
            - luma(texture(u_history, clamp(history_uv, vec2(0.0), vec2(1.0))).rgb);
        vec2 direction = normalize(vec2(gx, gy) + vec2(0.00001));
        history_uv += direction * temporal_delta * u_feedback_motion_warp * 0.06;
    }

    if (u_feedback_datamosh > 0.0001) {
        vec2 block = floor(v_uv * vec2(48.0, 27.0));
        float phase = floor(u_time * 3.0);
        float seed = hash21(block + vec2(phase, phase * 0.37));
        float gate = step(1.0 - u_feedback_datamosh * 0.34, seed);
        vec2 offset = vec2(
            hash21(block + vec2(17.0, phase)) - 0.5,
            hash21(block + vec2(phase, 31.0)) - 0.5
        );
        history_uv += offset * gate * u_feedback_datamosh * 0.075;
    }

    history_uv = clamp(history_uv, vec2(0.001), vec2(0.999));
    vec2 chroma = vec2(u_feedback_color_shift * 0.012, 0.0);
    vec3 previous;
    previous.r = texture(u_history, clamp(history_uv + chroma, vec2(0.0), vec2(1.0))).r;
    previous.g = texture(u_history, history_uv).g;
    previous.b = texture(u_history, clamp(history_uv - chroma, vec2(0.0), vec2(1.0))).b;
    previous *= u_feedback_decay;

    vec3 blended = previous;
    if (u_feedback_blend_mode == 1) {
        blended = min(current + previous, vec3(1.0));
    } else if (u_feedback_blend_mode == 2) {
        blended = 1.0 - (1.0 - current) * (1.0 - previous);
    } else if (u_feedback_blend_mode == 3) {
        blended = current * previous;
    } else if (u_feedback_blend_mode == 4) {
        blended = abs(current - previous);
    }

    frag_color = vec4(mix(current, blended, clamp(u_feedback_amount, 0.0, 1.0)), 1.0);
}
"""


class FeedbackEngine:
    """Per-render-context GPU feedback history; no CPU texture readback is performed."""

    HISTORY_LENGTH = 5

    def __init__(self, context: moderngl.Context, vertex_buffer: moderngl.Buffer) -> None:
        self.ctx = context
        self.program = context.program(
            vertex_shader=_VERTEX_SHADER,
            fragment_shader=_FEEDBACK_FRAGMENT,
        )
        self.vao = context.vertex_array(
            self.program,
            [(vertex_buffer, "2f 2f", "in_position", "in_uv")],
        )
        self.program["u_current"].value = 0
        self.program["u_history"].value = 1
        self.textures: list[moderngl.Texture] = []
        self.framebuffers: list[moderngl.Framebuffer] = []
        self.size = (0, 0)
        self.write_index = 0
        self.history_count = 0
        self.reset_generation = -1

    def _release_targets(self) -> None:
        for framebuffer in self.framebuffers:
            framebuffer.release()
        for texture in self.textures:
            texture.release()
        self.framebuffers.clear()
        self.textures.clear()
        self.size = (0, 0)
        self.write_index = 0
        self.history_count = 0

    def resize(self, width: int, height: int, reset_generation: int = 0) -> None:
        size = (max(1, int(width)), max(1, int(height)))
        if self.size == size:
            return
        self._release_targets()
        for _ in range(self.HISTORY_LENGTH):
            texture = self.ctx.texture(size, 4, dtype="f1")
            texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            texture.repeat_x = False
            texture.repeat_y = False
            framebuffer = self.ctx.framebuffer(color_attachments=[texture])
            self.textures.append(texture)
            self.framebuffers.append(framebuffer)
        self.size = size
        self.reset(reset_generation)

    def reset(self, reset_generation: int | None = None) -> None:
        for framebuffer in self.framebuffers:
            framebuffer.use()
            framebuffer.clear(0.0, 0.0, 0.0, 1.0)
        self.write_index = 0
        self.history_count = 0
        if reset_generation is not None:
            self.reset_generation = int(reset_generation)

    def render(
            self,
            current_texture: moderngl.Texture,
            target_fbo: int,
            width: int,
            height: int,
            settings: EffectSettings,
            time_seconds: float,
    ) -> None:
        settings.clamp()
        self.resize(width, height, settings.feedback_reset_generation)
        if settings.feedback_reset_generation != self.reset_generation:
            self.reset(settings.feedback_reset_generation)

        destination = self.ctx.detect_framebuffer(glo=int(target_fbo))
        write_index = self.write_index
        delay = settings.feedback_delay_frames
        read_index = (write_index - 1 - delay) % self.HISTORY_LENGTH
        history_valid = int(self.history_count > delay)
        output = (
            destination
            if settings.feedback_frozen
            else self.framebuffers[write_index]
        )
        output.use()
        self.ctx.viewport = (0, 0, max(1, int(width)), max(1, int(height)))
        current_texture.use(location=0)
        self.textures[read_index].use(location=1)

        values = {
            "u_resolution": (float(width), float(height)),
            "u_time": float(time_seconds),
            "u_history_valid": history_valid,
            "u_feedback_amount": settings.feedback_amount,
            "u_feedback_decay": settings.feedback_decay,
            "u_feedback_zoom": settings.feedback_zoom,
            "u_feedback_rotation": settings.feedback_rotation,
            "u_feedback_translation": (
                settings.feedback_translate_x,
                settings.feedback_translate_y,
            ),
            "u_feedback_color_shift": settings.feedback_color_shift,
            "u_feedback_distortion": settings.feedback_distortion,
            "u_feedback_motion_warp": settings.feedback_motion_warp,
            "u_feedback_datamosh": settings.feedback_datamosh,
            "u_feedback_blend_mode": {
                "normal": 0,
                "add": 1,
                "screen": 2,
                "multiply": 3,
                "difference": 4,
            }.get(settings.feedback_blend_mode, 0),
        }
        for uniform_name, value in values.items():
            self.program[uniform_name].value = value
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)

        if not settings.feedback_frozen:
            self.ctx.copy_framebuffer(destination, output)
            self.write_index = (write_index + 1) % self.HISTORY_LENGTH
            self.history_count = min(self.HISTORY_LENGTH, self.history_count + 1)

    def release(self) -> None:
        self._release_targets()
        self.vao.release()
        self.program.release()
