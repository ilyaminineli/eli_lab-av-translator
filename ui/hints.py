from __future__ import annotations

from PySide6.QtCore import QEvent, QObject


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
