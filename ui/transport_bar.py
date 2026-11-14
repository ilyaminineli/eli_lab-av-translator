from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget

from ui.icons import app_icon, icon_button
from ui.i18n import ui_text


class TransportBar(QWidget):
    random_set_requested = Signal()
    random_layout_requested = Signal()
    random_look_requested = Signal()
    lock_all_requested = Signal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.random_set_button = icon_button(
            self, "shuffle", "Randomize decks", size=32
        )
        self.random_layout_button = icon_button(
            self, "layout", "Randomize layout", size=32
        )
        self.random_look_button = icon_button(
            self, "sparkles", "Randomize look", size=32
        )
        self.lock_all_button = icon_button(
            self,
            "unlock",
            "Lock all layers",
            size=32,
            checkable=True,
        )

        self.random_set_button.clicked.connect(self.random_set_requested)
        self.random_layout_button.clicked.connect(self.random_layout_requested)
        self.random_look_button.clicked.connect(self.random_look_requested)
        self.lock_all_button.toggled.connect(self._lock_all_toggled)

        layout.addWidget(self.random_set_button)
        layout.addWidget(self.random_layout_button)
        layout.addWidget(self.random_look_button)
        layout.addStretch(1)
        layout.addWidget(self.lock_all_button)

    def _lock_all_toggled(self, locked: bool) -> None:
        self.lock_all_button.setIcon(app_icon("lock" if locked else "unlock"))
        action = (
            "Unlock all layers"
            if locked
            else "Lock all layers"
        )
        translated_action = ui_text(action)
        self.lock_all_button.setToolTip(translated_action)
        self.lock_all_button.setAccessibleName(translated_action)
        self.lock_all_requested.emit(locked)
