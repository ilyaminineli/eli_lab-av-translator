from __future__ import annotations

import random

from core.automation import AutomationDirector, AutomationSettings
from core.composition import Layer
from core.generative_director import GenerativeVariationDirector


def make_layers(count: int = 6) -> list[Layer]:
    kinds = (
        ("video", None),
        ("generator", "text"),
        ("generator", "geometry"),
        ("overlay", None),
        ("generator", "particles"),
        ("video", None),
    )
    layers: list[Layer] = []
    for index in range(count):
        source_type, generator_type = kinds[index % len(kinds)]
        layers.append(
            Layer(
                id=f"layer-{index}",
                name=f"Layer {index}",
                source_type=source_type,
                source_id=f"source-{index}",
                generator_type=generator_type,
            )
        )
    return layers


def test_legacy_settings_cannot_restore_the_two_layer_cap() -> None:
    settings = AutomationSettings(
        constrained_generative=False,
        max_layers_per_variation=2,
    )
    settings.normalize()

    assert settings.constrained_generative is True
    assert settings.max_layers_per_variation == 0
    assert settings.keep_visual_anchor is False
    assert settings.preserve_background_source is False


def test_director_can_select_more_than_two_layers() -> None:
    layers = make_layers(7)
    director = GenerativeVariationDirector()

    selected = director.select_layers(
        layers,
        maximum=len(layers),
        rng=random.Random(12),
    )

    assert len(selected) == len(layers)
    assert set(selected) == {layer.id for layer in layers}


def test_anchor_is_optional_and_only_removed_when_requested() -> None:
    layers = make_layers(5)
    director = GenerativeVariationDirector()

    unrestricted = director.select_layers(
        layers,
        maximum=len(layers),
        rng=random.Random(7),
        keep_anchor=False,
    )
    anchored = director.select_layers(
        layers,
        maximum=len(layers),
        rng=random.Random(7),
        keep_anchor=True,
    )

    assert len(unrestricted) == 5
    assert len(anchored) == 4
    assert director.anchor_layer_id not in anchored


def test_dynamic_budget_can_expand_to_every_eligible_layer() -> None:
    director = AutomationDirector(seed=11)
    director._layers = make_layers(8)
    director._performance_section = "peak"
    director._performance_energy = 1.0
    director._performance_intensity = 1.0
    director._macro_values = {
        "chaos": 1.0,
        "density": 1.0,
        "fragment": 1.0,
    }

    assert director._variation_budget(strength=1.0) == 8
    assert len(director._select_variation_layers(strength=1.0)) == 8


def test_layout_variation_includes_video_generators_and_overlays() -> None:
    director = AutomationDirector(seed=3)
    layers = make_layers(4)
    director._layers = layers
    director.settings = AutomationSettings(
        spatial_chaos=1.0,
        overlap_bias=1.0,
        offscreen_range=1.0,
        abrupt_transition_probability=1.0,
    )
    director.settings.normalize()
    director._macro_values = {"chaos": 1.0, "density": 1.0, "fragment": 1.0}

    changed = director._randomize_layout(
        layer_ids=[layer.id for layer in layers],
        now=100.0,
    )

    assert changed == 4
    assert not director._layout_morphs
    assert {layer.source_type for layer in layers} == {
        "video",
        "generator",
        "overlay",
    }
    assert all(layer.scale[0] >= 0.12 for layer in layers)
    assert all(-1.0 <= layer.position[0] <= 2.0 for layer in layers)
    assert all(-1.0 <= layer.position[1] <= 2.0 for layer in layers)


def test_timer_path_uses_the_unified_director_without_runtime_name_error() -> None:
    director = AutomationDirector(seed=5)
    director.running = True
    director._layers = make_layers(4)
    director.settings = AutomationSettings(
        musical_sync="time",
        randomize_layout=True,
        randomize_effects=False,
        randomize_generators=False,
        spatial_chaos=1.0,
        abrupt_transition_probability=1.0,
    )
    director.settings.normalize()
    director._macro_values = {"chaos": 1.0, "density": 1.0, "fragment": 1.0}
    director._layout_due = 5.0
    director._effects_due = None
    director._generators_due = None

    assert director.tick(now=6.0) is True
    assert "variation" in director.last_action


def test_bar_events_reach_the_director_for_every_director_character() -> None:
    for style in ("random", "structured", "generative"):
        director = AutomationDirector(seed=17)
        director.running = True
        director._layers = make_layers(4)
        director.settings = AutomationSettings(
            musical_sync="bar",
            performance_style=style,
            randomize_layout=False,
            randomize_effects=False,
            randomize_generators=False,
        )
        director.settings.normalize()

        director.on_musical_event(
            "bar",
            energy=0.8,
            intensity=0.85,
            cutoff=0.7,
            bar_index=16,
            macro_values={"chaos": 0.8, "density": 0.7, "fragment": 0.6},
            now=100.0,
        )

        assert "bar" in director.last_action
