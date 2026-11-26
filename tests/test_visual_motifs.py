from __future__ import annotations

import pytest

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
        invariants={
            "identity.geometry_signature": "seven-point-cycle",
            "identity.traits.symmetry": "seven-fold",
            "parameters.period_beats": 7,
        },
        allowed_variations=[
            "identity.palette_identity",
            "parameters.radius",
            "parameters.phase",
        ],
        seed=731,
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


def test_historical_visual_motif_defaults_new_c1_2_contract_fields() -> None:
    restored = VisualMotif.from_dict(
        {
            "schema_version": 1,
            "motif_id": "historical-motif",
            "name": "Historical Motif",
            "family": "contour",
            "identity": {"geometry_signature": "ring"},
        }
    )

    assert restored.invariants == {}
    assert restored.allowed_variations == []
    assert restored.seed is None


def test_visual_motif_invariants_and_variations_are_explicit_and_stable() -> None:
    motif = _visual_motif()
    restored = VisualMotif.from_dict(motif.to_dict())

    assert restored.invariants == motif.invariants
    assert restored.allowed_variations == motif.allowed_variations
    assert restored.seed == 731
    assert "identity.geometry_signature" in restored.invariants
    assert "identity.palette_identity" in restored.allowed_variations


def test_visual_motif_rejects_invariant_drift_and_unknown_variation_paths() -> None:
    motif = _visual_motif()
    drifted = VisualMotif.from_dict(motif.to_dict())
    drifted.identity.geometry_signature = "six-point-cycle"

    try:
        drifted.normalize()
    except ValueError as error:
        assert "must match its authored value" in str(error)
    else:
        raise AssertionError("A changed invariant must be rejected.")

    unknown_path = VisualMotif(
        motif_id="unknown-variation",
        parameters={"radius": 0.4},
        allowed_variations=["parameters.unregistered"],
    )
    try:
        unknown_path.normalize()
    except ValueError as error:
        assert "does not reference an authored field" in str(error)
    else:
        raise AssertionError("Unknown variation paths must be rejected.")


def test_visual_motif_invariant_requires_the_original_scalar_type() -> None:
    motif = _visual_motif()
    motif.invariants["parameters.period_beats"] = 7.0

    try:
        motif.normalize()
    except ValueError as error:
        assert "must match its authored value" in str(error)
    else:
        raise AssertionError("An integer invariant must not silently become a float.")


def test_visual_motif_rejects_overlapping_invariants_and_allowed_variations() -> None:
    motif = _visual_motif()
    motif.allowed_variations.append("identity.geometry_signature")

    try:
        motif.normalize()
    except ValueError as error:
        assert "cannot be both invariant and variable" in str(error)
    else:
        raise AssertionError("A field cannot be protected and variable together.")


def test_visual_motif_seed_is_bounded_and_rejects_boolean_values() -> None:
    for seed in (-1, True, 18_446_744_073_709_551_616):
        motif = VisualMotif(motif_id=f"invalid-seed-{seed}", seed=seed)
        try:
            motif.normalize()
        except ValueError as error:
            assert "unsigned 64-bit integer" in str(error)
        else:
            raise AssertionError("Invalid motif seeds must be rejected.")


def _unbound_composition() -> tuple[Composition, VisualMotif]:
    composition = Composition()
    motif = _visual_motif("registered-orbit")
    composition.add_visual_motif(motif)
    composition.add_visual_motif(_visual_motif("registered-texture"))
    for layer_id in ("bind-primary", "bind-echo"):
        layer = Layer(id=layer_id, source_type="generator", generator_type="geometry")
        visual_object = VisualObject(
            object_id=layer.visual_object_id,
            layer_id=layer.id,
            lineage=VisualLineage(
                parent_object_id="historical-parent",
                origin="authored",
                source_object_ids=["historical-parent"],
            ),
        )
        composition.add_layer(layer, visual_object=visual_object)
    return composition, motif


def test_explicit_binding_supports_many_distinct_objects_and_preserves_lineage() -> None:
    composition, motif = _unbound_composition()
    first_layer = composition.get_layer("bind-primary")
    second_layer = composition.get_layer("bind-echo")
    assert first_layer is not None
    assert second_layer is not None
    first = composition.visual_object_for_layer(first_layer.id)
    second = composition.visual_object_for_layer(second_layer.id)
    assert first is not None
    assert second is not None
    before_layer = first_layer.to_dict()
    before_revision = first.revision

    bound = composition.bind_visual_object_to_motif(first.object_id, motif.motif_id)
    assert bound is first
    assert first.object_id == first_layer.visual_object_id
    assert first.revision == before_revision + 1
    assert first.lineage.motif_id == motif.motif_id
    assert first.lineage.parent_object_id == "historical-parent"
    assert first.lineage.source_object_ids == ["historical-parent"]
    assert first.lineage.origin == "authored"
    assert first_layer.to_dict() == before_layer

    # Repeating the same explicit binding is idempotent and does not bump revision.
    assert composition.bind_visual_object_to_motif(first.object_id, motif.motif_id) is first
    assert first.revision == before_revision + 1

    composition.bind_visual_object_to_motif(second.object_id, motif.motif_id)
    assert first.object_id != second.object_id
    assert [
        item.object_id
        for item in composition.get_visual_objects_for_motif(motif.motif_id)
    ] == [
        first.object_id,
        second.object_id,
    ]

    restored = Composition.from_dict(composition.to_dict())
    restored_objects = restored.get_visual_objects_for_motif(motif.motif_id)
    assert [item.object_id for item in restored_objects] == [
        first.object_id,
        second.object_id,
    ]


def test_binding_rejects_unknown_motifs_and_silent_reassignment() -> None:
    composition, motif = _unbound_composition()
    layer = composition.get_layer("bind-primary")
    assert layer is not None
    visual_object = composition.visual_object_for_layer(layer.id)
    assert visual_object is not None

    before = visual_object.to_dict()
    with pytest.raises(ValueError, match="unknown visual motif"):
        composition.bind_visual_object_to_motif(
            visual_object.object_id,
            "missing-motif-definition",
        )
    assert visual_object.to_dict() == before

    composition.bind_visual_object_to_motif(visual_object.object_id, motif.motif_id)
    after_binding = visual_object.to_dict()
    with pytest.raises(ValueError, match="unbind it explicitly first"):
        composition.bind_visual_object_to_motif(
            visual_object.object_id,
            "registered-texture",
        )
    assert visual_object.to_dict() == after_binding

    assert composition.unbind_visual_object_from_motif(visual_object.object_id)
    composition.bind_visual_object_to_motif(
        visual_object.object_id,
        "registered-texture",
    )
    assert visual_object.lineage.motif_id == "registered-texture"


def test_unbind_is_safe_for_unbound_objects_and_unknown_object_ids() -> None:
    composition, _ = _unbound_composition()
    layer = composition.get_layer("bind-primary")
    assert layer is not None
    visual_object = composition.visual_object_for_layer(layer.id)
    assert visual_object is not None
    revision = visual_object.revision

    assert not composition.unbind_visual_object_from_motif(visual_object.object_id)
    assert visual_object.revision == revision
    with pytest.raises(KeyError, match="Unknown visual object"):
        composition.bind_visual_object_to_motif("missing-object", "registered-orbit")
    with pytest.raises(KeyError, match="Unknown visual object"):
        composition.unbind_visual_object_from_motif("missing-object")


def test_unresolved_legacy_motif_reference_requires_explicit_repair() -> None:
    layer = Layer(id="historic-binding-layer")
    visual_object = VisualObject(
        object_id=layer.visual_object_id,
        layer_id=layer.id,
        lineage=VisualLineage(
            parent_object_id="historic-parent",
            motif_id="motif-from-removed-library",
            origin="legacy_import",
            source_object_ids=["historic-parent"],
        ),
    )
    composition = Composition.from_dict(
        {
            "layers": [layer.to_dict()],
            "visual_objects": [visual_object.to_dict()],
        }
    )
    motif = _visual_motif("replacement-authored-motif")
    composition.add_visual_motif(motif)

    assert composition.get_visual_motif("motif-from-removed-library") is None
    unresolved = composition.get_visual_objects_for_motif(
        "motif-from-removed-library"
    )
    assert len(unresolved) == 1
    loaded = unresolved[0]
    before_revision = loaded.revision

    with pytest.raises(ValueError, match="already references"):
        composition.bind_visual_object_to_motif(loaded.object_id, motif.motif_id)
    assert loaded.lineage.motif_id == "motif-from-removed-library"

    assert composition.unbind_visual_object_from_motif(loaded.object_id)
    rebound = composition.bind_visual_object_to_motif(loaded.object_id, motif.motif_id)
    assert rebound is loaded
    assert loaded.lineage.motif_id == motif.motif_id
    assert loaded.lineage.parent_object_id == "historic-parent"
    assert loaded.lineage.source_object_ids == ["historic-parent"]
    assert loaded.lineage.origin == "legacy_import"
    assert loaded.revision == before_revision + 2
