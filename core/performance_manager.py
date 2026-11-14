from __future__ import annotations

import math
import random
from collections import defaultdict
from collections.abc import Iterable

from core.composition import Layer
from media.models import MediaAsset


class PerformanceManager:
    """Randomized media assignment and freeform visual composition helpers."""

    BLEND_MODES = ("normal", "add", "screen", "multiply", "difference")
    _LAYOUT_RELATIONSHIPS = ("independent", "shared_center", "orbit", "nested", "opposed")

    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self._shuffle_bags: dict[str, list[MediaAsset]] = defaultdict(list)

    def randomize_decks(
            self,
            assets: Iterable[MediaAsset],
            decks: Iterable[object],
    ) -> int:
        candidates = list(assets)
        unlocked = [deck for deck in decks if not getattr(deck, "locked", False)]
        if not candidates or not unlocked:
            return 0

        assigned = 0
        for deck in unlocked:
            collection_id = getattr(deck, "collection_id", None) or "all"
            bag = self._shuffle_bags[collection_id]
            if not bag:
                bag = list(candidates)
                self.random.shuffle(bag)
                self._shuffle_bags[collection_id] = bag
            asset = bag.pop()
            deck.load(asset.path, asset_id=asset.id, collection_id=asset.collection_id)
            assigned += 1
        return assigned

    def randomize_layout(self, layers: Iterable[Layer]) -> int:
        """Give every visible, unlocked source a fresh overlapping collage position.

        This is intentionally not a four-cell deck layout. Positions may overlap or
        leave the canvas, the source types share one spatial vocabulary, and a text
        layer (when present) becomes the foreground headline.
        """
        candidates = [
            layer for layer in layers
            if layer.visible
            and not layer.locked
            and layer.source_type in {"video", "generator", "overlay"}
        ]
        if not candidates:
            return 0

        text_layers = [
            layer for layer in candidates
            if layer.source_type == "generator" and layer.generator_type == "text"
        ]
        headline = self.random.choice(text_layers) if text_layers else None
        spatial = [layer for layer in candidates if layer is not headline]
        relationship = self.random.choice(self._LAYOUT_RELATIONSHIPS)
        center = (
            self.random.uniform(0.40, 0.60),
            self.random.uniform(0.40, 0.60),
        )
        phase = self.random.uniform(0.0, math.tau)
        draw_order = list(spatial)
        self.random.shuffle(draw_order)

        for index, layer in enumerate(draw_order):
            progress = index / max(1, len(draw_order))
            if relationship == "orbit":
                angle = phase + index * 2.399963229728653
                radius = self.random.uniform(0.18, 0.58)
                x = center[0] + math.cos(angle) * radius
                y = center[1] + math.sin(angle) * radius
            elif relationship == "nested":
                spread = 0.10 + progress * 0.22
                x = center[0] + self.random.uniform(-spread, spread)
                y = center[1] + self.random.uniform(-spread, spread)
            elif relationship == "shared_center":
                x = center[0] + self.random.uniform(-0.34, 0.34)
                y = center[1] + self.random.uniform(-0.34, 0.34)
            elif relationship == "opposed":
                direction = -1.0 if index % 2 else 1.0
                x = center[0] + direction * self.random.uniform(0.16, 0.54)
                y = center[1] + direction * self.random.uniform(-0.48, 0.48)
            else:
                x = self.random.uniform(-0.12, 1.12)
                y = self.random.uniform(-0.12, 1.12)

            # Occasional edge escapes break the clean, evenly-spaced tile look.
            if self.random.random() < 0.30:
                x += self.random.choice((-1.0, 1.0)) * self.random.uniform(0.04, 0.20)
            if self.random.random() < 0.22:
                y += self.random.choice((-1.0, 1.0)) * self.random.uniform(0.04, 0.18)

            base_scale = self.random.uniform(0.38, 0.94)
            if layer.source_type == "generator":
                base_scale = self.random.uniform(0.48, 1.02)
            if layer.source_type == "overlay":
                base_scale = self.random.uniform(0.42, 1.08)
            layer.position = (round(x, 3), round(y, 3))
            layer.scale = (
                round(base_scale * self.random.uniform(0.82, 1.20), 3),
                round(base_scale * self.random.uniform(0.82, 1.20), 3),
            )
            layer.rotation = round(self.random.uniform(-34.0, 34.0), 2)
            layer.opacity = round(self.random.uniform(0.55, 1.0), 3)
            layer.blend_mode = self.random.choice(self.BLEND_MODES)
            layer.z_index = index

        # Establish one large visual mass so the result reads as a composition,
        # not a collection of equally-sized windows.
        background_candidates = [
            layer for layer in spatial if layer.source_type == "video"
        ] or spatial
        if background_candidates:
            background = self.random.choice(background_candidates)
            background.position = (
                round(self.random.uniform(0.43, 0.57), 3),
                round(self.random.uniform(0.43, 0.57), 3),
            )
            background_scale = self.random.uniform(1.02, 1.30)
            background.scale = (round(background_scale, 3), round(background_scale, 3))
            background.rotation = round(self.random.uniform(-9.0, 9.0), 2)
            background.opacity = round(self.random.uniform(0.88, 1.0), 3)
            background.blend_mode = "normal"
            background.z_index = -1

        if headline is not None:
            headline.position = (
                round(self.random.uniform(0.44, 0.56), 3),
                round(self.random.uniform(0.42, 0.58), 3),
            )
            headline_scale = self.random.uniform(1.02, 1.22)
            headline.scale = (round(headline_scale, 3), round(headline_scale, 3))
            headline.rotation = round(self.random.uniform(-4.0, 4.0), 2)
            headline.opacity = round(self.random.uniform(0.94, 1.0), 3)
            headline.blend_mode = "normal"
            headline.z_index = len(candidates) + 1

        return len(candidates)
