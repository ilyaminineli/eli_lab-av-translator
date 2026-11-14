from __future__ import annotations

from core.composition import Composition, Layer
from core.event_bus import EventBus


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
        for name, value in changes.items():
            if not hasattr(layer, name):
                raise AttributeError(f"Layer has no property {name!r}")
            setattr(layer, name, value)
        layer.opacity = min(1.0, max(0.0, float(layer.opacity)))
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
