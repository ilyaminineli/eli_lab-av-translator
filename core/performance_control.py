from __future__ import annotations

import math
import re
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

CTRL_EVT_KINDS = frozenset({
    "transport.start",
    "transport.stop",
    "transport.pause",
    "transport.tempo",
    "transport.meter",
    "clock.beat",
    "clock.bar",
    "scene.select",
    "scene.intensity",
    "macro.set",
    "cue.trigger",
    "source.heartbeat",
})
_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_DEFAULT_QUEUE_CAPACITY = 512


@dataclass(frozen=True)
class ControlEvent:
    """Validated, renderer-independent performance-control message.

    Adapters (audio, OSC, MIDI or internal test sources) translate their native
    messages into this small event contract before they reach application state.
    """

    kind: str
    source: str
    payload: dict[str, str | int | float | bool] = field(default_factory=dict)
    sequence: int | None = None
    session_id: str = ""
    received_at: float = field(default_factory=time.monotonic)

    def __post_init__(self) -> None:
        if self.kind not in CTRL_EVT_KINDS:
            raise ValueError(f"Unsupported control event kind: {self.kind!r}")
        source = str(self.source).strip()
        if not _NAME_PATTERN.fullmatch(source):
            raise ValueError("Control event source must be a short identifier.")
        if self.sequence is not None:
            if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
                raise ValueError("Control event sequence must be an integer.")
            if self.sequence < 0:
                raise ValueError("Control event sequence must be non-negative.")
        if not math.isfinite(float(self.received_at)):
            raise ValueError("Control event timestamp must be finite.")
        session_id = str(self.session_id).strip()
        if session_id and not _NAME_PATTERN.fullmatch(session_id):
            raise ValueError("Control event session ID must be a short identifier.")

        clean_payload: dict[str, str | int | float | bool] = {}
        for key, value in dict(self.payload).items():
            name = str(key).strip()
            if not _NAME_PATTERN.fullmatch(name):
                raise ValueError(f"Invalid control payload key: {key!r}")
            if isinstance(value, bool):
                clean_payload[name] = value
            elif isinstance(value, (int, str)):
                clean_payload[name] = value
            elif isinstance(value, float) and math.isfinite(value):
                clean_payload[name] = value
            else:
                raise ValueError(f"Unsupported control payload value for {name!r}.")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "payload", clean_payload)
        object.__setattr__(self, "received_at", float(self.received_at))


class ControlEventQueue:
    """Small bounded ingress queue shared by future control-source adapters."""

    def __init__(self, capacity: int = _DEFAULT_QUEUE_CAPACITY) -> None:
        self.capacity = max(1, int(capacity))
        self._events: deque[ControlEvent] = deque()
        self._lock = threading.Lock()
        self.dropped_events = 0

    def submit(self, event: ControlEvent) -> bool:
        if not isinstance(event, ControlEvent):
            raise TypeError("Only validated ControlEvent instances can be submitted.")
        with self._lock:
            if len(self._events) >= self.capacity:
                self.dropped_events += 1
                return False
            self._events.append(event)
            return True

    def drain(self, limit: int = 128) -> list[ControlEvent]:
        count = max(0, int(limit))
        with self._lock:
            drained = [self._events.popleft() for _ in range(min(count, len(self._events)))]
        return drained

    def clear(self) -> None:
        with self._lock:
            self._events.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._events)


@dataclass
class PerformanceControlState:
    """Current normalized transport, scene and macro state for the visual instrument."""

    bpm: float = 120.0
    beats_per_bar: int = 4
    beat_index: int = 0
    bar_index: int = 0
    transport_running: bool = False
    transport_paused: bool = False
    source_id: str = "internal"
    scene_id: str = "idle"
    intensity: float = 0.0
    macros: dict[str, float] = field(default_factory=dict)
    macro_updated_at: dict[str, float] = field(default_factory=dict, repr=False)
    last_cue: str = ""
    last_event_at: float = 0.0
    last_event_kind: str = ""
    revision: int = 0
    _last_sequences: dict[tuple[str, str], int] = field(
        default_factory=dict,
        repr=False,
    )

    @staticmethod
    def _number(
            payload: dict[str, Any],
            key: str,
            default: float | None = None,
            minimum: float | None = None,
            maximum: float | None = None,
    ) -> float:
        raw = payload.get(key, default)
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise ValueError(f"Control field {key!r} must be numeric.")
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError(f"Control field {key!r} must be finite.")
        if minimum is not None and value < minimum:
            raise ValueError(f"Control field {key!r} is below its safe range.")
        if maximum is not None and value > maximum:
            raise ValueError(f"Control field {key!r} is above its safe range.")
        return value

    @staticmethod
    def _integer(
            payload: dict[str, Any],
            key: str,
            default: int | None = None,
            minimum: int | None = None,
            maximum: int | None = None,
    ) -> int:
        raw = payload.get(key, default)
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise ValueError(f"Control field {key!r} must be an integer.")
        if minimum is not None and raw < minimum:
            raise ValueError(f"Control field {key!r} is below its safe range.")
        if maximum is not None and raw > maximum:
            raise ValueError(f"Control field {key!r} is above its safe range.")
        return raw

    @staticmethod
    def _identifier(payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not _NAME_PATTERN.fullmatch(value):
            raise ValueError(f"Control field {key!r} must be a short identifier.")
        return value

    def _sequence_is_fresh(self, event: ControlEvent) -> bool:
        if event.sequence is None:
            return True
        key = (event.source, event.session_id)
        previous = self._last_sequences.get(key, -1)
        return event.sequence > previous

    def _record_sequence(self, event: ControlEvent) -> None:
        if event.sequence is not None:
            self._last_sequences[(event.source, event.session_id)] = event.sequence

    def apply(self, event: ControlEvent) -> bool:
        """Apply one event atomically; return False for stale duplicate sequences."""
        if not self._sequence_is_fresh(event):
            return False

        payload = event.payload
        updates: dict[str, Any] = {}
        if event.kind == "transport.start":
            updates["bpm"] = self._number(payload, "bpm", self.bpm, 20.0, 300.0)
            updates["beats_per_bar"] = self._integer(
                payload, "beats_per_bar", self.beats_per_bar, 1, 16
            )
            updates["transport_running"] = True
            updates["transport_paused"] = False
        elif event.kind == "transport.pause":
            updates["transport_running"] = False
            updates["transport_paused"] = True
        elif event.kind == "transport.stop":
            updates["transport_running"] = False
            updates["transport_paused"] = False
        elif event.kind == "transport.tempo":
            updates["bpm"] = self._number(payload, "bpm", minimum=20.0, maximum=300.0)
        elif event.kind == "transport.meter":
            updates["beats_per_bar"] = self._integer(
                payload, "beats_per_bar", minimum=1, maximum=16
            )
            if self.beat_index >= updates["beats_per_bar"]:
                updates["beat_index"] = 0
        elif event.kind == "clock.beat":
            beat = self._integer(payload, "beat_index", minimum=0, maximum=15)
            if beat >= self.beats_per_bar:
                raise ValueError("Beat index must be inside the current bar.")
            updates["beat_index"] = beat
            if "bar_index" in payload:
                updates["bar_index"] = self._integer(
                    payload, "bar_index", minimum=0, maximum=10_000_000
                )
        elif event.kind == "clock.bar":
            updates["bar_index"] = self._integer(
                payload, "bar_index", minimum=0, maximum=10_000_000
            )
            updates["beat_index"] = 0
            if "bpm" in payload:
                updates["bpm"] = self._number(
                    payload, "bpm", minimum=20.0, maximum=300.0
                )
            if "beats_per_bar" in payload:
                updates["beats_per_bar"] = self._integer(
                    payload, "beats_per_bar", minimum=1, maximum=16
                )
            updates["transport_running"] = True
            updates["transport_paused"] = False
        elif event.kind == "scene.select":
            updates["scene_id"] = self._identifier(payload, "scene_id")
            updates["intensity"] = self._number(
                payload, "intensity", 0.0, minimum=0.0, maximum=1.0
            )
            if "bar_index" in payload:
                updates["bar_index"] = self._integer(
                    payload, "bar_index", minimum=0, maximum=10_000_000
                )
        elif event.kind == "scene.intensity":
            updates["intensity"] = self._number(
                payload, "intensity", minimum=0.0, maximum=1.0
            )
        elif event.kind == "macro.set":
            macro = self._identifier(payload, "name")
            updates["macro"] = (
                macro,
                self._number(payload, "value", minimum=0.0, maximum=1.0),
            )
        elif event.kind == "cue.trigger":
            updates["last_cue"] = self._identifier(payload, "name")

        for name, value in updates.items():
            if name == "macro":
                macro_name, macro_value = value
                self.macros[macro_name] = macro_value
                self.macro_updated_at[macro_name] = event.received_at
            else:
                setattr(self, name, value)

        self._record_sequence(event)
        self.source_id = event.source
        self.last_event_at = event.received_at
        self.last_event_kind = event.kind
        self.revision += 1
        return True

    def reset(self) -> None:
        self.bpm = 120.0
        self.beats_per_bar = 4
        self.beat_index = 0
        self.bar_index = 0
        self.transport_running = False
        self.transport_paused = False
        self.source_id = "internal"
        self.scene_id = "idle"
        self.intensity = 0.0
        self.macros.clear()
        self.macro_updated_at.clear()
        self.last_cue = ""
        self.last_event_at = 0.0
        self.last_event_kind = ""
        self._last_sequences.clear()
        self.revision += 1

    def snapshot(self) -> dict[str, Any]:
        return {
            "bpm": self.bpm,
            "beats_per_bar": self.beats_per_bar,
            "beat_index": self.beat_index,
            "bar_index": self.bar_index,
            "transport_running": self.transport_running,
            "transport_paused": self.transport_paused,
            "source_id": self.source_id,
            "scene_id": self.scene_id,
            "intensity": self.intensity,
            "macros": dict(self.macros),
            "last_cue": self.last_cue,
            "last_event_at": self.last_event_at,
            "last_event_kind": self.last_event_kind,
            "revision": self.revision,
        }

    def status_text(self) -> str:
        state = (
            "PAUSE" if self.transport_paused
            else "RUN" if self.transport_running
            else "STOP"
        )
        return (
            f"CTRL · {self.source_id.upper()} · {state} · "
            f"{self.bpm:g} BPM · BR {self.bar_index} · "
            f"{self.scene_id.upper()} · INT {self.intensity:.2f}"
        )
