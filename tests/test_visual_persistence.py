from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.application import Application
from core.composition import Composition, Layer
from core.event_bus import EventBus
from core.layer_manager import LayerManager
from core.performance_environment import PerformanceScene, PerformanceSetStore
from core.project_manager import ProjectManager
from core.visual_model import VisualLineage, VisualObject
from core.visual_mutation_adapter import VisualMutationAdapter


FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> Path:
    return FIXTURES / name


def _assert_registry_is_one_to_one(composition: Composition) -> None:
    expected_ids = {layer.visual_object_id for layer in composition.layers}
    assert set(composition.visual_objects) == expected_ids
    assert len(composition.visual_objects) == len(composition.layers)
    for layer in composition.layers:
        visual_object = composition.visual_object_for_layer(layer.id)
        assert visual_object is not None
        assert visual_object.object_id == layer.visual_object_id
        assert visual_object.layer_id == layer.id


def test_historical_eliav_v2_loads_all_layer_state_and_migrates_stably(
    tmp_path: Path,
) -> None:
    manager = ProjectManager()
    source = _fixture("legacy_project_v2.eliav")

    composition, decks = manager.load(source)
    generator = composition.get_layer("legacy-generator")
    overlay = composition.get_layer("legacy-overlay")

    assert generator is not None
    assert generator.name == "Legacy Geometry"
    assert generator.source_type == "generator"
    assert generator.generator_type == "geometry"
    assert generator.generator_settings["pattern"] == "radial"
    assert generator.visible is True
    assert generator.locked is False
    assert generator.opacity == pytest.approx(0.72)
    assert generator.blend_mode == "add"
    assert generator.position == (0.18, 0.64)
    assert generator.scale == (1.25, 0.85)
    assert generator.rotation == pytest.approx(-22.5)
    assert generator.z_index == 4
    assert generator.performance_modifiers[0]["modifier_id"] == (
        "legacy-opacity-modifier"
    )
    assert generator.layer_effects["mix"] == pytest.approx(0.35)
    assert generator.fx_manual_override_until == pytest.approx(12.5)

    assert overlay is not None
    assert overlay.overlay_path == "C:/AVMedia/film-grain.gif"
    assert overlay.overlay_kind == "animated_image"
    assert overlay.overlay_in == pytest.approx(1.25)
    assert overlay.overlay_out == pytest.approx(5.5)
    assert overlay.overlay_speed == pytest.approx(0.75)
    assert overlay.overlay_frame_hold == 2
    assert overlay.overlay_scene_sync is True
    assert overlay.overlay_mask_mode == "luma"
    assert overlay.overlay_mask_source == "mask-source-legacy"
    assert overlay.visible is False
    assert overlay.opacity == pytest.approx(0.81)
    assert overlay.blend_mode == "screen"

    assert decks[0]["asset_id"] == "asset-legacy"
    assert decks[0]["segment_start"] == pytest.approx(2.0)
    assert manager.last_app_state["performance_settings"]["active_palette"] == "Clean"

    visual_object = composition.visual_object_for_layer(generator.id)
    assert visual_object is not None
    assert visual_object.lineage.origin == "legacy_import"
    _assert_registry_is_one_to_one(composition)

    repeated, _ = manager.load(source)
    repeated_object = repeated.visual_object_for_layer(generator.id)
    assert repeated_object is not None
    assert repeated_object.object_id == visual_object.object_id

    migrated_path = tmp_path / "migrated.eliav"
    manager.save(
        migrated_path,
        composition,
        decks=decks,
        app_state=manager.last_app_state,
    )
    saved_payload = json.loads(migrated_path.read_text(encoding="utf-8"))
    assert saved_payload["schema_version"] == 2
    assert saved_payload["composition"]["layers"][0]["visual_object_id"]
    assert saved_payload["composition"]["visual_objects"]

    restored, restored_decks = manager.load(migrated_path)
    restored_object = restored.visual_object_for_layer(generator.id)
    assert restored_object is not None
    assert restored_object.object_id == visual_object.object_id
    assert restored_decks == decks
    _assert_registry_is_one_to_one(restored)


def test_historical_eliset_v1_migrates_package_and_embedded_scene_compositions(
    tmp_path: Path,
) -> None:
    source = _fixture("legacy_performance_set_v1.eliset")
    payload = PerformanceSetStore.load(source)

    composition = Composition.from_dict(payload["composition"])
    generator = composition.get_layer("legacy-generator")
    assert generator is not None
    visual_object = composition.visual_object_for_layer(generator.id)
    assert visual_object is not None
    assert visual_object.lineage.origin == "legacy_import"
    _assert_registry_is_one_to_one(composition)

    scene = PerformanceScene(**payload["scenes"][0])
    scene.normalize()
    scene_composition = Composition.from_dict(scene.snapshot["composition"])
    scene_generator = scene_composition.get_layer("legacy-generator")
    assert scene_generator is not None
    scene_object = scene_composition.visual_object_for_layer(scene_generator.id)
    assert scene_object is not None
    assert scene_object.lineage.origin == "legacy_import"
    _assert_registry_is_one_to_one(scene_composition)

    payload["composition"] = composition.to_dict()
    scene.snapshot["composition"] = scene_composition.to_dict()
    payload["scenes"] = [scene.to_dict()]
    migrated_path = tmp_path / "migrated.eliset"
    PerformanceSetStore.save(migrated_path, payload)

    restored_payload = PerformanceSetStore.load(migrated_path)
    restored_composition = Composition.from_dict(restored_payload["composition"])
    restored_scene = PerformanceScene(**restored_payload["scenes"][0])
    restored_scene_composition = Composition.from_dict(
        restored_scene.snapshot["composition"]
    )
    assert (
        restored_composition.visual_object_for_layer(generator.id).object_id
        == visual_object.object_id
    )
    assert (
        restored_scene_composition.visual_object_for_layer(scene_generator.id).object_id
        == scene_object.object_id
    )
    _assert_registry_is_one_to_one(restored_composition)
    _assert_registry_is_one_to_one(restored_scene_composition)


def test_application_performance_set_restore_uses_legacy_project_migration() -> None:
    app = object.__new__(Application)
    app.events = EventBus()
    app.current_project_path = Path("previous-project.eliav")
    restored: dict[str, object] = {}

    def load_staged_project(path: str | Path) -> None:
        composition, decks = ProjectManager().load(path)
        restored["composition"] = composition
        restored["decks"] = decks

    def set_mappings(mappings) -> None:
        restored["mappings"] = list(mappings)

    app.load_project = load_staged_project
    app.set_midi_mappings = set_mappings

    app.load_performance_set(_fixture("legacy_performance_set_v1.eliset"))

    composition = restored["composition"]
    assert isinstance(composition, Composition)
    _assert_registry_is_one_to_one(composition)
    generator = composition.get_layer("legacy-generator")
    assert generator is not None
    assert composition.visual_object_for_layer(generator.id).lineage.origin == (
        "legacy_import"
    )
    assert restored["decks"][0]["asset_id"] == "asset-legacy"
    assert restored["mappings"] == []
    assert app.current_project_path is None
    assert set(app.performance_scenes) == {"historic-scene"}
    _assert_registry_is_one_to_one(
        Composition.from_dict(
            app.performance_scenes["historic-scene"].snapshot["composition"]
        )
    )


def test_application_scene_recall_keeps_live_locked_layer_and_visual_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = PerformanceSetStore.load(
        _fixture("legacy_performance_set_v1.eliset")
    )
    scene = PerformanceScene(**payload["scenes"][0])
    scene.normalize()

    scene_layer_id = "legacy-generator"
    live = Composition()
    locked_layer = Layer(
        id=scene_layer_id,
        name="Operator-owned locked layer",
        source_type="generator",
        generator_type="geometry",
        locked=True,
        opacity=0.31,
        position=(0.11, 0.89),
        rotation=41.0,
    )
    live.add_layer(locked_layer)
    live_object = live.visual_object_for_layer(locked_layer.id)
    assert live_object is not None
    live.add_layer(Layer(id="live-only-unlocked-layer", name="Discard on recall"))

    app = object.__new__(Application)
    app.performance_scenes = {scene.scene_id: scene}
    app.composition = live
    app.events = EventBus()
    app.visual_mutation_adapter = VisualMutationAdapter(LayerManager(live, app.events))
    app.automation = SimpleNamespace(update_layers=lambda layers: None)
    app.performance_modifier_engine = SimpleNamespace(reset=lambda: None)
    app.active_palette = "Clean"

    monkeypatch.setattr(
        Application,
        "_restore_scene_decks",
        lambda self, decks: None,
    )
    monkeypatch.setattr(Application, "_clear_overlays", lambda self: None)
    monkeypatch.setattr(
        Application,
        "_restore_scene_modulators",
        lambda self, snapshot: None,
    )
    monkeypatch.setattr(
        "core.application.install_default_performance_macro_modifiers",
        lambda layers: None,
    )

    assert app.recall_performance_scene(scene.scene_id)

    restored_locked = app.composition.get_layer(scene_layer_id)
    assert restored_locked is locked_layer
    assert restored_locked.name == "Operator-owned locked layer"
    assert restored_locked.locked is True
    assert restored_locked.opacity == pytest.approx(0.31)
    assert restored_locked.position == (0.11, 0.89)
    assert restored_locked.rotation == pytest.approx(41.0)
    assert app.composition.visual_object_for_layer(scene_layer_id) is live_object
    assert app.composition.get_layer("scene-only-layer") is not None
    assert app.composition.get_layer("live-only-unlocked-layer") is None
    _assert_registry_is_one_to_one(app.composition)


def test_motif_lineage_contract_preserves_instance_identity_and_provenance() -> None:
    motif_id = "authored-motif-fragments"
    root = VisualObject(
        object_id="object-root",
        layer_id="layer-root",
        lineage=VisualLineage(origin="authored", motif_id=motif_id),
    )
    duplicate = VisualObject(
        object_id="object-duplicate",
        layer_id="layer-duplicate",
        lineage=VisualLineage(
            parent_object_id=root.object_id,
            motif_id=motif_id,
            origin="duplication",
            source_object_ids=[root.object_id],
        ),
    )
    left_fragment = VisualObject(
        object_id="object-fragment-left",
        layer_id="layer-fragment-left",
        lineage=VisualLineage(
            parent_object_id=root.object_id,
            motif_id=motif_id,
            origin="fracture",
            source_object_ids=[root.object_id],
        ),
    )
    right_fragment = VisualObject(
        object_id="object-fragment-right",
        layer_id="layer-fragment-right",
        lineage=VisualLineage(
            parent_object_id=root.object_id,
            motif_id=motif_id,
            origin="fracture",
            source_object_ids=[root.object_id],
        ),
    )
    assembled = VisualObject(
        object_id="object-assembled",
        layer_id="layer-assembled",
        lineage=VisualLineage(
            origin="assembly",
            source_object_ids=[left_fragment.object_id, right_fragment.object_id],
        ),
    )
    returned = VisualObject(
        object_id="object-returned",
        layer_id="layer-returned",
        lineage=VisualLineage(
            motif_id=motif_id,
            origin="motif_return",
            source_object_ids=[root.object_id, assembled.object_id],
        ),
    )

    originals = (root, duplicate, left_fragment, right_fragment, assembled, returned)
    instances = [VisualObject.from_dict(item.to_dict()) for item in originals]
    assert len({item.object_id for item in instances}) == len(instances)
    assert duplicate.lineage.parent_object_id == root.object_id
    assert duplicate.lineage.motif_id == root.lineage.motif_id
    assert left_fragment.lineage.motif_id == right_fragment.lineage.motif_id == motif_id
    assert assembled.lineage.parent_object_id is None
    assert assembled.lineage.motif_id is None
    assert assembled.lineage.source_object_ids == [
        left_fragment.object_id,
        right_fragment.object_id,
    ]
    assert returned.lineage.origin == "motif_return"
    assert returned.lineage.motif_id == motif_id
    assert returned.lineage.source_object_ids == [
        root.object_id,
        assembled.object_id,
    ]
    assert all(
        restored.to_dict() == original.to_dict()
        for restored, original in zip(instances, originals, strict=True)
    )


def test_visual_registry_rejects_orphan_records_with_actionable_error() -> None:
    malformed = {
        "name": "Malformed registry",
        "layers": [{"id": "present-layer"}],
        "visual_objects": [{
            "object_id": "orphan-object",
            "layer_id": "missing-layer",
        }],
    }

    with pytest.raises(ValueError, match="visual objects without layers"):
        Composition.from_dict(malformed)
