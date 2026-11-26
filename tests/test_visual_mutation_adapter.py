from __future__ import annotations

import pytest

from core.application import Application
from core.automation import AutomationDirector
from core.composition import Composition, Layer
from core.layer_manager import LayerManager
from core.performance_modifiers import (
    LayerPerformanceModifier,
    LayerPerformanceModifierEngine,
)
from core.visual_model import VisualMutationContract
from core.visual_mutation_adapter import VisualMutationAdapter


def make_adapter(
    composition: Composition,
    on_commit=None,
) -> VisualMutationAdapter:
    return VisualMutationAdapter(
        LayerManager(composition),
        on_commit=on_commit,
    )


def test_adapter_commits_batch_once_and_preserves_shared_layer_list() -> None:
    composition = Composition()
    layer = Layer(id="layer-batch", opacity=0.8)
    composition.add_layer(layer)
    shared_layers = composition.layers
    original_object = composition.visual_object_for_layer(layer.id)
    assert original_object is not None
    notifications = []

    adapter = make_adapter(
        composition,
        lambda updated, changed, source: notifications.append(
            (updated.id, changed, source)
        ),
    )
    updated = adapter.apply_changes(
        layer.id,
        {"opacity": 0.35, "position": (0.2, 0.7), "rotation": 16.0},
        source="automation",
    )

    assert composition.layers is shared_layers
    assert composition.get_layer(layer.id) is updated
    assert updated.opacity == pytest.approx(0.35)
    assert updated.position == (0.2, 0.7)
    assert updated.rotation == pytest.approx(16.0)
    current_object = composition.visual_object_for_layer(layer.id)
    assert current_object is not None
    assert current_object.object_id == original_object.object_id
    assert current_object.revision == original_object.revision + 1
    assert notifications == [
        (
            layer.id,
            frozenset({"opacity", "position", "rotation"}),
            "automation",
        )
    ]


def test_candidate_mutation_rolls_back_when_validation_rejects() -> None:
    composition = Composition()
    layer = Layer(id="layer-rollback", opacity=0.65)
    composition.add_layer(layer)
    adapter = make_adapter(composition)
    before = composition.to_dict()
    original_layers = composition.layers

    def invalid_candidate(candidate: Layer) -> None:
        candidate.opacity = 0.1
        candidate.position = (0.5,)

    with pytest.raises((TypeError, ValueError)):
        adapter.mutate_layer(
            layer.id,
            invalid_candidate,
            source="automation",
        )

    assert composition.to_dict() == before
    assert composition.layers is original_layers


def test_candidate_can_explicitly_reject_without_committing() -> None:
    composition = Composition()
    layer = Layer(id="layer-reject", opacity=0.9)
    composition.add_layer(layer)
    adapter = make_adapter(composition)
    before = composition.to_dict()

    result = adapter.mutate_layer(
        layer.id,
        lambda candidate: False,
        source="automation",
    )

    assert result is None
    assert composition.to_dict() == before


def test_adapter_obeys_lock_and_contract_rejections() -> None:
    composition = Composition()
    layer = Layer(id="layer-locked", locked=True)
    composition.add_layer(layer)
    adapter = make_adapter(composition)

    with pytest.raises(PermissionError, match="locked"):
        adapter.apply_changes(
            layer.id,
            {"opacity": 0.2},
            source="automation",
        )

    unlocked = Layer(id="layer-contract")
    composition.add_layer(unlocked)
    before = composition.to_dict()
    with pytest.raises(ValueError, match="not allowed"):
        adapter.apply_changes(
            unlocked.id,
            {"name": "unauthorized rename"},
            source="automation",
        )
    assert composition.to_dict() == before


def test_automation_director_uses_injected_mutation_adapter() -> None:
    composition = Composition()
    layer = Layer(id="layer-auto", opacity=0.8)
    composition.add_layer(layer)
    director = AutomationDirector(seed=4)
    director.update_layers(composition.layers)
    director.set_mutation_adapter(make_adapter(composition))

    updated = director._apply_layer_changes(layer.id, opacity=0.42)

    assert updated is not None
    assert composition.get_layer(layer.id).opacity == pytest.approx(0.42)
    assert composition.visual_object_for_layer(layer.id).revision == 1


def test_performance_modifier_engine_commits_through_injected_adapter() -> None:
    composition = Composition()
    modifier = LayerPerformanceModifier(
        modifier_id="opacity-mod",
        source_id="audio.rms",
        target_id="layer.opacity",
        depth=0.25,
        polarity="positive",
        attack_ms=1.0,
        release_ms=1.0,
    )
    layer = Layer(
        id="layer-modifier",
        opacity=0.5,
        performance_modifiers=[modifier.to_dict()],
    )
    composition.add_layer(layer)
    engine = LayerPerformanceModifierEngine(make_adapter(composition))

    def get_target(layer_id: str, target_id: str) -> float | None:
        target = composition.get_layer(layer_id)
        return target.opacity if target_id == "layer.opacity" and target else None

    def set_target(
        layer_id: str,
        target_id: str,
        value: float,
        candidate: Layer | None = None,
    ) -> bool:
        if target_id != "layer.opacity" or candidate is None:
            return False
        candidate.opacity = value
        return True

    output = engine.evaluate(
        composition.layers,
        {"audio.rms": 1.0},
        get_target,
        set_target,
        now=10.0,
    )

    assert output[(layer.id, "layer.opacity")] == pytest.approx(0.75)
    assert composition.get_layer(layer.id).opacity == pytest.approx(0.75)
    assert composition.visual_object_for_layer(layer.id).revision == 1


def test_performance_modifier_respects_manual_override_with_adapter() -> None:
    composition = Composition()
    modifier = LayerPerformanceModifier(
        modifier_id="manual-protected",
        source_id="audio.rms",
        target_id="layer.opacity",
        depth=0.5,
    )
    layer = Layer(
        id="layer-manual",
        opacity=0.5,
        performance_modifiers=[modifier.to_dict()],
    )
    composition.add_layer(layer)
    engine = LayerPerformanceModifierEngine(make_adapter(composition))
    engine.notify_manual_override(
        layer.id,
        {"layer.opacity"},
        layer.performance_modifiers,
        duration_seconds=5.0,
        now=10.0,
    )

    def get_target(layer_id: str, target_id: str) -> float | None:
        target = composition.get_layer(layer_id)
        return target.opacity if target_id == "layer.opacity" and target else None

    def set_target(
        layer_id: str,
        target_id: str,
        value: float,
        candidate: Layer | None = None,
    ) -> bool:
        if target_id != "layer.opacity" or candidate is None:
            return False
        candidate.opacity = value
        return True

    engine.evaluate(
        composition.layers,
        {"audio.rms": 1.0},
        get_target,
        set_target,
        now=12.0,
    )

    assert composition.get_layer(layer.id).opacity == pytest.approx(0.5)
    assert composition.visual_object_for_layer(layer.id).revision == 0


def test_historical_default_contract_expands_only_legacy_defaults() -> None:
    historical = {
        "preserve": ["object_id", "layer_id", "role", "identity", "lineage"],
        "allow": [
            "position",
            "scale",
            "rotation",
            "opacity",
            "material",
            "palette",
            "motion",
            "blend_mode",
            "visibility",
        ],
        "forbid": ["replace_source", "reset_identity", "delete"],
    }

    restored = VisualMutationContract.from_dict(historical)
    assert "generator_settings" in restored.allow
    assert "layer_effects" in restored.allow
    assert "visible" in restored.allow
    assert "locked" in restored.allow

    restrictive = VisualMutationContract.from_dict(
        {"preserve": ["position"], "allow": ["rotation"], "forbid": []}
    )
    assert restrictive.allow == ["rotation"]


def test_modulation_target_writer_uses_shared_mutation_adapter() -> None:
    composition = Composition()
    layer = Layer(id="layer-modulation-target", opacity=0.8)
    composition.add_layer(layer)
    adapter = make_adapter(composition)
    application = object.__new__(Application)
    application.composition = composition
    application._selected_layer_id = layer.id
    application.visual_mutation_adapter = adapter
    application.events = __import__("core.event_bus", fromlist=["EventBus"]).EventBus()
    application._overlay_images = {}

    assert application._set_modulation_target("selected_layer.opacity", 0.3)
    assert composition.get_layer(layer.id).opacity == pytest.approx(0.3)
    assert composition.visual_object_for_layer(layer.id).revision == 1
