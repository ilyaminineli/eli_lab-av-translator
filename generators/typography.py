from __future__ import annotations

import math
import unicodedata
from bisect import bisect_right
from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen


def _font(style: dict[str, Any], defaults: dict[str, Any]) -> QFont:
    font = QFont(str(style.get("font_family", defaults.get("font_family", "Arial"))))
    font_size = int(style.get("font_size", defaults.get("font_size", 148)))
    font.setPixelSize(max(12, min(420, font_size)))
    weight = max(100, min(900, int(style.get("font_weight", defaults.get("font_weight", 700)))))
    font.setWeight(QFont.Weight(round(weight / 100) * 100))
    font.setLetterSpacing(
        QFont.SpacingType.AbsoluteSpacing,
        float(style.get("letter_spacing", defaults.get("letter_spacing", 0.0))),
    )
    return font


def _clusters(value: str) -> list[str]:
    """Split text into practical grapheme clusters without breaking combining marks."""
    result: list[str] = []
    join_next = False
    regional_count = 0
    for character in value:
        codepoint = ord(character)
        combining = bool(unicodedata.combining(character))
        variation = 0xFE00 <= codepoint <= 0xFE0F or 0xE0100 <= codepoint <= 0xE01EF
        modifier = 0x1F3FB <= codepoint <= 0x1F3FF
        regional = 0x1F1E6 <= codepoint <= 0x1F1FF
        if not result or (not combining and not variation and not modifier and not join_next
                          and codepoint != 0x200D and not (regional and regional_count % 2)):
            result.append(character)
        else:
            result[-1] += character
        join_next = codepoint == 0x200D
        if regional:
            regional_count += 1
        else:
            regional_count = 0
    return result


def _styles(settings: dict[str, Any]) -> list[dict[str, Any]]:
    base = {
        "font_family": settings.get("font_family", "Arial"),
        "font_size": settings.get("font_size", 148),
        "font_weight": settings.get("font_weight", 700),
        "color": settings.get("primary_color", "#F2EEE6"),
        "letter_spacing": settings.get("letter_spacing", 0.0),
        "stroke_color": settings.get("stroke_color", "#211B2A"),
        "stroke_width": settings.get("stroke_width", 0.0),
        "shadow": settings.get("shadow", False),
    }
    raw_runs = settings.get("text_runs", [])
    if not isinstance(raw_runs, (list, tuple)) or not raw_runs:
        return [{**base, "text": str(settings.get("text", ""))}]
    result = []
    for run in raw_runs[:64]:
        if not isinstance(run, dict):
            continue
        text = str(run.get("text", ""))
        if not text:
            continue
        result.append({**base, **run, "text": text})
    return result or [{**base, "text": str(settings.get("text", ""))}]


def _color(value: str, fallback: str = "#F2EEE6") -> QColor:
    color = QColor(str(value))
    return color if color.isValid() else QColor(fallback)


def _pen(color: str, width: float) -> QPen:
    pen = QPen(_color(color, "#211B2A"))
    pen.setWidthF(max(0.0, float(width)))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    return pen


def _draw_path(
        painter: QPainter,
        path: QPainterPath,
        style: dict[str, Any],
) -> None:
    stroke_width = max(0.0, float(style.get("stroke_width", 0.0)))
    stroke_color = str(style.get("stroke_color", "#211B2A"))
    fill = _color(str(style.get("color", "#F2EEE6")))
    if bool(style.get("shadow", False)):
        shadow = QPainterPath(path)
        shadow.translate(5.0, 7.0)
        painter.fillPath(shadow, QColor(0, 0, 0, 145))
    if stroke_width > 0.0:
        painter.strokePath(path, _pen(stroke_color, stroke_width))
    painter.fillPath(path, fill)


def _draw_horizontal(
        painter: QPainter,
        settings: dict[str, Any],
        styles: list[dict[str, Any]],
        width: int,
        height: int,
) -> None:
    margin = 96.0
    x = margin
    y = 48.0
    line_height = 0.0
    right = width - margin
    line_spacing = max(0.5, min(2.5, float(settings.get("line_spacing", 1.0))))

    for style in styles:
        font = _font(style, settings)
        metrics = QFontMetricsF(font)
        advance_height = metrics.height() * line_spacing
        line_height = max(line_height, advance_height)
        for paragraph_index, paragraph in enumerate(str(style.get("text", "")).split("\n")):
            if paragraph_index:
                x = margin
                y += max(line_height, advance_height)
                line_height = advance_height
            if not paragraph:
                continue
            full_advance = metrics.horizontalAdvance(paragraph)
            available = right - x
            if full_advance <= available:
                path = QPainterPath()
                path.addText(QPointF(x, y + metrics.ascent()), font, paragraph)
                _draw_path(painter, path, style)
                x += full_advance
                continue

            # Keep shaping intact for each word; only split a single oversized token.
            tokens = paragraph.split(" ")
            for token_index, token in enumerate(tokens):
                token_text = token + (" " if token_index < len(tokens) - 1 else "")
                token_advance = metrics.horizontalAdvance(token_text)
                if x > margin and x + token_advance > right:
                    x = margin
                    y += max(line_height, advance_height)
                    line_height = advance_height
                if token_advance <= right - x:
                    path = QPainterPath()
                    path.addText(QPointF(x, y + metrics.ascent()), font, token_text, )
                    _draw_path(painter, path, style)
                    x += token_advance
                else:
                    for cluster in _clusters(token_text):
                        cluster_advance = metrics.horizontalAdvance(cluster)
                        if x > margin and x + cluster_advance > right:
                            x = margin
                            y += max(line_height, advance_height)
                        path = QPainterPath()
                        path.addText(QPointF(x, y + metrics.ascent()), font, cluster)
                        _draw_path(painter, path, style)
                        x += cluster_advance
            if y > height + 2 * metrics.height():
                return


def _vertical_rotated(cluster: str) -> bool:
    return bool(cluster) and all(
        ord(character) < 128 and (character.isalnum() or character in "+-=/%&")
        for character in cluster
    )


def _draw_vertical(
        painter: QPainter,
        settings: dict[str, Any],
        styles: list[dict[str, Any]],
        width: int,
        height: int,
        writing_mode: str,
) -> None:
    direction = -1.0 if writing_mode == "vertical_rl" else 1.0
    maximum_size = max(
        _font(style, settings).pixelSize() for style in styles
    )
    column_step = max(18.0, float(maximum_size) * 1.35)
    cell_step = max(18.0, float(maximum_size) * 1.08)
    column = 0
    x_origin = width - 96.0 if direction < 0 else 96.0
    x = x_origin
    y = 48.0

    for style in styles:
        font = _font(style, settings)
        metrics = QFontMetricsF(font)
        cell_width = max(float(font.pixelSize()), metrics.height())
        for cluster in _clusters(str(style.get("text", ""))):
            if cluster in {"\n", "\r"}:
                column += 1
                x = x_origin + direction * column * column_step
                y = 48.0
                continue
            if y + cell_step > height - 24.0:
                column += 1
                x = x_origin + direction * column * column_step
                y = 48.0
            if x < -column_step or x > width + column_step:
                return
            if cluster.isspace():
                y += cell_step * 0.65
                continue

            glyph = QPainterPath()
            advance = max(1.0, metrics.horizontalAdvance(cluster))
            if _vertical_rotated(cluster):
                painter.save()
                painter.translate(x + cell_width * 0.5, y + cell_step * 0.5)
                painter.rotate(90.0)
                glyph.addText(QPointF(-advance * 0.5, metrics.ascent() * 0.35), font, cluster)
                _draw_path(painter, glyph, style)
                painter.restore()
            else:
                punctuation_offset = (
                    cell_width * 0.16 if cluster in {"、", "。", "，", "．"} else 0.0
                )
                glyph.addText(
                    QPointF(x + max(0.0, (cell_width - advance) * 0.5)
                            + punctuation_offset,
                            y + metrics.ascent()),
                    font,
                    cluster,
                )
                _draw_path(painter, glyph, style)
            y += cell_step


def _path_for_settings(
        settings: dict[str, Any],
        width: int,
        height: int,
        mode: str,
) -> QPainterPath:
    path = QPainterPath()
    if mode in {"circle", "arc"}:
        rectangle = QRectF(width * 0.12, height * 0.06, width * 0.76, height * 0.76)
        if mode == "circle":
            path.addEllipse(rectangle)
        else:
            path.arcMoveTo(rectangle, 215.0)
            path.arcTo(rectangle, 215.0, 110.0)
        return path

    points = settings.get("text_path_points", [])
    if not isinstance(points, (list, tuple)):
        points = []
    valid = []
    for point in points[:64]:
        try:
            if len(point) < 2:
                continue
            valid.append((
                max(0.0, min(1.0, float(point[0]))) * width,
                max(0.0, min(1.0, float(point[1]))) * height,
            ))
        except (TypeError, ValueError, OverflowError):
            continue
    if len(valid) < 2:
        valid = [
            (width * 0.12, height * 0.68),
            (width * 0.34, height * 0.28),
            (width * 0.66, height * 0.72),
            (width * 0.88, height * 0.32),
        ]
    path.moveTo(*valid[0])
    for point in valid[1:]:
        path.lineTo(*point)
    return path


def _path_samples(path: QPainterPath, count: int = 768) -> tuple[list[float], list[QPointF]]:
    points = [path.pointAtPercent(index / count) for index in range(count + 1)]
    distances = [0.0]
    for previous, current in zip(points, points[1:]):
        distances.append(distances[-1] + math.hypot(
            current.x() - previous.x(), current.y() - previous.y()
        ))
    return distances, points


def _point_at_distance(
        distance: float,
        distances: list[float],
        points: list[QPointF],
        *,
        wrap: bool,
) -> tuple[QPointF, float]:
    total = distances[-1]
    if total <= 0.001:
        return points[0], 0.0
    target = distance % total if wrap else max(0.0, min(total, distance))
    index = min(len(distances) - 2, max(0, bisect_right(distances, target) - 1))
    segment_length = max(0.0001, distances[index + 1] - distances[index])
    progress = (target - distances[index]) / segment_length
    start = points[index]
    end = points[index + 1]
    point = QPointF(
        start.x() + (end.x() - start.x()) * progress,
        start.y() + (end.y() - start.y()) * progress,
    )
    angle = math.degrees(math.atan2(end.y() - start.y(), end.x() - start.x()))
    return point, angle


def _draw_on_path(
        painter: QPainter,
        settings: dict[str, Any],
        styles: list[dict[str, Any]],
        width: int,
        height: int,
        mode: str,
) -> None:
    path = _path_for_settings(settings, width, height, mode)
    distances, samples = _path_samples(path)
    total_length = distances[-1]
    if total_length <= 1.0:
        return
    glyphs = []
    for style in styles:
        font = _font(style, settings)
        metrics = QFontMetricsF(font)
        for cluster in _clusters(str(style.get("text", ""))):
            if cluster in {"\n", "\r"}:
                continue
            glyph_advance = max(1.0, metrics.horizontalAdvance(cluster))
            glyphs.append((cluster, style, font, metrics, glyph_advance))
    text_length = sum(item[4] for item in glyphs)
    cursor = max(0.0, (total_length - text_length) * 0.5)
    wrap = mode == "circle"
    if wrap and text_length > total_length:
        cursor = 0.0
    for cluster, style, font, metrics, glyph_advance in glyphs:
        point, angle = _point_at_distance(
            cursor + glyph_advance * 0.5,
            distances,
            samples,
            wrap=wrap,
        )
        if not wrap and cursor + glyph_advance * 0.5 > total_length:
            break
        if not cluster.isspace():
            painter.save()
            painter.translate(point)
            painter.rotate(angle)
            glyph = QPainterPath()
            glyph.addText(
                QPointF(-glyph_advance * 0.5, metrics.ascent() * 0.34),
                font,
                cluster,
            )
            _draw_path(painter, glyph, style)
            painter.restore()
        cursor += glyph_advance


def draw_typography(
        painter: QPainter,
        settings: dict[str, Any],
        width: int,
        height: int,
) -> None:
    """Render the non-legacy typography layouts on the raster worker."""
    styles = _styles(settings)
    if not styles:
        return
    path_mode = str(settings.get("text_path_mode", "none"))
    writing_mode = str(settings.get("text_writing_mode", "horizontal"))
    if path_mode != "none":
        _draw_on_path(painter, settings, styles, width, height, path_mode)
    elif writing_mode in {"vertical_rl", "vertical_lr"}:
        _draw_vertical(painter, settings, styles, width, height, writing_mode)
    else:
        _draw_horizontal(painter, settings, styles, width, height)
