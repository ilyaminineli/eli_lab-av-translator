from __future__ import annotations

import os
import sqlite3

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget

from config import RESOURCE_DIR
from core.automation import AutomationSettings
from core.composition import Layer
from core.performance_manager import PerformanceManager
from generators.catalog import default_generator_settings, normalize_settings
from generators.text_pools import random_text_sample
from media.library import MediaLibrary
from ui.deck_panel import deck_columns_for_width
from ui.icons import app_icon, icon_button
from ui.theme import configure_application_theme


def test_manual_layout_randomizer_uses_video_generator_and_overlay_layers() -> None:
    layers = [
        Layer(
            id="video-background",
            source_type="video",
            source_id="deck_a",
            z_index=0,
        ),
        Layer(
            id="text-headline",
            source_type="generator",
            generator_type="text",
            source_id="generator:text",
            z_index=1,
        ),
        Layer(
            id="geometry",
            source_type="generator",
            generator_type="geometry",
            source_id="generator:geometry",
            z_index=2,
        ),
        Layer(
            id="overlay",
            source_type="overlay",
            source_id="overlay:one",
            z_index=3,
        ),
        Layer(
            id="locked",
            source_type="video",
            source_id="deck_b",
            locked=True,
            position=(0.1, 0.2),
            scale=(0.3, 0.4),
            rotation=12.0,
            z_index=4,
        ),
        Layer(
            id="hidden",
            source_type="video",
            source_id="deck_c",
            visible=False,
            position=(0.8, 0.9),
            scale=(0.6, 0.7),
            rotation=-9.0,
            z_index=5,
        ),
    ]
    protected = {
        layer.id: (
            layer.position,
            layer.scale,
            layer.rotation,
            layer.opacity,
            layer.blend_mode,
            layer.z_index,
        )
        for layer in layers if layer.locked or not layer.visible
    }

    manager = PerformanceManager(seed=29)
    changed = manager.randomize_layout(layers)

    assert changed == 4
    assert next(
        layer for layer in layers if layer.id == "video-background"
    ).z_index == -1
    text_layer = next(layer for layer in layers if layer.id == "text-headline")
    highest_other_visible_layer = max(
        layer.z_index
        for layer in layers
        if layer.visible and layer.id != text_layer.id
    )
    assert text_layer.z_index > highest_other_visible_layer
    assert text_layer.scale[0] >= 1.02
    assert text_layer.scale[1] >= 1.02
    for layer in layers:
        if layer.id in protected:
            assert (
                layer.position,
                layer.scale,
                layer.rotation,
                layer.opacity,
                layer.blend_mode,
                layer.z_index,
            ) == protected[layer.id]


def test_manual_layout_randomizer_does_not_mutate_locked_or_hidden_only_layers() -> None:
    layers = [
        Layer(id="locked", source_type="video", locked=True),
        Layer(id="hidden", source_type="video", visible=False),
    ]

    assert PerformanceManager(seed=2).randomize_layout(layers) == 0


def test_new_text_generators_default_to_headline_led_eight_fragment_collages() -> None:
    settings = default_generator_settings("text")
    normalized = normalize_settings("text", {})

    assert settings["text_pool_count"] == 8
    assert normalized["text_pool_count"] == 8
    assert settings["text_layout"] == "collage"
    assert settings["font_weight"] == 800
    assert AutomationSettings().text_fragments == 8


def test_default_text_pool_sample_contains_eight_fragments() -> None:
    sample = random_text_sample(seed=8, use_dictionary=False)

    assert len([line for line in sample.splitlines() if line.strip()]) == 8



def test_video_deck_grid_reflows_at_compact_and_wide_widths() -> None:
    assert deck_columns_for_width(420) == 1
    assert deck_columns_for_width(820) == 2
    assert deck_columns_for_width(1360) == 4



def test_media_library_repairs_legacy_txt_columns_without_losing_indexed_data(
        tmp_path,
) -> None:
    database_path = tmp_path / "media.sqlite3"
    thumbnail_directory = tmp_path / "thumbnails"

    with sqlite3.connect(database_path) as connection:
        connection.executescript(
            """
            CREATE TABLE assets (
                id TXT PRIMARY KEY,
                path TXT NOT NULL UNIQUE,
                collection_id TXT NOT NULL,
                name TXT NOT NULL,
                duration REAL,
                width INTEGER,
                height INTEGER,
                fps REAL,
                codec TXT,
                thumbnail_path TXT,
                status TXT NOT NULL,
                file_size INTEGER NOT NULL,
                modified_at REAL NOT NULL
            );
            CREATE TABLE collections (
                id TXT PRIMARY KEY,
                root_path TXT NOT NULL,
                name TXT NOT NULL,
                imported_at REAL NOT NULL
            );
            CREATE INDEX idx_assets_collection ON assets(collection_id);
            """
        )
        connection.execute(
            """
            INSERT INTO assets (
                id, path, collection_id, name, duration, width, height, fps,
                codec, thumbnail_path, status, file_size, modified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "asset-1", "/media/example.mp4", "collection-1", "example.mp4",
                12.5, 1920, 1080, 30.0, "h264", None, "ready", 1234, 42.0,
            ),
        )
        connection.execute(
            """
            INSERT INTO collections (id, root_path, name, imported_at)
            VALUES (?, ?, ?, ?)
            """,
            ("collection-1", "/media", "media", 42.0),
        )

    MediaLibrary(
        database_path=database_path,
        thumbnail_directory=thumbnail_directory,
    )

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        asset_columns = {
            row["name"]: row["type"]
            for row in connection.execute("PRAGMA table_info(assets)")
        }
        collection_columns = {
            row["name"]: row["type"]
            for row in connection.execute("PRAGMA table_info(collections)")
        }
        asset = connection.execute(
            "SELECT id, path, collection_id, name, codec FROM assets WHERE id=?",
            ("asset-1",),
        ).fetchone()
        collection = connection.execute(
            "SELECT id, root_path, name FROM collections WHERE id=?",
            ("collection-1",),
        ).fetchone()
        index = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name='idx_assets_collection'"
        ).fetchone()

    for name in (
            "id", "path", "collection_id", "name", "codec",
            "thumbnail_path", "status",
    ):
        assert asset_columns[name] == "TEXT"
    for name in ("id", "root_path", "name"):
        assert collection_columns[name] == "TEXT"

    assert tuple(asset) == (
        "asset-1", "/media/example.mp4", "collection-1", "example.mp4", "h264"
    )
    assert tuple(collection) == ("collection-1", "/media", "media")
    assert index is not None



def test_monochrome_icon_set_renders_and_keeps_accessible_actions() -> None:
    application = QApplication.instance() or QApplication([])
    configure_application_theme(application)
    stylesheet = application.styleSheet()
    assert "QDockWidget::close-button" in stylesheet
    assert "QDockWidget::float-button" in stylesheet
    assert "dock-close.svg" in stylesheet
    assert "dock-float.svg" in stylesheet
    assert 'url("file:' not in stylesheet
    for icon_name in ("dock-close.svg", "dock-float.svg", "dock-dock.svg"):
        icon_path = (RESOURCE_DIR / "icons" / icon_name).resolve().as_posix()
        assert f'url("{icon_path}")' in stylesheet
    parent = QWidget()
    icon_names = (
        "play", "pause", "stop", "load", "restart", "shuffle", "layout",
        "sparkles", "lock", "unlock", "trash", "apply", "reset", "settings",
        "warning", "library", "image", "menu", "close", "float", "dock",
    )

    for name in icon_names:
        icon = app_icon(name)
        assert not icon.isNull()
        assert not icon.pixmap(24, 24, QIcon.Mode.Disabled).isNull()

    checked_icon = app_icon("lock").pixmap(
        24, 24, QIcon.Mode.Normal, QIcon.State.On
    )
    assert not checked_icon.isNull()

    for icon_name in ("dock-close.svg", "dock-float.svg", "dock-dock.svg"):
        assert (RESOURCE_DIR / "icons" / icon_name).is_file()

    button = icon_button(parent, "settings", "Media library tools", checkable=True)
    assert button.toolTip() == "Media library tools"
    assert button.accessibleName() == "Media library tools"
    assert button.isCheckable()
    assert application is not None
