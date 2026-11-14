---
title: Field manual
section: 02 / OPERATIONS
---
# Field manual

This manual follows the order of a first session: prepare the computer, gather footage, build a composition, connect control and perform the image.

## 01 — Install and launch

The packaged application targets Windows 11 x64 and a graphics driver that supports OpenGL 3.3 Core Profile. Obtain the executable from the [GitHub Releases page](https://github.com/ilyaminineli/eli_lab-av-translator/releases).

For a development installation, follow the [Windows setup guide](SETUP_WINDOWS.md). The one-file executable does not require Python on the performance computer. Sonic Pi, source footage and user-added asset folders remain separate.

Read the [system requirements and acceptance notes](SETUP_WINDOWS.md#1-target-system-requirements) before preparing a production computer.

## 02 — Prepare your footage

1. Collect source videos in local folders. Begin with H.264 MP4 at 720p or 1080p while checking performance.
2. Open the **PREPARE** workspace and add the footage folder to the Media Library.
3. Wait for indexing and thumbnail creation to complete.
4. Load clips into the four independent video decks.
5. Keep the source folders available. Project files store paths and composition state; they do not embed video files.

See [M1 — Video collage](M1_VIDEO_COLLAGE.md) for deck and collage behaviour.

## 03 — Build a composition

Open **COMPOSE** and add the visual elements needed for the scene:

- Geometry, waveform and particle generators.
- Text Art, including animated typography and vertical-writing options.
- Image and video overlays.
- Layer transforms, opacity, blend modes and ordering.
- Master filters and per-layer effect stacks.

Use the [Generative visuals guide](M2_GENERATIVE_VISUALS.md) for the generator workflow and [Typography reference](M6_E_TYPOGRAPHY.md) for text layout and animation.

## 04 — Shape how the image moves

The six normalized Performance Macros provide a shared control language for live changes. The Modulator Bank adds reusable LFOs, envelopes, step sequences, rhythm patterns and followers.

Audio analysis can use a physical input or system loopback. MIDI can map hardware controls. Per-layer modifiers can route performance sources to visual parameters.

See [M5 — Performance environment](M5_PERFORMANCE_ENVIRONMENT.md), [M6 — Advanced performance controls](M6_ADVANCED_PERFORMANCE_CONTROLS.md) and [M5 — Modulator Bank](M5_MODULATOR_BANK.md).

## 05 — Connect Sonic Pi

The application receives versioned OSC messages at the `/eli_lab/v1` protocol. Sonic Pi remains responsible for music playback; AV Translator uses its transport, cues and macro messages to shape visuals.

For a same-computer setup, begin with `127.0.0.1` and the configured receiver port. For a two-computer arrangement, use the AV Translator computer's reachable LAN address.

Follow the [Sonic Pi / SONATA integration guide](SONIC_PI_SONATA_INTEGRATION.md) before a performance.

## 06 — Structure a set

Use VJ scenes to capture and recall a visual state. The live timeline can schedule markers and actions by bar and beat. Performance Mode arms the external controls and AUTO PERF system; it does not start Sonic Pi itself.

See [M6 — Scene composition bank](M6_B_SCENE_COMPOSITION_BANK.md), [M6 — Live performance timeline](M6_LIVE_PERFORMANCE_TIMELINE.md) and [M5 — Autonomous performance](M5_AUTONOMOUS_PERFORMANCE.md).

## 07 — Project the image

Connect the projector before opening the output. Set Windows to **Extend these displays**, then choose the target from **View → PROJECTOR OUTPUT**.

The local preview and projector have separate OpenGL contexts but use the same composition state. Validate the exact display resolution, refresh rate and graphics hardware before a production-critical show.

## 08 — Save and move a project

- `.eliav` stores composition and project state.
- `.eliset` stores a performance set.
- Source media remains external.

When moving to another computer, copy the media folders, import them into the Media Library and reassign or relink any paths that changed. The [project format reference](PROJECT_FORMAT.md) describes the saved data.

## Troubleshooting

- [Windows setup and troubleshooting](SETUP_WINDOWS.md#9-troubleshooting)
- [Architecture and renderer lifecycle](ARCHITECTURE.md)
- [Sonic Pi / OSC diagnostics](SONIC_PI_SONATA_INTEGRATION.md)
- [Known limitations and development status](ROADMAP.md)

The application is under active development. Automated code checks do not replace target-machine testing of OpenGL, multi-deck playback, long-duration operation and projector output.
