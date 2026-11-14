# -*- mode: python ; coding: utf-8 -*-
"""Windows x64 one-file build for eli_lab AV Translator (CPython 3.12-3.14)."""

from pathlib import Path
import importlib.util
import sysconfig

from PyInstaller.utils.hooks import collect_all

ROOT = Path(SPECPATH).resolve()
ICON = ROOT / "resources" / "icons" / "Icon.ico"

required_paths = (
    ROOT / "main.py",
    ROOT / "config.py",
    ROOT / "resources",
    ROOT / "resources" / "icons" / "Icon.ico",
    ROOT / "dictionary",
    ROOT / "THIRD_PARTY_NOTICES.md",
)
missing = [str(path) for path in required_paths if not path.exists()]
if missing:
    raise FileNotFoundError("Required AV Translator build inputs are missing:\n" + "\n".join(missing))

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
    "qt_material", # Qt Widgets stylesheet and theme assets
    "mido",        # MIDI abstraction; backend is optional
):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas.extend(package_datas)
    binaries.extend(package_binaries)
    hiddenimports.extend(package_hiddenimports)

# python-rtmidi currently has no CPython 3.14 Windows wheel. If the builder
# compiled/installed it from source via --with-midi, include its package too.
if importlib.util.find_spec("rtmidi") is not None:
    package_datas, package_binaries, package_hiddenimports = collect_all("rtmidi")
    datas.extend(package_datas)
    binaries.extend(package_binaries)
    hiddenimports.extend(package_hiddenimports)

# Keep any PyAV wheel auxiliary DLL directory, if the installed wheel uses one.
site_packages = Path(sysconfig.get_paths()["purelib"])
for libs_dir in site_packages.glob("av.libs"):
    binaries.extend((str(dll), ".") for dll in libs_dir.rglob("*.dll"))


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
    name="eli_lab AV Translator",
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
    icon=str(ICON),
)
