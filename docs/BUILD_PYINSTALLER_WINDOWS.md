# Windows one-file build with PyInstaller

## Supported build path

The supported local Windows x64 one-file build is:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
```

The project-local `.venv` is required. The script automatically relaunches itself through that environment if another Python environment is active.

## Build machine

- Windows 10/11 x64.
- 64-bit CPython 3.12, 3.13 or 3.14.
- Internet access for the pinned Python wheels/build dependencies.
- Enough free disk space for the virtual environment, PyInstaller work directory and final executable.
- Visual Studio C++ Build Tools are **not required** for the normal build. They are needed only if you choose to compile the optional native MIDI backend.

Create the project environment once, choosing an installed interpreter:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Use `py -3.12` or `py -3.13` instead if preferred. Do not substitute another project's active virtual environment.

## What the build script does

`scripts/build_pyinstaller.py`:

1. Verifies Windows x64 and 64-bit CPython 3.12–3.14.
2. Verifies the source files, resource folders, dictionaries and PyInstaller spec are present.
3. Installs/updates pip and installs `requirements-build-pyinstaller.txt` in the project-local environment.
4. Runs `pip check` and checks the runtime imports.
5. Compiles the application modules.
6. Runs PyInstaller using `AVTranslator.spec` to produce a one-file windowed executable.
7. Runs the packaged executable with `--self-check`.
8. Writes `build\pyinstaller-build-report.txt` with runtime/build versions, executable size and SHA-256.

Output:

`dist\eli_lab AV Translator.exe`

No compatibility patch to `main.py` is required. The current self-check treats native `rtmidi` as optional.

## Optional native MIDI hardware input

The default build includes the `mido` abstraction and does not require `python-rtmidi`. To attempt to include the native MIDI backend:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py --with-midi
```

This compiles `python-rtmidi` from source and requires Visual Studio 2022 Build Tools with **Desktop development with C++** and the Windows SDK. Native MIDI is optional; Sonic Pi OSC integration does not depend on it.

## Target computer

The target computer needs Windows 11 x64 and a graphics driver supporting OpenGL 3.3 Core Profile. It does not need Python, pip, PyInstaller, FFmpeg or Visual Studio. Sonic Pi, GPU drivers, audio devices, source video, project files and user-added assets remain external.

Run the executable with `--self-check` to validate packaged Python imports and bundled resources. The check does **not** initialize OpenGL, enumerate MIDI devices, test loopback capture, exercise projector output, run four video decks or measure long-duration performance. Those checks must be performed on the actual performance machine.

## GitHub Actions workflow

The repository's **Windows Onefile Build** workflow is manual-dispatch only. It is an optional CI build path and does not run automatically on pushes or pull requests. The regular local build command remains `scripts/build_pyinstaller.py`.
