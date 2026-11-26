# Windows one-file build guide — current entry point

The previous contents of this document described a superseded one-file packaging profile and an obsolete release branch. Those instructions are no longer current.

The supported local Windows x64 packaging path is **PyInstaller**:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
```

Follow [BUILD_PYINSTALLER_WINDOWS.md](BUILD_PYINSTALLER_WINDOWS.md) for current prerequisites, supported CPython versions, optional native MIDI, output paths and the limits of the packaged self-check.

The GitHub **Windows Onefile Build** workflow is manual-dispatch only. It is not triggered by ordinary pushes or pull requests. The local script above is the normal build workflow.

# Windows one-file build with PyInstaller

This document covers the Windows-specific local build and Windows extraction troubleshooting. To build both Windows x64 and Linux x86_64 in a single GitHub Actions run, see [Cross-platform versioned builds](BUILD_CROSS_PLATFORM.md).

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
- At least 2 GiB free on both the project/build volume and the configured build-temp volume; 5 GiB or more is recommended for a full Qt/FFmpeg one-file build.
- Visual Studio C++ Build Tools are **not required** for the normal build. They are needed only if you choose to compile the optional native MIDI backend.

Create the project environment once, choosing an installed interpreter:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Use `py -3.12` or `py -3.13` instead if preferred. Do not substitute another project's active virtual environment.

## Build identity, icon and fonts

The build reads the application display name, version and final `eli-lab-mark.ico` from the application configuration. The PyInstaller spec derives the executable filename and icon from that configuration. A preflight check verifies that `config.APP_VER` matches the project version in `pyproject.toml` and that the final icon exists before packaging.

The UI resolves Newsreader, DM Mono, Segoe UI, Yu Gothic UI and Japanese display/body fallbacks from installed system fonts. No additional pip dependency or bundled font binary is required for the typography pass. The spec collects the complete `resources/` tree, including the final application seal.

PyAV's Windows wheel stores FFmpeg DLLs in the sibling `av.libs/` directory. The pinned PyInstaller hooks-contrib set supplies `hook-av`, which preserves this directory in the bundle. Do not manually add the same DLLs again as root-level binaries: that creates duplicate copies and increases one-file extraction size.

## What the build script does

`scripts/build_pyinstaller.py`:

1. Verifies Windows x64 and 64-bit CPython 3.12–3.14.
2. Verifies the source files, resource folders, dictionaries and PyInstaller spec are present.
3. Creates `build\tmp` and `build\tmp\pip-cache`, then redirects `TEMP`, `TMP`, `TMPDIR` and `PIP_CACHE_DIR` there. This avoids relying on a nearly-full Windows system temp drive when the project lives on another volume. The build reports free space and stops if either volume has less than 2 GiB available.
4. Installs/updates pip and installs `requirements-build-pyinstaller.txt`, including the matching setuptools/wheel build tools and pinned PyInstaller hook set.
5. Refreshes local editable metadata with `pip install --no-deps --no-build-isolation --force-reinstall -e .`. The build-system requirements are already installed in the project venv, so pip does not create a second isolated build environment.
6. Runs `pip check` and checks the runtime imports.
7. Compiles the application modules.
8. Runs PyInstaller using `AVTranslator.spec` to produce a one-file windowed executable.
9. Runs the packaged executable with `--self-check`.
10. Writes `build\pyinstaller-build-report.txt` with application, Python and PyInstaller versions, resolved runtime package versions, icon path, executable size and SHA-256.

Output:

`dist\eli_lab AVTranslator.exe`

No compatibility patch to `main.py` is required. The current self-check treats native `rtmidi` as optional.

## Temporary extraction on the target computer

A one-file executable extracts its embedded Python and native DLLs to a temporary directory before starting. On Windows, PyInstaller normally uses the directory selected by `TEMP` / `TMP`. If the EXE reports an extraction/write error for an FFmpeg DLL (for example `swscale-*.dll` with decompression return code `-1`), first check free space and write access on that temporary volume. In PyInstaller's bootloader, `-1` is the zlib I/O error used when writing the extracted file fails; it is not, by itself, proof of a missing FFmpeg DLL or a corrupt FFmpeg package.

For a one-time test with the EXE on F:, you can direct that process to a roomy folder on F::

```powershell
New-Item -ItemType Directory -Force F:\AVTranslatorTemp | Out-Null
$env:TEMP = "F:\AVTranslatorTemp"
$env:TMP = $env:TEMP
& ".\dist\eli_lab AVTranslator.exe"
```

For normal double-click launches, set the Windows user `TEMP` and `TMP` environment variables to a writable folder with sufficient free space, or use a launcher that sets those variables before starting the EXE. Do not hard-code the developer's F: path into the distributed executable.

## Optional native MIDI hardware input

The default build includes the `mido` abstraction and does not require `python-rtmidi`. To attempt to include the native MIDI backend:

```powershell
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py --with-midi
```

This compiles `python-rtmidi` from source and requires Visual Studio 2022 Build Tools with **Desktop development with C++** and the Windows SDK when a compatible wheel is unavailable. The current 1.5.8 PyPI Windows wheel is for CPython 3.12 x64; CPython 3.14 therefore uses a source build. Native MIDI is optional; Sonic Pi OSC integration and the bundled Mido abstraction do not require the native backend. Do not install `.[midi]` unless you need direct native MIDI device access.

## Target computer

The target computer needs Windows 11 x64 and a graphics driver supporting OpenGL 3.3 Core Profile. It does not need Python, pip, PyInstaller, FFmpeg or Visual Studio. Sonic Pi, GPU drivers, audio devices, source video, project files and user-added assets remain external.

Run the executable with `--self-check` to validate packaged Python imports and bundled resources. The check does **not** initialize OpenGL, enumerate MIDI devices, test loopback capture, exercise projector output, run four video decks or measure long-duration performance. Those checks must be performed on the actual performance machine.

## GitHub Actions workflows

Use **Cross-platform Versioned Builds** for the normal one-run Windows + Linux release build. It runs each build on a native operating-system runner and uploads versioned compressed ZIP archives.

The legacy **Windows Onefile Build** workflow remains a Windows-only manual fallback. The local Windows command above remains useful for quick individual test builds.

# Cross-platform versioned builds

AVTranslator can be packaged as a native one-file executable on Windows x64 and Linux x86_64. PyInstaller is not a cross-compiler: each executable must be built on its target operating system. The **Cross-platform Versioned Builds** workflow performs both native builds in parallel during one manual workflow run.

## One-click Windows + Linux build

1. Open the repository's **Actions** tab.
2. Select **Cross-platform Versioned Builds**.
3. Choose the release ZIP compression method and level.
4. Press **Run workflow**.

The workflow reads the version from **config.APP_VER** and checks it against **pyproject.toml**. It then builds on **windows-latest** and **ubuntu-22.04**, runs each packaged executable's **--self-check**, and creates two versioned archives:

- **eli_lab-avtranslator-<version>-windows-x64.zip**
- **eli_lab-avtranslator-<version>-linux-x86_64.zip**

Both archives are uploaded to the same workflow run as separate artifacts. The build reports are also uploaded separately. The workflow creates downloadable build artifacts; it does not publish a GitHub Release or tag automatically.

## ZIP compression options

The workflow uses Python's standard-library **zipfile** module. The compression applies to the downloadable release archive, not to video frames, source footage, or the internal PyInstaller executable payload.

| Option | ZIP method | Characteristics |
| --- | --- | --- |
| **stored** | ZIP_STORED | No compression; fastest archive creation and extraction, largest archive |
| **deflate** | ZIP_DEFLATED | Best compatibility and a balanced default |
| **bzip2** | ZIP_BZIP2 | Higher compression in many cases, slower and less universally supported |
| **lzma** | ZIP_LZMA | Often compact but slower to create/extract and less compatible with older archive tools |

The default is Deflate level 6. Deflate accepts levels 0–9; BZIP2 accepts 1–9. The level is ignored by Stored and LZMA. Since PyInstaller executables already contain compressed Python modules and native libraries, further ZIP compression may save relatively little space. Use Stored for speed or Deflate for a broadly compatible release archive.

Python references: [Data Compression and Archiving](https://docs.python.org/3/library/archiving.html), [zipfile](https://docs.python.org/3/library/zipfile.html), and [tarfile](https://docs.python.org/3/library/tarfile.html).

## Local Windows build

Use 64-bit CPython 3.12, 3.13 or 3.14:

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
~~~

The executable is **dist\eli_lab AVTranslator.exe**.

Create a versioned release ZIP manually:

~~~powershell
.\.venv\Scripts\python.exe .\scripts\package_release.py --binary ".\dist\eli_lab AVTranslator.exe" --platform windows-x64 --compression deflate --level 6
~~~

## Local Linux build

The Linux builder targets x86_64 and is tested in the CI workflow on Ubuntu 22.04. A local build needs CPython 3.12–3.14, build tools, and Qt/OpenGL/audio runtime libraries. On Debian/Ubuntu, install the runtime libraries used by the CI runner, then run:

~~~bash
sudo apt-get update
sudo apt-get install -y build-essential libasound2 libegl1 libgl1 libpulse0 libx11-xcb1 libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0
~~~

~~~bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python scripts/build_pyinstaller.py
~~~

The executable is **dist/eli_lab AVTranslator**.

Create a versioned ZIP:

~~~bash
.venv/bin/python scripts/package_release.py --binary "dist/eli_lab AVTranslator" --platform linux-x86_64 --compression deflate --level 6
~~~

Linux runtime dependencies such as glibc, the graphics driver, OpenGL/EGL, X11/XCB and audio-system libraries remain provided by the target operating system. The bundled executable does not include the Linux kernel, GPU driver or every desktop-system library. The Ubuntu 22.04 build is the compatibility baseline; validate the binary on the actual target distribution and GPU.

## HQ 1080p rendering target

The application remains designed around a 1920×1080 composition canvas. Decode output is capped at 1920×1080 and 30 FPS; the live render target is also 30 FPS. Sources smaller than 1080p are kept at their native dimensions by the decoder rather than being enlarged there. Sources larger than the cap are downscaled with bicubic interpolation. This is an HQ 1080p target, not a 4K pipeline.

A low-resolution source clip will still look soft when displayed large. The deck cards expose the decoded source dimensions; use footage close to 1920×1080 when the final output fills a 1080p projector/display. ZIP compression has no effect on the image quality or live frame rate.

## Build outputs and reports

Each native build writes:

- **dist/eli_lab AVTranslator.exe** on Windows or **dist/eli_lab AVTranslator** on Linux.
- **build/pyinstaller-build-report.txt** with application version, OS, Python and package versions, executable size and SHA-256.
- **dist/releases/eli_lab-avtranslator-<version>-<platform>.zip** with the binary, README, third-party notices, build report and release-manifest.json.

The manifest records the platform, version, binary hash, archive format and selected ZIP compression. The packager verifies the finished ZIP by reading its members before reporting success.

**--with-midi** remains optional. The default builds include Mido and Sonic Pi OSC integration without requiring the native python-rtmidi device backend.
