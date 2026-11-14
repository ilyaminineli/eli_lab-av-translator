from __future__ import annotations

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from core.application import Application
from ui.hints import ToolTipFilter
from ui.i18n import tr
from ui.settings_dialog import SettingsDialog
from ui.theme import configure_application_theme


def test_theme_accepts_hover_hint_preference() -> None:
    application = QApplication.instance() or QApplication([])
    configure_application_theme(application, show_hints=False)
    tooltip_filter = getattr(application, "_eli_tooltip_filter")
    assert isinstance(tooltip_filter, ToolTipFilter)
    assert tooltip_filter.enabled is False


def test_tooltip_filter_can_be_toggled_without_removing_tooltips() -> None:
    tooltip_filter = ToolTipFilter(enabled=False)
    event = QEvent(QEvent.Type.ToolTip)
    event.ignore()

    assert tooltip_filter.eventFilter(None, event) is True
    assert event.isAccepted()

    tooltip_filter.set_enabled(True)
    enabled_event = QEvent(QEvent.Type.ToolTip)
    enabled_event.ignore()
    assert tooltip_filter.eventFilter(None, enabled_event) is False
    assert not enabled_event.isAccepted()


def test_settings_dialog_exposes_language_hints_and_recovery() -> None:
    application = QApplication.instance() or QApplication([])
    dialog = SettingsDialog(
        language="ja",
        show_hints=False,
        restore_session=False,
    )

    assert dialog.windowTitle() == "設定"
    assert dialog.language == "ja"
    assert dialog.show_hints is False
    assert dialog.restore_session is False
    assert application is not None


def test_japanese_catalog_and_english_fallback() -> None:
    assert tr("menu.settings", "ja") == "設定"
    assert tr("about.tagline", "ja") == "映像・生成表現・音楽をつなぐライブ映像制作ツール。"
    assert tr("menu.settings", "en") == "Settings"
    assert tr("missing.key", "ja") == "missing.key"


def test_recovery_snapshot_does_not_auto_start_performance_or_decks(
    tmp_path,
) -> None:
    application = Application()
    recovery_file = tmp_path / "session-recovery.eliav"
    try:
        application.performance_mode.plan.start_automation = True
        application.save_project(recovery_file)
        payload = json.loads(recovery_file.read_text(encoding="utf-8"))

        plan = payload["app_state"]["performance_settings"]["performance_mode_plan"]
        assert plan["start_automation"] is False
        assert all(not deck["playing"] for deck in payload["decks"])
    finally:
        application.shutdown()
