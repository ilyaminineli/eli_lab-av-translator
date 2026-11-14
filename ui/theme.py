from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from qt_material import apply_stylesheet


DEFAULT_THEME = "dark_red.xml"
DENSITY_SCALE = "-1"

APP_STYLE = """
QMainWindow {
    background: #0b0b0e;
}
QDockWidget {
    background: #101014;
}
QDockWidget::title {
    background: #18181d;
    color: #d9d9df;
    padding: 7px 9px;
    border-bottom: 1px solid #29292f;
    font-weight: 700;
    letter-spacing: 1px;
}
QToolBar {
    background: #0b0b0e;
    border: 0;
    spacing: 6px;
    padding: 4px 7px;
}
QStatusBar {
    background: #101014;
    border-top: 1px solid #29292f;
    color: #a9a9b2;
}
QTabWidget::pane {
    background: #101014;
    border: 1px solid #29292f;
}
QTabBar::tab {
    background: #141418;
    color: #a9a9b2;
    padding: 8px 14px;
    min-height: 22px;
    border: 0;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    background: #202026;
    color: #ffffff;
    border-bottom: 2px solid #e3303d;
}
QLabel#sectionHeading {
    color: #f0eff2;
    font-weight: 800;
    letter-spacing: 1.2px;
}
QLabel#mutedLabel {
    color: #92929d;
}
QPushButton {
    text-transform: none;
}
QPushButton:checked {
    background: #a91f2c;
    color: #ffffff;
}
QScrollArea {
    border: 0;
    background: transparent;
}
"""


def configure_application_theme(app: QApplication) -> None:
    """Apply the Widgets theme and AV Translator's shared visual tokens."""
    apply_stylesheet(
        app,
        theme=DEFAULT_THEME,
        extra={"density_scale": DENSITY_SCALE},
    )
    app.setFont(QFont("Segoe UI", 9))
    app.setStyleSheet(f"{app.styleSheet()}\n{APP_STYLE}")
