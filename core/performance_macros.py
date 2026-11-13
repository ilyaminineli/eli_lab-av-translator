from __future__ import annotations

import math
import re
import time
from dataclasses import asdict, dataclass
from typing import Literal

from core.modulation import SOURCE_RANGES

MacroCurve = Literal["linear", "smoothstep", "exponential"]
PERFORMANCE_MACRO_IDS = (
    "chaos",
    "density",
    "depth",
    "decay",
    "pressure",
    "fragment",
)
_MACRO_ID = re.compile(r"^[a-z][a-z0-9_]{1,31}$")


@dataclass
class PerformanceMacro:
    """One normalized performance control, independent of any specific target."""

    macro_id: str
    name: str
    description: str
    value: float = 0.0
    enabled: bool = True
    input_source: str = ""
    input_min: float = 0.0
    input_max: float = 1.0
    input_curve: MacroCurve = "linear"
    input_invert: bool = False
    attack_ms: float = 35.0
    release_ms: float = 260.0
    keyboard_shortcut: str = ""

    def normalize(self) -> None:
        self.macro_id = str(self.macro_id).strip().lower()
        if not _MACRO_ID.fullmatch(self.macro_id):
            raise ValueError("Performance macro ID must be a short lowercase identifier.")
        self.name = str(self.name).strip()[:32] or self.macro_id.upper()
        self.description = str(self.description).strip()[:160]
        self.value = float(self.value)
        if not math.isfinite(self.value):
            raise ValueError("Performance macro value must be finite.")
        self.value = max(0.0, min(1.0, self.value))
        self.enabled = bool(self.enabled)
        self.input_source = str(self.input_source).strip()[:128]
        if self.input_source:
            is_modulator = (
                self.input_source.startswith("modulator.")
                and bool(self.input_source.removeprefix("modulator.").strip())
            )
            if self.input_source not in SOURCE_RANGES and not is_modulator:
                raise ValueError(f"Unknown performance macro input: {self.input_source}")
        self.input_min = float(self.input_min)
        self.input_max = float(self.input_max)
        if not math.isfinite(self.input_min) or not math.isfinite(self.input_max):
            raise ValueError("Performance macro input range must be finite.")
        self.input_min = max(0.0, min(1.0, self.input_min))
        self.input_max = max(0.0, min(1.0, self.input_max))
        if self.input_max <= self.input_min:
            raise ValueError("Performance macro input maximum must exceed minimum.")
        if self.input_curve not in {"linear", "smoothstep", "exponential"}:
            self.input_curve = "linear"
        self.input_invert = bool(self.input_invert)
        self.attack_ms = max(1.0, min(5000.0, float(self.attack_ms)))
        self.release_ms = max(1.0, min(10000.0, float(self.release_ms)))
        self.keyboard_shortcut = str(self.keyboard_shortcut).strip()[:64]

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> PerformanceMacro:
        allowed = set(cls.__dataclass_fields__)
        item = cls(**{key: value for key, value in values.items() if key in allowed})
        item.normalize()
        return item


def default_performance_macros() -> list[PerformanceMacro]:
    """Create the six built-in macros with safe, neutral values and unique shortcuts."""
    definitions = (
        (
            "chaos", "CHAOS", "Glitch, rotation, displacement and feedback intensity",
            "Ctrl+Alt+1",
        ),
        (
            "density", "DENSITY", "Text, particle and geometric density",
            "Ctrl+Alt+2",
        ),
        (
            "depth", "DEPTH", "Zoom, feedback depth, trails and layer position",
            "Ctrl+Alt+3",
        ),
        (
            "decay", "DECAY", "Feedback persistence, trails and particle lifetime",
            "Ctrl+Alt+4",
        ),
        (
            "pressure", "PRESSURE", "Contrast, threshold and distortion intensity",
            "Ctrl+Alt+5",
        ),
        (
            "fragment", "FRAGMENT", "Pixelation, glyph motion and displacement",
            "Ctrl+Alt+6",
        ),
    )
    return [
        PerformanceMacro(
            macro_id=macro_id,
            name=name,
            description=description,
            value=0.0,
            keyboard_shortcut=shortcut,
        )
        for macro_id, name, description, shortcut in definitions
    ]


@dataclass
class _MacroRuntime:
    current: float | None = None
    last_update: float = 0.0
    manual_until: float = 0.0
    source_missing_since: float | None = None


class PerformanceMacroEngine:
    """Evaluates normalized macro inputs and publishes reusable source values."""

    SOURCE_MISSING_HOLD_SECONDS = 1.5

    def __init__(self) -> None:
        self.macros: dict[str, PerformanceMacro] = {
            item.macro_id: item for item in default_performance_macros()
        }
        self._runtime: dict[str, _MacroRuntime] = {}

    def list_macros(self) -> list[PerformanceMacro]:
        return [self.macros[key] for key in PERFORMANCE_MACRO_IDS if key in self.macros]

    def get(self, macro_id: str) -> PerformanceMacro | None:
        return self.macros.get(str(macro_id))

    def reset(self) -> None:
        self.macros = {
            item.macro_id: item for item in default_performance_macros()
        }
        self._runtime.clear()

    def update_macro(self, macro: PerformanceMacro | dict[str, object]) -> None:
        item = (
            macro if isinstance(macro, PerformanceMacro)
            else PerformanceMacro.from_dict(macro)
        )
        item.normalize()
        if item.macro_id not in self.macros:
            raise KeyError(f"Unknown performance macro: {item.macro_id}")
        if item.keyboard_shortcut:
            duplicate = next(
                (
                    other for other in self.macros.values()
                    if other.macro_id != item.macro_id
                    and other.keyboard_shortcut.casefold() == item.keyboard_shortcut.casefold()
                ),
                None,
            )
            if duplicate is not None:
                raise ValueError(
                    f"Keyboard shortcut is already assigned to {duplicate.name}."
                )
        self.macros[item.macro_id] = item
        self._runtime.pop(item.macro_id, None)

    def set_value(
            self,
            macro_id: str,
            value: float,
            hold_seconds: float = 1.5,
            now: float | None = None,
    ) -> float:
        item = self.macros.get(str(macro_id))
        if item is None:
            raise KeyError(f"Unknown performance macro: {macro_id}")
        result = float(value)
        if not math.isfinite(result):
            raise ValueError("Performance macro value must be finite.")
        result = max(0.0, min(1.0, result))
        stamp = time.monotonic() if now is None else float(now)
        item.value = result
        runtime = self._runtime.setdefault(item.macro_id, _MacroRuntime())
        runtime.current = result
        runtime.last_update = stamp
        runtime.manual_until = stamp + max(0.0, min(3600.0, float(hold_seconds)))
        runtime.source_missing_since = None
        return result

    @staticmethod
    def _curve(value: float, curve: MacroCurve) -> float:
        value = max(0.0, min(1.0, value))
        if curve == "smoothstep":
            return value * value * (3.0 - 2.0 * value)
        if curve == "exponential":
            return value * value
        return value

    def evaluate(
            self,
            sources: dict[str, float],
            now: float | None = None,
    ) -> dict[str, float]:
        stamp = time.monotonic() if now is None else float(now)
        outputs: dict[str, float] = {}
        for item in self.list_macros():
            runtime = self._runtime.setdefault(item.macro_id, _MacroRuntime())
            if not item.enabled:
                target = 0.0
                runtime.manual_until = 0.0
            elif stamp < runtime.manual_until:
                target = item.value
            elif item.input_source:
                raw = sources.get(item.input_source)
                if raw is not None and math.isfinite(float(raw)):
                    target = (
                        float(raw) - item.input_min
                    ) / max(1e-9, item.input_max - item.input_min)
                    target = self._curve(max(0.0, min(1.0, target)), item.input_curve)
                    if item.input_invert:
                        target = 1.0 - target
                    runtime.source_missing_since = None
                else:
                    if runtime.source_missing_since is None:
                        runtime.source_missing_since = stamp
                    if stamp - runtime.source_missing_since <= self.SOURCE_MISSING_HOLD_SECONDS:
                        target = (
                            runtime.current
                            if runtime.current is not None
                            else item.value
                        )
                    else:
                        target = item.value
            else:
                target = item.value
                runtime.source_missing_since = None

            if runtime.current is None:
                current = target
            else:
                tau = item.attack_ms if target > runtime.current else item.release_ms
                dt = max(0.0, stamp - runtime.last_update)
                alpha = 1.0 - math.exp(-dt / max(0.001, tau / 1000.0))
                current = runtime.current + alpha * (target - runtime.current)
            runtime.current = max(0.0, min(1.0, current))
            runtime.last_update = stamp
            outputs[f"performance_macro.{item.macro_id}"] = runtime.current
        return outputs

    def values(self) -> dict[str, float]:
        return {
            item.macro_id: (
                self._runtime[item.macro_id].current
                if item.macro_id in self._runtime
                and self._runtime[item.macro_id].current is not None
                else item.value
            )
            for item in self.list_macros()
        }

    def to_dict(self) -> list[dict[str, object]]:
        return [item.to_dict() for item in self.list_macros()]

    def load_dict(self, values: object) -> None:
        updated: dict[str, PerformanceMacro] = {
            item.macro_id: item for item in default_performance_macros()
        }
        if isinstance(values, list):
            for raw in values:
                if not isinstance(raw, dict):
                    continue
                try:
                    item = PerformanceMacro.from_dict(raw)
                except (TypeError, ValueError, KeyError):
                    continue
                if item.macro_id in updated:
                    updated[item.macro_id] = item
        shortcuts: set[str] = set()
        for item in updated.values():
            shortcut = item.keyboard_shortcut.casefold()
            if shortcut and shortcut in shortcuts:
                item.keyboard_shortcut = ""
            elif shortcut:
                shortcuts.add(shortcut)
        self.macros = updated
        self._runtime.clear()
