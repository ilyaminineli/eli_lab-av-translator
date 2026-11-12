# Windows one-file build guide — current entry point

The previous contents of this document described an older PySide deployment/Nuitka build profile and an obsolete release branch. Those instructions are no longer current.

The supported local Windows x64 packaging path is **PyInstaller**:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
```

Follow [BUILD_PYINSTALLER_WINDOWS.md](BUILD_PYINSTALLER_WINDOWS.md) for current prerequisites, supported CPython versions, optional native MIDI, output paths and the limits of the packaged self-check.

The GitHub **Windows Onefile Build** workflow is manual-dispatch only. It is not triggered by ordinary pushes or pull requests. The local script above is the normal build workflow.
