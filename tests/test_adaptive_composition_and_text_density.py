from __future__ import annotations

from core.automation import AutomationSettings
from core.composition import Layer
from core.performance_manager import PerformanceManager
from generators.catalog import default_generator_settings, normalize_settings
from generators.text_pools import random_text_sample


def test_manual_layout_randomizer_uses_video_generator_and_overlay_layers() -> None:
    layers = [
        Layer(
            id="video-background",
            source_type="video",
            source_id="deck_a",
            z_index=0,
        ),
        Layer(
            id="text-headline",
            source_type="generator",
            generator_type="text",
            source_id="generator:text",
            z_index=1,
        ),
        Layer(
            id="geometry",
            source_type="generator",
            generator_type="geometry",
            source_id="generator:geometry",
            z_index=2,
        ),
        Layer(
            id="overlay",
            source_type="overlay",
            source_id="overlay:one",
            z_index=3,
        ),
        Layer(
            id="locked",
            source_type="video",
            source_id="deck_b",
            locked=True,
            position=(0.1, 0.2),
            scale=(0.3, 0.4),
            rotation=12.0,
            z_index=4,
        ),
        Layer(
            id="hidden",
            source_type="video",
            source_id="deck_c",
            visible=False,
            position=(0.8, 0.9),
            scale=(0.6, 0.7),
            rotation=-9.0,
            z_index=5,
        ),
    ]
    protected = {
        layer.id: (
            layer.position,
            layer.scale,
            layer.rotation,
            layer.opacity,
            layer.blend_mode,
            layer.z_index,
        )
        for layer in layers if layer.locked or not layer.visible
    }

    manager = PerformanceManager(seed=29)
    changed = manager.randomize_layout(layers)

    assert changed == 4
    assert {layer.id for layer in layers if layer.z_index < 0} <= {
        "video-background", "geometry", "overlay"
    }
    text_layer = next(layer for layer in layers if layer.id == "text-headline")
    assert text_layer.z_index == max(layer.z_index for layer in layers)
    assert text_layer.scale[0] >= 1.02
    assert text_layer.scale[1] >= 1.02
    for layer in layers:
        if layer.id in protected:
            assert (
                layer.position,
                layer.scale,
                layer.rotation,
                layer.opacity,
                layer.blend_mode,
                layer.z_index,
            ) == protected[layer.id]


def test_manual_layout_randomizer_does_not_mutate_locked_or_hidden_only_layers() -> None:
    layers = [
        Layer(id="locked", source_type="video", locked=True),
        Layer(id="hidden", source_type="video", visible=False),
    ]

    assert PerformanceManager(seed=2).randomize_layout(layers) == 0


def test_new_text_generators_default_to_headline_led_eight_fragment_collages() -> None:
    settings = default_generator_settings("text")
    normalized = normalize_settings("text", {})

    assert settings["text_pool_count"] == 8
    assert normalized["text_pool_count"] == 8
    assert settings["text_layout"] == "collage"
    assert settings["font_weight"] == 800
    assert AutomationSettings().text_fragments == 8


def test_default_text_pool_sample_contains_eight_fragments() -> None:
    sample = random_text_sample(seed=8, use_dictionary=False)

    assert len([line for line in sample.splitlines() if line.strip()]) == 8
