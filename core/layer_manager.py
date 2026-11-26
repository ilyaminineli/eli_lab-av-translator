from __future__ import annotations

from uuid import uuid4

from core.composition import Composition, Layer
from core.event_bus import EventBus
from core.visual_model import VisualObject


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

    def update_layer(self, layer_id: str, **changes: object) -> Layer:
        layer = self.composition.get_layer(layer_id)
        if layer is None:
            raise KeyError(f"Unknown layer: {layer_id}")
        protected = {"id", "visual_object_id"}
        attempted = protected & set(changes)
        if attempted:
            raise AttributeError(
                "Layer identity fields can only be changed through explicit "
                "composition operations: " + ", ".join(sorted(attempted))
            )

        previous_object_id = layer.visual_object_id
        previous_object = self.composition.get_visual_object(previous_object_id)
        source_fields = {
            "source_type",
            "source_id",
            "generator_type",
            "overlay_path",
            "overlay_kind",
        }
        replaces_source = bool(source_fields & set(changes))
        for name, value in changes.items():
            if not hasattr(layer, name):
                raise AttributeError(f"Layer has no property {name!r}")
            setattr(layer, name, value)
        layer.opacity = min(1.0, max(0.0, float(layer.opacity)))

        if replaces_source:
            replacement_id = uuid4().hex
            layer.visual_object_id = replacement_id
            try:
                replacement = VisualObject.from_layer(
                    layer,
                    origin="source_replacement",
                )
            except Exception:
                layer.visual_object_id = previous_object_id
                raise
            if previous_object is not None:
                replacement.lineage.parent_object_id = previous_object.object_id
            self.composition.visual_objects.pop(previous_object_id, None)
            self.composition.visual_objects[replacement.object_id] = replacement

        self.composition.sort_layers()
        if self.events:
            self.events.publish("layer.updated", layer=layer)
        return layer

    def remove_layer(self, layer_id: str) -> bool:
        removed = self.composition.remove_layer(layer_id)
        if removed and self.events:
            self.events.publish("layer.removed", layer_id=layer_id)
        return removed

    def reorder_layer(self, layer_id: str, z_index: int) -> Layer:
        return self.update_layer(layer_id, z_index=int(z_index))
