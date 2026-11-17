from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QFont, QFontDatabase, QFontMetrics, QImage, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.i18n import apply_widget_translations
from ui.theme import configure_application_theme


def render_preview(destination: Path) -> None:
    application = QApplication.instance() or QApplication([])
    configure_application_theme(application, show_hints=True, language="ja")

    # The Windows GitHub runner may not have Japanese optional language fonts.
    # Load a test-only font supplied by CI, without bundling it with the app.
    proof_font_path = os.environ.get("ELI_JP_PROOF_FONT", "").strip()
    if proof_font_path:
        font_id = QFontDatabase.addApplicationFont(proof_font_path)
        if font_id < 0:
            raise RuntimeError(f"Could not load Japanese proof font: {proof_font_path}")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if not font_families:
            raise RuntimeError("Japanese proof font did not expose a font family.")
        font_family = str(font_families[0])
    else:
        installed = set(QFontDatabase.families())
        font_family = next(
            (
                family
                for family in (
                "Yu Gothic UI",
                "Meiryo UI",
                "BIZ UDGothic",
                "Noto Sans JP",
            )
                if family in installed
            ),
            "",
        )
    if not font_family:
        raise RuntimeError(
            "No Japanese font is available. Install a Windows Japanese font or "
            "set ELI_JP_PROOF_FONT to a test font file."
        )

    proof_font = QFont(font_family)
    proof_font.setPointSizeF(10)
    application.setFont(proof_font)
    font_metrics = QFontMetrics(proof_font)
    sample = "映像を、演奏する。日本語タイポグラフィ"
    missing_glyphs = [
        character for character in sample if not font_metrics.inFontUcs4(ord(character))
    ]
    if missing_glyphs:
        raise RuntimeError(
            f"Japanese proof font {font_family!r} is missing glyphs: "
            + "".join(sorted(set(missing_glyphs)))
        )
    print(f"Japanese UI proof font: {font_family}")

    window = QWidget()
    window.setWindowTitle("eli_lab AVTranslator — 日本語 UI")
    window.resize(1280, 720)
    root = QVBoxLayout(window)
    root.setContentsMargins(42, 36, 42, 36)
    root.setSpacing(20)

    index = QLabel("eli_lab / AVTranslator    —    JAPANESE UI PROOF")
    index.setObjectName("mutedLabel")
    root.addWidget(index)

    title = QLabel("映像を、演奏する。")
    title.setObjectName("sectionHeading")
    title.setStyleSheet("font-size: 30px; font-weight: 600;")
    root.addWidget(title)

    description = QLabel(
        "映像素材、生成グラフィックス、タイポグラフィを音楽とともに動かす。"
        " 日本語と English の文字組みを同じ画面で確認します。"
    )
    description.setWordWrap(True)
    root.addWidget(description)

    workspace = QHBoxLayout()
    for label in ("01  PERF", "02  COMPOSE", "03  PREPARE"):
        item = QLabel(label)
        item.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setMinimumHeight(48)
        item.setStyleSheet("border: 1px solid #555; padding: 8px;")
        workspace.addWidget(item)
    root.addLayout(workspace)

    group = QGroupBox("メディアと素材")
    group_layout = QVBoxLayout(group)
    search = QLabel("テクスチャ、マテリアル、マスクを検索…")
    group_layout.addWidget(search)
    choices = QComboBox()
    choices.addItems(["All media", "Images", "Videos"])
    group_layout.addWidget(choices)
    lock = QCheckBox("前回のセッションを復元")
    group_layout.addWidget(lock)
    buttons = QHBoxLayout()
    buttons.addWidget(QPushButton("素材フォルダーを追加"))
    buttons.addWidget(QPushButton("プロジェクトを保存"))
    group_layout.addLayout(buttons)
    root.addWidget(group)

    status = QLabel("ローカルプレビュー準備完了 · OpenGL 3.3 Core")
    status.setObjectName("mutedLabel")
    root.addWidget(status)
    root.addStretch(1)

    apply_widget_translations(window, "ja")
    window.show()
    application.processEvents()

    image = QImage(1280, 720, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor("#090909"))
    painter = QPainter(image)
    window.render(painter, QPoint())
    painter.end()

    destination.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(destination), "PNG"):
        raise RuntimeError(f"Could not save typography proof to {destination}")
    window.close()


if __name__ == "__main__":
    output = Path("artifacts/japanese-ui-proof.png")
    render_preview(output)
    print(f"Japanese UI proof written to {output.resolve()}")
