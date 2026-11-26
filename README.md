# eli_lab AVTranslator

**Windows-first audiovisual performance environment for live video collage, procedural visuals, typography, audio reactivity and Sonic Pi-controlled shows.**

**Static website:** [English homepage](index.html) · [Japanese homepage](site/ja/index.html) · [Features](site/features.html) · [Field manual](site/manual.html) · [Wiki](site/wiki.html) · [Windows setup](site/guides/windows-setup.html) · [Sonic Pi guide](site/guides/sonic-pi.html). The site is plain HTML/CSS under `site/`, with the real homepage in the repository root and a `.nojekyll` marker. It is ready for GitHub Pages **Deploy from a branch → main → /(root)**. Once Pages is enabled, the project URL is `https://ilyaminineli.github.io/eli_lab-av-translator/`. The Markdown source documents are kept under [docs/](docs/) and the website structure is described in [docs/WEBSITE_PLAN.md](docs/WEBSITE_PLAN.md).

## Project status — 27 November 2026

The `main` branch contains the M0–M6 rendering, video, generator, performance-control and live-workspace foundations, plus the first M7 implementation increments. [PR #34](https://github.com/ilyaminineli/eli_lab-av-translator/pull/34) merged the unified visual director and the initial PERF / COMPOSE / PREPARE workspace shell. [PR #35](https://github.com/ilyaminineli/eli_lab-av-translator/pull/35) hardened timeline/macro runtime handling, bounded generator raster work, and introduced the monochrome workspace theme and 16:9 local preview frame.

The freeform multi-source collage layouts, responsive four-deck cards, compact actions, headline-led Text Art and About/version update were merged to `main` in [PR #36](https://github.com/ilyaminineli/eli_lab-av-translator/pull/36). The operator-workspace follow-up added the final 絵 seal, responsive dock sizing, wheel-safe controls and complete English/Japanese navigation in [PR #40](https://github.com/ilyaminineli/eli_lab-av-translator/pull/40), then applied the website-aligned desktop typography hierarchy in [PR #42](https://github.com/ilyaminineli/eli_lab-av-translator/pull/42).

The active M7 roadmap has been restructured through M7-H. Work on M7-C0 — Visual Ontology, Object Identity and Mutation Contracts — is being developed on the `m7/m7-c0-visual-ontology` branch. The governing creative and architectural reference is [Volume 11 — IDM Visual Instrument](docs/guides/IDM_Visual_Instrument_Visual_Composition_Generative_Art_and_Live_Concert_Architecture.md); the implementation sequence and audit are in [docs/M7.md](docs/M7.md).

The Quality workflow performs Python compilation, Ruff, pytest regression tests and a Japanese UI typography proof. Those checks do not replace target-Windows GUI, OpenGL/GPU, four-deck, Sonic Pi, projector and sustained-performance acceptance. Hardware validation remains an explicit release gate; do not treat static CI as a hardware sign-off.

## Current capabilities

- **M0 — Rendering core:** PySide6 desktop UI, OpenGL 3.3 Core / ModernGL compositor, composition/layer model, project persistence and independent fullscreen projector output.
- **M1 — Video collage:** four independent PyAV video decks, local media library, segment playback, looping, transforms, blend modes, collage layouts and renderer/decode diagnostics. Preview and projector render from shared CPU frame snapshots while owning separate GPU resources.
- **M2 — Generative visuals:** geometry, Text Art, waveform and GPU particle generators; still/animated-image/video overlays; per-layer and master effects; animated typography and generator motion.
- **M3 — Audio-reactive control:** internal transport, physical-input/system-loopback analysis, RMS/peak/low/mid/high/onset features, scenes and a normalized modulation matrix.
- **M4 — Sonic Pi integration:** versioned `/eli_lab/v1` OSC receiver, session/sequence validation, bounded event delivery, diagnostics and SONATA control integration. Sonic Pi remains the music/audio playback authority.
- **M5 — Performance environment:** one-button Performance Mode, phrase-aware AUTO PERF, Modulator Bank, per-layer performance modifiers, MIDI mapping/scene tools and shared performance diagnostics.
- **M5 — Asynchronous generator rendering:** one application-owned background raster worker, latest-revision-wins snapshots, per-layer pending-job coalescing, static CPU raster / animated GPU-shader separation, preview/projector-local uploads and lifecycle invalidation.
- **M5 — Text raster controls:** live preview, Apply Immediately, commit-on-pause, 25/50/75/100% preview quality, optional 1600×900 final raster, 1–20 Hz text-job rate limit, freeze, last-valid-texture fallback and pipeline status.
- **M6 — Live performance controls:** six normalized 0–1 Performance Macros (CHAOS, DENSITY (DNST), DEPTH (DPTH), DECAY (DEC), PRESSURE and FRAGMENT (FRAG)), Modulator Bank source assignments, MIDI/OSC/keyboard input, VJ scenes and a bar/beat live performance timeline.
- **M7-A — Unified visual director:** composition-aware variation across video, generators and overlays; dynamic all-layer variation budgets, spatial relationships, optional anchors, activity feedback, per-layer cooldowns and manual-override precedence.
- **M7-B — Operator workspace foundation:** central PERF / COMPOSE / PREPARE workspaces, a shared macro strip, responsive operator docks, wheel-safe controls, the final 絵 seal and a website-aligned monochrome type system.

See [docs/PRODUCT_OVERVIEW.md](docs/PRODUCT_OVERVIEW.md) for a non-technical explanation and target audiences, [docs/WEBSITE_PLAN.md](docs/WEBSITE_PLAN.md) for the website content architecture, and [docs/ROADMAP.md](docs/ROADMAP.md) for milestone state and remaining acceptance gates. Implementation detail is in the [M5 Autonomous Performance guide](docs/M5_AUTONOMOUS_PERFORMANCE.md), [M5 Performance Environment](docs/M5_PERFORMANCE_ENVIRONMENT.md), [Architecture](docs/ARCHITECTURE.md) and [M5 Completion Handoff](docs/M5_COMPLETION_HANDOFF.md).

## Build for Windows and Linux

The supported local one-file build uses **PyInstaller** through the same cross-platform script.

Windows x64 (64-bit CPython 3.12–3.14):

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
~~~

Linux x86_64 (64-bit CPython 3.12–3.14):

~~~bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python scripts/build_pyinstaller.py
~~~

The script uses the repository-local .venv and installs the pinned runtime/build requirements. Native MIDI input remains optional; Sonic Pi OSC integration does not require python-rtmidi.

A single GitHub Actions run can build both platforms in parallel: open **Actions → Cross-platform Versioned Builds**, choose a ZIP compression method, and run the workflow. It uploads versioned Windows x64 and Linux x86_64 archives plus their build reports. The version is read from config.py and checked against pyproject.toml.

The release packager supports Stored, Deflate, BZIP2 and LZMA ZIP compression. Deflate level 6 is the default. Example Windows packaging command:

~~~powershell
.\.venv\Scripts\python.exe .\scripts\package_release.py --binary ".\dist\eli_lab AVTranslator.exe" --platform windows-x64 --compression deflate --level 6
~~~

Example Linux packaging command:

~~~bash
.venv/bin/python scripts/package_release.py --binary "dist/eli_lab AVTranslator" --platform linux-x86_64 --compression deflate --level 6
~~~

Full guide: [Cross-platform versioned builds](docs/BUILD_CROSS_PLATFORM.md). The [Windows PyInstaller guide](docs/BUILD_PYINSTALLER_WINDOWS.md) retains Windows-specific troubleshooting, and the [Windows setup guide](docs/SETUP_WINDOWS.md) covers the installed application. For repeatable UI/control stress tests and target-machine soak testing, see [Windows stability testing](docs/WINDOWS_STABILITY_TESTING.md).

Windows output: **dist\eli_lab AVTranslator.exe**. Linux output: **dist/eli_lab AVTranslator**. Linux builds target Ubuntu 22.04-compatible x86_64 environments; system OpenGL/X11/audio libraries and a suitable graphics driver remain required on the Linux target.

## Performance workflow

1. Import footage into the Media Library and load clips into the four decks.
2. Add generator and overlay layers as needed; compose the layer order, transforms and effects.
3. In **AUDIO / CTRL**, choose system loopback for analysis of actual computer audio, or use Sonic Pi macros without local audio capture.
4. In **AUTO PERF**, choose style, musical sync and session duration.
5. Press **PERF MODE**, then run SONATA in Sonic Pi. The app waits in ARMED until it receives the first valid transport/clock event.
6. Open **View → PROJECTOR OUTPUT** and select the external display.
7. Stop SONATA to end the current automation pass. Press **STOP PERF MODE** to release resources started by the mode and restore generated defaults.

For same-computer Sonic Pi use, the default receiver destination is `127.0.0.1:57121`. Sonic Pi's own incoming OSC port is not the destination for these outbound messages. See [SONATA integration notes](docs/SONIC_PI_SONATA_INTEGRATION.md). The Performance Macro panel is in AUDIO / CTRL; the six macros can be fed by audio, transport, Sonic Pi `energy/cutoff` or Modulator Bank outputs, then routed to multiple targets.

## Generator and text rendering

Static generator content is rasterized by the shared background service. Text content and typography changes create versioned CPU raster snapshots; text motion such as type-on, reveal, wave, jitter, crawl and glitch is applied by the compositor shader. A newer edit supersedes an older pending snapshot, and preview/projector renderers upload the accepted pixels independently while their own GL context is current.

Text's **TEXT RASTER** controls let the operator trade preview detail for edit responsiveness. The last valid texture can remain visible while a new raster is prepared or after a raster failure. These controls do not pause video decoding, GPU motion, effects or audio-reactive updates.

See [M2 Generative Visuals](docs/M2_GENERATIVE_VISUALS.md) and [M5 Autonomous Performance](docs/M5_AUTONOMOUS_PERFORMANCE.md).

## System requirements and practical limits

- Windows 11 x64 or a compatible Linux x86_64 distribution (Ubuntu 22.04 is the packaged Linux baseline).
- OpenGL 3.3 Core Profile and a current graphics driver.
- 16 GB RAM for lighter sessions; 32 GB recommended for multi-deck work, especially with integrated graphics.
- SSD/NVMe storage for the application database, thumbnails and footage.
- The live video pipeline targets HQ 1080p: 1920×1080 decode ceiling at 30 FPS and a 30 FPS renderer. Use footage close to 1080p for the sharpest full-screen projection; smaller source clips are preserved at native resolution rather than artificially upscaled by the decoder. 4K output is not a project target.
- HDMI or supported USB-C DisplayPort output for projector use.
- Sonic Pi installed separately for SONATA integration.

Performance depends on the exact CPU/GPU, codec, media bitrate, display mode and effects. Use the live diagnostics rather than assuming that four arbitrary sources will sustain the same frame rate.

## Data and project files

Writable application data, the SQLite media index, thumbnails and logs live under:

`%LOCALAPPDATA%\eli_lab\AVTranslator\`

`.eliav` project files and `.eliset` performance sets store settings and media paths, not the original video files. When moving to another computer, copy the source media folders and relink/re-import them if absolute paths changed.

## Validation boundary and known omissions

- The Quality workflow runs Python compilation, Ruff, pytest regression tests and a Japanese UI typography proof. It does not run an interactive live GUI, create a performance OpenGL session, execute SONATA or sign off target hardware.
- The full 384-bar SONATA rehearsal and session restart/stale-packet recovery remain manual validation.
- Physical-input/system-loopback discovery, device loss/reconnect and sustained capture remain hardware validation.
- Four-deck continuous typing with multiple generators, effects, audio reactivity and projector output has not yet been measured as a formal stress-acceptance run.
- Projector hot-plug, target refresh-rate/frame pacing and long-duration stability remain to be signed off.
- Master-output recording and audio/video muxing are not implemented; they are a separate deferred delivery item, not a completed M5 feature.
- Projects store absolute media paths; source media must be moved and relinked separately.
- Per-layer FX is a bounded effect stack, not an unlimited node graph.

## M6 — Advanced VJ Environment

M6 is in active development across the live-deck, scene-bank, visual-transformation, particle, typography and performance-control workstreams. The current Performance Macro follow-up is documented in [docs/M6_ADVANCED_PERFORMANCE_CONTROLS.md](docs/M6_ADVANCED_PERFORMANCE_CONTROLS.md); the wider VJ scope and acceptance criteria are tracked in [docs/M6_ADVANCED_VJ_ENVIRONMENT.md](docs/M6_ADVANCED_VJ_ENVIRONMENT.md).
