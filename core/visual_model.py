from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any
from uuid import uuid4

VISUAL_MODEL_SCHEMA_VERSION = 1

VISUAL_ROLES = frozenset(
    {
        "foreground_anchor",
        "foreground_accent",
        "foreground_motif",
        "midground_motion",
        "midground_structure",
        "background_environment",
        "background_memory",
        "transition_material",
        "spatial_boundary",
        "latent_object",
        "negative_space",
        "unassigned",
    }
)

VISUAL_MOTIF_SCHEMA_VERSION = 1

VISUAL_MOTIF_FAMILIES = frozenset(
    {
        "contour",
        "motion",
        "spatial",
        "texture",
        "typographic",
        "colour",
        "framing",
        "transformation",
        "absence",
        "composite",
    }
)

VISUAL_EVENT_TYPES = frozenset(
    {
        "spawn",
        "remove",
        "reveal",
        "conceal",
        "move",
        "morph",
        "fracture",
        "assemble",
        "rotate",
        "pulse",
        "freeze",
        "resume",
        "fade",
        "cut",
        "mask",
        "displace",
        "change_material",
        "change_palette",
        "change_camera",
        "change_scene",
        "hold",
        "reset",
    }
)

VISUAL_TIME_DOMAINS = frozenset(
    {
        "immediate",
        "performance_seconds",
        "bar_beat",
    }
)


def _identifier(value: object, label: str, *, optional: bool = False) -> str:
    result = str(value or "").strip()
    if not result and not optional:
        raise ValueError(f"{label} cannot be empty.")
    if len(result) > 128:
        raise ValueError(f"{label} must be at most 128 characters.")
    return result


def _string_list(values: object, label: str) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise ValueError(f"{label} must be a list.")
    result: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = str(raw).strip()
        if not value or len(value) > 64:
            raise ValueError(f"{label} entries must contain 1–64 characters.")
        if value not in seen:
            result.append(value)
            seen.add(value)
        if len(result) > 64:
            raise ValueError(f"{label} cannot contain more than 64 entries.")
    return result

def _visual_motif_scalar(
    value: object,
    label: str,
) -> str | int | float | bool:
    """Normalize one bounded, JSON-safe authored motif scalar."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value < -1_000_000_000 or value > 1_000_000_000:
            raise ValueError(f"{label} must be within ±1,000,000,000.")
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or value < -1_000_000_000 or value > 1_000_000_000:
            raise ValueError(f"{label} must be finite and within ±1,000,000,000.")
        return value
    if isinstance(value, str) and len(value) <= 128:
        return value
    raise ValueError(
        f"{label} must be a finite bounded number, boolean or string "
        "of at most 128 characters."
    )



@dataclass
class VisualIdentity:
    """Recognisable visual traits, independent of a layer's current parameters."""

    geometry_signature: str = ""
    palette_identity: str = ""
    motion_identity: str = ""
    material_identity: str = ""
    traits: dict[str, str] = field(default_factory=dict)

    def normalize(self) -> None:
        for name in (
            "geometry_signature",
            "palette_identity",
            "motion_identity",
            "material_identity",
        ):
            value = str(getattr(self, name)).strip()
            if len(value) > 128:
                raise ValueError(f"Visual identity field {name!r} is too long.")
            setattr(self, name, value)
        if not isinstance(self.traits, dict):
            raise ValueError("Visual identity traits must be an object.")
        clean: dict[str, str] = {}
        for raw_key, raw_value in self.traits.items():
            key, value = str(raw_key).strip(), str(raw_value).strip()
            if not key or len(key) > 64 or len(value) > 128:
                raise ValueError("Visual identity traits contain an invalid entry.")
            clean[key] = value
            if len(clean) > 64:
                raise ValueError("Visual identity cannot contain more than 64 traits.")
        self.traits = clean

    @classmethod
    def from_dict(cls, data: object) -> VisualIdentity:
        if not isinstance(data, dict):
            raise ValueError("Visual identity must be an object.")
        allowed = set(cls.__dataclass_fields__)
        result = cls(**{key: value for key, value in data.items() if key in allowed})
        result.normalize()
        return result


@dataclass
class VisualLineage:
    """Provenance linking an object to earlier objects or a recurring motif."""

    parent_object_id: str | None = None
    motif_id: str | None = None
    origin: str = "layer_created"
    source_object_ids: list[str] = field(default_factory=list)

    def normalize(self) -> None:
        self.parent_object_id = (
            _identifier(self.parent_object_id, "Parent visual object ID", optional=True)
            or None
        )
        self.motif_id = (
            _identifier(self.motif_id, "Visual motif ID", optional=True) or None
        )
        self.origin = str(self.origin).strip() or "layer_created"
        if len(self.origin) > 64:
            raise ValueError("Visual lineage origin must be at most 64 characters.")
        self.source_object_ids = _string_list(
            self.source_object_ids, "Visual lineage source IDs"
        )

    @classmethod
    def from_dict(cls, data: object) -> VisualLineage:
        if not isinstance(data, dict):
            raise ValueError("Visual lineage must be an object.")
        allowed = set(cls.__dataclass_fields__)
        result = cls(**{key: value for key, value in data.items() if key in allowed})
        result.normalize()
        return result


@dataclass
class VisualMutationContract:
    """Declares which visual properties a transformation may change."""

    preserve: list[str] = field(
        default_factory=lambda: [
            "object_id",
            "layer_id",
            "role",
            "identity",
            "lineage",
        ]
    )
    allow: list[str] = field(
        default_factory=lambda: [
            "position",
            "scale",
            "rotation",
            "opacity",
            "material",
            "palette",
            "motion",
            "blend_mode",
            "visibility",
            "visible",
            "z_index",
            "locked",
            "generator_settings",
            "layer_effects",
            "overlay_speed",
            "overlay_frame_hold",
        ]
    )
    forbid: list[str] = field(
        default_factory=lambda: [
            "replace_source",
            "reset_identity",
            "delete",
        ]
    )

    def normalize(self) -> None:
        self.preserve = _string_list(self.preserve, "Mutation preserve fields")
        self.allow = _string_list(self.allow, "Mutation allow fields")
        self.forbid = _string_list(self.forbid, "Mutation forbidden operations")
        overlap = set(self.preserve) & set(self.allow)
        if overlap:
            raise ValueError(
                "Mutation contract cannot both preserve and allow: "
                + ", ".join(sorted(overlap))
            )

    def validate(
        self,
        operation: str,
        changed_properties: set[str] | list[str] | tuple[str, ...],
    ) -> None:
        """Raise when an operation violates the declared mutation boundary."""
        self.normalize()
        selected_operation = _identifier(operation, "Mutation operation")
        changed = {str(value).strip() for value in changed_properties}
        if selected_operation in self.forbid:
            raise ValueError(f"Mutation operation {selected_operation!r} is forbidden.")
        protected = changed & set(self.preserve)
        if protected:
            raise ValueError(
                "Mutation would alter preserved identity fields: "
                + ", ".join(sorted(protected))
            )
        unsupported = changed - set(self.allow)
        if unsupported:
            raise ValueError(
                "Mutation changes properties not allowed by the contract: "
                + ", ".join(sorted(unsupported))
            )

    @classmethod
    def from_dict(cls, data: object) -> VisualMutationContract:
        if not isinstance(data, dict):
            raise ValueError("Visual mutation contract must be an object.")
        allowed = set(cls.__dataclass_fields__)
        result = cls(**{key: value for key, value in data.items() if key in allowed})
        # Early C0 releases serialized two default allow-list shapes. Expand
        # only those exact historical defaults; custom restrictive lists remain
        # untouched.
        legacy_default_allow = {
            "position",
            "scale",
            "rotation",
            "opacity",
            "material",
            "palette",
            "motion",
            "blend_mode",
            "visibility",
        }
        intermediate_default_allow = legacy_default_allow | {
            "visible",
            "z_index",
            "locked",
        }
        selected_allow = set(result.allow)
        if selected_allow == legacy_default_allow:
            result.allow.extend(
                (
                    "visible",
                    "z_index",
                    "locked",
                    "generator_settings",
                    "layer_effects",
                    "overlay_speed",
                    "overlay_frame_hold",
                )
            )
        elif selected_allow == intermediate_default_allow:
            result.allow.extend(
                (
                    "generator_settings",
                    "layer_effects",
                    "overlay_speed",
                    "overlay_frame_hold",
                )
            )
        result.normalize()
        return result


@dataclass
class VisualMotif:
    """Authored visual identity that can have multiple object realizations."""

    motif_id: str = field(default_factory=lambda: uuid4().hex)
    name: str = "Untitled Motif"
    family: str = "contour"
    identity: VisualIdentity = field(default_factory=VisualIdentity)
    parameters: dict[str, str | int | float | bool] = field(default_factory=dict)
    description: str = ""
    revision: int = 0
    invariants: dict[str, str | int | float | bool] = field(default_factory=dict)
    allowed_variations: list[str] = field(default_factory=list)
    seed: int | None = None

    def normalize(self) -> None:
        self.motif_id = _identifier(self.motif_id, "Visual motif ID")
        self.name = str(self.name).strip()
        if not self.name or len(self.name) > 128:
            raise ValueError("Visual motif name must contain 1–128 characters.")
        self.family = str(self.family).strip()
        if self.family not in VISUAL_MOTIF_FAMILIES:
            raise ValueError(
                f"Unsupported visual motif family: {self.family!r}"
            )
        if isinstance(self.identity, dict):
            self.identity = VisualIdentity.from_dict(self.identity)
        if not isinstance(self.identity, VisualIdentity):
            raise ValueError("Visual motif identity must be a VisualIdentity.")
        self.identity.normalize()
        if not isinstance(self.parameters, dict):
            raise ValueError("Visual motif parameters must be an object.")
        if len(self.parameters) > 64:
            raise ValueError("Visual motif cannot contain more than 64 parameters.")
        clean_parameters: dict[str, str | int | float | bool] = {}
        for raw_key, raw_value in self.parameters.items():
            key = str(raw_key).strip()
            if not key or len(key) > 64:
                raise ValueError("Visual motif parameter names must contain 1–64 characters.")
            if key in clean_parameters:
                raise ValueError(f"Duplicate visual motif parameter: {key}")
            clean_parameters[key] = _visual_motif_scalar(
                raw_value,
                f"Visual motif parameter {key!r}",
            )
        self.parameters = clean_parameters

        available_values: dict[str, str | int | float | bool] = {
            "identity.geometry_signature": self.identity.geometry_signature,
            "identity.palette_identity": self.identity.palette_identity,
            "identity.motion_identity": self.identity.motion_identity,
            "identity.material_identity": self.identity.material_identity,
        }
        available_values.update(
            {
                f"identity.traits.{key}": value
                for key, value in self.identity.traits.items()
            }
        )
        available_values.update(
            {
                f"parameters.{key}": value
                for key, value in self.parameters.items()
            }
        )

        if not isinstance(self.invariants, dict):
            raise ValueError("Visual motif invariants must be an object.")
        if len(self.invariants) > 64:
            raise ValueError("Visual motif cannot contain more than 64 invariants.")
        clean_invariants: dict[str, str | int | float | bool] = {}
        for raw_path, raw_expected in self.invariants.items():
            path = str(raw_path).strip()
            if not path or len(path) > 128:
                raise ValueError("Visual motif invariant paths must contain 1–128 characters.")
            if path not in available_values:
                raise ValueError(
                    f"Visual motif invariant {path!r} does not reference an authored field."
                )
            if path in clean_invariants:
                raise ValueError(f"Duplicate visual motif invariant path: {path}")
            expected = _visual_motif_scalar(
                raw_expected,
                f"Visual motif invariant {path!r}",
            )
            current = available_values[path]
            same_scalar_type = (
                isinstance(expected, bool) and isinstance(current, bool)
                or isinstance(expected, int)
                and not isinstance(expected, bool)
                and isinstance(current, int)
                and not isinstance(current, bool)
                or isinstance(expected, float) and isinstance(current, float)
                or isinstance(expected, str) and isinstance(current, str)
            )
            if not same_scalar_type or expected != current:
                raise ValueError(
                    f"Visual motif invariant {path!r} must match its authored value."
                )
            clean_invariants[path] = expected
        self.invariants = clean_invariants

        if not isinstance(self.allowed_variations, (list, tuple)):
            raise ValueError("Visual motif allowed_variations must be a list.")
        if len(self.allowed_variations) > 64:
            raise ValueError("Visual motif cannot contain more than 64 allowed variations.")
        clean_variations: list[str] = []
        seen_variations: set[str] = set()
        for raw_path in self.allowed_variations:
            path = str(raw_path).strip()
            if not path or len(path) > 128:
                raise ValueError(
                    "Visual motif variation paths must contain 1–128 characters."
                )
            if path in seen_variations:
                raise ValueError(f"Duplicate visual motif variation path: {path}")
            if path not in available_values:
                raise ValueError(
                    f"Visual motif variation {path!r} does not reference an authored field."
                )
            if path in clean_invariants:
                raise ValueError(
                    f"Visual motif field {path!r} cannot be both invariant and variable."
                )
            clean_variations.append(path)
            seen_variations.add(path)
        self.allowed_variations = clean_variations

        self.description = str(self.description).strip()
        if len(self.description) > 512:
            raise ValueError("Visual motif description must be at most 512 characters.")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int):
            raise ValueError("Visual motif revision must be an integer.")
        if self.revision < 0:
            raise ValueError("Visual motif revision cannot be negative.")
        if self.seed is not None and (
            isinstance(self.seed, bool)
            or not isinstance(self.seed, int)
            or self.seed < 0
            or self.seed > 18_446_744_073_709_551_615
        ):
            raise ValueError("Visual motif seed must be an unsigned 64-bit integer.")

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {
            "schema_version": VISUAL_MOTIF_SCHEMA_VERSION,
            **asdict(self),
        }

    @classmethod
    def from_dict(cls, data: object) -> VisualMotif:
        if not isinstance(data, dict):
            raise ValueError("Visual motif must be an object.")
        version = int(data.get("schema_version", VISUAL_MOTIF_SCHEMA_VERSION))
        if version > VISUAL_MOTIF_SCHEMA_VERSION:
            raise ValueError(
                f"Visual motif schema {version} is newer than supported schema "
                f"{VISUAL_MOTIF_SCHEMA_VERSION}."
            )
        allowed = set(cls.__dataclass_fields__)
        values = {key: value for key, value in data.items() if key in allowed}
        if isinstance(values.get("identity"), dict):
            values["identity"] = VisualIdentity.from_dict(values["identity"])
        result = cls(**values)
        result.normalize()
        return result


@dataclass
class VisualObject:
    """Renderer-independent identity associated with one renderable composition layer."""

    object_id: str = field(default_factory=lambda: uuid4().hex)
    layer_id: str = ""
    role: str = "unassigned"
    material: str = "unspecified"
    identity: VisualIdentity = field(default_factory=VisualIdentity)
    lineage: VisualLineage = field(default_factory=VisualLineage)
    mutation_contract: VisualMutationContract = field(default_factory=VisualMutationContract)
    revision: int = 0

    def normalize(self) -> None:
        self.object_id = _identifier(self.object_id, "Visual object ID")
        self.layer_id = _identifier(self.layer_id, "Visual object layer ID")
        self.role = str(self.role).strip() or "unassigned"
        self.material = str(self.material).strip() or "unspecified"
        if len(self.role) > 64 or len(self.material) > 128:
            raise ValueError("Visual object role or material is too long.")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int):
            raise ValueError("Visual object revision must be an integer.")
        if self.revision < 0:
            raise ValueError("Visual object revision cannot be negative.")
        if isinstance(self.identity, dict):
            self.identity = VisualIdentity.from_dict(self.identity)
        self.identity.normalize()
        if isinstance(self.lineage, dict):
            self.lineage = VisualLineage.from_dict(self.lineage)
        self.lineage.normalize()
        if self.lineage.parent_object_id == self.object_id:
            raise ValueError("A visual object cannot be its own parent.")
        if isinstance(self.mutation_contract, dict):
            self.mutation_contract = VisualMutationContract.from_dict(
                self.mutation_contract
            )
        self.mutation_contract.normalize()

    @classmethod
    def from_layer(cls, layer: object, *, origin: str = "layer_created") -> VisualObject:
        source_type = str(getattr(layer, "source_type", "unknown"))
        generator_type = str(getattr(layer, "generator_type", "") or "")
        material_by_source = {
            "video": "moving_image",
            "overlay": "image_or_video",
            "generator": "procedural",
        }
        result = cls(
            object_id=str(getattr(layer, "visual_object_id", "") or uuid4().hex),
            layer_id=str(getattr(layer, "id", "")),
            material=material_by_source.get(source_type, source_type or "unspecified"),
            identity=VisualIdentity(
                geometry_signature=generator_type or source_type,
                material_identity=source_type,
            ),
            lineage=VisualLineage(origin=origin),
        )
        result.normalize()
        return result

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {
            "schema_version": VISUAL_MODEL_SCHEMA_VERSION,
            **asdict(self),
        }

    @classmethod
    def from_dict(cls, data: object) -> VisualObject:
        if not isinstance(data, dict):
            raise ValueError("Visual object must be an object.")
        version = int(data.get("schema_version", VISUAL_MODEL_SCHEMA_VERSION))
        if version > VISUAL_MODEL_SCHEMA_VERSION:
            raise ValueError(
                f"Visual object schema {version} is newer than supported schema "
                f"{VISUAL_MODEL_SCHEMA_VERSION}."
            )
        allowed = set(cls.__dataclass_fields__)
        values = {key: value for key, value in data.items() if key in allowed}
        if isinstance(values.get("identity"), dict):
            values["identity"] = VisualIdentity.from_dict(values["identity"])
        if isinstance(values.get("lineage"), dict):
            values["lineage"] = VisualLineage.from_dict(values["lineage"])
        if isinstance(values.get("mutation_contract"), dict):
            values["mutation_contract"] = VisualMutationContract.from_dict(
                values["mutation_contract"]
            )
        result = cls(**values)
        result.normalize()
        return result


@dataclass
class VisualEvent:
    """Renderer-independent visual event with an explicit time domain."""

    event_type: str
    object_id: str | None = None
    time_domain: str = "immediate"
    position: dict[str, int | float] = field(default_factory=dict)
    payload: dict[str, Any] = field(default_factory=dict)
    source_id: str = "manual"
    sequence: int | None = None
    event_id: str = field(default_factory=lambda: uuid4().hex)

    def normalize(self) -> None:
        self.event_id = _identifier(self.event_id, "Visual event ID")
        self.object_id = (
            _identifier(self.object_id, "Visual event object ID", optional=True) or None
        )
        self.source_id = _identifier(self.source_id, "Visual event source ID")
        self.event_type = str(self.event_type).strip()
        self.time_domain = str(self.time_domain).strip()
        if self.event_type not in VISUAL_EVENT_TYPES:
            raise ValueError(f"Unsupported visual event type: {self.event_type!r}")
        if self.time_domain not in VISUAL_TIME_DOMAINS:
            raise ValueError(f"Unsupported visual time domain: {self.time_domain!r}")
        if not isinstance(self.position, dict):
            raise ValueError("Visual event position must be an object.")
        if self.time_domain == "immediate":
            if self.position:
                raise ValueError("Immediate visual events must not have a scheduled position.")
        elif self.time_domain == "performance_seconds":
            seconds = self.position.get("seconds")
            if (
                isinstance(seconds, bool)
                or not isinstance(seconds, (int, float))
                or not math.isfinite(float(seconds))
                or float(seconds) < 0.0
                or set(self.position) != {"seconds"}
            ):
                raise ValueError("Performance-time events require non-negative seconds.")
            self.position = {"seconds": float(seconds)}
        else:
            bar, beat = self.position.get("bar"), self.position.get("beat")
            if (
                isinstance(bar, bool)
                or not isinstance(bar, int)
                or bar < 1
                or isinstance(beat, bool)
                or not isinstance(beat, (int, float))
                or not math.isfinite(float(beat))
                or float(beat) < 1.0
                or set(self.position) != {"bar", "beat"}
            ):
                raise ValueError("Bar/beat events require a positive bar and beat.")
            self.position = {"bar": bar, "beat": float(beat)}
        if not isinstance(self.payload, dict):
            raise ValueError("Visual event payload must be an object.")
        if self.sequence is not None:
            if isinstance(self.sequence, bool) or not isinstance(self.sequence, int):
                raise ValueError("Visual event sequence must be an integer.")
            if self.sequence < 0:
                raise ValueError("Visual event sequence cannot be negative.")

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return asdict(self)

    @classmethod
    def from_dict(cls, data: object) -> VisualEvent:
        if not isinstance(data, dict):
            raise ValueError("Visual event must be an object.")
        allowed = set(cls.__dataclass_fields__)
        result = cls(**{key: value for key, value in data.items() if key in allowed})
        result.normalize()
        return result
