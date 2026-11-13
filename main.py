from __future__ import annotations

import importlib
import json
import logging
import sys

from PySide6.QtGui import QIcon, QSurfaceFormat
from PySide6.QtWidgets import QApplication

from config import APP_NAME, APP_VERSION, ICON_PATH, configure_logging
from core.application import Application
from ui.main_window import MainWindow


def configure_opengl() -> None:
    """Request a predictable OpenGL context before QApplication is created."""
    surface_format = QSurfaceFormat()
    surface_format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
    surface_format.setVersion(3, 3)
    surface_format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    surface_format.setDepthBufferSize(0)
    surface_format.setStencilBufferSize(0)
    surface_format.setSamples(0)
    QSurfaceFormat.setDefaultFormat(surface_format)


def self_check() -> int:
    """Verify packaged imports and read-only assets without opening a GUI or GL context."""
    from config import DICTIONARY_DIR, ICON_PATH, RESOURCE_DIR

    errors: list[str] = []
    checks: dict[str, object] = {}

    modules = (
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "PySide6.QtOpenGLWidgets",
        "moderngl",
        "glcontext",
        "av",
        "numpy",
        "soundcard",
        "pythonosc",
        "mido",
    )
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            checks[module_name] = "ok"
        except Exception as exc:
            checks[module_name] = f"ERROR: {type(exc).__name__}: {exc}"
            errors.append(f"{module_name}: {exc}")

    # Native MIDI is an optional project extra. Keep the application usable on
    # Python versions without a matching python-rtmidi wheel/build.
    try:
        importlib.import_module("rtmidi")
        checks["midi_backend"] = "available"
    except Exception as exc:
        checks["midi_backend"] = f"optional unavailable: {type(exc).__name__}: {exc}"

    try:
        import av

        checks["ffmpeg_libraries"] = {
            name: str(version) for name, version in av.library_versions.items()
        }
        checks["h264_decoder"] = "h264" in av.codecs_available
        if not checks["h264_decoder"]:
            errors.append(
                "The bundled PyAV/FFmpeg runtime does not expose an H.264 decoder."
            )
    except Exception as exc:
        checks["ffmpeg_libraries"] = f"ERROR: {exc}"
        errors.append(f"PyAV/FFmpeg: {exc}")

    checks["icon"] = ICON_PATH.is_file()
    checks["textures"] = (RESOURCE_DIR / "textures").is_dir()
    checks["sketches"] = (RESOURCE_DIR / "sketches_and_strokes").is_dir()
    dictionary_files = list(DICTIONARY_DIR.glob("*.txt"))
    checks["dictionary_text_files"] = len(dictionary_files)
    for name, passed in (
            ("icon", bool(checks["icon"])),
            ("textures", bool(checks["textures"])),
            ("sketches", bool(checks["sketches"])),
            ("dictionary", len(dictionary_files) > 0),
    ):
        if not passed:
            errors.append(f"Bundled resource check failed: {name}")

    checks["opengl"] = "requires a real display/GPU; not tested by --self-check"
    report = {
        "application": APP_NAME,
        "version": APP_VERSION,
        "runtime_root": str(RESOURCE_DIR.parent),
        "checks": checks,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


def main() -> int:
    if "--self-check" in sys.argv:
        return self_check()
    configure_logging()
    configure_opengl()

    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName(APP_NAME)
    qt_app.setApplicationVersion(APP_VERSION)
    qt_app.setOrganizationName("eli_lab")

    if ICON_PATH.exists():
        qt_app.setWindowIcon(QIcon(str(ICON_PATH)))

    application = Application()
    window = MainWindow(application)
    application.set_window(window)
    window.show()

    logging.getLogger(__name__).info("%s %s started", APP_NAME, APP_VERSION)
    return qt_app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
