from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal
from uuid import uuid4

ModulatorKind = Literal["follower", "envelope", "lfo", "steps", "rhythm"]
ModulatorSync = Literal["transport", "free"]
ModulatorReset = Literal["transport", "bar", "phrase"]
ModulatorWaveform = Literal[
    "sine", "triangle", "saw_up", "saw_down", "square", "pulse", "sample_hold"
]
ModulatorInterpolation = Literal["hold", "linear", "smooth"]
ModulatorDirection = Literal["forward", "reverse", "pingpong", "random"]

TRIGGER_SOURCES: dict[str, str] = {
    "transport.beat_pulse": "Every beat",
    "transport.downbeat_pulse": "Bar downbeat",
    "transport.phrase_pulse": "Phrase start",
    "audio.onset": "Audio onset",
    "audio.peak": "Audio peak",
    "macro.energy": "Sonic Pi energy",
    "macro.cutoff": "Sonic Pi cutoff",
}

FOLLOWER_SOURCES: dict[str, str] = {
    "macro.energy": "Sonic Pi · Energy",
    "macro.cutoff": "Sonic Pi · Cutoff",
    "transport.intensity": "Sonic Pi · Scene intensity",
    "transport.phase": "Transport · Beat phase",
    "transport.bar_phase": "Transport · Bar phase",
    "transport.beat_pulse": "Transport · Beat pulse",
    "transport.downbeat_pulse": "Transport · Downbeat pulse",
    "transport.phrase_pulse": "Transport · Phrase pulse",
    "audio.rms": "Audio · RMS",
    "audio.peak": "Audio · Peak",
    "audio.low": "Audio · Low band",
    "audio.mid": "Audio · Mid band",
    "audio.high": "Audio · High band",
    "audio.onset": "Audio · Onset",
    "audio.beat_confidence": "Audio · Beat confidence",
}

MODULATOR_KINDS = ("follower", "envelope", "lfo", "steps", "rhythm")


def euclidean_pattern(
        pulses: int,
        steps: int,
        rotation: int = 0,
) -> list[float]:
    """Return an evenly distributed binary rhythm rotated across a fixed grid."""
    length = max(1, min(64, int(steps)))
    hits = max(0, min(length, int(pulses)))
    if hits == 0:
        pattern = [0.0] * length
    elif hits == length:
        pattern = [1.0] * length
    else:
        pattern = []
        bucket = 0
        for _step in range(length):
            bucket += hits
            if bucket >= length:
                bucket -= length
                pattern.append(1.0)
            else:
                pattern.append(0.0)
    offset = int(rotation) % length
    if offset:
        pattern = pattern[-offset:] + pattern[:-offset]
    return pattern


@dataclass
class ModulatorDefinition:
    modulator_id: str = field(default_factory=lambda: uuid4().hex[:12])
    name: str = "New Modulator"
    kind: ModulatorKind = "lfo"
    enabled: bool = True
    sync_mode: ModulatorSync = "transport"
    reset_mode: ModulatorReset = "transport"
    rate_beats: float = 4.0
    rate_hz: float = 0.25
    phase: float = 0.0
    waveform: ModulatorWaveform = "sine"
    pulse_width: float = 0.5
    input_source: str = "macro.energy"
    input_min: float = 0.0
    input_max: float = 1.0
    input_invert: bool = False
    input_curve: Literal["linear", "smoothstep", "exponential"] = "linear"
    input_attack_ms: float = 35.0
    input_release_ms: float = 240.0
    trigger_source: str = "transport.beat_pulse"
    trigger_threshold: float = 0.5
    retrigger: Literal["restart", "legato"] = "restart"
    attack: float = 0.03
    decay: float = 0.16
    sustain: float = 0.2
    gate: float = 0.2
    release: float = 0.5
    step_values: list[float] = field(
        default_factory=lambda: [1.0, 0.0, 0.0, 0.0]
    )
    division_beats: float = 0.25
    step_rate_hz: float = 4.0
    interpolation: ModulatorInterpolation = "hold"
    direction: ModulatorDirection = "forward"
    swing: float = 0.5
    seed: int = 211

    def normalize(self) -> None:
        self.modulator_id = str(self.modulator_id).strip()[:40] or uuid4().hex[:12]
        self.name = str(self.name).strip()[:64] or "Modulator"
        if self.kind not in MODULATOR_KINDS:
            self.kind = "lfo"
        if self.sync_mode not in {"transport", "free"}:
            self.sync_mode = "transport"
        if self.reset_mode not in {"transport", "bar", "phrase"}:
            self.reset_mode = "transport"
        self.rate_beats = max(0.0625, min(256.0, float(self.rate_beats)))
        self.rate_hz = max(0.005, min(30.0, float(self.rate_hz)))
        self.phase = float(self.phase) % 1.0
        if self.waveform not in {
            "sine", "triangle", "saw_up", "saw_down", "square", "pulse", "sample_hold"
        }:
            self.waveform = "sine"
        self.pulse_width = max(0.02, min(0.98, float(self.pulse_width)))
        if self.input_source not in FOLLOWER_SOURCES:
            self.input_source = "macro.energy"
        self.input_min = max(0.0, min(1.0, float(self.input_min)))
        self.input_max = max(0.0, min(1.0, float(self.input_max)))
        if self.input_max <= self.input_min:
            self.input_min, self.input_max = 0.0, 1.0
        self.input_invert = bool(self.input_invert)
        if self.input_curve not in {"linear", "smoothstep", "exponential"}:
            self.input_curve = "linear"
        self.input_attack_ms = max(1.0, min(5000.0, float(self.input_attack_ms)))
        self.input_release_ms = max(1.0, min(10000.0, float(self.input_release_ms)))
        if self.trigger_source not in TRIGGER_SOURCES:
            self.trigger_source = "transport.beat_pulse"
        self.trigger_threshold = max(
            0.0, min(1.0, float(self.trigger_threshold))
        )
        if self.retrigger not in {"restart", "legato"}:
            self.retrigger = "restart"
        self.attack = max(0.0, min(64.0, float(self.attack)))
        self.decay = max(0.0, min(64.0, float(self.decay)))
        self.sustain = max(0.0, min(1.0, float(self.sustain)))
        self.gate = max(0.0, min(256.0, float(self.gate)))
        self.release = max(0.0, min(64.0, float(self.release)))
        self.gate = max(self.gate, self.attack + self.decay)
        if not isinstance(self.step_values, list):
            self.step_values = [1.0, 0.0, 0.0, 0.0]
        self.step_values = [
                               max(0.0, min(1.0, float(value)))
                               for value in self.step_values[:64]
                           ] or [0.5]
        self.division_beats = max(1.0 / 96.0, min(64.0, float(self.division_beats)))
        self.step_rate_hz = max(0.01, min(64.0, float(self.step_rate_hz)))
        if self.interpolation not in {"hold", "linear", "smooth"}:
            self.interpolation = "hold"
        if self.direction not in {"forward", "reverse", "pingpong", "random"}:
            self.direction = "forward"
        self.swing = max(0.5, min(0.75, float(self.swing)))
        self.seed = int(self.seed) % 2_147_483_647
        self.enabled = bool(self.enabled)

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> ModulatorDefinition:
        allowed = set(cls.__dataclass_fields__)
        clean = {key: value for key, value in values.items() if key in allowed}
        definition = cls(**clean)
        definition.normalize()
        return definition


@dataclass
class ModulatorPreset:
    preset_id: str
    name: str
    description: str
    definition: dict[str, object]
    builtin: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> ModulatorPreset:
        return cls(
            preset_id=str(values.get("preset_id", uuid4().hex[:12]))[:48],
            name=str(values.get("name", "Preset"))[:64],
            description=str(values.get("description", ""))[:180],
            definition=dict(values.get("definition", {})),
            builtin=False,
        )


def _preset(
        preset_id: str,
        preset_name: str,
        description: str,
        **definition: object,
) -> ModulatorPreset:
    item = ModulatorDefinition(**definition)
    item.normalize()
    payload = item.to_dict()
    payload.pop("modulator_id", None)
    payload.pop("name", None)
    return ModulatorPreset(preset_id, preset_name, description, payload, True)


def builtin_modulator_presets() -> list[ModulatorPreset]:
    return [
        _preset(
            "lfo-sine-swell",
            "Sine · 4-bar swell",
            "A slow, phrase-locked rise and fall.",
            name="Sine swell",
            kind="lfo",
            waveform="sine",
            rate_beats=16.0,
            reset_mode="phrase",
        ),
        _preset(
            "lfo-triangle-quarter",
            "Triangle · quarter cycle",
            "A smooth, even modulation with a musical one-beat period.",
            name="Quarter triangle",
            kind="lfo",
            waveform="triangle",
            rate_beats=1.0,
        ),
        _preset(
            "lfo-dotted-pulse",
            "Pulse · dotted eighth feel",
            "A narrow, syncopated pulse from a transport-synced LFO.",
            name="Dotted pulse",
            kind="lfo",
            waveform="pulse",
            rate_beats=0.75,
            pulse_width=0.32,
        ),
        _preset(
            "follower-sonic-pi-energy",
            "Follower · Sonic Pi energy",
            "Reusable smoothed follower of the SONATA energy macro.",
            name="Sonic Pi energy",
            kind="follower",
            input_source="macro.energy",
            input_attack_ms=80.0,
            input_release_ms=600.0,
        ),
        _preset(
            "follower-sonic-pi-cutoff",
            "Follower · Sonic Pi cutoff",
            "Reusable smoothed follower of the SONATA normalized cutoff macro.",
            name="Sonic Pi cutoff",
            kind="follower",
            input_source="macro.cutoff",
            input_attack_ms=40.0,
            input_release_ms=320.0,
        ),
        _preset(
            "env-beat-pluck",
            "Envelope · beat pluck",
            "Fast attack, short decay and a soft release on every beat.",
            name="Beat pluck",
            kind="envelope",
            trigger_source="transport.beat_pulse",
            attack=0.015,
            decay=0.12,
            sustain=0.08,
            gate=0.15,
            release=0.32,
        ),
        _preset(
            "env-downbeat-swell",
            "Envelope · downbeat swell",
            "A longer envelope triggered at the start of each bar.",
            name="Downbeat swell",
            kind="envelope",
            trigger_source="transport.downbeat_pulse",
            attack=0.18,
            decay=0.3,
            sustain=0.68,
            gate=1.0,
            release=0.75,
        ),
        _preset(
            "env-audio-onset",
            "Envelope · audio onset",
            "A transient follower with a punchy attack and release.",
            name="Audio onset",
            kind="envelope",
            sync_mode="free",
            trigger_source="audio.onset",
            attack=0.01,
            decay=0.1,
            sustain=0.0,
            gate=0.12,
            release=0.28,
        ),
        _preset(
            "seq-four-on-floor",
            "Rhythm · four on the floor",
            "Quarter-note accents over a one-bar 16-step grid.",
            name="Four on the floor",
            kind="rhythm",
            step_values=[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            division_beats=0.25,
            pulse_width=0.42,
            interpolation="hold",
        ),
        _preset(
            "seq-clave-3-2",
            "Rhythm · clave 3:2",
            "A five-accent clave-inspired pattern over two bars.",
            name="Clave 3:2",
            kind="rhythm",
            step_values=[1, 0, 0, 0.8, 0, 0, 1, 0, 0, 0, 0.8, 0, 0, 1, 0, 0],
            division_beats=0.25,
            pulse_width=0.38,
            interpolation="hold",
        ),
        _preset(
            "seq-triplet-shimmer",
            "Rhythm · triplet shimmer",
            "A repeating triplet pattern with alternating accents.",
            name="Triplet shimmer",
            kind="rhythm",
            step_values=[1, 0.35, 0.7, 0.25, 0.85, 0.3],
            division_beats=1.0 / 3.0,
            pulse_width=0.65,
            interpolation="hold",
        ),
        _preset(
            "steps-bipolar-staircase",
            "Steps · bipolar staircase",
            "An eight-step contour suitable for rotation or geometry.",
            name="Bipolar staircase",
            kind="steps",
            step_values=[0.0, 0.14, 0.28, 0.42, 0.58, 0.72, 0.86, 1.0],
            division_beats=0.5,
            interpolation="linear",
            direction="pingpong",
        ),
        _preset(
            "steps-random-drift",
            "Steps · random drift",
            "A seeded random-access stepped contour that repeats deterministically.",
            name="Random drift",
            kind="steps",
            step_values=[0.2, 0.75, 0.42, 0.9, 0.32, 0.62, 0.12, 0.55],
            division_beats=1.0,
            interpolation="hold",
            direction="random",
            seed=211,
        ),
    ]


class ModulatorBank:
    """Project-persisted source bank plus reusable built-in and user presets."""

    VERSION = 1

    def __init__(self) -> None:
        self.modulators: dict[str, ModulatorDefinition] = {}
        self.presets: dict[str, ModulatorPreset] = {
            preset.preset_id: preset for preset in builtin_modulator_presets()
        }

    def list_modulators(self) -> list[ModulatorDefinition]:
        return list(self.modulators.values())

    def list_presets(self) -> list[ModulatorPreset]:
        return list(self.presets.values())

    def get(self, modulator_id: str) -> ModulatorDefinition | None:
        return self.modulators.get(str(modulator_id))

    def add(self, definition: ModulatorDefinition) -> str:
        definition.normalize()
        if definition.modulator_id in self.modulators:
            raise ValueError(f"Modulator already exists: {definition.modulator_id}")
        self.modulators[definition.modulator_id] = definition
        return definition.modulator_id

    def update(self, definition: ModulatorDefinition) -> None:
        definition.normalize()
        if definition.modulator_id not in self.modulators:
            raise KeyError(f"Unknown modulator: {definition.modulator_id}")
        self.modulators[definition.modulator_id] = definition

    def create(self, kind: str = "lfo", name: str | None = None) -> ModulatorDefinition:
        defaults: dict[str, object] = {"kind": kind}
        if kind == "follower":
            defaults.update(
                name=name or "Sonic Pi follower",
                kind="follower",
                input_source="macro.energy",
                input_min=0.0,
                input_max=1.0,
                input_curve="linear",
                input_attack_ms=35.0,
                input_release_ms=240.0,
            )
        elif kind == "envelope":
            defaults.update(
                name=name or "Envelope",
                kind="envelope",
                trigger_source="transport.beat_pulse",
                attack=0.02,
                decay=0.2,
                sustain=0.3,
                gate=0.25,
                release=0.4,
            )
        elif kind == "steps":
            defaults.update(
                name=name or "Step sequence",
                kind="steps",
                step_values=[0.0, 0.33, 0.66, 1.0],
                division_beats=0.5,
                interpolation="hold",
            )
        elif kind == "rhythm":
            defaults.update(
                name=name or "Rhythm pattern",
                kind="rhythm",
                step_values=[1.0, 0.0, 0.0, 0.0],
                division_beats=0.25,
                pulse_width=0.4,
            )
        else:
            defaults.update(name=name or "LFO", kind="lfo")
        item = ModulatorDefinition(**defaults)
        self.add(item)
        return item

    def duplicate(self, modulator_id: str) -> ModulatorDefinition:
        original = self.get(modulator_id)
        if original is None:
            raise KeyError(f"Unknown modulator: {modulator_id}")
        values = original.to_dict()
        values["modulator_id"] = uuid4().hex[:12]
        values["name"] = f"{original.name} copy"
        duplicate = ModulatorDefinition.from_dict(values)
        self.add(duplicate)
        return duplicate

    def remove(self, modulator_id: str) -> bool:
        return self.modulators.pop(str(modulator_id), None) is not None

    def instantiate_preset(self, preset_id: str) -> ModulatorDefinition:
        preset = self.presets.get(str(preset_id))
        if preset is None:
            raise KeyError(f"Unknown modulator preset: {preset_id}")
        values = dict(preset.definition)
        values["modulator_id"] = uuid4().hex[:12]
        values["name"] = preset.name
        definition = ModulatorDefinition.from_dict(values)
        self.add(definition)
        return definition

    def save_preset(
            self,
            modulator_id: str,
            name: str,
            description: str = "",
    ) -> str:
        definition = self.get(modulator_id)
        if definition is None:
            raise KeyError(f"Unknown modulator: {modulator_id}")
        payload = definition.to_dict()
        payload.pop("modulator_id", None)
        payload.pop("name", None)
        preset_id = f"user-{uuid4().hex[:10]}"
        self.presets[preset_id] = ModulatorPreset(
            preset_id,
            str(name).strip()[:64] or definition.name,
            str(description).strip()[:180],
            payload,
            False,
        )
        return preset_id

    def delete_preset(self, preset_id: str) -> bool:
        preset = self.presets.get(str(preset_id))
        if preset is None or preset.builtin:
            return False
        self.presets.pop(str(preset_id), None)
        return True

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.VERSION,
            "modulators": [item.to_dict() for item in self.modulators.values()],
            "presets": [
                item.to_dict() for item in self.presets.values() if not item.builtin
            ],
        }

    def export_presets(self, path: str | Path) -> Path:
        destination = Path(path)
        payload = {
            "format": "eli-lab-modulator-presets",
            "version": self.VERSION,
            "presets": [
                preset.to_dict()
                for preset in self.presets.values()
                if not preset.builtin
            ],
        }
        destination.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return destination

    def import_presets(self, path: str | Path) -> int:
        source = Path(path)
        payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Modulator preset file must contain a JSON object.")
        if payload.get("format") not in {
            None, "eli-lab-modulator-presets"
        }:
            raise ValueError("This file is not an eli_lab modulator preset bank.")
        raw_presets = payload.get("presets")
        if not isinstance(raw_presets, list):
            raise ValueError("Modulator preset file has no preset list.")

        imported = 0
        for raw in raw_presets:
            if not isinstance(raw, dict):
                continue
            preset = ModulatorPreset.from_dict(raw)
            ModulatorDefinition.from_dict(preset.definition)
            if preset.preset_id in self.presets:
                preset.preset_id = f"user-{uuid4().hex[:10]}"
            self.presets[preset.preset_id] = preset
            imported += 1
        return imported

    def load_dict(self, values: object) -> None:
        if not isinstance(values, dict):
            return
        modulators: dict[str, ModulatorDefinition] = {}
        for raw in values.get("modulators", []):
            if not isinstance(raw, dict):
                continue
            try:
                item = ModulatorDefinition.from_dict(raw)
            except (TypeError, ValueError, KeyError):
                continue
            modulators[item.modulator_id] = item
        presets = {
            preset.preset_id: preset for preset in builtin_modulator_presets()
        }
        for raw in values.get("presets", []):
            if not isinstance(raw, dict):
                continue
            try:
                preset = ModulatorPreset.from_dict(raw)
                # Validate the embedded definition before accepting a preset.
                ModulatorDefinition.from_dict(preset.definition)
            except (TypeError, ValueError, KeyError):
                continue
            presets[preset.preset_id] = preset
        self.modulators = modulators
        self.presets = presets


@dataclass
class _ModulatorRuntime:
    started_at: float | None = None
    current: float | None = None
    last_update: float = 0.0
    previous_trigger: bool = False
    trigger_beat: float | None = None
    trigger_time: float | None = None


class ModulatorBankEngine:
    """Deterministic, UI-thread evaluator for reusable envelope/LFO/step sources."""

    def __init__(self) -> None:
        self._runtime: dict[str, _ModulatorRuntime] = {}
        self._live_values: dict[str, float] = {}

    def live_values(self) -> dict[str, float]:
        return dict(self._live_values)

    def reset_modulator(self, modulator_id: str) -> None:
        self._runtime.pop(str(modulator_id), None)
        self._live_values.pop(f"modulator.{modulator_id}", None)

    @staticmethod
    def _stable_random(modulator_id: str, seed: int, index: int) -> float:
        digest = hashlib.blake2b(
            f"{modulator_id}:{seed}:{index}".encode(),
            digest_size=8,
        ).digest()
        return int.from_bytes(digest, "big") / float(2 ** 64 - 1)

    @staticmethod
    def _reset_position(
            definition: ModulatorDefinition,
            sources: dict[str, float],
            beat_position: float,
    ) -> float:
        if definition.reset_mode == "bar":
            return beat_position % max(1.0, float(sources.get("transport.beats_per_bar", 4.0)))
        if definition.reset_mode == "phrase":
            return beat_position % max(1.0, float(sources.get("transport.phrase_beats", 16.0)))
        return beat_position

    @staticmethod
    def _lfo_value(
            definition: ModulatorDefinition,
            phase: float,
            cycle_index: int,
    ) -> float:
        phase %= 1.0
        if definition.waveform == "sine":
            return 0.5 + 0.5 * math.sin(2.0 * math.pi * phase)
        if definition.waveform == "triangle":
            return 1.0 - abs(2.0 * phase - 1.0)
        if definition.waveform == "saw_up":
            return phase
        if definition.waveform == "saw_down":
            return 1.0 - phase
        if definition.waveform == "square":
            return 1.0 if phase < 0.5 else 0.0
        if definition.waveform == "pulse":
            return 1.0 if phase < definition.pulse_width else 0.0
        return ModulatorBankEngine._stable_random(
            definition.modulator_id, definition.seed, cycle_index
        )

    @staticmethod
    def _sequence_index(
            definition: ModulatorDefinition,
            step_index: int,
            sequence_length: int,
            cycle_index: int,
    ) -> int:
        if definition.direction == "reverse":
            return sequence_length - 1 - (step_index % sequence_length)
        if definition.direction == "pingpong" and sequence_length > 1:
            span = sequence_length * 2 - 2
            position = step_index % span
            return position if position < sequence_length else span - position
        if definition.direction == "random":
            return min(
                sequence_length - 1,
                int(
                    ModulatorBankEngine._stable_random(
                        definition.modulator_id,
                        definition.seed,
                        cycle_index * sequence_length + step_index,
                    ) * sequence_length
                ),
            )
        return step_index % sequence_length

    @staticmethod
    def _sequence_value(
            definition: ModulatorDefinition,
            position: float,
            cycle_beats: float,
            cycle_index: int,
    ) -> float:
        values = definition.step_values
        length = len(values)
        if length == 1:
            value = values[0]
            return 0.5 + 0.5 * value if definition.kind == "rhythm" else value

        division = definition.division_beats
        if definition.swing > 0.500001 and length >= 2:
            pair_beats = division * 2.0
            pair_index = int(position // pair_beats)
            local = position - pair_index * pair_beats
            first_length = pair_beats * definition.swing
            if local < first_length:
                logical_index = pair_index * 2
                fraction = local / max(1e-9, first_length)
            else:
                logical_index = pair_index * 2 + 1
                fraction = (local - first_length) / max(1e-9, pair_beats - first_length)
        else:
            step_position = position / division
            logical_index = int(math.floor(step_position))
            fraction = step_position - logical_index

        selected_index = ModulatorBankEngine._sequence_index(
            definition, logical_index, length, cycle_index
        )
        selected = values[selected_index]
        next_index = ModulatorBankEngine._sequence_index(
            definition, logical_index + 1, length, cycle_index
        )
        next_value = values[next_index]

        if definition.kind == "rhythm":
            active = fraction <= definition.pulse_width
            value = selected if active else 0.0
            return 0.5 + 0.5 * value

        if definition.interpolation == "linear":
            value = selected + (next_value - selected) * fraction
        elif definition.interpolation == "smooth":
            eased = fraction * fraction * (3.0 - 2.0 * fraction)
            value = selected + (next_value - selected) * eased
        else:
            value = selected
        return max(0.0, min(1.0, value))

    def _envelope_value(
            self,
            definition: ModulatorDefinition,
            runtime: _ModulatorRuntime,
            sources: dict[str, float],
            now: float,
            transport_running: bool,
            beat_position: float,
    ) -> float:
        attack = definition.attack
        decay = definition.decay
        gate = max(definition.gate, attack + decay)
        release = definition.release

        active = False
        if runtime.trigger_time is not None:
            if (
                    definition.sync_mode == "transport"
                    and transport_running
                    and runtime.trigger_beat is not None
            ):
                previous_age = max(0.0, beat_position - runtime.trigger_beat)
            else:
                previous_age = max(0.0, now - runtime.trigger_time)
            active = previous_age < gate + release

        trigger_high = (
                float(sources.get(definition.trigger_source, 0.0))
                >= definition.trigger_threshold
        )
        if trigger_high and not runtime.previous_trigger:
            if definition.retrigger == "restart" or not active:
                runtime.trigger_time = now
                runtime.trigger_beat = beat_position if transport_running else None
        runtime.previous_trigger = trigger_high
        if runtime.trigger_time is None:
            return 0.0

        if definition.sync_mode == "transport":
            if not transport_running or runtime.trigger_beat is None:
                return 0.0
            age = max(0.0, beat_position - runtime.trigger_beat)
        else:
            age = max(0.0, now - runtime.trigger_time)
        if attack > 0.0 and age < attack:
            return max(0.0, min(1.0, age / attack))
        if decay > 0.0 and age < attack + decay:
            progress = (age - attack) / decay
            return 1.0 + (definition.sustain - 1.0) * progress
        if age < gate:
            return definition.sustain
        if release > 0.0 and age < gate + release:
            progress = (age - gate) / release
            return definition.sustain * (1.0 - progress)
        return 0.0

    def evaluate(
            self,
            bank: ModulatorBank,
            sources: dict[str, float],
            now: float | None = None,
    ) -> dict[str, float]:
        stamp = time.monotonic() if now is None else float(now)
        outputs: dict[str, float] = {}
        transport_running = bool(sources.get("transport.running", 0.0))
        beat_position = float(sources.get("transport.beat_position", 0.0))
        configured: set[str] = set()

        for definition in bank.list_modulators():
            configured.add(definition.modulator_id)
            runtime = self._runtime.setdefault(
                definition.modulator_id, _ModulatorRuntime(started_at=stamp)
            )
            if not definition.enabled:
                continue
            if runtime.started_at is None:
                runtime.started_at = stamp

            if definition.kind == "follower":
                raw_input = sources.get(definition.input_source)
                if raw_input is None or not math.isfinite(float(raw_input)):
                    runtime.current = None
                    runtime.last_update = stamp
                    continue
                normalized = (
                                     float(raw_input) - definition.input_min
                             ) / max(1e-9, definition.input_max - definition.input_min)
                normalized = max(0.0, min(1.0, normalized))
                if definition.input_curve == "smoothstep":
                    normalized = normalized * normalized * (3.0 - 2.0 * normalized)
                elif definition.input_curve == "exponential":
                    normalized *= normalized
                if definition.input_invert:
                    normalized = 1.0 - normalized
                if runtime.current is None:
                    value = normalized
                else:
                    tau = (
                        definition.input_attack_ms
                        if normalized > runtime.current
                        else definition.input_release_ms
                    )
                    dt = max(0.0, stamp - runtime.last_update)
                    alpha = 1.0 - math.exp(
                        -dt / max(0.001, tau / 1000.0)
                    )
                    value = runtime.current + alpha * (normalized - runtime.current)
                runtime.current = value
                runtime.last_update = stamp
                outputs[f"modulator.{definition.modulator_id}"] = max(
                    0.0, min(1.0, float(value))
                )
                continue

            if definition.sync_mode == "transport":
                if not transport_running:
                    outputs[f"modulator.{definition.modulator_id}"] = (
                        0.0 if definition.kind == "envelope" else 0.5
                    )
                    continue
                position = self._reset_position(
                    definition, sources, beat_position
                )
            else:
                position = max(0.0, stamp - runtime.started_at)

            if definition.kind == "envelope":
                value = self._envelope_value(
                    definition,
                    runtime,
                    sources,
                    stamp,
                    transport_running,
                    beat_position,
                )
            elif definition.kind == "lfo":
                if definition.sync_mode == "transport":
                    cycles = position / definition.rate_beats
                else:
                    cycles = position * definition.rate_hz
                phased = cycles + definition.phase
                cycle_index = int(math.floor(phased))
                value = self._lfo_value(
                    definition,
                    phased - cycle_index,
                    cycle_index,
                )
            else:
                sequence_steps = max(1, len(definition.step_values))
                if definition.direction == "pingpong" and sequence_steps > 1:
                    sequence_steps = sequence_steps * 2 - 2
                if definition.sync_mode == "transport":
                    sequence_position = position
                    cycle_beats = definition.division_beats * sequence_steps
                    cycle_index = int(math.floor(sequence_position / max(1e-9, cycle_beats)))
                    local_position = sequence_position % max(1e-9, cycle_beats)
                else:
                    step_position = position * definition.step_rate_hz
                    cycle_index = int(step_position // sequence_steps)
                    local_position = (
                                             step_position % sequence_steps
                                     ) * definition.division_beats
                    cycle_beats = definition.division_beats * sequence_steps
                value = self._sequence_value(
                    definition,
                    local_position,
                    cycle_beats,
                    cycle_index,
                )
            outputs[f"modulator.{definition.modulator_id}"] = max(
                0.0, min(1.0, float(value))
            )

        for modulator_id in tuple(self._runtime):
            if modulator_id not in configured:
                self._runtime.pop(modulator_id, None)
        self._live_values = dict(outputs)
        return outputs

    def reset(self) -> None:
        self._runtime.clear()
        self._live_values.clear()
