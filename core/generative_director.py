from __future__ import annotations

import math
import random
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class VisualActivity:
    """Composition-only estimate used by the director to avoid blind randomization."""

    layer_count: int
    overlap: float
    transform: float
    offscreen: float
    source_diversity: float
    score: float

    @classmethod
    def measure(cls, layers: Iterable[object]) -> "VisualActivity":
        eligible = [
            layer for layer in layers
            if bool(getattr(layer, "visible", True))
            and not bool(getattr(layer, "locked", False))
        ]
        if not eligible:
            return cls(0, 0.0, 0.0, 0.0, 0.0, 0.0)

        boxes: list[tuple[float, float, float, float, float]] = []
        transform_values: list[float] = []
        source_kinds: set[str] = set()
        offscreen_values: list[float] = []

        for layer in eligible:
            position = getattr(layer, "position", (0.5, 0.5))
            scale = getattr(layer, "scale", (1.0, 1.0))
            center_x = float(position[0])
            center_y = float(position[1])
            scale_x = max(0.001, abs(float(scale[0])))
            scale_y = max(0.001, abs(float(scale[1])))
            rotation = math.radians(float(getattr(layer, "rotation", 0.0)))
            cosine = abs(math.cos(rotation))
            sine = abs(math.sin(rotation))
            width = max(0.001, scale_x * cosine + scale_y * sine)
            height = max(0.001, scale_y * cosine + scale_x * sine)
            left = center_x - width * 0.5
            top = center_y - height * 0.5
            right = center_x + width * 0.5
            bottom = center_y + height * 0.5
            area = width * height
            boxes.append((left, top, right, bottom, area))

            scale_activity = min(
                1.0,
                0.5 * (
                    abs(math.log(scale_x)) + abs(math.log(scale_y))
                ) / math.log(4.0),
            )
            rotation_activity = min(1.0, abs(float(getattr(layer, "rotation", 0.0))) / 180.0)
            translation_activity = min(
                1.0,
                math.hypot(center_x - 0.5, center_y - 0.5) / math.sqrt(0.5),
            )
            transform_values.append(
                0.35 * scale_activity
                + 0.40 * rotation_activity
                + 0.25 * translation_activity
            )

            source_type = str(getattr(layer, "source_type", "unknown"))
            generator_type = str(getattr(layer, "generator_type", "") or "")
            source_kinds.add(
                f"generator:{generator_type}" if source_type == "generator" else source_type
            )

            visible_width = max(0.0, min(1.0, right) - max(0.0, left))
            visible_height = max(0.0, min(1.0, bottom) - max(0.0, top))
            visible_area = visible_width * visible_height
            offscreen_values.append(
                max(0.0, min(1.0, 1.0 - visible_area / max(area, 0.001)))
            )

        overlap_values: list[float] = []
        for index, first in enumerate(boxes):
            for second in boxes[index + 1:]:
                intersection_width = max(
                    0.0,
                    min(first[2], second[2]) - max(first[0], second[0]),
                )
                intersection_height = max(
                    0.0,
                    min(first[3], second[3]) - max(first[1], second[1]),
                )
                intersection = intersection_width * intersection_height
                if intersection > 0.0:
                    smaller_area = max(0.001, min(first[4], second[4]))
                    overlap_values.append(
                        max(0.0, min(1.0, intersection / smaller_area))
                    )

        overlap = sum(overlap_values) / len(overlap_values) if overlap_values else 0.0
        transform = sum(transform_values) / len(transform_values)
        offscreen = sum(offscreen_values) / len(offscreen_values)
        source_diversity = min(1.0, len(source_kinds) / 5.0)
        layer_density = min(1.0, len(eligible) / 8.0)
        score = max(
            0.0,
            min(
                1.0,
                0.33 * overlap
                + 0.25 * transform
                + 0.18 * layer_density
                + 0.14 * source_diversity
                + 0.10 * offscreen,
            ),
        )
        return cls(
            layer_count=len(eligible),
            overlap=overlap,
            transform=transform,
            offscreen=offscreen,
            source_diversity=source_diversity,
            score=score,
        )


class GenerativeVariationDirector:
    """Musical visual director: composition memory, variation selection and pacing."""

    def __init__(self, palette_memory_phrases: int = 4) -> None:
        self.palette_memory_phrases = max(0, min(16, int(palette_memory_phrases)))
        self._palette_history: deque[tuple[int, str]] = deque()
        self._phrase_index = 0
        self._anchor_layer_id: str | None = None
        self._transition_revision = 0
        self._effect_transition_revision = 0

    @staticmethod
    def _eligible(layer: object) -> bool:
        return bool(getattr(layer, "visible", True)) and not bool(
            getattr(layer, "locked", False)
        )

    @staticmethod
    def measure_visual_activity(layers: Iterable[object]) -> VisualActivity:
        """Estimate composition density, overlap, transform and off-canvas activity."""
        return VisualActivity.measure(layers)

    def reset(self, palette_memory_phrases: int | None = None) -> None:
        if palette_memory_phrases is not None:
            self.palette_memory_phrases = max(
                0, min(16, int(palette_memory_phrases))
            )
        self._palette_history.clear()
        self._phrase_index = 0
        self._anchor_layer_id = None
        self._transition_revision = 0
        self._effect_transition_revision = 0

    @property
    def anchor_layer_id(self) -> str | None:
        return self._anchor_layer_id

    @property
    def palette_history(self) -> tuple[str, ...]:
        return tuple(self._palette_history)

    @property
    def transition_revision(self) -> int:
        return self._transition_revision

    def choose_anchor(self, layers: Iterable[object], enabled: bool = True) -> str | None:
        candidates = [layer for layer in layers if self._eligible(layer)]
        current = next(
            (
                layer for layer in candidates
                if str(getattr(layer, "id", "")) == self._anchor_layer_id
            ),
            None,
        )
        if current is not None:
            return self._anchor_layer_id
        self._anchor_layer_id = None
        if not enabled or not candidates:
            return None

        # The lowest video layer is treated as the background source. If no
        # footage is present, prefer authored text, then overlays, then any layer.
        priorities = {
            "video": 0,
            "generator:text": 1,
            "overlay": 2,
        }

        def priority(layer: object) -> tuple[int, int, str]:
            source_type = str(getattr(layer, "source_type", ""))
            generator_type = str(getattr(layer, "generator_type", "") or "")
            key = (
                "generator:text"
                if source_type == "generator" and generator_type == "text"
                else source_type
            )
            return (
                priorities.get(key, 3),
                int(getattr(layer, "z_index", 0)),
                str(getattr(layer, "id", "")),
            )

        anchor = min(candidates, key=priority)
        self._anchor_layer_id = str(getattr(anchor, "id", "")) or None
        return self._anchor_layer_id

    def select_layers(
            self,
            layers: Iterable[object],
            maximum: int,
            rng: random.Random,
            *,
            keep_anchor: bool = False,
            prefer_particles: bool = False,
            anchor_persistence: float = 0.0,
    ) -> tuple[str, ...]:
        candidates = [
            layer for layer in layers
            if self._eligible(layer)
        ]
        anchor_id = self.choose_anchor(
            candidates,
            enabled=keep_anchor or anchor_persistence > 0.0,
        )
        if anchor_id:
            persistence = max(0.0, min(1.0, float(anchor_persistence)))
            if keep_anchor or rng.random() < persistence:
                candidates = [
                    layer for layer in candidates
                    if str(getattr(layer, "id", "")) != anchor_id
                ]
        rng.shuffle(candidates)
        if prefer_particles:
            particle_layers = [
                layer for layer in candidates
                if (
                        getattr(layer, "source_type", "") == "generator"
                        and getattr(layer, "generator_type", "")
                        in {"particles", "particle_system_2"}
                )
            ]
            particle_ids = {
                str(getattr(layer, "id", "")) for layer in particle_layers
            }
            candidates = particle_layers + [
                layer for layer in candidates
                if str(getattr(layer, "id", "")) not in particle_ids
            ]
        limit = max(0, min(len(candidates), int(maximum)))
        return tuple(
            str(getattr(layer, "id", ""))
            for layer in candidates[:limit]
            if str(getattr(layer, "id", ""))
        )

    def advance_phrase(self) -> int:
        """Advance phrase memory; palette reuse is measured in phrases, not changes."""
        self._phrase_index += 1
        cutoff = self._phrase_index - self.palette_memory_phrases
        while self._palette_history and self._palette_history[0][0] < cutoff:
            self._palette_history.popleft()
        return self._phrase_index

    def choose_palette(self, palette_names: Iterable[str], rng: random.Random) -> str | None:
        names = tuple(str(name) for name in palette_names if str(name))
        if not names:
            return None
        recent = {
            palette
            for phrase, palette in self._palette_history
            if self._phrase_index - phrase < self.palette_memory_phrases
        }
        available = [name for name in names if name not in recent]
        selected = rng.choice(available or list(names))
        if self.palette_memory_phrases > 0:
            if self._palette_history and self._palette_history[-1][0] == self._phrase_index:
                self._palette_history[-1] = (self._phrase_index, selected)
            else:
                self._palette_history.append((self._phrase_index, selected))
        return selected

    def mark_transition(self) -> int:
        self._transition_revision += 1
        return self._transition_revision

    def effect_ready(self, enabled: bool = True) -> bool:
        return bool(enabled) and (
                self._transition_revision > self._effect_transition_revision
        )

    def mark_effect_applied(self) -> None:
        self._effect_transition_revision = self._transition_revision

    @staticmethod
    def particle_peak_factor(
            section: str,
            energy: float,
            intensity: float,
            density_macro: float = 0.0,
            boost: float = 0.35,
    ) -> float:
        """Return a bounded multiplier for particle density/emission at peaks."""
        drive = max(float(energy), float(intensity), float(density_macro))
        if section != "peak" and drive < 0.78:
            return 1.0
        peak = max(
            0.78 if section == "peak" else 0.0,
            0.0,
            min(1.0, drive),
        )
        return 1.0 + max(0.0, min(1.0, float(boost))) * peak

    @staticmethod
    def transition_duration(
            section: str,
            rng: random.Random,
            *,
            slow_breakdowns: bool = True,
            normal_min: float = 0.65,
            normal_max: float = 1.8,
            breakdown_min: float = 5.0,
            breakdown_max: float = 9.0,
            depth: float = 0.0,
    ) -> float:
        """Choose a smooth transition duration, extending breakdowns and DEPTH."""
        if slow_breakdowns and section == "breakdown":
            low = max(2.0, float(breakdown_min))
            high = max(low, float(breakdown_max))
        else:
            low = max(0.1, float(normal_min))
            high = max(low, float(normal_max))
        depth_scale = 1.0 + max(0.0, min(1.0, float(depth))) * 0.75
        return rng.uniform(low, high) * depth_scale
