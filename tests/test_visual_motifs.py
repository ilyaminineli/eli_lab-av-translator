from __future__ import annotations

from core.composition import Composition, Layer
from core.performance_environment import PerformanceScene, PerformanceSetStore
from core.project_manager import ProjectManager
from core.visual_model import VisualIdentity, VisualLineage, VisualMotif, VisualObject


def _visual_motif(motif_id: str = "motif-orbit") -> VisualMotif:
    return VisualMotif(
        motif_id=motif_id,
        name="Seven-point orbit",
        family="motion",
        identity=VisualIdentity(
            geometry_signature="seven-point-cycle",
            motion_identity="counter-rotating",
            palette_identity="oxide-red-on-black",
            traits={"direction": "counter-clockwise", "symmetry": "seven-fold"},
        ),
        parameters={"period_beats": 7, "radius": 0.42, "phase": 0.25},
        description="A recurring seven-position orbital gesture.",
    )


def _composition_with_motif() -> tuple[Composition, VisualMotif]:
    composition = Composition()
    motif = _visual_motif()
    composition.add_visual_motif(motif)
    for layer_id in ("orbit-primary", "orbit-echo"):
        layer = Layer(id=layer_id, source_type="generator", generator_type="geometry")
        visual_object = VisualObject(
            object_id=layer.visual_object_id,
            layer_id=layer.id,
            lineage=VisualLineage(motif_id=motif.motif_id, origin="authored"),
        )
        composition.add_layer(layer, visual_object=visual_object)
    return composition, motif


def test_visual_motif_model_validates_identity_and_round_trips() -> None:
    motif = _visual_motif()
    restored = VisualMotif.from_dict(motif.to_dict())

    assert restored == motif
    assert restored.identity.traits["symmetry"] == "seven-fold"
    assert restored.parameters == {
        "period_beats": 7,
        "radius": 0.42,
        "phase": 0.25,
    }


def test_visual_motif_rejects_unknown_family_and_non_finite_parameters() -> None:
    invalid_family = VisualMotif(motif_id="bad-family", family="glitch")
    try:
        invalid_family.normalize()
    except ValueError as error:
        assert "Unsupported visual motif family" in str(error)
    else:
        raise AssertionError("Unknown motif family should be rejected.")

    invalid_parameter = VisualMotif(
        motif_id="bad-parameter",
        parameters={"radius": float("nan")},
    )
    try:
        invalid_parameter.normalize()
    except ValueError as error:
        assert "must be finite" in str(error)
    else:
        raise AssertionError("Non-finite motif parameters should be rejected.")


def test_composition_registry_allows_multiple_distinct_objects_per_motif() -> None:
    composition, motif = _composition_with_motif()

    first = composition.get_layer("orbit-primary")
    second = composition.get_layer("orbit-echo")
    assert first is not None
    assert second is not None
    first_object = composition.visual_object_for_layer(first.id)
    second_object = composition.visual_object_for_layer(second.id)
    assert first_object is not None
    assert second_object is not None

    assert first_object.object_id != second_object.object_id
    assert first_object.lineage.motif_id == motif.motif_id
    assert second_object.lineage.motif_id == motif.motif_id
    assert len(composition.visual_motifs) == 1
    assert composition.get_visual_motif(motif.motif_id) is motif

    restored = Composition.from_dict(composition.to_dict())
    restored_motif = restored.get_visual_motif(motif.motif_id)
    assert restored_motif == motif
    restored_objects = [
        restored.visual_object_for_layer("orbit-primary"),
        restored.visual_object_for_layer("orbit-echo"),
    ]
    assert all(item is not None for item in restored_objects)
    assert len({item.object_id for item in restored_objects if item}) == 2
    assert all(
        item.lineage.motif_id == motif.motif_id
        for item in restored_objects
        if item is not None
    )


def test_composition_rejects_duplicate_motif_ids_without_replacing_record() -> None:
    composition = Composition()
    original = _visual_motif("same-motif-id")
    composition.add_visual_motif(original)
    duplicate = VisualMotif(
        motif_id=original.motif_id,
        name="An accidental replacement",
        family="texture",
    )

    try:
        composition.add_visual_motif(duplicate)
    except ValueError as error:
        assert "Visual motif ID already exists" in str(error)
    else:
        raise AssertionError("Duplicate motif IDs should be rejected.")

    assert composition.get_visual_motif(original.motif_id) is original
    assert composition.get_visual_motif(original.motif_id).name == "Seven-point orbit"


def test_composition_rejects_mismatched_motif_registry_keys() -> None:
    motif = _visual_motif("actual-motif-id")
    payload = {
        "layers": [],
        "visual_motifs": {"incorrect-registry-key": motif.to_dict()},
    }

    try:
        Composition.from_dict(payload)
    except ValueError as error:
        assert "registry keys must match" in str(error)
    else:
        raise AssertionError("Mismatched motif registry keys should be rejected.")


def test_legacy_composition_keeps_unresolved_motif_references_without_inventing_motifs() -> None:
    layer = Layer(id="legacy-motif-layer")
    visual_object = VisualObject(
        object_id=layer.visual_object_id,
        layer_id=layer.id,
        lineage=VisualLineage(
            motif_id="motif-authored-in-an-older-tool",
            origin="legacy_import",
        ),
    )
    legacy_payload = {
        "name": "Legacy visual project",
        "layers": [layer.to_dict()],
        "visual_objects": [visual_object.to_dict()],
    }

    restored = Composition.from_dict(legacy_payload)
    item = restored.visual_object_for_layer(layer.id)
    assert item is not None
    assert item.lineage.motif_id == "motif-authored-in-an-older-tool"
    assert restored.visual_motifs == {}

    round_trip = Composition.from_dict(restored.to_dict())
    round_trip_item = round_trip.visual_object_for_layer(layer.id)
    assert round_trip_item is not None
    assert round_trip_item.lineage.motif_id == item.lineage.motif_id
    assert round_trip.visual_motifs == {}


def test_removing_layer_keeps_authored_motif_and_referenced_motif_cannot_be_deleted() -> None:
    composition, motif = _composition_with_motif()

    try:
        composition.remove_visual_motif(motif.motif_id)
    except ValueError as error:
        assert "still referenced" in str(error)
    else:
        raise AssertionError("A motif referenced by live objects cannot be removed.")

    assert composition.remove_layer("orbit-primary")
    assert composition.remove_layer("orbit-echo")
    assert composition.get_visual_motif(motif.motif_id) is motif
    assert composition.remove_visual_motif(motif.motif_id)
    assert composition.get_visual_motif(motif.motif_id) is None
    assert not composition.remove_visual_motif(motif.motif_id)


def test_project_and_performance_set_scene_snapshots_preserve_visual_motifs(tmp_path) -> None:
    composition, motif = _composition_with_motif()

    project_path = tmp_path / "motif-project.eliav"
    ProjectManager().save(project_path, composition)
    restored_project, _ = ProjectManager().load(project_path)
    assert restored_project.get_visual_motif(motif.motif_id) == motif

    scene = PerformanceScene(
        scene_id="motif-scene",
        label="Motif scene",
        snapshot={"composition": composition.to_dict(), "decks": []},
    )
    payload = PerformanceSetStore.build_payload(
        composition=composition.to_dict(),
        decks=[],
        effects={},
        automation_settings={},
        performance_settings={},
        scenes=[scene],
        midi_mappings=[],
    )
    set_path = tmp_path / "motif-set.eliset"
    PerformanceSetStore.save(set_path, payload)
    restored_payload = PerformanceSetStore.load(set_path)

    restored_set_composition = Composition.from_dict(restored_payload["composition"])
    assert restored_set_composition.get_visual_motif(motif.motif_id) == motif

    restored_scene = PerformanceScene(**restored_payload["scenes"][0])
    restored_scene.normalize()
    scene_composition = Composition.from_dict(restored_scene.snapshot["composition"])
    assert scene_composition.get_visual_motif(motif.motif_id) == motif
