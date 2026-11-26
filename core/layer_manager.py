from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
from uuid import uuid4

from core.composition import Composition, Layer
from core.event_bus import EventBus
from core.visual_model import VisualObject

SOURCE_FIELDS = frozenset(
    {"source_type", "source_id", "generator_type", "overlay_path", "overlay_kind"}
)
IDENTITY_FIELDS = frozenset({"id", "visual_object_id"})
LAYER_FIELDS = frozenset(item.name for item in fields(Layer))


class LayerManager:
    def __init__(
        self, composition: Composition, events: EventBus | None = None
    ) -> None:
        self.composition = composition
        self.events = events

    def create_layer(self, **properties: object) -> Layer:
        layer = Layer(**properties)
        self.composition.add_layer(layer)
        if self.events:
            self.events.publish("layer.added", layer=layer)
        return layer

    def update_layer(
        self,
        layer_id: str,
        *,
        operation: str = "transform",
        source_replacement: bool = False,
        respect_lock: bool = True,
        **changes: object,
    ) -> Layer:
        """Apply a validated candidate atomically; source changes create lineage.

        The live layer and registry are untouched until candidate validation and
        replacement-object construction have succeeded.
        """
        current = self.composition.get_layer(layer_id)
        if current is None:
            raise KeyError(f"Unknown layer: {layer_id}")
        attempted = IDENTITY_FIELDS & set(changes)
        if attempted:
            raise AttributeError(
                "Layer identity fields can only be changed through explicit "
                "composition operations: " + ", ".join(sorted(attempted))
            )
        unknown = set(changes) - LAYER_FIELDS
        if unknown:
            raise AttributeError(
                "Layer has no property/properties: " + ", ".join(sorted(unknown))
            )
        if respect_lock and current.locked:
            raise PermissionError(f"Layer {layer_id!r} is locked.")

        replaces_source = bool(SOURCE_FIELDS & set(changes))
        if replaces_source and not source_replacement:
            raise ValueError(
                "Source-defining changes require source_replacement=True."
            )
        if source_replacement and not replaces_source:
            raise ValueError(
                "source_replacement=True requires at least one source-defining field."
            )

        visual_object = self.composition.visual_object_for_layer(layer_id)
        if visual_object is None:
            raise RuntimeError(f"Layer {layer_id!r} has no registered visual object.")
        changed_properties = set(changes)
        if replaces_source:
            visual_object.mutation_contract.validate(
                "replace_source", changed_properties
            )
        else:
            visual_object.mutation_contract.validate(operation, changed_properties)

        candidate = deepcopy(current)
        for name, value in changes.items():
            setattr(candidate, name, value)
        candidate.__post_init__()

        replacement_object = visual_object
        if replaces_source:
            candidate.visual_object_id = uuid4().hex
            replacement_object = VisualObject.from_layer(
                candidate, origin="source_replacement"
            )
            replacement_object.lineage.parent_object_id = visual_object.object_id
            replacement_object.revision = visual_object.revision + 1
        else:
            replacement_object = deepcopy(visual_object)
            if changes:
                replacement_object.revision += 1
            replacement_object.normalize()

        # Composition.replace_layer stages and validates both records before commit.
        self.composition.replace_layer(candidate, replacement_object)

        if self.events:
            self.events.publish("layer.updated", layer=candidate)
            if replaces_source:
                self.events.publish(
                    "visual.object.replaced",
                    previous_object_id=visual_object.object_id,
                    object_id=replacement_object.object_id,
                    layer_id=layer_id,
                )
        return candidate

    def remove_layer(self, layer_id: str, *, respect_lock: bool = True) -> bool:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            return False
        if respect_lock and layer.locked:
            raise PermissionError(f"Layer {layer_id!r} is locked.")
        removed = self.composition.remove_layer(layer_id)
        if removed and self.events:
            self.events.publish("layer.removed", layer_id=layer_id)
        return removed

    def reorder_layer(self, layer_id: str, z_index: int) -> Layer:
        return self.update_layer(layer_id, z_index=int(z_index))
