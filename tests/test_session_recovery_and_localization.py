from __future__ import annotations

import json
import os
import tomllib
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QAction, QIcon, QImage, QWheelEvent
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QProgressBar,
    QScrollArea,
    QSlider,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config import APP_VER, ICON_PATH
from core.application import Application
from ui.generators_panel import GeneratorsPanel
from ui.hints import ToolTipFilter, WheelGuard
from ui.i18n import (
    apply_widget_translations,
    set_ui_format,
    set_ui_text,
    tr,
    ui_text,
)
from ui.performance_timeline_panel import PerformanceTimelinePanel
from ui.settings_dialog import SettingsDialog
from ui.theme import (
    _typography_stylesheet,
    application_font_families,
    configure_application_theme,
)


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
    assert (
        tr("about.tagline", "ja")
        == "映像・生成表現・音楽をつなぐライブ映像制作ツール。"
    )
    assert tr("menu.settings", "en") == "Settings"
    assert tr("missing.key", "ja") == "missing.key"
    assert ui_text("PERF MODIFIERS", "ja") == "レイヤー別モディファイア"
    assert ui_text("TEXT MOTION", "ja") == "テキストモーション"
    assert ui_text("MASTER FX", "ja") == "マスターFX"
    assert ui_text("FX", "ja") == "FX"
    assert ui_text("AUTO", "ja") == "AUTO"
    assert ui_text("PREVIEW", "ja") == "プレビュー"
    assert ui_text("AUDIO", "ja") == "音声"
    assert ui_text("MOD", "ja") == "MOD"
    assert ui_text("TIME", "ja") == "時間"


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
    english_typography = _typography_stylesheet("en")
    japanese_typography = _typography_stylesheet("ja")
    assert "Newsreader" in english_typography
    assert "DM Mono" in english_typography
    assert "Noto Serif JP" in japanese_typography


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


def test_palette_combo_keeps_internal_key_when_japanese_label_is_shown() -> None:
    qt_app = QApplication.instance() or QApplication([])
    qt_app.setProperty("ui_language", "ja")
    application = Application()
    panel = None
    try:
        panel = GeneratorsPanel(application)
        apply_widget_translations(panel, "ja")

        assert panel.palette_combo.itemText(0) == "手動設定"
        assert panel.palette_combo.itemData(0) == ""
        panel.palette_combo.setCurrentIndex(0)
        assert panel.palette_combo.itemData(1) == panel.palette_combo.itemText(1)

        panel.palette_combo.setCurrentIndex(1)
        assert panel.primary_color.text().startswith("#")
        assert panel.secondary_color.text().startswith("#")
    finally:
        if panel is not None:
            panel.close()
        application.shutdown()


def test_dynamic_text_can_switch_between_languages_without_losing_source() -> None:
    qt_app = QApplication.instance() or QApplication([])
    root = QWidget()
    label = QLabel(root)

    source = "Added {name} as a composition overlay."
    rendered = source.format(name="Overlay · Rain")
    set_ui_text(label, rendered, "ja")
    assert label.text() == "Overlay · Rainを構成オーバーレイとして追加しました。"

    apply_widget_translations(root, "en")
    assert label.text() == rendered
    apply_widget_translations(root, "ja")
    assert label.text() == "Overlay · Rainを構成オーバーレイとして追加しました。"
    assert qt_app is not None


def test_japanese_dynamic_status_templates() -> None:
    assert (
        ui_text("Indexed 12 video file(s).", "ja")
        == "動画ファイルを12件索引化しました。"
    )
    assert ui_text("CONNECTED · USB MIDI", "ja") == "接続中 · USB MIDI"
    assert ui_text("TEXT PIPELINE · READY", "ja") == "テキスト処理 · 準備完了"


def test_dynamic_dialog_and_multiline_media_prompts_translate() -> None:
    assert ui_text("New project", "ja") == "新規プロジェクト"
    assert ui_text("Imported 3 modulator preset(s).", "ja") == (
        "モジュレータープリセットを3件インポートしました。"
    )
    prompt = (
        "Remove Archive from the library index?\n\n"
        "This removes its entries and cached thumbnails only. "
        "Your original video files and folders will NOT be deleted. "
        "Clips already loaded into decks continue playing."
    )
    translated = ui_text(prompt, "ja")
    assert translated.startswith("Archiveをライブラリの索引から削除しますか？")
    assert "元の動画ファイルやフォルダーは削除されません" in translated


def test_widget_headers_and_progress_formats_retranslate_live() -> None:
    qt_app = QApplication.instance() or QApplication([])
    root = QWidget()
    table = QTableWidget(0, 2, root)
    table.setHorizontalHeaderLabels(["Layer", "Opacity"])
    progress = QProgressBar(root)
    set_ui_format(progress, "IDLE", "ja")

    apply_widget_translations(root, "ja")
    assert table.horizontalHeaderItem(0).text() == "レイヤー"
    assert table.horizontalHeaderItem(1).text() == "不透明度"
    assert progress.format() == "待機中"

    apply_widget_translations(root, "en")
    assert table.horizontalHeaderItem(0).text() == "Layer"
    assert table.horizontalHeaderItem(1).text() == "Opacity"
    assert progress.format() == "IDLE"
    assert qt_app is not None


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


def test_final_application_seal_is_packaged() -> None:
    assert ICON_PATH.name == "eli-lab-mark.ico"
    assert ICON_PATH.is_file()
    assert not QIcon(str(ICON_PATH)).isNull()


def test_theme_uses_responsive_group_and_control_metrics() -> None:
    from ui.theme import APP_STYLE, _typography_stylesheet

    english = _typography_stylesheet("en")
    japanese = _typography_stylesheet("ja")
    assert "QSplitter::handle" in APP_STYLE
    assert "min-height: 20px" in APP_STYLE
    assert "Newsreader" in english
    assert "DM Mono" in english
    for control in (
        "QLabel",
        "QAbstractItemView",
        "QToolTip",
        "QGroupBox::title",
        "QGroupBox#deckCard::title",
        "QGroupBox#performanceModifiersGroup::title",
        "QPushButton",
        "QToolButton",
        "QCheckBox",
        "QRadioButton",
        "QMenuBar",
        "QMenu",
        "QHeaderView::section",
        "QComboBox",
        "QSpinBox",
    ):
        assert control in english
        assert control in japanese
    assert "Yu Gothic UI" in japanese
    assert "Segoe UI" in english
    assert "padding: 5px 8px 6px" in APP_STYLE
    assert "min-height: 20px" in APP_STYLE


def test_inspector_dock_tab_titles_are_compact_and_stable() -> None:
    from ui.main_window import _DOCK_TAB_TITLES

    assert _DOCK_TAB_TITLES == {
        "LAYERS": "LAYERS",
        "FX + OVERLAYS": "FX",
        "AUTO PERF": "AUTO",
        "LOCAL PREVIEW": "PREVIEW",
        "AUDIO / CTRL": "AUDIO",
        "MOD BANK": "MOD",
        "LIVE TIMELINE": "TIME",
    }
    assert all(len(label) <= 7 for label in _DOCK_TAB_TITLES.values())


def test_build_temp_storage_is_redirected_to_project_build_area(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts import build_pyinstaller

    build_temp = tmp_path / "build" / "tmp"
    pip_cache = build_temp / "pip-cache"
    monkeypatch.setattr(build_pyinstaller, "ROOT", tmp_path)
    monkeypatch.setattr(build_pyinstaller, "BUILD_TEMP_DIR", build_temp)
    monkeypatch.setattr(build_pyinstaller, "PIP_CACHE_DIR", pip_cache)
    real_usage = build_pyinstaller.shutil.disk_usage(tmp_path)
    enough_space = real_usage._replace(free=6 * 1024**3)
    monkeypatch.setattr(
        build_pyinstaller.shutil, "disk_usage", lambda _path: enough_space
    )

    build_pyinstaller.configure_build_storage()

    assert build_temp.is_dir()
    assert pip_cache.is_dir()
    assert os.environ["TEMP"] == str(build_temp)
    assert os.environ["TMP"] == str(build_temp)
    assert os.environ["TMPDIR"] == str(build_temp)
    assert os.environ["PIP_CACHE_DIR"] == str(pip_cache)


def test_package_and_build_metadata_are_consistent() -> None:
    root = Path(__file__).resolve().parents[1]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    runtime_requirements = {
        line.strip()
        for line in (root / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    dev_requirements = {
        line.strip()
        for line in (root / "requirements-dev.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
        and not line.lstrip().startswith("#")
        and not line.lstrip().startswith("-r ")
    }
    build_requirements = (root / "requirements-build-pyinstaller.txt").read_text(
        encoding="utf-8"
    )
    spec = (root / "AVTranslator.spec").read_text(encoding="utf-8")
    build_script = (root / "scripts" / "build_pyinstaller.py").read_text(
        encoding="utf-8"
    )

    assert project["version"] == APP_VER
    assert (
        project["dependencies"] and set(project["dependencies"]) == runtime_requirements
    )
    assert set(project["optional-dependencies"]["dev"]) == dev_requirements
    assert "mido>=1.3,<2" in project["optional-dependencies"]["midi"]
    assert "python-rtmidi==1.5.8" in project["optional-dependencies"]["midi"]
    assert "PyInstaller==6.22.3" in build_requirements
    assert "pyinstaller-hooks-contrib==2026.9" in build_requirements
    assert "setuptools>=69" in build_requirements
    assert "wheel" in build_requirements
    assert "from config import APP_NAME, ICON_PATH" in spec
    assert "name=APP_NAME" in spec
    assert "ICON = ICON_PATH" in spec
    assert "APP_NAME" in build_script
    assert "APP_VER" in build_script
    assert "ICON_PATH" in build_script
    assert "--no-deps" in build_script
    assert "--no-build-isolation" in build_script
    assert "--force-reinstall" in build_script
    assert "AVT_BUILD_TEMP_DIR" in build_script
    assert "PIP_CACHE_DIR" in build_script
    assert ICON_PATH.is_file()

    # PyInstaller's hook-av preserves the wheel's av.libs directory. The spec
    # must not add a second top-level binary copy of those same FFmpeg DLLs.
    assert "sysconfig" not in spec
    assert 'site_packages.glob("av.libs")' not in spec
    assert '(str(dll), ".")' not in spec
    assert "PyInstaller" in spec


def test_eliding_status_label_keeps_full_diagnostic_text() -> None:
    qt_app = QApplication.instance() or QApplication([])
    from ui.main_window import ElidingLabel

    label = ElidingLabel()
    label.resize(76, 24)
    source = "PROJECTOR READY · NVIDIA GeForce RTX 4060"
    label.setText(source)
    label.show()
    qt_app.processEvents()

    assert label.text() != source
    assert label.toolTip() == source
    label.close()


def test_performance_macro_strip_uses_three_column_layout() -> None:
    from ui.performance_control_panel import PerformanceControlPanel

    application = Application()
    panel = None
    try:
        panel = PerformanceControlPanel(application)
        layout = panel.performance_macro_group.layout()
        assert isinstance(layout, QGridLayout)
        assert len(panel.macro_sliders) == 6
        assert layout.columnCount() == 3
        panel.take_performance_macro_group()
        assert panel.performance_macro_group.maximumHeight() >= 260
    finally:
        if panel is not None:
            panel.close()
        application.shutdown()


def test_wheel_over_controls_scrolls_panel_without_changing_values() -> None:
    qt_app = QApplication.instance() or QApplication([])
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    content = QWidget()
    layout = QVBoxLayout(content)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(40)
    combo = QComboBox()
    combo.addItems(["Manual", "MIDI", "OSC"])
    layout.addWidget(slider)
    layout.addWidget(combo)
    for index in range(24):
        layout.addWidget(QLabel(f"SCROLL ROW {index:02d}"))

    scroll_area.setWidget(content)
    scroll_area.resize(280, 150)
    scroll_area.show()
    guard = WheelGuard(qt_app)
    qt_app.installEventFilter(guard)
    qt_app.processEvents()

    def wheel_over(widget: QWidget) -> None:
        local_position = QPointF(widget.width() / 2, widget.height() / 2)
        global_position = QPointF(widget.mapToGlobal(local_position.toPoint()))
        event = QWheelEvent(
            local_position,
            global_position,
            QPoint(0, 0),
            QPoint(0, -120),
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
            Qt.ScrollPhase.NoScrollPhase,
            False,
        )
        QApplication.sendEvent(widget, event)
        qt_app.processEvents()

    try:
        vertical_scroll = scroll_area.verticalScrollBar()
        initial_scroll = vertical_scroll.value()
        wheel_over(slider)
        assert slider.value() == 40
        after_slider_scroll = vertical_scroll.value()
        assert after_slider_scroll > initial_scroll

        initial_combo_index = combo.currentIndex()
        wheel_over(combo)
        assert combo.currentIndex() == initial_combo_index
        assert vertical_scroll.value() > after_slider_scroll
    finally:
        qt_app.removeEventFilter(guard)
        scroll_area.close()
        guard.deleteLater()
