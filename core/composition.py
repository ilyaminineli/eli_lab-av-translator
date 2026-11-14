from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

from config import DEFAULT_CANVAS_HEIGHT, DEFAULT_CANVAS_WIDTH, DEFAULT_FPS


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

    def __post_init__(self) -> None:
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
        return cls(**values)


@dataclass
class Composition:
    name: str = "Untitled Composition"
    width: int = DEFAULT_CANVAS_WIDTH
    height: int = DEFAULT_CANVAS_HEIGHT
    fps: int = DEFAULT_FPS
    background: str = "#08090b"
    layers: list[Layer] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_layer(self, layer: Layer) -> None:
        if any(existing.id == layer.id for existing in self.layers):
            raise ValueError(f"Layer id already exists: {layer.id}")
        self.layers.append(layer)
        self.sort_layers()

    def remove_layer(self, layer_id: str) -> bool:
        original_count = len(self.layers)
        self.layers = [layer for layer in self.layers if layer.id != layer_id]
        return len(self.layers) != original_count

    def get_layer(self, layer_id: str) -> Layer | None:
        return next((layer for layer in self.layers if layer.id == layer_id), None)

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
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Composition:
        composition = cls(
            name=str(data.get("name", "Untitled Composition")),
            width=int(data.get("width", DEFAULT_CANVAS_WIDTH)),
            height=int(data.get("height", DEFAULT_CANVAS_HEIGHT)),
            fps=int(data.get("fps", DEFAULT_FPS)),
            background=str(data.get("background", "#08090b")),
            layers=[Layer.from_dict(item) for item in data.get("layers", [])],
            metadata=dict(data.get("metadata", {})),
        )
        composition.sort_layers()
        return composition
