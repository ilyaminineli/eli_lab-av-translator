from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import tr


class SettingsDialog(QDialog):
    def __init__(
        self,
        parent: QWidget | None = None,
        language: str = "en",
        show_hints: bool = True,
        restore_session: bool = True,
    ) -> None:
        super().__init__(parent)
        self._language = language if language in {"en", "ja"} else "en"
        self.setWindowTitle(tr("settings.title", self._language))
        root = QVBoxLayout(self)

        interface_group = QGroupBox(tr("settings.interface", self._language), self)
        interface_form = QFormLayout(interface_group)
        self.language_combo = QComboBox(interface_group)
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("日本語", "ja")
        self.language_combo.setCurrentIndex(
            max(0, self.language_combo.findData(self._language))
        )
        interface_form.addRow(
            tr("settings.language", self._language),
            self.language_combo,
        )
        root.addWidget(interface_group)

        self.show_hints_check = QCheckBox(
            tr("settings.show_hints", self._language), self
        )
        self.show_hints_check.setChecked(bool(show_hints))
        root.addWidget(self.show_hints_check)

        session_group = QGroupBox(tr("settings.session", self._language), self)
        session_layout = QVBoxLayout(session_group)
        self.restore_session_check = QCheckBox(
            tr("settings.restore_session", self._language), session_group
        )
        self.restore_session_check.setChecked(bool(restore_session))
        session_layout.addWidget(self.restore_session_check)
        root.addWidget(session_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            tr("settings.save", self._language)
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(
            tr("settings.cancel", self._language)
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    @property
    def language(self) -> str:
        return str(self.language_combo.currentData() or "en")

    @property
    def show_hints(self) -> bool:
        return self.show_hints_check.isChecked()

    @property
    def restore_session(self) -> bool:
        return self.restore_session_check.isChecked()
