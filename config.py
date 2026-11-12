from __future__ import annotations

import logging
import os
from pathlib import Path

APP_NAME = "eli_lab AV Translator"
APP_VERSION = "0.5.0"
APP_AUTHOR = "Ilya Minin (Eli)"
APP_STUDIO = "eli_lab"
APP_COPYRIGHT = "© 2026 Ilya Minin (Eli) · eli_lab"
APP_REPOSITORY_URL = "https://github.com/ilyaminineli/eli_lab-av-translator"

DEFAULT_CANVAS_WIDTH = 1920
DEFAULT_CANVAS_HEIGHT = 1080
DEFAULT_FPS = 60
# Decoder output is capped to reduce RGB conversion and texture-upload bandwidth.
MAX_DECODE_WIDTH = 1920
MAX_DECODE_HEIGHT = 1080
MAX_DECODE_FPS = 30
RENDER_TARGET_FPS = 30
OPENGL_REQUIREMENT = 330
VIDEO_DECK_IDS = ("deck_a", "deck_b", "deck_c", "deck_d")


def _runtime_root() -> Path:
    """Locate bundled read-only data in source or the frozen application runtime.

    Packaged resources are read-only and separate from the executable's original
    directory. User-writable settings, logs and databases must never be placed in
    the temporary one-file extraction directory.
    """
    compiled = globals().get("__compiled__")
    runtime_dir = getattr(compiled, "python_runtime_dir", None)
    if runtime_dir:
        return Path(runtime_dir).resolve()
    return Path(__file__).resolve().parent


PROJECT_ROOT = _runtime_root()
RESOURCE_DIR = PROJECT_ROOT / "resources"
DICTIONARY_DIR = PROJECT_ROOT / "dictionary"
ICON_PATH = RESOURCE_DIR / "icons" / "Icon.ico"

if os.name == "nt":
    _app_data_root = Path(
        os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")
    )
else:
    _app_data_root = Path(
        os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
    )

DATA_DIR = _app_data_root / "eli_lab" / "AV Translator"
CACHE_DIR = DATA_DIR / "cache"
THUMBNAIL_DIR = CACHE_DIR / "thumbnails"
MEDIA_DB_PATH = DATA_DIR / "media-library.sqlite3"
LOG_DIR = DATA_DIR / "logs"


def ensure_data_directories() -> None:
    """Create only writable per-user directories; packaged resources stay read-only."""
    for directory in (DATA_DIR, CACHE_DIR, THUMBNAIL_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def configure_logging(level: int = logging.INFO) -> None:
    ensure_data_directories()
    log_file = LOG_DIR / "av-translator.log"
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )
