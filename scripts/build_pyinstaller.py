from __future__ import annotations

import argparse
import hashlib
import os
import struct
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
REQUIREMENTS = ROOT / "requirements-build-pyinstaller.txt"
MIDI_REQUIREMENTS = ROOT / "requirements-build-pyinstaller-midi.txt"
SPEC = ROOT / "AVTranslator.spec"
EXE = ROOT / "dist" / "eli_lab AV Translator.exe"


def run(command: list[str], *, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    print("\n> " + subprocess.list2cmdline(command), flush=True)
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        check=True,
        timeout=timeout,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build eli_lab AV Translator as a Windows x64 one-file executable."
    )
    parser.add_argument(
        "--with-midi",
        action="store_true",
        help=(
            "also build/install the native python-rtmidi backend. On Python 3.14 this "
            "requires the Visual Studio 2022 C++ Build Tools and Windows SDK."
        ),
    )
    return parser.parse_args()


def relaunch_in_project_venv() -> None:
    """Avoid accidentally building in a different project's activated venv."""
    if not PROJECT_PYTHON.is_file():
        raise SystemExit(
            "Project virtual environment not found:\n"
            f"  {PROJECT_PYTHON}\n\n"
            "Create it with a 64-bit CPython 3.12, 3.13 or 3.14 installation, "
            "then select it in PyCharm."
        )

    current = Path(sys.executable).resolve()
    expected = PROJECT_PYTHON.resolve()
    if current != expected:
        print(
            "Using the AV Translator project's own .venv instead of the currently "
            "activated interpreter:\n"
            f"  {expected}",
            flush=True,
        )
        result = subprocess.run(
            [str(expected), str(Path(__file__).resolve()), *sys.argv[1:]],
            cwd=ROOT,
        )
        raise SystemExit(result.returncode)


def validate_environment() -> None:
    if os.name != "nt":
        raise SystemExit("This profile builds a native Windows executable and must run on Windows.")
    if struct.calcsize("P") * 8 != 64:
        raise SystemExit("A 64-bit Python interpreter is required for the Windows x64 executable.")
    if sys.implementation.name != "cpython" or not (3, 12) <= sys.version_info[:2] < (3, 15):
        raise SystemExit(
            "This AV Translator PyInstaller profile supports 64-bit CPython 3.12, 3.13 or 3.14.\n"
            f"Current interpreter: {sys.version.split()[0]} ({sys.implementation.name})."
        )

    required = (
        ROOT / "main.py",
        ROOT / "config.py",
        ROOT / "resources",
        ROOT / "dictionary",
        ROOT / "THIRD_PARTY_NOTICES.md",
        SPEC,
        REQUIREMENTS,
        MIDI_REQUIREMENTS,
    )
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("Missing required project/build files:\n" + "\n".join(missing))

    # main.py's packaged --self-check must treat native MIDI as optional on CPython 3.14.
    main_text = (ROOT / "main.py").read_text(encoding="utf-8")
    if '"midi_backend"' not in main_text:
        raise SystemExit(
            "Your main.py still treats rtmidi as a mandatory self-check dependency.\n"
            "Apply the included compatibility patch first:\n"
            "  git apply .\\patches\\main_optional_rtmidi.patch"
        )


def main() -> int:
    args = parse_args()
    relaunch_in_project_venv()
    validate_environment()
    python = str(PROJECT_PYTHON.resolve())

    print("=" * 72)
    print("eli_lab AV Translator — local PyInstaller one-file build")
    print(f"Python: {sys.version.split()[0]} x64")
    print(f"Environment: {PROJECT_PYTHON}")
    print(f"Native MIDI backend requested: {'yes' if args.with_midi else 'no'}")
    print("=" * 72)

    # Install the app's runtime packages and PyInstaller into the AV Translator-local .venv.
    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    run([python, "-m", "pip", "install", "-r", str(REQUIREMENTS)])
    if args.with_midi:
        print(
            "\nBuilding optional python-rtmidi from source. A working MSVC C++ toolchain "
            "and Windows SDK must be installed.",
            flush=True,
        )
        run([
            python, "-m", "pip", "install",
            "--no-binary=python-rtmidi", "-r", str(MIDI_REQUIREMENTS),
        ])
    run([python, "-m", "pip", "check"])

    # Verify the expected runtime imports before starting packaging.
    run([
        python, "-c",
        "import PySide6, moderngl, glcontext, av, numpy, soundcard, pythonosc, mido; "
        "print('Core runtime imports: PASS'); "
        "import importlib.util; "
        "print('Native MIDI backend:', "
        "'available' if importlib.util.find_spec('rtmidi') "
        "else 'not installed (optional)')",
    ])

    run([
        python, "-m", "compileall", "-q", "main.py", "config.py",
        "core", "effects", "generators", "media", "rendering", "ui",
    ])

    # PyInstaller's spec collects Qt, FFmpeg/PyAV, ModernGL/glcontext,
    # SoundCard, OSC/Mido, and the app resources/icon/dictionaries.
    run([
        python, "-m", "PyInstaller", "--clean", "--noconfirm",
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(ROOT / "build" / "pyinstaller"),
        str(SPEC),
    ])

    if not EXE.is_file():
        raise SystemExit(f"PyInstaller completed without producing the expected executable: {EXE}")

    print("\nRunning packaged --self-check ...", flush=True)
    check = subprocess.run(
        [str(EXE), "--self-check"], cwd=ROOT, text=True,
        capture_output=True, timeout=240,
    )
    if check.returncode != 0:
        details = "\n".join(part for part in (check.stdout, check.stderr) if part)
        raise SystemExit(
            "The packaged executable failed --self-check "
            f"(exit code {check.returncode}).\n{details}\n"
            "Inspect %LOCALAPPDATA%\\eli_lab\\AV Translator\\logs if available."
        )

    try:
        import importlib
        importlib.import_module("rtmidi")
        midi_available = True
    except Exception:
        midi_available = False
    size_mib = EXE.stat().st_size / (1024 * 1024)
    digest = sha256_file(EXE)
    report = (
        "eli_lab AV Translator — PyInstaller build report\n"
        f"Built (UTC): {datetime.now(UTC).isoformat()}\n"
        f"Python: {sys.version.split()[0]} x64\n"
        f"PyInstaller: {__import__('PyInstaller').__version__}\n"
        f"Native MIDI backend: {'included' if midi_available else 'not included (optional)'}\n"
        f"Executable: {EXE}\n"
        f"Size: {size_mib:.1f} MiB\n"
        f"SHA-256: {digest}\n"
        "Packaged self-check: PASS\n"
    )
    report_path = ROOT / "build" / "pyinstaller-build-report.txt"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")

    print("\n" + "=" * 72)
    print("BUILD COMPLETE")
    print(f"Executable: {EXE}")
    print(f"Size:       {size_mib:.1f} MiB")
    print(f"SHA-256:    {digest}")
    print(f"MIDI:       {'included' if midi_available else 'not included (optional backend)'}")
    print(f"Report:     {report_path}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print("\nBUILD FAILED while running:", subprocess.list2cmdline(exc.cmd), file=sys.stderr)
        raise SystemExit(exc.returncode or 1) from exc
