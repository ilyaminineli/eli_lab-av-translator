from __future__ import annotations

import json
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent
from PySide6.QtGui import QAction, QImage
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.application import Application
from ui.generators_panel import GeneratorsPanel
from ui.hints import ToolTipFilter
from ui.i18n import apply_widget_translations, tr
from ui.performance_timeline_panel import PerformanceTimelinePanel
from ui.settings_dialog import SettingsDialog
from ui.theme import application_font_families, configure_application_theme


def test_theme_accepts_hover_hint_preference() -> None:
    application = QApplication.instance() or QApplication([])
    configure_application_theme(application, show_hints=False, language="ja")
    tooltip_filter = getattr(application, "_eli_tooltip_filter")
    assert isinstance(tooltip_filter, ToolTipFilter)
    assert tooltip_filter.enabled is False
    assert application.font().families()[0] == "Yu Gothic UI"
    assert application.property("ui_language") == "ja"


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



def test_widget_translation_covers_controls_and_preserves_user_input() -> None:
    application = QApplication.instance() or QApplication([])
    root = QWidget()
    layout = QVBoxLayout(root)

    group = QGroupBox("TEXT ART", root)
    group_layout = QVBoxLayout(group)
    label = QLabel("CONTENT · EDIT BUFFER", group)
    combo = QComboBox(group)
    combo.addItem("English", "english")
    edit = QLineEdit(group)
    edit.setText("Do not translate my content.")
    edit.setPlaceholderText("Search textures, materials, masks…")
    edit.setToolTip("Reset the master look to its default values")
    group_layout.addWidget(label)
    group_layout.addWidget(combo)
    group_layout.addWidget(edit)
    layout.addWidget(group)

    tabs = QTabWidget(root)
    tabs.addTab(QWidget(), "COMPOSE")
    layout.addWidget(tabs)
    action = QAction("REMOVE", root)

    apply_widget_translations(root, "ja")

    assert group.title() == "テキストアート"
    assert label.text() == "内容 · 編集バッファ"
    assert combo.itemText(0) == "英語"
    assert edit.placeholderText() == "テクスチャ、マテリアル、マスクを検索…"
    assert edit.text() == "Do not translate my content."
    assert edit.toolTip() == "マスタールックを初期値に戻します"
    assert tabs.tabText(0) == "構成"

    root.addAction(action)
    apply_widget_translations(root, "ja")
    assert action.text() == "削除"
    assert application.property("ui_language") == "ja"


def test_language_font_fallback_order_is_readable() -> None:
    english = application_font_families("en")
    japanese = application_font_families("ja")

    assert english[0] == "Segoe UI"
    assert japanese[0] == "Yu Gothic UI"
    assert "Noto Sans JP" in japanese
    assert "Noto Sans" in english


def test_timeline_payload_explanation_is_japanese_hover_help_only() -> None:
    qt_app = QApplication.instance() or QApplication([])
    qt_app.setProperty("ui_language", "ja")
    application = Application()
    panel = None
    try:
        panel = PerformanceTimelinePanel(application)
        assert not hasattr(panel, "payload_hint")
        assert panel.payload_edit.toolTip() == (
            "INTRO／PEAK／BREAKDOWNなどの区間名を記録します。シーンの呼び出しは行いません。"
        )
    finally:
        if panel is not None:
            panel.close()
        application.shutdown()




def test_overlay_format_note_is_hover_only_and_localized(tmp_path) -> None:
    qt_app = QApplication.instance() or QApplication([])
    qt_app.setProperty("ui_language", "ja")
    application = Application()
    panel = None
    try:
        image_path = tmp_path / "overlay.png"
        image = QImage(2, 2, QImage.Format.Format_RGBA8888)
        assert image.save(str(image_path))
        layer = application.add_media_overlay(image_path)

        panel = GeneratorsPanel(application)
        panel.refresh(select_id=layer.id)

        assert not hasattr(panel, "overlay_hint")
        assert panel.overlay_group.toolTip() == (
            "静止画像では開始／終了位置、不透明度、合成モード、マットを設定できます。"
            "再生速度、フレーム保持、ループ再生は適用されません。"
        )
    finally:
        if panel is not None:
            panel.close()
        application.shutdown()



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
