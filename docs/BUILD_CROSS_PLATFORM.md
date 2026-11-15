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
|---|---|---|
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
