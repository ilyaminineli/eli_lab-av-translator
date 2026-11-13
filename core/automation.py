from __future__ import annotations

import logging
import random
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from core.composition import Layer
from effects.layer_settings import LAYER_EFFECT_PRESETS, apply_layer_effect_preset
from effects.settings import PRESETS, EffectSettings
from generators.catalog import GENERATOR_TYPES, normalize_settings
from generators.palettes import palette_look, palette_names
from generators.text_pools import random_text_sample
from core.generative_director import GenerativeVariationDirector
from media.models import MediaAsset

_LOG = logging.getLogger(__name__)


@dataclass
class AutomationSettings:
    """Timing and probability controls for unattended collage performance."""

    min_segment_seconds: float = 4.0
    max_segment_seconds: float = 16.0
    min_cut_interval: float = 8.0
    max_cut_interval: float = 24.0
    loop_probability: float = 0.58
    clip_switch_probability: float = 0.38
    randomize_layout: bool = True
    randomize_effects: bool = True
    min_layout_interval: float = 14.0
    max_layout_interval: float = 32.0
    min_effect_interval: float = 10.0
    max_effect_interval: float = 26.0
    randomize_generators: bool = True
    randomize_text: bool = True
    randomize_layer_effects: bool = True
    randomize_overlays: bool = True
    randomize_palette: bool = False
    min_generator_interval: float = 18.0
    max_generator_interval: float = 42.0
    text_language: str = "bilingual"
    text_theme: str = "random"
    text_fragments: int = 16
    performance_style: str = "random"
    musical_sync: str = "time"
    constrained_generative: bool = True
    max_layers_per_variation: int = 2
    preserve_background_source: bool = True
    keep_visual_anchor: bool = True
    effect_after_transition: bool = True
    palette_memory_phrases: int = 4
    peak_particle_boost: float = 0.35
    slow_breakdown_transitions: bool = True
    breakdown_transition_min_seconds: float = 5.0
    breakdown_transition_max_seconds: float = 9.0
    layout_transition_min_seconds: float = 0.65
    layout_transition_max_seconds: float = 1.8

    def normalize(self) -> None:
        self.min_segment_seconds = max(0.5, float(self.min_segment_seconds))
        self.max_segment_seconds = max(self.min_segment_seconds, float(self.max_segment_seconds))
        self.min_cut_interval = max(1.0, float(self.min_cut_interval))
        self.max_cut_interval = max(self.min_cut_interval, float(self.max_cut_interval))
        self.loop_probability = max(0.0, min(1.0, float(self.loop_probability)))
        self.clip_switch_probability = max(0.0, min(1.0, float(self.clip_switch_probability)))
        self.min_layout_interval = max(2.0, float(self.min_layout_interval))
        self.max_layout_interval = max(self.min_layout_interval, float(self.max_layout_interval))
        self.min_effect_interval = max(2.0, float(self.min_effect_interval))
        self.max_effect_interval = max(self.min_effect_interval, float(self.max_effect_interval))
        self.min_generator_interval = max(3.0, float(self.min_generator_interval))
        self.max_generator_interval = max(
            self.min_generator_interval, float(self.max_generator_interval)
        )
        if self.text_language not in {"english", "japanese", "bilingual"}:
            self.text_language = "bilingual"
        if self.text_theme not in {"random", "memory", "body", "signal", "ritual", "identity"}:
            self.text_theme = "random"
        self.text_fragments = max(1, min(60, int(self.text_fragments)))
        if self.performance_style not in {"random", "structured", "generative"}:
            self.performance_style = "random"
        if self.musical_sync not in {"time", "bar", "phrase", "hybrid"}:
            self.musical_sync = "time"
        self.constrained_generative = bool(self.constrained_generative)
        self.max_layers_per_variation = max(1, min(2, int(self.max_layers_per_variation)))
        self.preserve_background_source = bool(self.preserve_background_source)
        self.keep_visual_anchor = bool(self.keep_visual_anchor)
        self.effect_after_transition = bool(self.effect_after_transition)
        self.palette_memory_phrases = max(0, min(16, int(self.palette_memory_phrases)))
        self.peak_particle_boost = max(0.0, min(1.0, float(self.peak_particle_boost)))
        self.slow_breakdown_transitions = bool(self.slow_breakdown_transitions)
        self.layout_transition_min_seconds = max(
            0.1, min(8.0, float(self.layout_transition_min_seconds))
        )
        self.layout_transition_max_seconds = max(
            self.layout_transition_min_seconds,
            min(12.0, float(self.layout_transition_max_seconds)),
        )
        self.breakdown_transition_min_seconds = max(
            2.0, min(20.0, float(self.breakdown_transition_min_seconds))
        )
        self.breakdown_transition_max_seconds = max(
            self.breakdown_transition_min_seconds,
            min(30.0, float(self.breakdown_transition_max_seconds)),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def choose_random_segment(
        duration: float | None,
        minimum: float,
        maximum: float,
        rng: random.Random,
) -> tuple[float, float | None]:
    """Return a random in/out range contained in the clip duration."""
    minimum = max(0.5, float(minimum))
    maximum = max(minimum, float(maximum))
    if duration is None or duration <= 0:
        return 0.0, None

    safe_duration = max(0.1, float(duration))
    segment_length = min(safe_duration, rng.uniform(minimum, maximum))
    latest_start = max(0.0, safe_duration - segment_length)
    start = rng.uniform(0.0, latest_start) if latest_start > 0 else 0.0
    end = min(safe_duration, start + segment_length)
    return round(start, 3), round(end, 3)


class AutomationDirector:
    """Schedules footage, layout, master looks, generators, text and layer FX."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.settings = AutomationSettings()
        self.running = False
        self.started_at = 0.0
        self.ends_at: float | None = None
        self.last_action = "Idle"
        self._assets: list[MediaAsset] = []
        self._decks: dict[str, object] = {}
        self._layers: list[Layer] = []
        self._effects: EffectSettings | None = None
        self._deck_due: dict[str, float] = {}
        self._layout_due: float | None = None
        self._effects_due: float | None = None
        self._generators_due: float | None = None
        self._performance_energy = 0.0
        self._performance_cutoff = 0.5
        self._performance_intensity = 0.0
        self._performance_bar_index = 0
        self._performance_section = "idle"
        self._last_musical_event_at = 0.0
        self._macro_values: dict[str, float] = {}
        self._last_scene_id = ""
        self._layout_morphs: dict[str, dict[str, object]] = {}
        self._peak_particle_base: dict[str, tuple[str, float]] = {}
        self._director = GenerativeVariationDirector()
        self.generator_settings_changed = None
        self.palette_changed = None

    @staticmethod
    def _interval(rng: random.Random, low: float, high: float) -> float:
        return rng.uniform(low, high)

    def start(
            self,
            assets: Iterable[MediaAsset],
            decks: Iterable[object] | dict[str, object],
            layers: list[Layer],
            effects: EffectSettings,
            settings: AutomationSettings | None = None,
            duration_seconds: float | None = 1800.0,
            now: float | None = None,
    ) -> int:
        candidates = [
            asset for asset in assets
            if asset.status not in {"error", "unsupported"} and Path(asset.path).is_file()
        ]
        self.settings = settings or AutomationSettings()
        self.settings.normalize()
        self._assets = candidates
        if isinstance(decks, dict):
            self._decks = decks
        else:
            self._decks = {str(getattr(deck, "id")): deck for deck in decks}
        self._layers = layers
        self._effects = effects
        started = time.monotonic() if now is None else float(now)
        self.started_at = started
        self.ends_at = (
            started + max(1.0, float(duration_seconds))
            if duration_seconds is not None else None
        )
        self._deck_due.clear()
        self._layout_morphs.clear()
        self._peak_particle_base.clear()
        self._macro_values.clear()
        self._last_scene_id = ""
        self._director.reset(self.settings.palette_memory_phrases)
        self.running = True
        loaded = 0

        for deck_id, deck in self._decks.items():
            if getattr(deck, "locked", False):
                continue
            if self._load_random_segment(deck, None, started):
                loaded += 1

        if not loaded and candidates:
            self.running = False
            self._deck_due.clear()
            raise ValueError(
                "Playable footage exists, but no unlocked video deck could load it. "
                "Unlock a deck and check that the imported videos are readable."
            )

        if self.settings.randomize_layout:
            self._randomize_layout(now=started)
        if self.settings.randomize_effects and not (
                self.settings.performance_style == "generative"
                and self.settings.constrained_generative
                and self.settings.effect_after_transition
        ):
            self._randomize_effects()
        self._layout_due = started + self._interval(
            self.rng, self.settings.min_layout_interval, self.settings.max_layout_interval
        )
        self._effects_due = started + self._interval(
            self.rng, self.settings.min_effect_interval, self.settings.max_effect_interval
        )
        self._generators_due = started + self._interval(
            self.rng, self.settings.min_generator_interval, self.settings.max_generator_interval
        )
        self.last_action = f"Automation started · {loaded} deck(s)"
        return loaded

    def replace_assets(
            self,
            assets: Iterable[MediaAsset],
            now: float | None = None,
    ) -> None:
        """Refresh the live source pool without interrupting currently loaded clips."""
        self._assets = [
            asset for asset in assets
            if asset.status not in {"error", "unsupported"} and Path(asset.path).is_file()
        ]
        if not self.running:
            return
        current = time.monotonic() if now is None else float(now)
        if not self._assets:
            self._deck_due.clear()
            self.last_action = "Source pool empty · current clips continue playing"
            return
        for deck_id in self._decks:
            self._deck_due[deck_id] = current + self._interval(
                self.rng, self.settings.min_cut_interval, self.settings.max_cut_interval
            )
        self.last_action = f"Source pool refreshed · {len(self._assets)} clip(s)"

    def _load_random_segment(
            self,
            deck: object,
            current_asset_id: str | None,
            now: float,
    ) -> bool:
        if not self._assets:
            return False

        deck_id = str(getattr(deck, "id"))
        switch = (
                current_asset_id is None
                or self.rng.random() < self.settings.clip_switch_probability
        )
        current_asset = next(
            (asset for asset in self._assets if asset.id == current_asset_id),
            None,
        )
        if not switch and current_asset is not None:
            ordered_assets = [current_asset]
            ordered_assets.extend(
                asset for asset in self._assets if asset.id != current_asset.id
            )
        else:
            alternatives = [
                asset for asset in self._assets if asset.id != current_asset_id
            ]
            self.rng.shuffle(alternatives)
            if current_asset is not None:
                alternatives.append(current_asset)
            ordered_assets = alternatives or list(self._assets)

        # A single corrupt or unreadable clip must not abort a whole Auto session.
        for asset in ordered_assets:
            segment_start, segment_end = choose_random_segment(
                asset.duration,
                self.settings.min_segment_seconds,
                self.settings.max_segment_seconds,
                self.rng,
            )
            should_loop = self.rng.random() < self.settings.loop_probability
            try:
                deck.load(
                    asset.path,
                    asset_id=asset.id,
                    collection_id=asset.collection_id,
                    segment_start=segment_start,
                    segment_end=segment_end,
                    loop=should_loop,
                )
            except Exception:
                _LOG.exception(
                    "Auto Mode could not load %s into %s; trying another clip",
                    asset.path,
                    deck_id,
                )
                continue

            if not should_loop and segment_end is not None:
                # One-shot fragments advance as soon as their out point is reached.
                cut_delay = max(0.5, segment_end - segment_start)
            else:
                cut_delay = self._interval(
                    self.rng,
                    self.settings.min_cut_interval,
                    self.settings.max_cut_interval,
                )
            self._deck_due[deck_id] = now + cut_delay
            return True

        self._deck_due[deck_id] = now + self._interval(
            self.rng,
            self.settings.min_cut_interval,
            self.settings.max_cut_interval,
        )
        self.last_action = f"No readable footage found for {deck_id.upper()}"
        return False

    def _randomize_layout(self) -> None:
        # Auto Mode randomizes video layouts without disturbing authored generator
        # typography and procedural graphics.
        active = [
            layer for layer in self._layers
            if layer.source_type == "video" and not layer.locked
        ]
        if not active:
            return
        patterns = [
            [(0.25, 0.25, 0.5), (0.75, 0.25, 0.5), (0.25, 0.75, 0.5), (0.75, 0.75, 0.5)],
            [(0.5, 0.5, 1.0), (0.78, 0.22, 0.28), (0.78, 0.78, 0.28), (0.22, 0.78, 0.28)],
            [(0.5, 0.17, 1.0), (0.5, 0.50, 1.0), (0.5, 0.83, 1.0), (0.5, 0.5, 0.45)],
            [(0.17, 0.5, 1.0), (0.50, 0.5, 1.0), (0.83, 0.5, 1.0), (0.5, 0.5, 0.45)],
            [(0.34, 0.34, 0.68), (0.68, 0.34, 0.42), (0.34, 0.68, 0.42), (0.72, 0.72, 0.34)],
            [(0.5, 0.5, 0.82), (0.5, 0.5, 0.62), (0.5, 0.5, 0.40), (0.5, 0.5, 0.22)],
        ]
        pattern = self.rng.choice(patterns)
        for index, layer in enumerate(active):
            x, y, size = pattern[index % len(pattern)]
            jitter = 0.035
            layer.position = (
                max(0.0, min(1.0, x + self.rng.uniform(-jitter, jitter))),
                max(0.0, min(1.0, y + self.rng.uniform(-jitter, jitter))),
            )
            scale = max(0.12, size * self.rng.uniform(0.88, 1.12))
            layer.scale = (scale, scale)
            layer.rotation = self.rng.uniform(-5.0, 5.0)
            layer.opacity = self.rng.uniform(0.78, 1.0)
            layer.blend_mode = self.rng.choice(
                ("normal", "normal", "screen", "add", "multiply", "difference")
            )

    def _randomize_effects(self) -> None:
        if self._effects is None:
            return
        names = [name for name in PRESETS if name != "Clean"]
        self._effects.apply_preset(self.rng.choice(names))

    def _randomize_generators(self) -> int:
        changed = 0
        for layer in self._layers:
            if layer.locked or not layer.visible:
                continue

            if layer.source_type == "generator" and layer.generator_type in GENERATOR_TYPES:
                kind = layer.generator_type
                values = normalize_settings(kind, layer.generator_settings)
                updated = False
                if self.settings.randomize_palette:
                    from generators.palettes import random_palette_look
                    values.update(random_palette_look(self.rng))
                    updated = True

                if (
                        self.settings.randomize_generators
                        and kind == "text"
                        and self.settings.randomize_text
                ):
                    if bool(values.get("text_auto_regenerate", True)):
                        values.update({
                            "text": random_text_sample(
                                str(values.get("text_pool_language", self.settings.text_language)),
                                str(values.get("text_pool_theme", self.settings.text_theme)),
                                int(values.get("text_pool_count", self.settings.text_fragments)),
                                seed=self.rng.randrange(0, 2 ** 31 - 1),
                                use_dictionary=bool(values.get("text_pool_dictionary", True)),
                            ),
                            "text_layout": self.rng.choice(("single", "collage")),
                            "collage_seed": self.rng.randrange(0, 2 ** 31 - 1),
                            "text_color_mode": self.rng.choice(("single", "alternate")),
                        })
                    # Motion can vary even when the phrase itself is held.
                    values.update({
                        "text_animation": self.rng.choice(
                            ("type_on", "word_reveal", "line_wave", "jitter", "crawl", "glitch")
                        ),
                        "text_animation_speed": self.rng.uniform(0.35, 2.8),
                        "text_animation_amount": self.rng.uniform(0.015, 0.12),
                    })
                    updated = True
                elif self.settings.randomize_generators and kind == "geometry":
                    motion = self.rng.choice(("rotate", "pulse", "drift", "warp"))
                    motion_ranges = {
                        "rotate": (20.0, 100.0),
                        "pulse": (0.04, 0.22),
                        "drift": (0.015, 0.07),
                        "warp": (0.08, 0.42),
                    }
                    values.update({
                        "pattern": self.rng.choice(
                            ("rings", "grid", "radial", "crosshatch", "spiral", "moire", "hexgrid")
                        ),
                        "density": self.rng.randint(6, 34),
                        "rotation": self.rng.uniform(-35, 35),
                        "animation": motion,
                        "animation_speed": self.rng.uniform(0.08, 1.8),
                        "animation_amount": self.rng.uniform(*motion_ranges[motion]),
                    })
                    updated = True
                elif self.settings.randomize_generators and kind == "waveform":
                    values.update({
                        "pattern": self.rng.choice(
                            ("sine", "lissajous", "orbit", "radial", "rose")
                        ),
                        "density": self.rng.randint(2, 9),
                        "amplitude": self.rng.uniform(0.08, 0.38),
                        "frequency": self.rng.uniform(0.8, 8.0),
                        "phase_offset": self.rng.uniform(0.0, 6.283),
                    })
                    updated = True
                elif self.settings.randomize_generators and kind == "particles":
                    values.update({
                        "density": self.rng.randint(16, 100),
                        "speed": self.rng.uniform(0.05, 0.8),
                        "size": self.rng.uniform(0.06, 0.36),
                        "spread": self.rng.uniform(0.15, 0.9),
                        "trail": self.rng.uniform(0.05, 0.65),
                        "mode": self.rng.choice(("drift", "rise", "fall", "orbit")),
                    })
                    updated = True

                if updated:
                    layer.generator_settings = normalize_settings(kind, values)
                    if self.generator_settings_changed is not None:
                        self.generator_settings_changed(layer)
                    changed += 1

            if (
                    self.settings.randomize_overlays
                    and layer.source_type == "overlay"
                    and time.time() >= float(getattr(layer, "overlay_manual_override_until", 0.0))
            ):
                layer.opacity = self.rng.uniform(0.82, 1.0)
                layer.scale = tuple(
                    max(0.05, min(2.0, value * self.rng.uniform(0.96, 1.04)))
                    for value in layer.scale
                )
                layer.rotation += self.rng.uniform(-2.5, 2.5)
                layer.blend_mode = self.rng.choice(("normal", "screen", "add", "multiply"))
                changed += 1

            if (
                    self.settings.randomize_layer_effects
                    and time.time() >= float(getattr(layer, "fx_manual_override_until", 0.0))
                    and layer.source_type in {"video", "generator", "overlay"}
            ):
                fx = layer.layer_effects if isinstance(layer.layer_effects, dict) else {}
                if fx.get("enabled", False):
                    preset_names = [name for name in LAYER_EFFECT_PRESETS if name != "Clean"]
                    layer.layer_effects = apply_layer_effect_preset(
                        self.rng.choice(preset_names)
                    )
                    changed += 1
        return changed

    def set_performance_context(
            self,
            energy: float,
            cutoff: float,
            intensity: float,
            bar_index: int = 0,
    ) -> None:
        """Refresh normalized musical context used by phrase-aware automation."""
        self._performance_energy = max(0.0, min(1.0, float(energy)))
        self._performance_cutoff = max(0.0, min(1.0, float(cutoff)))
        self._performance_intensity = max(0.0, min(1.0, float(intensity)))
        self._performance_bar_index = max(0, int(bar_index))

    @staticmethod
    def _scene_section(scene_id: str) -> str:
        if scene_id in {"in", "c", "end"}:
            return "intro" if scene_id == "in" else "outro"
        if scene_id in {"ssp", "intd", "trns", "rls"}:
            return "breakdown"
        if scene_id in {"peak", "rc_w", "s_s", "rc"}:
            return "peak"
        return "development"

    def on_musical_event(
            self,
            event: str,
            *,
            scene_id: str = "",
            intensity: float | None = None,
            energy: float | None = None,
            cutoff: float | None = None,
            bar_index: int | None = None,
            now: float | None = None,
    ) -> bool:
        """Make visual decisions on Sonic Pi bar, phrase and scene boundaries."""
        if not self.running:
            return False
        stamp = time.monotonic() if now is None else float(now)
        if intensity is not None:
            self._performance_intensity = max(0.0, min(1.0, float(intensity)))
        if energy is not None:
            self._performance_energy = max(0.0, min(1.0, float(energy)))
        if cutoff is not None:
            self._performance_cutoff = max(0.0, min(1.0, float(cutoff)))
        if bar_index is not None:
            self._performance_bar_index = max(0, int(bar_index))

        if event == "scene":
            self._performance_section = self._scene_section(scene_id)
            if scene_id == "end":
                self.running = False
                self.last_action = "SONATA end scene · automation stopped"
                return True
            if self.settings.musical_sync == "time":
                return False
        elif event == "bar":
            if self.settings.musical_sync not in {"bar", "hybrid"}:
                return False
        elif event == "phrase":
            if self.settings.musical_sync not in {"phrase", "hybrid"}:
                return False
        else:
            return False

        energy = self._performance_energy
        cutoff = self._performance_cutoff
        intensity = self._performance_intensity
        if self.settings.performance_style == "random":
            strength = 0.22 + 0.24 * energy + 0.20 * intensity
        elif self.settings.performance_style == "structured":
            section_scale = {
                "intro": 0.20,
                "development": 0.52,
                "peak": 0.88,
                "breakdown": 0.28,
                "outro": 0.12,
            }.get(self._performance_section, 0.4)
            strength = section_scale * (0.45 + 0.55 * max(energy, intensity))
        else:
            strength = 0.12 + 0.68 * max(energy, intensity)
        strength = max(0.05, min(0.94, strength))
        cutoff_drive = 0.65 + 0.7 * cutoff

        changed = False
        if event in {"scene", "phrase"} or (
                event == "bar" and self.settings.performance_style == "generative"
        ):
            if (
                    self.settings.randomize_layout
                    and (self._layout_due is None or stamp >= self._layout_due)
                    and self.rng.random() < min(0.98, strength * cutoff_drive)
            ):
                self._randomize_layout()
                self._layout_due = stamp + self._interval(
                    self.rng,
                    self.settings.min_layout_interval,
                    self.settings.max_layout_interval,
                )
                changed = True
            if (
                    self.settings.randomize_effects
                    and (self._effects_due is None or stamp >= self._effects_due)
                    and self.rng.random() < min(0.96, strength * (0.8 + 0.2 * energy))
            ):
                self._randomize_effects()
                self._effects_due = stamp + self._interval(
                    self.rng,
                    self.settings.min_effect_interval,
                    self.settings.max_effect_interval,
                )
                changed = True
            if (
                    (
                            self.settings.randomize_generators
                            or self.settings.randomize_palette
                            or self.settings.randomize_layer_effects
                            or self.settings.randomize_overlays
                    )
                    and (self._generators_due is None or stamp >= self._generators_due)
                    and self.rng.random() < min(0.98, strength * (0.75 + 0.25 * cutoff))
            ):
                changed = bool(self._randomize_generators()) or changed
                self._generators_due = stamp + self._interval(
                    self.rng,
                    self.settings.min_generator_interval,
                    self.settings.max_generator_interval,
                )

        if event == "phrase":
            self._trigger_phrase_cuts(
                stamp,
                min(0.95, strength * self.settings.clip_switch_probability),
            )
        elif event == "bar" and self.settings.performance_style == "generative":
            self._trigger_phrase_cuts(
                stamp,
                min(0.35, strength * self.settings.clip_switch_probability * 0.22),
            )

        self._last_musical_event_at = stamp
        section = (
            f"{self._performance_section} · "
            if self._performance_section != "idle" else ""
        )
        action = "musical variation" if changed else "musical cue evaluated"
        self.last_action = (
            f"{section}{action} · {event} · energy {energy:.2f} · "
            f"cutoff {cutoff:.2f} · intensity {intensity:.2f}"
        )
        return changed

    def _trigger_phrase_cuts(self, now: float, probability: float) -> None:
        if not self._assets:
            return
        for deck_id, deck in self._decks.items():
            if getattr(deck, "locked", False):
                continue
            due = self._deck_due.get(deck_id, 0.0)
            if now < due or self.rng.random() >= probability:
                continue
            self._load_random_segment(deck, getattr(deck, "asset_id", None), now)

    def tick(self, now: float | None = None) -> bool:

        if not self.running:
            return False
        current = time.monotonic() if now is None else float(now)
        if self.ends_at is not None and current >= self.ends_at:
            self.running = False
            self.last_action = "Automation session completed"
            return True

        changed = False
        run_time_events = self.settings.musical_sync in {"time", "hybrid"}
        if run_time_events:
            for deck_id, deck in self._decks.items():
                if getattr(deck, "locked", False):
                    continue
                due = self._deck_due.get(deck_id)
                if due is None:
                    self._deck_due[deck_id] = current + self._interval(
                        self.rng,
                        self.settings.min_cut_interval,
                        self.settings.max_cut_interval,
                    )
                    continue
                if current < due:
                    continue
                asset_id = getattr(deck, "asset_id", None)
                loaded = self._load_random_segment(deck, asset_id, current)
                if loaded:
                    self.last_action = f"Random cut · {deck_id.upper()}"
                changed = changed or loaded

        if (
                run_time_events
                and self.settings.randomize_layout
                and self._layout_due is not None
                and current >= self._layout_due
        ):
            self._randomize_layout()
            self._layout_due = current + self._interval(
                self.rng, self.settings.min_layout_interval, self.settings.max_layout_interval
            )
            self.last_action = "Collage layout changed"
            changed = True

        if (
                run_time_events
                and self.settings.randomize_effects
                and self._effects_due is not None
                and current >= self._effects_due
        ):
            self._randomize_effects()
            self._effects_due = current + self._interval(
                self.rng, self.settings.min_effect_interval, self.settings.max_effect_interval
            )
            self.last_action = f"Overlay look · {self._effects.preset_name}"
            changed = True

        if (
                run_time_events
                and (
                self.settings.randomize_generators
                or self.settings.randomize_palette
                or self.settings.randomize_layer_effects
                or self.settings.randomize_overlays
        )
                and self._generators_due is not None
                and current >= self._generators_due
        ):
            count = self._randomize_generators()
            self._generators_due = current + self._interval(
                self.rng, self.settings.min_generator_interval, self.settings.max_generator_interval
            )
            if count:
                self.last_action = f"Generators / text / layer FX varied · {count} change(s)"
                changed = True
        return changed

    def stop(self) -> None:
        self.running = False
        self.last_action = "Automation stopped"

    def remaining_seconds(self, now: float | None = None) -> float | None:
        if self.ends_at is None:
            return None
        current = time.monotonic() if now is None else float(now)
        return max(0.0, self.ends_at - current)
