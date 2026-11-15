# Windows setup and operation

There are two common ways to use AVTranslator:

- **Performance computer:** copy and run the Windows x64 one-file executable. Python and development tools are not required.
- **Development/build computer:** run from source or build the executable using the repository-local Python environment.

For packaging, use [BUILD_PYINSTALLER_WINDOWS.md](BUILD_PYINSTALLER_WINDOWS.md). This document covers daily operation and troubleshooting.

## 1. Target system requirements

- Windows 11 64-bit.
- Graphics driver supporting OpenGL 3.3 Core Profile.
- SSD storage; NVMe is recommended for larger footage libraries.
- HDMI or supported USB-C DisplayPort output for a projector.
- Sonic Pi installed separately when using SONATA Expanded.
- H.264 MP4 footage is recommended for initial validation.

For multi-deck performance, 32 GB RAM is recommended, especially on systems with integrated graphics that share system memory. 16 GB can be sufficient for lighter sessions. Check the exact laptop model/SKU for supported HDMI resolution and refresh rate. Four simultaneous high-bitrate 4K streams are not guaranteed on an integrated GPU.

## 2. Install the one-file executable

1. Obtain the Windows x64 EXE from a trusted build output/artifact.
2. Copy the EXE to a local folder on the performance computer.
3. Double-click to start it.
4. On first launch, allow time for one-file extraction and Windows Defender scanning.
5. Writable application data, the media database, thumbnails and logs are created under:

   `%LOCALAPPDATA%\eli_lab\AVTranslator\`

The target computer does not need Python, pip, PyInstaller or FFmpeg. The executable bundles the Python application/runtime, Qt/PySide6, rendering/media/audio/OSC/MIDI dependencies and bundled visual resources/dictionaries.

Sonic Pi, graphics/audio drivers, user video files and user-added asset folders are not part of the EXE.

## 3. Desktop interface fonts

The desktop interface uses Newsreader / Georgia for English display headings, Yu Mincho / Noto Serif JP for Japanese display headings, DM Mono with Consolas / Cascadia Mono fallbacks for technical labels and controls, and Segoe UI / Yu Gothic UI for editable text and longer body copy. These are system-resolved font families; the application does not bundle font binaries or install extra font packages. If a preferred face is absent, its fallback is used.

In Japanese mode, the body/control font stack prefers **Yu Gothic UI**, **Meiryo UI / Meiryo**, **MS UI Gothic / MS PGothic / MS Gothic**, **BIZ UDGothic**, then Noto Sans JP and normal system fallbacks.

Some Windows installations do not include the Japanese supplemental fonts by default. If Japanese characters appear as empty squares or boxes:

1. Open **Settings → System → Optional features**.
2. Choose **View features** beside Add an optional feature.
3. Search for and install **Japanese Supplemental Fonts**.
4. Close and restart AVTranslator so Qt can refresh the available system font list.

You can open the Optional features page directly with `ms-settings:optionalfeatures`. Installing these fonts does not require changing the Windows display language. Microsoft lists Meiryo, Meiryo UI, MS Gothic, MS PGothic, MS UI Gothic and Yu Mincho among the Japanese supplemental families. [Microsoft's Windows font guidance](https://learn.microsoft.com/en-us/windows/deployment/windows-missing-fonts) explains the optional-font installation path.

## 4. Prepare footage and projects

A `.eliav` project and an `.eliset` performance set store composition state and source paths; they do not embed the original video files.

When moving a project:

1. Copy the video and user asset folders to the new computer.
2. Keep the folder structure the same where practical.
3. Import the folders into the Media Library on the new computer.
4. Reassign/relink the four decks and media overlays if absolute paths changed.
5. Save a fresh project/performance set on that computer.

A project JSON file alone is not a portable copy of the video media.

## 5. Connect the projector

1. Connect HDMI before opening the fullscreen output.
2. In Windows Display Settings, choose **Extend these displays**.
3. Start AVTranslator.
4. Begin with 1920×1080 at 60 Hz for the first validation. Test higher resolutions only after checking the actual laptop and projector specifications.
5. Select **View → PROJECTOR OUTPUT → Display N**.
6. Confirm the status bar reports the active projector renderer and FPS.
7. Press Escape in the projector output to close it. The main application remains open.

Preview and projector use separate OpenGL contexts but share application state and CPU frame snapshots. Each output owns and uploads its own GPU textures.

## 6. Run an autonomous Sonic Pi performance

1. Prepare a composition with video decks and/or generator layers.
2. In **AUD / CTRL**, choose System Loopback for analysis of actual audio-band/onset activity, or Sonic Pi macros only when local capture is unavailable or unnecessary.
3. In **AUTO PERF**, choose Generative or Structured style, musical sync and duration.
4. Press **PERF MODE**.
5. Run SONATA Expanded in Sonic Pi.
6. Confirm the application moves from ARMED to LIVE and OSC/audio status is healthy.
7. Open the projector output.
8. Stop SONATA to end the current AUTO pass. Performance Mode re-arms for a subsequent patch run. Press **STOP PERF MODE** when the show is finished.

Sonic Pi energy/cutoff macros are normalized musical control signals, not raw audio samples. System loopback is required for actual low/mid/high band and onset analysis.

See [SONATA integration notes](SONIC_PI_SONATA_INTEGRATION.md) for remote-computer OSC addressing and the protocol.

## 7. Developer setup (source run)

Use 64-bit CPython 3.12, 3.13 or 3.14 on the Windows development computer:

```powershell
git clone https://github.com/ilyaminineli/eli_lab-av-translator.git
cd eli_lab-av-translator
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
.\.venv\Scripts\python.exe main.py
```

Use `py -3.12` or `py -3.13` if preferred. PowerShell activation is optional; calling the project interpreter directly avoids activating the wrong environment.

## 8. Developer quality checks

The repository includes a pytest regression suite. The Windows Quality workflow runs compilation, Ruff, pytest and a Japanese UI typography proof. Run the same core checks locally:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q .
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest -q
```

Install the complete development/test environment with `requirements-dev.txt`. The equivalent editable-install extra is `pip install -e ".[dev]"`.

A green quality workflow is not a runtime, GUI, OpenGL, musical or hardware acceptance result.

## 9. Diagnostics

The one-file build supports:

```powershell
& ".\dist\eli_lab AVTranslator.exe" --self-check
```

It reports whether required Python packages import, which FFmpeg libraries are present, whether H.264 decoding is available and whether bundled icons/textures/sketches/dictionaries are present. It does not initialize an OpenGL context or test HDMI/projector output.

The application log is:

`%LOCALAPPDATA%\eli_lab\AVTranslator\logs\av-translator.log`

## 10. Troubleshooting

### OpenGL initialization fails

- Update the graphics driver using the computer manufacturer's support channel.
- Confirm OpenGL 3.3 Core Profile support.
- Check the status bar for the active renderer's actual error.
- LOCAL PREVIEW IDLE means the local preview dock is hidden; it does not mean that the projector renderer failed.
- The projector renderer reports its own initialization result and FPS.

### Playback is slow or drops frames

- Connect AC power and use Windows Best performance mode.
- Begin with one or two 1080p H.264 clips, then add decks.
- Use a local SSD rather than a slow external drive.
- Close browsers, games and other GPU-heavy software.
- Reduce source resolution/bitrate before simplifying the visual composition.
- Compare renderer FPS, decode time, conversion time, upload cost and dropped-frame counters.

### Audio loopback is unavailable

- Check Windows playback and recording devices.
- Refresh the device list in AUD / CTRL.
- Sonic Pi transport and energy/cutoff macros can still operate without local audio capture.
- Actual low/mid/high bands and onset analysis require a supported loopback source.

### Projector appears on the wrong display

- Confirm Windows is set to Extend.
- Close the output window and reopen **View → PROJECTOR OUTPUT** after changing display topology.
- Verify the target HDMI mode and refresh rate are supported by the exact laptop and projector models.

### Media is missing after moving the project

Projects store source paths, not copies of video files. Copy the original folders and import/reassign them on the target computer.

### One-file EXE fails while extracting an FFmpeg DLL

Errors such as `Failed to extract swscale-*.dll` with `decompression resulted in return code -1` are often caused by a write failure in the one-file temporary extraction directory. Check free space on the drive used by `$env:TEMP`, not only the drive containing the EXE. Close other AVTranslator instances and remove only stale `_MEI*` extraction folders that are not in use. For a test launch from a roomy F: volume:

```powershell
New-Item -ItemType Directory -Force F:\AVTranslatorTemp | Out-Null
$env:TEMP = "F:\AVTranslatorTemp"
$env:TMP = $env:TEMP
& ".\dist\eli_lab AVTranslator.exe"
```

If it still fails with ample free space, compare the executable SHA-256 with its build report and rebuild; a different zlib error code may indicate archive corruption rather than a write-space problem.

### Windows Defender/SmartScreen warns about the EXE

One-file applications extract their payload to a temporary directory and may trigger an unfamiliar-app scan. Obtain the EXE from the trusted build source and compare its SHA-256 build report. Do not disable Defender globally to run an unverified executable.
