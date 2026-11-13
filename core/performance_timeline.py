from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from config import VIDEO_DECK_IDS
from core.performance_macros import PERFORMANCE_MACRO_IDS
from effects.settings import PRESETS
from generators.palettes import palette_names

TIMELINE_VERSION = 1
MAX_TIMELINE_EVENTS = 512
MAX_TIMELINE_BAR = 1_000_000

TIMELINE_EVENT_TYPES = (
    "scene_marker",
    "phrase_marker",
    "scene_recall",
    "clip_trigger",
    "effect_change",
    "text_regenerate",
    "palette_change",
    "modulation",
    "transition_cue",
)

TIMELINE_EVENT_LABELS = {
    "scene_marker": "Scene marker",
    "phrase_marker": "Phrase marker",
    "scene_recall": "Scene recall",
    "clip_trigger": "Clip trigger",
    "effect_change": "Effect change",
    "text_regenerate": "Text regeneration",
    "palette_change": "Palette change",
    "modulation": "Modulation event",
    "transition_cue": "Transition cue",
}

EFFECT_SETTING_FIELDS = frozenset({
    "enabled", "mix", "brightness", "exposure", "contrast", "saturation", "gamma",
    "temperature", "tint", "hue", "vignette", "grain", "scanlines", "chromatic",
    "glitch", "pixelate", "posterize", "invert", "halftone", "solarize",
    "transform_mode", "transform_mix", "kaleidoscope_slices",
    "kaleidoscope_rotation", "kaleidoscope_zoom", "mosaic_tiles",
    "pixel_sort_amount", "pixel_sort_threshold", "edge_amount", "dither",
    "displacement_source_id", "displacement_amount", "displacement_scale",
    "displacement_luma", "feedback_enabled", "feedback_amount", "feedback_decay",
    "feedback_zoom", "feedback_rotation", "feedback_translate_x",
    "feedback_translate_y", "feedback_color_shift", "feedback_distortion",
    "feedback_motion_warp", "feedback_datamosh", "feedback_blend_mode",
    "feedback_delay_frames", "feedback_frozen",
})

_EFFECT_ENUMS = {
    "transform_mode": {"none", "kaleidoscope", "polar", "mosaic", "pixel_sort"},
    "feedback_blend_mode": {"normal", "add", "screen", "multiply", "difference"},
}
_IDENTIFIER = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


def _finite_number(value: object, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{field_name} must be finite.")
    return result


def _identifier(value: object, field_name: str, maximum: int = 128) -> str:
    result = str(value).strip()
    if not result or len(result) > maximum or not _IDENTIFIER.fullmatch(result):
        raise ValueError(f"{field_name} must be a short identifier.")
    return result


def _sanitize_json_value(value: object, depth: int = 0) -> object:
    """Copy a small JSON-safe payload and reject objects/oversized structures."""
    if depth > 3:
        raise ValueError("Timeline event payload is nested too deeply.")
    if value is None or isinstance(value, (str, bool, int)):
        if isinstance(value, str) and len(value) > 1024:
            raise ValueError("Timeline event text values are limited to 1024 characters.")
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Timeline event values must be finite.")
        return value
    if isinstance(value, list):
        if len(value) > 64:
            raise ValueError("Timeline event lists are limited to 64 items.")
        return [_sanitize_json_value(item, depth + 1) for item in value]
    if isinstance(value, dict):
        if len(value) > 32:
            raise ValueError("Timeline event objects are limited to 32 fields.")
        result: dict[str, object] = {}
        for key, item in value.items():
            name = str(key).strip()
            if not name or len(name) > 64:
                raise ValueError("Timeline event payload contains an invalid field name.")
            result[name] = _sanitize_json_value(item, depth + 1)
        return result
    raise ValueError("Timeline event payload must contain JSON-compatible values.")


@dataclass
class PerformanceTimelineEvent:
    """A single action or descriptive marker at a musical bar/beat position."""

    event_id: str = field(default_factory=lambda: uuid4().hex[:12])
    bar: int = 1
    beat: int = 1
    event_type: str = "phrase_marker"
    label: str = "New marker"
    payload: dict[str, object] = field(default_factory=dict)
    enabled: bool = True

    def normalize(self) -> None:
        self.event_id = _identifier(self.event_id, "Timeline event ID", 40)
        if isinstance(self.bar, bool) or not isinstance(self.bar, int):
            raise ValueError("Timeline bar must be an integer.")
        if not 1 <= self.bar <= MAX_TIMELINE_BAR:
            raise ValueError(f"Timeline bar must be between 1 and {MAX_TIMELINE_BAR}.")
        if isinstance(self.beat, bool) or not isinstance(self.beat, int):
            raise ValueError("Timeline beat must be an integer.")
        if not 1 <= self.beat <= 16:
            raise ValueError("Timeline beat must be between 1 and 16.")
        self.event_type = str(self.event_type).strip()
        if self.event_type not in TIMELINE_EVENT_TYPES:
            raise ValueError(f"Unknown timeline event type: {self.event_type}")
        self.label = str(self.label).strip()[:80]
        if not isinstance(self.enabled, bool):
            raise ValueError("Timeline event enabled state must be true or false.")
        clean = _sanitize_json_value(
            self.payload if isinstance(self.payload, dict) else {}
        )
        self.payload = dict(clean)

        if self.event_type in {"scene_marker", "phrase_marker"}:
            if not self.label:
                raise ValueError("Timeline markers need a visible label.")
            self.payload = {}
            return

        if self.event_type in {"scene_recall", "transition_cue"}:
            self.payload["scene_id"] = _identifier(
                self.payload.get("scene_id", ""), "Scene ID", 64
            )
            duration = _finite_number(
                self.payload.get(
                    "morph_seconds",
                    0.0 if self.event_type == "scene_recall" else 2.0,
                ),
                "Transition duration",
            )
            if not 0.0 <= duration <= 60.0:
                raise ValueError("Transition duration must be between 0 and 60 seconds.")
            self.payload["morph_seconds"] = duration

        elif self.event_type == "clip_trigger":
            deck_id = str(self.payload.get("deck_id", "")).strip()
            if deck_id not in VIDEO_DECK_IDS:
                raise ValueError(f"Clip trigger deck must be one of {', '.join(VIDEO_DECK_IDS)}.")
            action = str(self.payload.get("action", "play")).strip().lower()
            if action not in {"load", "play", "pause", "hold", "release", "restart", "stop", "seek"}:
                raise ValueError("Unsupported clip trigger action.")
            self.payload["deck_id"] = deck_id
            self.payload["action"] = action
            asset_id = str(self.payload.get("asset_id", "")).strip()
            if asset_id:
                self.payload["asset_id"] = _identifier(asset_id, "Media asset ID")
            else:
                self.payload.pop("asset_id", None)
            if action == "seek":
                seconds = _finite_number(self.payload.get("seconds", 0.0), "Seek position")
                if not 0.0 <= seconds <= 86400.0:
                    raise ValueError("Clip seek position must be between 0 and 86400 seconds.")
                self.payload["seconds"] = seconds
            for name in ("segment_start", "segment_end"):
                if name in self.payload and self.payload[name] is not None:
                    seconds = _finite_number(self.payload[name], name)
                    if not 0.0 <= seconds <= 86400.0:
                        raise ValueError(f"{name} must be between 0 and 86400 seconds.")
                    self.payload[name] = seconds
            if (
                    self.payload.get("segment_end") is not None
                    and float(self.payload["segment_end"])
                    <= float(self.payload.get("segment_start", 0.0))
            ):
                raise ValueError("Clip segment end must be later than its start.")
            loop_value = self.payload.get("loop", True)
            if not isinstance(loop_value, bool):
                raise ValueError("Clip loop state must be true or false.")
            self.payload["loop"] = loop_value

        elif self.event_type == "effect_change":
            preset = str(self.payload.get("preset_name", "")).strip()
            settings = self.payload.get("settings", {})
            if preset and preset not in PRESETS:
                raise ValueError(f"Unknown master effect preset: {preset}")
            if not isinstance(settings, dict):
                raise ValueError("Effect settings must be a JSON object.")
            unknown = set(settings) - EFFECT_SETTING_FIELDS
            if unknown:
                raise ValueError(
                    "Unsupported effect field(s): " + ", ".join(sorted(unknown))
                )
            clean_settings: dict[str, object] = {}
            for name, value in settings.items():
                if name in _EFFECT_ENUMS:
                    enum_value = str(value).casefold()
                    if enum_value not in _EFFECT_ENUMS[name]:
                        raise ValueError(f"Unsupported {name} value: {value}")
                    clean_settings[name] = enum_value
                elif name in {
                    "enabled", "displacement_luma", "feedback_enabled", "feedback_frozen"
                }:
                    if not isinstance(value, bool):
                        raise ValueError(f"{name} must be true or false.")
                    clean_settings[name] = value
                elif name == "displacement_source_id":
                    clean_settings[name] = str(value).strip()[:256]
                else:
                    clean_settings[name] = _finite_number(value, name)
            if not preset and not clean_settings:
                raise ValueError("Effect change needs a preset name or one or more settings.")
            self.payload = {"preset_name": preset, "settings": clean_settings}

        elif self.event_type == "text_regenerate":
            layer_id = str(self.payload.get("layer_id", "")).strip()
            if layer_id:
                self.payload["layer_id"] = _identifier(layer_id, "Text layer ID", 64)
            else:
                self.payload.pop("layer_id", None)
            if "seed" in self.payload:
                seed = self.payload["seed"]
                if isinstance(seed, bool) or not isinstance(seed, int):
                    raise ValueError("Text regeneration seed must be an integer.")
                if not 0 <= seed <= 2_147_483_647:
                    raise ValueError("Text regeneration seed is outside its permitted range.")

        elif self.event_type == "palette_change":
            palette = str(self.payload.get("palette", "")).strip()
            if not palette or palette not in palette_names():
                raise ValueError("Choose a palette from the current palette library.")
            self.payload = {"palette": palette}

        elif self.event_type == "modulation":
            macro_id = str(self.payload.get("macro_id", "")).strip()
            if macro_id not in PERFORMANCE_MACRO_IDS:
                raise ValueError(f"Modulation event macro must be one of {', '.join(PERFORMANCE_MACRO_IDS)}.")
            value = _finite_number(self.payload.get("value"), "Macro value")
            if not 0.0 <= value <= 1.0:
                raise ValueError("Macro value must be normalized between 0 and 1.")
            duration_bars = self.payload.get("duration_bars", 4)
            if (
                    isinstance(duration_bars, bool)
                    or not isinstance(duration_bars, int)
                    or not 1 <= duration_bars <= 256
            ):
                raise ValueError("Macro duration must be between 1 and 256 bars.")
            self.payload = {
                "macro_id": macro_id,
                "value": value,
                "duration_bars": duration_bars,
            }

    def to_dict(self) -> dict[str, object]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, values: dict[str, object]) -> PerformanceTimelineEvent:
        allowed = set(cls.__dataclass_fields__)
        item = cls(**{key: value for key, value in values.items() if key in allowed})
        item.normalize()
        return item

    @property
    def position(self) -> tuple[int, int]:
        return self.bar, self.beat


class PerformanceTimeline:
    """Bar/beat event list with a one-shot, transport-following playback cursor."""

    def __init__(self) -> None:
        self.events: list[PerformanceTimelineEvent] = []
        self.armed = False
        self.current_bar = 1
        self.current_beat = 1
        self.current_marker = ""
        self.last_event_label = ""
        self.last_event_type = ""
        self.last_event_result = ""
        self.last_error = ""
        self._last_position: tuple[int, int] = (0, 0)
        self._fired_ids: set[str] = set()
        self.definition_revision = 0
        self.state_revision = 0

    def list_events(self) -> list[PerformanceTimelineEvent]:
        return list(self.events)

    def _sort_events(self) -> None:
        # Python's sort is stable: events at the same beat retain insertion order.
        self.events.sort(key=lambda item: (item.bar, item.beat))

    def add_event(
            self,
            event: PerformanceTimelineEvent | dict[str, object],
    ) -> str:
        item = (
            event if isinstance(event, PerformanceTimelineEvent)
            else PerformanceTimelineEvent.from_dict(event)
        )
        item.normalize()
        if len(self.events) >= MAX_TIMELINE_EVENTS:
            raise ValueError(f"A timeline can contain at most {MAX_TIMELINE_EVENTS} events.")
        if any(existing.event_id == item.event_id for existing in self.events):
            raise ValueError(f"Duplicate timeline event ID: {item.event_id}")
        self.events.append(item)
        self._sort_events()
        self.definition_revision += 1
        self.state_revision += 1
        return item.event_id

    def update_event(
            self,
            event_id: str,
            changes: PerformanceTimelineEvent | dict[str, object],
    ) -> None:
        index = next(
            (i for i, item in enumerate(self.events) if item.event_id == event_id),
            None,
        )
        if index is None:
            raise KeyError(f"Unknown timeline event: {event_id}")
        existing = self.events[index]
        if isinstance(changes, PerformanceTimelineEvent):
            item = changes
        else:
            values = existing.to_dict()
            values.update(dict(changes))
            values["event_id"] = existing.event_id
            item = PerformanceTimelineEvent.from_dict(values)
        item.normalize()
        self.events[index] = item
        self._sort_events()
        self.definition_revision += 1
        self.state_revision += 1
        self._fired_ids.discard(event_id)

    def remove_event(self, event_id: str) -> bool:
        before = len(self.events)
        self.events = [item for item in self.events if item.event_id != str(event_id)]
        removed = len(self.events) != before
        if removed:
            self._fired_ids.discard(str(event_id))
            self.definition_revision += 1
            self.state_revision += 1
        return removed

    def clear_events(self) -> None:
        if not self.events:
            return
        self.events.clear()
        self._fired_ids.clear()
        self.current_marker = ""
        self.definition_revision += 1
        self.state_revision += 1

    def arm(
            self,
            current_bar: int = 1,
            current_beat: int = 1,
            transport_running: bool = False,
    ) -> None:
        bar = max(1, min(MAX_TIMELINE_BAR, int(current_bar)))
        beat = max(1, min(16, int(current_beat)))
        self.armed = True
        self.current_bar = bar
        self.current_beat = beat
        # Arming while stopped starts from bar 1. Arming mid-show waits for the
        # next musical position, avoiding an accidental retrigger at the cursor.
        self._last_position = (bar, beat) if transport_running else (0, 0)
        self._fired_ids.clear()
        self.last_event_label = ""
        self.last_event_type = ""
        self.last_event_result = "ARMED · waiting for transport" if not transport_running else "ARMED"
        self.last_error = ""
        self.state_revision += 1

    def synchronize_position(
            self,
            bar: int,
            beat: int,
            beats_per_bar: int = 4,
    ) -> None:
        """Prime a running show at a received clock position without replaying earlier bars."""
        bar_value = max(1, min(MAX_TIMELINE_BAR, int(bar)))
        beat_value = max(1, min(max(1, min(16, int(beats_per_bar))), int(beat)))
        position = (bar_value, beat_value)
        self._fired_ids = {
            event.event_id for event in self.events
            if event.position < position
        }
        # Mark bars before the received clock as elapsed, but leave the exact
        # received position eligible so a marker on this bar/beat can still fire.
        self._fired_ids = {
            event.event_id for event in self.events
            if event.position < position
        }
        self._last_position = (
            (bar_value, beat_value - 1)
            if beat_value > 1
            else (max(0, bar_value - 1), 16)
        )
        self.current_bar, self.current_beat = position
        self.state_revision += 1

    def disarm(self, reset_cursor: bool = False) -> None:
        changed = self.armed
        self.armed = False
        if reset_cursor:
            self.current_bar = 1
            self.current_beat = 1
            self._last_position = (0, 0)
            self._fired_ids.clear()
            changed = True
        self.last_event_result = "DISARMED"
        if changed:
            self.state_revision += 1

    def reset_playback(self) -> None:
        self.armed = False
        self.current_bar = 1
        self.current_beat = 1
        self._last_position = (0, 0)
        self._fired_ids.clear()
        self.current_marker = ""
        self.last_event_label = ""
        self.last_event_type = ""
        self.last_event_result = "REWOUND"
        self.last_error = ""
        self.state_revision += 1

    def tick(
            self,
            bar: int,
            beat: int,
            beats_per_bar: int = 4,
    ) -> list[PerformanceTimelineEvent]:
        current = (
            max(1, min(MAX_TIMELINE_BAR, int(bar))),
            max(1, min(max(1, min(16, int(beats_per_bar))), int(beat))),
        )
        if current != (self.current_bar, self.current_beat):
            self.current_bar, self.current_beat = current
        if not self.armed:
            return []

        if current < self._last_position:
            # A transport restart/rewind makes later events eligible again.
            self._fired_ids = {
                event_id for event_id in self._fired_ids
                if (
                    (item := next(
                        (candidate for candidate in self.events
                         if candidate.event_id == event_id),
                        None,
                    )) is not None
                    and item.position < current
                )
            }
            previous = (current[0], current[1] - 1) if current[1] > 1 else (
                max(0, current[0] - 1), 16
            )
            self._last_position = previous

        due = [
            item for item in self.events
            if item.enabled
            and item.event_id not in self._fired_ids
            and self._last_position < item.position <= current
            and item.beat <= max(1, min(16, int(beats_per_bar)))
        ]
        for item in due:
            self._fired_ids.add(item.event_id)
        self._last_position = current
        if due:
            self.state_revision += 1
        return due

    def record_result(
            self,
            event: PerformanceTimelineEvent,
            success: bool,
            message: str,
    ) -> None:
        self.last_event_label = event.label or TIMELINE_EVENT_LABELS[event.event_type]
        self.last_event_type = event.event_type
        self.last_event_result = ("OK · " if success else "SKIPPED · ") + str(message)
        self.last_error = "" if success else str(message)
        if event.event_type in {"scene_marker", "phrase_marker"} and success:
            self.current_marker = self.last_event_label
        self.state_revision += 1

    def to_dict(self) -> dict[str, object]:
        """Serialize definitions only; an opened project never resumes armed playback."""
        return {
            "version": TIMELINE_VERSION,
            "events": [item.to_dict() for item in self.events],
        }

    def load_dict(self, values: object) -> None:
        raw_events = (
            values.get("events", [])
            if isinstance(values, dict) else []
        )
        result: list[PerformanceTimelineEvent] = []
        seen: set[str] = set()
        if isinstance(raw_events, list):
            for raw in raw_events[:MAX_TIMELINE_EVENTS]:
                if not isinstance(raw, dict):
                    continue
                try:
                    item = PerformanceTimelineEvent.from_dict(raw)
                except (TypeError, ValueError, KeyError):
                    continue
                if item.event_id in seen:
                    continue
                seen.add(item.event_id)
                result.append(item)
        self.events = result
        self._sort_events()
        self.armed = False
        self.current_bar = 1
        self.current_beat = 1
        self.current_marker = ""
        self.last_event_label = ""
        self.last_event_type = ""
        self.last_event_result = "READY"
        self.last_error = ""
        self._last_position = (0, 0)
        self._fired_ids.clear()
        self.definition_revision += 1
        self.state_revision += 1

    def snapshot(self) -> dict[str, object]:
        return {
            "armed": self.armed,
            "current_bar": self.current_bar,
            "current_beat": self.current_beat,
            "current_marker": self.current_marker,
            "last_event_label": self.last_event_label,
            "last_event_type": self.last_event_type,
            "last_event_result": self.last_event_result,
            "last_error": self.last_error,
            "event_count": len(self.events),
            "enabled_count": sum(item.enabled for item in self.events),
            "definition_revision": self.definition_revision,
            "state_revision": self.state_revision,
        }
