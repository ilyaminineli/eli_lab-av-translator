# Architecture

## Product and runtime boundaries

eli_lab AV Translator is a Windows-first live audiovisual/VJ performance environment. The application combines four independent video decks, composition layers, procedural generators, overlays, GPU effects and renderer-independent performance controls. M5 adds autonomous show orchestration and a shared asynchronous generator-raster pipeline. M6 is planned to make the operator experience more like a dedicated live VJ mixer.

The main ownership boundaries are:

- **UI** owns Qt widgets, editor state, dock/window lifecycle and operator controls.
- **Application core** owns the composition, project state, service coordination, event application and automation/performance ticks.
- **Media** owns discovery, metadata, thumbnails, decoder workers and bounded video/image frame queues.
- **Generators** own normalized settings, CPU rasterization and the application-shared raster job service.
- **Rendering** owns per-window OpenGL resources, video/generator textures, composition and post-processing.
- **Effects** own master and per-layer effect settings/presets.
- **Performance control** owns normalized transport, scene, audio, OSC/MIDI, modulation, modifier and Performance Mode state.

Worker threads publish immutable or copied CPU-side data. They do not update Qt widgets, mutate the composition or create/change OpenGL resources.

## Rendering lifecycle

1. Qt creates a `QOpenGLWidget` context for the local preview or projector output.
2. `PerformanceView.initializeGL` creates that window's ModernGL wrapper and compositor.
3. Each video decoder produces timestamped CPU frames into its bounded queue.
4. The application tick consumes each deck queue and updates shared latest-frame snapshots.
5. Preview and projector renderers read the same CPU snapshots independently.
6. Each `RenderEngine` uploads only unseen revisions into textures owned by its own GL context.
7. The compositor blends visible video, generator and overlay layers into ping-pong framebuffers, applying per-layer FX.
8. The master GLSL effect pass processes the composed output.
9. The final framebuffer is drawn into that output window's Qt framebuffer.

The two outputs share application/composition state and CPU frame snapshots. They do **not** share GL texture objects or GL contexts.

## Generator raster lifecycle

Static generator rasterization is owned by one `GeneratorRasterService` created by `Application` and shared by all output renderers.

- The service uses a single condition-driven background worker. It creates CPU pixel arrays only.
- Requests carry a copied settings snapshot, dimensions, fingerprint and monotonically increasing per-layer revision.
- An ordered pending map holds at most one waiting snapshot per layer. A newer request replaces that layer's pending snapshot instead of adding an obsolete keystroke to a backlog.
- There is at most one active raster job globally. Text jobs have a configurable start-rate limit; non-text generator jobs are not blocked by that text-only limiter.
- Completion or failure is accepted only when the job's revision and fingerprint still match the newest request. Renderers validate again when receiving the signal and before uploading.
- The service caches the latest completed CPU snapshot. Each renderer performs its own upload only while its own GL context is current.
- Deleting layers, project reset/load and application shutdown invalidate pending/completed work. The previous valid texture can remain displayed while a replacement is generated or when a replacement fails.

Static text content and typography are rasterized on the CPU. Text motion (type-on, word/column reveal, line wave, jitter, crawl and signal glitch) is applied by the existing compositor shader using per-frame uniforms; motion-only changes do not submit a CPU raster job.

Text editing keeps a UI buffer separate from committed layer settings. The operator can pause live preview, commit after a typing pause, apply immediately, select 25/50/75/100% preview quality, request full-resolution 1600×900 output, rate-limit text raster starts, freeze the currently displayed texture and retain the last valid result after a failure. Pipeline state is exposed to the editor.

## Performance-control lifecycle

M3 introduced the normalized transport/audio/control model. M4 adds the versioned `/eli_lab/v1` OSC adapter. M5 connects those sources to Performance Mode, AUTO PERFORMANCE, the Modulator Bank and per-layer performance modifiers.

1. Audio, OSC, MIDI and internal transport adapters validate input and publish normalized events or feature snapshots.
2. Network/device callbacks place bounded items into thread-safe queues; they do not mutate composition or UI state.
3. The application tick drains a bounded batch, updates performance-control state and evaluates modulation/modifiers.
4. Registered targets update existing layer, generator, effect or automation settings subject to range, lock, manual-override and ownership rules.
5. Performance Mode installs only missing defaults, tracks which services it started and releases only resources it owns when stopped.
6. Project files persist user-facing configuration and stable IDs, not live device handles, worker threads, active GL resources or transient signal buffers.

Sonic Pi macros are normalized musical controls, not raw audio. System loopback is needed for local RMS/FFT/onset analysis of the sound output.

## Runtime resources and writable data

Read-only packaged resources (icons, textures, sketches and dictionaries) are resolved from the source tree during development or from the frozen application bundle at runtime. PyInstaller's one-file bootloader extracts bundled data into its runtime directory; bundled module `__file__` paths resolve inside that extraction root. The runtime hook also supplies safe stdout/stderr sinks for a windowed executable.

Writable data is kept separately under:

`%LOCALAPPDATA%\eli_lab\AV Translator\`

This includes the SQLite media database, thumbnail cache and logs. User footage, project files and user-added asset roots remain external and are never written into the temporary one-file extraction directory.

## Packaging and checks

The supported local Windows one-file build is `scripts/build_pyinstaller.py`, using the repository-local `.venv` and `AVTranslator.spec`. It supports 64-bit CPython 3.12–3.14, installs the pinned build requirements, checks imports and dependencies, compiles the source, creates the one-file executable and runs its `--self-check`. Native `python-rtmidi` support is optional and may be built separately with `--with-midi`.

The GitHub Windows Onefile Build workflow is manual-dispatch only. The normal Quality workflow performs Python compilation and Ruff; it is not a GUI, OpenGL, audio-device or hardware integration test. See [Windows PyInstaller build guide](BUILD_PYINSTALLER_WINDOWS.md).

## Project data

`.eliav` projects persist composition/layers, deck assignments, effects and performance configuration. `.eliset` performance sets persist a reusable performance setup, including deck state, automation/performance settings, scenes and MIDI mappings. Media files are referenced by path and are not embedded. Runtime handles, GPU objects and transient frame/audio queues are recreated when a project/set is loaded.

## M6 direction

M6 — Advanced VJ Environment — is planned. Its first defined workstream is a live-mixer interaction model with media-bin clip triggering, including simultaneous triggers. The current four video decks remain the playback foundation; M6 should build a dedicated operator surface without moving decode, composition or GPU ownership into the UI. See [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md).
