# eli_lab AV Translator

**Windows-first audiovisual performance environment for live video collage, procedural visuals, typography, audio reactivity and Sonic Pi-controlled shows.**

## Project status — 12 November 2026

M0–M5 implementation is on `main`. M5's asynchronous generator rasterization and text-performance controls were merged in [PR #19](https://github.com/ilyaminineli/eli_lab-av-translator/pull/19). The latest `main` snapshot is `358dc597`; **Quality workflow #116 passed** Python compilation and Ruff on that commit ([run #116](https://github.com/ilyaminineli/eli_lab-av-translator/actions/runs/43132442896)).

A green quality workflow is a static-code check, not a hardware sign-off. Full SONATA rehearsal, audio-device reconnect, four-deck stress and projector acceptance still need to be performed on the target Windows computer. The former pytest/unit-test suite is not present in this repository.

The next development milestone is **M6 — Advanced VJ Environment**. Its first defined workstream is a more operator-focused live mixer. M6 is planned; those features are not yet implemented.

## Current capabilities

- **M0 — Rendering core:** PySide6 desktop UI, OpenGL 3.3 Core / ModernGL compositor, composition/layer model, project persistence and independent fullscreen projector output.
- **M1 — Video collage:** four independent PyAV video decks, local media library, segment playback, looping, transforms, blend modes, collage layouts and renderer/decode diagnostics. Preview and projector render from shared CPU frame snapshots while owning separate GPU resources.
- **M2 — Generative visuals:** geometry, Text Art, waveform and GPU particle generators; still/animated-image/video overlays; per-layer and master effects; animated typography and generator motion.
- **M3 — Audio-reactive control:** internal transport, physical-input/system-loopback analysis, RMS/peak/low/mid/high/onset features, scenes and a normalized modulation matrix.
- **M4 — Sonic Pi integration:** versioned `/eli_lab/v1` OSC receiver, session/sequence validation, bounded event delivery, diagnostics and SONATA control integration. Sonic Pi remains the music/audio playback authority.
- **M5 — Performance environment:** one-button Performance Mode, phrase-aware AUTO PERFORMANCE, Modulator Bank, per-layer performance modifiers, MIDI mapping/scene tools and shared performance diagnostics.
- **M5 — Asynchronous generator rendering:** one application-owned background raster worker, latest-revision-wins snapshots, per-layer pending-job coalescing, static CPU raster / animated GPU-shader separation, preview/projector-local uploads and lifecycle invalidation.
- **M5 — Text raster controls:** live preview, Apply Immediately, commit-on-pause, 25/50/75/100% preview quality, optional 1600×900 final raster, 1–20 Hz text-job rate limit, freeze, last-valid-texture fallback and pipeline status.

See [docs/ROADMAP.md](docs/ROADMAP.md) for milestone state and remaining acceptance gates. Implementation detail is in the [M5 Autonomous Performance guide](docs/M5_AUTONOMOUS_PERFORMANCE.md), [M5 Performance Environment](docs/M5_PERFORMANCE_ENVIRONMENT.md), [Architecture](docs/ARCHITECTURE.md) and [M5 Completion Handoff](docs/M5_COMPLETION_HANDOFF.md).

## Build and run on Windows

The supported local one-file build is **PyInstaller** through the repository script:

```powershell
# Create the project-local environment once; choose an installed 64-bit CPython.
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# Build, self-check the executable and write a SHA-256 build report.
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
```

Use `py -3.12` or `py -3.13` instead when that is the selected interpreter. The script requires the repository-local `.venv`; it switches back to that environment if another Python environment is active. Native MIDI input is optional; `--with-midi` attempts to compile the native `python-rtmidi` backend and requires Visual Studio C++ Build Tools.

Output:

`dist\eli_lab AV Translator.exe`

The target computer needs Windows 11 x64 and a current graphics driver supporting OpenGL 3.3 Core. It does not need Python, pip, PyInstaller or FFmpeg. Sonic Pi, video media, projects, audio devices and user-added asset folders remain external.

Full steps and limitations: [Windows PyInstaller build guide](docs/BUILD_PYINSTALLER_WINDOWS.md) and [Windows setup guide](docs/SETUP_WINDOWS.md).

The GitHub **Windows Onefile Build** workflow is manual-dispatch only. It does not run on ordinary pull-request or push updates. The local `scripts/build_pyinstaller.py` command above is the normal build path.

## Performance workflow

1. Import footage into the Media Library and load clips into the four decks.
2. Add generator and overlay layers as needed; compose the layer order, transforms and effects.
3. In **AUDIO / CONTROL**, choose system loopback for analysis of actual computer audio, or use Sonic Pi macros without local audio capture.
4. In **AUTO PERFORMANCE**, choose style, musical sync and session duration.
5. Press **PERFORMANCE MODE**, then run SONATA in Sonic Pi. The app waits in ARMED until it receives the first valid transport/clock event.
6. Open **View → PROJECTOR OUTPUT** and select the external display.
7. Stop SONATA to end the current automation pass. Press **STOP PERFORMANCE MODE** to release resources started by the mode and restore generated defaults.

For same-computer Sonic Pi use, the default receiver destination is `127.0.0.1:57121`. Sonic Pi's own incoming OSC port is not the destination for these outbound messages. See [SONATA integration notes](docs/SONIC_PI_SONATA_INTEGRATION.md).

## Generator and text rendering

Static generator content is rasterized by the shared background service. Text content and typography changes create versioned CPU raster snapshots; text motion such as type-on, reveal, wave, jitter, crawl and glitch is applied by the compositor shader. A newer edit supersedes an older pending snapshot, and preview/projector renderers upload the accepted pixels independently while their own GL context is current.

Text's **TEXT RASTER PERFORMANCE** controls let the operator trade preview detail for edit responsiveness. The last valid texture can remain visible while a new raster is prepared or after a raster failure. These controls do not pause video decoding, GPU motion, effects or audio-reactive updates.

See [M2 Generative Visuals](docs/M2_GENERATIVE_VISUALS.md) and [M5 Autonomous Performance](docs/M5_AUTONOMOUS_PERFORMANCE.md).

## System requirements and practical limits

- Windows 11 x64 for the packaged performance build.
- OpenGL 3.3 Core Profile and a current graphics driver.
- 16 GB RAM for lighter sessions; 32 GB recommended for multi-deck work, especially with integrated graphics.
- SSD/NVMe storage for the application database, thumbnails and footage.
- Start validation with H.264 720p/1080p clips. Four simultaneous high-bitrate 4K streams are not guaranteed on integrated graphics.
- HDMI or supported USB-C DisplayPort output for projector use.
- Sonic Pi installed separately for SONATA integration.

Performance depends on the exact CPU/GPU, codec, media bitrate, display mode and effects. Use the live diagnostics rather than assuming that four arbitrary sources will sustain the same frame rate.

## Data and project files

Writable application data, the SQLite media index, thumbnails and logs live under:

`%LOCALAPPDATA%\eli_lab\AV Translator\`

`.eliav` project files and `.eliset` performance sets store settings and media paths, not the original video files. When moving to another computer, copy the source media folders and relink/re-import them if absolute paths changed.

## Validation boundary and known omissions

- The Quality workflow runs Python compilation and Ruff. It does not run a GUI, create an OpenGL context, execute SONATA or test target hardware.
- The full 384-bar SONATA rehearsal and session restart/stale-packet recovery remain manual validation.
- Physical-input/system-loopback discovery, device loss/reconnect and sustained capture remain hardware validation.
- Four-deck continuous typing with multiple generators, effects, audio reactivity and projector output has not yet been measured as a formal stress-acceptance run.
- Projector hot-plug, target refresh-rate/frame pacing and long-duration stability remain to be signed off.
- Master-output recording and audio/video muxing are not implemented; they are a separate deferred delivery item, not a completed M5 feature.
- Projects store absolute media paths; source media must be moved and relinked separately.
- Per-layer FX is a bounded effect stack, not an unlimited node graph.

## M6 — Advanced VJ Environment

M6 is the next planned development phase. The first workstream is **A. A proper live mixer**: evolve the current four-deck foundation into an operator-first VJ surface. The M6 brief emphasizes triggering multiple clips together from media bins, with a clear live-performance interaction model. The detailed initial scope and acceptance criteria are tracked in [docs/M6_ADVANCED_VJ_ENVIRONMENT.md](docs/M6_ADVANCED_VJ_ENVIRONMENT.md).
