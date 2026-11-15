# -*- mode: python ; coding: utf-8 -*-
"""Native Windows x64 / Linux x86_64 one-file build (CPython 3.12-3.14)."""

import importlib.util
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).resolve()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import APP_NAME, ICON_PATH  # noqa: E402

# PyInstaller embeds ICO metadata on Windows. Linux executables have no
# equivalent native file-icon resource; the ICO remains bundled for Qt's UI.
ICON = ICON_PATH if sys.platform == "win32" else None

required_paths = (
    ROOT / "main.py",
    ROOT / "config.py",
    ROOT / "resources",
    ICON_PATH,
    ROOT / "dictionary",
    ROOT / "THIRD_PARTY_NOTICES.md",
)
missing = [str(path) for path in required_paths if not path.exists()]
if missing:
    raise FileNotFoundError("Required AVTranslator build inputs are missing:\n" + "\n".join(missing))

datas = [
    (str(ROOT / "resources"), "resources"),
    (str(ROOT / "dictionary"), "dictionary"),
    (str(ROOT / "THIRD_PARTY_NOTICES.md"), "."),
]
binaries = []
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtOpenGL",
    "PySide6.QtOpenGLWidgets",
]

for package in (
    "av",          # PyAV; wheel contains the FFmpeg runtime DLLs
    "moderngl",    # ModernGL renderer
    "glcontext",   # OpenGL context providers
    "soundcard",   # Windows audio loopback/input
    "pythonosc",   # Sonic Pi OSC receiver
    "mido",        # MIDI abstraction; backend is optional
):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas.extend(package_datas)
    binaries.extend(package_binaries)
    hiddenimports.extend(package_hiddenimports)

# If the builder installed the optional native MIDI backend via --with-midi,
# include its package too.
if importlib.util.find_spec("rtmidi") is not None:
    package_datas, package_binaries, package_hiddenimports = collect_all("rtmidi")
    datas.extend(package_datas)
    binaries.extend(package_binaries)
    hiddenimports.extend(package_hiddenimports)

# The PyInstaller hook for PyAV collects Windows wheel DLLs as data under
# "av.libs". Do not add a second copy as top-level binaries: that duplicates
# the FFmpeg DLL payload and defeats the hook's preserved runtime directory.


def deduplicate(items):
    seen = set()
    result = []
    for item in items:
        key = tuple(str(part) for part in item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


datas = deduplicate(datas)
binaries = deduplicate(binaries)
hiddenimports = sorted(set(hiddenimports))

analysis = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(ROOT / "scripts" / "pyinstaller_runtime.py")],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ICON) if ICON is not None else None,
)
