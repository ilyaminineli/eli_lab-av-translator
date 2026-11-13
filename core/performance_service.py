from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

from core.modulation import ModulationMatrix, ModulationRoute
from core.modulator_bank import ModulatorBank
from core.performance_modifiers import LayerPerformanceModifier
from generators.catalog import normalize_settings


@dataclass
class PerformanceModePlan:
    """Stable user preferences for an autonomous show; no live worker handles."""

    osc_bind_address: str = "127.0.0.1"
    osc_port: int = 57121
    audio_device_id: str = ""
    audio_test_signal: bool = False
    prefer_loopback: bool = True
    start_automation: bool = True
    automation_duration_seconds: float | None = None
    automation_settings: dict[str, Any] = field(
        default_factory=lambda: {
            "performance_style": "generative",
            "musical_sync": "phrase",
        }
    )
    stop_automation_on_patch_stop: bool = True
    install_default_mappings: bool = True

    def normalize(self) -> None:
        self.osc_bind_address = str(self.osc_bind_address).strip() or "127.0.0.1"
        self.osc_port = max(1024, min(65535, int(self.osc_port)))
        self.audio_device_id = str(self.audio_device_id).strip()
        self.audio_test_signal = bool(self.audio_test_signal)
        self.prefer_loopback = bool(self.prefer_loopback)
        self.start_automation = bool(self.start_automation)
        self.stop_automation_on_patch_stop = bool(self.stop_automation_on_patch_stop)
        self.install_default_mappings = bool(self.install_default_mappings)
        if not isinstance(self.automation_settings, dict):
            self.automation_settings = {}
        if self.automation_duration_seconds is not None:
            self.automation_duration_seconds = max(
                1.0, float(self.automation_duration_seconds)
            )

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return asdict(self)


@dataclass
class PerformanceModeSnapshot:
    enabled: bool = False
    phase: str = "off"
    started_at: float = 0.0
    last_event_at: float = 0.0
    last_event: str = ""
    source_session: str = ""
    automation_armed: bool = False
    automation_running: bool = False
    osc_owned: bool = False
    audio_owned: bool = False
    audio_status: str = "disabled"
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PerformanceModeService:
    """Small state machine for the one-button live-performance lifecycle."""

    def __init__(self) -> None:
        self.snapshot_state = PerformanceModeSnapshot()
        self.plan = PerformanceModePlan()

    @property
    def enabled(self) -> bool:
        return self.snapshot_state.enabled

    def begin(self, plan: PerformanceModePlan) -> None:
        if self.enabled:
            raise RuntimeError("Performance Mode is already enabled.")
        plan.normalize()
        self.plan = plan
        self.snapshot_state = PerformanceModeSnapshot(
            enabled=True,
            phase="arming",
            started_at=time.monotonic(),
            automation_armed=plan.start_automation,
            audio_status=(
                "starting"
                if plan.audio_device_id or plan.audio_test_signal
                else "disabled"
            ),
        )

    def mark_armed(self, *, osc_owned: bool, audio_owned: bool, audio_status: str) -> None:
        state = self.snapshot_state
        state.osc_owned = bool(osc_owned)
        state.audio_owned = bool(audio_owned)
        state.audio_status = str(audio_status)
        state.phase = "waiting_for_sonic_pi"
        state.last_event = "performance_mode.armed"
        state.last_event_at = time.monotonic()

    def mark_live(self, event: str, session_id: str = "") -> None:
        state = self.snapshot_state
        state.phase = "live"
        state.last_event = str(event)
        state.last_event_at = time.monotonic()
        if session_id:
            state.source_session = str(session_id)
        state.error = ""

    def mark_waiting(self, event: str, error: str = "") -> None:
        state = self.snapshot_state
        if state.enabled:
            state.phase = "waiting_for_sonic_pi"
        state.last_event = str(event)
        state.last_event_at = time.monotonic()
        state.error = str(error)

    def mark_degraded(self, event: str, error: str) -> None:
        state = self.snapshot_state
        if state.enabled:
            state.phase = "degraded"
        state.last_event = str(event)
        state.last_event_at = time.monotonic()
        state.error = str(error)

    def set_automation_armed(self, armed: bool, running: bool = False) -> None:
        self.snapshot_state.automation_armed = bool(armed)
        self.snapshot_state.automation_running = bool(running)

    def note_event(self, event: str, session_id: str = "") -> None:
        state = self.snapshot_state
        state.last_event = str(event)
        state.last_event_at = time.monotonic()
        if session_id:
            state.source_session = str(session_id)

    def stop(self) -> PerformanceModeSnapshot:
        previous = self.snapshot_state
        stopped = PerformanceModeSnapshot(
            enabled=False,
            phase="off",
            last_event="performance_mode.stopped",
            last_event_at=time.monotonic(),
            audio_status="stopped",
        )
        self.snapshot_state = stopped
        return previous

    def snapshot(self) -> dict[str, Any]:
        value = self.snapshot_state.to_dict()
        value["plan"] = self.plan.to_dict()
        return value


# The global matrix handles master-output and AUTO PERFORMANCE parameters. Layer
# domains use the same LayerPerformanceModifier engine used by authored modifiers.
DEFAULT_MATRIX_ROUTES: tuple[tuple[str, str, float, float, bool, float], ...] = (
    ("performance_macro.chaos", "master.glitch", 0.0, 0.82, False, 0.78),
    ("performance_macro.pressure", "master.edge_amount", 0.0, 0.72, False, 0.56),
    ("macro.cutoff", "master.saturation", 0.55, 1.65, False, 0.82),
    ("performance_macro.pressure", "master.contrast", 1.0, 1.75, False, 0.72),
    ("audio.high", "master.grain", 0.0, 0.48, False, 0.55),
    ("macro.energy", "automation.clip_switch_probability", 0.12, 0.82, False, 0.78),
    ("macro.cutoff", "automation.cut_interval", 24.0, 3.0, False, 0.72),
    ("transport.intensity", "automation.layout_interval", 34.0, 7.0, False, 0.68),
    ("macro.energy", "automation.generator_interval", 36.0, 9.0, False, 0.62),
    ("macro.cutoff", "automation.effect_interval", 30.0, 8.0, False, 0.58),
    ("audio.onset", "automation.min_segment_seconds", 18.0, 3.0, False, 0.55),
    ("performance_macro.chaos", "master.chromatic", 0.0, 0.72, False, 0.58),
    ("transport.beat_pulse", "master.scanlines", 0.02, 0.36, False, 0.45),
    ("macro.cutoff", "master.posterize", 0.0, 0.24, False, 0.38),
    ("audio.onset", "master.invert", 0.0, 0.10, False, 0.32),
    ("macro.energy", "master.hue", -12.0, 12.0, False, 0.4),
    ("performance_macro.fragment", "master.pixelate", 0.0, 0.88, False, 0.66),
    ("macro.cutoff", "master.halftone", 0.0, 0.20, False, 0.30),
    ("audio.onset", "master.solarize", 0.0, 0.12, False, 0.28),
    ("performance_macro.depth", "master.transform_mix", 0.18, 0.78, False, 0.70),
    ("transport.beat_pulse", "master.kaleidoscope_rotation", -8.0, 8.0, False, 0.5),
    ("audio.low", "master.kaleidoscope_zoom", 0.92, 1.18, False, 0.48),
    ("performance_macro.density", "master.kaleidoscope_slices", 4.0, 16.0, False, 0.52),
    ("performance_macro.density", "master.mosaic_tiles", 4.0, 180.0, False, 0.64),
    ("performance_macro.fragment", "master.pixel_sort_amount", 0.0, 0.78, False, 0.62),
    ("audio.high", "master.pixel_sort_threshold", 0.55, 0.82, False, 0.42),
    ("audio.high", "master.edge_amount", 0.0, 0.48, False, 0.42),
    ("transport.beat_pulse", "master.dither", 0.0, 0.24, False, 0.35),
    ("performance_macro.chaos", "master.displacement_amount", 0.0, 0.88, False, 0.62),
    ("performance_macro.fragment", "master.displacement_scale", 1.0, 4.0, False, 0.58),
    ("performance_macro.depth", "master.feedback_amount", 0.0, 0.78, False, 0.7),
    ("performance_macro.decay", "master.feedback_decay", 0.82, 0.995, False, 0.64),
    ("performance_macro.depth", "master.feedback_zoom", 1.0, 1.55, False, 0.58),
    ("performance_macro.chaos", "master.feedback_rotation", 0.0, 14.0, False, 0.5),
    ("transport.beat_pulse", "master.feedback_translate_x", -0.025, 0.025, False, 0.38),
    ("transport.phrase_pulse", "master.feedback_translate_y", -0.025, 0.025, False, 0.38),
    ("audio.high", "master.feedback_color_shift", 0.0, 0.22, False, 0.35),
    ("performance_macro.pressure", "master.feedback_distortion", 0.0, 0.78, False, 0.58),
    ("performance_macro.chaos", "master.feedback_motion_warp", 0.0, 0.62, False, 0.55),
    ("audio.onset", "master.feedback_datamosh", 0.0, 0.18, False, 0.38),
    ("transport.beat_pulse", "master.feedback_delay_frames", 0.0, 2.0, False, 0.3),
)

# Earlier autonomous defaults animated these CPU-rasterized properties. Remove only
# the exact generated defaults and replace them with shader/layer-transform targets.
LEGACY_CPU_RASTER_MODIFIERS: dict[str, set[tuple[str, str]]] = {
    "geometry": {
        ("AUTO · beat rotation", "generator.rotation"),
        ("AUTO · phrase density", "generator.density"),
    },
    "text": {
        ("AUTO · phrase type scale", "generator.font_size"),
        ("AUTO · onset tracking", "generator.letter_spacing"),
    },
    "waveform": {
        ("AUTO · bass amplitude", "generator.waveform_amplitude"),
        ("AUTO · cutoff frequency", "generator.waveform_frequency"),
        ("AUTO · beat amplitude", "generator.waveform_amplitude"),
    },
}

DEFAULT_MODULATORS: tuple[tuple[str, str], ...] = (
    ("follower-sonic-pi-energy", "AUTO · Sonic Pi energy"),
    ("follower-sonic-pi-cutoff", "AUTO · Sonic Pi cutoff"),
    ("env-beat-pluck", "AUTO · Beat envelope"),
    ("env-audio-onset", "AUTO · Audio onset"),
    ("lfo-sine-swell", "AUTO · Phrase swell"),
)


def install_default_performance_macro_routes(matrix: ModulationMatrix) -> int:
    """Install standalone master routes for the six normalized macro outputs."""
    existing_targets = {route.target_id for route in matrix.routes}
    added = 0
    for source, target, low, high, inverted, ceiling in DEFAULT_MATRIX_ROUTES:
        if not source.startswith("performance_macro."):
            continue
        if target in existing_targets:
            existing = next(
                (route for route in matrix.routes if route.target_id == target),
                None,
            )
            if existing is not None and existing.route_id.startswith("auto-performance-"):
                changes = {
                    "source_id": source,
                    "output_min": low,
                    "output_max": high,
                    "inverted": inverted,
                    "intensity_ceiling": ceiling,
                }
                if any(getattr(existing, key) != value for key, value in changes.items()):
                    matrix.update_route(existing.route_id, changes)
            continue
        matrix.add_route(ModulationRoute(
            route_id=f"performance-macro-{target.replace('.', '-')}",
            source_id=source,
            target_id=target,
            input_min=0.0,
            input_max=1.0,
            output_min=low,
            output_max=high,
            curve="smoothstep",
            inverted=inverted,
            smoothing_ms=80.0,
            attack_ms=35.0,
            release_ms=260.0,
            hold_ms=0.0,
            intensity_ceiling=ceiling,
            enabled=True,
        ))
        existing_targets.add(target)
        added += 1
    return added


def install_default_matrix_routes(matrix: ModulationMatrix) -> int:
    """Add missing autonomous routes while preserving every existing custom route."""
    existing_targets = {route.target_id for route in matrix.routes}
    added = 0
    for source, target, low, high, inverted, ceiling in DEFAULT_MATRIX_ROUTES:
        if target in existing_targets:
            existing = next(
                (route for route in matrix.routes if route.target_id == target), None
            )
            if existing is not None and existing.route_id.startswith("auto-performance-"):
                changes = {
                    "source_id": source,
                    "output_min": low,
                    "output_max": high,
                    "inverted": inverted,
                    "intensity_ceiling": ceiling,
                    "enabled": True,
                }
                if any(getattr(existing, key) != value for key, value in changes.items()):
                    matrix.update_route(existing.route_id, changes)
            continue
        route = ModulationRoute(
            route_id=f"auto-performance-{target.replace('.', '-')}",
            source_id=source,
            target_id=target,
            input_min=0.0,
            input_max=1.0,
            output_min=low,
            output_max=high,
            curve="smoothstep",
            inverted=inverted,
            smoothing_ms=120.0,
            attack_ms=45.0,
            release_ms=420.0,
            hold_ms=180.0,
            intensity_ceiling=ceiling,
            enabled=True,
        )
        matrix.add_route(route)
        existing_targets.add(target)
        added += 1
    return added


def install_default_modulators(bank: ModulatorBank) -> dict[str, str]:
    """Ensure the reusable followers, beat/onset envelopes and phrase LFO exist."""
    result: dict[str, str] = {}
    by_name = {item.name: item for item in bank.list_modulators()}
    for preset_id, name in DEFAULT_MODULATORS:
        existing = by_name.get(name)
        if existing is not None:
            existing.enabled = True
            result[preset_id] = existing.modulator_id
            continue
        item = bank.instantiate_preset(preset_id)
        item.name = name
        bank.update(item)
        result[preset_id] = item.modulator_id
        by_name[name] = item
    return result


def _modifier(
        name: str,
        source_id: str,
        target_id: str,
        depth: float,
        curve: str = "smoothstep",
        attack_ms: float = 35.0,
        release_ms: float = 300.0,
        polarity: str = "positive",
) -> LayerPerformanceModifier:
    return LayerPerformanceModifier(
        modifier_id=(
                        f"auto-{source_id.removeprefix('modulator.').replace('.', '-')}-"
                        f"{target_id.replace('.', '-')}"
                    )[:40],
        name=f"AUTO · {name}",
        source_id=source_id,
        target_id=target_id,
        depth=depth,
        polarity=polarity,
        curve=curve,
        attack_ms=attack_ms,
        release_ms=release_ms,
        enabled=True,
    )


def _performance_macro_modifier(
        macro_id: str,
        name: str,
        target_id: str,
        depth: float,
) -> LayerPerformanceModifier:
    source_id = f"performance_macro.{macro_id}"
    item = _modifier(name, source_id, target_id, depth)
    item.modifier_id = f"macro-{macro_id}-{target_id.replace('.', '-')}"[:40]
    item.name = f"MACRO · {macro_id.upper()} · {name}"[:48]
    return item


def install_default_performance_macro_modifiers(layers: list[object]) -> int:
    """Install reusable macro-to-layer mappings without requiring AUTO PERFORMANCE."""
    universal = {
        "chaos": (
            ("rotation accent", "layer.rotation", 0.08),
            ("chromatic aberration", "layer_fx.chromatic", 0.14),
            ("invert accent", "layer_fx.invert", 0.08),
            ("scanline intensity", "layer_fx.scanlines", 0.10),
        ),
        "density": (
            ("layer scale density", "layer.scale", 0.06),
            ("threshold density", "layer_fx.threshold", 0.06),
        ),
        "depth": (
            ("layer scale depth", "layer.scale", 0.12),
            ("horizontal depth", "layer.position_x", 0.05),
            ("vertical depth", "layer.position_y", 0.05),
        ),
        "decay": (("effect persistence", "layer_fx.mix", 0.10),),
        "pressure": (
            ("contrast pressure", "layer_fx.contrast", 0.12),
            ("threshold pressure", "layer_fx.threshold", 0.10),
            ("brightness pressure", "layer_fx.brightness", 0.06),
        ),
        "fragment": (
            ("posterize fragments", "layer_fx.posterize", 0.12),
            ("chromatic fragments", "layer_fx.chromatic", 0.10),
        ),
    }
    generator = {
        "geometry": (
            ("chaos", "motion amount", "generator.animation_amount", 0.12),
            ("density", "geometry density", "generator.density", 0.10),
            ("depth", "motion speed", "generator.animation_speed", 0.10),
            ("fragment", "fragmented motion", "generator.animation_amount", 0.10),
        ),
        "text": (
            ("chaos", "glyph motion", "generator.text_animation_amount", 0.18),
            ("density", "reveal density", "generator.text_animation_columns", 0.12),
            ("decay", "scroll speed", "generator.text_animation_speed", 0.08),
            ("pressure", "text distortion", "generator.text_animation_amount", 0.10),
            ("fragment", "glyph fragmentation", "generator.text_animation_amount", 0.18),
        ),
        "waveform": (
            ("chaos", "waveform movement", "generator.animation_amount", 0.10),
            ("density", "waveform density", "generator.density", 0.10),
            ("depth", "waveform motion speed", "generator.animation_speed", 0.08),
            ("pressure", "waveform amplitude", "generator.waveform_amplitude", 0.12),
        ),
        "particles": (
            ("chaos", "particle speed", "generator.particle_speed", 0.14),
            ("density", "particle density", "generator.density", 0.10),
            ("depth", "particle trails", "generator.particle_trail", 0.12),
            ("decay", "particle trail persistence", "generator.particle_trail", 0.18),
            ("pressure", "particle size", "generator.particle_size", 0.08),
            ("fragment", "particle spread", "generator.particle_spread", 0.12),
        ),
        "particle_system_2": (
            ("chaos", "particle speed", "generator.particle_speed", 0.12),
            ("chaos", "particle turbulence", "generator.particle_turbulence", 0.12),
            ("density", "continuous emission", "generator.particle_emission_rate", 0.16),
            ("density", "particle radius", "generator.particle_system_size", 0.10),
            ("depth", "particle trails", "generator.particle_trail", 0.14),
            ("depth", "source reformation", "generator.particle_reform_strength", 0.10),
            ("decay", "particle lifetime", "generator.particle_lifetime", 0.14),
            ("decay", "particle persistence", "generator.particle_trail", 0.18),
            ("pressure", "particle force", "generator.particle_force_strength", 0.12),
            ("pressure", "particle turbulence", "generator.particle_turbulence", 0.10),
            ("fragment", "particle spread", "generator.particle_spread", 0.14),
        ),
    }
    count = 0
    for layer in layers:
        if getattr(layer, "locked", False):
            continue
        configured = getattr(layer, "performance_modifiers", None)
        if not isinstance(configured, list):
            configured = []
            layer.performance_modifiers = configured
        existing = {
            (str(raw.get("source_id", "")), str(raw.get("target_id", "")))
            for raw in configured if isinstance(raw, dict)
        }
        candidates = [
            _performance_macro_modifier(macro_id, name, target, depth)
            for macro_id, mappings in universal.items()
            for name, target, depth in mappings
        ]
        if getattr(layer, "source_type", "") == "generator":
            kind = str(getattr(layer, "generator_type", "") or "")
            candidates.extend(
                _performance_macro_modifier(macro_id, name, target, depth)
                for macro_id, name, target, depth in generator.get(kind, ())
            )
        for item in candidates:
            item.normalize()
            key = (item.source_id, item.target_id)
            if key in existing:
                continue
            configured.append(item.to_dict())
            existing.add(key)
            count += 1
    return count


def install_default_layer_modifiers(
        layers: list[object],
        modulator_ids: dict[str, str],
) -> int:
    """Install GPU-friendly curves and migrate the earlier CPU-raster defaults."""
    energy = f"modulator.{modulator_ids['follower-sonic-pi-energy']}"
    cutoff = f"modulator.{modulator_ids['follower-sonic-pi-cutoff']}"
    beat = f"modulator.{modulator_ids['env-beat-pluck']}"
    onset = f"modulator.{modulator_ids['env-audio-onset']}"
    swell = f"modulator.{modulator_ids['lfo-sine-swell']}"
    count = 0

    for layer in layers:
        configured = getattr(layer, "performance_modifiers", None)
        if not isinstance(configured, list):
            continue

        kind = layer.generator_type if layer.source_type == "generator" else None
        legacy = LEGACY_CPU_RASTER_MODIFIERS.get(str(kind), set())
        if legacy:
            configured[:] = [
                raw for raw in configured
                if not (
                        isinstance(raw, dict)
                        and str(raw.get("modifier_id", "")).startswith("auto-")
                        and (
                            str(raw.get("name", "")),
                            str(raw.get("target_id", "")),
                        ) in legacy
                )
            ]
        # Migrate prior AUTO curves even on currently locked layers; do not
        # install any new defaults until the layer is unlocked.
        if getattr(layer, "locked", False):
            continue

        existing_records = {
            (str(raw.get("source_id", "")), str(raw.get("target_id", ""))): raw
            for raw in configured if isinstance(raw, dict)
        }
        existing = set(existing_records)
        candidates: list[LayerPerformanceModifier] = []

        if layer.source_type == "video":
            candidates.extend((
                _modifier(
                    "downbeat opacity", "transport.beat_pulse", "layer.opacity",
                    0.10, "exponential", 8.0, 180.0,
                ),
                _modifier("bass scale", "audio.low", "layer.scale", 0.08),
                _modifier("energy rotation", energy, "layer.rotation", 0.035),
            ))
        elif layer.source_type == "generator" and layer.generator_type:
            settings = normalize_settings(layer.generator_type, layer.generator_settings)
            if kind == "geometry":
                candidates.extend((
                    _modifier(
                        "energy deformation", energy, "generator.animation_amount", 0.10
                    ),
                    _modifier(
                        "cutoff motion", cutoff, "generator.animation_speed", 0.12
                    ),
                    _modifier(
                        "beat rotation", beat, "layer.rotation",
                        0.055, "exponential", 8.0, 220.0,
                    ),
                    _modifier("phrase scale", swell, "layer.scale", 0.035),
                ))
            elif kind == "text":
                candidates.extend((
                    _modifier(
                        "energy typography", energy, "generator.text_animation_amount", 0.24
                    ),
                    _modifier(
                        "cutoff type speed", cutoff, "generator.text_animation_speed", 0.16
                    ),
                    _modifier("phrase type scale", swell, "layer.scale", 0.035),
                    _modifier(
                        "onset tracking", onset, "layer.rotation",
                        0.035, "exponential", 5.0, 240.0,
                    ),
                    _modifier(
                        "phrase reveal density", swell,
                        "generator.text_animation_columns", 0.08,
                    ),
                ))
            elif kind == "waveform":
                candidates.extend((
                    _modifier(
                        "bass scale", "audio.low", "layer.scale",
                        0.18, "exponential", 8.0, 220.0,
                    ),
                    _modifier(
                        "cutoff motion", cutoff, "generator.animation_speed", 0.12
                    ),
                    _modifier(
                        "beat motion", beat, "generator.animation_amount",
                        0.12, "exponential", 5.0, 180.0,
                    ),
                ))
            elif kind == "particles":
                # Particle fields are evaluated directly in the fragment shader;
                # these targets update uniforms and never invalidate a CPU texture.
                candidates.extend((
                    _modifier(
                        "energy particle speed", energy, "generator.particle_speed", 0.24
                    ),
                    _modifier(
                        "onset particle size", onset, "generator.particle_size",
                        0.18, "exponential", 5.0, 160.0,
                    ),
                    _modifier(
                        "beat trails", beat, "generator.particle_trail",
                        0.22, "exponential", 5.0, 200.0,
                    ),
                    _modifier(
                        "phrase spread", swell, "generator.particle_spread", 0.10
                    ),
                ))
            elif kind == "particle_system_2":
                # Fixed-step simulation exposes these as uniforms; automation
                # changes live behaviour without recreating GPU populations.
                candidates.extend((
                    _modifier(
                        "energy emission rate", energy,
                        "generator.particle_emission_rate", 0.12,
                    ),
                    _modifier(
                        "beat emission pulse", beat,
                        "generator.particle_emission_rate",
                        0.18, "exponential", 4.0, 170.0,
                    ),
                    _modifier(
                        "onset particle speed", onset,
                        "generator.particle_speed", 0.10,
                        "exponential", 4.0, 150.0,
                    ),
                    _modifier(
                        "bass force field", "audio.low",
                        "generator.particle_force_strength", 0.12,
                    ),
                    _modifier(
                        "cutoff turbulence", cutoff,
                        "generator.particle_turbulence", 0.14,
                    ),
                    _modifier(
                        "phrase particle trails", swell,
                        "generator.particle_trail", 0.12,
                    ),
                    _modifier(
                        "source reform", energy,
                        "generator.particle_reform_strength", 0.08,
                    ),
                    _modifier(
                        "downbeat particle radius", beat,
                        "generator.particle_system_size",
                        0.08, "exponential", 5.0, 180.0,
                    ),
                    _modifier(
                        "onset force accent", onset,
                        "generator.particle_force_strength",
                        0.08, "exponential", 4.0, 150.0,
                    ),
                ))
            else:
                settings = {}

            macro_generator_targets = {
                "geometry": (
                    ("chaos", "motion amount", "generator.animation_amount", 0.12),
                    ("depth", "motion speed", "generator.animation_speed", 0.10),
                    ("fragment", "fragmented motion", "generator.animation_amount", 0.10),
                ),
                "text": (
                    ("chaos", "glyph motion", "generator.text_animation_amount", 0.18),
                    ("density", "reveal density", "generator.text_animation_columns", 0.12),
                    ("decay", "scroll speed", "generator.text_animation_speed", 0.08),
                    ("pressure", "text distortion", "generator.text_animation_amount", 0.10),
                    ("fragment", "glyph fragmentation", "generator.text_animation_amount", 0.18),
                ),
                "waveform": (
                    ("chaos", "waveform movement", "generator.animation_amount", 0.10),
                    ("depth", "waveform motion speed", "generator.animation_speed", 0.08),
                    ("pressure", "waveform amplitude", "generator.waveform_amplitude", 0.12),
                ),
                "particles": (
                    ("chaos", "particle speed", "generator.particle_speed", 0.14),
                    ("density", "particle density", "generator.density", 0.10),
                    ("depth", "particle trails", "generator.particle_trail", 0.12),
                    ("decay", "particle trail persistence", "generator.particle_trail", 0.18),
                    ("pressure", "particle size", "generator.particle_size", 0.08),
                    ("fragment", "particle spread", "generator.particle_spread", 0.12),
                ),
                "particle_system_2": (
                    ("chaos", "particle speed", "generator.particle_speed", 0.12),
                    ("chaos", "particle turbulence", "generator.particle_turbulence", 0.12),
                    ("density", "continuous emission", "generator.particle_emission_rate", 0.16),
                    ("density", "particle radius", "generator.particle_system_size", 0.10),
                    ("depth", "particle trails", "generator.particle_trail", 0.14),
                    ("depth", "source reformation", "generator.particle_reform_strength", 0.10),
                    ("decay", "particle lifetime", "generator.particle_lifetime", 0.14),
                    ("decay", "particle persistence", "generator.particle_trail", 0.18),
                    ("pressure", "particle force", "generator.particle_force_strength", 0.12),
                    ("pressure", "particle turbulence", "generator.particle_turbulence", 0.10),
                    ("fragment", "particle spread", "generator.particle_spread", 0.14),
                ),
            }
            candidates.extend(
                _performance_macro_modifier(macro_id, name, target, depth)
                for macro_id, name, target, depth in macro_generator_targets.get(
                    str(kind), ()
                )
            )

            available = {
                "generator.animation_speed": "animation_speed",
                "generator.animation_amount": "animation_amount",
                "generator.density": "density",
                "generator.rotation": "rotation",
                "generator.waveform_amplitude": "amplitude",
                "generator.waveform_frequency": "frequency",
                "generator.text_animation_speed": "text_animation_speed",
                "generator.text_animation_amount": "text_animation_amount",
                "generator.text_animation_columns": "text_animation_columns",
                "generator.particle_speed": "speed",
                "generator.particle_size": "size",
                "generator.particle_spread": "spread",
                "generator.particle_trail": "trail",
                "generator.particle_emission_rate": "emission_rate",
                "generator.particle_system_size": "particle_size",
                "generator.particle_lifetime": "lifetime",
                "generator.particle_turbulence": "turbulence",
                "generator.particle_force_strength": "force_strength",
                "generator.particle_reform_strength": "reform_strength",
            }
            candidates = [
                item for item in candidates
                if (
                        item.target_id.startswith("layer.")
                        or available.get(item.target_id) in settings
                )
            ]
        elif layer.source_type == "overlay":
            candidates.extend((
                _modifier("overlay rate", energy, "overlay.playback_speed", 0.18),
                _modifier(
                    "overlay frame pulse", beat, "overlay.frame_hold",
                    0.22, "exponential", 5.0, 180.0,
                ),
            ))

        # Layer FX are GPU-evaluated on every composition type.
        candidates.extend((
            _performance_macro_modifier(
                "chaos", "rotation accent", "layer.rotation", 0.08
            ),
            _performance_macro_modifier(
                "chaos", "chromatic aberration", "layer_fx.chromatic", 0.14
            ),
            _performance_macro_modifier(
                "chaos", "invert accent", "layer_fx.invert", 0.08
            ),
            _performance_macro_modifier(
                "chaos", "scanline intensity", "layer_fx.scanlines", 0.10
            ),
            _performance_macro_modifier(
                "density", "layer scale density", "layer.scale", 0.06
            ),
            _performance_macro_modifier(
                "density", "threshold density", "layer_fx.threshold", 0.06
            ),
            _performance_macro_modifier(
                "depth", "layer scale depth", "layer.scale", 0.12
            ),
            _performance_macro_modifier(
                "depth", "horizontal depth", "layer.position_x", 0.05
            ),
            _performance_macro_modifier(
                "depth", "vertical depth", "layer.position_y", 0.05
            ),
            _performance_macro_modifier(
                "decay", "effect persistence", "layer_fx.mix", 0.10
            ),
            _performance_macro_modifier(
                "pressure", "contrast pressure", "layer_fx.contrast", 0.12
            ),
            _performance_macro_modifier(
                "pressure", "threshold pressure", "layer_fx.threshold", 0.10
            ),
            _performance_macro_modifier(
                "pressure", "brightness pressure", "layer_fx.brightness", 0.06
            ),
            _performance_macro_modifier(
                "fragment", "posterize fragments", "layer_fx.posterize", 0.12
            ),
            _performance_macro_modifier(
                "fragment", "chromatic fragments", "layer_fx.chromatic", 0.10
            ),
            _modifier(
                "high-band chromatic", "audio.high",
                "layer_fx.chromatic", 0.14,
                "exponential", 5.0, 180.0,
            ),
            _modifier(
                "beat scanlines", beat, "layer_fx.scanlines",
                0.12, "exponential", 4.0, 160.0,
            ),
            _modifier(
                "phrase posterize", swell, "layer_fx.posterize", 0.10,
            ),
            _modifier(
                "onset invert accent", onset, "layer_fx.invert",
                0.08, "exponential", 4.0, 160.0,
            ),
            _modifier(
                "energy hue shift", energy, "layer_fx.hue", 0.06,
            ),
            _modifier(
                "energy saturation", energy, "layer_fx.saturation", 0.08,
            ),
            _modifier(
                "phrase monochrome", swell, "layer_fx.monochrome", 0.10,
            ),
            _modifier(
                "onset threshold", onset, "layer_fx.threshold", 0.08,
            ),
            _modifier(
                "bass layer contrast", "audio.low", "layer_fx.contrast", 0.10,
            ),
            _modifier(
                "cutoff brightness", cutoff, "layer_fx.brightness", 0.07,
            ),
            _modifier(
                "energy FX blend", energy, "layer_fx.mix", 0.06,
                polarity="bipolar",
            ),
        ))

        for item in candidates:
            item.normalize()
            key = (item.source_id, item.target_id)
            if key in existing:
                raw_existing = existing_records[key]
                if str(raw_existing.get("name", "")).startswith("AUTO ·"):
                    raw_existing["enabled"] = True
                continue
            configured.append(item.to_dict())
            existing.add(key)
            count += 1
    count += install_default_performance_macro_modifiers(layers)
    return count


def set_default_routing_enabled(
        matrix: ModulationMatrix,
        bank: ModulatorBank,
        layers: list[object],
        enabled: bool,
) -> None:
    """Gate only generated AUTO routes, modulators and layer curves."""
    state = bool(enabled)
    for route in matrix.routes:
        if route.route_id.startswith("auto-performance-"):
            route.enabled = state
    for definition in bank.list_modulators():
        if definition.name.startswith("AUTO ·"):
            definition.enabled = state
    for layer in layers:
        records = getattr(layer, "performance_modifiers", [])
        for record in records:
            if isinstance(record, dict) and str(record.get("name", "")).startswith("AUTO ·"):
                record["enabled"] = state
