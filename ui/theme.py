from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from config import RESOURCE_DIR
from ui.hints import ToolTipFilter, WheelGuard

APP_STYLE = """
QMainWindow, QDialog, QMessageBox, QWidget {
    background: #090909;
    color: #eeeeee;
}
QWidget { font-size: 9pt; }
QLabel { background: transparent; }
QLabel#eyebrow {
    color: #858585;
    font-size: 8pt;
    padding: 2px 0;
}
QLabel#sectionHeading {
    color: #f0f0f0;
    font-size: 17pt;
    font-weight: 400;
    padding: 5px 0 8px;
}
QLabel#panelSubheading {
    color: #c8c8c8;
    font-size: 10pt;
    padding: 3px 0 5px;
}
QLabel#mutedLabel {
    color: #969696;
    font-size: 8pt;
}
QLabel#brandMark {
    font-family: "Noto Serif JP", "Yu Mincho", serif;
    font-size: 27pt;
    color: #f1f1f1;
}
QLabel#brandName {
    font-size: 8pt;
    color: #d0d0d0;
}
QMenuBar {
    background: #090909;
    color: #bdbdbd;
    border-bottom: 1px solid #252525;
    padding: 2px 8px;
    spacing: 8px;
}
QMenuBar::item {
    background: transparent;
    padding: 5px 9px;
    margin: 0 1px;
}
QMenuBar::item:selected {
    background: #171717;
    color: #ffffff;
}
QMenu {
    background: #101010;
    color: #eeeeee;
    border: 1px solid #383838;
    padding: 5px;
}
QMenu::item {
    padding: 7px 28px 7px 12px;
}
QMenu::item:selected {
    background: #e8e8e8;
    color: #090909;
}
QToolBar {
    background: #090909;
    border: 0;
    spacing: 9px;
    padding: 7px 12px;
}
QToolBar::separator {
    width: 1px;
    background: #303030;
    margin: 5px 7px;
}
QStatusBar {
    background: #101010;
    border-top: 1px solid #303030;
    color: #a3a3a3;
    padding: 3px 9px;
    min-height: 22px;
}
QStatusBar::item { border: 0; }
QDockWidget {
    background: #101010;
    color: #eeeeee;
}
QDockWidget::title {
    background: #101010;
    color: #a3a3a3;
    padding: 9px 12px;
    border: 0;
    border-bottom: 1px solid #303030;
    text-align: left;
    font-size: 8.5pt;
}
QDockWidget::close-button,
QDockWidget::float-button {
    background: transparent;
    border: 0;
    width: 15px;
    height: 15px;
    margin: 0 4px;
}
QDockWidget::close-button:hover,
QDockWidget::float-button:hover {
    background: #202020;
    border: 1px solid #555555;
}
QTabWidget::pane {
    background: #101010;
    border: 0;
    border-top: 1px solid #303030;
}
QTabBar {
    background: #090909;
    qproperty-drawBase: 0;
}
QTabBar::tab {
    background: transparent;
    color: #888888;
    padding: 11px 17px 12px;
    min-height: 26px;
    border: 0;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:hover {
    color: #eeeeee;
    background: #111111;
}
QTabBar::tab:selected {
    background: transparent;
    color: #ffffff;
    border-bottom: 2px solid #eeeeee;
}
QGroupBox {
    background: #0e0e0e;
    color: #e5e5e5;
    border: 1px solid #303030;
    border-radius: 1px;
    margin-top: 17px;
    padding: 17px 14px 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 7px;
    color: #c2c2c2;
    background: #0e0e0e;
    font-size: 8.5pt;
    letter-spacing: 1px;
}
QLabel { color: #e5e5e5; }
QLabel#sectionHeading {
    color: #f0f0f0;
    font-size: 18px;
    font-weight: 400;
    padding: 4px 0 7px;
}
QLabel#mutedLabel {
    color: #9a9a9a;
    font-size: 8.5pt;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
QPlainTextEdit, QTextEdit, QListWidget, QTreeWidget, QTableWidget {
    background: #0d0d0d;
    color: #eeeeee;
    border: 1px solid #303030;
    border-radius: 1px;
    padding: 7px 9px;
    min-height: 22px;
    selection-background-color: #dedede;
    selection-color: #090909;
}
QLineEdit:hover, QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover,
QPlainTextEdit:hover, QTextEdit:hover {
    border-color: #4a4a4a;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus {
    border: 1px solid #969696;
}
QComboBox::drop-down {
    border: 0;
    width: 22px;
}
QLabel#fieldCaption {
    color: #a3a3a3;
    font-family: "DM Mono", "Consolas", monospace;
    font-size: 8pt;
    letter-spacing: 0.08em;
}
QLabel#sliderReadout {
    color: #a3a3a3;
    font-family: "DM Mono", "Consolas", monospace;
    font-size: 8pt;
    min-height: 22px;
}
QComboBox#propertyCombo {
    font-family: "DM Mono", "Consolas", monospace;
    font-size: 8.5pt;
    letter-spacing: 0.02em;
}
QSlider#propertySlider::groove:horizontal {
    height: 2px;
    background: #3c3c3c;
}
QSlider#propertySlider::sub-page:horizontal {
    background: #cfcfcf;
}
QSlider#propertySlider::add-page:horizontal {
    background: #292929;
}
QSlider#propertySlider::handle:horizontal {
    width: 11px;
    height: 11px;
    margin: -5px 0;
    background: #eeeeee;
    border: 1px solid #eeeeee;
    border-radius: 6px;
}
QComboBox QAbstractItemView {
    background: #111111;
    color: #eeeeee;
    border: 1px solid #424242;
    selection-background-color: #dedede;
    selection-color: #090909;
    outline: 0;
}
QPushButton {
    background: #151515;
    color: #e8e8e8;
    border: 1px solid #343434;
    border-radius: 1px;
    padding: 8px 13px;
    min-height: 25px;
}
QPushButton:hover {
    background: #202020;
    border-color: #6a6a6a;
}
QPushButton:pressed {
    background: #303030;
}
QPushButton:checked {
    background: #ededed;
    color: #090909;
    border-color: #ededed;
}
QPushButton:disabled {
    background: #101010;
    color: #626262;
    border-color: #262626;
}
QToolButton {
    background: transparent;
    color: #dedede;
    border: 1px solid transparent;
    border-radius: 1px;
    padding: 5px;
}
QToolButton:hover {
    background: #181818;
    border-color: #424242;
}
QToolButton:pressed {
    background: #2c2c2c;
    border-color: #777777;
}
QToolButton:checked {
    background: #ededed;
    color: #101010;
    border-color: #ededed;
}
QToolButton:disabled {
    color: #5e5e5e;
}
QCheckBox, QRadioButton {
    spacing: 7px;
    color: #d7d7d7;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    background: #101010;
    border: 1px solid #737373;
}
QCheckBox::indicator { border-radius: 1px; }
QRadioButton::indicator { border-radius: 7px; }
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: #eeeeee;
    border-color: #eeeeee;
}
QSlider::groove:horizontal {
    height: 2px;
    background: #3c3c3c;
}
QSlider::sub-page:horizontal { background: #cfcfcf; }
QSlider::add-page:horizontal { background: #292929; }
QSlider::handle:horizontal {
    width: 11px;
    height: 11px;
    margin: -5px 0;
    background: #eeeeee;
    border: 1px solid #eeeeee;
    border-radius: 6px;
}
QProgressBar {
    background: #141414;
    border: 1px solid #303030;
    color: #eaeaea;
    text-align: center;
    min-height: 8px;
}
QProgressBar::chunk { background: #bdbdbd; }
QHeaderView::section {
    background: #121212;
    color: #a3a3a3;
    border: 0;
    border-bottom: 1px solid #303030;
    padding: 9px 11px;
}
QAbstractItemView::item {
    padding: 3px;
}
QAbstractItemView::item:selected {
    background: #dedede;
    color: #090909;
}
QScrollArea { border: 0; background: transparent; }
QSplitter::handle {
    background: #282828;
}
QSplitter::handle:hover {
    background: #595959;
}
QToolBar {
    spacing: 12px;
    min-height: 42px;
}
QDockWidget::title {
    padding: 11px 13px;
    min-height: 20px;
    font-size: 8.5pt;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #101010;
    width: 10px;
    height: 10px;
    border: 0;
    margin: 0;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #3d3d3d;
    min-height: 24px;
    min-width: 24px;
    border: 2px solid #101010;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #696969;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
QToolTip {
    background: #151515;
    color: #eeeeee;
    border: 1px solid #555555;
    padding: 5px 7px;
}
QMessageBox QLabel {
    color: #eeeeee;
    min-width: 280px;
}
QMessageBox QPushButton {
    min-width: 72px;
}
"""


def _typography_stylesheet(language: str) -> str:
    if language == "ja":
        return """
QLabel#sectionHeading {
    font-family: "Yu Mincho", "Noto Serif JP", "MS Mincho", serif;
    font-size: 17px;
    font-weight: 500;
    letter-spacing: 0px;
}
QLabel, QAbstractItemView, QToolTip,
QGroupBox::title, QDockWidget::title, QTabBar::tab,
QLabel#eyebrow, QLabel#mutedLabel, QLabel#brandName, QStatusBar,
QPushButton, QToolButton, QCheckBox, QRadioButton, QProgressBar,
QMenuBar, QMenu, QHeaderView::section,
QComboBox, QSpinBox, QDoubleSpinBox {
    font-family: "DM Mono", "Yu Gothic UI", "Meiryo UI", "Noto Sans JP", monospace;
    letter-spacing: 0.4px;
}
QLineEdit, QPlainTextEdit, QTextEdit {
    font-family: "Yu Gothic UI", "Meiryo UI", "Noto Sans JP", sans-serif;
}
QLabel#brandMark {
    font-family: "Yu Mincho", "Noto Serif JP", "MS Mincho", serif;
    font-size: 27px;
    font-weight: 500;
    color: #eeeeee;
}
QLabel#brandName {
    font-size: 8pt;
    letter-spacing: 1.1px;
    color: #d0d0d0;
}
"""
    return """
QLabel#sectionHeading, QLabel#brandMark {
    font-family: "Newsreader", "Yu Mincho", "Noto Serif JP", "Georgia", serif;
}
QLabel#brandMark {
    font-size: 27px;
    font-weight: 500;
    color: #eeeeee;
}
QLabel, QAbstractItemView, QToolTip,
QGroupBox::title, QDockWidget::title, QTabBar::tab,
QLabel#eyebrow, QLabel#mutedLabel, QLabel#brandName, QStatusBar,
QPushButton, QToolButton, QCheckBox, QRadioButton,
QMenuBar, QMenu, QHeaderView::section,
QComboBox, QSpinBox, QDoubleSpinBox {
    font-family: "DM Mono", "Consolas", "Cascadia Mono", monospace;
    letter-spacing: 0.55px;
}
QLineEdit, QPlainTextEdit, QTextEdit {
    font-family: "Segoe UI", "Noto Sans", "Arial", sans-serif;
}
QLabel#brandName {
    font-size: 8pt;
    letter-spacing: 1.1px;
    color: #d0d0d0;
}
"""


def application_font_families(language: str = "en") -> list[str]:
    """Return readable system-first UI font stacks for the selected language."""
    if language == "ja":
        return [
            "Yu Gothic UI",
            "Meiryo UI",
            "Meiryo",
            "MS UI Gothic",
            "MS PGothic",
            "MS Gothic",
            "BIZ UDGothic",
            "Noto Sans JP",
            "Noto Sans CJK JP",
            "Segoe UI",
            "sans-serif",
        ]
    return ["Segoe UI", "Noto Sans", "Arial", "sans-serif"]


def apply_application_language(app: QApplication, language: str) -> None:
    """Apply body fonts and matching editorial heading/metadata type."""
    normalized = language if language in {"en", "ja"} else "en"
    font = QFont()
    font.setFamilies(application_font_families(normalized))
    font.setPointSizeF(9.5)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    app.setProperty("ui_language", normalized)
    base_style = str(app.property("_eli_theme_base") or APP_STYLE)
    app.setStyleSheet(f"{base_style}\n{_typography_stylesheet(normalized)}")


def configure_application_theme(
    app: QApplication,
    show_hints: bool = True,
    language: str = "en",
) -> None:
    """Apply the monochrome editorial theme and system-first language fonts."""
    app.setStyle("Fusion")
    tooltip_filter = ToolTipFilter(show_hints, app)
    app.installEventFilter(tooltip_filter)
    app._eli_tooltip_filter = tooltip_filter

    wheel_guard = getattr(app, "_eli_wheel_guard", None)
    if not isinstance(wheel_guard, WheelGuard):
        wheel_guard = WheelGuard(app)
        app.installEventFilter(wheel_guard)
        app._eli_wheel_guard = wheel_guard

    icon_directory = (RESOURCE_DIR / "icons").resolve()
    close_icon = (icon_directory / "dock-close.svg").as_posix()
    float_icon = (icon_directory / "dock-float.svg").as_posix()
    dock_icon = (icon_directory / "dock-dock.svg").as_posix()
    dock_controls_style = f"""
QDockWidget::close-button,
QDockWidget::float-button {{
    image: url("{close_icon}");
    background: transparent;
    border: 0;
    width: 15px;
    height: 15px;
    margin: 0 4px;
}}
QDockWidget::float-button {{
    image: url("{float_icon}");
}}
QDockWidget::float-button:checked {{
    image: url("{dock_icon}");
}}
QDockWidget::close-button:hover,
QDockWidget::float-button:hover {{
    background: #202020;
    border: 1px solid #555555;
    border-radius: 1px;
}}
"""
    app.setProperty("_eli_theme_base", f"{APP_STYLE}\n{dock_controls_style}")
    apply_application_language(app, language)
