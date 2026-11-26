from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

MOTION_GESTURE_SCHEMA_VERSION = 1
VISUAL_PATTERN_SCHEMA_VERSION = 1
VISUAL_PATTERN_STEP_SCHEMA_VERSION = 1
MAX_MOTION_GESTURE_PARAMETERS = 32
MAX_VISUAL_PATTERN_STEPS = 64
MAX_MOTION_GRAMMAR_ENTRIES = 256
MAX_SEED = 18_446_744_073_709_551_615

MOTION_GESTURE_KINDS = frozenset(
    {
        "translate",
        "rotate",
        "scale",
        "opacity",
        "deform",
        "orbit",
        "palette",
        "material",
        "camera",
        "hold",
        "composite",
    }
)

MOTION_EASINGS = frozenset(
    {
        "linear",
        "smoothstep",
        "ease_in",
        "ease_out",
        "ease_in_out",
        "step",
        "sine",
    }
)

VISUAL_PATTERN_FAMILIES = frozenset(
    {
        "pulse_field",
        "displaced_accent",
        "rotating_cycle",
        "unequal_cycle_interlock",
        "phase_drift",
        "omission",
        "burst",
        "sparse_punctuation",
        "density_cloud",
        "call_and_response",
        "unison_fusion",
        "counter_motion",
        "hierarchical_motion",
        "accumulation",
        "erosion",
        "fracture_repair",
        "scan_traverse",
        "memory_echo",
        "stutter_hold",
        "morphing_cycle",
    }
)

VISUAL_CYCLE_UNITS = frozenset({"seconds", "beats", "bars"})
VISUAL_TIMING_BASES = frozenset({"visual_clock", "authored_music"})


def _identifier(value: object, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{label} cannot be empty.")
    if len(result) > 128:
        raise ValueError(f"{label} must be at most 128 characters.")
    return result


def _bounded_scalar(value: object, label: str) -> str | int | float | bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value < -1_000_000_000 or value > 1_000_000_000:
            raise ValueError(f"{label} must be within ±1,000,000,000.")
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or value < -1_000_000_000 or value > 1_000_000_000:
            raise ValueError(f"{label} must be finite and within ±1,000,000,000.")
        return value
    if isinstance(value, str) and len(value) <= 128:
        return value
    raise ValueError(
        f"{label} must be a finite bounded number, boolean or string "
        "of at most 128 characters."
    )


def _normalize_seed(seed: object, label: str) -> int | None:
    if seed is None:
        return None
    if (
        isinstance(seed, bool)
        or not isinstance(seed, int)
        or seed < 0
        or seed > MAX_SEED
    ):
        raise ValueError(f"{label} must be an unsigned 64-bit integer.")
    return seed


def _normalize_revision(revision: object, label: str) -> int:
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return revision


def _unit_interval(value: object, label: str, *, include_one: bool) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number in [0, 1].")
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f"{label} must be a finite number in [0, 1].") from None
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite number in [0, 1].")
    if result < 0.0 or result > 1.0 or (not include_one and result == 1.0):
        boundary = "[0, 1]" if include_one else "[0, 1)"
        raise ValueError(f"{label} must be in {boundary}.")
    return result


@dataclass
class MotionGesture:
    """A renderer-independent, reusable visual transformation description."""

    gesture_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "Untitled Gesture"
    kind: str = "translate"
    parameters: dict[str, str | int | float | bool] = field(default_factory=dict)
    easing: str = "linear"
    reversible: bool = True
    revision: int = 0

    def normalize(self) -> None:
        self.gesture_id = _identifier(self.gesture_id, "Motion gesture ID")
        self.name = str(self.name).strip()
        if not self.name or len(self.name) > 128:
            raise ValueError("Motion gesture name must contain 1–128 characters.")
        self.kind = str(self.kind).strip()
        if self.kind not in MOTION_GESTURE_KINDS:
            raise ValueError(f"Unsupported motion gesture kind: {self.kind!r}.")
        self.easing = str(self.easing).strip()
        if self.easing not in MOTION_EASINGS:
            raise ValueError(f"Unsupported motion easing: {self.easing!r}.")
        if not isinstance(self.reversible, bool):
            raise ValueError("Motion gesture reversible must be a boolean.")
        if not isinstance(self.parameters, dict):
            raise ValueError("Motion gesture parameters must be an object.")
        if len(self.parameters) > MAX_MOTION_GESTURE_PARAMETERS:
            raise ValueError(
                f"Motion gesture cannot contain more than "
                f"{MAX_MOTION_GESTURE_PARAMETERS} parameters."
            )
        normalized: dict[str, str | int | float | bool] = {}
        for raw_key, raw_value in self.parameters.items():
            key = str(raw_key).strip()
            if not key or len(key) > 64:
                raise ValueError("Motion gesture parameter names must contain 1–64 characters.")
            if key in normalized:
                raise ValueError(f"Duplicate motion gesture parameter: {key}")
            normalized[key] = _bounded_scalar(
                raw_value,
                f"Motion gesture parameter {key!r}",
            )
        self.parameters = normalized
        self.revision = _normalize_revision(self.revision, "Motion gesture revision")

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {
            "schema_version": MOTION_GESTURE_SCHEMA_VERSION,
            **asdict(self),
        }

    @classmethod
    def from_dict(cls, data: object) -> MotionGesture:
        if not isinstance(data, dict):
            raise ValueError("Motion gesture must be an object.")
        version = int(data.get("schema_version", MOTION_GESTURE_SCHEMA_VERSION))
        if version > MOTION_GESTURE_SCHEMA_VERSION:
            raise ValueError(
                f"Motion gesture schema {version} is newer than supported schema "
                f"{MOTION_GESTURE_SCHEMA_VERSION}."
            )
        values = {
            key: value
            for key, value in data.items()
            if key in cls.__dataclass_fields__
        }
        result = cls(**values)
        result.normalize()
        return result


@dataclass
class VisualPatternStep:
    """One gesture scheduled at a normalized position in a visual cycle."""

    step_id: str = field(default_factory=lambda: uuid4().hex)
    gesture_id: str = ""
    start_fraction: float = 0.0
    duration_fraction: float = 1.0
    intensity: float = 1.0
    group: str = ""

    def normalize(self) -> None:
        self.step_id = _identifier(self.step_id, "Visual pattern step ID")
        self.gesture_id = _identifier(self.gesture_id, "Visual pattern gesture ID")
        self.start_fraction = _unit_interval(
            self.start_fraction,
            "Visual pattern step start fraction",
            include_one=False,
        )
        self.duration_fraction = _unit_interval(
            self.duration_fraction,
            "Visual pattern step duration fraction",
            include_one=True,
        )
        if self.duration_fraction <= 0.0:
            raise ValueError("Visual pattern step duration must be greater than zero.")
        self.intensity = _unit_interval(
            self.intensity,
            "Visual pattern step intensity",
            include_one=True,
        )
        self.group = str(self.group).strip()
        if len(self.group) > 64:
            raise ValueError("Visual pattern step group must be at most 64 characters.")

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {
            "schema_version": VISUAL_PATTERN_STEP_SCHEMA_VERSION,
            **asdict(self),
        }

    @classmethod
    def from_dict(cls, data: object) -> VisualPatternStep:
        if not isinstance(data, dict):
            raise ValueError("Visual pattern step must be an object.")
        version = int(data.get("schema_version", VISUAL_PATTERN_STEP_SCHEMA_VERSION))
        if version > VISUAL_PATTERN_STEP_SCHEMA_VERSION:
            raise ValueError(
                f"Visual pattern step schema {version} is newer than supported schema "
                f"{VISUAL_PATTERN_STEP_SCHEMA_VERSION}."
            )
        values = {
            key: value
            for key, value in data.items()
            if key in cls.__dataclass_fields__
        }
        result = cls(**values)
        result.normalize()
        return result


@dataclass
class VisualPattern:
    """A reusable cycle/sequence composed from references to MotionGestures."""

    pattern_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "Untitled Pattern"
    family: str = "rotating_cycle"
    cycle_length: float = 1.0
    cycle_unit: str = "seconds"
    timing_basis: str = "visual_clock"
    phase: float = 0.0
    steps: list[VisualPatternStep] = field(default_factory=list)
    seed: int | None = None
    revision: int = 0

    def normalize(self) -> None:
        self.pattern_id = _identifier(self.pattern_id, "Visual pattern ID")
        self.name = str(self.name).strip()
        if not self.name or len(self.name) > 128:
            raise ValueError("Visual pattern name must contain 1–128 characters.")
        self.family = str(self.family).strip()
        if self.family not in VISUAL_PATTERN_FAMILIES:
            raise ValueError(f"Unsupported visual pattern family: {self.family!r}.")
        if isinstance(self.cycle_length, bool) or not isinstance(
            self.cycle_length, (int, float)
        ):
            raise ValueError("Visual pattern cycle length must be finite and positive.")
        try:
            cycle_length = float(self.cycle_length)
        except (OverflowError, ValueError):
            raise ValueError(
                "Visual pattern cycle length must be finite and positive."
            ) from None
        if not math.isfinite(cycle_length) or cycle_length <= 0.0:
            raise ValueError("Visual pattern cycle length must be finite and positive.")
        self.cycle_length = cycle_length
        self.cycle_unit = str(self.cycle_unit).strip()
        if self.cycle_unit not in VISUAL_CYCLE_UNITS:
            raise ValueError(f"Unsupported visual cycle unit: {self.cycle_unit!r}.")
        cycle_limit = 86_400.0 if self.cycle_unit == "seconds" else 4_096.0
        if self.cycle_length > cycle_limit:
            raise ValueError(
                f"Visual pattern cycle length exceeds the {self.cycle_unit} limit."
            )
        self.timing_basis = str(self.timing_basis).strip()
        if self.timing_basis not in VISUAL_TIMING_BASES:
            raise ValueError(f"Unsupported visual timing basis: {self.timing_basis!r}.")
        expected_basis = (
            "visual_clock" if self.cycle_unit == "seconds" else "authored_music"
        )
        if self.timing_basis != expected_basis:
            raise ValueError(
                f"Visual pattern unit {self.cycle_unit!r} requires timing basis "
                f"{expected_basis!r}; audio observations are not authored musical time."
            )
        self.phase = _unit_interval(
            self.phase,
            "Visual pattern phase",
            include_one=False,
        )
        if not isinstance(self.steps, list):
            raise ValueError("Visual pattern steps must be a list.")
        if len(self.steps) > MAX_VISUAL_PATTERN_STEPS:
            raise ValueError(
                f"Visual pattern cannot contain more than {MAX_VISUAL_PATTERN_STEPS} steps."
            )
        normalized_steps: list[VisualPatternStep] = []
        seen_step_ids: set[str] = set()
        for raw_step in self.steps:
            step = (
                raw_step
                if isinstance(raw_step, VisualPatternStep)
                else VisualPatternStep.from_dict(raw_step)
            )
            step.normalize()
            if step.step_id in seen_step_ids:
                raise ValueError(f"Duplicate visual pattern step ID: {step.step_id}")
            seen_step_ids.add(step.step_id)
            normalized_steps.append(step)
        self.steps = normalized_steps
        self.seed = _normalize_seed(self.seed, "Visual pattern seed")
        self.revision = _normalize_revision(self.revision, "Visual pattern revision")

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {
            "schema_version": VISUAL_PATTERN_SCHEMA_VERSION,
            "pattern_id": self.pattern_id,
            "name": self.name,
            "family": self.family,
            "cycle_length": self.cycle_length,
            "cycle_unit": self.cycle_unit,
            "timing_basis": self.timing_basis,
            "phase": self.phase,
            "steps": [step.to_dict() for step in self.steps],
            "seed": self.seed,
            "revision": self.revision,
        }

    @classmethod
    def from_dict(cls, data: object) -> VisualPattern:
        if not isinstance(data, dict):
            raise ValueError("Visual pattern must be an object.")
        version = int(data.get("schema_version", VISUAL_PATTERN_SCHEMA_VERSION))
        if version > VISUAL_PATTERN_SCHEMA_VERSION:
            raise ValueError(
                f"Visual pattern schema {version} is newer than supported schema "
                f"{VISUAL_PATTERN_SCHEMA_VERSION}."
            )
        values = {
            key: value
            for key, value in data.items()
            if key in cls.__dataclass_fields__
        }
        raw_steps = values.get("steps", [])
        if not isinstance(raw_steps, list):
            raise ValueError("Visual pattern steps must be a list.")
        values["steps"] = [
            item
            if isinstance(item, VisualPatternStep)
            else VisualPatternStep.from_dict(item)
            for item in raw_steps
        ]
        result = cls(**values)
        result.normalize()
        return result
