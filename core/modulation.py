from __future__ import annotations

import math
import time
from dataclasses import asdict, dataclass, field
from typing import Literal

CurveName = Literal["linear", "smoothstep", "exponential"]

SOURCE_RANGES: dict[str, tuple[float, float]] = {
    "audio.rms": (0.0, 1.0),
    "audio.peak": (0.0, 1.0),
    "audio.low": (0.0, 1.0),
    "audio.mid": (0.0, 1.0),
    "audio.high": (0.0, 1.0),
    "audio.onset": (0.0, 1.0),
    "audio.beat_confidence": (0.0, 1.0),
    "audio.bpm_normalized": (0.0, 1.0),
    "transport.intensity": (0.0, 1.0),
    "transport.phase": (0.0, 1.0),
    "transport.bar_phase": (0.0, 1.0),
    "transport.beat_pulse": (0.0, 1.0),
    "transport.downbeat_pulse": (0.0, 1.0),
    "transport.phrase_pulse": (0.0, 1.0),
    "macro.energy": (0.0, 1.0),
    "macro.cutoff": (0.0, 1.0),
}


@dataclass(frozen=True)
class ModulationTargetSpec:
    target_id: str
    label: str
    minimum: float
    maximum: float
    category: str


TARGET_SPECS: dict[str, ModulationTargetSpec] = {
    "master.brightness": ModulationTargetSpec(
        "master.brightness", "Master brightness", -0.5, 0.5, "master"
    ),
    "master.exposure": ModulationTargetSpec(
        "master.exposure", "Master exposure", -2.0, 2.0, "master"
    ),
    "master.contrast": ModulationTargetSpec(
        "master.contrast", "Master contrast", 0.25, 2.25, "master"
    ),
    "master.saturation": ModulationTargetSpec(
        "master.saturation", "Master saturation", 0.0, 2.25, "master"
    ),
    "master.grain": ModulationTargetSpec(
        "master.grain", "Master grain", 0.0, 1.0, "master"
    ),
    "master.glitch": ModulationTargetSpec(
        "master.glitch", "Master glitch", 0.0, 1.0, "master"
    ),
    "master.vignette": ModulationTargetSpec(
        "master.vignette", "Master vignette", 0.0, 1.0, "master"
    ),
    "master.hue": ModulationTargetSpec(
        "master.hue", "Master hue rotation", -180.0, 180.0, "master"
    ),
    "master.chromatic": ModulationTargetSpec(
        "master.chromatic", "Master chromatic aberration", 0.0, 1.0, "master"
    ),
    "master.scanlines": ModulationTargetSpec(
        "master.scanlines", "Master scanlines", 0.0, 1.0, "master"
    ),
    "master.pixelate": ModulationTargetSpec(
        "master.pixelate", "Master pixelation", 0.0, 1.0, "master"
    ),
    "master.posterize": ModulationTargetSpec(
        "master.posterize", "Master posterize", 0.0, 1.0, "master"
    ),
    "master.invert": ModulationTargetSpec(
        "master.invert", "Master invert", 0.0, 1.0, "master"
    ),
    "master.halftone": ModulationTargetSpec(
        "master.halftone", "Master halftone", 0.0, 1.0, "master"
    ),
    "master.solarize": ModulationTargetSpec(
        "master.solarize", "Master solarize", 0.0, 1.0, "master"
    ),
    "master.transform_mix": ModulationTargetSpec(
        "master.transform_mix", "Master transform mix", 0.0, 1.0, "master"
    ),
    "master.kaleidoscope_slices": ModulationTargetSpec(
        "master.kaleidoscope_slices", "Kaleidoscope slices", 2.0, 64.0, "master"
    ),
    "master.kaleidoscope_rotation": ModulationTargetSpec(
        "master.kaleidoscope_rotation", "Kaleidoscope rotation", -180.0, 180.0, "master"
    ),
    "master.kaleidoscope_zoom": ModulationTargetSpec(
        "master.kaleidoscope_zoom", "Kaleidoscope zoom", 0.1, 4.0, "master"
    ),
    "master.mosaic_tiles": ModulationTargetSpec(
        "master.mosaic_tiles", "Mosaic tile count", 4.0, 512.0, "master"
    ),
    "master.pixel_sort_amount": ModulationTargetSpec(
        "master.pixel_sort_amount", "Pixel-sort displacement", 0.0, 1.0, "master"
    ),
    "master.pixel_sort_threshold": ModulationTargetSpec(
        "master.pixel_sort_threshold", "Pixel-sort threshold", 0.0, 1.0, "master"
    ),
    "master.edge_amount": ModulationTargetSpec(
        "master.edge_amount", "Edge extraction", 0.0, 1.0, "master"
    ),
    "master.dither": ModulationTargetSpec(
        "master.dither", "Ordered dithering", 0.0, 1.0, "master"
    ),
    "master.displacement_amount": ModulationTargetSpec(
        "master.displacement_amount", "Layer-map displacement", -1.0, 1.0, "master"
    ),
    "master.displacement_scale": ModulationTargetSpec(
        "master.displacement_scale", "Displacement scale", 0.1, 8.0, "master"
    ),
    "master.feedback_amount": ModulationTargetSpec(
        "master.feedback_amount", "Feedback amount", 0.0, 1.0, "master"
    ),
    "master.feedback_decay": ModulationTargetSpec(
        "master.feedback_decay", "Feedback decay", 0.0, 1.0, "master"
    ),
    "master.feedback_zoom": ModulationTargetSpec(
        "master.feedback_zoom", "Feedback zoom", 0.5, 2.0, "master"
    ),
    "master.feedback_rotation": ModulationTargetSpec(
        "master.feedback_rotation", "Feedback rotation", -180.0, 180.0, "master"
    ),
    "master.feedback_translate_x": ModulationTargetSpec(
        "master.feedback_translate_x", "Feedback horizontal translation", -0.25, 0.25, "master"
    ),
    "master.feedback_translate_y": ModulationTargetSpec(
        "master.feedback_translate_y", "Feedback vertical translation", -0.25, 0.25, "master"
    ),
    "master.feedback_color_shift": ModulationTargetSpec(
        "master.feedback_color_shift", "Feedback colour shift", 0.0, 1.0, "master"
    ),
    "master.feedback_distortion": ModulationTargetSpec(
        "master.feedback_distortion", "Feedback distortion", 0.0, 1.0, "master"
    ),
    "master.feedback_motion_warp": ModulationTargetSpec(
        "master.feedback_motion_warp", "Feedback motion warp", 0.0, 1.0, "master"
    ),
    "master.feedback_datamosh": ModulationTargetSpec(
        "master.feedback_datamosh", "Feedback datamosh blocks", 0.0, 1.0, "master"
    ),
    "master.feedback_delay_frames": ModulationTargetSpec(
        "master.feedback_delay_frames", "Feedback delay", 0.0, 3.0, "master"
    ),
    "selected_layer.opacity": ModulationTargetSpec(
        "selected_layer.opacity", "Selected layer opacity", 0.0, 1.0, "layer"
    ),
    "selected_layer.rotation": ModulationTargetSpec(
        "selected_layer.rotation", "Selected layer rotation", -180.0, 180.0, "layer"
    ),
    "selected_layer.scale": ModulationTargetSpec(
        "selected_layer.scale", "Selected layer scale", 0.05, 2.0, "layer"
    ),
    "selected_layer.position_x": ModulationTargetSpec(
        "selected_layer.position_x", "Selected layer X position", 0.0, 1.0, "layer"
    ),
    "selected_layer.position_y": ModulationTargetSpec(
        "selected_layer.position_y", "Selected layer Y position", 0.0, 1.0, "layer"
    ),
    "layer_fx.mix": ModulationTargetSpec(
        "layer_fx.mix", "Layer FX mix", 0.0, 1.0, "layer"
    ),
    "layer_fx.monochrome": ModulationTargetSpec(
        "layer_fx.monochrome", "Layer FX monochrome", 0.0, 1.0, "layer"
    ),
    "layer_fx.threshold": ModulationTargetSpec(
        "layer_fx.threshold", "Layer FX threshold", 0.0, 1.0, "layer"
    ),
    "layer_fx.contrast": ModulationTargetSpec(
        "layer_fx.contrast", "Layer FX contrast", 0.0, 2.5, "layer"
    ),
    "layer_fx.brightness": ModulationTargetSpec(
        "layer_fx.brightness", "Layer FX brightness", -0.5, 0.5, "layer"
    ),
    "layer_fx.chromatic": ModulationTargetSpec(
        "layer_fx.chromatic", "Layer FX chromatic aberration", 0.0, 1.0, "layer"
    ),
    "layer_fx.scanlines": ModulationTargetSpec(
        "layer_fx.scanlines", "Layer FX scanlines", 0.0, 1.0, "layer"
    ),
    "layer_fx.posterize": ModulationTargetSpec(
        "layer_fx.posterize", "Layer FX posterize", 0.0, 1.0, "layer"
    ),
    "layer_fx.invert": ModulationTargetSpec(
        "layer_fx.invert", "Layer FX invert", 0.0, 1.0, "layer"
    ),
    "layer_fx.hue": ModulationTargetSpec(
        "layer_fx.hue", "Layer FX hue rotation", -180.0, 180.0, "layer"
    ),
    "layer_fx.saturation": ModulationTargetSpec(
        "layer_fx.saturation", "Layer FX saturation", 0.0, 2.5, "layer"
    ),

    "generator.animation_speed": ModulationTargetSpec(
        "generator.animation_speed", "Generator animation speed", 0.0, 8.0, "generator"
    ),
    "generator.animation_amount": ModulationTargetSpec(
        "generator.animation_amount", "Generator motion amount", 0.0, 360.0, "generator"
    ),
    "generator.density": ModulationTargetSpec(
        "generator.density", "Generator density", 1.0, 120.0, "generator"
    ),
    "generator.rotation": ModulationTargetSpec(
        "generator.rotation", "Geometry rotation", -360.0, 360.0, "generator"
    ),
    "generator.text_animation_speed": ModulationTargetSpec(
        "generator.text_animation_speed", "Text animation speed", 0.0, 8.0, "generator"
    ),
    "generator.text_animation_amount": ModulationTargetSpec(
        "generator.text_animation_amount", "Text animation amount", 0.0, 0.18, "generator"
    ),
    "generator.text_animation_columns": ModulationTargetSpec(
        "generator.text_animation_columns", "Text animation reveal steps", 2.0, 80.0, "generator"
    ),
    "generator.font_size": ModulationTargetSpec(
        "generator.font_size", "Text font size", 12.0, 420.0, "generator"
    ),
    "generator.letter_spacing": ModulationTargetSpec(
        "generator.letter_spacing", "Text letter spacing", -8.0, 48.0, "generator"
    ),
    "generator.waveform_amplitude": ModulationTargetSpec(
        "generator.waveform_amplitude", "Waveform amplitude", 0.01, 0.48, "generator"
    ),
    "generator.waveform_frequency": ModulationTargetSpec(
        "generator.waveform_frequency", "Waveform frequency", 0.1, 24.0, "generator"
    ),
    "generator.particle_speed": ModulationTargetSpec(
        "generator.particle_speed", "Particle speed", 0.0, 2.0, "generator"
    ),
    "generator.particle_size": ModulationTargetSpec(
        "generator.particle_size", "Particle size", 0.02, 0.8, "generator"
    ),
    "generator.particle_spread": ModulationTargetSpec(
        "generator.particle_spread", "Particle spread", 0.0, 1.0, "generator"
    ),
    "generator.particle_trail": ModulationTargetSpec(
        "generator.particle_trail", "Particle trail", 0.0, 1.0, "generator"
    ),
    "generator.particle_emission_rate": ModulationTargetSpec(
        "generator.particle_emission_rate", "Particle emission rate", 0.0, 3000.0, "generator"
    ),
    "generator.particle_system_size": ModulationTargetSpec(
        "generator.particle_system_size", "Particle System 2.0 size", 1.0, 48.0, "generator"
    ),
    "generator.particle_lifetime": ModulationTargetSpec(
        "generator.particle_lifetime", "Particle lifetime", 0.25, 60.0, "generator"
    ),
    "generator.particle_turbulence": ModulationTargetSpec(
        "generator.particle_turbulence", "Particle turbulence", 0.0, 1.5, "generator"
    ),
    "generator.particle_force_strength": ModulationTargetSpec(
        "generator.particle_force_strength", "Particle force strength", 0.0, 4.0, "generator"
    ),
    "generator.particle_reform_strength": ModulationTargetSpec(
        "generator.particle_reform_strength",
        "Particle source reform strength",
        0.0,
        4.0,
        "generator",
    ),
    "overlay.playback_speed": ModulationTargetSpec(
        "overlay.playback_speed", "Animated overlay playback speed", 0.1, 4.0, "overlay"
    ),
    "overlay.frame_hold": ModulationTargetSpec(
        "overlay.frame_hold", "Animated overlay frame hold", 1.0, 24.0, "overlay"
    ),
    "automation.loop_probability": ModulationTargetSpec(
        "automation.loop_probability", "Auto loop probability", 0.0, 1.0, "automation"
    ),
    "automation.clip_switch_probability": ModulationTargetSpec(
        "automation.clip_switch_probability", "Auto clip switch probability", 0.0, 1.0, "automation"
    ),
    "automation.cut_interval": ModulationTargetSpec(
        "automation.cut_interval", "Auto minimum cut interval", 1.0, 60.0, "automation"
    ),
    "automation.min_segment_seconds": ModulationTargetSpec(
        "automation.min_segment_seconds", "Auto minimum segment length", 0.5, 30.0, "automation"
    ),
    "automation.max_segment_seconds": ModulationTargetSpec(
        "automation.max_segment_seconds", "Auto maximum segment length", 0.5, 60.0, "automation"
    ),
    "automation.layout_interval": ModulationTargetSpec(
        "automation.layout_interval", "Auto layout interval", 2.0, 120.0, "automation"
    ),
    "automation.effect_interval": ModulationTargetSpec(
        "automation.effect_interval", "Auto look interval", 2.0, 120.0, "automation"
    ),
    "automation.generator_interval": ModulationTargetSpec(
        "automation.generator_interval", "Auto generator / text interval", 3.0, 120.0, "automation"
    ),
}


@dataclass
class ModulationRoute:
    route_id: str
    source_id: str
    target_id: str
    input_min: float = 0.0
    input_max: float = 1.0
    output_min: float | None = None
    output_max: float | None = None
    curve: CurveName = "linear"
    inverted: bool = False
    smoothing_ms: float = 80.0
    attack_ms: float = 25.0
    release_ms: float = 220.0
    hold_ms: float = 0.0
    intensity_ceiling: float = 1.0
    enabled: bool = True

    def normalize(self) -> None:
        is_bank_source = (
                self.source_id.startswith("modulator.")
                and bool(self.source_id.removeprefix("modulator.").strip())
        )
        is_performance_macro = (
                self.source_id.startswith("performance_macro.")
                and bool(self.source_id.removeprefix("performance_macro.").strip())
        )
        if (
                self.source_id not in SOURCE_RANGES
                and not is_bank_source
                and not is_performance_macro
        ):
            raise ValueError(f"Unknown modulation source: {self.source_id}")
        if self.target_id not in TARGET_SPECS:
            raise ValueError(f"Unknown modulation target: {self.target_id}")
        self.input_min = max(0.0, min(1.0, float(self.input_min)))
        self.input_max = max(0.0, min(1.0, float(self.input_max)))
        if self.input_max <= self.input_min:
            raise ValueError("Modulation input maximum must exceed input minimum.")
        spec = TARGET_SPECS[self.target_id]
        self.output_min = (
            spec.minimum if self.output_min is None
            else float(self.output_min)
        )
        self.output_max = (
            spec.maximum if self.output_max is None
            else float(self.output_max)
        )
        if not (
                spec.minimum <= self.output_min <= spec.maximum
                and spec.minimum <= self.output_max <= spec.maximum
        ):
            raise ValueError(
                f"Output range for {self.target_id} exceeds its registered safety range."
            )
        if self.curve not in {"linear", "smoothstep", "exponential"}:
            self.curve = "linear"
        self.smoothing_ms = max(0.0, min(3000.0, float(self.smoothing_ms)))
        self.attack_ms = max(1.0, min(2000.0, float(self.attack_ms)))
        self.release_ms = max(1.0, min(5000.0, float(self.release_ms)))
        self.hold_ms = max(0.0, min(5000.0, float(self.hold_ms)))
        self.intensity_ceiling = max(0.0, min(1.0, float(self.intensity_ceiling)))
        self.enabled = bool(self.enabled)

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> ModulationRoute:
        allowed = set(cls.__dataclass_fields__)
        clean = {key: value for key, value in values.items() if key in allowed}
        route = cls(**clean)
        route.normalize()
        return route


@dataclass
class _RouteRuntime:
    current: float | None = None
    last_output: float | None = None
    last_seen: float = 0.0
    last_update: float = 0.0


@dataclass
class ModulationMatrix:
    routes: list[ModulationRoute] = field(default_factory=list)
    _runtime: dict[str, _RouteRuntime] = field(default_factory=dict, repr=False)
    _manual_until: dict[str, float] = field(default_factory=dict, repr=False)
    _last_active_targets: set[str] = field(default_factory=set, repr=False)
    _outputs: dict[str, float] = field(default_factory=dict, repr=False)

    def add_route(self, route: ModulationRoute) -> None:
        route.normalize()
        if any(item.route_id == route.route_id for item in self.routes):
            raise ValueError(f"Duplicate modulation route ID: {route.route_id}")
        if any(item.target_id == route.target_id for item in self.routes):
            raise ValueError(f"Target already has a modulation route: {route.target_id}")
        self.routes.append(route)
        self._runtime[route.route_id] = _RouteRuntime()

    def update_route(self, route_id: str, changes: dict[str, object]) -> None:
        current = next((item for item in self.routes if item.route_id == route_id), None)
        if current is None:
            raise KeyError(f"Unknown modulation route: {route_id}")
        values = current.to_dict()
        values.update(changes)
        updated = ModulationRoute.from_dict(values)
        if any(
                item.route_id != route_id and item.target_id == updated.target_id
                for item in self.routes
        ):
            raise ValueError(f"Target already has a modulation route: {updated.target_id}")
        self.routes = [
            updated if item.route_id == route_id else item
            for item in self.routes
        ]
        self._runtime[route_id] = _RouteRuntime()
        self._last_active_targets.discard(current.target_id)
        self._outputs.pop(current.target_id, None)

    def remove_route(self, route_id: str) -> None:
        self.routes = [item for item in self.routes if item.route_id != route_id]
        self._runtime.pop(route_id, None)

    def set_route_enabled(self, route_id: str, enabled: bool) -> None:
        for route in self.routes:
            if route.route_id == route_id:
                route.enabled = bool(enabled)
                return

    def manual_override(
            self,
            target_id: str,
            duration_seconds: float = 3.0,
            now: float | None = None,
    ) -> None:
        if target_id not in TARGET_SPECS:
            return
        stamp = time.monotonic() if now is None else float(now)
        self._manual_until[target_id] = stamp + max(0.0, float(duration_seconds))

    @staticmethod
    def _map_value(route: ModulationRoute, source_value: float) -> float:
        value = (source_value - route.input_min) / (route.input_max - route.input_min)
        value = max(0.0, min(1.0, value))
        if route.inverted:
            value = 1.0 - value
        if route.curve == "smoothstep":
            value = value * value * (3.0 - 2.0 * value)
        elif route.curve == "exponential":
            value = value * value
        value = min(route.intensity_ceiling, value)
        assert route.output_min is not None and route.output_max is not None
        return route.output_min + value * (route.output_max - route.output_min)

    def evaluate(
            self,
            sources: dict[str, float],
            now: float | None = None,
    ) -> tuple[dict[str, float], set[str]]:
        stamp = time.monotonic() if now is None else float(now)
        outputs: dict[str, float] = {}
        active_targets: set[str] = set()

        for route in self.routes:
            route.normalize()
            if not route.enabled:
                continue
            manual_until = self._manual_until.get(route.target_id, 0.0)
            if stamp < manual_until:
                continue
            raw = sources.get(route.source_id)
            runtime = self._runtime.setdefault(route.route_id, _RouteRuntime())
            if raw is None:
                if (
                        runtime.last_output is not None
                        and route.hold_ms > 0
                        and stamp - runtime.last_seen <= route.hold_ms / 1000.0
                ):
                    mapped = runtime.last_output
                else:
                    continue
            else:
                value = float(raw)
                if not math.isfinite(value):
                    continue
                mapped = self._map_value(route, max(0.0, min(1.0, value)))
                runtime.last_seen = stamp

            if runtime.current is None:
                smoothed = mapped
            else:
                previous = runtime.current
                tau_ms = route.attack_ms if mapped > previous else route.release_ms
                if route.smoothing_ms > 0:
                    tau_ms = max(tau_ms, route.smoothing_ms)
                dt = max(0.0, stamp - runtime.last_update)
                alpha = 1.0 if tau_ms <= 0 else 1.0 - math.exp(
                    -dt / max(0.001, tau_ms / 1000.0)
                )
                smoothed = previous + alpha * (mapped - previous)

            runtime.current = smoothed
            runtime.last_output = mapped
            runtime.last_update = stamp
            outputs[route.target_id] = smoothed
            active_targets.add(route.target_id)

        released = self._last_active_targets - active_targets
        self._last_active_targets = active_targets
        self._outputs = dict(outputs)
        return outputs, released

    def reset_runtime(self) -> None:
        self._runtime.clear()
        self._manual_until.clear()
        self._last_active_targets.clear()
        self._outputs.clear()

    def to_dict(self) -> list[dict[str, object]]:
        return [route.to_dict() for route in self.routes]

    def load_dict(self, values: object) -> None:
        routes: list[ModulationRoute] = []
        if isinstance(values, list):
            for item in values:
                if not isinstance(item, dict):
                    continue
                try:
                    routes.append(ModulationRoute.from_dict(item))
                except (ValueError, TypeError, KeyError):
                    continue
        self.routes = routes
        self.reset_runtime()

    def active_targets(self) -> set[str]:
        return set(self._last_active_targets)

    def outputs(self) -> dict[str, float]:
        return dict(self._outputs)
