from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QHBoxLayout, QStyle, QToolButton, QWidget


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

        self.random_set_button = self._tool_button(
            QStyle.StandardPixmap.SP_BrowserReload,
            "Randomize video deck assignments",
        )
        self.random_layout_button = self._tool_button(
            QStyle.StandardPixmap.SP_FileDialogDetailedView,
            "Generate a new freeform collage layout",
        )
        self.random_look_button = self._tool_button(
            QStyle.StandardPixmap.SP_DriveNetIcon,
            "Apply a randomized master-effect look",
        )
        self.lock_all_button = self._tool_button(
            QStyle.StandardPixmap.SP_MessageBoxWarning,
            "Lock or unlock all decks and visual layers",
        )
        self.lock_all_button.setCheckable(True)

        self.random_set_button.clicked.connect(self.random_set_requested)
        self.random_layout_button.clicked.connect(self.random_layout_requested)
        self.random_look_button.clicked.connect(self.random_look_requested)
        self.lock_all_button.toggled.connect(self.lock_all_requested)

        layout.addWidget(self.random_set_button)
        layout.addWidget(self.random_layout_button)
        layout.addWidget(self.random_look_button)
        layout.addStretch(1)
        layout.addWidget(self.lock_all_button)

    def _tool_button(
            self,
            icon: QStyle.StandardPixmap,
            tooltip: str,
    ) -> QToolButton:
        button = QToolButton(self)
        button.setIcon(self.style().standardIcon(icon))
        button.setIconSize(QSize(16, 16))
        button.setToolTip(tooltip)
        button.setAccessibleName(tooltip)
        button.setAutoRaise(False)
        button.setFixedSize(32, 28)
        return button
