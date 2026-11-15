# eli_lab AVTranslator

**A live audiovisual instrument for building video collages, generative graphics and typographic scenes that move with music.**

eli_lab AVTranslator is a Windows desktop environment for making visuals behave like part of a live performance. It brings video footage, text, procedural graphics, image overlays and visual effects into one composition. That composition can react to audio, follow musical time, receive control messages from Sonic Pi or MIDI, and be sent to a local preview or an external projector.

It is closer to a visual performance instrument than to a conventional video editor. The goal is not to assemble a finished film on a timeline. The goal is to create a visual system that can be played, changed and shaped while music is happening.

## What can it do?

### Build a live collage from footage

Load up to four independent video decks and arrange them as a live collage. Each deck has its own playback position, segment, loop, hold and lock controls. The media library indexes local footage and keeps source files outside the project.

### Mix footage with generated material

A composition can contain video, image overlays, animated images, geometry, waveforms, text and GPU particle layers. Layers can be moved, scaled, blended and reordered. Master effects and per-layer effect stacks let the same composition move between clean, degraded, printed, displaced or feedback-heavy looks.

### Make typography part of the image

Text Art supports multiline text, styled text runs, different writing directions, path layouts and animated treatments. A bilingual text pool can draw from English and Japanese material. Text is rasterized in the background while motion is handled by the compositor, so editing text does not have to rebuild the entire visual scene.

### Let visuals respond to sound and time

The application can analyse an audio input or system loopback and expose features such as level, peaks, frequency bands, onsets and tempo estimates. Its six normalized Performance Macros can control multiple visual parameters at once. Reusable LFOs, envelopes, step sequences and followers provide more deliberate modulation.

### Perform with Sonic Pi, MIDI and scenes

The OSC receiver accepts the versioned `/eli_lab/v1` control protocol. Sonic Pi can send transport, cue and macro information while remaining responsible for music playback. MIDI input and keyboard mappings can also control the performance. VJ scenes, transitions and a bar/beat timeline help structure a set without turning it into a fixed video edit.

### Send the composition to a screen or projector

The local preview and fullscreen projector output use the same composition state while maintaining separate graphics resources. This makes the application useful for performances where the operator needs a working view and an audience-facing display.

## Three ways to work

**PREPARE — gather the material.** Import footage, organise the media library and browse visual assets.

**COMPOSE — build the visual system.** Add layers, text, generators, overlays, blends and effects. Adjust how the elements relate to one another.

**PERF — operate the composition live.** Run the decks, use the macros, connect audio or Sonic Pi, change scenes and send the output to a projector.

The workspaces are different views of one composition, not separate projects.

## Who is it for?

### VJs and live visual performers

This is the clearest match. The four-deck collage, live layer controls, visual effects, scene recall, performance macros and projector output are all designed around visuals that change during a set.

### Electronic musicians and Sonic Pi performers

Performers who already build music or generative scores in Sonic Pi can use its OSC messages to steer visual energy, transitions, scenes and parameters. The application complements a music setup; it does not replace a DAW or Sonic Pi as the audio playback engine.

### Audiovisual and media artists

Artists working with sound, moving image, projection and live systems can combine prepared footage with procedural layers and real-time control. It is especially relevant when the visual result is meant to remain open to variation rather than play identically every time.

### Generative artists and creative coders

The generator, modulation and composition systems offer a way to explore visual behaviour without building a complete renderer or patching environment from scratch. The application is useful as a performance surface for procedural work, though it is not a general-purpose node-based programming environment.

### Typography-led and bilingual visual artists

Text Art, animated typography, vertical writing options and the English/Japanese text pool make the software relevant to artists using language as an image: lyric visuals, title sequences, experimental captions, visual poetry and typographic performance.

### Workshops, studios and teaching spaces

It may also suit workshops or small studios that want to demonstrate the relationship between sound, rhythm and moving image. This is a secondary use case: the current application is an evolving creative tool, not a packaged curriculum or classroom-management product.

## When it is probably the wrong tool

- **Traditional film and video editing:** it does not offer the full editorial workflow of a non-linear editor, with a conventional clip timeline, detailed trimming tools, editorial metadata and finishing pipeline.
- **Audio production:** it does not replace a DAW, instrument, mixer or audio mastering system. Sonic Pi or another application remains responsible for sound playback.
- **Final master recording:** master-output recording and audio/video muxing are not implemented.
- **3D scene production:** the current visual system is built around 2D composition, generators, effects and particles rather than a full 3D authoring environment.
- **Unvalidated high-load installations:** projector hot-plug, long-duration stability and high-bitrate multi-stream performance still need to be checked on the target computer and GPU before a production-critical installation.

## System requirements

The packaged performance build targets **Windows 11 x64** and requires a current graphics driver with **OpenGL 3.3 Core Profile** support.

A practical starting point is 16 GB RAM for lighter sessions; 32 GB is recommended for multi-deck work, especially on integrated graphics. An SSD is recommended for the media index, thumbnails and footage. Start with H.264 720p or 1080p material. Four simultaneous high-bitrate 4K streams are not guaranteed on integrated graphics.

Sonic Pi is installed separately when OSC-driven music control is needed. MIDI hardware input is optional.

## Project and media files

Projects use the `.eliav` format and performance sets use `.eliset`. They store composition settings and media paths, not copies of the original video files. Keep the source media available and relink or re-import it after moving a project to another computer.

## Current development status

The repository contains the rendering, multi-deck video, generator, effects, audio-reactive, Sonic Pi, performance-control and central-workspace foundations. Some M6 and M7 areas remain in active development, and hardware acceptance is separate from automated code checks.

For implementation status and limitations, see the [Roadmap](ROADMAP.md), [M7 work plan](M7.md) and [Windows setup guide](SETUP_WINDOWS.md).

## Explore the project

- [Feature and milestone documentation](ROADMAP.md)
- [Windows setup](SETUP_WINDOWS.md)
- [Build the Windows executable](BUILD_PYINSTALLER_WINDOWS.md)
- [Architecture](ARCHITECTURE.md)
- [M2 — Generative visuals](M2_GENERATIVE_VISUALS.md)
- [M5 — Autonomous performance](M5_AUTONOMOUS_PERFORMANCE.md)
- [M5 — Performance environment](M5_PERFORMANCE_ENVIRONMENT.md)
- [M6 — Advanced VJ environment](M6_ADVANCED_VJ_ENVIRONMENT.md)
- [Sonic Pi / SONATA integration](SONIC_PI_SONATA_INTEGRATION.md)
- [Project file format](PROJECT_FORMAT.md)
- [Downloads and releases](https://github.com/ilyaminineli/eli_lab-av-translator/releases)

