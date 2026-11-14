from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

# Neutral Material base; all application accents are overridden to grayscale below.
DEFAULT_THEME = "dark_teal.xml"
DENSITY_SCALE = "-1"

MATERIAL_COLORS = {
    "density_scale": DENSITY_SCALE,
    "primaryColor": "#bdbdbd",
    "primaryLightColor": "#f0f0f0",
    "secondaryColor": "#242424",
    "secondaryLightColor": "#3a3a3a",
    "secondaryDarkColor": "#101010",
    "primaryTextColor": "#090909",
    "secondaryTextColor": "#f0f0f0",
    "disabledTextColor": "#666666",
    "iconColor": "#eeeeee",
    "backgroundColor": "#090909",
    "paperColor": "#151515",
}

APP_STYLE = """
QMainWindow, QDialog {
    background: #090909;
    color: #eeeeee;
}
QDockWidget {
    background: #101010;
    color: #eeeeee;
}
QDockWidget::title {
    background: #151515;
    color: #f0f0f0;
    padding: 6px 9px;
    border-bottom: 1px solid #303030;
    font-weight: 700;
}
QToolBar {
    background: #090909;
    border: 0;
    spacing: 5px;
    padding: 3px 6px;
}
QStatusBar {
    background: #101010;
    border-top: 1px solid #303030;
    color: #c7c7c7;
}
QTabWidget::pane {
    background: #101010;
    border: 1px solid #303030;
}
QTabBar::tab {
    background: #141414;
    color: #a8a8a8;
    padding: 7px 13px;
    min-height: 21px;
    border: 0;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    background: #222222;
    color: #ffffff;
    border-bottom: 2px solid #f0f0f0;
}
QGroupBox {
    background: transparent;
    color: #eeeeee;
    border: 1px solid #303030;
    border-radius: 3px;
    margin-top: 9px;
    padding: 7px 6px 5px 6px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
    color: #e6e6e6;
    font-weight: 700;
}
QLabel {
    color: #e5e5e5;
}
QLabel#sectionHeading {
    color: #ffffff;
    font-weight: 800;
    letter-spacing: 1px;
}
QLabel#mutedLabel {
    color: #a3a3a3;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
QPlainTextEdit, QTextEdit, QListWidget, QTreeWidget, QTableWidget {
    background: #101010;
    color: #eeeeee;
    border: 1px solid #383838;
    selection-background-color: #dedede;
    selection-color: #090909;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QPlainTextEdit:focus, QTextEdit:focus {
    border: 1px solid #d0d0d0;
}
QPushButton {
    background: #1b1b1b;
    color: #e8e8e8;
    border: 1px solid #3b3b3b;
    border-radius: 3px;
    padding: 5px 9px;
}
QPushButton:hover {
    background: #292929;
    border-color: #777777;
}
QPushButton:pressed {
    background: #363636;
}
QPushButton:checked {
    background: #ededed;
    color: #090909;
    border-color: #ededed;
}
QPushButton:disabled {
    background: #141414;
    color: #666666;
    border-color: #292929;
}
QToolButton {
    background: #1b1b1b;
    color: #e8e8e8;
    border: 1px solid #3b3b3b;
    border-radius: 3px;
    padding: 2px;
}
QToolButton:hover {
    background: #303030;
    border-color: #858585;
}
QToolButton:pressed {
    background: #e8e8e8;
}
QToolButton:checked {
    background: #ededed;
    border-color: #ededed;
}
QToolButton:disabled {
    background: #141414;
    border-color: #292929;
}
QCheckBox {
    spacing: 6px;
    color: #d9d9d9;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    background: #101010;
    border: 1px solid #777777;
    border-radius: 2px;
}
QCheckBox::indicator:checked {
    background: #eeeeee;
    border-color: #eeeeee;
}
QSlider::groove:horizontal {
    height: 3px;
    background: #414141;
}
QSlider::sub-page:horizontal {
    background: #d8d8d8;
}
QSlider::add-page:horizontal {
    background: #303030;
}
QSlider::handle:horizontal {
    width: 10px;
    margin: -5px 0;
    background: #f0f0f0;
    border: 1px solid #f0f0f0;
    border-radius: 5px;
}
QProgressBar {
    background: #1a1a1a;
    border: 1px solid #383838;
    color: #eaeaea;
    text-align: center;
}
QProgressBar::chunk {
    background: #bdbdbd;
}
QMenu {
    background: #151515;
    color: #eeeeee;
    border: 1px solid #3a3a3a;
}
QMenu::item {
    padding: 5px 24px 5px 10px;
}
QMenu::item:selected {
    background: #e6e6e6;
    color: #090909;
}
QAbstractItemView::item:selected {
    background: #dedede;
    color: #090909;
}
QHeaderView::section {
    background: #191919;
    color: #dedede;
    border: 0;
    border-bottom: 1px solid #3a3a3a;
    padding: 4px 6px;
}
QScrollArea {
    border: 0;
    background: transparent;
}
QScrollBar:vertical, QScrollBar:horizontal {
    background: #101010;
    border: 0;
    margin: 0;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #454545;
    min-height: 22px;
    min-width: 22px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #666666;
}
QScrollBar::add-line, QScrollBar::sub-line {
    width: 0;
    height: 0;
}
QToolTip {
    background: #171717;
    color: #f0f0f0;
    border: 1px solid #555555;
    padding: 4px;
}
"""


def configure_application_theme(app: QApplication) -> None:
    """Apply a compact, high-contrast monochrome Qt Material theme."""
    apply_stylesheet(
        app,
        theme=DEFAULT_THEME,
        extra=MATERIAL_COLORS,
    )
    app.setFont(QFont("Segoe UI", 9))
    app.setStyleSheet(f"{app.styleSheet()}\n{APP_STYLE}")
