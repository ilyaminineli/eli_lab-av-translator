# eli_lab AV Translator — Product Roadmap

**Roadmap snapshot:** 12 November 2026  
**Current priority:** M6 — Advanced VJ Environment. The initial M6-A1 live-deck surface is merged to main. M6-B0 is documented and M6-B1 full-scene capture/recall is underway on `m6/b1-vj-scene-bank`. M0–M5 software foundations are merged to main. M5 target-machine validation and the independent Video Mixer release gate remain open and continue in parallel; master-output recording/audio muxing is a separate deferred deliverable.

## Product goal

Build a dependable Windows-first audiovisual performance instrument: import a large personal footage library, compose four independent video decks into a live GPU canvas, create expressive visual treatments, run semi-random or fully unattended performances, and route the result to a second display or projector.

The roadmap is deliberately staged. M0–M2 establish the visual instrument. M3 adds audio analysis and the normalized transport/scene/macro control foundation. M4 adds Sonic Pi as a timed, semantic OSC source for that same control layer. M5 adds autonomous performance orchestration, Modulator Bank/per-layer control and an asynchronous generator-raster pipeline. M6 focuses on the operator-facing live VJ mixer.

**Development rule:** the Video Mixer Completion Gate remains an independent release criterion and is not marked passed. Later milestones may proceed in parallel, but do not describe the mixer as hardware/release-ready until its Windows reliability, projector and sustained-session checks have been completed.

---

## Current implementation snapshot

| Milestone | Current state | Notes |
| --- | --- | --- |
| M0 — Rendering Core | Core implemented; hardware hardening remains | PySide6 shell, OpenGL/ModernGL render contexts, canvas/layers, project persistence and fullscreen external output are present. |
| M1 — Video Collage | Core implemented; hardware/release gate open | Folder indexing, four decoder decks, transforms, blending, library cleanup, bounded import workers, decoder retirement and preview output limits are implemented on main. Manual deck, projector and long-run acceptance remains. |
| M2 — Generative Visuals | Core generator and overlay workflow implemented; advanced extensions remain | Geometry, Text Art, waveform and GPU particle fields are available. Still/animated-image/video overlays, layer effects, shader animation and project persistence are implemented. Vector paths, shape groups and a full particle simulation with lifetime/velocity/acceleration remain future extensions. |
| M3 — Audio-Reactive Engine & Control Foundation | Software implementation complete; Windows hardware sign-off pending | Internal transport and quantization, SoundCard input/loopback capture, FFT/onset/tempo analysis, scene profiles, editable modulation matrix, lock/manual-override precedence and persistence are implemented. Physical device/reconnect and sustained-session checks remain on the performance PC. The repository unit-test suite was removed at the user's request; current CI performs static checks only. |
| M4 — Sonic Pi Integration | Software complete; live rehearsal pending | Versioned `/eli_lab/v1` receiver, test sender, diagnostics, bounded validation, M3 clock/modulation bridge and optional SONATA sender are implemented. Verify the complete 384-bar performance on the target machine. |
| M5 — Performance Environment | Software implementation merged; target-machine acceptance pending | Performance Mode, AUTO PERFORMANCE, Modulator Bank, per-layer modifiers, MIDI/performance-set foundations, asynchronous generator rasterization and text-raster controls are on main. Quality #116 passed compile/Ruff. SONATA, audio-device, four-deck and projector checks remain manual; recording/muxing is deferred separately. |

### Observed machine test

During the November 4, 2026 user test, the application rendered the collage smoothly by user report and the runtime log identified **NVIDIA GeForce RTX 4060** during OpenGL initialization. This confirms that the application initialized on that machine; it is not yet a substitute for a long-duration soak test, multi-monitor reconnect test or performance benchmark.

### Recent reliability and performance hardening

- Thumbnail conversion now makes an owned C-contiguous RGB copy before creating the Qt image; a regression test covers a strided NumPy frame.
- The Media Library has a folder selector and a LIBRARY menu to remove one imported folder, prune missing source files, clear the index, or clean unused thumbnail files. These operations never delete the source videos.
- Folder scans are serialized and thumbnail generation is limited to two background workers, preventing a large import from spawning an unbounded number of simultaneous decode tasks. Destructive library actions are disabled while an import is still indexing.
- Legacy library databases recover imported root paths from the stable collection hash; intentionally imported empty folders remain visible and removable.
- Auto Mode refreshes its eligible source pool when collections are added or removed. Current deck playback is not interrupted; an empty pool simply stops scheduling further random cuts until footage is imported again.
- Decoder replacements use separate frame queues and retain references to workers that have not finished shutting down.
- Preview output is capped at 30 FPS and scaled to a maximum of 1920×1080 before RGB conversion. Smaller sources are not upscaled.
- The renderer reports rolling per-second decode and RGB-conversion cost, render CPU submission time, upload time/bandwidth, active deck count and per-second frame drops. These are diagnostic counters, not GPU timer queries.

The November 4 RTX 4060 screenshot showed approximately 18.9 FPS. The new counters are intended to identify whether the remaining limit is CPU conversion, texture upload or compositor submission. CPU-side timings are not GPU timer-query measurements, so hardware profiling is still required before claiming a specific bottleneck or improvement.

---

# M0 — Rendering Core

## Objective

Provide the stable desktop and GPU foundation on which every video, generator and performance feature is built.

## Implemented

- PySide6 desktop application shell and dockable work panels.
- Qt OpenGL widget with ModernGL rendering.
- Master composition canvas and layer model.
- GPU texture upload and multi-layer framebuffer compositing.
- Independent render contexts for preview and external fullscreen output windows.
- Shared CPU frame snapshots with independent per-window GPU texture uploads.
- .eliav project persistence for the composition and application state.

## Completion and hardening work

- Handle OpenGL context loss, window resize and renderer teardown without leaking resources.
- Test changing display resolution, Windows scaling/DPI, display orientation and primary-monitor selection.
- Handle a projector being disconnected or reconnected while the application is open.
- Make output-window lifecycle deterministic: one selected output, clear close behaviour, safe return to preview.
- Expose useful render diagnostics: actual output size, frame rate, renderer/GPU name and recoverable errors.
- Keep the UI responsive if a render context cannot be initialized.
- Confirm the saved project can be reopened after application restart and after a monitor configuration change.

**M0 exit condition:** preview and external output open, resize, close and reopen reliably; no stale GL resources or frozen UI after repeated operations.

---

# M1 — Video Collage

## Objective

Turn the canvas into a practical four-deck video mixer with a usable footage library and direct control over each source.

## Implemented

- Recursive local folder scanner and video metadata indexing.
- SQLite-backed media library.
- Background thumbnail generation and cached thumbnail paths.
- Four independent PyAV decoder decks with bounded frame queues.
- Per-deck load, play/stop and loop behaviour.
- Random in/out segment playback used by automation.
- Layer visibility, position, scale, rotation, opacity and z-order.
- Normal, Add, Screen, Multiply and Difference blend modes.
- Drag-and-drop folder import into the media browser.
- Random deck assignment and randomized collage layouts.

## Work required to make the mixer dependable

### Media ingest and library

- Make thumbnail conversion stride-safe, as covered by the regression test.
- Show a consistent placeholder and an actionable reason when a thumbnail cannot be produced; a thumbnail failure must never invalidate a playable asset.
- Keep scanning and thumbnail work bounded so importing thousands of clips does not overwhelm memory, worker threads or disk I/O.
- Prevent duplicate concurrent scans of the same folder and provide clear scan progress, cancellation and failure states.
- Revalidate missing or moved media paths and provide a relink workflow.
- Separate unsupported, corrupt and temporarily unavailable media states in the browser.
- Add search, sorting, collection filtering, favourites and a clear way to inspect clip metadata.

### Deck playback

- Make decoder shutdown, replacement and restart race-safe; old workers must not publish frames into a newly loaded deck.
- Test variable-frame-rate footage, long-GOP codecs, unusual frame sizes, rotation metadata and clips with no usable video stream.
- Provide robust end-of-file behaviour for both looping and one-shot playback.
- Add precise seek / scrub, frame stepping, pause and resume.
- Add playback speed and reverse playback only after timestamp and decoder behaviour can be kept correct.
- Define an explicit aspect policy: Fit, Fill/Crop and Stretch, with predictable source and canvas aspect handling.
- Keep playback state, duration, segment in/out and error state visible in the deck UI.
- Ensure one bad decoder cannot stall the other three decks or the render loop.

### Mixer and composition controls

- Make layer selection and deck-to-layer relationships obvious.
- Improve direct manipulation of position, size and rotation, including reset and fit-to-canvas actions.
- Provide predictable opacity and blend-mode controls with useful visual feedback.
- Add per-deck mute/hide/hold/freeze controls for visual operation (not audio muting).
- Add a practical transition model: hard cut first, followed by dissolve and selected stylized transitions.
- Make random composition choices reproducible when the user requests a seeded or saved run.

**M1 exit condition:** a user can load and mix four representative sources, make manual adjustments, save/reopen a composition, and continue playback without UI freezes, decoder cross-talk or unexplained loss of a deck.

---

# M2 — Generative Visuals

## Objective

Give the video mixer a distinctive visual toolkit and make automated performances feel composed rather than merely shuffled.

## Implemented foundations

- GPU master post-processing pass after the layer compositor.
- First-class transparent generator layers integrated into the standard composition transform, opacity, blend mode, z-order and project serializer.
- Procedural geometry: concentric rings, grids, radial constructions, crosshatch and nested polygons.
- Typographic art with editable multiline content, installed system fonts, weight, size, tracking, line spacing, alignment, outline, shadow and alternate accent-line colours.
- Procedural waveform visuals: sine traces, Lissajous figures, orbit patterns, radial traces and rose curves.
- Expanded geometry patterns: spiral, moiré and hex-grid constructions.
- Text Art single-block and seeded typographic collage layouts, bilingual English/Japanese thematic text pools, and type-on, word reveal, line wave, jitter, crawl and glitch motion.
- Debounced live Text Art updates; text motion runs in the GPU shader without re-rasterizing unchanged glyph artwork.
- GPU procedural particle field with density, size, speed, spread, trails, colours, and drift/rise/fall/orbit modes.
- Still, Qt-supported animated-image and video overlays as saved, reorderable composition layers.
- Independent per-layer FX stack with bypass/mix, monochrome, threshold/Xerox, invert, posterize, hue, contrast, saturation, brightness, scanlines and RGB separation.
- Static generator content is rasterized only when settings change; layer and text motion run in the GPU compositing shader.
- Generator layers render independently in preview and projector contexts.
- Brightness, exposure, contrast, saturation, gamma, temperature, tint and hue rotation.
- Vignette, grain, scanlines, RGB split / chromatic aberration, glitch and pixelation.
- Posterization, inversion, halftone print and solarization.
- Global effect bypass and processed/unprocessed mix for A/B comparison.
- Additional looks: Halftone Print, Photocopy, Infrared, Cold Steel and Solarized.
- Built-in Clean, 16mm Film, VHS / Tape, CRT, Bleach Bypass, Dream Haze and Digital Damage looks.
- Effect and automation settings saved in .eliav projects.
- Semi-random collage layouts and timed effect-look changes.
- Unattended automation sessions with a selected duration or manual stop.

## Remaining generator work

### Geometry

- Editable vector paths, Bézier curves, text-on-path and shape groups.
- More parameterized pattern families and procedural tiling systems.
- Optional geometry instancing for high-density scenes.
- Generator-level macro parameters and reusable user presets.

### Particles

- Upgrade the first procedural GPU field into a general simulation with particle lifetimes, velocity/acceleration curves and bounded resource budgets.
- Emit from points, paths, shapes and sampled image/video regions.
- Add force fields: turbulence, attraction, repulsion, orbit and drag.
- Add seeded emitter presets and a stable scene recall model.

### Waveform and signal visuals

- Additional oscilloscope, phase-scope, circular scope and signal-grid styles.
- Editable amplitude envelopes and independent phase controls.
- In M3, allow the same visualizers to subscribe to live audio bands or beat events without coupling the generator to the audio input device.

### Typography

- Rich text runs with multiple styles and colours inside one text layer.
- Text paths, true packed/contour-aware layouts, vertical CJK text and variable font axes.
- More entrance/exit behaviours, per-word timing and text motion presets.
- Additional layout anchors, safe areas and alignment guides.
- Project-safe font fallback and explicit missing-font handling.

### Particle simulation extensions

- Add emitter shapes, particle lifetime/velocity curves, acceleration and trail persistence.
- Add CPU/GPU resource ceilings and deterministic seeds for saved particle scenes.

### Effect and overlay system

- Expand the current compact per-layer FX controls into reorderable effect-stage chains with a documented order.
- Add user-saveable layer FX chains and project-level preset import/export.
- Add overlay in/out timing, playback speed, frame hold, masks/track mattes and scene sync.
- Add more animated overlay controls while preserving independent preview/projector frame snapshots.
- Add safe automation variation for layer effects and overlays with manual override and cooldowns.

**M2 exit condition:** a saved composition can combine video decks, generated geometry, particles, typography and overlays; its looks can be adjusted manually or varied by automation; the same composition renders consistently in preview and projector output.

---

# Independent Release Gate — Video Mixer Completion Gate

This is an independent reliability/release track. It closes the gap between a promising live prototype and a dependable visual performance tool; later feature milestones may proceed in parallel.

## Gate A — Reliability first

1. Fix and regression-test the non-contiguous thumbnail buffer error.
2. Make media scanning and thumbnail generation resilient to large folders and individual bad files.
3. Verify decoder replacement, EOF, one-shot segments, loop boundaries and shutdown.
4. Make all worker-thread ownership and cancellation explicit.
5. Ensure errors are visible and local to the failed asset/deck, never fatal to the session.
6. Exercise project save/load with missing footage, moved paths and older schema versions.

## Gate B — Finish the hands-on mixer

1. Complete the deck transport controls and clear visual feedback.
2. Add Fit / Fill / Stretch and predictable transforms.
3. Improve layer selection, ordering, lock, hide and per-layer blend controls.
4. Add hold/freeze and a small, reliable transition set.
5. Make the media library practical to search and curate.
6. Keep preview and projector output frame-consistent.

## Gate C — Make Auto Mode a real instrument

The existing random mode is a foundation. It should mature into a controllable director with:

- A selectable source pool and per-deck include/exclude rules.
- Independent deck timing, segment length and loop/one-shot behaviour.
- Weighted clip selection with no immediate repeats where the pool allows.
- Cut pacing profiles and user-defined minimum / maximum timing.
- Layout families with intensity / complexity controls.
- Effect and overlay variation with intensity limits and cooldowns.
- Lock, hold and manual override behaviour that automation always respects.
- Scene-aware choices so a session has coherent changes rather than unrelated parameter noise.
- Optional deterministic seed and a record of the last automated action.
- Session duration, pause/resume and safe stop that does not abruptly black out the composition.
- A quick “re-roll this deck / layout / look” action for live intervention.

Automation must never overwrite locked content, exceed configured safety ranges or block the UI while loading media.

## Gate D — Visual identity and control

- Polish the mixer UI into a deliberate VJ surface: clear deck status, strong hierarchy, compact transport and useful meters/indicators.
- Add a small set of high-quality, coherent visual presets before adding dozens of shallow effects.
- Give every generator and effect sensible defaults and an obvious bypass.
- Make overlays and typography easy to edit during playback.
- Provide feedback for active automation, current look, current layout and remaining session time.

## Gate E — Performance and hardware validation

- Measure preview and projector frame rate independently.
- Record decode latency, dropped frames, queue depth and GPU render time.
- Stress-test four concurrent clips at 1080p H.264, then test representative higher-resolution footage.
- Test 30-minute and 60-minute unattended sessions.
- Test repeated projector open / close, display disconnect / reconnect and window resizing.
- Check memory, thread count and GPU resources before and after a long run.
- Keep a graceful reduced-load mode for machines that cannot decode four demanding sources simultaneously.

**Video Mixer release criterion:** all gates above have been exercised on Windows hardware, critical errors are resolved, a 60-minute run completes without degradation, and the user can recover from a bad media file or output-display change without restarting the application.

---

# M3 — Audio-Reactive Engine & Performance Control

## Objective

Add a source-independent performance-control layer and optional audio analysis. Audio is the first live analysis source; M4 adds Sonic Pi OSC to the same normalized control contract.

## Implemented

- Drift-resistant internal transport/test clock with BPM, meter, beat/bar position, start/pause/resume/stop and bounded catch-up.
- Immediate, beat, bar and four-bar phrase scene quantization.
- Scene profile registry with sixteen SONATA-compatible IDs, master-look and Japanese colour-palette assignments, and intensity values.
- SoundCard physical-input and supported system-loopback capture through a dedicated owned worker.
- Device-loss/error states, explicit cancellation/shutdown, source refresh and restart after device reconnection.
- Deterministic synthetic source and recorded fixture replay.
- Bounded audio-frame queue and RMS/peak, low/mid/high FFT energy, onset and optional tempo/confidence analysis.
- Configurable sensitivity, attack/release, onset threshold and tempo confidence/range.
- Explicit modulation source and target registries, source/target ranges, mapping curves, inversion, smoothing, attack/release, hold, bypass and intensity ceiling.
- Targets for master effects, selected-layer opacity/rotation, generator motion/density and Auto Performance timing/loop probability.
- One route per target for deterministic ownership, with editable routes in the Audio / Control dock.
- Layer lock and manual-override precedence, including baseline restoration when modulation is released.
- Project persistence for transport configuration, audio-analysis settings, routes and scene profiles; live device handles and analysis buffers are not persisted.
- Audio / Control UI dock, meters and status monitor; no audio or control worker performs Qt widget or OpenGL work.

## Verification

Windows CI covers the internal clock, quantized scenes, FFT/onset/tempo analysis, fake input/loopback backends, recorder ownership, device-loss handling, fixture replay, bounded queues, modulation routing, project round-trip and the Qt control/lock panels.

The optional runtime dependency is `soundcard>=0.4.6`. Audio capture is optional; an unavailable device reports an error locally without stopping video playback.

**M3 software exit condition:** complete.

**Remaining hardware sign-off:** on the intended Windows performance machine, test a physical input and system loopback, unplug/reconnect the active device, verify manual source refresh/restart, and run a sustained audio-reactive session while video is rendering. CI's fake devices do not replace those checks.

See [M3 Audio-Reactive Foundation](M3_AUDIO_REACTIVE_FOUNDATION.md).

---

# M4 — Sonic Pi Integration

## Status

**Software implementation complete; full live SONATA rehearsal remains a manual validation step.**

## Delivered

- Dedicated local IPv4 OSC receiver with loopback default and configurable bind address / port.
- Versioned `/eli_lab/v1` decoder translated into M3 `ControlEvent` events.
- Strict address, argument-count, type, numeric-range and macro-name validation.
- Session IDs, monotonically increasing per-session sequence numbers, restart de-duplication and stale-session rejection.
- Bounded 60-message/second ingress, malformed-packet recovery and diagnostics for last address, freshness, accepted, rejected, rate-limited and dropped messages.
- A single network worker that only submits validated events to the bounded M3 queue; the application/UI tick owns state changes.
- AUDIO / CONTROL dock controls and live/stale receiver monitor.
- Local deterministic OSC sender and UDP/protocol tests that do not require Sonic Pi.
- SONATA sender helper with explicit host/port, unique session ID, shared sequence counter and no-AV toggle.
- Patch output at start, bar, scene, per-bar energy/cutoff macro, four-bar phrase, heartbeat and end points. The 93 audio loops remain untouched.

## Exit condition

The protocol is documented and versioned; CI verifies strict decoding, session restart/de-duplication, local UDP delivery, malformed packet recovery and bounded queue failure. The SONATA source emits the required high-level events from its musical clock. A live 384-bar Sonic Pi rehearsal is still required to sign off exact runtime scheduling on the target machine.

See [SONATA Expanded integration notes](SONIC_PI_SONATA_INTEGRATION.md).

---

# M5 — Performance Environment

## Status

**M5 software implementation is merged to main.** Performance Mode, AUTO PERFORMANCE, Modulator Bank, per-layer performance modifiers, MIDI/performance-set foundations, asynchronous generator rasterization and text-raster controls are implemented. Quality workflow #116 passed compile/Ruff on main commit `358dc597`. Live SONATA, audio-device, four-deck stress and projector acceptance remain manual sign-off. Master-output recording/audio muxing is not implemented and is tracked separately; it does not block starting M6.

## Implemented

- One-button Performance Mode in the main toolbar. It starts/reuses the versioned Sonic Pi OSC receiver, optionally starts system-loopback capture, enables generated curves and arms AUTO PERFORMANCE.
- SONATA transport/start or the first clock/bar event switches the mode LIVE and starts AUTO PERFORMANCE. Scene selections and phrase cues trigger musical visual decisions; transport/stop stops the automation session while the mode waits for a patch restart.
- Shared Sonic Pi energy/cutoff and transport controls plus local audio RMS/peak/low/mid/high/onset features feed one automation energy/cutoff context. Stale audio and OSC inputs expire rather than holding the last value indefinitely.
- Non-destructive default routes for master effects, AUTO cut/clip/segment/layout/effect/generator controls, and generated per-layer curves for video transforms, procedural geometry, Text Art, waveform, particles and animated overlays.
- Built-in Modulator Bank followers, envelopes and phrase LFOs are created/reused and connected to compatible layer parameters.
- AUTO PERFORMANCE supports random, structured and generative styles with time, bar, phrase and hybrid scheduling. Phrase mode gates off the independent wall-clock randomizer so musical cues own the variations.
- Stop Performance Mode disables only generated AUTO defaults, restores their baselines and closes only the OSC/audio services it started. User-authored mappings and previously running services are preserved.
- Project saves persist the selected Performance Mode plan but store generated default routes/modifiers disabled, so project opening does not unexpectedly start a live show.
- Dictionary candidates in `generators/text_pools.py` are cached by language, theme and dictionary-file version to avoid rescanning multi-megabyte dictionaries on each regeneration.
- Unified diagnostics for OSC counters/freshness, audio state/queue/drop count, control queue, active routes/modulators, automation section/energy/cutoff and video/render metrics.

## Remaining validation and separately deferred work

- Full 384-bar SONATA rehearsal, including scene/bar/macro/phrase timing and stop/restart recovery.
- Windows physical-input/system-loopback selection, device loss/reconnect and sustained capture.
- Four-deck continuous typing with multiple generators, effects, audio reactivity and projector output; record input responsiveness, raster rate/duration, FPS and dropped frames.
- Projector open/close, display hot-plug, frame pacing and long-duration session validation.
- Master-output recording and audio/video muxing are not implemented; keep this as a separate deferred output-delivery feature rather than treating it as completed M5 scope.

## Verification and repository cleanup

- The `tests/` unit-test suite and pytest dependencies were removed at the user's request. CI has been replaced with Python compilation and Ruff checks; it no longer runs unit tests.
- Quality workflow #116 passed on main commit `358dc597` with Python compilation and Ruff. CI does not execute runtime, musical, audio-device or GPU/projector validation.

**M5 implementation exit is met and merged.** M5 live-performance acceptance remains open until the target-machine checks above are run and recorded. Recording/audio muxing is explicitly deferred as a separate deliverable. See [M5 Completion & Live Validation Handoff](M5_COMPLETION_HANDOFF.md).

See [M5 Autonomous Performance](M5_AUTONOMOUS_PERFORMANCE.md), [M5 Performance Environment](M5_PERFORMANCE_ENVIRONMENT.md), [M5 Unified Mapping Matrix](M5_MAPPING_MATRIX.md), [M5 Performance Modifiers](M5_PERFORMANCE_MODIFIERS.md) and [M5 Modulator Bank](M5_MODULATOR_BANK.md).

# M6 — Advanced VJ Environment

## Status

**Merged foundations — M6-A1, M6-B1, M6-C1, M6-D1/D2 and M6-E1 are on `main`.** C1 adds GPU transforms and feedback; D1/D2 add the bounded GPU particle system and source/path emitters; E1 adds rich typography, vertical layouts, paths and shader motion. The current live-performance follow-up connects these new targets to AUTO PERFORMANCE, adds rate-based particle emission and retains state across short layer cuts. Adaptive compact/4:3 workspace sizing and the Queer text pool are included. Target-Windows GPU/projector acceptance remains open; media bins, synchronized multi-trigger, scene transitions and D3 particle authoring remain future work.

## A. A proper live mixer

The current four-deck system remains the playback foundation. The operator should be able to work more like a live VJ: prepare clips in performance-oriented media bins, trigger one or multiple clips deliberately, understand deck state at a glance and perform common source/mix actions without navigating through detailed editing docks.

Initial design/implementation slices:

1. **Operator model and deck surface:** clear source identity, thumbnail, playback/segment state, lock/hold/error feedback and direct deck transport.
2. **Media bins:** named show bins/collections that reference indexed media without duplicating or moving source files.
3. **Explicit clip routing:** single-clip trigger into a chosen deck; multi-selection mapped visibly to available decks. Selecting, loading and triggering must be distinct actions.
4. **Multi-trigger and sync:** multiple deck launches treated as one action, with immediate launch first and optional beat/bar/phrase quantization using the existing control clock. Pending launches must be visible and cancellable.
5. **Mix and transitions:** define deck levels/opacity, A/B or group selection and a crossfade/transition model that reuses existing layer/compositor state. Hard cuts remain deterministic; additional transitions require measured render cost.
6. **Performance integration:** manual controls, automation, lock/manual-override precedence, event diagnostics and persistence of bins/operator preferences.

Before coding, settle the policy when more clips are selected than decks are available and when a target deck is already playing. Do not silently overwrite a live source. A dedicated program/preview bus is not part of the existing architecture and should be treated as a design decision, not an already implemented feature.

## M6-A acceptance

- A show can be prepared in named media bins without interrupting current playback.
- A single clip can be loaded and triggered into a selected deck.
- Multiple clips can be mapped to available decks and launched as one operator action.
- Quantized launches share one beat/bar/phrase boundary and can be cancelled before triggering.
- Deck source, playback, pending, locked and failed states are visible on the live surface.
- Manual protection and locks prevent AUTO PERFORMANCE from unexpectedly replacing operator-controlled material.
- Four-deck playback, generators/effects and projector output continue to use the existing bounded worker and per-context rendering architecture.
- Media/decode failures remain local and the UI stays responsive under active four-deck load.
- Bins and assignments can be saved/reopened without persisting decoder handles or GPU resources.

The detailed initial scope and staged acceptance checklist are in [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md).

## M6-B — VJ Scene and Composition Banks

**In progress — M6-B1 full-scene capture/recall.** The existing Performance Scene Bank is being promoted into a first-class VJ Scene Bank without creating a parallel persistence system. B1 captures deck assignments, composition/layers, master and layer effects, palette, automation/transport, modulation routes and Modulator Bank definitions. It adds cue-based OSC and MIDI scene triggering, internal/external clock quantization and compatible random selection.

**Transition boundary:** current numeric-compatible parameters morph; discrete media/text/generator changes still use a cut. Dual-scene crossfade, midpoint switching, sequences and per-parameter locks remain planned.

See [M6-B — VJ Scene and Composition Banks](M6_B_SCENE_COMPOSITION_BANK.md) for implementation details and acceptance criteria.

## M6-C — Advanced Visual Transformations

**C1 implementation in progress.** Extend the ModernGL compositor with GPU-only image geometry and temporal processing. The first slice includes kaleidoscope, polar remapping, mosaic/tile, directional scan displacement, selectable layer-driven displacement maps, edge extraction, ordered dithering and a dedicated feedback engine with bounded per-renderer GPU history. Feedback exposes amount, decay, zoom, rotation, translation, colour shift, distortion, motion-driven warp, datamosh blocks, blend mode, short frame delay, freeze and reset.

Directional scan sorting is a controlled shader approximation, not a full image-region sorting algorithm. Motion-driven warp is temporal-difference/gradient driven, not a dense optical-flow solver. These limitations and later C2/C3 work are documented in [M6-C — Advanced Visual Transformations](M6_C_ADVANCED_VISUAL_TRANSFORMATIONS.md).

## M6-D — Advanced Particle Simulation

**D1 + D2 are merged to `main`.** Particle System 2.0 remains separate from the legacy procedural `particles` field. D1 adds point/circle/rectangle emitters, deterministic seeded populations, fixed-step GPU lifetime/velocity/acceleration simulation, turbulence, attract/repel/orbit fields, size curves and trails. D2 adds editable path emitters, video-luminance, image alpha/luma silhouette and contour emitters, plus GPU source-target reformation with periodic target resampling. The live-event follow-up adds a bounded 0–3000 particles/second emission rate (distributed across populations), event-driven AUTO PERFORMANCE mappings and six-second state retention across brief inactive cuts. Resource ceilings remain 8192 particles per system, four systems and 16384 particles per output renderer. Simulation and source sampling are owned by each Compositor/GL context and bypass the CPU raster service.

Per-population overrides and advanced vector/collision fields remain D3 work. See [M6-D — Advanced Particle Simulation](M6_D_ADVANCED_PARTICLE_SIMULATION.md).

## M6-E — Typography as an independent visual instrument

E1 is merged to `main`. It extends Text Art without moving layout or raster work into the frame loop:

- Styled rich-text runs with per-run typeface, size, weight, colour, tracking, outline and shadow.
- Horizontal mixed-language layout, vertical right-to-left / left-to-right columns, and text on circular, arc and custom paths.
- GPU texture-space animation controls for reverse typewriter reveal, dissolve, flicker, character-cell displacement, vertical reveal, scattered glyph motion, segmented collision-style movement and mechanical scrolling.
- AUTO PERFORMANCE now has a live target for text reveal-step/column density, in addition to text motion speed and amount.

The next E2 slice should introduce a bounded glyph atlas/instance representation for truly independent per-character transforms, deterministic replacement, and word/character timing. E3 can address reusable typographic presets and a dedicated text-feedback route. E1's vertical layout and shader modes require visual validation on the Windows target GPU; they are not yet a per-glyph engine.

See [M6-E — Typography as an Independent Visual Instrument](M6_E_TYPOGRAPHY.md).

## M6 live-performance integration follow-up

The new text, layer-FX and Particle System 2.0 controls are registered as per-layer performance targets and in the manual modulation/MIDI target registry. AUTO PERFORMANCE includes energy/beat/onset routes for particle emission and physics, phrase/energy routes for trails and source reformation, reveal-step motion for typography, and modulation of GPU layer-FX parameters. GPU-only changes remain uniform updates; they do not require per-frame CPU rasterization.

The workspace adapts dock constraints and default sizing for compact and 4:3 windows while preserving user-saved layouts. The compositor already fits the existing composition canvas to output aspect without distortion; it letterboxes rather than stretching content. This UI adaptation does not silently change a project's stored canvas resolution.

Text Art includes an explicit **Queer / クィア** pool with the word **QUEER**, identity and pronoun vocabulary, and short self-definition / chosen-family phrases in English and Japanese. Offensive English dictionary headwords are filtered during dictionary ingestion as an additional safeguard; local dictionary files remain user-editable and should continue to be curated.

See [M6 Live Performance and Workspace Integration](M6_LIVE_PERFORMANCE_WORKSPACE.md) for implementation details and acceptance checks.

## Engineering principles across all milestones

1. **Rendering must stay isolated.** Decoder, audio and OSC workers publish data; only the relevant render context owns and changes its GPU resources.
2. **Bound every queue.** No unbounded frame, event or analysis buffers in a long-running session.
3. **Keep the UI non-blocking.** File scanning, thumbnail generation, decoding, audio capture and OSC I/O must not run synchronously on the main UI thread.
4. **Prefer recoverable failure.** A broken file, lost input device or disconnected output should be isolated and reported, not crash the whole performance.
5. **Persist intent.** Projects and performance sets should store user-facing settings and stable identifiers, not transient GPU objects or worker state.
6. **Make automation explainable.** Show what changed, when, and why; respect locks and manual overrides.
7. **Test the seams.** Cover worker replacement, device changes, project compatibility, timing boundaries and preview/output synchronization.
8. **Optimize from measurements.** Add diagnostics before choosing frame dropping, resolution scaling or decoder concurrency policies.

## Immediate next implementation order

1. Validate M6-C1 geometry/feedback on the target Windows GPU, including resize, freeze/reset, delay and dual-output independence.
2. Validate M6-D1/D2 simulation on the target GPU: determinism, source/path emitters, reformation against live footage, resource ceilings, particle/trail quality, resize, layer removal and dual-output independence.
3. Continue M6-A2/A3: named media bins, explicit deck routing, atomic multi-trigger and quantization.
4. Continue M6-B2: dual-scene transition engine, then scene sequences and parameter locks.
5. Continue M5 target-machine validation and the independent Video Mixer Completion Gate. Keep recording/audio muxing separately scoped.

See [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md) for the current M6-A scope and acceptance criteria.
