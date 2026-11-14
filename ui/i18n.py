from __future__ import annotations

from typing import Any

_ENGLISH: dict[str, str] = {
    "menu.file": "File",
    "menu.view": "View",
    "menu.help": "Help",
    "menu.about": "About",
    "menu.settings": "Settings",
    "menu.new": "&New Project",
    "menu.open": "&Open Project…",
    "menu.save": "&Save Project",
    "menu.save_as": "Save Project &As…",
    "menu.save_set": "Save Performance Set…",
    "menu.load_set": "Load Performance Set…",
    "menu.add_folder": "Add Media &Folder…",
    "menu.add_overlay": "Add Image / Video Overlay…",
    "menu.exit": "E&xit",
    "menu.restore_layout": "Restore Default Layout",
    "menu.workspace": "WORKSPACE",
    "menu.projector": "PROJECTOR OUTPUT",
    "workspace.perf": "01  PERF",
    "workspace.compose": "02  COMPOSE",
    "workspace.prepare": "03  PREPARE",
    "workspace.live_perf": "LIVE PERF",
    "button.open_perf": "OPEN PERF",
    "settings.title": "Settings",
    "settings.language": "Language",
    "settings.interface": "Interface",
    "settings.show_hints": "Show hover hints",
    "settings.restore_session": "Restore last session",
    "settings.session": "Session",
    "settings.save": "Apply",
    "settings.cancel": "Cancel",
    "about.tagline": "A live audiovisual instrument for video, generative graphics and music.",
    "about.project": "Project",
    "about.created": "Created by",
    "status.recovered": "Last session restored.",
}
_JAPANESE: dict[str, str] = {
    "menu.file": "ファイル",
    "menu.view": "表示",
    "menu.help": "ヘルプ",
    "menu.about": "このアプリについて",
    "menu.settings": "設定",
    "menu.new": "新規プロジェクト",
    "menu.open": "プロジェクトを開く…",
    "menu.save": "プロジェクトを保存",
    "menu.save_as": "名前を付けて保存…",
    "menu.save_set": "パフォーマンスセットを保存…",
    "menu.load_set": "パフォーマンスセットを読み込む…",
    "menu.add_folder": "メディアフォルダーを追加…",
    "menu.add_overlay": "画像／動画オーバーレイを追加…",
    "menu.exit": "終了",
    "menu.restore_layout": "レイアウトを初期化",
    "menu.workspace": "ワークスペース",
    "menu.projector": "プロジェクター出力",
    "workspace.perf": "01  PERF",
    "workspace.compose": "02  COMPOSE",
    "workspace.prepare": "03  PREPARE",
    "workspace.live_perf": "ライブパフォーマンス",
    "button.open_perf": "PERFを開く",
    "settings.title": "設定",
    "settings.language": "言語",
    "settings.interface": "インターフェース",
    "settings.show_hints": "マウスオーバー時にヒントを表示",
    "settings.restore_session": "前回のセッションを復元",
    "settings.session": "セッション",
    "settings.save": "適用",
    "settings.cancel": "キャンセル",
    "about.tagline": "映像・生成表現・音楽をつなぐライブ映像制作ツール。",
    "about.project": "プロジェクト",
    "about.created": "制作",
    "status.recovered": "前回のセッションを復元しました。",
}


def tr(key: str, language: str = "en", **values: Any) -> str:
    catalog = _JAPANESE if language == "ja" else _ENGLISH
    template = catalog.get(key, _ENGLISH.get(key, key))
    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return template
