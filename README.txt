eli_lab AV Translator — documentation pointer

The canonical project overview is README.md.
The supported Windows x64 one-file build is PyInstaller, using the repository-local environment:

    .\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py

Build prerequisites, optional native MIDI, output paths and the packaged self-check are documented in:

    docs/BUILD_PYINSTALLER_WINDOWS.md

This file replaces an older build-note copy. Do not apply a compatibility patch to main.py; optional native MIDI handling is already part of the current source. The Windows Onefile Build GitHub Actions workflow is manual-dispatch only. Normal builds are performed locally with scripts/build_pyinstaller.py.

Current milestone state and target-machine acceptance gates:

    docs/ROADMAP.md
    docs/M5_COMPLETION_HANDOFF.md
    docs/M6_ADVANCED_VJ_ENVIRONMENT.md
