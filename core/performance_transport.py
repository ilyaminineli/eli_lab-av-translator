from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Literal

from core.performance_control import ControlEvent

Quantization = Literal["immediate", "beat", "bar", "phrase"]


@dataclass(frozen=True)
class ScheduledScene:
    scene_id: str
    intensity: float
    due_beat: int | None
    created_at: float


@dataclass
class InternalTransport:
    """Monotonic internal clock with beat/bar/phrase quantization.

    The UI timer only calls tick(); no sleeping or thread is required. Deadlines
    are advanced from the previous deadline, preventing accumulated timer drift.
    """

    bpm: float = 120.0
    beats_per_bar: int = 4
    phrase_bars: int = 4
    running: bool = False
    paused: bool = False
    total_beats: int = 0
    started_at: float = 0.0
    next_beat_at: float = 0.0
    last_tick_at: float = 0.0
    source: str = "internal"
    _pending_scenes: list[ScheduledScene] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.set_tempo(self.bpm)
        self.beats_per_bar = max(1, min(16, int(self.beats_per_bar)))
        self.phrase_bars = max(1, min(32, int(self.phrase_bars)))

    @property
    def beat_duration(self) -> float:
        return 60.0 / self.bpm

    @property
    def bar_index(self) -> int:
        return self.total_beats // self.beats_per_bar + 1

    @property
    def beat_index(self) -> int:
        return self.total_beats % self.beats_per_bar

    @property
    def phrase_index(self) -> int:
        return (self.bar_index - 1) // self.phrase_bars + 1

    @property
    def phase(self) -> float:
        if not self.running or self.paused:
            return 0.0
        remaining = max(0.0, self.next_beat_at - self.last_tick_at)
        return max(0.0, min(1.0, 1.0 - remaining / self.beat_duration))

    def set_tempo(self, bpm: float, now: float | None = None) -> None:
        value = float(bpm)
        if not math.isfinite(value) or not 20.0 <= value <= 300.0:
            raise ValueError("Tempo must be between 20 and 300 BPM.")
        previous_duration = self.beat_duration if hasattr(self, "bpm") else 0.5
        self.bpm = value
        if self.running and not self.paused:
            stamp = time.monotonic() if now is None else float(now)
            remaining = max(0.0, self.next_beat_at - stamp)
            fraction = min(1.0, remaining / previous_duration)
            self.next_beat_at = stamp + self.beat_duration * fraction

    def set_meter(self, beats_per_bar: int) -> None:
        value = int(beats_per_bar)
        if not 1 <= value <= 16:
            raise ValueError("Beats per bar must be between 1 and 16.")
        self.beats_per_bar = value

    def start(self, now: float | None = None, reset: bool = True) -> list[ControlEvent]:
        stamp = time.monotonic() if now is None else float(now)
        if reset:
            self.total_beats = 0
            self._pending_scenes.clear()
        self.running = True
        self.paused = False
        self.started_at = stamp
        self.last_tick_at = stamp
        self.next_beat_at = stamp
        return [
            ControlEvent(
                "transport.start",
                self.source,
                {"bpm": self.bpm, "beats_per_bar": self.beats_per_bar},
                received_at=stamp,
            )
        ]

    def pause(self, now: float | None = None) -> list[ControlEvent]:
        if not self.running or self.paused:
            return []
        stamp = time.monotonic() if now is None else float(now)
        self.paused = True
        self.last_tick_at = stamp
        return [ControlEvent("transport.pause", self.source, received_at=stamp)]

    def resume(self, now: float | None = None) -> list[ControlEvent]:
        if not self.running or not self.paused:
            return []
        stamp = time.monotonic() if now is None else float(now)
        self.paused = False
        self.last_tick_at = stamp
        self.next_beat_at = stamp + self.beat_duration
        return [
            ControlEvent(
                "transport.start",
                self.source,
                {"bpm": self.bpm, "beats_per_bar": self.beats_per_bar},
                received_at=stamp,
            )
        ]

    def stop(self, now: float | None = None, reset: bool = True) -> list[ControlEvent]:
        stamp = time.monotonic() if now is None else float(now)
        self.running = False
        self.paused = False
        self._pending_scenes.clear()
        if reset:
            self.total_beats = 0
        self.last_tick_at = stamp
        return [ControlEvent("transport.stop", self.source, received_at=stamp)]

    def schedule_scene(
            self,
            scene_id: str,
            intensity: float,
            quantization: Quantization = "bar",
            now: float | None = None,
    ) -> ScheduledScene:
        stamp = time.monotonic() if now is None else float(now)
        value = float(intensity)
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError("Scene intensity must be between 0 and 1.")
        if quantization not in {"immediate", "beat", "bar", "phrase"}:
            raise ValueError(f"Unsupported quantization: {quantization}")
        due: int | None = None
        if self.running and not self.paused and quantization != "immediate":
            next_beat = self.total_beats
            if quantization == "beat":
                due = next_beat
            else:
                bar_beats = self.beats_per_bar
                unit = (
                    bar_beats if quantization == "bar" else bar_beats * self.phrase_bars
                )
                due = ((next_beat + unit - 1) // unit) * unit
        item = ScheduledScene(str(scene_id), value, due, stamp)
        if due is None:
            self._pending_scenes.append(item)
        else:
            self._pending_scenes.append(item)
        return item

    def tick(
            self, now: float | None = None, max_catch_up_beats: int = 8
    ) -> list[ControlEvent]:
        stamp = time.monotonic() if now is None else float(now)
        self.last_tick_at = stamp
        if not self.running or self.paused:
            return []

        events: list[ControlEvent] = []
        emitted = 0
        while stamp >= self.next_beat_at and emitted < max(1, int(max_catch_up_beats)):
            beat_time = self.next_beat_at
            beat_index = self.total_beats % self.beats_per_bar
            bar_index = self.total_beats // self.beats_per_bar + 1
            if beat_index == 0:
                events.append(
                    ControlEvent(
                        "clock.bar",
                        self.source,
                        {
                            "bar_index": bar_index,
                            "bpm": self.bpm,
                            "beats_per_bar": self.beats_per_bar,
                        },
                        received_at=beat_time,
                    )
                )
            events.append(
                ControlEvent(
                    "clock.beat",
                    self.source,
                    {"beat_index": beat_index, "bar_index": bar_index},
                    received_at=beat_time,
                )
            )
            self.total_beats += 1
            emitted += 1
            self.next_beat_at += self.beat_duration

            due_items = [
                item
                for item in self._pending_scenes
                if item.due_beat is None or item.due_beat <= self.total_beats - 1
            ]
            for item in due_items:
                events.append(
                    ControlEvent(
                        "scene.select",
                        self.source,
                        {
                            "scene_id": item.scene_id,
                            "intensity": item.intensity,
                            "bar_index": bar_index,
                        },
                        received_at=beat_time,
                    )
                )
                self._pending_scenes.remove(item)

        return events

    def to_dict(self) -> dict[str, float | int]:
        return {
            "bpm": self.bpm,
            "beats_per_bar": self.beats_per_bar,
            "phrase_bars": self.phrase_bars,
        }

    def load_settings(self, values: dict[str, object]) -> None:
        self.set_tempo(float(values.get("bpm", self.bpm)))
        self.set_meter(int(values.get("beats_per_bar", self.beats_per_bar)))
        self.phrase_bars = max(
            1, min(32, int(values.get("phrase_bars", self.phrase_bars)))
        )
