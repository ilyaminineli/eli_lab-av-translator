from __future__ import annotations

from copy import deepcopy
from typing import Any

GENERATOR_TYPES = ("geometry", "text", "waveform", "particles", "particle_system_2")

_DEFAULTS: dict[str, dict[str, Any]] = {
    "geometry": {
        "pattern": "rings",
        "primary_color": "#E8E4DA",
        "secondary_color": "#8678A8",
        "background_color": "#00000000",
        "density": 12,
        "line_width": 2.0,
        "rotation": 0.0,
        "animation": "rotate",
        "animation_speed": 0.18,
        "animation_amount": 12.0,
    },
    "text": {
        "text": "THE SHAPE OF\nA VANISHING\nSIGNAL",
        "text_runs": [],
        "text_writing_mode": "horizontal",
        "text_path_mode": "none",
        "text_path_points": [[0.12, 0.68], [0.34, 0.28], [0.66, 0.72], [0.88, 0.32]],
        "text_pool_language": "bilingual",
        "text_pool_theme": "random",
        "text_pool_count": 16,
        "text_pool_dictionary": True,
        "text_auto_regenerate": True,
        "font_family": "Arial",
        "font_size": 148,
        "font_weight": 700,
        "letter_spacing": 10.0,
        "line_spacing": 1.0,
        "alignment": "center",
        "vertical_alignment": "middle",
        "primary_color": "#F2EEE6",
        "secondary_color": "#C35C75",
        "text_color_mode": "alternate",
        "text_layout": "single",
        "collage_seed": 211,
        "collage_font_variation": 0.65,
        "text_animation": "none",
        "text_animation_speed": 1.0,
        "text_animation_amount": 0.025,
        "text_animation_columns": 18,
        "stroke_color": "#211B2A",
        "stroke_width": 2.0,
        "shadow": True,
        "animation": "none",
        "animation_speed": 0.2,
        "animation_amount": 0.0,
    },
    "waveform": {
        "pattern": "sine",
        "primary_color": "#E8E4DA",
        "secondary_color": "#C35C75",
        "density": 5,
        "line_width": 3.0,
        "amplitude": 0.22,
        "frequency": 2.5,
        "phase_offset": 0.8,
        "animation": "drift",
        "animation_speed": 0.28,
        "animation_amount": 0.025,
    },
    "particles": {
        "primary_color": "#E8E4DA",
        "secondary_color": "#C35C75",
        "density": 42,
        "speed": 0.22,
        "size": 0.18,
        "spread": 0.42,
        "trail": 0.18,
        "mode": "drift",
        "animation": "none",
        "animation_speed": 0.0,
        "animation_amount": 0.0,
    },
    "particle_system_2": {
        "primary_color": "#E8E4DA",
        "secondary_color": "#C35C75",
        "particle_count": 4096,
        "population_count": 2,
        "emitter_type": "point",
        "emitter_center": [0.5, 0.5],
        "emitter_source_id": "",
        "emitter_map_mode": "luminance",
        "emitter_threshold": 0.52,
        "emitter_sample_attempts": 12,
        "emitter_sample_interval": 0.5,
        "reform_strength": 0.0,
        "path_points": [[0.12, 0.5], [0.34, 0.18], [0.66, 0.82], [0.88, 0.5]],
        "emitter_radius": 0.18,
        "emitter_size": [0.34, 0.24],
        "direction": "radial",
        "lifetime": 4.5,
        "speed": 0.22,
        "spread": 0.36,
        "acceleration": [0.0, 0.0],
        "turbulence": 0.14,
        "turbulence_scale": 5.0,
        "force_type": "none",
        "force_center": [0.5, 0.5],
        "force_strength": 0.55,
        "force_radius": 0.34,
        "drag": 0.08,
        "trail": 0.72,
        "particle_size": 6.0,
        "size_curve": "shrink",
        "seed": 20261112,
        "animation": "none",
        "animation_speed": 0.0,
        "animation_amount": 0.0,
    },
}

_ANIMATIONS = ("none", "pulse", "rotate", "drift", "flicker", "warp")


def default_generator_settings(generator_type: str) -> dict[str, Any]:
    if generator_type not in _DEFAULTS:
        raise ValueError(f"Unknown generator type: {generator_type}")
    return deepcopy(_DEFAULTS[generator_type])


def normalize_settings(generator_type: str, settings: dict[str, Any] | None) -> dict[str, Any]:
    """Merge user settings with safe defaults and clamp resource/visual ranges."""
    result = default_generator_settings(generator_type)
    if settings:
        result.update({
            key: value for key, value in settings.items()
            if key in result
        })

    if generator_type == "geometry":
        if result["pattern"] not in {
            "rings", "grid", "radial", "crosshatch", "polygon",
            "spiral", "moire", "hexgrid",
        }:
            result["pattern"] = "rings"
        result["density"] = max(2, min(80, int(result["density"])))
        result["line_width"] = max(0.5, min(24.0, float(result["line_width"])))
        result["rotation"] = max(-360.0, min(360.0, float(result["rotation"])))
    elif generator_type == "text":
        result["text_pool_language"] = result.get("text_pool_language", "bilingual")
        if result["text_pool_language"] not in {"english", "japanese", "bilingual"}:
            result["text_pool_language"] = "bilingual"
        result["text_pool_theme"] = result.get("text_pool_theme", "random")
        if result["text_pool_theme"] not in {
            "random", "memory", "body", "signal", "ritual", "identity"
        }:
            result["text_pool_theme"] = "random"
        result["text_pool_count"] = max(1, min(60, int(result.get("text_pool_count", 16))))
        result["text_pool_dictionary"] = bool(result.get("text_pool_dictionary", True))
        result["text_auto_regenerate"] = bool(result.get("text_auto_regenerate", True))
        result["font_size"] = max(12, min(420, int(result["font_size"])))
        requested_weight = max(100, min(900, int(result["font_weight"])))
        supported_weights = (100, 200, 300, 400, 500, 600, 700, 800, 900)
        result["font_weight"] = min(
            supported_weights,
            key=lambda weight: abs(weight - requested_weight),
        )
        result["letter_spacing"] = max(-8.0, min(48.0, float(result["letter_spacing"])))
        result["line_spacing"] = max(0.5, min(2.5, float(result["line_spacing"])))
        result["stroke_width"] = max(0.0, min(24.0, float(result["stroke_width"])))
        if result["alignment"] not in {"left", "center", "right"}:
            result["alignment"] = "center"
        if result["vertical_alignment"] not in {"top", "middle", "bottom"}:
            result["vertical_alignment"] = "middle"
        if result.get("text_color_mode") not in {"single", "alternate"}:
            result["text_color_mode"] = "single"
        result["shadow"] = bool(result["shadow"])
        if result.get("text_layout") not in {"single", "collage"}:
            result["text_layout"] = "single"
        if result.get("text_writing_mode") not in {
                "horizontal", "vertical_rl", "vertical_lr",
        }:
            result["text_writing_mode"] = "horizontal"
        if result.get("text_path_mode") not in {"none", "circle", "arc", "custom"}:
            result["text_path_mode"] = "none"
        raw_path_points = result.get("text_path_points", [])
        path_points = []
        if isinstance(raw_path_points, (list, tuple)):
            for point in raw_path_points[:64]:
                try:
                    if len(point) < 2:
                        continue
                    path_points.append([
                        max(0.0, min(1.0, float(point[0]))),
                        max(0.0, min(1.0, float(point[1]))),
                    ])
                except (TypeError, ValueError, OverflowError):
                    continue
        if len(path_points) < 2:
            path_points = [[0.12, 0.68], [0.34, 0.28], [0.66, 0.72], [0.88, 0.32]]
        result["text_path_points"] = path_points
        raw_runs = result.get("text_runs", [])
        text_runs = []
        total_run_characters = 0
        if isinstance(raw_runs, (list, tuple)):
            for raw_run in raw_runs[:64]:
                if not isinstance(raw_run, dict):
                    continue
                run_text = str(raw_run.get("text", ""))[:4096]
                if not run_text:
                    continue
                total_run_characters += len(run_text)
                if total_run_characters > 8192:
                    break
                run = {"text": run_text}
                family = str(raw_run.get("font_family", result["font_family"]))[:128].strip()
                run["font_family"] = family or str(result["font_family"])
                run["font_size"] = max(
                    12, min(420, int(raw_run.get("font_size", result["font_size"])))
                )
                requested_run_weight = max(
                    100, min(900, int(raw_run.get("font_weight", result["font_weight"])))
                )
                run["font_weight"] = min(
                    (100, 200, 300, 400, 500, 600, 700, 800, 900),
                    key=lambda weight: abs(weight - requested_run_weight),
                )
                for key, fallback in (
                        ("color", result["primary_color"]),
                        ("stroke_color", result["stroke_color"]),
                ):
                    value = str(raw_run.get(key, fallback)).strip()
                    run[key] = value[:32] if value.startswith("#") else fallback
                run["letter_spacing"] = max(
                    -8.0, min(48.0, float(raw_run.get("letter_spacing", result["letter_spacing"])))
                )
                run["stroke_width"] = max(
                    0.0, min(24.0, float(raw_run.get("stroke_width", result["stroke_width"])))
                )
                run["shadow"] = bool(raw_run.get("shadow", result["shadow"]))
                text_runs.append(run)
        result["text_runs"] = text_runs
        result["collage_seed"] = max(0, min(2 ** 31 - 1, int(result["collage_seed"])))
        result["collage_font_variation"] = max(
            0.0, min(1.0, float(result["collage_font_variation"]))
        )
        if result.get("text_animation") not in {
            "none", "type_on", "word_reveal", "line_wave", "jitter", "crawl", "glitch",
            "reverse_typewriter", "dissolve", "flicker", "character_displacement",
            "vertical_reveal", "scattered_glyphs", "word_collisions", "mechanical_scroll",
        }:
            result["text_animation"] = "none"
        result["text_animation_speed"] = max(
            0.0, min(8.0, float(result["text_animation_speed"]))
        )
        result["text_animation_amount"] = max(
            0.0, min(0.18, float(result["text_animation_amount"]))
        )
        result["text_animation_columns"] = max(
            2, min(80, int(result["text_animation_columns"]))
        )
    elif generator_type == "waveform":
        if result["pattern"] not in {"sine", "lissajous", "orbit", "radial", "rose"}:
            result["pattern"] = "sine"
        result["density"] = max(1, min(12, int(result["density"])))
        result["line_width"] = max(0.5, min(20.0, float(result["line_width"])))
        result["amplitude"] = max(0.01, min(0.48, float(result["amplitude"])))
        result["frequency"] = max(0.1, min(24.0, float(result["frequency"])))
        result["phase_offset"] = max(0.0, min(6.283, float(result["phase_offset"])))
    elif generator_type == "particles":
        result["density"] = max(4, min(120, int(result["density"])))
        result["speed"] = max(0.0, min(2.0, float(result["speed"])))
        result["size"] = max(0.02, min(0.8, float(result["size"])))
        result["spread"] = max(0.0, min(1.0, float(result["spread"])))
        result["trail"] = max(0.0, min(1.0, float(result["trail"])))
        if result.get("mode") not in {"drift", "rise", "fall", "orbit"}:
            result["mode"] = "drift"
    elif generator_type == "particle_system_2":
        result["particle_count"] = max(128, min(8192, int(result["particle_count"])))
        result["population_count"] = max(1, min(4, int(result["population_count"])))
        if result["emitter_type"] not in {
                "point", "circle", "rectangle", "path", "video_luminance",
                "image_silhouette", "contour",
        }:
            result["emitter_type"] = "point"
        if result["emitter_map_mode"] not in {"luminance", "alpha", "contour"}:
            result["emitter_map_mode"] = "luminance"
        if result["direction"] not in {
                "radial", "random", "up", "down", "left", "right", "tangent",
        }:
            result["direction"] = "radial"
        if result["force_type"] not in {"none", "attract", "repel", "orbit"}:
            result["force_type"] = "none"
        if result["size_curve"] not in {"constant", "grow", "shrink", "pulse"}:
            result["size_curve"] = "shrink"
        def pair(value, fallback, low, high):
            try:
                values = list(value)
                if len(values) < 2:
                    raise ValueError("Pair needs two values")
                return [
                    max(low, min(high, float(values[0]))),
                    max(low, min(high, float(values[1]))),
                ]
            except (TypeError, ValueError, OverflowError):
                return list(fallback)
        result["emitter_center"] = pair(
            result["emitter_center"], (0.5, 0.5), 0.0, 1.0
        )
        result["emitter_size"] = pair(
            result["emitter_size"], (0.34, 0.24), 0.01, 1.0
        )
        result["acceleration"] = pair(
            result["acceleration"], (0.0, 0.0), -2.0, 2.0
        )
        result["force_center"] = pair(
            result["force_center"], (0.5, 0.5), 0.0, 1.0
        )
        result["emitter_source_id"] = str(result["emitter_source_id"] or "").strip()[:256]
        result["emitter_threshold"] = max(
            0.0, min(1.0, float(result["emitter_threshold"]))
        )
        result["emitter_sample_attempts"] = max(
            1, min(16, int(result["emitter_sample_attempts"]))
        )
        result["emitter_sample_interval"] = max(
            0.1, min(10.0, float(result["emitter_sample_interval"]))
        )
        result["reform_strength"] = max(0.0, min(4.0, float(result["reform_strength"])))
        raw_path = result.get("path_points", [])
        path_points = []
        if isinstance(raw_path, (list, tuple)):
            for point in raw_path[:64]:
                path_points.append(pair(point, (0.5, 0.5), 0.0, 1.0))
        if len(path_points) < 2:
            path_points = [
                [0.12, 0.5], [0.34, 0.18], [0.66, 0.82], [0.88, 0.5],
            ]
        result["path_points"] = path_points
        result["emitter_radius"] = max(0.01, min(0.5, float(result["emitter_radius"])))
        result["lifetime"] = max(0.25, min(60.0, float(result["lifetime"])))
        result["speed"] = max(0.0, min(1.5, float(result["speed"])))
        result["spread"] = max(0.0, min(2.0, float(result["spread"])))
        result["turbulence"] = max(0.0, min(1.5, float(result["turbulence"])))
        result["turbulence_scale"] = max(0.1, min(24.0, float(result["turbulence_scale"])))
        result["force_strength"] = max(0.0, min(4.0, float(result["force_strength"])))
        result["force_radius"] = max(0.01, min(1.0, float(result["force_radius"])))
        result["drag"] = max(0.0, min(4.0, float(result["drag"])))
        result["trail"] = max(0.0, min(1.0, float(result["trail"])))
        result["particle_size"] = max(1.0, min(48.0, float(result["particle_size"])))
        result["seed"] = max(0, min(2 ** 31 - 1, int(result["seed"])))

    if result.get("animation") not in _ANIMATIONS:
        result["animation"] = "none"
    result["animation_speed"] = max(0.0, min(8.0, float(result["animation_speed"])))
    result["animation_amount"] = max(
        0.0,
        min(360.0 if result["animation"] == "rotate" else 0.45,
            float(result["animation_amount"])),
    )
    return result


def animation_code(settings: dict[str, Any]) -> int:
    """Map animation presets to the compositor's small uniform enum."""
    return {
        "none": 0,
        "pulse": 1,
        "rotate": 2,
        "drift": 3,
        "flicker": 4,
        "warp": 5,
    }.get(str(settings.get("animation", "none")), 0)


def text_animation_code(settings: dict[str, Any]) -> int:
    """Map text-specific motion behaviours to the compositor shader."""
    return {
        "none": 0,
        "type_on": 1,
        "word_reveal": 2,
        "line_wave": 3,
        "jitter": 4,
        "crawl": 5,
        "glitch": 6,
        "reverse_typewriter": 7,
        "dissolve": 8,
        "flicker": 9,
        "character_displacement": 10,
        "vertical_reveal": 11,
        "scattered_glyphs": 12,
        "word_collisions": 13,
        "mechanical_scroll": 14,
    }.get(str(settings.get("text_animation", "none")), 0)
