# eli_lab AV Translator — Product Roadmap

**Roadmap snapshot:** 6 November 2026  
**Current priority:** M5 live SONATA validation and master-output recording/audio muxing, followed by M6 definition. M4/M5 software foundations are merged to main; Windows loopback, target-machine/projector acceptance and the independent Video Mixer hardware release gate remain open.

## Product goal

Build a dependable Windows-first audiovisual performance instrument: import a large personal footage library, compose four independent video decks into a live GPU canvas, create expressive visual treatments, run semi-random or fully unattended performances, and route the result to a second display or projector.

The roadmap is deliberately staged. M0–M2 establish the visual instrument. M3 adds audio analysis and the normalized transport/scene/macro control foundation. M4 adds Sonic Pi as a timed, semantic OSC source for that same control layer. M5 turns the application into a configurable live performance environment.

**Development rule:** the Video Mixer Completion Gate remains an independent release criterion and is not marked passed. M3 foundation work may proceed, but do not describe M0–M2 as release-ready until the Windows hardware and 60-minute validation has been completed.

---

## Current implementation snapshot

| Milestone | Current state | Notes |
|---|---|---|
| M0 — Rendering Core | Core implemented; hardware hardening remains | PySide6 shell, OpenGL/ModernGL render contexts, canvas/layers, project persistence and fullscreen external output are present. |
| M1 — Video Collage | Core implemented; reliability pass in progress | Folder indexing, four decoder decks, transforms, blending and random collage behaviour are present. Safe library cleanup, bounded import workers, decoder retirement and preview output limits are now implemented in the hardening branch. |
| M2 — Generative Visuals | Core generator and overlay workflow implemented; advanced extensions remain | Geometry, Text Art, waveform and GPU particle fields are available. Still/animated-image/video overlays, layer effects, shader animation and project persistence are implemented. Vector paths, shape groups and a full particle simulation with lifetime/velocity/acceleration remain future extensions. |
| M3 — Audio-Reactive Engine & Control Foundation | Software implementation complete; Windows hardware sign-off pending | Internal transport and quantization, SoundCard input/loopback capture, FFT/onset/tempo analysis, scene profiles, editable modulation matrix, lock/manual-override precedence and persistence are implemented. Physical device/reconnect and sustained-session checks remain on the performance PC. The repository unit-test suite was removed at the user's request; current CI performs static checks only. |
| M4 — Sonic Pi Integration | Software complete; live rehearsal pending | Versioned `/eli_lab/v1` receiver, test sender, diagnostics, bounded validation, M3 clock/modulation bridge and optional SONATA sender are implemented. Verify the complete 384-bar performance on the target machine. |
| M5 — Performance Environment | Autonomous Performance Mode implemented; release gates remain | One-button Sonic Pi orchestration, default reactive mappings, Modulator Bank/per-layer curves and phrase-aware AUTO PERFORMANCE are implemented. Master-output recording/audio muxing, target-machine rehearsal and output validation remain open. |

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

# Video Mixer Completion Gate — Priority Before M3

This is the immediate delivery track. It closes the gap between a promising live prototype and a dependable visual performance tool.

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

**M5 software implementation is merged to main. Autonomous Performance Mode, the Modulator Bank, per-layer performance modifiers and Sonic Pi orchestration are implemented. Live SONATA and target-machine validation remain manual sign-off; master-output recording/audio muxing is not implemented, so the M5 milestone exit remains open. A Windows x64 one-file release build is configured on `release/windows-onefile-readiness`; its native Windows build and Lenovo/projector acceptance tests remain pending.**

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

## Remaining work and sign-off

- Master-output recording with bounded frame handoff, encoder worker, configurable format/frame rate/destination and audio muxing.
- Explicit output recording routing and target-machine preview/projector frame-pacing and A/V synchronisation validation.
- Last-known-good set recovery and optional event/performance-session recording.
- Full 384-bar SONATA rehearsal, Windows system-loopback reconnect and long-duration autonomous session validation.

## Verification and repository cleanup

- The `tests/` unit-test suite and pytest dependencies were removed at the user's request. CI has been replaced with Python compilation and Ruff checks; it no longer runs unit tests.
- A static quality workflow must pass on the latest PR head. Hardware and musical rehearsal remain manual sign-off.

**M5 exit condition is not yet met** until master-output recording/audio muxing is delivered and the target-machine validation gates are completed. For the same-computer SONATA setup and the exact live rehearsal checklist, see [M5 Completion & Live Validation Handoff](M5_COMPLETION_HANDOFF.md).

See [M5 Autonomous Performance](M5_AUTONOMOUS_PERFORMANCE.md), [M5 Performance Environment](M5_PERFORMANCE_ENVIRONMENT.md), [M5 Unified Mapping Matrix](M5_MAPPING_MATRIX.md), [M5 Performance Modifiers](M5_PERFORMANCE_MODIFIERS.md) and [M5 Modulator Bank](M5_MODULATOR_BANK.md).

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

1. Perform the live SONATA 384-bar rehearsal and verify bar/scene/macro timing, session restart and lost-packet recovery.
2. Perform M3 hardware sign-off on Windows: physical input, system loopback, device unplug/reconnect, source refresh/restart and sustained capture while video is playing.
3. Continue the Video Mixer Completion Gate as a separate release track; do not infer its hardware sign-off from M3 CI.

M3 is the control foundation and audio-analysis source. M4 is the explicit Sonic Pi integration milestone. The two share the normalized event/state contract; neither needs to change the GPU renderer.
