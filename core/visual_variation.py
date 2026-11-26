from __future__ import annotations

import hashlib
import json
import math
import random
from dataclasses import asdict, dataclass, field
from typing import Any

from core.visual_grammar import MAX_SEED, VisualPattern
from core.visual_model import VisualMotif

VISUAL_VARIATION_RULE_SCHEMA_VERSION = 1
VISUAL_MOTIF_VARIATION_SCHEMA_VERSION = 1
MAX_VISUAL_VARIATION_RULES = 64
MAX_VISUAL_VARIATION_CHOICES = 32
MAX_VARIATION_FIELD_VALUE = 1_000_000_000


def _identifier(value: object, label: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{label} cannot be empty.")
    if len(result) > 128:
        raise ValueError(f"{label} must be at most 128 characters.")
    return result


def _revision(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer.")
    return value


def _seed(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= MAX_SEED:
        raise ValueError(f"{label} must be an unsigned 64-bit integer.")
    return value


def _scalar(value: object, label: str) -> str | int | float | bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if not -MAX_VARIATION_FIELD_VALUE <= value <= MAX_VARIATION_FIELD_VALUE:
            raise ValueError(f"{label} must be within ±1,000,000,000.")
        return value
    if isinstance(value, float):
        if not math.isfinite(value) or not -MAX_VARIATION_FIELD_VALUE <= value <= MAX_VARIATION_FIELD_VALUE:
            raise ValueError(f"{label} must be finite and within ±1,000,000,000.")
        return value
    if isinstance(value, str) and len(value) <= 128:
        return value
    raise ValueError(f"{label} must be a bounded scalar string, number or boolean.")


def _motif_value(motif: VisualMotif, path: str) -> str | int | float | bool:
    fields = {
        "identity.geometry_signature": motif.identity.geometry_signature,
        "identity.palette_identity": motif.identity.palette_identity,
        "identity.motion_identity": motif.identity.motion_identity,
        "identity.material_identity": motif.identity.material_identity,
    }
    if path in fields:
        return fields[path]
    if path.startswith("identity.traits."):
        key = path.removeprefix("identity.traits.")
        if key in motif.identity.traits:
            return motif.identity.traits[key]
    if path.startswith("parameters."):
        key = path.removeprefix("parameters.")
        if key in motif.parameters:
            return motif.parameters[key]
    raise ValueError(f"Visual variation path does not exist: {path!r}")


@dataclass
class VisualVariationRule:
    """Explicit constraints for varying one authored motif field."""

    path: str = ""
    mode: str = "uniform"
    minimum: int | float | None = None
    maximum: int | float | None = None
    value_type: str | None = None
    choices: list[str | int | float | bool] = field(default_factory=list)

    def normalize(self) -> None:
        self.path = _identifier(self.path, "Visual variation path")
        if not isinstance(self.choices, list):
            raise ValueError("Visual variation choices must be a list.")
        if self.mode not in {"uniform", "choice"}:
            raise ValueError(f"Unsupported visual variation rule mode: {self.mode!r}.")
        if self.mode == "uniform":
            if self.choices:
                raise ValueError("Uniform visual variation rules cannot contain choices.")
            if self.value_type not in {"integer", "number"}:
                raise ValueError(
                    "Uniform visual variation requires value_type 'integer' or 'number'."
                )
            bounds: list[float] = []
            for label, value in (("minimum", self.minimum), ("maximum", self.maximum)):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Uniform visual variation {label} must be a finite bounded number."
                    )
                try:
                    numeric = float(value)
                except (OverflowError, ValueError):
                    raise ValueError(
                        f"Uniform visual variation {label} must be a finite bounded number."
                    ) from None
                if (
                    not math.isfinite(numeric)
                    or not -MAX_VARIATION_FIELD_VALUE <= numeric <= MAX_VARIATION_FIELD_VALUE
                ):
                    raise ValueError(
                        f"Uniform visual variation {label} must be a finite bounded number."
                    )
                if self.value_type == "integer" and not isinstance(value, int):
                    raise ValueError("Integer variation rules require integer bounds.")
                bounds.append(numeric)
            if bounds[0] >= bounds[1]:
                raise ValueError("Uniform visual variation minimum must be less than maximum.")
            if self.value_type == "integer":
                self.minimum = int(self.minimum)
                self.maximum = int(self.maximum)
            else:
                self.minimum = float(self.minimum)
                self.maximum = float(self.maximum)
        else:
            if self.minimum is not None or self.maximum is not None:
                raise ValueError("Choice visual variation rules cannot contain numeric bounds.")
            if self.value_type is not None:
                raise ValueError("Choice visual variation rules infer type from their choices.")
            if not 2 <= len(self.choices) <= MAX_VISUAL_VARIATION_CHOICES:
                raise ValueError("Visual variation choices must contain 2–32 entries.")
            normalized = [
                _scalar(value, f"Visual variation choice for {self.path!r}")
                for value in self.choices
            ]
            typed_values = [(type(value), value) for value in normalized]
            if len(set(typed_values)) != len(normalized):
                raise ValueError("Visual variation choices must be unique.")
            self.choices = normalized

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {"schema_version": VISUAL_VARIATION_RULE_SCHEMA_VERSION, **asdict(self)}

    @classmethod
    def from_dict(cls, data: object) -> VisualVariationRule:
        if not isinstance(data, dict):
            raise ValueError("Visual variation rule must be an object.")
        if not str(data.get("path", "")).strip():
            raise ValueError("Visual variation rule path is required.")
        version = int(data.get("schema_version", VISUAL_VARIATION_RULE_SCHEMA_VERSION))
        if version > VISUAL_VARIATION_RULE_SCHEMA_VERSION:
            raise ValueError(
                f"Visual variation rule schema {version} is newer than supported schema "
                f"{VISUAL_VARIATION_RULE_SCHEMA_VERSION}."
            )
        values = {key: value for key, value in data.items() if key in cls.__dataclass_fields__}
        result = cls(**values)
        result.normalize()
        return result


def _variation_id(
    *,
    motif_id: str,
    source_object_id: str,
    source_motif_revision: int,
    pattern_id: str | None,
    pattern_revision: int | None,
    motif_seed: int | None,
    pattern_seed: int | None,
    seed_salt: int,
    seed: int,
    rules: list[VisualVariationRule],
    values: dict[str, str | int | float | bool],
) -> str:
    payload = {
        "motif_id": motif_id,
        "source_object_id": source_object_id,
        "source_motif_revision": source_motif_revision,
        "pattern_id": pattern_id,
        "pattern_revision": pattern_revision,
        "motif_seed": motif_seed,
        "pattern_seed": pattern_seed,
        "seed_salt": seed_salt,
        "seed": seed,
        "rules": [rule.to_dict() for rule in rules],
        "values": values,
    }
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()[:24]
    return f"variation-{digest}"


def _validate_candidate_value(
    rule: VisualVariationRule,
    value: str | int | float | bool,
) -> None:
    if rule.mode == "choice":
        valid = any(type(value) is type(item) and value == item for item in rule.choices)
        if not valid:
            raise ValueError(
                f"Visual variation value for {rule.path!r} is not an allowed choice."
            )
        return
    if rule.value_type == "integer":
        valid = (
            isinstance(value, int)
            and not isinstance(value, bool)
            and rule.minimum <= value <= rule.maximum
        )
    else:
        valid = (
            isinstance(value, float)
            and math.isfinite(value)
            and rule.minimum <= value <= rule.maximum
        )
    if not valid:
        raise ValueError(
            f"Visual variation value for {rule.path!r} is outside its rule bounds."
        )


@dataclass
class VisualMotifVariation:
    """A deterministic candidate overlay; it never mutates the authored motif."""

    variation_id: str = ""
    motif_id: str = ""
    source_object_id: str = ""
    source_motif_revision: int = 0
    pattern_id: str | None = None
    pattern_revision: int | None = None
    motif_seed: int | None = None
    pattern_seed: int | None = None
    seed_salt: int = 0
    seed: int = 0
    selected_paths: list[str] = field(default_factory=list)
    rules: list[VisualVariationRule] = field(default_factory=list)
    values: dict[str, str | int | float | bool] = field(default_factory=dict)

    def normalize(self) -> None:
        self.variation_id = _identifier(self.variation_id, "Visual variation ID")
        self.motif_id = _identifier(self.motif_id, "Visual variation motif ID")
        self.source_object_id = _identifier(
            self.source_object_id,
            "Visual variation source object ID",
        )
        self.source_motif_revision = _revision(
            self.source_motif_revision,
            "Visual variation source motif revision",
        )
        if self.pattern_id is not None:
            self.pattern_id = _identifier(self.pattern_id, "Visual variation pattern ID")
        if self.pattern_revision is not None:
            self.pattern_revision = _revision(
                self.pattern_revision,
                "Visual variation pattern revision",
            )
        if self.pattern_id is None and (
            self.pattern_revision is not None or self.pattern_seed is not None
        ):
            raise ValueError("Visual variation pattern provenance requires a pattern ID.")
        if self.pattern_id is not None and self.pattern_revision is None:
            raise ValueError("Visual variation pattern provenance requires a pattern revision.")
        self.motif_seed = (
            _seed(self.motif_seed, "Visual variation motif seed")
            if self.motif_seed is not None else None
        )
        self.pattern_seed = (
            _seed(self.pattern_seed, "Visual variation pattern seed")
            if self.pattern_seed is not None else None
        )
        self.seed_salt = _seed(self.seed_salt, "Visual variation seed salt")
        self.seed = _seed(self.seed, "Visual variation derived seed")
        if self.motif_seed is None and self.pattern_seed is None:
            raise ValueError("Visual variation must retain an authored motif or pattern seed.")

        if not isinstance(self.selected_paths, list) or not self.selected_paths:
            raise ValueError("Visual variation must contain selected field paths.")
        self.selected_paths = [
            _identifier(path, "Visual variation selected path")
            for path in self.selected_paths
        ]
        if len(self.selected_paths) > MAX_VISUAL_VARIATION_RULES:
            raise ValueError(
                f"Visual variation cannot contain more than {MAX_VISUAL_VARIATION_RULES} paths."
            )
        if len(set(self.selected_paths)) != len(self.selected_paths):
            raise ValueError("Visual variation selected paths must be unique.")

        if not isinstance(self.rules, list) or len(self.rules) != len(self.selected_paths):
            raise ValueError("Visual variation rules must match its selected paths.")
        normalized_rules = [
            rule if isinstance(rule, VisualVariationRule) else VisualVariationRule.from_dict(rule)
            for rule in self.rules
        ]
        for rule in normalized_rules:
            rule.normalize()
        if [rule.path for rule in normalized_rules] != self.selected_paths:
            raise ValueError("Visual variation rule order must match selected paths.")
        self.rules = normalized_rules

        if not isinstance(self.values, dict) or set(self.values) != set(self.selected_paths):
            raise ValueError("Visual variation values must match its selected paths.")
        normalized_values = {
            path: _scalar(self.values[path], f"Visual variation value for {path!r}")
            for path in self.selected_paths
        }
        for rule in self.rules:
            _validate_candidate_value(rule, normalized_values[rule.path])
        self.values = normalized_values

        expected = _variation_id(
            motif_id=self.motif_id,
            source_object_id=self.source_object_id,
            source_motif_revision=self.source_motif_revision,
            pattern_id=self.pattern_id,
            pattern_revision=self.pattern_revision,
            motif_seed=self.motif_seed,
            pattern_seed=self.pattern_seed,
            seed_salt=self.seed_salt,
            seed=self.seed,
            rules=self.rules,
            values=self.values,
        )
        if self.variation_id != expected:
            raise ValueError(
                "Visual variation ID does not match its deterministic provenance."
            )

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return {
            "schema_version": VISUAL_MOTIF_VARIATION_SCHEMA_VERSION,
            **asdict(self),
            "rules": [rule.to_dict() for rule in self.rules],
            "selected_paths": list(self.selected_paths),
            "values": dict(self.values),
        }

    @classmethod
    def from_dict(cls, data: object) -> VisualMotifVariation:
        if not isinstance(data, dict):
            raise ValueError("Visual motif variation must be an object.")
        for field_name in ("variation_id", "motif_id", "source_object_id", "seed"):
            if not str(data.get(field_name, "")).strip():
                raise ValueError(
                    f"Visual motif variation field {field_name!r} is required."
                )
        version = int(data.get("schema_version", VISUAL_MOTIF_VARIATION_SCHEMA_VERSION))
        if version > VISUAL_MOTIF_VARIATION_SCHEMA_VERSION:
            raise ValueError(
                f"Visual motif variation schema {version} is newer than supported schema "
                f"{VISUAL_MOTIF_VARIATION_SCHEMA_VERSION}."
            )
        values = {key: value for key, value in data.items() if key in cls.__dataclass_fields__}
        raw_rules = values.get("rules", [])
        if not isinstance(raw_rules, list):
            raise ValueError("Visual motif variation rules must be a list.")
        values["rules"] = [
            item if isinstance(item, VisualVariationRule) else VisualVariationRule.from_dict(item)
            for item in raw_rules
        ]
        result = cls(**values)
        result.normalize()
        return result


class VisualVariationEngine:
    """Pure deterministic candidate generator with an isolated stream per field."""

    def generate_candidate(
        self,
        motif: VisualMotif,
        source_object_id: str,
        rules: list[VisualVariationRule],
        *,
        pattern: VisualPattern | None = None,
        seed_salt: int = 0,
    ) -> VisualMotifVariation:
        if not isinstance(motif, VisualMotif):
            raise TypeError("Visual variation requires a VisualMotif.")
        if pattern is not None and not isinstance(pattern, VisualPattern):
            raise TypeError("Visual variation pattern must be a VisualPattern.")
        if not isinstance(rules, list) or not rules:
            raise ValueError("Visual variation requires at least one rule.")
        if len(rules) > MAX_VISUAL_VARIATION_RULES:
            raise ValueError(
                f"Visual variation cannot contain more than {MAX_VISUAL_VARIATION_RULES} rules."
            )
        normalized_salt = _seed(seed_salt, "Visual variation seed salt")
        source_id = _identifier(source_object_id, "Visual variation source object ID")
        motif_snapshot = VisualMotif.from_dict(motif.to_dict())
        pattern_snapshot = (
            VisualPattern.from_dict(pattern.to_dict()) if pattern is not None else None
        )
        if motif_snapshot.seed is None and (
            pattern_snapshot is None or pattern_snapshot.seed is None
        ):
            raise ValueError(
                "Visual variation requires an authored motif or pattern seed."
            )

        normalized_rules = [
            VisualVariationRule.from_dict(
                rule.to_dict() if isinstance(rule, VisualVariationRule) else rule
            )
            for rule in rules
        ]
        normalized_rules.sort(key=lambda rule: rule.path)
        paths = [rule.path for rule in normalized_rules]
        if len(set(paths)) != len(paths):
            raise ValueError("Visual variation rules must have unique field paths.")

        allowed_paths = set(motif_snapshot.allowed_variations)
        invariant_paths = set(motif_snapshot.invariants)
        root_seed = self._root_seed(
            motif_snapshot,
            source_id,
            pattern_snapshot,
            normalized_salt,
        )
        values: dict[str, str | int | float | bool] = {}
        for rule in normalized_rules:
            if rule.path not in allowed_paths:
                raise ValueError(
                    f"Visual variation path {rule.path!r} is not declared as allowed."
                )
            if rule.path in invariant_paths:
                raise ValueError(
                    f"Visual variation cannot change invariant field {rule.path!r}."
                )
            current = _motif_value(motif_snapshot, rule.path)
            values[rule.path] = self._generate_value(
                rule,
                current,
                self._path_seed(root_seed, rule.path),
            )

        result = VisualMotifVariation(
            variation_id="pending",
            motif_id=motif_snapshot.motif_id,
            source_object_id=source_id,
            source_motif_revision=motif_snapshot.revision,
            pattern_id=pattern_snapshot.pattern_id if pattern_snapshot else None,
            pattern_revision=pattern_snapshot.revision if pattern_snapshot else None,
            motif_seed=motif_snapshot.seed,
            pattern_seed=pattern_snapshot.seed if pattern_snapshot else None,
            seed_salt=normalized_salt,
            seed=root_seed,
            selected_paths=paths,
            rules=normalized_rules,
            values=values,
        )
        result.variation_id = _variation_id(
            motif_id=result.motif_id,
            source_object_id=result.source_object_id,
            source_motif_revision=result.source_motif_revision,
            pattern_id=result.pattern_id,
            pattern_revision=result.pattern_revision,
            motif_seed=result.motif_seed,
            pattern_seed=result.pattern_seed,
            seed_salt=result.seed_salt,
            seed=result.seed,
            rules=result.rules,
            values=result.values,
        )
        result.normalize()
        return result

    @staticmethod
    def _root_seed(
        motif: VisualMotif,
        source_object_id: str,
        pattern: VisualPattern | None,
        seed_salt: int,
    ) -> int:
        payload = {
            "motif_id": motif.motif_id,
            "motif_revision": motif.revision,
            "motif_seed": motif.seed,
            "source_object_id": source_object_id,
            "pattern_id": pattern.pattern_id if pattern else None,
            "pattern_revision": pattern.revision if pattern else None,
            "pattern_seed": pattern.seed if pattern else None,
            "seed_salt": seed_salt,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")

    @staticmethod
    def _path_seed(root_seed: int, path: str) -> int:
        encoded = f"{root_seed}:{path}".encode("utf-8")
        return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")

    @staticmethod
    def _generate_value(
        rule: VisualVariationRule,
        current: str | int | float | bool,
        seed: int,
    ) -> str | int | float | bool:
        rng = random.Random(seed)
        if rule.mode == "choice":
            if any(type(value) is not type(current) for value in rule.choices):
                raise ValueError(
                    f"Visual variation choices for {rule.path!r} must match "
                    "the authored field type."
                )
            alternatives = [value for value in rule.choices if value != current]
            if not alternatives:
                raise ValueError(
                    f"Visual variation choices for {rule.path!r} do not change its value."
                )
            return rng.choice(alternatives)
        if rule.value_type == "integer":
            if isinstance(current, bool) or not isinstance(current, int):
                raise ValueError(
                    f"Integer variation rule requires an integer field: {rule.path!r}."
                )
            return rng.randint(rule.minimum, rule.maximum)
        if isinstance(current, bool) or not isinstance(current, float):
            raise ValueError(
                f"Number variation rule requires a floating-point field: {rule.path!r}."
            )
        return rng.uniform(float(rule.minimum), float(rule.maximum))
