from __future__ import annotations

import json
from uuid import uuid4

import pytest

from core.composition import Composition, Layer
from core.layer_manager import LayerManager
from core.project_manager import ProjectManager
from core.visual_model import (
    VisualEvent,
    VisualIdentity,
    VisualLineage,
    VisualMutationContract,
    VisualObject,
)


def test_legacy_composition_creates_identity_and_round_trips() -> None:
    legacy = {
        "name": "Legacy",
        "layers": [
            {
                "id": "layer-legacy",
                "name": "Legacy video",
                "source_type": "video",
                "source_id": "deck_a",
            }
        ],
    }

    composition = Composition.from_dict(legacy)
    layer = composition.get_layer("layer-legacy")
    assert layer is not None
    visual_object = composition.visual_object_for_layer(layer.id)
    assert visual_object is not None
    assert visual_object.layer_id == layer.id
    assert visual_object.lineage.origin == "legacy_import"

    repeated_legacy_load = Composition.from_dict(legacy)
    repeated_object = repeated_legacy_load.visual_object_for_layer(layer.id)
    assert repeated_object is not None
    assert repeated_object.object_id == visual_object.object_id

    restored = Composition.from_dict(composition.to_dict())
    restored_object = restored.visual_object_for_layer(layer.id)
    assert restored_object is not None
    assert restored_object.object_id == visual_object.object_id
    assert restored_object.identity.geometry_signature == "video"


def test_add_and_remove_layer_keep_registry_in_sync() -> None:
    composition = Composition()
    layer = Layer(id="layer-one")
    composition.add_layer(layer)

    assert composition.visual_object_for_layer(layer.id) is not None
    assert len(composition.visual_objects) == 1

    assert composition.remove_layer(layer.id)
    assert composition.visual_objects == {}
    assert not composition.remove_layer(layer.id)


def test_layer_manager_source_replacement_creates_child_identity() -> None:
    composition = Composition()
    layer = Layer(
        id="layer-video",
        source_type="video",
        source_id="deck_a",
    )
    composition.add_layer(layer)
    previous = composition.visual_object_for_layer(layer.id)
    assert previous is not None

    manager = LayerManager(composition)
    updated = manager.update_layer(
        layer.id, source_replacement=True, source_id="deck_b"
    )
    replacement = composition.visual_object_for_layer(layer.id)

    assert updated.source_id == "deck_b"
    assert replacement is not None
    assert replacement.object_id != previous.object_id
    assert replacement.lineage.parent_object_id == previous.object_id
    assert replacement.lineage.origin == "source_replacement"
    assert previous.object_id not in composition.visual_objects


def test_layer_identity_fields_cannot_be_changed_through_generic_update() -> None:
    composition = Composition()
    layer = Layer(id="layer-stable")
    composition.add_layer(layer)
    manager = LayerManager(composition)

    with pytest.raises(AttributeError, match="identity fields"):
        manager.update_layer(layer.id, visual_object_id=uuid4().hex)
    with pytest.raises(AttributeError, match="identity fields"):
        manager.update_layer(layer.id, id="another-layer")


def test_locked_layer_replacement_preserves_its_visual_object() -> None:
    live = Composition()
    locked = Layer(id="layer-locked", locked=True)
    live.add_layer(locked)
    live_object = live.visual_object_for_layer(locked.id)
    assert live_object is not None

    candidate = Composition.from_dict(
        {
            "layers": [
                {
                    "id": locked.id,
                    "name": "Snapshot replacement",
                    "source_type": "generator",
                    "generator_type": "geometry",
                },
                {
                    "id": "layer-new",
                    "name": "New layer",
                    "source_type": "generator",
                    "generator_type": "text",
                },
            ]
        }
    )
    candidate.replace_layer(locked, visual_object=live_object)

    assert candidate.get_layer(locked.id) is locked
    assert candidate.visual_object_for_layer(locked.id) is live_object
    assert len(candidate.visual_objects) == len(candidate.layers) == 2


def test_project_save_load_preserves_visual_object_identity(tmp_path) -> None:
    composition = Composition()
    layer = Layer(id="layer-persist")
    composition.add_layer(layer)
    original = composition.visual_object_for_layer(layer.id)
    assert original is not None

    path = tmp_path / "visual-identity.eliav"
    manager = ProjectManager()
    manager.save(path, composition)
    restored, _ = manager.load(path)

    result = restored.visual_object_for_layer(layer.id)
    assert result is not None
    assert result.object_id == original.object_id
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["composition"]["visual_objects"][0]["schema_version"] == 1


def test_mutation_contract_allows_declared_transforms_and_rejects_identity_reset() -> None:
    contract = VisualMutationContract()
    contract.validate("transform", {"position", "scale", "rotation"})

    with pytest.raises(ValueError, match="preserved identity"):
        contract.validate("transform", {"position", "object_id"})
    with pytest.raises(ValueError, match="forbidden"):
        contract.validate("replace_source", {"source_id"})

    conflicting = VisualMutationContract(
        preserve=["position"],
        allow=["position"],
    )
    with pytest.raises(ValueError, match="both preserve and allow"):
        conflicting.validate("transform", {"position"})


def test_visual_object_rejects_self_parent_and_duplicate_layer_association() -> None:
    object_id = uuid4().hex
    item = VisualObject(
        object_id=object_id,
        layer_id="layer-self",
        lineage=VisualLineage(parent_object_id=object_id),
    )
    with pytest.raises(ValueError, match="own parent"):
        item.normalize()

    composition = Composition()
    first = Layer(id="layer-first", visual_object_id="object-shared")
    second = Layer(id="layer-second", visual_object_id="object-shared")
    composition.add_layer(first)
    with pytest.raises(ValueError, match="Visual object ID already exists"):
        composition.add_layer(second)


def test_visual_event_requires_explicit_time_domain_shape() -> None:
    immediate = VisualEvent(event_type="fracture", object_id="object-1")
    restored = VisualEvent.from_dict(immediate.to_dict())
    assert restored.event_type == "fracture"
    assert restored.time_domain == "immediate"

    scheduled = VisualEvent(
        event_type="change_scene",
        time_domain="bar_beat",
        position={"bar": 3, "beat": 2.5},
    )
    assert VisualEvent.from_dict(scheduled.to_dict()).position == {
        "bar": 3,
        "beat": 2.5,
    }

    with pytest.raises(ValueError, match="positive bar and beat"):
        VisualEvent(
            event_type="move",
            time_domain="bar_beat",
            position={"bar": 0, "beat": 1},
        ).normalize()


def test_visual_identity_traits_round_trip() -> None:
    identity = VisualIdentity(
        geometry_signature="radial-fragment",
        palette_identity="monochrome-red",
        motion_identity="orbit-slow",
        material_identity="ink",
        traits={"edge": "rough", "symmetry": "broken"},
    )
    restored = VisualIdentity.from_dict(identity.__dict__)
    assert restored == identity


def test_layer_manager_update_is_atomic_on_late_invalid_value() -> None:
    composition = Composition()
    layer = Layer(id="layer-atomic", opacity=0.7)
    composition.add_layer(layer)
    manager = LayerManager(composition)
    before = composition.to_dict()

    with pytest.raises((TypeError, ValueError)):
        manager.update_layer(layer.id, opacity=0.2, position=(0.1,))

    assert composition.to_dict() == before


def test_layer_manager_contract_rejects_unknown_visual_property_without_mutation() -> None:
    composition = Composition()
    layer = Layer(id="layer-contract")
    composition.add_layer(layer)
    manager = LayerManager(composition)
    before = composition.to_dict()

    with pytest.raises(ValueError, match="not allowed"):
        manager.update_layer(layer.id, operation="transform", name="renamed")

    assert composition.to_dict() == before


def test_source_replacement_must_be_explicit_and_locked_layers_are_protected() -> None:
    composition = Composition()
    layer = Layer(id="layer-source")
    composition.add_layer(layer)
    manager = LayerManager(composition)
    before_id = layer.visual_object_id

    with pytest.raises(ValueError, match="source_replacement=True"):
        manager.update_layer(layer.id, source_id="other")
    assert composition.get_layer(layer.id).visual_object_id == before_id

    locked = manager.update_layer(layer.id, locked=True)
    assert locked.locked
    with pytest.raises(PermissionError):
        manager.update_layer(layer.id, opacity=0.4)
