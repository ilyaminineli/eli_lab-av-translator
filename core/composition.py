from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

from config import DEFAULT_CANVAS_HEIGHT, DEFAULT_CANVAS_WIDTH, DEFAULT_FPS
from core.visual_grammar import (
    MAX_MOTION_GRAMMAR_ENTRIES,
    MotionGesture,
    VisualPattern,
)
from core.visual_model import VisualMotif, VisualObject


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
    # Appended to preserve the positional Composition constructor contract.
    visual_motifs: dict[str, VisualMotif] = field(default_factory=dict)
    motion_gestures: dict[str, MotionGesture] = field(default_factory=dict)
    visual_patterns: dict[str, VisualPattern] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Rebuild the registry through the same checks used by add_layer so
        # deserialized and directly constructed compositions share one invariant.
        initial_layers = list(self.layers)
        initial_objects = dict(self.visual_objects)
        initial_motifs = dict(self.visual_motifs)
        initial_gestures = dict(self.motion_gestures)
        initial_patterns = dict(self.visual_patterns)
        self.layers = []
        self.visual_objects = {}
        self.visual_motifs = {}
        self.motion_gestures = {}
        self.visual_patterns = {}
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
        for registry_key, raw_motif in initial_motifs.items():
            motif = (
                raw_motif
                if isinstance(raw_motif, VisualMotif)
                else VisualMotif.from_dict(raw_motif)
            )
            if str(registry_key) != motif.motif_id:
                raise ValueError(
                    "Visual motif registry keys must match their motif IDs."
                )
            self.add_visual_motif(motif)

        for registry_key, raw_gesture in initial_gestures.items():
            gesture = (
                raw_gesture
                if isinstance(raw_gesture, MotionGesture)
                else MotionGesture.from_dict(raw_gesture)
            )
            if str(registry_key) != gesture.gesture_id:
                raise ValueError(
                    "Motion gesture registry keys must match their gesture IDs."
                )
            self.add_motion_gesture(gesture)
        for registry_key, raw_pattern in initial_patterns.items():
            pattern = (
                raw_pattern
                if isinstance(raw_pattern, VisualPattern)
                else VisualPattern.from_dict(raw_pattern)
            )
            if str(registry_key) != pattern.pattern_id:
                raise ValueError(
                    "Visual pattern registry keys must match their pattern IDs."
                )
            self.add_visual_pattern(pattern)

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
        self.layers[:] = [item for item in self.layers if item.id != layer_id]
        self.visual_objects.pop(layer.visual_object_id, None)
        return True

    def get_visual_motif(self, motif_id: str) -> VisualMotif | None:
        return self.visual_motifs.get(str(motif_id))

    def add_visual_motif(self, motif: VisualMotif) -> None:
        """Register one authored motif without changing its object realizations."""
        if not isinstance(motif, VisualMotif):
            raise TypeError("Composition motifs must be VisualMotif instances.")
        motif.normalize()
        if motif.motif_id in self.visual_motifs:
            raise ValueError(f"Visual motif ID already exists: {motif.motif_id}")
        self.visual_motifs[motif.motif_id] = motif

    def remove_visual_motif(self, motif_id: str) -> bool:
        """Remove an unused motif; object references must be explicitly rebound first."""
        selected_id = str(motif_id)
        if selected_id not in self.visual_motifs:
            return False
        if any(
            item.lineage.motif_id == selected_id
            for item in self.visual_objects.values()
        ):
            raise ValueError(
                f"Visual motif {selected_id!r} is still referenced by visual objects."
            )
        self.visual_motifs.pop(selected_id)
        return True

    def get_visual_objects_for_motif(self, motif_id: str) -> list[VisualObject]:
        """Return motif realizations in layer order, including unresolved references."""
        selected_id = str(motif_id)
        return [
            self.visual_objects[layer.visual_object_id]
            for layer in self.layers
            if layer.visual_object_id in self.visual_objects
            and self.visual_objects[layer.visual_object_id].lineage.motif_id
            == selected_id
        ]

    def bind_visual_object_to_motif(
        self,
        object_id: str,
        motif_id: str,
    ) -> VisualObject:
        """Explicitly attach an unbound object to a registered authored motif.

        This is a semantic relationship operation, not a transform of the renderable
        layer. It stages a complete object before committing only lineage and revision.
        """
        visual_object = self.get_visual_object(object_id)
        if visual_object is None:
            raise KeyError(f"Unknown visual object: {object_id}")
        selected_motif_id = str(motif_id).strip()
        if not selected_motif_id or selected_motif_id not in self.visual_motifs:
            raise ValueError(
                f"Cannot bind to unknown visual motif: {selected_motif_id!r}"
            )
        if visual_object.lineage.motif_id == selected_motif_id:
            return visual_object
        if visual_object.lineage.motif_id is not None:
            raise ValueError(
                f"Visual object {visual_object.object_id!r} already references "
                f"motif {visual_object.lineage.motif_id!r}; unbind it explicitly first."
            )
        visual_object.mutation_contract.validate(
            "bind_motif",
            {"lineage.motif_id"},
        )

        candidate = VisualObject.from_dict(visual_object.to_dict())
        candidate.lineage.motif_id = selected_motif_id
        candidate.revision += 1
        candidate.normalize()

        visual_object.lineage = candidate.lineage
        visual_object.revision = candidate.revision
        return visual_object

    def unbind_visual_object_from_motif(self, object_id: str) -> bool:
        """Explicitly clear a resolved or historical motif reference."""
        visual_object = self.get_visual_object(object_id)
        if visual_object is None:
            raise KeyError(f"Unknown visual object: {object_id}")
        if visual_object.lineage.motif_id is None:
            return False
        visual_object.mutation_contract.validate(
            "unbind_motif",
            {"lineage.motif_id"},
        )

        candidate = VisualObject.from_dict(visual_object.to_dict())
        candidate.lineage.motif_id = None
        candidate.revision += 1
        candidate.normalize()

        visual_object.lineage = candidate.lineage
        visual_object.revision = candidate.revision
        return True

    def get_motion_gesture(self, gesture_id: str) -> MotionGesture | None:
        return self.motion_gestures.get(str(gesture_id))

    def add_motion_gesture(self, gesture: MotionGesture) -> None:
        """Register one reusable renderer-independent motion gesture."""
        if not isinstance(gesture, MotionGesture):
            raise TypeError("Composition gestures must be MotionGesture instances.")
        gesture.normalize()
        if gesture.gesture_id in self.motion_gestures:
            raise ValueError(
                f"Motion gesture ID already exists: {gesture.gesture_id}"
            )
        if len(self.motion_gestures) >= MAX_MOTION_GRAMMAR_ENTRIES:
            raise ValueError(
                f"Composition cannot contain more than "
                f"{MAX_MOTION_GRAMMAR_ENTRIES} motion gestures."
            )
        self.motion_gestures[gesture.gesture_id] = gesture

    def remove_motion_gesture(self, gesture_id: str) -> bool:
        """Remove an unused gesture; referenced pattern steps must be edited first."""
        selected_id = str(gesture_id)
        if selected_id not in self.motion_gestures:
            return False
        if any(
            step.gesture_id == selected_id
            for pattern in self.visual_patterns.values()
            for step in pattern.steps
        ):
            raise ValueError(
                f"Motion gesture {selected_id!r} is still referenced by visual patterns."
            )
        self.motion_gestures.pop(selected_id)
        return True

    def get_visual_pattern(self, pattern_id: str) -> VisualPattern | None:
        return self.visual_patterns.get(str(pattern_id))

    def add_visual_pattern(self, pattern: VisualPattern) -> None:
        """Register a bounded cycle whose steps reference existing gestures."""
        if not isinstance(pattern, VisualPattern):
            raise TypeError("Composition patterns must be VisualPattern instances.")
        pattern.normalize()
        if pattern.pattern_id in self.visual_patterns:
            raise ValueError(f"Visual pattern ID already exists: {pattern.pattern_id}")
        if len(self.visual_patterns) >= MAX_MOTION_GRAMMAR_ENTRIES:
            raise ValueError(
                f"Composition cannot contain more than "
                f"{MAX_MOTION_GRAMMAR_ENTRIES} visual patterns."
            )
        missing = sorted(
            {
                step.gesture_id
                for step in pattern.steps
                if step.gesture_id not in self.motion_gestures
            }
        )
        if missing:
            raise ValueError(
                "Visual pattern references unknown motion gestures: "
                + ", ".join(missing)
            )
        self.visual_patterns[pattern.pattern_id] = pattern

    def remove_visual_pattern(self, pattern_id: str) -> bool:
        return self.visual_patterns.pop(str(pattern_id), None) is not None

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
            "visual_motifs": [
                self.visual_motifs[key].to_dict()
                for key in sorted(self.visual_motifs)
            ],
            "motion_gestures": [
                self.motion_gestures[key].to_dict()
                for key in sorted(self.motion_gestures)
            ],
            "visual_patterns": [
                self.visual_patterns[key].to_dict()
                for key in sorted(self.visual_patterns)
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
        raw_motifs = data.get("visual_motifs", [])
        visual_motifs: dict[str, VisualMotif] = {}
        if isinstance(raw_motifs, dict):
            motif_values = list(raw_motifs.items())
        elif isinstance(raw_motifs, list):
            motif_values = [(None, item) for item in raw_motifs]
        else:
            raise ValueError("Composition visual_motifs must be a list or object.")
        for registry_key, raw_motif in motif_values:
            item = VisualMotif.from_dict(raw_motif)
            if registry_key is not None and str(registry_key) != item.motif_id:
                raise ValueError(
                    "Visual motif registry keys must match their motif IDs."
                )
            if item.motif_id in visual_motifs:
                raise ValueError(f"Duplicate visual motif ID: {item.motif_id}")
            visual_motifs[item.motif_id] = item
        raw_gestures = data.get("motion_gestures", [])
        if isinstance(raw_gestures, dict):
            gesture_values = list(raw_gestures.items())
        elif isinstance(raw_gestures, list):
            gesture_values = [(None, item) for item in raw_gestures]
        else:
            raise ValueError("Composition motion_gestures must be a list or object.")
        motion_gestures: dict[str, MotionGesture] = {}
        for registry_key, raw_gesture in gesture_values:
            gesture = MotionGesture.from_dict(raw_gesture)
            if registry_key is not None and str(registry_key) != gesture.gesture_id:
                raise ValueError(
                    "Motion gesture registry keys must match their gesture IDs."
                )
            if gesture.gesture_id in motion_gestures:
                raise ValueError(f"Duplicate motion gesture ID: {gesture.gesture_id}")
            motion_gestures[gesture.gesture_id] = gesture

        raw_patterns = data.get("visual_patterns", [])
        if isinstance(raw_patterns, dict):
            pattern_values = list(raw_patterns.items())
        elif isinstance(raw_patterns, list):
            pattern_values = [(None, item) for item in raw_patterns]
        else:
            raise ValueError("Composition visual_patterns must be a list or object.")
        visual_patterns: dict[str, VisualPattern] = {}
        for registry_key, raw_pattern in pattern_values:
            pattern = VisualPattern.from_dict(raw_pattern)
            if registry_key is not None and str(registry_key) != pattern.pattern_id:
                raise ValueError(
                    "Visual pattern registry keys must match their pattern IDs."
                )
            if pattern.pattern_id in visual_patterns:
                raise ValueError(f"Duplicate visual pattern ID: {pattern.pattern_id}")
            visual_patterns[pattern.pattern_id] = pattern
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
            visual_motifs=visual_motifs,
            motion_gestures=motion_gestures,
            visual_patterns=visual_patterns,
        )
