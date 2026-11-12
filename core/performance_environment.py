from __future__ import annotations

import json
import math
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

PERFORMANCE_SET_FORMAT = "eli_lab_performance_set"
PERFORMANCE_SET_VERSION = 1


@dataclass
class MIDIMapping:
    """Stable MIDI-to-performance binding with scaling and pickup semantics."""
    mapping_id: str = field(default_factory=lambda: uuid4().hex[:12])
    device_id: str = "*"
    channel: int = 0
    message: str = "cc"
    number: int = 1
    target: str = "macro.energy"
    minimum: float = 0.0
    maximum: float = 1.0
    curve: str = "linear"
    pickup: bool = True
    enabled: bool = True
    last_physical: float | None = None

    def normalize(self) -> None:
        self.mapping_id = str(self.mapping_id).strip()[:40] or uuid4().hex[:12]
        self.device_id = str(self.device_id).strip()[:128] or "*"
        self.channel = max(0, min(15, int(self.channel)))
        if self.message not in {"cc", "note", "pitch"}:
            raise ValueError("MIDI message must be cc, note or pitch.")
        self.number = max(0, min(127, int(self.number)))
        self.target = str(self.target).strip()[:128]
        if not self.target:
            raise ValueError("MIDI mapping target cannot be empty.")
        self.minimum = float(self.minimum)
        self.maximum = float(self.maximum)
        if not math.isfinite(self.minimum) or not math.isfinite(self.maximum):
            raise ValueError("MIDI mapping range must be finite.")
        if self.maximum <= self.minimum:
            raise ValueError("MIDI mapping maximum must exceed minimum.")
        if self.curve not in {"linear", "smoothstep", "exponential"}:
            self.curve = "linear"
        self.enabled = bool(self.enabled)
        self.pickup = bool(self.pickup)
        if self.last_physical is not None:
            physical = float(self.last_physical)
            self.last_physical = max(0.0, min(1.0, physical)) if math.isfinite(physical) else None

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        data = asdict(self)
        data.pop("last_physical", None)  # transient hardware position is not a saved setting
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MIDIMapping:
        allowed = set(cls.__dataclass_fields__)
        item = cls(**{key: value for key, value in data.items() if key in allowed})
        item.normalize()
        return item


class MIDIMappingEngine:
    """Applies learned mappings without owning devices or touching the renderer."""

    def __init__(self) -> None:
        self.mappings: list[MIDIMapping] = []
        self._pickup_armed: dict[str, bool] = {}
        self._previous: dict[str, float] = {}

    def replace_mappings(self, values: list[MIDIMapping | dict[str, Any]]) -> None:
        result: list[MIDIMapping] = []
        ids: set[str] = set()
        for raw in values:
            item = raw if isinstance(raw, MIDIMapping) else MIDIMapping.from_dict(raw)
            item.normalize()
            if item.mapping_id in ids:
                raise ValueError(f"Duplicate MIDI mapping ID: {item.mapping_id}")
            ids.add(item.mapping_id)
            result.append(item)
        self.mappings = result
        self._pickup_armed.clear()
        self._previous.clear()

    @staticmethod
    def _curve(value: float, curve: str) -> float:
        value = max(0.0, min(1.0, value))
        if curve == "smoothstep":
            return value * value * (3.0 - 2.0 * value)
        if curve == "exponential":
            return value * value
        return value

    def process(self, device_id: str, message: str, channel: int, number: int,
                value: float, current_targets: dict[str, float] | None = None
                ) -> list[tuple[str, float]]:
        physical = float(value)
        if not math.isfinite(physical):
            return []
        physical = max(0.0, min(1.0, physical))
        current_targets = current_targets or {}
        results: list[tuple[str, float]] = []
        for item in self.mappings:
            if not item.enabled or item.device_id not in {'*', str(device_id)}:
                continue
            if (item.message, item.channel, item.number) != (message, channel, number):
                continue
            previous = self._previous.get(item.mapping_id)
            self._previous[item.mapping_id] = physical
            if item.pickup and item.target in current_targets:
                target_norm = (float(current_targets[item.target]) - item.minimum) / (
                        item.maximum - item.minimum
                )
                crossed = previous is not None and (previous - target_norm) * (
                        physical - target_norm
                ) <= 0
                close = abs(physical - target_norm) <= 0.015
                if not (self._pickup_armed.get(item.mapping_id, False) or crossed or close):
                    continue
                self._pickup_armed[item.mapping_id] = True
            shaped = self._curve(physical, item.curve)
            item.last_physical = physical
            results.append((item.target, item.minimum + shaped * (item.maximum - item.minimum)))
        return results

    def to_dict(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.mappings]

    def load_dict(self, values: object) -> None:
        mappings = [v for v in values if isinstance(v, dict)] if isinstance(values, list) else []
        self.replace_mappings(mappings)


@dataclass
class PerformanceScene:
    """First-class VJ scene: a versioned, recallable audiovisual composition snapshot."""

    scene_id: str
    label: str
    snapshot: dict[str, Any]
    quantization: str = "bar"
    cue: str = ""
    tags: list[str] = field(default_factory=list)
    transition: dict[str, Any] = field(default_factory=lambda: {
        "duration": 0.0,
        "curve": "smoothstep",
        "discrete": "switch_midpoint",
    })

    def normalize(self) -> None:
        self.scene_id = str(self.scene_id).strip()[:64]
        self.label = str(self.label).strip()[:80] or self.scene_id
        if self.quantization not in {"immediate", "beat", "bar", "phrase"}:
            self.quantization = "bar"
        self.cue = str(self.cue).strip()[:128]
        if not self.scene_id or not isinstance(self.snapshot, dict):
            raise ValueError("Performance scene requires an ID and snapshot object.")

        clean_tags = []
        seen_tags = set()
        for raw in self.tags if isinstance(self.tags, list) else []:
            tag = str(raw).strip()[:32]
            key = tag.casefold()
            if tag and key not in seen_tags:
                clean_tags.append(tag)
                seen_tags.add(key)
            if len(clean_tags) >= 16:
                break
        self.tags = clean_tags

        raw_transition = self.transition if isinstance(self.transition, dict) else {}
        try:
            duration = float(raw_transition.get("duration", 0.0))
        except (TypeError, ValueError):
            duration = 0.0
        import math
        if not math.isfinite(duration):
            duration = 0.0
        curve = str(raw_transition.get("curve", "smoothstep"))
        if curve not in {"linear", "smoothstep", "ease_in", "ease_out"}:
            curve = "smoothstep"
        discrete = str(raw_transition.get("discrete", "switch_midpoint"))
        if discrete not in {"cut", "switch_midpoint", "fade_through_black"}:
            discrete = "switch_midpoint"
        self.transition = {
            "duration": max(0.0, min(60.0, duration)),
            "curve": curve,
            "discrete": discrete,
        }

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return asdict(self)


class PerformanceSetStore:
    """Versioned, atomic set persistence. Validation occurs before application mutation."""

    @staticmethod
    def build_payload(composition: dict[str, Any], decks: list[dict[str, Any]],
                      effects: dict[str, Any], automation_settings: dict[str, Any],
                      performance_settings: dict[str, Any],
                      scenes: list[PerformanceScene] | None = None,
                      midi_mappings: list[MIDIMapping] | None = None) -> dict[str, Any]:
        return {
            "format": PERFORMANCE_SET_FORMAT, "version": PERFORMANCE_SET_VERSION,
            "created_at": time.time(), "composition": composition, "decks": decks,
            "effects": effects, "automation_settings": automation_settings,
            "performance_settings": performance_settings,
            "scenes": [item.to_dict() for item in (scenes or [])],
            "midi_mappings": [item.to_dict() for item in (midi_mappings or [])],
        }

    @staticmethod
    def save(path: str | Path, payload: dict[str, Any]) -> Path:
        destination = Path(path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = dict(payload)
        data["format"] = PERFORMANCE_SET_FORMAT
        data["version"] = PERFORMANCE_SET_VERSION
        temporary = destination.with_name(destination.name + ".tmp")
        try:
            temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            temporary.replace(destination)
        finally:
            if temporary.exists():
                temporary.unlink()
        return destination

    @staticmethod
    def load(path: str | Path) -> dict[str, Any]:
        data = json.loads(Path(path).expanduser().resolve().read_text(encoding='utf-8'))
        if not isinstance(data, dict) or data.get("format") != PERFORMANCE_SET_FORMAT:
            raise ValueError("This file is not an eli_lab performance set.")
        version = int(data.get('version', 0))
        if version > PERFORMANCE_SET_VERSION:
            raise ValueError(f"Performance set version {version} is newer than supported.")
        for key, expected in (('composition', dict), ('decks', list), ('effects', dict),
                              ('automation_settings', dict), ('performance_settings', dict),
                              ('scenes', list), ('midi_mappings', list)):
            if key in data and not isinstance(data[key], expected):
                raise ValueError(f"Invalid performance set field: {key}")
        # Validate every persisted control definition before returning the payload.
        data['midi_mappings'] = [
            MIDIMapping.from_dict(item).to_dict()
            for item in data.get('midi_mappings', [])
        ]
        scenes = []
        for raw in data.get('scenes', []):
            item = PerformanceScene(**raw)
            item.normalize()
            scenes.append(item.to_dict())
        data['scenes'] = scenes
        return data


@dataclass
class SceneMorph:
    start: dict[str, float]
    end: dict[str, float]
    started_at: float
    duration: float
    curve: str = "smoothstep"

    def value(self, now: float | None = None) -> tuple[float, dict[str, float]]:
        stamp = time.monotonic() if now is None else float(now)
        fraction = (
            1.0
            if self.duration <= 0
            else max(
                0.0,
                min(1.0, (stamp - self.started_at) / self.duration),
            )
        )
        if self.curve == "linear":
            eased = fraction
        elif self.curve == "ease_in":
            eased = fraction * fraction
        elif self.curve == "ease_out":
            eased = 1.0 - (1.0 - fraction) * (1.0 - fraction)
        else:
            eased = fraction * fraction * (3.0 - 2.0 * fraction)
        return fraction, {
            key: self.start[key] + (self.end[key] - self.start[key]) * eased
            for key in self.start.keys() & self.end.keys()
        }


class MIDIInputService:
    """Optional mido input with bounded callback-to-UI event delivery."""

    def __init__(self, callback, queue_capacity: int = 256) -> None:
        self.callback = callback
        self.queue_capacity = max(1, int(queue_capacity))
        from collections import deque
        self._events: deque[tuple[str, str, int, int, float]] = deque()
        self._lock = threading.Lock()
        self._port = None
        self.state = "stopped"
        self.error = ""
        self.device_id = ""
        self.dropped_events = 0

    @staticmethod
    def discover() -> list[str]:
        try:
            import mido
            return list(mido.get_input_names())
        except ImportError:
            return []
        except Exception:
            return []

    def start(self, device_name: str) -> bool:
        self.stop()
        try:
            import mido
            self._port = mido.open_input(
                device_name,
                callback=lambda message: self._receive(device_name, message),
            )
            self.device_id = str(device_name)
            self.state, self.error = "running", ""
            return True
        except Exception as exc:
            self.state, self.error = "error", str(exc)
            self._port = None
            return False

    def _receive(self, device_name: str, message) -> None:
        kind = getattr(message, "type", "")
        channel = int(getattr(message, "channel", 0))
        if kind == "control_change":
            event = (device_name, "cc", channel, int(message.control), float(message.value) / 127)
        elif kind in {"note_on", "note_off"}:
            velocity = float(message.velocity) / 127 if kind == "note_on" else 0.0
            event = (device_name, "note", channel, int(message.note), velocity)
        elif kind == "pitchwheel":
            event = (device_name, "pitch", channel, 0, (float(message.pitch) + 8192) / 16383)
        else:
            return
        with self._lock:
            if len(self._events) >= self.queue_capacity:
                self.dropped_events += 1
                return
            self._events.append(event)

    def drain(self, limit: int = 64) -> int:
        with self._lock:
            count = min(max(0, int(limit)), len(self._events))
            batch = [self._events.popleft() for _ in range(count)]
        for item in batch:
            self.callback(*item)
        return len(batch)

    def stop(self) -> None:
        port, self._port = self._port, None
        if port is not None:
            try:
                port.close()
            except Exception:
                pass
        with self._lock:
            self._events.clear()
        if self.state != 'error':
            self.state = "stopped"
