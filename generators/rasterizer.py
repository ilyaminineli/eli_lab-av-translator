from __future__ import annotations

import hashlib
import json
import math
import random
from typing import Any

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
)

from core.composition import Layer
from generators.catalog import normalize_settings

GENERATOR_WIDTH = 1600
GENERATOR_HEIGHT = 900

_GPU_UNIFORM_SETTINGS = (
    "animation",
    "animation_speed",
    "animation_amount",
    "text_animation",
    "text_animation_speed",
    "text_animation_amount",
    "text_animation_columns",
)


def raster_content_settings(
        generator_type: str,
        raw_settings: dict[str, Any],
) -> dict[str, Any]:
    """Return normalized settings that affect CPU-rasterized generator content."""
    settings = normalize_settings(generator_type, raw_settings)
    for key in _GPU_UNIFORM_SETTINGS:
        settings.pop(key, None)
    return settings


def _static_raster_settings(
        generator_type: str,
        raw_settings: dict[str, Any],
) -> dict[str, Any]:
    """Return only settings that change the CPU-rasterized generator image."""
    return raster_content_settings(generator_type, raw_settings)


class GeneratorRasterizer:
    """Rasterizes static generator content once; animation stays in the GPU compositor."""

    def __init__(
            self,
            width: int = GENERATOR_WIDTH,
            height: int = GENERATOR_HEIGHT,
    ) -> None:
        self.width = max(320, int(width))
        self.height = max(180, int(height))
        self._cache: dict[str, tuple[str, np.ndarray]] = {}

    @staticmethod
    def fingerprint(layer: Layer) -> str:
        settings = _static_raster_settings(
            layer.generator_type or "geometry",
            layer.generator_settings,
        )
        payload = {
            "type": layer.generator_type,
            "settings": settings,
            "size": [GENERATOR_WIDTH, GENERATOR_HEIGHT],
        }
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha1(encoded).hexdigest()

    def render_settings(
            self,
            layer_id: str,
            generator_type: str,
            raw_settings: dict[str, Any],
            *,
            width: int | None = None,
            height: int | None = None,
    ) -> tuple[str, np.ndarray]:
        """Render an immutable snapshot at its requested raster dimensions."""
        target_width = max(320, int(width or self.width))
        target_height = max(180, int(height or self.height))
        fingerprint = self.fingerprint_settings(
            generator_type, raw_settings, width=target_width, height=target_height
        )
        cached = self._cache.get(layer_id)
        if cached and cached[0] == fingerprint:
            return cached

        settings = normalize_settings(generator_type, raw_settings)
        image = QImage(
            target_width,
            target_height,
            QImage.Format.Format_RGBA8888,
        )
        image.fill(QColor(0, 0, 0, 0))
        painter = QPainter(image)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            # Draw in the canonical 1600×900 coordinate space, then scale the
            # painter as a whole. Font sizes, margins, strokes and collage
            # placement therefore retain the same proportions in draft preview.
            painter.scale(
                target_width / self.width,
                target_height / self.height,
            )
            if generator_type == "geometry":
                self._draw_geometry(painter, settings)
            elif generator_type == "text":
                self._draw_text(painter, settings)
            elif generator_type == "waveform":
                self._draw_waveform(painter, settings)
        finally:
            painter.end()
        rgba = image.bits().tobytes()
        pixels = np.frombuffer(rgba, dtype=np.uint8).reshape(
            target_height, target_width, 4
        ).copy()

        result = (fingerprint, pixels)
        self._cache[layer_id] = result
        return result

    def render(self, layer: Layer) -> tuple[str, np.ndarray]:
        return self.render_settings(
            layer.id,
            layer.generator_type or "geometry",
            dict(layer.generator_settings),
        )

    @staticmethod
    def fingerprint_settings(
            generator_type: str,
            raw_settings: dict[str, Any],
            *,
            width: int = GENERATOR_WIDTH,
            height: int = GENERATOR_HEIGHT,
    ) -> str:
        settings = _static_raster_settings(generator_type, raw_settings)
        payload = {
            "type": generator_type,
            "settings": settings,
            "size": [int(width), int(height)],
        }
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha1(encoded).hexdigest()

    def remove_missing(self, layer_ids: set[str]) -> None:
        for layer_id in tuple(self._cache):
            if layer_id not in layer_ids:
                self._cache.pop(layer_id, None)

    def clear(self) -> None:
        self._cache.clear()

    @staticmethod
    def _color(value: str, fallback: str = "#E8E4DA") -> QColor:
        color = QColor(value)
        return color if color.isValid() else QColor(fallback)

    def _pen(self, color: str, width: float) -> QPen:
        pen = QPen(self._color(color))
        pen.setWidthF(float(width))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return pen

    def _draw_geometry(self, painter: QPainter, settings: dict[str, Any]) -> None:
        width = self.width
        height = self.height
        center = QPointF(width / 2.0, height / 2.0)
        primary = str(settings["primary_color"])
        secondary = str(settings["secondary_color"])
        count = int(settings["density"])
        line_width = float(settings["line_width"])
        pattern = str(settings["pattern"])
        painter.save()
        painter.translate(center)
        painter.rotate(float(settings.get("rotation", 0.0)))
        painter.translate(-center)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if pattern == "grid":
            step = max(12, round(min(width, height) / count))
            painter.setPen(self._pen(secondary, max(0.5, line_width * 0.55)))
            for x in range(-width, width * 2, step):
                painter.drawLine(QPointF(x, 0), QPointF(x, height))
            for y in range(-height, height * 2, step):
                painter.drawLine(QPointF(0, y), QPointF(width, y))
            painter.setPen(self._pen(primary, line_width))
            painter.drawRect(QRectF(0, 0, width, height))
        elif pattern == "crosshatch":
            step = max(10, round(min(width, height) / count))
            painter.setPen(self._pen(primary, line_width))
            for offset in range(-height, width + height, step):
                painter.drawLine(QPointF(offset, 0), QPointF(offset + height, height))
                painter.drawLine(QPointF(offset, height), QPointF(offset + height, 0))
            painter.setPen(self._pen(secondary, line_width * 0.6))
            for offset in range(-height, width + height, step * 2):
                painter.drawLine(QPointF(offset, 0), QPointF(offset + height, height))
        elif pattern == "hexgrid":
            cell_height = max(16.0, min(width, height) / count)
            cell_width = cell_height * 0.866
            painter.setPen(self._pen(secondary, max(0.5, line_width * 0.55)))
            rows = math.ceil(height / (cell_height * 0.75)) + 2
            columns = math.ceil(width / cell_width) + 2
            for row in range(-1, rows):
                y = row * cell_height * 0.75
                for column in range(-1, columns):
                    x = column * cell_width + (row % 2) * cell_width * 0.5
                    path = QPainterPath()
                    for point in range(6):
                        angle = math.tau * point / 6.0 - math.pi / 6.0
                        px = x + math.cos(angle) * cell_width * 0.48
                        py = y + math.sin(angle) * cell_height * 0.48
                        if point == 0:
                            path.moveTo(px, py)
                        else:
                            path.lineTo(px, py)
                    path.closeSubpath()
                    painter.drawPath(path)
            painter.setPen(self._pen(primary, line_width))
            painter.drawLine(QPointF(0, height / 2), QPointF(width, height / 2))
        elif pattern == "moire":
            radius_max = math.hypot(width, height) * 0.48
            offsets = (-width * 0.105, width * 0.105)
            for side, offset in enumerate(offsets):
                moire_center = QPointF(center.x() + offset, center.y())
                for ring in range(1, count * 2 + 1):
                    radius = radius_max * ring / (count * 2)
                    color = primary if (ring + side) % 2 else secondary
                    painter.setPen(self._pen(color, line_width * 0.7))
                    painter.drawEllipse(moire_center, radius, radius)
        elif pattern == "spiral":
            radius_max = min(width, height) * 0.72
            points = max(480, count * 100)
            for spiral_index, phase in enumerate((0.0, math.pi)):
                path = QPainterPath()
                for step in range(points + 1):
                    progress = step / points
                    angle = progress * math.tau * max(2, count // 2) + phase
                    radius = radius_max * progress
                    x = center.x() + math.cos(angle) * radius
                    y = center.y() + math.sin(angle) * radius
                    if step == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                painter.setPen(self._pen(
                    primary if spiral_index == 0 else secondary,
                    line_width if spiral_index == 0 else line_width * 0.7,
                ))
                painter.drawPath(path)
        elif pattern == "radial":
            radius = math.hypot(width, height) * 0.56
            painter.setPen(self._pen(secondary, max(0.5, line_width * 0.65)))
            for index in range(count * 3):
                angle = math.tau * index / (count * 3)
                painter.drawLine(
                    center,
                    QPointF(
                        center.x() + math.cos(angle) * radius,
                        center.y() + math.sin(angle) * radius,
                    ),
                )
            painter.setPen(self._pen(primary, line_width))
            for ring in range(1, max(4, count // 2)):
                r = radius * ring / max(4, count // 2)
                painter.drawEllipse(center, r, r)
        elif pattern == "polygon":
            painter.setPen(self._pen(primary, line_width))
            sides = max(3, min(12, count // 2))
            for ring in range(1, count + 1):
                radius = min(width, height) * 0.48 * ring / count
                path = QPainterPath()
                for point in range(sides):
                    angle = math.tau * point / sides - math.pi / 2
                    x = center.x() + math.cos(angle) * radius
                    y = center.y() + math.sin(angle) * radius
                    if point == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                path.closeSubpath()
                painter.setPen(self._pen(
                    primary if ring % 2 else secondary,
                    line_width if ring % 2 else line_width * 0.7,
                ))
                painter.drawPath(path)
        else:  # rings
            max_radius = math.hypot(width, height) * 0.52
            for ring in range(count):
                radius = max_radius * (ring + 1) / count
                painter.setPen(self._pen(
                    primary if ring % 2 == 0 else secondary,
                    line_width if ring % 2 == 0 else line_width * 0.7,
                ))
                painter.drawEllipse(center, radius, radius)
        painter.restore()

    def _draw_text(self, painter: QPainter, settings: dict[str, Any]) -> None:
        if (
                settings.get("text_runs")
                or settings.get("text_writing_mode") != "horizontal"
                or settings.get("text_path_mode") != "none"
        ):
            from generators.typography import draw_typography

            draw_typography(painter, settings, self.width, self.height)
            return
        text = str(settings.get("text", "")).replace("\\n", "\n")
        if not text:
            return
        if settings.get("text_layout") == "collage":
            self._draw_text_collage(painter, settings, text)
            return
        family = str(settings.get("font_family", "Arial"))
        font = QFont(family)
        font.setPixelSize(int(settings["font_size"]))
        # PySide6 6.7+ requires the QFont.Weight enum rather than a plain int.
        font.setWeight(QFont.Weight(int(settings["font_weight"])))
        font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing,
            float(settings["letter_spacing"]),
        )
        metrics = QFontMetricsF(font)
        lines = text.splitlines() or [text]
        line_height = metrics.height() * float(settings["line_spacing"])
        total_height = line_height * len(lines)
        vertical = str(settings["vertical_alignment"])
        if vertical == "top":
            y = metrics.ascent() + 48
        elif vertical == "bottom":
            y = self.height - total_height + metrics.ascent() - 48
        else:
            y = (self.height - total_height) / 2.0 + metrics.ascent()

        alignment = str(settings["alignment"])
        if alignment == "left":
            x_anchor = 96.0
        elif alignment == "right":
            x_anchor = self.width - 96.0
        else:
            x_anchor = self.width / 2.0

        for line_index, line in enumerate(lines):
            path = QPainterPath()
            advance = metrics.horizontalAdvance(line)
            if alignment == "left":
                x = x_anchor
            elif alignment == "right":
                x = x_anchor - advance
            else:
                x = x_anchor - advance / 2.0
            path.addText(QPointF(x, y), font, line)
            if bool(settings.get("shadow", False)):
                shadow = QPainterPath(path)
                shadow.translate(8.0, 10.0)
                painter.fillPath(shadow, QColor(0, 0, 0, 150))
            stroke_width = float(settings["stroke_width"])
            if stroke_width > 0:
                painter.strokePath(
                    path,
                    self._pen(str(settings["stroke_color"]), stroke_width),
                )
            fill_color = str(settings["primary_color"])
            if (
                    settings.get("text_color_mode") == "alternate"
                    and line_index % 2 == 1
            ):
                fill_color = str(settings.get("secondary_color", fill_color))
            painter.fillPath(path, self._color(fill_color))
            y += line_height

    def _draw_text_collage(
            self,
            painter: QPainter,
            settings: dict[str, Any],
            text: str,
    ) -> None:
        rng = random.Random(int(settings.get("collage_seed", 211)))
        words = [item.strip() for item in text.splitlines() if item.strip()]
        if not words:
            return
        variation = float(settings.get("collage_font_variation", 0.65))
        base_size = int(settings["font_size"])
        family = str(settings.get("font_family", "Arial"))
        primary = str(settings.get("primary_color", "#F2EEE6"))
        secondary = str(settings.get("secondary_color", "#C35C75"))
        stroke_width = float(settings.get("stroke_width", 0.0))
        for index, word in enumerate(words):
            ratio = rng.uniform(1.0 - variation * 0.62, 1.0 + variation * 0.78)
            size = max(18, min(560, round(base_size * ratio)))
            font = QFont(family)
            font.setPixelSize(size)
            weights = (500, 600, 700, 800, 900)
            font.setWeight(QFont.Weight(rng.choice(weights)))
            font.setLetterSpacing(
                QFont.SpacingType.AbsoluteSpacing,
                float(settings.get("letter_spacing", 0.0)),
            )
            metrics = QFontMetricsF(font)
            advance = metrics.horizontalAdvance(word)
            x = rng.uniform(45.0, max(46.0, self.width - advance - 45.0))
            y = rng.uniform(size + 24.0, self.height - 24.0)
            angle = rng.choice((0.0, 0.0, 0.0, 90.0, -90.0, rng.uniform(-18.0, 18.0)))
            path = QPainterPath()
            path.addText(QPointF(0.0, 0.0), font, word)
            color = primary if index % 2 == 0 else secondary
            painter.save()
            painter.translate(x, y)
            painter.rotate(angle)
            if bool(settings.get("shadow", False)):
                shadow = QPainterPath(path)
                shadow.translate(5.0, 6.0)
                painter.fillPath(shadow, QColor(0, 0, 0, 125))
            if stroke_width > 0.0:
                painter.strokePath(
                    path,
                    self._pen(str(settings.get("stroke_color", "#211B2A")), stroke_width),
                )
            painter.fillPath(path, self._color(color))
            painter.restore()

    def _draw_waveform(self, painter: QPainter, settings: dict[str, Any]) -> None:
        width = self.width
        height = self.height
        density = int(settings["density"])
        amplitude = float(settings["amplitude"]) * height
        frequency = float(settings["frequency"])
        phase = float(settings["phase_offset"])
        line_width = float(settings["line_width"])
        pattern = str(settings.get("pattern", "sine"))
        for band in range(density):
            normalized = (band + 0.5) / density
            center_y = normalized * height
            offset = band * phase
            path = QPainterPath()
            for step in range(481):
                progress = step / 480.0
                if pattern == "lissajous":
                    angle = progress * math.tau * max(1.0, frequency)
                    x = width / 2.0 + math.sin(angle + offset) * width * 0.42
                    y = height / 2.0 + math.sin(
                        angle * 1.5 + offset + phase
                    ) * height * 0.38
                elif pattern == "radial":
                    angle = progress * math.tau
                    radius = min(width, height) * (
                            0.12 + 0.30 * (
                            0.5 + 0.5 * math.sin(angle * frequency + offset)
                    )
                    )
                    x = width / 2.0 + math.cos(angle + offset) * radius
                    y = height / 2.0 + math.sin(angle + offset) * radius
                elif pattern == "rose":
                    angle = progress * math.tau * max(1.0, frequency)
                    radius = min(width, height) * (
                            0.12 + 0.28 * (0.5 + 0.5 * math.cos(5.0 * angle + offset))
                    )
                    x = width / 2.0 + math.cos(angle + offset) * radius
                    y = height / 2.0 + math.sin(angle + offset) * radius
                elif pattern == "orbit":
                    angle = progress * math.tau
                    radius = min(width, height) * (
                            0.12 + 0.28 * (0.5 + 0.5 * math.sin(angle * frequency + offset))
                    )
                    x = width / 2.0 + math.cos(angle + offset) * radius
                    y = height / 2.0 + math.sin(angle + offset) * radius
                else:
                    x = width * progress
                    envelope = 0.35 + 0.65 * (
                            math.sin(math.pi * progress) ** 0.5
                    )
                    y = center_y + math.sin(
                        progress * math.tau * frequency + offset
                    ) * amplitude * envelope
                if step == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            painter.setPen(self._pen(
                str(settings["primary_color"])
                if band % 2 == 0 else str(settings["secondary_color"]),
                line_width if band % 2 == 0 else line_width * 0.65,
            ))
            painter.drawPath(path)
