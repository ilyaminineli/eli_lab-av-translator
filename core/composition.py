from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

from config import DEFAULT_CANVAS_HEIGHT, DEFAULT_CANVAS_WIDTH, DEFAULT_FPS
from core.visual_model import VisualObject


@dataclass
class Layer:
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "Video Layer"
    source_type: str = "video"
    source_id: str = ""
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blend_mode: str = "normal"
    position: tuple[float, float] = (0.5, 0.5)
    scale: tuple[float, float] = (1.0, 1.0)
    rotation: float = 0.0
    z_index: int = 0
    generator_type: str | None = None
    generator_settings: dict[str, Any] = field(default_factory=dict)
    performance_modifiers: list[dict[str, Any]] = field(default_factory=list)
    layer_effects: dict[str, Any] = field(default_factory=dict)
    fx_manual_override_until: float = 0.0
    overlay_manual_override_until: float = 0.0
    overlay_path: str | None = None
    overlay_kind: str | None = None
    overlay_in: float = 0.0
    overlay_out: float | None = None
    overlay_speed: float = 1.0
    overlay_frame_hold: int = 1
    overlay_loop: bool = True
    overlay_scene_sync: bool = False
    overlay_mask_mode: str = "none"
    overlay_mask_source: str = ""
    # Appended to preserve the positional constructor contract of older Layer callers.
    visual_object_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        self.visual_object_id = str(self.visual_object_id or uuid4().hex).strip()
        if not self.visual_object_id:
            self.visual_object_id = uuid4().hex
        self.opacity = min(1.0, max(0.0, float(self.opacity)))
        self.overlay_in = max(0.0, float(self.overlay_in))
        self.overlay_out = (
            None
            if self.overlay_out is None
            else max(self.overlay_in, float(self.overlay_out))
        )
        self.overlay_speed = max(0.1, min(4.0, float(self.overlay_speed)))
        self.overlay_frame_hold = max(1, min(24, int(self.overlay_frame_hold)))
        self.overlay_loop = bool(self.overlay_loop)
        if not isinstance(self.performance_modifiers, list):
            self.performance_modifiers = []
        self.performance_modifiers = [
            dict(item) for item in self.performance_modifiers if isinstance(item, dict)
        ]
        if self.overlay_mask_mode not in {"none", "alpha", "luma"}:
            self.overlay_mask_mode = "none"
        self.position = tuple(float(v) for v in self.position[:2])
        self.scale = tuple(max(0.001, float(v)) for v in self.scale[:2])
        if len(self.position) != 2 or len(self.scale) != 2:
            raise ValueError("Layer position and scale must contain two values.")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["position"] = list(self.position)
        data["scale"] = list(self.scale)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Layer:
        allowed = {
            "id",
            "visual_object_id",
            "name",
            "source_type",
            "source_id",
            "visible",
            "locked",
            "opacity",
            "blend_mode",
            "position",
            "scale",
            "rotation",
            "z_index",
            "generator_type",
            "generator_settings",
            "performance_modifiers",
            "layer_effects",
            "fx_manual_override_until",
            "overlay_manual_override_until",
            "overlay_path",
            "overlay_kind",
            "overlay_in",
            "overlay_out",
            "overlay_speed",
            "overlay_frame_hold",
            "overlay_loop",
            "overlay_scene_sync",
            "overlay_mask_mode",
            "overlay_mask_source",
        }
        values = {key: value for key, value in data.items() if key in allowed}
        if not isinstance(values.get("generator_settings", {}), dict):
            values["generator_settings"] = {}
        if not isinstance(values.get("layer_effects", {}), dict):
            values["layer_effects"] = {}
        if not isinstance(values.get("performance_modifiers", []), list):
            values["performance_modifiers"] = []
        layer = cls(**values)
        if not layer.visual_object_id or "visual_object_id" not in data:
            # A legacy layer ID is stable across loads, so its synthesized object
            # identity must also be stable until the project is next saved.
            layer.visual_object_id = uuid5(
                NAMESPACE_URL,
                f"eli_lab_av_translator:visual-object:{layer.id}",
            ).hex
        return layer


@dataclass
class Composition:
    name: str = "Untitled Composition"
    width: int = DEFAULT_CANVAS_WIDTH
    height: int = DEFAULT_CANVAS_HEIGHT
    fps: int = DEFAULT_FPS
    background: str = "#08090b"
    layers: list[Layer] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    visual_objects: dict[str, VisualObject] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Rebuild the registry through the same checks used by add_layer so
        # deserialized and directly constructed compositions share one invariant.
        initial_layers = list(self.layers)
        initial_objects = dict(self.visual_objects)
        self.layers = []
        self.visual_objects = {}
        for layer in initial_layers:
            visual_object = initial_objects.pop(layer.visual_object_id, None)
            if visual_object is not None and not isinstance(visual_object, VisualObject):
                visual_object = VisualObject.from_dict(visual_object)
            self.add_layer(
                layer,
                visual_object=visual_object,
                origin="legacy_import",
            )
        if initial_objects:
            orphaned = ", ".join(sorted(str(key) for key in initial_objects))
            raise ValueError(f"Composition contains visual objects without layers: {orphaned}")

    def _visual_object_for(
        self,
        layer: Layer,
        visual_object: VisualObject | None = None,
        *,
        origin: str = "layer_created",
    ) -> VisualObject:
        selected = visual_object or self.visual_objects.get(layer.visual_object_id)
        if selected is None:
            selected = VisualObject.from_layer(layer, origin=origin)
        selected.normalize()
        if selected.object_id != layer.visual_object_id:
            raise ValueError(
                "Layer visual_object_id must match its VisualObject object_id."
            )
        if selected.layer_id != layer.id:
            raise ValueError(
                "VisualObject layer_id must match the layer it represents."
            )
        return selected

    def add_layer(
        self,
        layer: Layer,
        visual_object: VisualObject | None = None,
        *,
        origin: str = "layer_created",
    ) -> None:
        if any(existing.id == layer.id for existing in self.layers):
            raise ValueError(f"Layer id already exists: {layer.id}")
        if layer.visual_object_id in self.visual_objects:
            raise ValueError(
                f"Visual object ID already exists: {layer.visual_object_id}"
            )
        selected = self._visual_object_for(layer, visual_object, origin=origin)
        self.layers.append(layer)
        self.visual_objects[selected.object_id] = selected
        self.sort_layers()

    def replace_layer(
        self,
        layer: Layer,
        visual_object: VisualObject | None = None,
    ) -> None:
        """Atomically replace a layer and its visual identity record."""
        index = next(
            (i for i, existing in enumerate(self.layers) if existing.id == layer.id),
            None,
        )
        if index is None:
            self.add_layer(layer, visual_object=visual_object)
            return

        previous = self.layers[index]
        previous_object = self.visual_objects.get(previous.visual_object_id)
        if visual_object is None and layer.visual_object_id == previous.visual_object_id:
            visual_object = previous_object

        # Stage all validation against a registry that excludes only the object
        # being replaced. Do not mutate the authoritative list or dictionary
        # until the candidate object is known to be valid.
        staged_registry = dict(self.visual_objects)
        staged_registry.pop(previous.visual_object_id, None)
        selected = self._visual_object_for(layer, visual_object)
        if selected.object_id in staged_registry:
            raise ValueError(
                f"Visual object ID already exists: {layer.visual_object_id}"
            )
        staged_registry[selected.object_id] = selected
        # Preserve the list object shared with runtime services such as
        # AutomationDirector while swapping the validated Layer entry.
        self.layers[index] = layer
        self.layers.sort(key=lambda item: item.z_index)
        self.visual_objects = staged_registry

    def remove_layer(self, layer_id: str) -> bool:
        layer = self.get_layer(layer_id)
        if layer is None:
            return False
        self.layers = [item for item in self.layers if item.id != layer_id]
        self.visual_objects.pop(layer.visual_object_id, None)
        return True

    def get_layer(self, layer_id: str) -> Layer | None:
        return next((layer for layer in self.layers if layer.id == layer_id), None)

    def get_visual_object(self, object_id: str) -> VisualObject | None:
        return self.visual_objects.get(str(object_id))

    def visual_object_for_layer(self, layer_id: str) -> VisualObject | None:
        layer = self.get_layer(layer_id)
        return self.visual_objects.get(layer.visual_object_id) if layer else None

    def sort_layers(self) -> None:
        self.layers.sort(key=lambda layer: layer.z_index)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "background": self.background,
            "layers": [layer.to_dict() for layer in self.layers],
            "metadata": self.metadata,
            "visual_objects": [
                self.visual_objects[key].to_dict()
                for key in sorted(self.visual_objects)
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Composition:
        raw_objects = data.get("visual_objects", [])
        visual_objects: dict[str, VisualObject] = {}
        if isinstance(raw_objects, dict):
            object_values = list(raw_objects.values())
        elif isinstance(raw_objects, list):
            object_values = raw_objects
        else:
            raise ValueError("Composition visual_objects must be a list or object.")
        for raw in object_values:
            item = VisualObject.from_dict(raw)
            if item.object_id in visual_objects:
                raise ValueError(f"Duplicate visual object ID: {item.object_id}")
            visual_objects[item.object_id] = item

        raw_layers = data.get("layers", [])
        if not isinstance(raw_layers, list):
            raise ValueError("Composition layers must be a list.")
        metadata = data.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        return cls(
            name=str(data.get("name", "Untitled Composition")),
            width=int(data.get("width", DEFAULT_CANVAS_WIDTH)),
            height=int(data.get("height", DEFAULT_CANVAS_HEIGHT)),
            fps=int(data.get("fps", DEFAULT_FPS)),
            background=str(data.get("background", "#08090b")),
            layers=[Layer.from_dict(item) for item in raw_layers],
            metadata=dict(metadata),
            visual_objects=visual_objects,
        )
