from __future__ import annotations

import pytest

from core.visual_grammar import VisualPattern
from core.visual_model import VisualIdentity, VisualMotif
from core.visual_variation import (
    VisualMotifVariation,
    VisualVariationEngine,
    VisualVariationRule,
)


def _motif(*, seed: int | None = 731) -> VisualMotif:
    return VisualMotif(
        motif_id="orbit-motif",
        name="Seven-point orbit",
        family="motion",
        identity=VisualIdentity(
            geometry_signature="seven-point-cycle",
            palette_identity="oxide-red-on-black",
            motion_identity="counter-rotating",
            traits={"symmetry": "seven-fold"},
        ),
        parameters={"radius": 0.42, "phase": 0.25, "period_beats": 7},
        invariants={
            "identity.geometry_signature": "seven-point-cycle",
            "identity.traits.symmetry": "seven-fold",
            "parameters.period_beats": 7,
        },
        allowed_variations=[
            "identity.palette_identity",
            "parameters.radius",
            "parameters.phase",
        ],
        seed=seed,
        revision=4,
    )


def _rules() -> list[VisualVariationRule]:
    return [
        VisualVariationRule(
            path="identity.palette_identity",
            mode="choice",
            choices=[
                "oxide-red-on-black",
                "cold-cyan-on-black",
                "paper-white-on-oxide",
            ],
        ),
        VisualVariationRule(
            path="parameters.radius",
            mode="uniform",
            minimum=0.2,
            maximum=0.8,
            value_type="number",
        ),
        VisualVariationRule(
            path="parameters.phase",
            mode="uniform",
            minimum=0.0,
            maximum=1.0,
            value_type="number",
        ),
    ]


def test_seeded_variation_is_reproducible_and_does_not_mutate_motif() -> None:
    engine = VisualVariationEngine()
    motif = _motif()
    before = motif.to_dict()

    first = engine.generate_candidate(motif, "object-a", _rules())
    second = engine.generate_candidate(motif, "object-a", _rules())

    assert first.to_dict() == second.to_dict()
    assert motif.to_dict() == before
    assert first.motif_id == motif.motif_id
    assert first.source_object_id == "object-a"
    assert first.source_motif_revision == motif.revision
    assert first.motif_seed == motif.seed
    assert first.seed != motif.seed
    assert first.values["identity.palette_identity"] in {
        "cold-cyan-on-black",
        "paper-white-on-oxide",
    }
    assert 0.2 <= first.values["parameters.radius"] <= 0.8
    assert 0.0 <= first.values["parameters.phase"] <= 1.0


def test_each_field_has_an_isolated_stream_independent_of_rule_order() -> None:
    engine = VisualVariationEngine()
    motif = _motif()
    forward = engine.generate_candidate(motif, "object-a", _rules())
    reverse = engine.generate_candidate(
        motif,
        "object-a",
        list(reversed(_rules())),
    )

    assert forward.seed == reverse.seed
    assert forward.values == reverse.values
    assert forward.variation_id == reverse.variation_id


def test_stable_object_identity_and_pattern_seed_change_the_stream() -> None:
    engine = VisualVariationEngine()
    motif = _motif()
    base = engine.generate_candidate(motif, "object-a", _rules())
    other_object = engine.generate_candidate(motif, "object-b", _rules())
    pattern_a = VisualPattern(
        pattern_id="seven-beat-pattern",
        cycle_length=7,
        cycle_unit="beats",
        timing_basis="authored_music",
        seed=11,
    )
    pattern_b = VisualPattern(
        pattern_id="seven-beat-pattern",
        cycle_length=7,
        cycle_unit="beats",
        timing_basis="authored_music",
        seed=12,
    )
    candidate_a = engine.generate_candidate(
        motif, "object-a", _rules(), pattern=pattern_a
    )
    candidate_b = engine.generate_candidate(
        motif, "object-a", _rules(), pattern=pattern_b
    )

    assert base.seed != other_object.seed
    assert candidate_a.seed != candidate_b.seed
    assert candidate_a.pattern_id == pattern_a.pattern_id
    assert candidate_a.pattern_seed == pattern_a.seed


def test_pattern_identity_is_retained_without_a_pattern_seed() -> None:
    pattern = VisualPattern(pattern_id="unseeded-pattern")
    candidate = VisualVariationEngine().generate_candidate(
        _motif(),
        "object-pattern",
        _rules(),
        pattern=pattern,
    )

    assert candidate.pattern_id == pattern.pattern_id
    assert candidate.pattern_revision == pattern.revision
    assert candidate.pattern_seed is None


def test_pattern_seed_can_supply_determinism_without_motif_seed() -> None:
    pattern = VisualPattern(pattern_id="pattern-seeded", seed=19)
    candidate = VisualVariationEngine().generate_candidate(
        _motif(seed=None),
        "object-pattern-seeded",
        _rules(),
        pattern=pattern,
    )

    assert candidate.motif_seed is None
    assert candidate.pattern_seed == 19
    assert candidate.pattern_id == pattern.pattern_id


def test_variation_requires_an_authored_motif_or_pattern_seed() -> None:
    with pytest.raises(ValueError, match="requires an authored motif or pattern seed"):
        VisualVariationEngine().generate_candidate(
            _motif(seed=None),
            "object-no-seed",
            _rules(),
        )


def test_variation_rejects_undeclared_and_invariant_paths() -> None:
    engine = VisualVariationEngine()
    motif = _motif()

    with pytest.raises(ValueError, match="not declared as allowed"):
        engine.generate_candidate(
            motif,
            "object-invalid",
            [
                VisualVariationRule(
                    path="identity.geometry_signature",
                    mode="choice",
                    choices=["seven-point-cycle", "six-point-cycle"],
                )
            ],
        )

    with pytest.raises(ValueError, match="not declared as allowed"):
        engine.generate_candidate(
            motif,
            "object-invalid",
            [
                VisualVariationRule(
                    path="identity.traits.symmetry",
                    mode="choice",
                    choices=["seven-fold", "six-fold"],
                )
            ],
        )


def test_variation_rules_require_explicit_typed_bounds_or_choices() -> None:
    with pytest.raises(ValueError, match="requires value_type"):
        VisualVariationRule(
            path="parameters.radius",
            mode="uniform",
            minimum=0.2,
            maximum=0.8,
        ).normalize()

    with pytest.raises(ValueError, match="requires integer bounds"):
        VisualVariationRule(
            path="parameters.period_beats",
            mode="uniform",
            minimum=6.0,
            maximum=8.0,
            value_type="integer",
        ).normalize()

    with pytest.raises(ValueError, match="must match"):
        VisualVariationEngine().generate_candidate(
            _motif(),
            "object-invalid",
            [
                VisualVariationRule(
                    path="parameters.radius",
                    mode="choice",
                    choices=["small", "large"],
                )
            ],
        )


def test_variation_candidate_is_self_verifying_and_round_trips() -> None:
    candidate = VisualVariationEngine().generate_candidate(
        _motif(),
        "object-replay",
        _rules(),
        seed_salt=17,
    )
    restored = VisualMotifVariation.from_dict(candidate.to_dict())

    assert restored == candidate
    tampered = candidate.to_dict()
    tampered["values"]["parameters.radius"] = 0.7
    with pytest.raises(ValueError, match="ID does not match"):
        VisualMotifVariation.from_dict(tampered)

    tampered_outside_rule = candidate.to_dict()
    tampered_outside_rule["values"]["parameters.radius"] = 1.7
    with pytest.raises(ValueError, match="outside its rule bounds"):
        VisualMotifVariation.from_dict(tampered_outside_rule)


def test_variation_rejects_duplicate_excessive_rules_and_invalid_seeds() -> None:
    engine = VisualVariationEngine()
    motif = _motif()
    duplicate = [
        VisualVariationRule(
            path="parameters.radius",
            mode="uniform",
            minimum=0.2,
            maximum=0.8,
            value_type="number",
        ),
        VisualVariationRule(
            path="parameters.radius",
            mode="uniform",
            minimum=0.3,
            maximum=0.9,
            value_type="number",
        ),
    ]
    with pytest.raises(ValueError, match="unique field paths"):
        engine.generate_candidate(motif, "object-duplicate", duplicate)

    with pytest.raises(ValueError, match="unsigned 64-bit"):
        engine.generate_candidate(motif, "object-bad-salt", _rules(), seed_salt=-1)

    excessive = [
        VisualVariationRule(
            path="parameters.radius",
            mode="uniform",
            minimum=0.2,
            maximum=0.8,
            value_type="number",
        )
        for _ in range(65)
    ]
    with pytest.raises(ValueError, match="more than 64 rules"):
        engine.generate_candidate(motif, "object-excessive", excessive)


def test_rule_and_candidate_ids_are_required_on_deserialization() -> None:
    with pytest.raises(ValueError, match="rule path is required"):
        VisualVariationRule.from_dict({"mode": "uniform", "minimum": 0, "maximum": 1})

    with pytest.raises(ValueError, match="variation field 'variation_id' is required"):
        VisualMotifVariation.from_dict(
            {"motif_id": "motif", "source_object_id": "object", "seed": 1}
        )
