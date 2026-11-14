from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtWidgets import QToolButton, QWidget

ICON_COLOR = "#D8D8D8"
ICON_DISABLED_COLOR = "#666666"


def _render_icon(name: str, color: str, size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    pen = QPen(
        QColor(color),
        max(1.45, size / 13.0),
        Qt.PenStyle.SolidLine,
        Qt.PenCapStyle.RoundCap,
        Qt.PenJoinStyle.RoundJoin,
    )
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    def line(*points: tuple[float, float]) -> None:
        for start, end in zip(points, points[1:]):
            painter.drawLine(QPointF(*start), QPointF(*end))

    def path(points: tuple[tuple[float, float], ...], close: bool = False) -> None:
        shape = QPainterPath()
        shape.moveTo(QPointF(*points[0]))
        for point in points[1:]:
            shape.lineTo(QPointF(*point))
        if close:
            shape.closeSubpath()
        painter.drawPath(shape)

    def filled_triangle(points: tuple[tuple[float, float], ...]) -> None:
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(color))
        painter.drawPolygon(QPolygonF([QPointF(*point) for point in points]))
        painter.restore()

    def sparkle(cx: float, cy: float, radius: float) -> None:
        path((
            (cx, cy - radius),
            (cx + radius * 0.22, cy - radius * 0.22),
            (cx + radius, cy),
            (cx + radius * 0.22, cy + radius * 0.22),
            (cx, cy + radius),
            (cx - radius * 0.22, cy + radius * 0.22),
            (cx - radius, cy),
            (cx - radius * 0.22, cy - radius * 0.22),
        ), close=True)

    if name == "play":
        filled_triangle(((8.0, 5.0), (19.0, 12.0), (8.0, 19.0)))
    elif name == "pause":
        painter.setBrush(QColor(color))
        painter.drawRoundedRect(6.0, 5.0, 4.0, 14.0, 1.0, 1.0)
        painter.drawRoundedRect(14.0, 5.0, 4.0, 14.0, 1.0, 1.0)
    elif name == "stop":
        painter.setBrush(QColor(color))
        painter.drawRoundedRect(6.0, 6.0, 12.0, 12.0, 1.5, 1.5)
    elif name == "load":
        path((
            (3.0, 8.0),
            (3.0, 5.5),
            (9.5, 5.5),
            (12.0, 8.0),
            (21.0, 8.0),
            (21.0, 18.5),
            (3.0, 18.5),
            (3.0, 8.0),
        ))
        line((12.0, 10.0), (12.0, 16.0))
        line((9.5, 13.5), (12.0, 16.0), (14.5, 13.5))
    elif name == "restart":
        painter.drawArc(QRectF(5.0, 5.0, 14.0, 14.0), 45 * 16, 290 * 16)
        filled_triangle(((17.2, 4.0), (21.0, 9.4), (14.5, 9.0)))
    elif name == "shuffle":
        path(((4.0, 7.0), (7.0, 7.0), (16.5, 17.0), (20.0, 17.0)))
        path(((4.0, 17.0), (7.0, 17.0), (16.5, 7.0), (20.0, 7.0)))
        line((16.5, 4.0), (20.0, 7.0), (16.5, 10.0))
        line((16.5, 14.0), (20.0, 17.0), (16.5, 20.0))
    elif name == "layout":
        painter.drawRoundedRect(3.5, 4.0, 11.0, 8.5, 1.0, 1.0)
        painter.drawRoundedRect(9.5, 11.5, 11.0, 8.5, 1.0, 1.0)
        line((7.0, 15.5), (7.0, 19.5), (11.0, 19.5))
    elif name == "sparkles":
        sparkle(11.0, 12.0, 7.0)
        sparkle(18.5, 5.5, 3.0)
        sparkle(5.0, 19.0, 2.5)
    elif name == "lock":
        painter.drawRoundedRect(5.0, 10.0, 14.0, 10.0, 1.8, 1.8)
        painter.drawArc(8.0, 3.0, 8.0, 12.0, 0, 180 * 16)
        line((12.0, 14.0), (12.0, 16.5))
    elif name == "unlock":
        painter.drawRoundedRect(5.0, 10.0, 14.0, 10.0, 1.8, 1.8)
        painter.drawArc(8.0, 3.0, 8.0, 12.0, 0, 115 * 16)
        line((16.0, 5.0), (18.5, 7.0))
        line((12.0, 14.0), (12.0, 16.5))
    elif name == "trash":
        line((4.0, 7.0), (20.0, 7.0))
        line((9.0, 4.5), (15.0, 4.5))
        path(((6.0, 8.5), (7.0, 19.5), (17.0, 19.5), (18.0, 8.5)))
        line((10.0, 10.5), (10.5, 17.0))
        line((14.0, 10.5), (13.5, 17.0))
    elif name == "apply":
        line((4.0, 12.5), (9.0, 17.5), (20.0, 6.0))
    elif name == "reset":
        painter.drawArc(QRectF(4.5, 4.5, 15.0, 15.0), 55 * 16, 290 * 16)
        line((5.0, 4.5), (5.5, 9.0), (10.0, 8.0))
    elif name == "settings":
        points = []
        for index in range(32):
            angle = math.tau * index / 32.0 - math.pi / 2.0
            radius = 9.0 if index % 4 in {0, 1} else 7.2
            points.append((12.0 + math.cos(angle) * radius, 12.0 + math.sin(angle) * radius))
        path(tuple(points), close=True)
        painter.drawEllipse(QPointF(12.0, 12.0), 3.0, 3.0)
    elif name == "warning":
        path(((12.0, 3.0), (21.0, 20.0), (3.0, 20.0), (12.0, 3.0)))
        line((12.0, 8.0), (12.0, 14.0))
        painter.drawPoint(QPointF(12.0, 17.0))
    elif name == "library":
        painter.drawRoundedRect(3.5, 4.0, 5.0, 16.0, 0.8, 0.8)
        painter.drawRoundedRect(10.0, 4.0, 5.0, 16.0, 0.8, 0.8)
        painter.drawRoundedRect(16.5, 4.0, 4.0, 16.0, 0.8, 0.8)
        line((5.0, 7.0), (7.0, 7.0), (7.0, 16.5))
        line((11.5, 7.0), (13.5, 7.0), (13.5, 16.5))
    elif name == "image":
        painter.drawRoundedRect(3.0, 4.0, 18.0, 16.0, 1.5, 1.5)
        painter.drawEllipse(QPointF(16.5, 8.5), 1.5, 1.5)
        path(((4.5, 17.5), (9.0, 12.5), (12.0, 15.0), (15.0, 11.5), (19.5, 17.5)))
    elif name == "menu":
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        for y in (6.0, 12.0, 18.0):
            painter.drawEllipse(QPointF(12.0, y), 1.35, 1.35)
    elif name == "close":
        line((6.0, 6.0), (18.0, 18.0))
        line((18.0, 6.0), (6.0, 18.0))
    elif name == "float":
        path(((4.0, 8.0), (4.0, 5.0), (5.0, 4.0), (13.0, 4.0)))
        path(((4.0, 8.0), (4.0, 19.0), (16.0, 19.0), (16.0, 14.0)))
        line((12.0, 4.0), (20.0, 4.0), (20.0, 12.0))
        line((20.0, 4.0), (10.0, 14.0))
    elif name == "dock":
        painter.drawRoundedRect(3.5, 4.0, 17.0, 16.0, 1.5, 1.5)
        line((8.0, 7.0), (8.0, 17.0))
        line((8.0, 12.0), (16.0, 12.0))
        line((13.0, 9.0), (16.0, 12.0), (13.0, 15.0))
    else:
        painter.drawEllipse(QPointF(12.0, 12.0), 7.0, 7.0)

    painter.end()
    return pixmap


def app_icon(name: str, size: int = 24, color: str = ICON_COLOR) -> QIcon:
    """Return a platform-independent monochrome vector-style icon."""
    icon = QIcon()
    icon.addPixmap(
        _render_icon(name, color, size),
        QIcon.Mode.Normal,
        QIcon.State.Off,
    )
    # Checked tool buttons receive a dark mark on their light active surface.
    icon.addPixmap(
        _render_icon(name, "#111111", size),
        QIcon.Mode.Normal,
        QIcon.State.On,
    )
    icon.addPixmap(
        _render_icon(name, ICON_DISABLED_COLOR, size),
        QIcon.Mode.Disabled,
        QIcon.State.Off,
    )
    icon.addPixmap(
        _render_icon(name, ICON_DISABLED_COLOR, size),
        QIcon.Mode.Disabled,
        QIcon.State.On,
    )
    return icon


def icon_button(
        parent: QWidget,
        name: str,
        tooltip: str,
        size: int = 30,
        checkable: bool = False,
) -> QToolButton:
    button = QToolButton(parent)
    button.setIcon(app_icon(name))
    button.setIconSize(QSize(17, 17))
    button.setToolTip(tooltip)
    button.setAccessibleName(tooltip)
    button.setAutoRaise(False)
    button.setFixedSize(size, max(26, size - 2))
    button.setCheckable(checkable)
    return button
