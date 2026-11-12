from __future__ import annotations

import logging

import moderngl
import numpy as np

from core.composition import Layer
from effects.layer_settings import normalize_layer_effects
from effects.settings import EffectSettings
from generators.catalog import animation_code, normalize_settings, text_animation_code
from rendering.feedback import FeedbackEngine
from rendering.particle_system import ParticleSystem2

_LOG = logging.getLogger(__name__)

_VERTEX_SHADER = """#version 330
in vec2 in_position;
in vec2 in_uv;
out vec2 v_uv;
void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_position, 0.0, 1.0);
}
"""

_COMPOSITE_FRAGMENT = """#version 330
uniform sampler2D u_base;
uniform sampler2D u_layer;
uniform sampler2D u_mask;
uniform int u_mask_enabled;
uniform int u_mask_mode;
uniform vec2 u_position;
uniform vec2 u_scale;
uniform float u_rotation;
uniform float u_opacity;
uniform int u_blend_mode;
uniform vec2 u_canvas_scale;
uniform float u_time;
uniform int u_animation;
uniform float u_animation_speed;
uniform float u_animation_amount;
uniform int u_generator_type;
uniform int u_text_animation;
uniform float u_text_animation_speed;
uniform float u_text_animation_amount;
uniform float u_text_animation_columns;
uniform float u_particle_density;
uniform float u_particle_speed;
uniform float u_particle_size;
uniform float u_particle_spread;
uniform float u_particle_trail;
uniform int u_particle_mode;
uniform vec3 u_particle_primary;
uniform vec3 u_particle_secondary;
uniform int u_layer_fx_enabled;
uniform float u_layer_fx_mix;
uniform float u_layer_fx_monochrome;
uniform float u_layer_fx_invert;
uniform float u_layer_fx_threshold;
uniform float u_layer_fx_posterize;
uniform float u_layer_fx_hue;
uniform float u_layer_fx_saturation;
uniform float u_layer_fx_contrast;
uniform float u_layer_fx_brightness;
uniform float u_layer_fx_scanlines;
uniform float u_layer_fx_chromatic;
uniform int u_fx_stage_count;
uniform int u_fx_stage_type[8];
uniform float u_fx_stage_amount[8];

in vec2 v_uv;
out vec4 frag_color;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

vec4 particle_field(vec2 uv) {
    vec2 grid = vec2(
        max(4.0, u_particle_density),
        max(3.0, u_particle_density * 0.5625)
    );
    vec2 cell = floor(uv * grid);
    vec2 cell_size = 1.0 / grid;
    float alpha = 0.0;
    vec3 particle_color = u_particle_primary;
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 id = cell + vec2(float(x), float(y));
            float seed = hash21(id);
            vec2 jitter = vec2(
                hash21(id + vec2(17.0, 3.0)),
                hash21(id + vec2(7.0, 29.0))
            );
            vec2 point = (id + jitter) / grid;
            float phase = u_time * u_particle_speed * 0.22 + seed * 6.28318;
            if (u_particle_mode == 1) {
                point.y = fract(point.y - phase / 6.28318);
            } else if (u_particle_mode == 2) {
                point.y = fract(point.y + phase / 6.28318);
            } else if (u_particle_mode == 3) {
                point += vec2(cos(phase), sin(phase)) * u_particle_spread * 0.09;
                point = fract(point);
            } else {
                point.y = fract(point.y + sin(phase) * u_particle_spread * 0.08);
                point.x = fract(point.x + cos(phase * 0.7) * u_particle_spread * 0.08);
            }
            float radius = max(cell_size.x, cell_size.y) * u_particle_size * 0.23;
            vec2 delta = uv - point;
            float distance_to_point = length(delta);
            float core = 1.0 - smoothstep(radius * 0.28, radius, distance_to_point);
            float tail = 0.0;
            if (u_particle_trail > 0.001) {
                float along = max(0.0, -delta.y) / max(radius, 0.0001);
                float across = abs(delta.x) / max(radius * 0.34, 0.0001);
                tail = exp(-along * 1.8) * (1.0 - smoothstep(0.5, 1.5, across));
                tail *= smoothstep(0.0, 0.22, along) * u_particle_trail;
            }
            float coverage = max(core, tail);
            if (coverage > alpha) {
                alpha = coverage;
                particle_color = mix(
                    u_particle_primary,
                    u_particle_secondary,
                    step(0.52, seed)
                );
            }
        }
    }
    return vec4(particle_color, clamp(alpha, 0.0, 1.0));
}

vec3 layer_color_effects(vec3 color, vec2 uv) {
    if (u_layer_fx_enabled == 0 || u_layer_fx_mix <= 0.0) {
        return color;
    }
    vec3 original = color;
    if (u_fx_stage_count > 0) {
        for (int i = 0; i < 8; i++) {
            if (i >= u_fx_stage_count) break;
            float amount = clamp(u_fx_stage_amount[i], 0.0, 1.0);
            int stage_type = u_fx_stage_type[i];
            if (stage_type == 1) {
                float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
                color = mix(color, vec3(luma), amount);
            } else if (stage_type == 2) {
                color = mix(color, vec3(1.0) - color, amount);
            } else if (stage_type == 3) {
                float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
                color = mix(color, vec3(step(0.5, luma)), amount);
            } else if (stage_type == 4) {
                float levels = mix(24.0, 2.0, amount);
                color = floor(clamp(color, 0.0, 1.0) * levels) / levels;
            } else if (stage_type == 5) {
                float scan = 0.82 + 0.18 * sin(uv.y * 720.0 * 3.14159265);
                color *= mix(1.0, scan, amount);
            } else if (stage_type == 6) {
                float angle = amount * 6.2831853;
                float luma = dot(color, vec3(0.299, 0.587, 0.114));
                color = vec3(
                    luma + (color.r - luma) * cos(angle) - (color.g - luma) * sin(angle),
                    luma + (color.r - luma) * sin(angle) + (color.g - luma) * cos(angle),
                    color.b
                );
            } else if (stage_type == 7) {
                color = (color - 0.5) * mix(1.0, 2.5, amount) + 0.5;
            } else if (stage_type == 8) {
                float luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
                color = mix(vec3(luma), color, mix(1.0, 2.5, amount));
            } else if (stage_type == 9) {
                color += (amount - 0.5) * 0.5;
            }
        }
    }
    color = (color - 0.5) * u_layer_fx_contrast + 0.5;
    float luminance = dot(color, vec3(0.2126, 0.7152, 0.0722));
    color = mix(color, vec3(luminance), u_layer_fx_monochrome);
    color *= u_layer_fx_saturation;
    color += u_layer_fx_brightness;
    float angle = radians(u_layer_fx_hue);
    float yi = dot(color, vec3(0.596, -0.274, -0.322));
    float yq = dot(color, vec3(0.211, -0.523, 0.312));
    float yy = dot(color, vec3(0.299, 0.587, 0.114));
    float ri = yi * cos(angle) - yq * sin(angle);
    float rq = yi * sin(angle) + yq * cos(angle);
    color = vec3(
        yy + 0.956 * ri + 0.621 * rq,
        yy - 0.272 * ri - 0.647 * rq,
        yy - 1.106 * ri + 1.703 * rq
    );
    float thresholded = step(u_layer_fx_threshold, luminance);
    color = mix(color, vec3(thresholded), u_layer_fx_threshold);
    if (u_layer_fx_posterize > 0.001) {
        float levels = mix(24.0, 2.0, u_layer_fx_posterize);
        color = floor(clamp(color, 0.0, 1.0) * levels) / levels;
    }
    color = mix(color, vec3(1.0) - color, u_layer_fx_invert);
    float scan = 0.82 + 0.18 * sin(uv.y * 720.0 * 3.14159265);
    color *= mix(1.0, scan, u_layer_fx_scanlines);
    return mix(original, clamp(color, 0.0, 1.0), u_layer_fx_mix);
}

void main() {
    vec4 base = texture(u_base, v_uv);
    vec2 canvas_uv = (v_uv - vec2(0.5)) / u_canvas_scale + vec2(0.5);
    if (canvas_uv.x < 0.0 || canvas_uv.x > 1.0
            || canvas_uv.y < 0.0 || canvas_uv.y > 1.0) {
        frag_color = base;
        return;
    }
    vec2 screen_uv = vec2(canvas_uv.x, 1.0 - canvas_uv.y);
    vec2 animated_position = u_position;
    vec2 animated_scale = u_scale;
    float animated_rotation = u_rotation;
    float animated_opacity = u_opacity;
    float phase = u_time * u_animation_speed;

    if (u_animation == 1) {
        animated_scale *= 1.0 + sin(phase) * u_animation_amount;
    } else if (u_animation == 2) {
        animated_rotation += sin(phase) * u_animation_amount;
    } else if (u_animation == 3) {
        animated_position += vec2(sin(phase), cos(phase * 0.83)) * u_animation_amount;
    } else if (u_animation == 4) {
        animated_opacity *= 0.65 + 0.35 * (0.5 + 0.5 * sin(phase * 3.7));
    }

    vec2 local = screen_uv - animated_position;
    float angle = radians(-animated_rotation);
    float c = cos(angle);
    float s = sin(angle);
    local = vec2(c * local.x - s * local.y, s * local.x + c * local.y);
    local = local / max(animated_scale, vec2(0.001)) + vec2(0.5);

    if (local.x < 0.0 || local.x > 1.0 || local.y < 0.0 || local.y > 1.0) {
        frag_color = base;
        return;
    }

    vec2 sample_local = local;
    float text_mask = 1.0;
    // Warp deforms the geometry texture itself, not just its layer transform.
    if (u_generator_type == 3 && u_animation == 5) {
        float warp_phase = u_time * u_animation_speed;
        sample_local.x += sin(local.y * 31.0 + warp_phase * 1.7)
            * u_animation_amount * 0.12;
        sample_local.y += cos(local.x * 27.0 - warp_phase)
            * u_animation_amount * 0.12;
    }
    float text_phase = u_time * u_text_animation_speed;
    if (u_generator_type == 2) {
        if (u_text_animation == 1) {
            float reveal = fract(text_phase * 0.08);
            text_mask = 1.0 - smoothstep(reveal - 0.012, reveal + 0.012, local.x);
        } else if (u_text_animation == 2) {
            float columns = max(2.0, u_text_animation_columns);
            float cell = floor(local.x * columns) / columns;
            float reveal = fract(text_phase * 0.08);
            text_mask = step(cell, reveal);
        } else if (u_text_animation == 3) {
            sample_local.x += sin(local.y * 44.0 + text_phase * 2.0)
                * u_text_animation_amount;
        } else if (u_text_animation == 4) {
            vec2 seed = floor(local * 52.0);
            float jitter = hash21(seed + floor(text_phase * 8.0)) - 0.5;
            sample_local += vec2(jitter, -jitter) * u_text_animation_amount;
        } else if (u_text_animation == 5) {
            sample_local.y = fract(local.y + text_phase * 0.045);
        } else if (u_text_animation == 6) {
            float line = floor(local.y * 45.0);
            float gate = step(0.86, hash21(vec2(line, floor(text_phase * 12.0))));
            sample_local.x += gate * sin(text_phase * 19.0 + line) * u_text_animation_amount;
        } else if (u_text_animation == 7) {
            float reveal = fract(text_phase * 0.08);
            text_mask = smoothstep(
                1.0 - reveal - 0.012, 1.0 - reveal + 0.012, local.x
            );
        } else if (u_text_animation == 8) {
            vec2 grid = vec2(
                max(4.0, u_text_animation_columns),
                max(3.0, u_text_animation_columns * 0.5625)
            );
            float cell_noise = hash21(floor(local * grid));
            float dissolve = fract(text_phase * 0.08);
            text_mask = 1.0 - smoothstep(
                dissolve - 0.035, dissolve + 0.035, cell_noise
            );
        } else if (u_text_animation == 9) {
            vec2 grid = vec2(
                max(4.0, u_text_animation_columns),
                max(3.0, u_text_animation_columns * 0.5625)
            );
            vec2 cell = floor(local * grid);
            float pulse = hash21(cell + floor(text_phase * 12.0));
            text_mask *= mix(0.08, 1.0, step(0.22, pulse));
        } else if (u_text_animation == 10) {
            vec2 grid = vec2(
                max(4.0, u_text_animation_columns),
                max(3.0, u_text_animation_columns * 0.5625)
            );
            vec2 cell = floor(local * grid);
            vec2 random_offset = vec2(
                hash21(cell + 17.0), hash21(cell + 43.0)
            ) - 0.5;
            float phase = sin(text_phase * 2.4 + hash21(cell) * 6.28318);
            sample_local += random_offset * phase * u_text_animation_amount * 0.18;
        } else if (u_text_animation == 11) {
            float reveal = fract(text_phase * 0.08);
            text_mask = 1.0 - smoothstep(
                reveal - 0.012, reveal + 0.012, local.y
            );
        } else if (u_text_animation == 12) {
            vec2 grid = vec2(
                max(4.0, u_text_animation_columns),
                max(3.0, u_text_animation_columns * 0.5625)
            );
            vec2 cell = floor(local * grid);
            vec2 random_offset = vec2(
                hash21(cell + 71.0), hash21(cell + 113.0)
            ) - 0.5;
            float scatter = sin(text_phase * 1.7 + hash21(cell) * 6.28318);
            sample_local += random_offset * scatter * u_text_animation_amount * 0.3;
        } else if (u_text_animation == 13) {
            float segment = floor(local.x * max(4.0, u_text_animation_columns * 0.5));
            float collision = sin(text_phase * 2.0 + segment * 1.37);
            float direction = step(0.5, hash21(vec2(segment, 91.0))) * 2.0 - 1.0;
            sample_local.x += collision * direction * u_text_animation_amount * 0.22;
            sample_local.y += abs(collision) * u_text_animation_amount * 0.06;
        } else if (u_text_animation == 14) {
            float rows = max(8.0, u_text_animation_columns);
            float offset = text_phase * 0.9;
            sample_local.y = fract(floor((local.y + offset) * rows) / rows);
        }
    }

    vec4 source;
    if (u_generator_type == 1) {
        source = particle_field(local);
    } else {
        float rgb_shift_amount = (
            u_layer_fx_chromatic * u_layer_fx_mix * float(u_layer_fx_enabled)
        );
        vec2 rgb_shift = vec2(rgb_shift_amount * 0.012, 0.0);
        vec2 uv_safe = clamp(sample_local, vec2(0.001), vec2(0.999));
        source = texture(u_layer, uv_safe);
        if (u_layer_fx_chromatic > 0.001) {
            source.r = texture(
                u_layer,
                clamp(uv_safe + rgb_shift, vec2(0.001), vec2(0.999))
            ).r;
            source.b = texture(
                u_layer,
                clamp(uv_safe - rgb_shift, vec2(0.001), vec2(0.999))
            ).b;
        }
        if (u_generator_type == 2) {
            source.a *= text_mask;
        }
        if (u_mask_enabled == 1) {
            vec4 matte = texture(u_mask, uv_safe);
            float matte_value = u_mask_mode == 2
                ? dot(matte.rgb, vec3(0.2126, 0.7152, 0.0722))
                : matte.a;
            source.a *= matte_value;
        }
    }
    source.rgb = layer_color_effects(source.rgb, local);
    float alpha = clamp(source.a * animated_opacity, 0.0, 1.0);
    vec3 blended = source.rgb;

    if (u_blend_mode == 1) {
        blended = min(base.rgb + source.rgb, vec3(1.0));
    } else if (u_blend_mode == 2) {
        blended = 1.0 - (1.0 - base.rgb) * (1.0 - source.rgb);
    } else if (u_blend_mode == 3) {
        blended = base.rgb * source.rgb;
    } else if (u_blend_mode == 4) {
        blended = abs(base.rgb - source.rgb);
    }

    frag_color = vec4(mix(base.rgb, blended, alpha), 1.0);
}
"""

_POST_FRAGMENT = """#version 330
uniform sampler2D u_texture;
uniform vec2 u_resolution;
uniform float u_time;
uniform float u_brightness;
uniform float u_exposure;
uniform float u_contrast;
uniform float u_saturation;
uniform float u_gamma;
uniform float u_temperature;
uniform float u_tint;
uniform float u_hue;
uniform float u_vignette;
uniform float u_grain;
uniform float u_scanlines;
uniform float u_chromatic;
uniform float u_glitch;
uniform float u_pixelate;
uniform float u_posterize;
uniform float u_invert;
uniform float u_halftone;
uniform float u_solarize;
uniform float u_mix;
uniform sampler2D u_displacement_map;
uniform int u_displacement_enabled;
uniform int u_displacement_luma;
uniform int u_transform_mode;
uniform float u_transform_mix;
uniform float u_kaleidoscope_slices;
uniform float u_kaleidoscope_rotation;
uniform float u_kaleidoscope_zoom;
uniform float u_mosaic_tiles;
uniform float u_pixel_sort_amount;
uniform float u_pixel_sort_threshold;
uniform float u_edge_amount;
uniform float u_dither;
uniform float u_displacement_amount;
uniform float u_displacement_scale;

in vec2 v_uv;
out vec4 frag_color;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void main() {
    vec2 uv = v_uv;
    float aspect = u_resolution.x / max(u_resolution.y, 1.0);
    if (u_transform_mode == 1) {
        vec2 centered = (uv - vec2(0.5)) * vec2(aspect, 1.0);
        float radius = length(centered) / max(u_kaleidoscope_zoom, 0.01);
        float angle = atan(centered.y, centered.x) - radians(u_kaleidoscope_rotation);
        float slice_angle = 6.2831853 / max(u_kaleidoscope_slices, 2.0);
        angle = abs(mod(angle + slice_angle * 0.5, slice_angle) - slice_angle * 0.5);
        centered = vec2(cos(angle), sin(angle)) * radius;
        uv = vec2(centered.x / max(aspect, 0.001), centered.y) + vec2(0.5);
    } else if (u_transform_mode == 2) {
        vec2 centered = (uv - vec2(0.5)) * vec2(aspect, 1.0);
        float angle = atan(centered.y, centered.x);
        float radius = length(centered) * 1.41421356;
        uv = vec2(fract(angle / 6.2831853 + 0.5), clamp(radius, 0.0, 1.0));
    } else if (u_transform_mode == 3) {
        vec2 grid = vec2(max(4.0, u_mosaic_tiles) * aspect, max(4.0, u_mosaic_tiles));
        uv = (floor(uv * grid) + vec2(0.5)) / grid;
    } else if (u_transform_mode == 4) {
        float source_luma = dot(texture(u_texture, uv).rgb, vec3(0.2126, 0.7152, 0.0722));
        float gate = smoothstep(
            u_pixel_sort_threshold - 0.04,
            u_pixel_sort_threshold + 0.04,
            source_luma
        );
        float row = floor(uv.y * u_resolution.y / 3.0);
        float scan_seed = hash21(vec2(row, floor(u_time * 3.0)));
        uv.x += (scan_seed - 0.5) * u_pixel_sort_amount * 0.18 * gate;
    }
    if (u_displacement_enabled == 1) {
        vec2 map_uv = fract(uv * max(u_displacement_scale, 0.01));
        vec4 map_value = texture(u_displacement_map, map_uv);
        vec2 displacement = map_value.rg * 2.0 - 1.0;
        if (u_displacement_luma == 1) {
            float map_luma = dot(map_value.rgb, vec3(0.2126, 0.7152, 0.0722));
            displacement = vec2(map_luma * 2.0 - 1.0);
        }
        uv += displacement * u_displacement_amount * 0.06;
    }
    uv = clamp(uv, vec2(0.001), vec2(0.999));
    vec3 untransformed_color = texture(u_texture, v_uv).rgb;
    vec3 transformed_color = texture(u_texture, uv).rgb;
    vec3 original_color = mix(
        untransformed_color,
        transformed_color,
        clamp(u_transform_mix, 0.0, 1.0)
    );

    float row_seed = hash21(vec2(floor(uv.y * u_resolution.y), floor(u_time * 19.0)));
    float glitch_gate = step(0.986, row_seed) * u_glitch;
    uv.x += (row_seed - 0.5) * 0.045 * glitch_gate;

    float pixel_size = mix(1.0, 30.0, clamp(u_pixelate, 0.0, 1.0));
    uv = floor(uv * u_resolution / pixel_size) * pixel_size / u_resolution;
    uv = clamp(uv, vec2(0.001), vec2(0.999));

    vec2 split = vec2(u_chromatic * 0.009 + glitch_gate * 0.012, 0.0);
    vec3 color;
    color.r = texture(u_texture, clamp(uv + split, vec2(0.0), vec2(1.0))).r;
    color.g = texture(u_texture, uv).g;
    color.b = texture(u_texture, clamp(uv - split, vec2(0.0), vec2(1.0))).b;

    color = (color - 0.5) * u_contrast + 0.5;
    float luminance = dot(color, vec3(0.2126, 0.7152, 0.0722));
    color = mix(vec3(luminance), color, u_saturation);
    color *= exp2(u_exposure);
    color = pow(max(color, vec3(0.0)), vec3(1.0 / max(u_gamma, 0.05)));
    color += u_brightness;

    // Simple white-balance controls. Positive temperature warms highlights;
    // positive tint adds magenta, while negative tint leans green.
    color += vec3(
        u_temperature * 0.12 + u_tint * 0.035,
        u_tint * 0.10,
        -u_temperature * 0.12 + u_tint * 0.035
    );

    // Rotate hue in YIQ space while preserving approximate luminance.
    float hue_angle = radians(u_hue);
    float yiq_y = dot(color, vec3(0.299, 0.587, 0.114));
    float yiq_i = dot(color, vec3(0.596, -0.274, -0.322));
    float yiq_q = dot(color, vec3(0.211, -0.523, 0.312));
    float rotated_i = yiq_i * cos(hue_angle) - yiq_q * sin(hue_angle);
    float rotated_q = yiq_i * sin(hue_angle) + yiq_q * cos(hue_angle);
    color = vec3(
        yiq_y + 0.956 * rotated_i + 0.621 * rotated_q,
        yiq_y - 0.272 * rotated_i - 0.647 * rotated_q,
        yiq_y - 1.106 * rotated_i + 1.703 * rotated_q
    );

    if (u_posterize > 0.001 || u_dither > 0.001) {
        float levels = mix(24.0, 3.0, clamp(u_posterize, 0.0, 1.0));
        vec2 ordered_cell = mod(floor(gl_FragCoord.xy), 4.0);
        float ordered_rank = mod(
            ordered_cell.x * 2.0 + ordered_cell.y * 3.0
                + ordered_cell.x * ordered_cell.y * 5.0,
            16.0
        ) / 16.0;
        float dither_offset = (ordered_rank - 0.5) * u_dither / levels;
        color = floor(clamp(color + dither_offset, 0.0, 1.0) * levels) / levels;
    }
    if (u_edge_amount > 0.001) {
        vec2 pixel = 1.0 / max(u_resolution, vec2(1.0));
        float left_luma = dot(
            texture(
                u_texture,
                clamp(uv - vec2(pixel.x, 0.0), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float right_luma = dot(
            texture(
                u_texture,
                clamp(uv + vec2(pixel.x, 0.0), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float down_luma = dot(
            texture(
                u_texture,
                clamp(uv - vec2(0.0, pixel.y), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float up_luma = dot(
            texture(
                u_texture,
                clamp(uv + vec2(0.0, pixel.y), vec2(0.0), vec2(1.0))
            ).rgb,
            vec3(0.2126, 0.7152, 0.0722)
        );
        float edge_value = clamp(
            length(vec2(right_luma - left_luma, up_luma - down_luma)) * 2.4,
            0.0,
            1.0
        );
        color = mix(color, vec3(edge_value), u_edge_amount);
    }
    color = mix(color, vec3(1.0) - color, clamp(u_invert, 0.0, 1.0));

    float solar_luma = dot(color, vec3(0.2126, 0.7152, 0.0722));
    vec3 solarized = mix(color, vec3(1.0) - color, step(0.58, solar_luma));
    color = mix(color, solarized, clamp(u_solarize, 0.0, 1.0));

    vec2 screen_cells = v_uv * u_resolution / 7.0;
    vec2 screen_dot = fract(screen_cells) - 0.5;
    float print_luma = dot(clamp(color, 0.0, 1.0), vec3(0.2126, 0.7152, 0.0722));
    float dot_radius = mix(0.07, 0.48, print_luma);
    float dot_coverage = 1.0 - smoothstep(
        dot_radius,
        dot_radius + 0.035,
        length(screen_dot)
    );
    color = mix(color, color * dot_coverage, clamp(u_halftone, 0.0, 1.0));

    vec2 centered = (v_uv - 0.5) * vec2(u_resolution.x / max(u_resolution.y, 1.0), 1.0);
    float radius = length(centered);
    float vignette_mask = smoothstep(0.22, 0.92, radius);
    color *= 1.0 - vignette_mask * u_vignette * 0.88;

    float noise_seed = hash21(floor(v_uv * u_resolution) + floor(u_time * 24.0));
    color += (noise_seed - 0.5) * u_grain * 0.22;

    float scan = 0.5 + 0.5 * sin(v_uv.y * u_resolution.y * 3.14159265);
    color *= mix(1.0, 0.72 + 0.28 * scan, u_scanlines);

    vec3 processed = clamp(color, 0.0, 1.0);
    frag_color = vec4(mix(original_color, processed, clamp(u_mix, 0.0, 1.0)), 1.0);
}
"""


def canvas_fit_scale(
        output_width: int,
        output_height: int,
        canvas_width: int,
        canvas_height: int,
) -> tuple[float, float]:
    """Return normalized UV scale that letterboxes a canvas without distortion."""
    output_aspect = max(1, int(output_width)) / max(1, int(output_height))
    canvas_aspect = max(1, int(canvas_width)) / max(1, int(canvas_height))
    if output_aspect > canvas_aspect:
        return canvas_aspect / output_aspect, 1.0
    return 1.0, output_aspect / canvas_aspect


_BLEND_MODES = {
    "normal": 0,
    "add": 1,
    "screen": 2,
    "multiply": 3,
    "difference": 4,
}


class Compositor:
    """GPU video-layer compositor followed by real-time master/temporal effects."""

    MAX_PARTICLE_SYSTEMS = 4
    MAX_TOTAL_PARTICLES = 16384

    def __init__(self, context: moderngl.Context) -> None:
        self.ctx = context
        self.composite_program = context.program(
            vertex_shader=_VERTEX_SHADER,
            fragment_shader=_COMPOSITE_FRAGMENT,
        )
        self.post_program = context.program(
            vertex_shader=_VERTEX_SHADER,
            fragment_shader=_POST_FRAGMENT,
        )
        vertices = np.array(
            [
                -1.0, -1.0, 0.0, 0.0,
                1.0, -1.0, 1.0, 0.0,
                -1.0, 1.0, 0.0, 1.0,
                1.0, 1.0, 1.0, 1.0,
            ],
            dtype="f4",
        )
        self.vertex_buffer = context.buffer(vertices.tobytes())
        self.composite_vao = context.vertex_array(
            self.composite_program,
            [(self.vertex_buffer, "2f 2f", "in_position", "in_uv")],
        )
        self.post_vao = context.vertex_array(
            self.post_program,
            [(self.vertex_buffer, "2f 2f", "in_position", "in_uv")],
        )
        self.composite_program["u_base"].value = 0
        self.composite_program["u_layer"].value = 1
        self.composite_program["u_mask"].value = 2
        self.composite_program["u_animation"].value = 0
        self.composite_program["u_animation_speed"].value = 0.0
        self.composite_program["u_animation_amount"].value = 0.0
        self.composite_program["u_generator_type"].value = 0
        self.composite_program["u_text_animation"].value = 0
        self.composite_program["u_particle_mode"].value = 0
        self.composite_program["u_layer_fx_enabled"].value = 0
        self.post_program["u_texture"].value = 0
        self.post_program["u_displacement_map"].value = 1
        self.particle_stub = context.texture(
            (1, 1),
            4,
            bytes((0, 0, 0, 0)),
            alignment=1,
            dtype="f1",
        )
        self.particle_stub.filter = (moderngl.NEAREST, moderngl.NEAREST)

        self.source_textures: dict[str, moderngl.Texture] = {}
        self.targets: list[moderngl.Texture] = []
        self.framebuffers: list[moderngl.Framebuffer] = []
        self.post_target: moderngl.Texture | None = None
        self.post_framebuffer: moderngl.Framebuffer | None = None
        self.feedback_engine = FeedbackEngine(context, self.vertex_buffer)
        self.particle_systems: dict[str, ParticleSystem2] = {}
        self.size = (0, 0)

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

    def update_texture(self, source_id: str, pixels: np.ndarray) -> None:
        frame = np.ascontiguousarray(pixels, dtype=np.uint8)
        if frame.ndim != 3 or frame.shape[2] not in (3, 4):
            raise ValueError("Video texture must be an HxWx3 or HxWx4 uint8 array.")
        height, width, components = frame.shape
        texture = self.source_textures.get(source_id)
        if (
                texture is None
                or texture.size != (width, height)
                or texture.components != components
        ):
            if texture is not None:
                texture.release()
            texture = self.ctx.texture(
                (width, height),
                components,
                frame.tobytes(),
                alignment=1,
                dtype="f1",
            )
            texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            texture.repeat_x = False
            texture.repeat_y = False
            self.source_textures[source_id] = texture
        else:
            texture.write(frame.tobytes(), alignment=1)

    def _resize_targets(self, width: int, height: int) -> None:
        width = max(1, int(width))
        height = max(1, int(height))
        if self.size == (width, height):
            return
        self._release_targets()
        for _ in range(2):
            texture = self.ctx.texture((width, height), 4, dtype="f1")
            texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
            framebuffer = self.ctx.framebuffer(color_attachments=[texture])
            self.targets.append(texture)
            self.framebuffers.append(framebuffer)
        self.post_target = self.ctx.texture((width, height), 4, dtype="f1")
        self.post_target.filter = (moderngl.LINEAR, moderngl.LINEAR)
        self.post_framebuffer = self.ctx.framebuffer(
            color_attachments=[self.post_target]
        )
        if self.feedback_engine.size != (0, 0):
            self.feedback_engine.resize(width, height)
        self.size = (width, height)

    def _apply_effects(
            self,
            texture: moderngl.Texture,
            target_fbo: int,
            width: int,
            height: int,
            effects: EffectSettings,
            time_seconds: float,
    ) -> None:
        destination = self.ctx.detect_framebuffer(glo=int(target_fbo))
        destination.use()
        self.ctx.viewport = (0, 0, width, height)
        texture.use(location=0)
        displacement_texture = (
            self.source_textures.get(effects.displacement_source_id)
            if effects.displacement_source_id else None
        )
        if displacement_texture is None:
            self.particle_stub.use(location=1)
        else:
            displacement_texture.use(location=1)
        effects.clamp()
        values = {
            "u_resolution": (float(width), float(height)),
            "u_time": float(time_seconds),
            "u_brightness": effects.brightness,
            "u_exposure": effects.exposure,
            "u_contrast": effects.contrast,
            "u_saturation": effects.saturation,
            "u_gamma": effects.gamma,
            "u_temperature": effects.temperature,
            "u_tint": effects.tint,
            "u_hue": effects.hue,
            "u_vignette": effects.vignette,
            "u_grain": effects.grain,
            "u_scanlines": effects.scanlines,
            "u_chromatic": effects.chromatic,
            "u_glitch": effects.glitch,
            "u_pixelate": effects.pixelate,
            "u_posterize": effects.posterize,
            "u_invert": effects.invert,
            "u_halftone": effects.halftone,
            "u_solarize": effects.solarize,
            "u_mix": effects.mix if effects.enabled else 0.0,
            "u_displacement_enabled": int(
                displacement_texture is not None and abs(effects.displacement_amount) > 0.0001
            ),
            "u_displacement_luma": int(effects.displacement_luma),
            "u_transform_mode": {
                "none": 0, "kaleidoscope": 1, "polar": 2, "mosaic": 3, "pixel_sort": 4,
            }.get(effects.transform_mode, 0),
            "u_transform_mix": effects.transform_mix,
            "u_kaleidoscope_slices": float(effects.kaleidoscope_slices),
            "u_kaleidoscope_rotation": effects.kaleidoscope_rotation,
            "u_kaleidoscope_zoom": effects.kaleidoscope_zoom,
            "u_mosaic_tiles": float(effects.mosaic_tiles),
            "u_pixel_sort_amount": effects.pixel_sort_amount,
            "u_pixel_sort_threshold": effects.pixel_sort_threshold,
            "u_edge_amount": effects.edge_amount,
            "u_dither": effects.dither,
            "u_displacement_amount": effects.displacement_amount,
            "u_displacement_scale": effects.displacement_scale,
        }
        for uniform_name, value in values.items():
            self.post_program[uniform_name].value = value
        self.post_vao.render(mode=moderngl.TRIANGLE_STRIP)

    def render(
            self,
            layers: list[Layer],
            target_fbo: int,
            width: int,
            height: int,
            effects: EffectSettings | None = None,
            time_seconds: float = 0.0,
            canvas_width: int = 1920,
            canvas_height: int = 1080,
    ) -> None:
        self._resize_targets(width, height)
        self.composite_program["u_canvas_scale"].value = canvas_fit_scale(
            width,
            height,
            canvas_width,
            canvas_height,
        )
        self.ctx.viewport = (0, 0, width, height)
        self.framebuffers[0].use()
        self.framebuffers[0].clear(0.025, 0.028, 0.035, 1.0)

        ordered_layers = sorted(layers, key=lambda item: item.z_index)
        active_particle_ids: set[str] = set()
        particle_outputs: dict[str, moderngl.Texture] = {}
        particle_budget = self.MAX_TOTAL_PARTICLES
        active_particle_systems = 0
        source_layers = {
            layer.source_id: layer
            for layer in ordered_layers
            if layer.source_id
        }

        # Simulation state and output targets belong to this Compositor's GL context.
        # Particle allocation is deterministic by layer order and globally bounded.
        for particle_layer in ordered_layers:
            if (
                    particle_layer.source_type != "generator"
                    or particle_layer.generator_type != "particle_system_2"
                    or not particle_layer.visible
                    or particle_layer.opacity <= 0.0
            ):
                continue
            if active_particle_systems >= self.MAX_PARTICLE_SYSTEMS or particle_budget <= 0:
                continue
            settings = normalize_settings(
                "particle_system_2", particle_layer.generator_settings
            )
            requested = min(
                int(settings["particle_count"]),
                ParticleSystem2.MAX_PARTICLES_PER_SYSTEM,
                particle_budget,
            )
            if requested <= 0:
                continue
            system = self.particle_systems.get(particle_layer.id)
            if system is None:
                try:
                    system = ParticleSystem2(self.ctx, self.vertex_buffer)
                    self.particle_systems[particle_layer.id] = system
                except Exception:
                    _LOG.exception("Could not initialize Particle System 2.0 for %s",
                                   particle_layer.name)
                    continue
            try:
                emitter_source_id = str(settings["emitter_source_id"])
                emitter_source = (
                    self.source_textures.get(emitter_source_id)
                    if emitter_source_id else None
                )
                source_layer = source_layers.get(emitter_source_id)
                source_transform = (
                    (
                        tuple(float(value) for value in source_layer.position),
                        tuple(float(value) for value in source_layer.scale),
                        float(source_layer.rotation),
                    )
                    if source_layer is not None else None
                )
                texture = system.render(
                    settings,
                    width,
                    height,
                    time_seconds,
                    particle_limit=requested,
                    emitter_source=emitter_source,
                    emitter_source_transform=source_transform,
                )
            except Exception:
                _LOG.exception("Particle System 2.0 render failed for %s", particle_layer.name)
                system.release()
                self.particle_systems.pop(particle_layer.id, None)
                continue
            if texture is not None:
                particle_outputs[particle_layer.id] = texture
                active_particle_ids.add(particle_layer.id)
                particle_budget -= requested
                active_particle_systems += 1

        for layer_id in tuple(self.particle_systems):
            if layer_id not in active_particle_ids:
                self.particle_systems.pop(layer_id).release()

        current = 0
        for layer in ordered_layers:
            if not layer.visible or layer.opacity <= 0.0:
                continue
            is_particle_layer = (
                    layer.source_type == "generator" and layer.generator_type == "particles"
            )
            is_particle_system = (
                    layer.source_type == "generator"
                    and layer.generator_type == "particle_system_2"
            )
            layer_texture = (
                particle_outputs.get(layer.id)
                if is_particle_system
                else self.source_textures.get(layer.source_id)
            )
            if layer_texture is None and not is_particle_layer:
                continue

            next_target = 1 - current
            self.framebuffers[next_target].use()
            self.ctx.viewport = (0, 0, width, height)

            self.targets[current].use(location=0)
            if layer_texture is not None:
                layer_texture.use(location=1)
            else:
                self.particle_stub.use(location=1)
            mask_texture = (
                self.source_textures.get(layer.overlay_mask_source)
                if layer.overlay_mask_source else None
            )
            if mask_texture is not None and layer.overlay_mask_mode in {"alpha", "luma"}:
                mask_texture.use(location=2)
                self.composite_program["u_mask_enabled"].value = 1
                self.composite_program["u_mask_mode"].value = (
                    2 if layer.overlay_mask_mode == "luma" else 1
                )
            else:
                self.particle_stub.use(location=2)
                self.composite_program["u_mask_enabled"].value = 0
                self.composite_program["u_mask_mode"].value = 0

            self.composite_program["u_position"].value = tuple(layer.position)
            self.composite_program["u_scale"].value = tuple(layer.scale)
            self.composite_program["u_rotation"].value = float(layer.rotation)
            self.composite_program["u_opacity"].value = float(layer.opacity)
            self.composite_program["u_blend_mode"].value = _BLEND_MODES.get(
                layer.blend_mode, 0
            )
            self.composite_program["u_time"].value = float(time_seconds)
            animation = layer.generator_settings if layer.source_type == "generator" else {}
            self.composite_program["u_animation"].value = animation_code(animation)
            self.composite_program["u_animation_speed"].value = float(
                animation.get("animation_speed", 0.0)
            )
            self.composite_program["u_animation_amount"].value = float(
                animation.get("animation_amount", 0.0)
            )
            generator_kind = layer.generator_type if layer.source_type == "generator" else None
            self.composite_program["u_generator_type"].value = {
                "particles": 1,
                "text": 2,
                "geometry": 3,
                "particle_system_2": 4,
            }.get(generator_kind, 0)
            self.composite_program["u_text_animation"].value = (
                text_animation_code(animation) if generator_kind == "text" else 0
            )
            self.composite_program["u_text_animation_speed"].value = float(
                animation.get("text_animation_speed", 1.0)
            )
            self.composite_program["u_text_animation_amount"].value = float(
                animation.get("text_animation_amount", 0.025)
            )
            self.composite_program["u_text_animation_columns"].value = float(
                animation.get("text_animation_columns", 18)
            )

            if generator_kind == "particles":
                settings = animation
                self.composite_program["u_particle_density"].value = float(settings["density"])
                self.composite_program["u_particle_speed"].value = float(settings["speed"])
                self.composite_program["u_particle_size"].value = float(settings["size"])
                self.composite_program["u_particle_spread"].value = float(settings["spread"])
                self.composite_program["u_particle_trail"].value = float(settings["trail"])
                self.composite_program["u_particle_mode"].value = {
                    "drift": 0, "rise": 1, "fall": 2, "orbit": 3,
                }.get(str(settings.get("mode", "drift")), 0)
                self.composite_program["u_particle_primary"].value = self._rgb(
                    str(settings["primary_color"])
                )
                self.composite_program["u_particle_secondary"].value = self._rgb(
                    str(settings["secondary_color"])
                )

            layer_fx = normalize_layer_effects(layer.layer_effects)
            stage_codes = {"monochrome": 1, "invert": 2, "threshold": 3,
                           "posterize": 4, "scanlines": 5, "hue": 6,
                           "contrast": 7, "saturation": 8, "brightness": 9}
            active_stages = [stage for stage in layer_fx["stages"] if stage["enabled"]]
            stage_types = [stage_codes[stage["type"]] for stage in active_stages]
            stage_amounts = [float(stage["amount"]) for stage in active_stages]
            self.composite_program["u_fx_stage_count"].value = len(stage_types)
            self.composite_program["u_fx_stage_type"].value = tuple(
                stage_types + [0] * (8 - len(stage_types))
            )
            self.composite_program["u_fx_stage_amount"].value = tuple(
                stage_amounts + [0.0] * (8 - len(stage_amounts))
            )
            self.composite_program["u_layer_fx_enabled"].value = int(layer_fx["enabled"])
            for uniform, key in (
                    ("u_layer_fx_mix", "mix"),
                    ("u_layer_fx_monochrome", "monochrome"),
                    ("u_layer_fx_invert", "invert"),
                    ("u_layer_fx_threshold", "threshold"),
                    ("u_layer_fx_posterize", "posterize"),
                    ("u_layer_fx_hue", "hue"),
                    ("u_layer_fx_saturation", "saturation"),
                    ("u_layer_fx_contrast", "contrast"),
                    ("u_layer_fx_brightness", "brightness"),
                    ("u_layer_fx_scanlines", "scanlines"),
                    ("u_layer_fx_chromatic", "chromatic"),
            ):
                self.composite_program[uniform].value = float(layer_fx[key])
            self.composite_vao.render(mode=moderngl.TRIANGLE_STRIP)
            current = next_target

        active_effects = effects or EffectSettings()
        active_effects.clamp()
        feedback_active = (
            active_effects.feedback_enabled and active_effects.feedback_amount > 0.0001
        )
        post_target_fbo = (
            self.post_framebuffer.glo
            if feedback_active and self.post_framebuffer is not None
            else target_fbo
        )
        self._apply_effects(
            self.targets[current],
            post_target_fbo,
            width,
            height,
            active_effects,
            time_seconds,
        )
        if feedback_active and self.post_target is not None:
            self.feedback_engine.render(
                self.post_target,
                target_fbo,
                width,
                height,
                active_effects,
                time_seconds,
            )

    def remove_texture(self, source_id: str) -> None:
        texture = self.source_textures.pop(source_id, None)
        if texture is not None:
            texture.release()

    def _release_targets(self) -> None:
        for framebuffer in self.framebuffers:
            framebuffer.release()
        for texture in self.targets:
            texture.release()
        self.framebuffers.clear()
        self.targets.clear()
        if self.post_framebuffer is not None:
            self.post_framebuffer.release()
            self.post_framebuffer = None
        if self.post_target is not None:
            self.post_target.release()
            self.post_target = None

    def release(self) -> None:
        self._release_targets()
        self.feedback_engine.release()
        for system in self.particle_systems.values():
            system.release()
        self.particle_systems.clear()
        for texture in self.source_textures.values():
            texture.release()
        self.source_textures.clear()
        self.composite_vao.release()
        self.post_vao.release()
        self.vertex_buffer.release()
        self.composite_program.release()
        self.post_program.release()
        self.particle_stub.release()
