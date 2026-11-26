from __future__ import annotations

from core.performance_timeline import PerformanceTimeline, PerformanceTimelineEvent
from core.visual_model import VisualEvent


def test_visual_event_timeline_adapter_uses_existing_bar_beat_cursor() -> None:
    timeline = PerformanceTimeline()
    event = VisualEvent(
        event_type="fracture",
        object_id="object-1",
        time_domain="bar_beat",
        position={"bar": 2, "beat": 3},
        source_id="timeline",
        sequence=1,
    )
    definition = PerformanceTimelineEvent(
        event_id="visual-001",
        bar=2,
        beat=3,
        event_type="visual_event",
        label="Fracture",
        payload={"event": event.to_dict()},
    )
    timeline.add_event(definition)
    timeline.arm()
    assert timeline.tick(2, 2, 4) == []
    due = timeline.tick(2, 3, 4)
    assert [item.event_id for item in due] == ["visual-001"]
    assert timeline.tick(2, 3, 4) == []


def test_visual_event_timeline_rejects_mismatched_position_and_time_domain() -> None:
    event = VisualEvent(event_type="move", time_domain="immediate")
    definition = PerformanceTimelineEvent(
        event_type="visual_event",
        payload={"event": event.to_dict()},
    )
    import pytest

    with pytest.raises(ValueError, match="bar_beat"):
        definition.normalize()


def test_visual_event_timeline_stable_same_position_order_and_late_skip() -> None:
    timeline = PerformanceTimeline()
    for event_id in ("visual-a", "visual-b"):
        timeline.add_event(
            PerformanceTimelineEvent(
                event_id=event_id,
                bar=1,
                beat=2,
                event_type="visual_event",
                payload={
                    "event": VisualEvent(
                        event_type="hold",
                        time_domain="bar_beat",
                        position={"bar": 1, "beat": 2},
                    ).to_dict()
                },
            )
        )
    timeline.arm()
    due = timeline.tick(1, 3, 4)
    assert [item.event_id for item in due] == ["visual-a", "visual-b"]
    assert timeline.tick(1, 3, 4) == []
