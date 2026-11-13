# Windows setup and operation

There are two common ways to use AV Translator:

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

   `%LOCALAPPDATA%\eli_lab\AV Translator\`

The target computer does not need Python, pip, PyInstaller or FFmpeg. The executable bundles the Python application/runtime, Qt/PySide6, rendering/media/audio/OSC/MIDI dependencies and bundled visual resources/dictionaries.

Sonic Pi, graphics/audio drivers, user video files and user-added asset folders are not part of the EXE.

## 3. Prepare footage and projects

A `.eliav` project and an `.eliset` performance set store composition state and source paths; they do not embed the original video files.

When moving a project:

1. Copy the video and user asset folders to the new computer.
2. Keep the folder structure the same where practical.
3. Import the folders into the Media Library on the new computer.
4. Reassign/relink the four decks and media overlays if absolute paths changed.
5. Save a fresh project/performance set on that computer.

A project JSON file alone is not a portable copy of the video media.

## 4. Connect the projector

1. Connect HDMI before opening the fullscreen output.
2. In Windows Display Settings, choose **Extend these displays**.
3. Start AV Translator.
4. Begin with 1920×1080 at 60 Hz for the first validation. Test higher resolutions only after checking the actual laptop and projector specifications.
5. Select **View → PROJECTOR OUTPUT → Display N**.
6. Confirm the status bar reports the active projector renderer and FPS.
7. Press Escape in the projector output to close it. The main application remains open.

Preview and projector use separate OpenGL contexts but share application state and CPU frame snapshots. Each output owns and uploads its own GPU textures.

## 5. Run an autonomous Sonic Pi performance

1. Prepare a composition with video decks and/or generator layers.
2. In **AUDIO / CONTROL**, choose System Loopback for analysis of actual audio-band/onset activity, or Sonic Pi macros only when local capture is unavailable or unnecessary.
3. In **AUTO PERFORMANCE**, choose Generative or Structured style, musical sync and duration.
4. Press **PERFORMANCE MODE**.
5. Run SONATA Expanded in Sonic Pi.
6. Confirm the application moves from ARMED to LIVE and OSC/audio status is healthy.
7. Open the projector output.
8. Stop SONATA to end the current AUTO pass. Performance Mode re-arms for a subsequent patch run. Press **STOP PERFORMANCE MODE** when the show is finished.

Sonic Pi energy/cutoff macros are normalized musical control signals, not raw audio samples. System loopback is required for actual low/mid/high band and onset analysis.

See [SONATA integration notes](SONIC_PI_SONATA_INTEGRATION.md) for remote-computer OSC addressing and the protocol.

## 6. Developer setup (source run)

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

## 7. Developer quality checks

The former pytest/unit-test suite and its dependencies are not present in the current repository. The Quality workflow performs Python compilation and Ruff:

```powershell
.\.venv\Scripts\python.exe -m compileall -q .
.\.venv\Scripts\python.exe -m ruff check .
```

A green quality workflow is not a runtime, GUI, OpenGL, musical or hardware acceptance result.

## 8. Diagnostics

The one-file build supports:

```powershell
& ".\dist\eli_lab AV Translator.exe" --self-check
```

It reports whether required Python packages import, which FFmpeg libraries are present, whether H.264 decoding is available and whether bundled icons/textures/sketches/dictionaries are present. It does not initialize an OpenGL context or test HDMI/projector output.

The application log is:

`%LOCALAPPDATA%\eli_lab\AV Translator\logs\av-translator.log`

## 9. Troubleshooting

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
- Refresh the device list in AUDIO / CONTROL.
- Sonic Pi transport and energy/cutoff macros can still operate without local audio capture.
- Actual low/mid/high bands and onset analysis require a supported loopback source.

### Projector appears on the wrong display

- Confirm Windows is set to Extend.
- Close the output window and reopen **View → PROJECTOR OUTPUT** after changing display topology.
- Verify the target HDMI mode and refresh rate are supported by the exact laptop and projector models.

### Media is missing after moving the project

Projects store source paths, not copies of video files. Copy the original folders and import/reassign them on the target computer.

### Windows Defender/SmartScreen warns about the EXE

One-file applications extract their payload to a temporary directory and may trigger an unfamiliar-app scan. Obtain the EXE from the trusted build source and compare its SHA-256 build report. Do not disable Defender globally to run an unverified executable.
