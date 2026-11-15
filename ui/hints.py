from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPointF
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QSlider,
)


class ToolTipFilter(QObject):
    """Suppress Qt hover help globally without discarding accessible tooltips."""

    def __init__(self, enabled: bool = True, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.enabled = bool(enabled)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ToolTip and not self.enabled:
            event.accept()
            return True
        return False


class WheelGuard(QObject):
    """Keep wheel scrolling from changing values in hovered controls.

    When a protected control lives inside a scroll area, relay the wheel event
    to that area's viewport so the user can continue scrolling the panel.
    Combo-box popup views are separate list widgets and remain normally scrollable.
    """

    _PROTECTED_CONTROLS = (QAbstractSpinBox, QComboBox, QSlider)

    @staticmethod
    def _scroll_area_for(widget: QObject) -> QAbstractScrollArea | None:
        parent = widget.parent()
        while parent is not None:
            if isinstance(parent, QAbstractScrollArea):
                return parent
            parent = parent.parent()
        return None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() != QEvent.Type.Wheel or not isinstance(
            watched, self._PROTECTED_CONTROLS
        ):
            return False

        scroll_area = self._scroll_area_for(watched)
        if scroll_area is None:
            event.accept()
            return True

        # Send a fresh wheel event to the scroll viewport. Sending the original
        # event would re-enter the application filter and could recurse.
        wheel = event
        viewport = scroll_area.viewport()
        global_position = wheel.globalPosition()
        local_position = QPointF(viewport.mapFromGlobal(global_position.toPoint()))
        forwarded = QWheelEvent(
            local_position,
            global_position,
            wheel.pixelDelta(),
            wheel.angleDelta(),
            wheel.buttons(),
            wheel.modifiers(),
            wheel.phase(),
            wheel.inverted(),
            wheel.source(),
        )
        QApplication.sendEvent(viewport, forwarded)
        event.accept()
        return True
