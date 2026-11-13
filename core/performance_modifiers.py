from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field
from typing import Literal
from uuid import uuid4

from core.modulation import SOURCE_RANGES

ModifierCurve = Literal["linear", "smoothstep", "exponential"]
ModifierPolarity = Literal["positive", "bipolar"]


@dataclass(frozen=True)
class ModifierTargetSpec:
    target_id: str
    label: str
    minimum: float
    maximum: float
    category: str


PERFORMANCE_MODIFIER_SOURCES: dict[str, str] = {
    "transport.beat_pulse": "Rhythm · Every beat",
    "transport.downbeat_pulse": "Rhythm · Bar downbeat",
    "transport.phrase_pulse": "Rhythm · Phrase start",
    "transport.bar_phase": "Rhythm · Bar phase",
    "transport.phase": "Rhythm · Beat phase",
    "transport.intensity": "Scene · Intensity",
    "audio.rms": "Audio · RMS / energy",
    "audio.peak": "Audio · Peak",
    "audio.low": "Audio · Low band",
    "audio.mid": "Audio · Mid band",
    "audio.high": "Audio · High band",
    "audio.onset": "Audio · Onset",
    "audio.beat_confidence": "Audio · Beat confidence",
    "macro.energy": "Sonic Pi · Energy",
    "macro.cutoff": "Sonic Pi · Cutoff",
}

PERFORMANCE_MODIFIER_TARGETS: dict[str, ModifierTargetSpec] = {
    "layer.opacity": ModifierTargetSpec("layer.opacity", "Layer opacity", 0.0, 1.0, "layer"),
    "layer.rotation": ModifierTargetSpec(
        "layer.rotation", "Layer rotation", -180.0, 180.0, "layer"
    ),
    "layer.scale": ModifierTargetSpec("layer.scale", "Layer scale", 0.05, 2.0, "layer"),
    "layer.position_x": ModifierTargetSpec(
        "layer.position_x", "Layer X position", 0.0, 1.0, "layer"
    ),
    "layer.position_y": ModifierTargetSpec(
        "layer.position_y", "Layer Y position", 0.0, 1.0, "layer"
    ),
    "layer_fx.chromatic": ModifierTargetSpec(
        "layer_fx.chromatic", "Layer FX chromatic aberration", 0.0, 1.0, "layer"
    ),
    "layer_fx.scanlines": ModifierTargetSpec(
        "layer_fx.scanlines", "Layer FX scanlines", 0.0, 1.0, "layer"
    ),
    "layer_fx.posterize": ModifierTargetSpec(
        "layer_fx.posterize", "Layer FX posterize", 0.0, 1.0, "layer"
    ),
    "layer_fx.invert": ModifierTargetSpec(
        "layer_fx.invert", "Layer FX invert", 0.0, 1.0, "layer"
    ),
    "layer_fx.hue": ModifierTargetSpec(
        "layer_fx.hue", "Layer FX hue rotation", -180.0, 180.0, "layer"
    ),
    "layer_fx.saturation": ModifierTargetSpec(
        "layer_fx.saturation", "Layer FX saturation", 0.0, 2.5, "layer"
    ),
    "generator.animation_speed": ModifierTargetSpec(
        "generator.animation_speed", "Generator animation speed", 0.0, 8.0, "generator"
    ),
    "generator.animation_amount": ModifierTargetSpec(
        "generator.animation_amount", "Generator motion amount", 0.0, 360.0, "generator"
    ),
    "generator.density": ModifierTargetSpec(
        "generator.density", "Generator density", 1.0, 120.0, "generator"
    ),
    "generator.rotation": ModifierTargetSpec(
        "generator.rotation", "Geometry rotation", -360.0, 360.0, "generator"
    ),
    "generator.text_animation_speed": ModifierTargetSpec(
        "generator.text_animation_speed", "Text animation speed", 0.0, 8.0, "generator"
    ),
    "generator.text_animation_amount": ModifierTargetSpec(
        "generator.text_animation_amount", "Text animation amount", 0.0, 0.18, "generator"
    ),
    "generator.text_animation_columns": ModifierTargetSpec(
        "generator.text_animation_columns", "Text animation reveal steps", 2.0, 80.0, "generator"
    ),
    "generator.font_size": ModifierTargetSpec(
        "generator.font_size", "Text font size", 12.0, 420.0, "generator"
    ),
    "generator.letter_spacing": ModifierTargetSpec(
        "generator.letter_spacing", "Text letter spacing", -8.0, 48.0, "generator"
    ),
    "generator.waveform_amplitude": ModifierTargetSpec(
        "generator.waveform_amplitude", "Waveform amplitude", 0.01, 0.48, "generator"
    ),
    "generator.waveform_frequency": ModifierTargetSpec(
        "generator.waveform_frequency", "Waveform frequency", 0.1, 24.0, "generator"
    ),
    "generator.particle_speed": ModifierTargetSpec(
        "generator.particle_speed", "Particle speed", 0.0, 2.0, "generator"
    ),
    "generator.particle_size": ModifierTargetSpec(
        "generator.particle_size", "Particle size", 0.02, 0.8, "generator"
    ),
    "generator.particle_spread": ModifierTargetSpec(
        "generator.particle_spread", "Particle spread", 0.0, 1.0, "generator"
    ),
    "generator.particle_trail": ModifierTargetSpec(
        "generator.particle_trail", "Particle trail", 0.0, 1.0, "generator"
    ),
    "generator.particle_emission_rate": ModifierTargetSpec(
        "generator.particle_emission_rate", "Particle emission rate", 0.0, 3000.0, "generator"
    ),
    "generator.particle_system_size": ModifierTargetSpec(
        "generator.particle_system_size", "Particle System 2.0 size", 1.0, 48.0, "generator"
    ),
    "generator.particle_lifetime": ModifierTargetSpec(
        "generator.particle_lifetime", "Particle lifetime", 0.25, 60.0, "generator"
    ),
    "generator.particle_turbulence": ModifierTargetSpec(
        "generator.particle_turbulence", "Particle turbulence", 0.0, 1.5, "generator"
    ),
    "generator.particle_force_strength": ModifierTargetSpec(
        "generator.particle_force_strength", "Particle force strength", 0.0, 4.0, "generator"
    ),
    "generator.particle_reform_strength": ModifierTargetSpec(
        "generator.particle_reform_strength", "Particle source reform strength", 0.0, 4.0, "generator"
    ),
    "overlay.playback_speed": ModifierTargetSpec(
        "overlay.playback_speed", "Overlay playback speed", 0.1, 4.0, "overlay"
    ),
    "overlay.frame_hold": ModifierTargetSpec(
        "overlay.frame_hold", "Overlay frame hold", 1.0, 24.0, "overlay"
    ),
}


@dataclass
class LayerPerformanceModifier:
    modifier_id: str = field(default_factory=lambda: uuid4().hex[:10])
    name: str = "Beat motion"
    source_id: str = "transport.beat_pulse"
    target_id: str = "generator.animation_amount"
    depth: float = 0.12
    polarity: ModifierPolarity = "positive"
    curve: ModifierCurve = "smoothstep"
    attack_ms: float = 12.0
    release_ms: float = 180.0
    enabled: bool = True

    def normalize(self) -> None:
        is_modulator_source = self.source_id.startswith("modulator.")
        if is_modulator_source:
            if not self.source_id.removeprefix("modulator.").strip():
                raise ValueError("A modulator source must include a modulator ID.")
        else:
            if self.source_id not in SOURCE_RANGES:
                raise ValueError(f"Unknown performance modifier source: {self.source_id}")
            if self.source_id not in PERFORMANCE_MODIFIER_SOURCES:
                raise ValueError(f"Unsupported per-layer source: {self.source_id}")
        if self.target_id not in PERFORMANCE_MODIFIER_TARGETS:
            raise ValueError(f"Unknown performance modifier target: {self.target_id}")
        self.modifier_id = str(self.modifier_id).strip()[:40] or uuid4().hex[:10]
        self.name = str(self.name).strip()[:48] or "Performance modifier"
        self.depth = max(0.0, min(1.0, float(self.depth)))
        if self.polarity not in {"positive", "bipolar"}:
            self.polarity = "positive"
        if self.curve not in {"linear", "smoothstep", "exponential"}:
            self.curve = "smoothstep"
        self.attack_ms = max(1.0, min(2000.0, float(self.attack_ms)))
        self.release_ms = max(1.0, min(5000.0, float(self.release_ms)))
        self.enabled = bool(self.enabled)

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> LayerPerformanceModifier:
        allowed = set(cls.__dataclass_fields__)
        clean = {key: value for key, value in values.items() if key in allowed}
        modifier = cls(**clean)
        modifier.normalize()
        return modifier


@dataclass
class _ModifierRuntime:
    current: float | None = None
    last_update: float = 0.0


class LayerPerformanceModifierEngine:
    """Evaluates saved per-layer modifiers on the application/UI tick."""

    def __init__(self) -> None:
        self._runtime: dict[tuple[str, str], _ModifierRuntime] = {}
        self._base_values: dict[tuple[str, str], float] = {}
        self._active_targets: set[tuple[str, str]] = set()
        self._manual_until: dict[tuple[str, str], float] = {}
        self._live_values: dict[tuple[str, str], float] = {}

    @staticmethod
    def _curve(value: float, curve: ModifierCurve) -> float:
        value = max(0.0, min(1.0, value))
        if curve == "smoothstep":
            return value * value * (3.0 - 2.0 * value)
        if curve == "exponential":
            return value * value
        return value

    def notify_manual_override(
            self,
            layer_id: str,
            target_ids: set[str],
            modifier_records: list[dict[str, object]],
            duration_seconds: float = 3.0,
            now: float | None = None,
    ) -> None:
        stamp = time.monotonic() if now is None else float(now)
        affected_ids: set[str] = set()
        for target_id in target_ids:
            key = (layer_id, target_id)
            self._manual_until[key] = stamp + max(0.0, float(duration_seconds))
            self._base_values.pop(key, None)
            self._active_targets.discard(key)
            for raw in modifier_records:
                if not isinstance(raw, dict) or raw.get("target_id") != target_id:
                    continue
                affected_ids.add(str(raw.get("modifier_id", "")))
        for runtime_key in tuple(self._runtime):
            if runtime_key[0] == layer_id and runtime_key[1] in affected_ids:
                self._runtime.pop(runtime_key, None)
                self._live_values.pop(runtime_key, None)

    def claimed_targets(
            self,
            layer,
            now: float | None = None,
            available_sources: set[str] | None = None,
    ) -> set[str]:
        if layer is None:
            return set()
        layer_id = str(layer.id)
        stamp = time.monotonic() if now is None else float(now)
        result: set[str] = set()
        for raw in getattr(layer, "performance_modifiers", []):
            if not isinstance(raw, dict):
                continue
            try:
                modifier = LayerPerformanceModifier.from_dict(raw)
            except (TypeError, ValueError, KeyError):
                continue
            source_requires_presence = modifier.source_id.startswith(
                ("modulator.", "macro.")
            )
            source_available = (
                    available_sources is None
                    or not source_requires_presence
                    or modifier.source_id in available_sources
            )
            if (
                    modifier.enabled
                    and source_available
                    and stamp >= self._manual_until.get(
                (layer_id, modifier.target_id), 0.0
            )
            ):
                result.add(modifier.target_id)
        return result

    def reset(self) -> None:
        self._runtime.clear()
        self._base_values.clear()
        self._active_targets.clear()
        self._manual_until.clear()
        self._live_values.clear()

    def clear_layer(self, layer_id: str) -> None:
        self._runtime = {key: value for key, value in self._runtime.items() if key[0] != layer_id}
        self._base_values = {
            key: value for key, value in self._base_values.items()
            if key[0] != layer_id
        }
        self._active_targets = {key for key in self._active_targets if key[0] != layer_id}
        self._manual_until = {
            key: value for key, value in self._manual_until.items()
            if key[0] != layer_id
        }
        self._live_values = {
            key: value for key, value in self._live_values.items()
            if key[0] != layer_id
        }

    def live_values(self, layer_id: str) -> dict[str, float]:
        return {
            modifier_id: value
            for (owner_id, modifier_id), value in self._live_values.items()
            if owner_id == layer_id
        }

    def base_values(self) -> dict[tuple[str, str], float]:
        """Return pre-modulation values for clean project persistence."""
        return dict(self._base_values)

    def evaluate(
            self,
            layers: list[object],
            sources: dict[str, float],
            get_target,
            set_target,
            now: float | None = None,
    ) -> dict[tuple[str, str], float]:
        stamp = time.monotonic() if now is None else float(now)
        contributions: dict[tuple[str, str], float] = {}
        current_live: dict[tuple[str, str], float] = {}
        configured_runtime_keys: set[tuple[str, str]] = set()
        for key, deadline in tuple(self._manual_until.items()):
            if stamp >= deadline:
                self._manual_until.pop(key, None)
        for layer in layers:
            parsed: list[LayerPerformanceModifier] = []
            for raw in getattr(layer, "performance_modifiers", []):
                if not isinstance(raw, dict):
                    continue
                try:
                    parsed.append(LayerPerformanceModifier.from_dict(raw))
                except (TypeError, ValueError, KeyError):
                    continue
            if getattr(layer, "locked", False):
                continue
            layer_id = str(getattr(layer, "id", ""))
            for modifier in parsed:
                if not modifier.enabled:
                    continue
                target_key = (layer_id, modifier.target_id)
                if stamp < self._manual_until.get(target_key, 0.0):
                    continue
                runtime_key = (layer_id, modifier.modifier_id)
                configured_runtime_keys.add(runtime_key)
                raw_source = sources.get(modifier.source_id)
                if raw_source is None:
                    continue
                source = float(raw_source)
                if not math.isfinite(source):
                    continue
                source = self._curve(source, modifier.curve)
                runtime = self._runtime.setdefault(runtime_key, _ModifierRuntime())
                if runtime.current is None:
                    smoothed = source
                else:
                    tau = modifier.attack_ms if source > runtime.current else modifier.release_ms
                    dt = max(0.0, stamp - runtime.last_update)
                    alpha = 1.0 - math.exp(-dt / max(0.001, tau / 1000.0))
                    smoothed = runtime.current + alpha * (source - runtime.current)
                runtime.current = smoothed
                runtime.last_update = stamp
                current_live[runtime_key] = smoothed

                spec = PERFORMANCE_MODIFIER_TARGETS[modifier.target_id]
                polarity_value = (
                    smoothed
                    if modifier.polarity == "positive"
                    else (smoothed * 2.0 - 1.0)
                )
                offset = polarity_value * (spec.maximum - spec.minimum) * modifier.depth
                contributions[target_key] = contributions.get(target_key, 0.0) + offset

        for runtime_key in tuple(self._runtime):
            if runtime_key not in configured_runtime_keys:
                self._runtime.pop(runtime_key, None)
                self._live_values.pop(runtime_key, None)

        active_targets: set[tuple[str, str]] = set()
        outputs: dict[tuple[str, str], float] = {}
        for target_key, offset in contributions.items():
            layer_id, target_id = target_key
            if target_key not in self._base_values:
                base = get_target(layer_id, target_id)
                if base is None:
                    continue
                self._base_values[target_key] = float(base)
            spec = PERFORMANCE_MODIFIER_TARGETS[target_id]
            value = self._base_values[target_key] + offset
            value = max(spec.minimum, min(spec.maximum, value))
            if set_target(layer_id, target_id, value):
                outputs[target_key] = value
                active_targets.add(target_key)
            else:
                self._base_values.pop(target_key, None)

        for target_key in self._active_targets - active_targets:
            layer_id, target_id = target_key
            base = self._base_values.pop(target_key, None)
            if base is not None:
                set_target(layer_id, target_id, base)

        self._active_targets = active_targets
        self._live_values = current_live
        return outputs
