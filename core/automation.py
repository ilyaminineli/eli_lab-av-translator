from __future__ import annotations

import logging
import math
import random
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from core.composition import Layer
from core.generative_director import GenerativeVariationDirector
from effects.layer_settings import LAYER_EFFECT_PRESETS, apply_layer_effect_preset
from effects.settings import PRESETS, EffectSettings
from generators.catalog import GENERATOR_TYPES, normalize_settings
from generators.palettes import palette_look, palette_names
from generators.text_pools import random_text_sample
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
    text_fragments: int = 8
    performance_style: str = "random"
    musical_sync: str = "time"
    # Compatibility fields for existing .eliset files. The director is always
    # active; this is now a soft variation preference, not an activation gate.
    constrained_generative: bool = True
    max_layers_per_variation: int = 0
    preserve_background_source: bool = False
    keep_visual_anchor: bool = False
    anchor_persistence: float = 0.0
    spatial_chaos: float = 0.82
    overlap_bias: float = 0.88
    offscreen_range: float = 0.55
    abrupt_transition_probability: float = 0.45
    layer_cooldown_seconds: float = 1.5
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
        # Legacy serialized flags remain readable, but can no longer disable
        # the director or restore the historical two-layer ceiling.
        self.constrained_generative = True
        self.max_layers_per_variation = 0
        self.preserve_background_source = bool(self.preserve_background_source)
        self.keep_visual_anchor = bool(self.keep_visual_anchor)
        self.anchor_persistence = max(0.0, min(1.0, float(self.anchor_persistence)))
        self.spatial_chaos = max(0.0, min(1.0, float(self.spatial_chaos)))
        self.overlap_bias = max(0.0, min(1.0, float(self.overlap_bias)))
        self.offscreen_range = max(0.0, min(1.0, float(self.offscreen_range)))
        self.abrupt_transition_probability = max(
            0.0, min(1.0, float(self.abrupt_transition_probability))
        )
        self.layer_cooldown_seconds = max(
            0.0, min(30.0, float(self.layer_cooldown_seconds))
        )
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
        self._peak_particle_base: dict[str, tuple[str, float, str]] = {}
        self._active_variation_layer_ids: tuple[str, ...] = ()
        self._layer_last_variation_at: dict[str, float] = {}
        self._manual_layer_until: dict[str, float] = {}
        self._last_layer_fx_variation = False
        self._last_peak_context = False
        self._director = GenerativeVariationDirector()
        self._last_layout_relationship = "independent"
        self._last_visual_activity = self._director.measure_visual_activity(())
        self._last_visual_activity_at = 0.0
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
        self._active_variation_layer_ids = ()
        self._layer_last_variation_at.clear()
        self._manual_layer_until.clear()
        self._last_layer_fx_variation = False
        self._last_peak_context = False
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
        if self.settings.randomize_effects and self.settings.effect_after_transition:
            self._director.mark_effect_applied()
        elif self.settings.randomize_effects:
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

    def update_layers(self, layers: list[Layer]) -> None:
        """Rebind after scene/project restore replaces the Composition object."""
        self._layers = layers
        valid_ids = {layer.id for layer in layers}
        self._layout_morphs = {
            layer_id: state
            for layer_id, state in self._layout_morphs.items()
            if layer_id in valid_ids
        }
        self._peak_particle_base = {
            layer_id: state
            for layer_id, state in self._peak_particle_base.items()
            if layer_id in valid_ids
        }
        self._active_variation_layer_ids = tuple(
            layer_id for layer_id in self._active_variation_layer_ids
            if layer_id in valid_ids
        )
        self._layer_last_variation_at = {
            layer_id: stamp
            for layer_id, stamp in self._layer_last_variation_at.items()
            if layer_id in valid_ids
        }
        self._manual_layer_until = {
            layer_id: stamp
            for layer_id, stamp in self._manual_layer_until.items()
            if layer_id in valid_ids
        }

    def notify_layer_manual_override(
            self,
            layer_id: str,
            duration_seconds: float = 3.0,
            now: float | None = None,
            *,
            invalidate_peak_particle_base: bool = False,
    ) -> None:
        """Suspend automatic changes after a direct operator edit."""
        stamp = time.monotonic() if now is None else float(now)
        duration = max(0.0, min(120.0, float(duration_seconds)))
        if duration <= 0.0:
            return
        self._manual_layer_until[layer_id] = max(
            self._manual_layer_until.get(layer_id, 0.0),
            stamp + duration,
        )
        self._layout_morphs.pop(layer_id, None)
        if invalidate_peak_particle_base:
            # Generator edits to particle density/emission supersede the cached
            # temporary peak baseline. Transform edits must retain that baseline.
            self._peak_particle_base.pop(layer_id, None)
        self._active_variation_layer_ids = tuple(
            item for item in self._active_variation_layer_ids if item != layer_id
        )

    def _is_manual_layer_override(self, layer_id: str, now: float) -> bool:
        deadline = self._manual_layer_until.get(layer_id, 0.0)
        if deadline <= now:
            self._manual_layer_until.pop(layer_id, None)
            return False
        return True

    def _effective_layer_cooldown(self) -> float:
        base = self.settings.layer_cooldown_seconds
        if base <= 0.0:
            return 0.0
        drive = max(
            self._performance_energy,
            self._performance_intensity,
            self._macro_values.get("chaos", self.settings.spatial_chaos),
            self._macro_values.get("density", 0.0),
            self._macro_values.get("fragment", 0.0),
            1.0 if self._performance_section == "peak" else 0.0,
        )
        # High musical pressure shortens the rest, but never removes it entirely.
        return max(0.12, base * (1.0 - 0.82 * min(1.0, drive)))

    def _mark_layer_varied(self, layer_id: str, now: float) -> None:
        self._layer_last_variation_at[layer_id] = float(now)

    def _eligible_variation_layers(self, now: float | None = None) -> list[Layer]:
        stamp = time.monotonic() if now is None else float(now)
        cooldown = self._effective_layer_cooldown()
        eligible: list[Layer] = []
        for layer in self._layers:
            if layer.locked or not layer.visible:
                continue
            if self._is_manual_layer_override(layer.id, stamp):
                continue
            last_change = self._layer_last_variation_at.get(layer.id)
            if cooldown > 0.0 and last_change is not None:
                if stamp - last_change < cooldown:
                    continue
            eligible.append(layer)
        return eligible

    def _variation_budget(
            self,
            strength: float | None = None,
            now: float | None = None,
            eligible_layers: list[Layer] | None = None,
    ) -> int:
        """Choose a dynamic scope from music, activity and cooldown-eligible layers."""
        candidates = (
            self._eligible_variation_layers(now)
            if eligible_layers is None else eligible_layers
        )
        eligible = len(candidates)
        if eligible <= 0:
            return 0
        chaos = self._macro_values.get("chaos", self.settings.spatial_chaos)
        fragment = self._macro_values.get("fragment", 0.0)
        density = self._macro_values.get("density", 0.0)
        musical_drive = max(
            self._performance_energy,
            self._performance_intensity,
            self._performance_cutoff * 0.55,
            float(strength or 0.0),
        )
        activity_now = time.monotonic()
        if activity_now - self._last_visual_activity_at >= 0.25:
            self._last_visual_activity = self._director.measure_visual_activity(self._layers)
            self._last_visual_activity_at = activity_now
        underactivity = 1.0 - self._last_visual_activity.score
        drive = max(
            0.0,
            min(
                1.0,
                0.30 * chaos
                + 0.21 * fragment
                + 0.19 * density
                + 0.17 * musical_drive
                + 0.13 * underactivity,
            ),
        )
        # At a genuinely maximal musical peak, allow a deterministic global event.
        # Outside that case, global bursts remain probabilistic and activity-aware.
        if self._performance_section == "peak" and drive >= 0.90:
            return eligible
        global_burst_probability = max(0.0, min(1.0, (drive - 0.72) / 0.28))
        if self.rng.random() < global_burst_probability:
            return eligible
        fraction = 0.25 + 0.75 * drive
        return min(eligible, max(1, round(eligible * fraction)))

    def visual_activity_snapshot(self) -> dict[str, object]:
        """Return the latest composition-only activity estimate for diagnostics/UI."""
        self._last_visual_activity = self._director.measure_visual_activity(self._layers)
        self._last_visual_activity_at = time.monotonic()
        return asdict(self._last_visual_activity)

    def _select_variation_layers(
            self,
            prefer_particles: bool = False,
            *,
            strength: float | None = None,
            now: float | None = None,
    ) -> tuple[str, ...]:
        candidates = self._eligible_variation_layers(now)
        budget = self._variation_budget(strength, now, candidates)
        return self._director.select_layers(
            candidates,
            budget,
            self.rng,
            keep_anchor=self.settings.keep_visual_anchor,
            prefer_particles=prefer_particles,
            anchor_persistence=self.settings.anchor_persistence,
        )

    def _choose_palette(self) -> str | None:
        selected = self._director.choose_palette(palette_names(), self.rng)
        if selected and callable(self.palette_changed):
            self.palette_changed(selected)
        return selected

    def _randomize_layout(
            self,
            layer_ids: Iterable[str] | None = None,
            now: float | None = None,
    ) -> int:
        # Every visible unlocked visual source participates, not only video.
        stamp = time.monotonic() if now is None else float(now)
        allowed = (
            set(layer_ids)
            if layer_ids is not None
            else set(self._select_variation_layers(now=stamp))
        )
        self._active_variation_layer_ids = tuple(allowed)
        anchor_id = self._director.choose_anchor(
            self._layers,
            enabled=self.settings.keep_visual_anchor or self.settings.preserve_background_source,
        )
        active = [
            layer for layer in self._layers
            if not layer.locked
            and layer.visible
            and layer.id in allowed
            and not (
                self.settings.preserve_background_source
                and layer.source_type == "video"
                and layer.id == anchor_id
            )
            and not self._is_manual_layer_override(layer.id, stamp)
            and not (
                layer.source_type == "overlay"
                and time.time() < float(
                    getattr(layer, "overlay_manual_override_until", 0.0)
                )
            )
        ]
        if not active:
            return 0
        patterns = [
            [(0.25, 0.25, 0.5), (0.75, 0.25, 0.5), (0.25, 0.75, 0.5), (0.75, 0.75, 0.5)],
            [(0.5, 0.5, 1.0), (0.78, 0.22, 0.28), (0.78, 0.78, 0.28), (0.22, 0.78, 0.28)],
            [(0.5, 0.17, 1.0), (0.5, 0.50, 1.0), (0.5, 0.83, 1.0), (0.5, 0.5, 0.45)],
            [(0.17, 0.5, 1.0), (0.50, 0.5, 1.0), (0.83, 0.5, 1.0), (0.5, 0.5, 0.45)],
            [(0.34, 0.34, 0.68), (0.68, 0.34, 0.42), (0.34, 0.68, 0.42), (0.72, 0.72, 0.34)],
            [(0.5, 0.5, 0.82), (0.5, 0.5, 0.62), (0.5, 0.5, 0.40), (0.5, 0.5, 0.22)],
        ]
        pattern = self.rng.choice(patterns)
        chaos = max(0.0, min(
            1.0, self._macro_values.get("chaos", self.settings.spatial_chaos)
        ))
        overlap = max(0.0, min(1.0, self.settings.overlap_bias))
        offscreen = max(0.0, min(1.0, self.settings.offscreen_range))
        use_seed = self.rng.random() > chaos * 0.78
        relationship = self.rng.choices(
            ("independent", "shared_center", "opposed", "nested", "orbit"),
            weights=(
                max(0.12, 1.0 - overlap),
                0.22 + overlap * 0.62,
                0.16 + overlap * 0.22,
                0.16 + overlap * 0.30,
                0.10 + overlap * 0.38,
            ),
            k=1,
        )[0]
        self._last_layout_relationship = relationship
        relationship_center = (
            self.rng.uniform(0.28, 0.72),
            self.rng.uniform(0.28, 0.72),
        )
        depth = self._macro_values.get("depth", 0.0)
        duration = self._director.transition_duration(
            self._performance_section,
            self.rng,
            slow_breakdowns=self.settings.slow_breakdown_transitions,
            normal_min=self.settings.layout_transition_min_seconds,
            normal_max=self.settings.layout_transition_max_seconds,
            breakdown_min=self.settings.breakdown_transition_min_seconds,
            breakdown_max=self.settings.breakdown_transition_max_seconds,
            depth=depth,
        )
        for index, layer in enumerate(active):
            # A new event supersedes an unfinished morph on that layer.
            self._layout_morphs.pop(layer.id, None)
            if use_seed:
                x, y, seed_size = pattern[index % len(pattern)]
                spread = 0.08 + chaos * 0.52
                target_x = x + self.rng.uniform(-spread, spread)
                target_y = y + self.rng.uniform(-spread, spread)
                target_scale = seed_size * self.rng.uniform(0.55, 1.75 + chaos * 2.0)
            else:
                # The director creates spatial relationships, not just independent
                # random transforms. High overlap bias favours shared visual masses.
                center_x, center_y = relationship_center
                cluster_spread = 0.05 + (1.0 - overlap) * 0.45
                if relationship == "shared_center":
                    target_x = center_x + self.rng.gauss(0.0, cluster_spread * 0.55)
                    target_y = center_y + self.rng.gauss(0.0, cluster_spread * 0.55)
                    target_scale = self.rng.uniform(0.42, 1.35 + chaos * 1.55)
                elif relationship == "opposed":
                    side = -1.0 if index % 2 else 1.0
                    offset = self.rng.uniform(0.08, 0.30 + chaos * 0.18)
                    target_x = center_x + side * offset
                    target_y = center_y + self.rng.gauss(0.0, cluster_spread * 0.65)
                    target_scale = self.rng.uniform(0.35, 1.25 + chaos * 1.55)
                elif relationship == "nested":
                    target_x = center_x + self.rng.gauss(0.0, cluster_spread * 0.25)
                    target_y = center_y + self.rng.gauss(0.0, cluster_spread * 0.25)
                    nesting = 1.0 - 0.62 * (index / max(1, len(active)))
                    target_scale = nesting * self.rng.uniform(0.62, 1.30 + chaos * 1.3)
                elif relationship == "orbit":
                    angle = (
                        2.0 * math.pi * index / max(1, len(active))
                        + self.rng.uniform(-0.28, 0.28)
                    )
                    radius = self.rng.uniform(0.12, 0.30 + chaos * 0.18)
                    target_x = center_x + math.cos(angle) * radius
                    target_y = center_y + math.sin(angle) * radius
                    target_scale = self.rng.uniform(0.32, 1.25 + chaos * 1.5)
                else:
                    target_x = self.rng.uniform(0.18, 0.82) + self.rng.gauss(
                        0.0, cluster_spread
                    )
                    target_y = self.rng.uniform(0.18, 0.82) + self.rng.gauss(
                        0.0, cluster_spread
                    )
                    target_scale = self.rng.uniform(0.28, 1.35 + chaos * 1.65)
            if self.rng.random() < offscreen * (0.08 + chaos * 0.48):
                target_x += self.rng.choice((-1.0, 1.0)) * self.rng.uniform(0.05, offscreen)
                target_y += self.rng.uniform(-0.35, 0.35) * offscreen
            target_position = (
                max(-offscreen, min(1.0 + offscreen, target_x)),
                max(-offscreen, min(1.0 + offscreen, target_y)),
            )
            target_scale = max(0.12, min(4.0, target_scale))
            rotation_range = 25.0 + chaos * 335.0
            target_rotation = self.rng.uniform(-rotation_range, rotation_range)
            target_opacity = self.rng.uniform(0.38, 1.0)
            target_blend = self.rng.choices(
                ("normal", "screen", "add", "multiply", "difference"),
                weights=(3, 2, 2, 1, 2),
                k=1,
            )[0]
            abrupt = (
                self.rng.random()
                < self.settings.abrupt_transition_probability * chaos
            )
            if not abrupt:
                self._layout_morphs[layer.id] = {
                    "started_at": stamp,
                    "duration": duration,
                    "start_position": tuple(layer.position),
                    "end_position": target_position,
                    "start_scale": float(layer.scale[0]),
                    "end_scale": target_scale,
                    "start_rotation": float(layer.rotation),
                    "end_rotation": target_rotation,
                    "start_opacity": float(layer.opacity),
                    "end_opacity": target_opacity,
                    "end_blend_mode": target_blend,
                }
            else:
                layer.position = target_position
                layer.scale = (target_scale, target_scale)
                layer.rotation = target_rotation
                layer.opacity = target_opacity
                layer.blend_mode = target_blend
            self._mark_layer_varied(layer.id, stamp)
        return len(active)

    def _tick_layout_transitions(self, now: float) -> bool:
        changed = False
        for layer_id, morph in tuple(self._layout_morphs.items()):
            layer = next(
                (item for item in self._layers if item.id == layer_id),
                None,
            )
            if layer is None:
                self._layout_morphs.pop(layer_id, None)
                continue
            duration = max(0.001, float(morph["duration"]))
            fraction = max(
                0.0,
                min(1.0, (float(now) - float(morph["started_at"])) / duration),
            )
            eased = fraction * fraction * (3.0 - 2.0 * fraction)
            start_x, start_y = morph["start_position"]
            end_x, end_y = morph["end_position"]
            layer.position = (
                float(start_x) + (float(end_x) - float(start_x)) * eased,
                float(start_y) + (float(end_y) - float(start_y)) * eased,
            )
            scale = float(morph["start_scale"]) + (
                    float(morph["end_scale"]) - float(morph["start_scale"])
            ) * eased
            layer.scale = (scale, scale)
            layer.rotation = float(morph["start_rotation"]) + (
                    float(morph["end_rotation"]) - float(morph["start_rotation"])
            ) * eased
            layer.opacity = float(morph["start_opacity"]) + (
                    float(morph["end_opacity"]) - float(morph["start_opacity"])
            ) * eased
            if fraction >= 1.0:
                layer.blend_mode = str(morph["end_blend_mode"])
                self._layout_morphs.pop(layer_id, None)
                self._director.mark_transition()
            changed = True
        return changed

    def _apply_peak_particle_density(
            self,
            layer_ids: Iterable[str] | None,
    ) -> bool:
        allowed = set(layer_ids) if layer_ids is not None else set()
        factor = self._director.particle_peak_factor(
            self._performance_section,
            self._performance_energy,
            self._performance_intensity,
            self._macro_values.get("density", 0.0),
            self.settings.peak_particle_boost,
        )
        changed = False
        for layer in self._layers:
            if self._is_manual_layer_override(layer.id, time.monotonic()):
                # Pause automatic particle modulation during the manual-edit window.
                # Keep the baseline unless the generator parameter itself was edited.
                continue
            stored = self._peak_particle_base.get(layer.id)
            kind = str(layer.generator_type or "")
            if stored is not None and (
                    layer.id not in allowed
                    or layer.locked
                    or layer.source_type != "generator"
                    or kind not in {"particles", "particle_system_2"}
                    or factor <= 1.0
                    or stored[2] != kind
            ):
                field, base_value, stored_kind = stored
                if layer.source_type == "generator" and kind == stored_kind:
                    values = normalize_settings(kind, layer.generator_settings)
                    values[field] = base_value
                    layer.generator_settings = normalize_settings(kind, values)
                    if self.generator_settings_changed is not None:
                        self.generator_settings_changed(layer)
                self._peak_particle_base.pop(layer.id, None)
                changed = True
            if (
                    layer.id not in allowed
                    or layer.locked
                    or layer.source_type != "generator"
                    or kind not in {"particles", "particle_system_2"}
                    or factor <= 1.0
            ):
                continue
            field = "density" if kind == "particles" else "emission_rate"
            values = normalize_settings(kind, layer.generator_settings)
            if layer.id not in self._peak_particle_base:
                self._peak_particle_base[layer.id] = (
                    field,
                    float(values[field]),
                    kind,
                )
            base_field, base_value, _stored_kind = self._peak_particle_base[layer.id]
            desired = base_value * factor
            if abs(float(values[base_field]) - desired) < 1e-4:
                continue
            values[base_field] = desired
            layer.generator_settings = normalize_settings(kind, values)
            if self.generator_settings_changed is not None:
                self.generator_settings_changed(layer)
            changed = True
        return changed

    def _randomize_effects(self) -> None:
        if self._effects is None:
            return
        names = [name for name in PRESETS if name != "Clean"]
        self._effects.apply_preset(self.rng.choice(names))
        self._director.mark_effect_applied()

    def _randomize_generators(
            self,
            layer_ids: Iterable[str] | None = None,
            *,
            allow_effect_change: bool = True,
            now: float | None = None,
    ) -> int:
        changed = 0
        variation_now = time.monotonic() if now is None else float(now)
        self._last_layer_fx_variation = False
        allowed = set(layer_ids) if layer_ids is not None else None
        if allowed is None:
            allowed = set(self._select_variation_layers())
        chaos = self._macro_values.get("chaos", self.settings.spatial_chaos)
        density_macro = self._macro_values.get("density", 0.0)
        decay = self._macro_values.get("decay", 0.0)
        fragment = self._macro_values.get("fragment", 0.0)
        palette_name = None
        palette_values = None
        if self.settings.randomize_palette:
            palette_name = self._choose_palette()
            if palette_name:
                palette_values = palette_look(palette_name)

        for layer in self._layers:
            if (
                    layer.locked
                    or not layer.visible
                    or (allowed is not None and layer.id not in allowed)
                    or self._is_manual_layer_override(layer.id, variation_now)
            ):
                continue
            changed_before_layer = changed

            if layer.source_type == "generator" and layer.generator_type in GENERATOR_TYPES:
                kind = layer.generator_type
                values = normalize_settings(kind, layer.generator_settings)
                updated = False
                if palette_values is not None:
                    values.update({
                        key: palette_values[key]
                        for key in ("primary_color", "secondary_color", "background_color")
                    })
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
                    text_modes = (
                        "type_on", "word_reveal", "line_wave", "jitter", "crawl", "glitch",
                        "reverse_typewriter", "dissolve", "flicker", "character_displacement",
                        "vertical_reveal", "scattered_glyphs", "word_collisions",
                        "mechanical_scroll",
                    )
                    if fragment >= 0.55:
                        text_modes = (
                            "jitter", "glitch", "character_displacement",
                            "scattered_glyphs", "word_collisions", "dissolve",
                        )
                    values.update({
                        "text_animation": self.rng.choice(text_modes),
                        "text_animation_speed": self.rng.uniform(
                            0.35, 2.8 + chaos * 2.0
                        ),
                        "text_animation_amount": self.rng.uniform(
                            0.015, min(0.18, 0.12 + fragment * 0.06)
                        ),
                    })
                    if self.rng.random() < 0.25:
                        values["text_writing_mode"] = self.rng.choice(
                            ("horizontal", "vertical_rl", "vertical_lr")
                        )
                    if self.rng.random() < 0.25:
                        values["text_path_mode"] = self.rng.choice(
                            ("none", "circle", "arc", "custom")
                        )
                    updated = True
                elif self.settings.randomize_generators and kind == "geometry":
                    motion = self.rng.choice(("rotate", "pulse", "drift", "warp"))
                    motion_ranges = {
                        "rotate": (20.0, 100.0 + 100.0 * chaos),
                        "pulse": (0.04, 0.22 + 0.12 * chaos),
                        "drift": (0.015, 0.07 + 0.08 * chaos),
                        "warp": (0.08, 0.42 + 0.18 * chaos),
                    }
                    density_high = min(80, 34 + int(density_macro * 30))
                    values.update({
                        "pattern": self.rng.choice(
                            ("rings", "grid", "radial", "crosshatch", "spiral", "moire", "hexgrid")
                        ),
                        "density": self.rng.randint(6, max(6, density_high)),
                        "rotation": self.rng.uniform(-35.0, 35.0) * (1.0 + chaos),
                        "animation": motion,
                        "animation_speed": self.rng.uniform(0.08, 1.8 + chaos * 2.0),
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
                        "frequency": self.rng.uniform(0.8, 8.0 + chaos * 5.0),
                        "phase_offset": self.rng.uniform(0.0, 6.283),
                    })
                    updated = True
                elif self.settings.randomize_generators and kind == "particles":
                    values.update({
                        "density": self.rng.randint(16, 100),
                        "speed": self.rng.uniform(0.05, 0.8 + chaos * 0.55),
                        "size": self.rng.uniform(0.06, 0.36),
                        "spread": self.rng.uniform(0.15, 0.9),
                        "trail": self.rng.uniform(0.05, min(1.0, 0.65 + decay * 0.3)),
                        "mode": self.rng.choice(("drift", "rise", "fall", "orbit")),
                    })
                    updated = True
                elif self.settings.randomize_generators and kind == "particle_system_2":
                    values.update({
                        "emission_rate": self.rng.uniform(240.0, 1200.0),
                        "population_count": self.rng.choice((1, 2, 2, 3, 4)),
                        "emitter_type": self.rng.choice(("point", "circle", "rectangle", "path")),
                        "direction": self.rng.choice(
                            ("radial", "random", "up", "down", "left", "right", "tangent")
                        ),
                        "lifetime": self.rng.uniform(2.5, 12.0 + decay * 18.0),
                        "speed": self.rng.uniform(0.06, 0.72 + chaos * 0.65),
                        "spread": self.rng.uniform(0.12, 1.5),
                        "turbulence": self.rng.uniform(0.02, 0.8 + chaos * 0.7),
                        "force_type": self.rng.choice(("none", "attract", "repel", "orbit")),
                        "force_strength": self.rng.uniform(0.0, 2.2 + chaos * 1.2),
                        "drag": self.rng.uniform(0.02, 0.65 + decay * 0.8),
                        "trail": self.rng.uniform(0.2, min(1.0, 0.76 + decay * 0.24)),
                        "particle_size": self.rng.uniform(2.0, 16.0),
                        "size_curve": self.rng.choice(("constant", "grow", "shrink", "pulse")),
                        "reform_strength": self.rng.uniform(0.0, 0.8),
                    })
                    updated = True

                if updated:
                    layer.generator_settings = normalize_settings(kind, values)
                    if kind in {"particles", "particle_system_2"}:
                        field = "density" if kind == "particles" else "emission_rate"
                        if layer.id in self._peak_particle_base:
                            self._peak_particle_base[layer.id] = (
                                field,
                                float(layer.generator_settings[field]),
                                kind,
                            )
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
                    and allow_effect_change
                    and time.time() >= float(getattr(layer, "fx_manual_override_until", 0.0))
                    and layer.source_type in {"video", "generator", "overlay"}
            ):
                fx = layer.layer_effects if isinstance(layer.layer_effects, dict) else {}
                if fx.get("enabled", False):
                    preset_names = [name for name in LAYER_EFFECT_PRESETS if name != "Clean"]
                    layer.layer_effects = apply_layer_effect_preset(
                        self.rng.choice(preset_names)
                    )
                    self._last_layer_fx_variation = True
                    changed += 1

            if changed > changed_before_layer:
                self._mark_layer_varied(layer.id, variation_now)
        return changed

    def set_performance_context(
            self,
            energy: float,
            cutoff: float,
            intensity: float,
            bar_index: int = 0,
            macro_values: dict[str, float] | None = None,
    ) -> None:
        """Refresh normalized musical and Performance Macro context."""
        self._performance_energy = max(0.0, min(1.0, float(energy)))
        self._performance_cutoff = max(0.0, min(1.0, float(cutoff)))
        self._performance_intensity = max(0.0, min(1.0, float(intensity)))
        self._performance_bar_index = max(0, int(bar_index))
        if macro_values is not None:
            self._macro_values = {
                str(name): max(0.0, min(1.0, float(value)))
                for name, value in macro_values.items()
                if isinstance(value, (int, float))
            }

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
            macro_values: dict[str, float] | None = None,
            now: float | None = None,
    ) -> bool:
        """Apply a musical cue through the unified visual director."""
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
        if macro_values is not None:
            self.set_performance_context(
                self._performance_energy,
                self._performance_cutoff,
                self._performance_intensity,
                self._performance_bar_index,
                macro_values,
            )

        if event == "phrase":
            self._director.advance_phrase()

        if event == "scene":
            next_section = self._scene_section(scene_id)
            if scene_id and scene_id != self._last_scene_id:
                self._director.mark_transition()
            self._last_scene_id = scene_id
            self._performance_section = next_section
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
        chaos = self._macro_values.get("chaos", 0.0)
        pressure = self._macro_values.get("pressure", 0.0)
        density = self._macro_values.get("density", 0.0)
        section_scale = {
            "intro": 0.46,
            "development": 0.68,
            "peak": 0.96,
            "breakdown": 0.38,
            "outro": 0.30,
        }.get(self._performance_section, 0.58)
        style_bias = {
            "random": 0.88,
            "structured": 0.78,
            "generative": 1.0,
        }.get(self.settings.performance_style, 1.0)
        strength = (
            0.16 + 0.44 * max(energy, intensity) + 0.25 * section_scale
            + 0.15 * self._macro_values.get("density", 0.0)
        ) * style_bias
        strength *= 1.0 + 0.22 * chaos + 0.12 * pressure
        strength = max(0.05, min(0.98, strength))
        cutoff_drive = 0.65 + 0.7 * cutoff + 0.12 * self._macro_values.get("fragment", 0.0)

        peak_context = (
                self._performance_section == "peak"
                or energy >= 0.78
                or intensity >= 0.82
        )
        variation_layer_ids = self._select_variation_layers(
            prefer_particles=peak_context,
            strength=strength,
            now=stamp,
        )
        self._active_variation_layer_ids = tuple(variation_layer_ids)
        allow_effect_change = (
            not self.settings.effect_after_transition
            or self._director.effect_ready()
        )
        changed = False
        # Every director character participates at phrase/bar/scene boundaries.
        # The style only biases the probability and intensity, never bypasses the director.
        allow_variations = event in {"scene", "phrase", "bar"}
        if allow_variations:
            if (
                    self.settings.randomize_layout
                    and (self._layout_due is None or stamp >= self._layout_due)
                    and self.rng.random() < min(0.98, strength * cutoff_drive)
            ):
                changed = bool(
                    self._randomize_layout(variation_layer_ids, now=stamp)
                ) or changed
                self._layout_due = stamp + self._interval(
                    self.rng,
                    self.settings.min_layout_interval,
                    self.settings.max_layout_interval,
                )

            if (
                    self.settings.randomize_effects
                    and (self._effects_due is None or stamp >= self._effects_due)
                    and allow_effect_change
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
                    and self.rng.random() < min(
                0.98, strength * (0.75 + 0.25 * cutoff + density * 0.12)
            )
            ):
                count = self._randomize_generators(
                    variation_layer_ids,
                    allow_effect_change=allow_effect_change,
                    now=stamp,
                )
                if (
                        allow_effect_change
                        and getattr(self, "_last_layer_fx_variation", False)
                ):
                    self._director.mark_effect_applied()
                changed = bool(count) or changed
                self._generators_due = stamp + self._interval(
                    self.rng,
                    self.settings.min_generator_interval,
                    self.settings.max_generator_interval,
                )

            changed = self._apply_peak_particle_density(
                variation_layer_ids
            ) or changed

        if event == "phrase":
            cut_probability = min(
                0.95,
                strength * self.settings.clip_switch_probability
                * (1.0 - 0.25 * self._macro_values.get("decay", 0.0)),
            )
            changed = self._trigger_phrase_cuts(
                stamp,
                cut_probability,
                variation_layer_ids,
            ) or changed
        elif event == "bar":
            changed = self._trigger_phrase_cuts(
                stamp,
                min(0.35, strength * self.settings.clip_switch_probability * 0.22),
                variation_layer_ids,
            ) or changed

        self._last_musical_event_at = stamp
        section = (
            f"{self._performance_section} · "
            if self._performance_section != "idle" else ""
        )
        action = "generative variation" if changed else "musical cue evaluated"
        anchor = (
            f" · anchor {self._director.anchor_layer_id}"
            if self.settings.keep_visual_anchor and self._director.anchor_layer_id else ""
        )
        self.last_action = (
            f"{section}{action} · {event} · energy {energy:.2f} · "
            f"cutoff {cutoff:.2f} · intensity {intensity:.2f}{anchor}"
        )
        return changed

    def _trigger_phrase_cuts(
            self,
            now: float,
            probability: float,
            layer_ids: Iterable[str] | None = None,
    ) -> bool:
        if not self._assets:
            return False
        allowed = set(layer_ids) if layer_ids is not None else None
        video_layers = {
            layer.source_id: layer
            for layer in self._layers
            if layer.source_type == "video"
        }
        anchor_id = self._director.choose_anchor(
            self._layers,
            enabled=self.settings.keep_visual_anchor or self.settings.preserve_background_source,
        )
        changed = False
        for deck_id, deck in self._decks.items():
            if getattr(deck, "locked", False):
                continue
            layer = video_layers.get(deck_id)
            if layer is None or self._is_manual_layer_override(layer.id, now):
                continue
            if allowed is not None and (
                    layer is None or layer.id not in allowed
            ):
                continue
            if (
                    self.settings.preserve_background_source
                    and layer is not None
                    and layer.id == anchor_id
            ):
                continue
            due = self._deck_due.get(deck_id, 0.0)
            if now < due or self.rng.random() >= probability:
                continue
            loaded = self._load_random_segment(
                deck,
                getattr(deck, "asset_id", None),
                now,
            )
            if loaded:
                self._director.mark_transition()
                self._mark_layer_varied(layer.id, now)
                changed = True
        return changed

    def tick(self, now: float | None = None) -> bool:
        """Advance the unified director once, independent of the sync source."""
        if not self.running:
            return False
        current = time.monotonic() if now is None else float(now)
        if self.ends_at is not None and current >= self.ends_at:
            self.running = False
            self.last_action = "Automation session completed"
            return True

        changed = self._tick_layout_transitions(current)
        if self.settings.musical_sync in {"time", "hybrid"}:
            changed = self._tick_unified_time_events(current) or changed
        else:
            # Musical modes are event-driven; retain bounded section/peak response
            # between phrase/bar/scene cues without running a second scheduler.
            selected = self._select_variation_layers(
                prefer_particles=(
                    self._performance_section == "peak"
                    or self._performance_energy >= 0.78
                )
            )
            changed = self._apply_peak_particle_density(selected) or changed
        return changed

    def _tick_unified_time_events(self, current: float) -> bool:
        """Run interval-driven actions through the same musical variation director."""
        peak_context = (
            self._performance_section == "peak"
            or self._performance_energy >= 0.78
            or self._performance_intensity >= 0.82
            or self._macro_values.get("density", 0.0) >= 0.78
        )
        strength = (
            0.16
            + 0.44 * max(self._performance_energy, self._performance_intensity)
            + 0.25 * {
                "intro": 0.46,
                "development": 0.68,
                "peak": 0.96,
                "breakdown": 0.38,
                "outro": 0.30,
            }.get(self._performance_section, 0.58)
            + 0.15 * self._macro_values.get("density", 0.0)
        )
        strength *= 1.0 + (
            0.22 * self._macro_values.get("chaos", self.settings.spatial_chaos)
            + 0.12 * self._macro_values.get("pressure", 0.0)
        )
        strength = max(0.05, min(0.98, strength))

        # Initialise per-deck timers lazily. Each eligible deck remains independent.
        due_decks: list[str] = []
        for deck_id, deck in self._decks.items():
            if getattr(deck, "locked", False):
                continue
            if deck_id not in self._deck_due:
                self._deck_due[deck_id] = current + self._interval(
                    self.rng,
                    self.settings.min_cut_interval,
                    self.settings.max_cut_interval,
                )
            elif current >= self._deck_due[deck_id]:
                due_decks.append(deck_id)

        layout_due = (
            self.settings.randomize_layout
            and self._layout_due is not None
            and current >= self._layout_due
        )
        effects_due = (
            self.settings.randomize_effects
            and self._effects_due is not None
            and current >= self._effects_due
        )
        generators_due = (
            (
                self.settings.randomize_generators
                or self.settings.randomize_palette
                or self.settings.randomize_layer_effects
                or self.settings.randomize_overlays
            )
            and self._generators_due is not None
            and current >= self._generators_due
        )

        budget = self._select_variation_layers(
            prefer_particles=peak_context,
            strength=strength,
            now=current,
        )
        allowed = set(budget)
        self._active_variation_layer_ids = tuple(budget)
        video_layers = {
            layer.source_id: layer
            for layer in self._layers
            if layer.source_type == "video"
        }
        anchor_id = self._director.choose_anchor(
            self._layers,
            enabled=(
                self.settings.keep_visual_anchor
                or self.settings.preserve_background_source
            ),
        )

        changed = False
        transition_happened = False
        for deck_id in due_decks:
            deck = self._decks[deck_id]
            layer = video_layers.get(deck_id)
            if layer is None or layer.id not in allowed:
                self._deck_due[deck_id] = current + self._interval(
                    self.rng,
                    self.settings.min_cut_interval,
                    self.settings.max_cut_interval,
                )
                continue
            if (
                self.settings.preserve_background_source
                and layer.id == anchor_id
            ):
                self._deck_due[deck_id] = current + self._interval(
                    self.rng,
                    self.settings.min_cut_interval,
                    self.settings.max_cut_interval,
                )
                continue
            if self.rng.random() < min(
                0.98,
                strength * self.settings.clip_switch_probability,
            ):
                loaded = self._load_random_segment(
                    deck,
                    getattr(deck, "asset_id", None),
                    current,
                )
                if loaded:
                    self._director.mark_transition()
                    self._mark_layer_varied(layer.id, current)
                    transition_happened = True
                    changed = True
            self._deck_due[deck_id] = current + self._interval(
                self.rng,
                self.settings.min_cut_interval,
                self.settings.max_cut_interval,
            )

        if layout_due:
            layout_count = self._randomize_layout(budget, now=current)
            changed = bool(layout_count) or changed
            transition_happened = transition_happened or bool(layout_count)
            self._layout_due = current + self._interval(
                self.rng,
                self.settings.min_layout_interval,
                self.settings.max_layout_interval,
            )

        effect_ready = (
            not self.settings.effect_after_transition
            or self._director.effect_ready()
        )
        if effects_due and effect_ready:
            self._randomize_effects()
            self._effects_due = current + self._interval(
                self.rng,
                self.settings.min_effect_interval,
                self.settings.max_effect_interval,
            )
            changed = True

        if generators_due:
            count = self._randomize_generators(
                budget,
                allow_effect_change=effect_ready,
                now=current,
            )
            if effect_ready and self._last_layer_fx_variation:
                self._director.mark_effect_applied()
            self._generators_due = current + self._interval(
                self.rng,
                self.settings.min_generator_interval,
                self.settings.max_generator_interval,
            )
            changed = bool(count) or changed

        changed = self._apply_peak_particle_density(budget) or changed
        if transition_happened:
            self.last_action = (
                f"unified variation · {self._performance_section} · "
                f"{len(budget)} varied layer(s)"
            )
        elif changed:
            self.last_action = f"visual variation · {len(budget)} eligible layer(s)"
        return changed

    def _tick_constrained_generative(self, current: float) -> bool:
        """Compatibility wrapper for older internal call sites."""
        return self._tick_unified_time_events(current)

    def stop(self) -> None:
        """Finish active morphs and restore temporary peak-only particle boosts."""
        for layer_id, morph in tuple(self._layout_morphs.items()):
            layer = next(
                (item for item in self._layers if item.id == layer_id),
                None,
            )
            if layer is None:
                continue
            end_x, end_y = morph["end_position"]
            layer.position = (float(end_x), float(end_y))
            scale = float(morph["end_scale"])
            layer.scale = (scale, scale)
            layer.rotation = float(morph["end_rotation"])
            layer.opacity = float(morph["end_opacity"])
            layer.blend_mode = str(morph["end_blend_mode"])
        self._layout_morphs.clear()
        for layer_id, (field, base_value, kind) in tuple(
                self._peak_particle_base.items()
        ):
            layer = next(
                (item for item in self._layers if item.id == layer_id),
                None,
            )
            if layer is None or layer.source_type != "generator" or layer.generator_type != kind:
                continue
            values = normalize_settings(kind, layer.generator_settings)
            values[field] = base_value
            layer.generator_settings = normalize_settings(kind, values)
            if self.generator_settings_changed is not None:
                self.generator_settings_changed(layer)
        self._peak_particle_base.clear()
        self._active_variation_layer_ids = ()
        self.running = False
        self.last_action = "Automation stopped"

    def remaining_seconds(self, now: float | None = None) -> float | None:
        if self.ends_at is None:
            return None
        current = time.monotonic() if now is None else float(now)
        return max(0.0, self.ends_at - current)
