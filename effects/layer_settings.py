from __future__ import annotations

from copy import deepcopy
from typing import Any

LY_EFFECT_DEFAULTS: dict[str, Any] = {
    "enabled": False,
    "stages": [],
    "mix": 1.0,
    "monochrome": 0.0,
    "invert": 0.0,
    "threshold": 0.0,
    "posterize": 0.0,
    "hue": 0.0,
    "saturation": 1.0,
    "contrast": 1.0,
    "brightness": 0.0,
    "scanlines": 0.0,
    "chromatic": 0.0,
}

LY_EFFECT_PSETS: dict[str, dict[str, Any]] = {
    "Clean": {},
    "Monochrome": {"monochrome": 1.0, "contrast": 1.12},
    "Xerox": {
        "monochrome": 1.0,
        "contrast": 1.75,
        "threshold": 0.66,
        "posterize": 0.8,
        "scanlines": 0.08,
    },
    "Negative": {"invert": 1.0, "contrast": 1.08},
    "Duotone": {"monochrome": 0.82, "hue": -28.0, "saturation": 1.5},
    "Ghost": {
        "monochrome": 0.35,
        "chromatic": 0.72,
        "saturation": 1.35,
        "contrast": 1.22,
        "brightness": 0.06,
    },
    "Tape": {
        "chromatic": 0.6,
        "scanlines": 0.48,
        "saturation": 1.18,
        "hue": 8.0,
    },
    "Bleach Bypass": {"contrast": 1.72, "saturation": 0.48, "brightness": -0.035},
    "Infrared": {"hue": -42.0, "saturation": 1.9, "contrast": 1.28, "brightness": 0.04},
    "Cold Storage": {"hue": 22.0, "saturation": 0.72, "contrast": 1.18, "brightness": -0.025},
    "Riso Print": {"monochrome": 0.28, "posterize": 0.72, "contrast": 1.4, "saturation": 1.45},
    "Soft Ghost": {"monochrome": 0.18, "chromatic": 0.28, "saturation": 0.62, "contrast": 0.82},
    "Hard Signal": {"threshold": 0.42, "posterize": 0.9, "scanlines": 0.62, "contrast": 1.9},
}


def default_layer_effects() -> dict[str, Any]:
    return deepcopy(LY_EFFECT_DEFAULTS)


def normalize_layer_effects(settings: dict[str, Any] | None) -> dict[str, Any]:
    result = default_layer_effects()
    if isinstance(settings, dict):
        result.update({
            key: value for key, value in settings.items()
            if key in result
        })
    result["enabled"] = bool(result["enabled"])
    raw_stages = result.get("stages", [])
    result["stages"] = normalize_effect_stages(raw_stages)
    for key in (
            "mix", "monochrome", "invert", "threshold", "posterize",
            "scanlines", "chromatic",
    ):
        result[key] = max(0.0, min(1.0, float(result[key])))
    result["hue"] = max(-180.0, min(180.0, float(result["hue"])))
    result["saturation"] = max(0.0, min(2.5, float(result["saturation"])))
    result["contrast"] = max(0.0, min(2.5, float(result["contrast"])))
    result["brightness"] = max(-0.5, min(0.5, float(result["brightness"])))
    return result


def apply_layer_effect_preset(name: str) -> dict[str, Any]:
    if name not in LY_EFFECT_PSETS:
        raise KeyError(f"Unknown layer effect preset: {name}")
    values = default_layer_effects()
    values["enabled"] = name != "Clean"
    values.update(LY_EFFECT_PSETS[name])
    return normalize_layer_effects(values)


EFFECT_STAGE_TYPES = {
    "monochrome": "Monochrome",
    "invert": "Negative",
    "threshold": "Threshold",
    "posterize": "Posterize",
    "scanlines": "Scanlines",
    "hue": "Hue shift",
    "contrast": "Contrast",
    "saturation": "Saturation",
    "brightness": "Brightness",
}


def normalize_effect_stages(stages: object) -> list[dict[str, Any]]:
    """Normalize ordered layer FX stages. The list order is the render order."""
    if not isinstance(stages, list):
        return []
    normalized = []
    for item in stages[:8]:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("type", ""))
        if kind not in EFFECT_STAGE_TYPES:
            continue
        try:
            amount = float(item.get("amount", 1.0))
        except (TypeError, ValueError):
            amount = 1.0
        normalized.append({
            "type": kind,
            "amount": max(0.0, min(1.0, amount)),
            "enabled": bool(item.get("enabled", True)),
        })
    return normalized


def default_effect_chain() -> list[dict[str, Any]]:
    return [
        {"type": "monochrome", "amount": 1.0, "enabled": True},
        {"type": "threshold", "amount": 0.45, "enabled": True},
    ]


def apply_effect_chain_preset(name: str) -> dict[str, Any]:
    chains = {
        "Xerox Stack": default_effect_chain(),
        "Negative Print": [
            {"type": "invert", "amount": 1.0, "enabled": True},
            {"type": "posterize", "amount": 0.55, "enabled": True},
        ],
        "Signal Scan": [
            {"type": "hue", "amount": 0.22, "enabled": True},
            {"type": "scanlines", "amount": 0.7, "enabled": True},
        ],
        "Clean": [],
    }
    if name not in chains:
        raise KeyError(f"Unknown effect chain preset: {name}")
    values = default_layer_effects()
    values["enabled"] = bool(chains[name])
    values["stages"] = deepcopy(chains[name])
    return normalize_layer_effects(values)
