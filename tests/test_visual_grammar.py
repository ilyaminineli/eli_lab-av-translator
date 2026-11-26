from __future__ import annotations

import pytest

from core.composition import Composition
from core.performance_environment import PerformanceScene, PerformanceSetStore
from core.project_manager import ProjectManager
from core.visual_grammar import MotionGesture, VisualPattern, VisualPatternStep


def _gesture(gesture_id: str = "gesture-orbit") -> MotionGesture:
    return MotionGesture(
        gesture_id=gesture_id,
        name="Counter-rotating orbit",
        kind="rotate",
        parameters={"axis": "z", "degrees": 120, "return_to_origin": True},
        easing="smoothstep",
        reversible=True,
        revision=2,
    )


def _pattern() -> VisualPattern:
    return VisualPattern(
        pattern_id="pattern-call-response",
        name="Seven-beat call and response",
        family="call_and_response",
        cycle_length=7,
        cycle_unit="beats",
        timing_basis="authored_music",
        phase=0.25,
        steps=[
            VisualPatternStep(
                step_id="call",
                gesture_id="gesture-orbit",
                start_fraction=0.0,
                duration_fraction=0.25,
                intensity=0.8,
                group="call",
            ),
            VisualPatternStep(
                step_id="response",
                gesture_id="gesture-orbit",
                start_fraction=0.5,
                duration_fraction=0.25,
                intensity=0.55,
                group="response",
            ),
        ],
        seed=731,
        revision=1,
    )


def _composition_with_pattern() -> tuple[Composition, MotionGesture, VisualPattern]:
    composition = Composition()
    gesture = _gesture()
    pattern = _pattern()
    composition.add_motion_gesture(gesture)
    composition.add_visual_pattern(pattern)
    return composition, gesture, pattern


def test_motion_gesture_is_renderer_independent_and_round_trips() -> None:
    gesture = _gesture()
    restored = MotionGesture.from_dict(gesture.to_dict())

    assert restored == gesture
    assert restored.parameters == {
        "axis": "z",
        "degrees": 120,
        "return_to_origin": True,
    }
    assert restored.easing == "smoothstep"
    assert restored.reversible is True


def test_motion_gesture_rejects_unknown_kind_easing_and_unbounded_values() -> None:
    with pytest.raises(ValueError, match="Unsupported motion gesture kind"):
        MotionGesture(gesture_id="bad-kind", kind="audio_follow").normalize()

    with pytest.raises(ValueError, match="Unsupported motion easing"):
        MotionGesture(gesture_id="bad-easing", easing="random").normalize()

    with pytest.raises(ValueError, match="must be finite"):
        MotionGesture(
            gesture_id="bad-number",
            parameters={"distance": float("inf")},
        ).normalize()

    with pytest.raises(ValueError, match="at most 32 parameters"):
        MotionGesture(
            gesture_id="too-many-parameters",
            parameters={f"p{i}": i for i in range(33)},
        ).normalize()


def test_visual_pattern_cycle_and_steps_round_trip_with_explicit_music_basis() -> None:
    pattern = _pattern()
    restored = VisualPattern.from_dict(pattern.to_dict())

    assert restored == pattern
    assert restored.cycle_length == 7.0
    assert restored.cycle_unit == "beats"
    assert restored.timing_basis == "authored_music"
    assert restored.phase == pytest.approx(0.25)
    assert [step.group for step in restored.steps] == ["call", "response"]
    assert [step.start_fraction for step in restored.steps] == [0.0, 0.5]


def test_visual_pattern_rejects_confused_clock_and_music_time_domains() -> None:
    with pytest.raises(ValueError, match="requires timing basis 'authored_music'"):
        VisualPattern(
            pattern_id="implicit-beats",
            cycle_unit="beats",
            timing_basis="visual_clock",
        ).normalize()

    with pytest.raises(ValueError, match="requires timing basis 'visual_clock'"):
        VisualPattern(
            pattern_id="implicit-seconds",
            cycle_unit="seconds",
            timing_basis="authored_music",
        ).normalize()

    with pytest.raises(ValueError, match="Unsupported visual timing basis"):
        VisualPattern(
            pattern_id="audio-is-not-a-musical-clock",
            cycle_unit="beats",
            timing_basis="audio_analysis",
        ).normalize()


def test_pattern_steps_validate_normalized_phase_duration_and_identity() -> None:
    with pytest.raises(ValueError, match="start fraction must be in"):
        VisualPatternStep(
            step_id="bad-start",
            gesture_id="gesture",
            start_fraction=1.0,
        ).normalize()

    with pytest.raises(ValueError, match="duration must be greater than zero"):
        VisualPatternStep(
            step_id="bad-duration",
            gesture_id="gesture",
            duration_fraction=0.0,
        ).normalize()

    with pytest.raises(ValueError, match="intensity must be in"):
        VisualPatternStep(
            step_id="bad-intensity",
            gesture_id="gesture",
            intensity=1.1,
        ).normalize()

    with pytest.raises(ValueError, match="Duplicate visual pattern step ID"):
        VisualPattern(
            pattern_id="duplicate-step",
            steps=[
                VisualPatternStep(step_id="same", gesture_id="gesture"),
                VisualPatternStep(step_id="same", gesture_id="gesture"),
            ],
        ).normalize()


def test_visual_pattern_bounds_step_count_and_cycle_length() -> None:
    with pytest.raises(ValueError, match="more than 64 steps"):
        VisualPattern(
            pattern_id="too-many-steps",
            steps=[
                VisualPatternStep(
                    step_id=f"step-{index}",
                    gesture_id="gesture",
                    start_fraction=(index % 64) / 64,
                )
                for index in range(65)
            ],
        ).normalize()

    with pytest.raises(ValueError, match="cycle length exceeds"):
        VisualPattern(
            pattern_id="too-long-cycle",
            cycle_length=86_401,
        ).normalize()


def test_composition_registry_validates_pattern_references_and_lifecycle() -> None:
    composition = Composition()
    gesture = _gesture()
    composition.add_motion_gesture(gesture)

    pattern = _pattern()
    composition.add_visual_pattern(pattern)
    assert composition.get_motion_gesture(gesture.gesture_id) is gesture
    assert composition.get_visual_pattern(pattern.pattern_id) is pattern

    with pytest.raises(ValueError, match="still referenced"):
        composition.remove_motion_gesture(gesture.gesture_id)

    with pytest.raises(ValueError, match="already exists"):
        composition.add_motion_gesture(_gesture())

    with pytest.raises(ValueError, match="unknown motion gestures"):
        composition.add_visual_pattern(
            VisualPattern(
                pattern_id="dangling-gesture",
                steps=[
                    VisualPatternStep(
                        step_id="missing-ref",
                        gesture_id="gesture-not-registered",
                    )
                ],
            )
        )

    assert composition.remove_visual_pattern(pattern.pattern_id)
    assert composition.remove_motion_gesture(gesture.gesture_id)
    assert not composition.remove_motion_gesture(gesture.gesture_id)


def test_composition_rejects_duplicate_and_mismatched_grammar_registry_ids() -> None:
    gesture = _gesture()
    duplicate_payload = {
        "layers": [],
        "motion_gestures": [gesture.to_dict(), gesture.to_dict()],
    }
    with pytest.raises(ValueError, match="Duplicate motion gesture ID"):
        Composition.from_dict(duplicate_payload)

    mismatched_payload = {
        "layers": [],
        "motion_gestures": {"different-key": gesture.to_dict()},
    }
    with pytest.raises(ValueError, match="registry keys must match"):
        Composition.from_dict(mismatched_payload)

    pattern = _pattern()
    mismatched_pattern_payload = {
        "layers": [],
        "motion_gestures": [gesture.to_dict()],
        "visual_patterns": {"different-key": pattern.to_dict()},
    }
    with pytest.raises(ValueError, match="registry keys must match"):
        Composition.from_dict(mismatched_pattern_payload)


def test_composition_serialization_preserves_cycle_grammar_and_legacy_defaults(
    tmp_path,
) -> None:
    composition, gesture, pattern = _composition_with_pattern()
    payload = composition.to_dict()
    assert payload["motion_gestures"][0]["gesture_id"] == gesture.gesture_id
    assert payload["visual_patterns"][0]["pattern_id"] == pattern.pattern_id

    restored = Composition.from_dict(payload)
    assert restored.get_motion_gesture(gesture.gesture_id) == gesture
    assert restored.get_visual_pattern(pattern.pattern_id) == pattern

    legacy = Composition.from_dict({"name": "Legacy without grammar", "layers": []})
    assert legacy.motion_gestures == {}
    assert legacy.visual_patterns == {}

    project_path = tmp_path / "visual-grammar.eliav"
    ProjectManager().save(project_path, composition)
    restored_project, _ = ProjectManager().load(project_path)
    assert restored_project.get_visual_pattern(pattern.pattern_id) == pattern

    scene = PerformanceScene(
        scene_id="grammar-scene",
        label="Grammar scene",
        snapshot={"composition": composition.to_dict(), "decks": []},
    )
    set_payload = PerformanceSetStore.build_payload(
        composition=composition.to_dict(),
        decks=[],
        effects={},
        automation_settings={},
        performance_settings={},
        scenes=[scene],
        midi_mappings=[],
    )
    set_path = tmp_path / "visual-grammar.eliset"
    PerformanceSetStore.save(set_path, set_payload)
    recovered_set = PerformanceSetStore.load(set_path)
    recovered_composition = Composition.from_dict(recovered_set["composition"])
    recovered_pattern = recovered_composition.get_visual_pattern(pattern.pattern_id)
    assert recovered_pattern == pattern

    recovered_scene = PerformanceScene(**recovered_set["scenes"][0])
    recovered_scene.normalize()
    recovered_scene_composition = Composition.from_dict(
        recovered_scene.snapshot["composition"]
    )
    assert recovered_scene_composition.get_motion_gesture(gesture.gesture_id) == gesture
    assert recovered_scene_composition.get_visual_pattern(pattern.pattern_id) == pattern


def test_composition_bounds_motion_grammar_registry_sizes() -> None:
    composition = Composition()
    for index in range(256):
        composition.add_motion_gesture(
            MotionGesture(gesture_id=f"gesture-{index}")
        )
    with pytest.raises(ValueError, match="more than 256 motion gestures"):
        composition.add_motion_gesture(MotionGesture(gesture_id="gesture-overflow"))

    pattern_composition = Composition()
    for index in range(256):
        pattern_composition.add_visual_pattern(
            VisualPattern(pattern_id=f"pattern-{index}")
        )
    with pytest.raises(ValueError, match="more than 256 visual patterns"):
        pattern_composition.add_visual_pattern(
            VisualPattern(pattern_id="pattern-overflow")
        )


def test_pattern_numeric_validation_normalizes_extreme_values_to_value_error() -> None:
    with pytest.raises(ValueError, match="cycle length must be finite and positive"):
        VisualPattern(
            pattern_id="overflow-cycle",
            cycle_length=10**10000,
        ).normalize()

    with pytest.raises(ValueError, match="start fraction must be a finite number"):
        VisualPatternStep(
            step_id="overflow-step",
            gesture_id="gesture",
            start_fraction=10**10000,
        ).normalize()
