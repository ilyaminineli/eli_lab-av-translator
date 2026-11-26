# M0 — Rendering Core

## Scope

- Windows desktop bootstrap with PySide6.
- OpenGL 3.3 Core request.
- ModernGL wrapper created from Qt's current OpenGL context.
- QOpenGLWidget master preview.
- Composition and layer data models.
- Event bus and atomic project persistence.
- Renderer diagnostics and clean resource shutdown.

## Acceptance

- Application opens and presents a master canvas.
- Renderer diagnostics identify the active OpenGL renderer.
- Preview resizes with the window.
- Composition/layers serialize and deserialize.
- Project save uses an atomic temporary-file replacement.
- The former unit-test suite has been removed at the user's request. Current CI runs Python compilation and Ruff; renderer/GPU behaviour requires a live Windows hardware check.

# M1 — Video Collage

## Scope

- Recursive folder scanner and metadata probe.
- SQLite-backed media library.
- Asynchronous thumbnail generation.
- Four independent PyAV video decoders.
- Timestamp-paced playback and bounded latest-frame queues.
- GPU video texture upload.
- Four-layer compositor with position, scale, rotation, opacity and blend modes.
- Random deck assignment and randomized layout with layer locks.
- Media browser, deck controls, layer panel and transport controls.

## First test workflow

1. Launch the application.
2. Drag a local video folder into the Media Library, or use Add Media Folder.
3. Wait for indexing and thumbnails.
4. Double-click a clip to assign it to the selected deck.
5. Repeat for the other decks.
6. Adjust visibility, opacity, blend mode and transforms in the Layers dock.
7. Use Random Set and Randomize Layout.
8. Save a project as .eliav, close the application and reopen it.

## Playback limitations

- Audio playback is not included; video is treated as a visual source.
- Reverse playback and variable-speed playback are not included.
- Playback performance depends on CPU decoding capability and source codec.
- The application currently targets an OpenGL 3.3 Core context.

# M2 — Automated Collage, Effects and Projector Output

## Purpose

M2 turns the four-deck video mixer into an unattended VJ instrument. The operator imports a footage folder, chooses a pacing profile and SESSL, starts automation, and can send the master composition to a separate monitor or projector.

This milestone deliberately focuses on video, effects and automation. Audio and Sonic Pi integration remain separate work.

## Automated video direction

Each unlocked deck receives its own random in/out segment:

- A segment start is chosen within the source clip's duration.
- Segment length is selected from the chosen short, mixed or long range.
- A deck randomly loops that segment or plays it once.
- A per-deck cut timer chooses when to load a new clip or another segment from the current clip.
- The clip-switch probability controls how often the director changes source files rather than selecting another section of the current file.

Locked decks are skipped. The automation session does not stop playback when its timer expires; it simply stops scheduling new changes.

## Semi-random collage

The director cycles among a family of arrangements:

- Four-panel grid.
- Full-frame base with picture-in-picture accents.
- Horizontal split.
- Vertical split.
- Asymmetric collage.
- Centered / stacked layers.

A small position jitter, scale variation, opacity and blend-mode choice prevent every cycle from looking identical. Locked layers are left alone.

## Effect and overlay pass

The master compositor runs one GPU post-processing pass after video layers are composited.

Available controls:

- Brightness, contrast, saturation and gamma.
- Vignette and film grain.
- Scanlines and RGB split / chromatic aberration.
- Horizontal signal glitch.
- Pixelation and posterization.
- Color inversion.

Built-in looks are parameter presets. They are intentionally editable rather than baked video effects.

## Session controls

The automation panel exposes:

- FPOOL: all indexed folders or one imported folder.
- SESSL: 30, 45, 60, 90 or 120 minutes, or until stopped.
- Cut rhythm: slow, balanced or fast.
- In/out length: short, mixed or long fragments.
- Loop probability: occasional, mixed or frequent.
- Automatic layout and look changes: independently enabled.

The director uses monotonic time for scheduling. UI repaint rate does not change the chosen cut intervals.

## Separate output window

The output window is a separate fullscreen Qt top-level window placed on the selected QScreen. Each window owns its own QOpenGLWidget, ModernGL context, GPU textures and renderer resources.

Decoders are not duplicated. The application collects each deck's latest CPU frame once into a shared snapshot cache. The preview and projector renderers each track their own frame revision and upload a new snapshot into their own GPU context.

This avoids two output windows racing to consume one decoder queue and avoids relying on cross-window OpenGL texture sharing.

Use View → PROJECTOR OUTPUT → Display N to open the output. Press Escape on the output display to close it.

## Project persistence

Project schema version 2 stores:

- Deck source paths and media IDs.
- Segment in/out points and loop state.
- Master effect parameters and selected look.
- Automation settings.

The project loader still accepts schema version 1 projects; their missing M2 settings use defaults.

## Validation

The former unit-test suite was removed at the user's request. Current CI checks Python compilation and Ruff only; random scheduling, media playback and projector behaviour require runtime validation on Windows.

A physical Windows multi-display test is still required to validate monitor placement, GPU driver behavior and four-stream playback on the target performance computer.

## M2 effect-chain completion

Layer FX support ordered, up-to-eight-stage chains. The stage order is top-to-bottom and is applied in the same compositor shader used by preview and projector. Available stages: monochrome, negative, threshold, posterize, scanlines and hue shift. Chains can be saved as individual JSON files; project preset collections can be imported into composition metadata, selected from the layer preset control and exported with the project.

Overlay layers expose persisted in/out metadata, playback speed, frame hold, scene-sync intent and track-matte selection. Animated image playback responds live to speed and hold changes. Alpha and luma mattes sample another composition source by source ID. The application continues to publish one CPU frame snapshot per source to independent preview/projector GPU contexts.

Auto Performance varies enabled per-layer FX independently of generator variation, and has a separate overlay-transform/blend toggle. A manual layer-FX or overlay-control edit starts a 30-second cooldown; locked layers are always excluded. The same scheduled mutation updates the shared composition model, so both output windows see the same state.

Overlay in/out are layer-local elapsed seconds from attachment and gate the shared CPU frame snapshot, so preview and projector hide/show the overlay together. Scene-sync remains a persisted intent for M3's scene/timeline clock; video-overlay source trimming is not yet implemented.

## Follow-up usability pass (November 2026)

- Overlay image/video layers now expose a dedicated **Remove Overlay Image / Video** action in the selected overlay controls; it routes through the application lifecycle so decoder/player resources are released.
- Ordered layer FX stages are individually checkable, reorderable, removable and amount-editable. Contrast, saturation and brightness are now available as ordered stages too; the legacy sliders are composited after the stage chain rather than being silently bypassed when a chain exists.
- Added additional looks: Bleach Bypass, Infrared, Cold Storage, Riso Print, Soft Ghost and Hard Signal.
- Geometry adds a texture-space **Warp** motion mode. Shader time is now session-relative to keep animation phase precision stable during long performances.
- Generator styling includes curated Japanese colour-family looks (Sakura, Beni, Matcha, Ai, Fuji, Kitsune, Yamabuki, Sumi, Shinbashi and Riso). The generator panel can import Photoshop `.aco` files, grouping imported RGB/grayscale swatches into four-colour looks; Auto Performance can vary these palette colours independently of generator-shape variation.
- Bundled visual textures are indexed by category, tags, media type and inferred purposes (overlay, texture, surface/distress, mask/matte, material, background, particles/atmosphere, geometry/environment). The Visual Asset Library dock indexes bundled textures and sketch/stroke assets, supports user-added folders, search and purpose filters (including PBR map types), and can add selected assets as composition overlays.

Current asset-library application path: selected indexed assets can be placed as overlay layers. Direct material-slot binding for geometry, particle sprite assignment and automatic post-processing texture routing remain future extensions; the index exposes those purposes for discovery.

- Geometry animation controls now use mode-specific amplitude ranges: rotate is in degrees, pulse is a bounded scale variation, drift is a small canvas-space offset, and warp is a texture-space displacement. Auto Performance varies the geometry animation mode with corresponding safe amplitude ranges.

- Master post-production looks now also include Sakura Fade, Noh Theatre, Indigo Night, Shin-hanga and Kintsugi alongside the existing film/CRT/print/signal presets.

# M2 — Generative Visuals, Typography and Overlays

## Purpose

M2 turns the video mixer into a mixed-media VJ instrument. Generators, still/animated media and ordinary video footage share one composition-layer model. All layers can be ordered, positioned, scaled, rotated, hidden, locked, blended, saved and rendered by preview and projector outputs.

## Generator layers

### Geometry

Transparent procedural patterns rasterized once when settings change:

- Rings, grids, radial constructions, crosshatch and nested polygons
- Spirals, offset-circle moiré and hexagonal grids

Controls include density, line width, primary/accent colours and the common layer transform/opacity/blend controls.

### Text Art

The Text Art layer has two layouts:

- **Single block:** editable multiline text, system typeface, weight, font size, tracking, line spacing, horizontal/vertical alignment, primary/accent colour, outline and shadow.
- **Typographic collage:** each line is treated as a word/phrase fragment. A seeded arrangement varies scale, font weight, rotation, placement and accent colour to form dense editorial/experimental typography compositions.

Text animation is applied in the GPU compositor after the static text texture has been cached. Available behaviours:

| Motion | Behaviour |
| --- | --- |
| Type-on | Horizontal reveal sweep |
| Word / column reveal | Reveal in successive horizontal cells |
| Line wave | Displace text sampling by a wave |
| Glyph jitter | Time-varying local sample jitter |
| Crawl | Vertical texture travel |
| Signal glitch | Sparse horizontal line displacement |
| None | No text-specific motion |

Changing text or typography raster settings updates the cached texture after a short UI debounce. Changing only the animation mode, speed or amount does not invalidate the raster cache. The explicit Apply button remains available.

### Bilingual random text pool

The editor includes reproducible-ready text pools in English, Japanese or bilingual mode. Themes:

- Memory / 記憶
- Body / 身体
- Signal / 信号
- Ritual / 儀式
- Identity / 自己
- Random mix

Generated text is inserted into the editable text field and stored in the project. Regeneration is manual or scheduled by Auto Performance; it never occurs per frame. The repository's local English wordlists and Japanese reading/kanji lists can enrich the curated phrase sets, with the curated pools retained as a fallback. The dictionary checkbox lets the user opt out. Language, theme, fragment count and dictionary preference are saved with generator settings. The collage arrangement uses a saved seed so a saved project retains the same composition until the user requests another random text set.

### Waveform

Procedural signal-like visuals that need no audio device:

- Parallel sine traces
- Lissajous curves
- Orbit patterns
- Radial traces
- Rose curves

Density, amplitude, frequency, line width and two-colour treatment are adjustable. Audio-band modulation remains part of M3.

### Particle Field

A first procedural GPU particle layer is implemented directly in the composition shader. It supports density, size, speed, spread, primary/accent colour and trails, with four motion modes:

- Drift
- Rise
- Fall
- Orbit

The particle field is generated per pixel in the shader. It does not upload a CPU-generated full-canvas bitmap each frame. This is the first M2 particle treatment, not yet a general-purpose physics simulation: emitters from arbitrary geometry/video, particle collisions, acceleration fields, lifetime curves and instanced particle sprites remain future extensions.

## Still and animated-media overlays

Use **+ IMG / VID OVL** in the Generators dock or **File → Add Image / Video Overlay**.

An overlay becomes a normal composition layer with a saved source path, media kind, transform, opacity, blend mode, visibility, lock and per-layer effects.

- Still PNG and other Qt-supported still-image formats retain their alpha channel.
- Qt-supported animated image formats are advanced by the image reader using each frame's delay. They loop continuously by default for performance use.
- Video overlays use their own VideoDeck decoder and frame queue.
- Preview and projector outputs receive the same CPU-side frame snapshots; each renderer uploads those revisions into its own GL context.

Animated-image format support depends on the Qt image-format plugins installed with the runtime. If a format cannot be decoded, the overlay import reports the error instead of adding a broken layer. Video support follows the app's PyAV/FFmpeg decoder support.

## Independent per-layer effects

The **LYS** dock now includes a selected-layer FX section. Each layer stores its own effect dictionary and can have these treatments independently of the master output grade:

- Monochrome
- Inversion
- Threshold / Xerox
- Posterization
- Hue shift
- Contrast, saturation and brightness
- Scanlines
- RGB separation
- FX enable/bypass and mix

Starting layer presets are Clean, Monochrome, Xerox, Negative, Duotone, Ghost and Tape. These per-layer treatments are applied during GPU composition before the layer blends into the accumulated frame. The master post-process remains available after all layers have been composed.

## Master effects

The master GPU post-process can be bypassed without changing saved parameters. An effect-mix slider blends the treated image with the untouched composition for A/B comparison.

Master controls include exposure, brightness, contrast, saturation, gamma, temperature, tint, hue rotation, vignette, film grain, scanlines, RGB separation, signal glitch, pixelation, posterization, inversion, halftone and solarization.

Available looks: Clean, 16mm Film, VHS / Tape, CRT, Bleach Bypass, Dream Haze, Digital Damage, Halftone Print, Photocopy, Infrared, Cold Steel and Solarized.

## Project and rendering architecture

- core.composition.Layer stores generator settings, per-layer effect settings and overlay source metadata.
- generators.catalog validates generator values and clamps visual/resource ranges.
- generators.rasterizer.GeneratorRasterizer creates transparent RGBA content and caches it by a content fingerprint.
- Text motion-only settings are excluded from the raster fingerprint.
- media.image_overlay.ImageOverlayPlayer decodes still/animated images to stride-safe RGBA frames.
- Video overlays use their own decoder and bounded frame queue.
- core.render_engine.RenderEngine uploads new source/generator revisions per GL context.
- rendering.compositor.Compositor applies transforms, per-layer FX and blends; it generates particle fields and text motion in the shader.
- The master effect pass runs after the full layer stack.

Layer settings and media references are stored in .eliav projects. Older projects load with neutral defaults for the added layer fields.

## Auto Performance integration\n\nAuto Performance can now vary generators, regenerate text pools and mix independent per-layer FX. Generator changes are scheduled separately from footage cuts, layout changes and master looks. Text generation draws from the curated English/Japanese pools plus optional local dictionary files; all results are saved as ordinary generator settings and therefore survive project save/load. Locked layers are excluded from automation.\n\n## Remaining M2 work

- General particle simulation with emitter shapes, lifetime/velocity curves and force fields.
- More compact and densely packed typographic layout solvers, text paths, variable fonts and vertical CJK composition.
- Rich text runs with multiple styles and arbitrary mixed language runs.
- [x] Overlay timing metadata, animated-image playback speed/frame hold and alpha/luma track mattes; scene-sync metadata is persisted for timeline integration.
- [x] Per-layer effect stage ordering, reorder controls, chain save/import and project preset import/export.
- User-defined generator presets and scene banks.
- Auto Performance can periodically vary geometry, waveform, particle and text generator settings, regenerate bilingual dictionary-backed text, and vary enabled per-layer FX presets. Each generator/FX variation has a separate interval; locked layers are never changed. The UI exposes generator/text and layer-FX variation toggles.

Audio reactivity remains M3; Sonic Pi control remains M4.

## M2 effect-chain and overlay close-out

Per-layer FX are stored as ordered stages (maximum eight), rendered top-to-bottom in the shared compositor. Current GPU stages are monochrome, negative, threshold, posterize, scanlines and hue shift. Stage order is project data, so preview and projector consume the same saved chain. The layer panel supports stage add/remove/reorder and saving a chain JSON file. Project preset collections can be imported into composition metadata and exported as JSON. Auto Performance skips a layer's FX for 30 seconds after a manual edit, in addition to respecting the layer lock.

Overlay layers persist source in/out values, speed, frame-hold count, scene-sync intent and a matte source/mode. Animated image overlays use speed and hold settings at decode time. Alpha and luma mattes sample a referenced source texture in the compositor. Video source trimming and scene-clock scheduling remain dependent on the performance timeline introduced in M3; the saved fields provide the compatibility contract.

# M3 — Audio-Reactive Engine and Performance Control Foundation

## Purpose

M3 adds a source-independent performance-control layer and optional audio-reactive analysis to the visual instrument. Audio is the first live analysis source. The same normalized control contract is ready for M4 Sonic Pi OSC without coupling the renderer to audio libraries, network protocols or Sonic Pi.

The pipeline is:

```text
Physical input / supported system loopback / test signal / fixture replay
                              │
                              ▼
                    Owned capture worker
                              │
                              ▼
                    Audio analysis frames
                     (bounded latest queue)
                              │
                              ▼
                 Application/UI-thread tick
                              │
             ┌────────────────┴────────────────┐
             ▼                                 ▼
      Normalized control events          Analysis features
      transport / scene / macros          RMS / bands / onset
             │                                 │
             └────────────────┬────────────────┘
                              ▼
                     Modulation matrix
                  explicit sources and targets
                              │
                              ▼
            Existing effects / layers / generators
                     and Auto Performance
                              │
                              ▼
                         GPU renderer
```

M3 does not introduce a second renderer or audio playback engine. Audio playback remains external (for example, Sonic Pi).

## Implemented

### 1. Internal transport and scene system

- Monotonic, drift-resistant internal test clock driven by the existing application timer; it does not sleep or block the UI.
- BPM range 20–300, configurable meter, one-based bar and zero-based beat position.
- Start, pause, resume, stop, tempo and meter controls.
- Beat, bar and phrase quantization for scene changes, with a bounded catch-up limit after a delayed UI tick.
- Named scene profiles with master-look, Japanese colour-palette and intensity defaults.
- Sixteen initial profile IDs matching the SONATA form: `in`, `exp`, `tm_a`, `trns`, `dev`, `fr`, `ssp`, `rtrns`, `rc`, `rc_w`, `peak`, `intd`, `s_s`, `rls`, `c`, `end`.
- Scene selection applies the configured master look and palette to generator layers.

### 2. Audio source and analysis

- SoundCard backend for physical input devices and supported system-output loopback devices.
- Dedicated worker owns the recorder from open through close; source replacement cancels and joins the previous worker before starting another.
- Clear stopped, starting, running, device-lost and error states, with visible source name/error text.
- Device refresh and periodic presence checks; disconnect stops the capture loop without stopping video playback. Select/refresh a source and restart capture after reconnection.
- Deterministic generated test signal and recorded NumPy fixture replay, both using the same analysis path as live sources.
- Bounded latest-feature queue; old analysis frames are discarded rather than allowing an unbounded backlog.
- RMS and peak envelope; low, mid and high FFT energy; transient/onset strength; optional tempo estimate and confidence.
- Configurable sensitivity, attack, release, onset threshold and beat-estimator confidence/range.
- Multi-channel downmixing, non-finite sample sanitization and bounded feature values.

The optional runtime dependency is `soundcard>=0.4.6`. Audio backend/device errors remain local to the Audio / Control dock; they do not stop the video mixer.

### 3. Modulation matrix and visual control

- Explicit normalized source registry: audio RMS, peak, low/mid/high bands, onset, beat confidence, estimated tempo, transport phase/intensity and named macros.
- Explicit target registry and per-target safe output range. No arbitrary Python attributes, paths or shader uniforms are exposed.
- One active route per target to keep ownership deterministic.
- Editable input and output ranges, linear/smoothstep/exponential curves, inversion, smoothing, attack/release, hold, intensity ceiling and independent enable/bypass.
- Current outputs are shown in the Audio / Control dock.
- Initial targets: master brightness/exposure/contrast/saturation/grain/glitch/vignette; selected-layer opacity/rotation; generator animation amount/density; Auto Performance loop probability and minimum cut interval.
- Layer lock prevents modulation from changing a locked selected layer. The modulation baseline is restored before locking.
- Manual changes to master effects, selected layer appearance and generator settings temporarily take precedence over a route. The prior baseline is restored when a route is bypassed or released.
- Scene profiles and modulation routes can be created/edited in the control dock.

## M5 groundwork — expanded live targets

The modulation target registry is being expanded beyond master effects and two generator parameters. The current M5 implementation branch adds safe, normalized targets for:

- Layer transforms: opacity, rotation, uniform scale and X/Y position.
- Generator motion: animation speed/amount, density and geometry rotation.
- Text: animation speed/amount, font size and letter spacing.
- Waveforms: amplitude and frequency.
- Particles: speed, size, spread and trail.
- Animated image overlays: playback speed and frame hold.
- Auto Performance: loop probability, clip-switch probability, cut interval, segment length, layout interval, look interval and generator/text variation interval.

The Audio / Control dock also has two route presets: **ADD AUD-REACTIVE ROUTES** and **ADD SONIC PI ROUTES**. They add starter mappings from audio bands/onsets or Sonic Pi energy/cutoff and transport state. Existing operator-authored routes are preserved; the presets do not silently replace a route that already owns a target.

Generator targets act on the currently selected, unlocked, compatible generator. Overlay playback targets apply only to an animated image overlay. Auto Performance targets change the corresponding live director settings; locks and manual overrides continue to take precedence. The modulation worker boundary remains unchanged: routes are evaluated on the application tick, not in audio or OSC workers.

### 4. Persistence and lifecycle

- Projects persist transport settings, audio analysis configuration, modulation routes and scene profiles.
- Projects do not persist live input-device handles, running capture threads, replay buffers or live analysis frames.
- Older projects without M3 performance settings load safe defaults.
- Project load/reset and application shutdown stop capture, clear transient audio data and reset modulation runtime state.

### 5. UI and application integration

- New dock: **AUD / CTRL**.
- Internal transport controls, scene profile editor, input/loopback selector, test signal, audio meters, tempo confidence and editable modulation route list.
- Compact transport/scene/source status in the main status bar.
- Audio capture, analysis and modulation work remain off the Qt paint path. The audio worker only publishes bounded analysis frames; the application tick consumes them and applies the visual state.

## Verification

The former unit-test suite was removed at the user's request. The current Windows quality workflow performs Python compilation and Ruff checks only. It does not run the previous fake-device, FFT, transport or Qt-panel tests.

Manual hardware sign-off is still required for:

- Physical microphone and system-loopback device discovery.
- Device loss, reconnect and switching while video is playing.
- Stable sustained capture and bounded-queue behaviour during a long session.
- A/V timing and preview/projector consistency on the target hardware.

## M3 exit status

<badge color="warning">Software implemented; hardware sign-off pending</badge>

The internal transport/test clock, audio source and analysis bus, normalized control state, scene profiles, modulation matrix, UI and persistence are implemented. Automated regression coverage is not currently present in this repository. Before declaring hardware validation complete, exercise physical input and loopback devices on the performance PC, unplug/reconnect the active device, and run a sustained session while video is playing.

The transport/scene/macro contract is ready for M4. M3 does not include an OSC receiver or changes to the SONATA patch.

## Explicitly out of scope

- Sonic Pi OSC receiver, outbound patch sender and protocol diagnostics (M4).
- MIDI learn/controller mapping (M5).
- Audio playback or DAW functionality.
- Arbitrary remote control of application internals or shader uniforms.

# M5 — Autonomous Performance Mode

## Operator workflow

The intended live workflow is deliberately short:

1. Prepare a composition with video decks and/or generator layers.
2. In AUD / CTRL, select a system-loopback device for local FFT analysis, or select Sonic Pi macros only.
3. In AUTO PERF, choose a style, musical synchronisation mode and session duration. The default is Generative + Phrase synchronised + Until stopped.
4. Press PERF MODE in the main toolbar.
5. Run SONATA Expanded in Sonic Pi.
6. Perform. Stop the Sonic Pi patch to stop AUTO PERF at its transport/stop event; press STOP PERF MODE to release resources and generated routing.

Performance Mode starts the OSC receiver automatically using the address and port in AUD / CTRL. The default is 127.0.0.1:57121. The receiver may already be running; in that case, the mode reuses it and does not claim ownership of it.

The first accepted Sonic Pi transport/start or clock/bar event changes the mode from ARMED to LIVE and starts the armed AUTO PERF session. Starting the mode before running the patch is therefore safe: it waits for Sonic Pi rather than inventing a local musical clock. If the patch is already running and its OSC stream is still live, AUTO PERF starts immediately when the mode is armed.

## Sonic Pi and audio are separate inputs

The OSC stream is a musical control source, not an audio capture device. It supplies transport, bar positions, scenes, normalized intensity, energy, cutoff and phrase cues.

For analysis of the actual audio output, select a Windows system-loopback device. The UI prefers an available loopback device automatically. This enables RMS/peak, low/mid/high bands, onset and tempo-confidence analysis. If the audio backend cannot start or the loopback device is disconnected, the mode remains active and Sonic Pi's energy/cutoff macros continue driving the show.

Sonic Pi energy/cutoff values are held only for a bounded freshness window. Audio features are also expired when capture stops producing frames. Stale inputs disappear from the modulation source map, causing envelopes and modifiers to release rather than holding the last value indefinitely.

## What Performance Mode arms

The application installs only missing defaults; it does not replace a custom route or a user-created layer modifier.

### Global matrix

- Energy drives master glitch and AUTO clip-switch/generator variation.
- Cutoff drives master saturation, AUTO cut timing and effect intervals.
- Scene intensity drives layout intervals.
- Local audio low/high/onset bands drive contrast, grain and segment decisions when loopback is active.

Every route uses the existing normalized Modulation Matrix with range, curve, smoothing, attack/release, hold, intensity ceiling and safe target ranges.

### Per-layer curves

Compatible unlocked layers receive generated AUTO modifiers:

- Video layers: beat/downbeat opacity pulses, bass scale and energy rotation.
- Geometry: energy deformation, cutoff-driven speed, beat rotation and phrase density.
- Text: energy-driven animation amount, cutoff-driven animation speed, phrase font scaling and onset tracking.
- Waveform: bass amplitude and cutoff frequency with beat envelopes.
- Particles: energy speed, onset size, beat trails and phrase spread.
- Animated overlays: energy playback rate and beat-driven frame hold.

The shared LayerPerformanceModifierEngine evaluates these at the application tick. It respects locks and manual override precedence and restores saved baselines when a source expires or an AUTO modifier is disabled. Generator defaults animate only shader uniforms (`animation_speed`, `animation_amount`, text animation uniforms), particle shader uniforms, and layer transforms such as rotation/scale. Geometry density/rotation, text font-size/letter-spacing and waveform shape parameters stay in the static CPU-raster cache; changing those on every tick would force a full 1600×900 QPainter rasterisation in every active output renderer. The installer automatically migrates the earlier generated AUTO curves off those CPU-rasterized properties.

Static generator rasterization is performed by a single shared background worker. The generator editor maintains an editing buffer and a committed settings snapshot; the text field has its own short debounce and commits only the text value, while other generator controls use the regular settings debounce. Each distinct raster request receives a monotonically increasing per-layer revision alongside its copied settings snapshot and fingerprint. Text and typography commits submit that snapshot immediately, so a newer revision invalidates older work before the next render frame. When a worker finishes, the service caches and emits the result only if its revision and fingerprint still match the newest request; renderers check the revision again when receiving the signal and immediately before uploading. The worker uses an ordered pending map keyed by layer; new edits replace that layer's queued snapshot in place. There is at most one active raster globally and one pending snapshot per layer, so obsolete keystrokes do not accumulate as queued work items. Completed pixels are delivered to the GUI thread as CPU memory; preview and projector renderers each upload that snapshot only while their own OpenGL context is current. The last successful texture remains visible while a replacement is being rasterized. OpenGL objects and context-bound uploads are never created on the worker thread.

### Static and animated typography

Text rendering keeps one shared raster texture and the existing compositor shader; it does not create a second text renderer.

| Operation | Processing path |
| --- | --- |
| Typing/editing characters | UI editing buffer only; committed text is submitted after the text debounce |
| Changing text, font family/weight/size, tracking, line spacing, alignment, layout, stroke or static colours | Versioned background CPU raster request |
| Type-on, word/column reveal, line wave, glyph jitter, text scrolling and signal glitch | Existing GPU compositor shader |
| Motion mode, speed, amount and reveal columns | Layer settings consumed as per-frame shader uniforms; no raster request |

The raster fingerprint is built from the static settings projection and includes the requested raster dimensions. GPU-uniform keys are explicitly excluded in one shared definition, so changing motion cannot invalidate the text texture. The editor has a dedicated motion-control update path and timer; it changes only the four shader settings and never calls the raster service. Static typography retains the normal raster debounce/revision path. AUTO and other live generator mutation callbacks also compare the resolution-aware static fingerprint before submitting work, avoiding redundant requests when only shader uniforms changed.

#### Text raster performance controls

The TXT RASTER PERF section gives the operator independent controls over editing and raster work:

- **Live Preview:** when enabled, committed text snapshots are rasterized automatically. When disabled, edits may still be committed to the composition, but the last uploaded texture is held until preview is re-enabled or Apply Immediately is invoked.
- **Commit on pause:** commits the editor buffer after the short typing debounce. Turning it off leaves the buffer pending until an explicit apply or layer switch.
- **Preview quality:** Draft (25%), Balanced (50%), High (75%) or Maximum (100%) scales CPU raster dimensions while retaining the 16:9 texture aspect ratio. The selected dimensions are part of the raster fingerprint so preview and projector renderers agree on the same snapshot.
- **Full-resolution final rendering:** Apply Immediately can bypass preview scaling and submit a 1600×900 raster. This is an explicit operator action; motion uniforms stay GPU-side.
- **Maximum raster rate:** text jobs start at no more than the configured 1–20 Hz rate (default 4 Hz). The single worker still coalesces to one pending snapshot per layer, and non-text generator jobs are not held behind the text-rate limiter.
- **Freeze current text texture:** keeps the currently uploaded image visible while newer settings are retained as the newest deferred snapshot. Unfreezing schedules only that latest snapshot.
- **Last-valid recovery:** when enabled (default), a failed replacement leaves the previous successful texture in each renderer. Disabling it explicitly clears the affected texture on the next raster failure.

The status readout follows the service lifecycle: **EDITING → RASTERIZING → READY**. A failed render is shown as FAILED and indicates that the last valid texture is retained when recovery is enabled. A frozen layer reports FROZEN. These controls affect the text raster path only; shader motion, video decoding, layer effects and audio-reactive updates continue on their existing real-time paths.

The four-deck/multi-layer acceptance test remains a target-machine rehearsal: keep all four video decks, several text and other generator layers, per-layer effects, audio reactivity and projector output active while continuously typing Japanese/English multiline text. Verify the editor remains responsive, obsolete rasters are discarded, no more than the configured number of text jobs start per second, and all renderers converge to the newest revision. Record GUI input responsiveness, raster duration, upload time, FPS and dropped-frame metrics. This repository-side implementation does not claim that hardware acceptance test has been performed.

### Modulator Bank

Performance Mode ensures the built-in Sonic Pi energy/cutoff followers, beat/onset envelopes and phrase LFO exist. These become reusable named sources in the Modulator Bank and can feed multiple compatible layer targets. Existing modulator definitions with those AUTO names are re-enabled rather than duplicated.

### AUTO PERF

The mode arms AUTO PERF and waits for the Sonic Pi transport. Phrase/scene cues then drive random, structured or generative visual decisions. Generative mode increases variation with energy and intensity; scene IDs classify sections such as intro, development, peak, breakdown and outro. Cut probability, segment length, layout/effect/generator intervals and loop/switch probabilities are also modulation targets.

In Phrase mode the scheduled wall-clock randomizer is gated off. Changes are evaluated at phrase/scene cues; bar events can add small generative cuts in Bar/Hybrid modes. Time and Hybrid settings retain interval-based behaviour. This avoids two independent random schedulers fighting the musical form.

If no playable video clips are loaded, AUTO PERF can still operate on generators, text, layout, overlays and effects. Video cuts are simply skipped until footage is available.

## State and ownership

The mode tracks whether it started the OSC receiver and audio capture. Stop only closes services the mode owns. A receiver or audio stream that was already running before the mode started remains available afterward. When SONATA sends transport/stop, the current AUTO PERF pass stops and the mode re-arms; running the patch again starts a fresh pass without toggling Performance Mode.

Generated defaults use stable AUTO identifiers. Stop disables only those generated routes, Modulator Bank definitions and per-layer modifiers, evaluates the release path, and restores their baselines. User-authored routes and modifiers remain configured and enabled.

Saving a project or performance set while Performance Mode is live writes the generated defaults as disabled. A project therefore opens in an idle state; pressing Performance Mode re-enables the defaults. The saved plan retains receiver address/port, local audio selection, automation style/sync and session duration, but not active hardware handles, worker threads or a live session state.

## Diagnostics and recovery

The AUD / CTRL mode status displays OFF, ARMED, LIVE or DEGRADED. Its tooltip and the application diagnostics expose OSC status/counters, last-message age, audio state/queue/drop counters, bounded control queue state, active route/modulator counts, AUTO section/energy/cutoff and video/decode/render metrics. The main status bar follows the active projector renderer when a projector window is open; when the local preview dock is hidden, it explicitly reports LOCAL PREVIEW IDLE rather than implying that the projector's OpenGL context failed to initialise.

If Sonic Pi is not started, the mode remains ARMED. If its OSC stream becomes stale, the mode returns to a waiting state and stale musical macros expire. If local audio capture fails, the mode continues in Sonic Pi-macro mode. A receiver startup failure is shown as DEGRADED and can be corrected by stopping/rearming the mode.

## Validation boundary

The software lifecycle and source/target wiring are implemented. Target-machine validation is still required for the actual 384-bar SONATA rehearsal, loopback device selection/reconnect, long-duration performance and projector behaviour. This milestone does not claim master-output video recording or audio/video muxing; those remain separate delivery items.

# M5 Completion & Live Validation Handoff

**Repository:** `ilyaminineli/eli_lab-av-translator`  
**Baseline reviewed:** `main` at `358dc597c76e9ee11344f5c13c8361667a07fafe` (12 November 2026)  
**M5 feature PR:** [#19 — Separate text editing from asynchronous generator rasterization](https://github.com/ilyaminineli/eli_lab-av-translator/pull/19), merged as `ecc6f86bb896e9c8ff1cd23d083683fdfdef8e14`  
**Quality:** [Workflow #116 passed](https://github.com/ilyaminineli/eli_lab-av-translator/actions/runs/43132442896) on the reviewed `main` head (compile + Ruff only).  
**Connection topology:** Sonic Pi and AVTranslator on the same computer.

## Status

**M5 implementation scope is merged to `main`. Code-level CI is green. M5 live-performance acceptance remains open pending target-machine rehearsal. M6 planning/implementation may proceed in parallel.**

The final M5 code review covered the application-owned generator raster service, CPU rasterizer, preview/projector render integration, generator editor controls, Performance Mode/AUTO PERF integration, project lifecycle and the PyInstaller local build route. PR #19 is merged; `main` subsequently received the formatting-only commit `358dc597`.

The Quality workflow on that current commit passed Python compilation and Ruff. The repository does not contain the former pytest/unit-test suite. A green Quality run does not execute the GUI, create a real OpenGL context, run Sonic Pi, exercise a Windows audio device or measure projector performance.

## M5 implementation inventory

- One application-owned background generator raster worker shared by preview/projector renderers.
- One active raster job globally and at most one pending snapshot per layer; newer pending work replaces older queued work.
- Monotonic per-layer revisions and static-settings fingerprints; obsolete worker results are discarded before caching/emission and checked again by renderers before texture upload.
- CPU-only raster workers; preview and projector upload their own accepted pixel snapshots while their individual OpenGL contexts are current.
- Separate static typography rasterization and GPU-shader text animation paths.
- Text edit buffer separated from committed layer settings, debounced commit and explicit Apply Immediately.
- Live Preview, commit-on-pause, Draft/Balanced/High/Maximum preview quality, optional 1600×900 final raster, maximum 1–20 Hz text raster rate, Freeze current texture, last-valid-texture fallback and EDITING/RASTERIZING/READY/FAILED/FROZEN status.
- Cached raster replay for a renderer that missed an earlier completion, including preview re-enable/unfreeze.
- Raster invalidation on layer deletion, project reset/load and application shutdown.
- Performance Mode, Modulator Bank, generated per-layer performance modifiers and phrase-aware AUTO PERF remain part of the merged M5 foundation.

## Same-computer OSC configuration

Use loopback. No LAN address is required.

| Setting | Value |
| --- | --- |
| AVTranslator OSC bind address | `127.0.0.1` |
| AVTranslator OSC UDP port | `57121` |
| SONATA `$sp_av_enabled` | `true` |
| SONATA `$sp_av_host` | `"127.0.0.1"` |
| SONATA `$sp_av_port` | `57121` |

Sonic Pi's own incoming OSC port (commonly `4560`) is not the destination for these messages. SONATA sends outbound OSC to AVTranslator on port `57121`.

## Live start sequence

1. Launch AVTranslator.
2. Open **AUD / CTRL** and confirm the OSC receiver is configured for `127.0.0.1:57121`.
3. Choose **System loopback** if the show needs FFT/audio-band/onset analysis of Sonic Pi's actual output. Choose the macros-only option if SONATA's normalized energy/cutoff controls are sufficient.
4. Press **PERF MODE**. Confirm the mode is **ARMED** and the receiver is listening.
5. In Sonic Pi, confirm the three SONATA settings above and run `SONATA_expanded.rb`.
6. Confirm the first accepted transport/start or clock/bar packet changes the mode to **LIVE** and starts AUTO PERF.

## Full SONATA rehearsal

SONATA is 92 BPM, 4/4 and 384 bars: approximately **16 minutes 42 seconds**.

During the uninterrupted run, verify:

- [ ] Receiver remains **LIVE**; packet age does not repeatedly cross the stale threshold.
- [ ] BPM reads 92 and bar position advances from 1 through 384.
- [ ] All 16 scene IDs arrive in the documented order, including the final `end` marker.
- [ ] Energy and normalized cutoff values change and feed the modulation system.
- [ ] Four-bar phrase cues trigger phrase-aware AUTO PERF.
- [ ] Modulator Bank followers/envelopes/LFOs and compatible per-layer modifiers respond.
- [ ] The visual output remains responsive; no sustained render stalls or unexpected automation freeze.
- [ ] SONATA reaches its final stop event cleanly.

At 92 BPM, a 4/4 bar is about 2.61 seconds. The continuous musical clock/macros—not the diagnostic sender—should maintain LIVE status during the performance.

## Recovery and ownership checks

After the uninterrupted run:

- [ ] Stop and restart SONATA. Confirm the new session ID is accepted and LIVE resumes.
- [ ] Confirm delayed packets from the superseded session are rejected.
- [ ] Press STOP PERF MODE while SONATA is playing. Confirm Sonic Pi audio continues.
- [ ] Re-arm Performance Mode, restart SONATA and confirm a fresh session becomes LIVE.
- [ ] Confirm user-authored routes/modifiers and services that were already running are preserved.

## Generator raster / four-deck acceptance

On the target Windows machine, keep all of the following active together:

- [ ] Four video decks playing representative H.264 footage.
- [ ] Multiple text and non-text generator layers.
- [ ] Per-layer effects and master effects.
- [ ] Audio reactivity and/or live SONATA macros.
- [ ] Projector output open on the external display.
- [ ] Continuous rapid typing/pasting of long Japanese and English multiline text.

Record input responsiveness, text raster duration/start rate, preview and projector upload timing, FPS and dropped frames. Verify the latest committed text revision eventually appears on every output and that old revisions never replace it. Exercise Live Preview off/on, Freeze/unfreeze, Apply Immediately at full resolution, a forced raster failure/fallback, layer deletion, project reset/load and output-window close/reopen while raster work is active.

**This stress acceptance has not yet been performed or measured in the repository review.**

## Diagnostic sender is not the rehearsal

`python scripts/osc_test_sender.py --host 127.0.0.1 --port 57121` is a finite protocol/receiver diagnostic. It sends a short sequence and exits. A later STALE state is expected after it stops; that is not a failure of the live SONATA sender.

## Remaining validation and deferred work

| Gate | State on 12 November 2026 |
| --- | --- |
| M4 versioned OSC receiver, validation, session/replay protection and diagnostics | Implemented |
| M5 Performance Mode orchestration and AUTO PERF integration | Implemented; live rehearsal pending |
| Modulator Bank and generated per-layer performance modifiers | Implemented; live response rehearsal pending |
| Async generator raster service and text raster controls | Merged; static Quality check passed |
| Full 384-bar SONATA rehearsal | **Not yet validated** |
| Stop/restart and stale-session recovery rehearsal | **Not yet validated** |
| Windows physical input/system-loopback reconnect and sustained capture | **Pending target-machine validation** |
| Four-deck continuous-text stress with effects/audio/projector active | **Pending target-machine validation** |
| Projector hot-plug, frame-pacing and long-duration rehearsal | **Pending target-machine validation** |
| Local PyInstaller executable build and packaged self-check on the build computer | **Not certified by the Quality workflow; run locally** |
| Windows Onefile Build GitHub Actions fallback | Manual-dispatch only |
| Master-output recording and audio/video muxing | **Not implemented; deferred separate delivery item** |

## M5 exit decision and M6 handoff

M5 **implementation** is complete and merged. M5 **live-performance acceptance** is not yet signed off; the checklist above remains an open validation record. The recording/audio-muxing feature is not implemented and is explicitly treated as a separate deferred deliverable, rather than being presented as complete or used to block M6 development.

M6 can begin from the merged M5 baseline while the target-machine validation is completed. Carry the outstanding M5 checks into the performance release checklist and record actual results before claiming hardware readiness.

See [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md) for the next milestone's initial live-mixer scope.

# M5 — Unified Performance Mapping Matrix

The same normalized source/mapping semantics are used by every performance target family. Separate source-specific code must not be added in the renderer or individual generator widgets.

## Inputs

Transport beat/downbeat/phrase pulses, beat/bar phase and scene intensity; audio RMS/peak/low/mid/high/onset/beat confidence; Sonic Pi energy/cutoff; named Modulator Bank sources.

## Target namespaces

| Namespace | Parameters |
| --- | --- |
| `layer.*` | opacity, rotation, scale, position_x, position_y |
| `generator.*` | animation_speed, animation_amount, density, rotation, text_animation_speed, text_animation_amount, font_size, letter_spacing, waveform_amplitude, waveform_frequency, particle_speed, particle_size, particle_spread, particle_trail |
| `overlay.*` | playback_speed, frame_hold |
| `automation.*` | loop/switch probability, cut/segment bounds, layout/effect/generator interval |
| `master.*` | effect parameters exposed by the global Modulation Matrix |
| `macro.*` | named normalized macro controls |

Local layer targets are saved with composition layers. Global effect and automation targets remain in the Modulation Matrix. MIDI addresses stable target IDs. A target is only implemented when it has a registered range, getter/setter, compatibility filter, UI surface and persistence; verification must be documented separately from static CI checks.

## Precedence

1. A locked layer suspends local modulation and automation writes.
2. A manual edit temporarily owns that target.
3. A valid per-layer modifier claims its exact layer target before a selected-layer global route.
4. Global routes own master and automation targets.
5. Releasing a source, disabling/removing a mapping, stopping a set or changing project restores the pre-modulation baseline.

# M5 — Modulator Bank

## Purpose

The Modulator Bank separates a time-varying control source from the visual parameter it drives. A single modulator can be assigned to multiple targets and layers; each assignment keeps its own depth, polarity and response curve.

The bank is available as a dedicated **MOD BANK** dock, next to **AUD / CTRL**. The View menu also includes the dock visibility action.

## Modulator types

### Control follower · external source

A control follower turns an existing continuous control signal into a reusable named source. It can follow SONATA's `macro.energy` or `macro.cutoff`, scene intensity, transport phase/pulses, or the audio RMS, peak, frequency bands and onset.

Each follower provides an input range, linear/smoothstep/exponential response, inversion, and independent attack/release smoothing. Its normalized 0–1 output can be assigned to multiple targets/layers exactly like an LFO or sequence. Followers do not require the transport to run, so audio and macro control remain usable independently. The live monitor displays both the raw input value (or **NO SIGNAL**) and the smoothed follower output.

SONATA sends its macros once per bar. The application keeps a received macro available for a bounded freshness window (at least five seconds, or two current bars if longer). When that source becomes stale or disappears, the follower stops publishing an output and its assignments release to their baselines. This avoids a disconnected Sonic Pi session leaving a waveform parameter frozen at its last value.

### Envelope · ADSR

An envelope is triggered by a selected event and follows attack, decay, sustain, gate and release stages.

Available trigger sources include every beat, bar downbeat, phrase start, audio onset, audio peak, Sonic Pi energy and Sonic Pi cutoff. The normalized trigger threshold is editable. Retrigger behaviour can restart the envelope or remain legato while the current envelope is active.

When transport-synced, stage times are measured in beats. In free-run mode, they are measured in seconds.

### LFO · cyclic waveform

The LFO provides sine, triangle, rising saw, falling saw, square, pulse and deterministic sample-and-hold waveforms.

Transport sync uses a period measured in beats. Free-run uses cycles per second (Hz). Phase can continue across the transport, or reset at each bar or phrase. Pulse width and initial phase are editable.

LFO output is normalized to 0–1. Its midpoint is 0.5, so **BIPOLAR** assignment makes the midpoint neutral and the two halves move in opposite directions.

### Steps · control sequencer

The step sequencer accepts 1–64 values normalized to 0–1. It supports hold, linear or smooth interpolation; forward, reverse, ping-pong or seeded-random direction; and adjustable step division and swing.

Transport sync measures step division in beats. Free-run measures step rate in steps per second. A seeded random sequence is deterministic and repeats the same pattern for repeatable performances.

### Rhythm · gated pattern

The rhythm grid uses the same 1–64 step pattern model but treats values as accents. A pulse-width/gate setting controls how much of each step remains active. The off-step level is centered at 0.5, so a bipolar assignment returns to the parameter baseline between hits.

The rhythm editor also includes a Euclidean generator: choose the number of pulses, grid length and rotation, then generate an evenly distributed pattern. The generated values are placed into the editable step field, so individual hits can be accented, muted or reshaped before applying.

This supports patterns such as four-on-the-floor, clave-like accents, triplets, syncopated gates, Euclidean distributions and fully custom sequences.

## Using the bank

1. Open **MOD BANK** from the right-side dock tabs or **View** menu.
2. Create a Control Follower, LFO, Envelope, Steps or Rhythm source, or load a preset.
3. Edit the name, timebase and type-specific settings, then click **APPLY MOD CHANGES**.
4. Select a layer in the LYS dock. The bank's **ASSIGN TO SELECTED LY** section offers only compatible targets for that layer.
5. Set assignment depth and response, then click **ASSIGN MOD TO LY**.
6. Assign the same bank source to further targets or layers. Its output is evaluated once and reused by every assignment.

The Layer dock's existing per-layer modifier list displays bank sources by name alongside direct audio, transport and Sonic Pi sources. The global **AUD / CTRL → MODULATION MATRIX** source list also exposes each active bank modulator, so the same source can drive a global target such as master grain/brightness, or an **AUTO PERF** parameter such as generator interval, as well as layer-local targets. One LFO or follower can therefore feed a waveform frequency locally and a master effect or automation interval globally.

Removing a bank modulator removes its per-layer assignments and any global matrix routes that use it. Project loading drops global routes whose referenced bank source is missing. Bypassing a modulator releases its targets to their saved baselines.

## Presets

The bank includes built-in presets for Sonic Pi energy and cutoff followers, slow phrase swells, quarter-note triangle motion, dotted pulses, beat plucks, downbeat envelopes, audio-onset envelopes, four-on-the-floor, clave-inspired accents, triplet shimmer, a bipolar staircase and seeded random drift.

- **LOAD PSET** creates a new active modulator from the selected preset; it does not overwrite the current modulator.
- **SAVE AS PSET** stores the selected modulator as a user preset.
- **DUPLICATE** copies an active modulator with a new ID.
- **EXPT USER PSETS** writes custom presets to a portable JSON file.
- **IMPORT PSETS** adds presets from an exported JSON file. Built-in presets cannot be deleted; user presets can.

Active modulators and user presets are saved in the current AVTranslator project. Imported/exported preset files can be reused in other projects.

## Assignment response

Each layer assignment retains its own depth and polarity. **AUTO** uses positive response for envelopes and bipolar response for LFOs, step sequences and rhythm patterns. Explicit positive and bipolar choices remain available. Existing smoothstep, linear and exponential response curves are supported.

Assignments continue to use the existing per-layer lock/manual-override and global-route ownership rules. The bank engine only generates normalized control values; the application tick applies those values to layers and generator settings.

For a waveform generator, the selected-layer assignment targets include **Waveform amplitude** and **Waveform frequency**. A typical SONATA mapping is: load **Follower · Sonic Pi energy**, assign it to waveform amplitude, then load **Follower · Sonic Pi cutoff** and assign it to waveform frequency. The same two reusable followers can also drive geometry, text, particles and other compatible visual targets on separate layers.

## Timing and persistence

Transport-synced modulators use the application's absolute beat position derived from the internal transport or Sonic Pi bar clock. Bar and phrase reset modes use the current meter and configured phrase length. Free-running modulators use a monotonic clock, not wall-clock time.

Project files store active modulator definitions, user presets and layer assignments. Runtime phases, trigger timestamps and live output values are not persisted. Opening a project starts fresh runtime phases while retaining the saved settings and assignments.

## Preset file format

The portable JSON format uses the top-level fields:

- `format`: `eli-lab-modulator-presets`
- `version`: currently `1`
- `presets`: an array of named preset definitions

Each preset definition is validated and normalized when imported. Invalid preset definitions are skipped or reported as an import error; built-in preset IDs are protected from replacement.

# M5 — Performance Environment

## Scope and status

M5 connects the M3 transport/audio layer, M4 Sonic Pi bridge, per-layer modifier stacks, Modulator Bank and AUTO PERF into a one-button autonomous show. The M5 software implementation is merged to `main`. Live SONATA, audio-device and target-projector acceptance remain manual validation tasks; master-output recording and audio/video muxing are not implemented and are tracked as a separate deferred deliverable.

Press PERF MODE, then run SONATA in Sonic Pi. The first transport/start or clock/bar event starts the armed generative session; phrase and scene cues drive visual changes. The normalized mapping contract remains shared across video layers, geometry, text, waveform, particles, animated overlays and AUTO PERF.

## Unified mapping coverage

| Domain | Supported target families |
| --- | --- |
| Composition geometry | opacity, position X/Y, scale, rotation |
| Procedural geometry | motion speed/amount, density, rotation |
| Text Art | animation speed/amount, font size, letter spacing |
| Waveform | amplitude and frequency |
| Particles | speed, size, spread, trails |
| Animated overlays | playback speed and frame hold |
| AUTO PERF | cut/segment timing, layout/effect/generator intervals, loop/switch probability |
| Master output | global modulation matrix effect targets |

Audio bands, onset/beat confidence, normalized transport phases/pulses, scene intensity, Sonic Pi energy/cutoff and Modulator Bank sources are shareable inputs. A target is offered only when its owner can apply it. Per-layer modifiers retain their current baseline, lock, manual override and ownership rules.

## Autonomous Performance Mode

See [M5 Autonomous Performance](M5_AUTONOMOUS_PERFORMANCE.md) for the operator sequence. The mode starts or reuses OSC, optionally starts loopback capture, enables generated default routes/modulators/layer curves, and waits for Sonic Pi. Sonic Pi energy/cutoff and scene/phrase events can drive the visual performance even when no audio device is selected. A system-loopback device adds real audio-band/onset analysis.

The default global routes cover master look, clip switching, cut timing, segment length and automation intervals. Per-layer AUTO curves cover video, geometry, text, waveform, particles and animated overlays. Defaults use stable IDs and are non-destructive: custom routes are kept, generated mappings are disabled when the mode stops, and saving an active show stores those generated mappings disabled.

AUTO PERF supports random, structured and generative styles with time, bar, phrase and hybrid sync. Phrase mode uses musical cues instead of a parallel wall-clock randomizer. If the FPOOL is empty, generators, text, effects and layout automation can still run.

## MIDI controls and performance sets

The optional MIDI adapter uses `mido`; native `python-rtmidi` is an optional backend, not a startup dependency. Device discovery is explicit. Port callbacks enqueue compact normalized events into a bounded queue; the application tick drains them and applies mappings outside the callback. The AUD / CTRL panel exposes discovery, connect/disconnect, Learn Next Controller, a target selector, per-mapping range/curve/pickup editing, and mapping update/removal.

Mappings support CC, note and pitch wheel messages, device/channel/number filters, target IDs, min/max scaling, linear/smoothstep/exponential curves and pickup. Pickup holds until the incoming physical control crosses or approaches the current virtual value. Mapping definitions persist, but physical positions and pickup latch state do not. Device loss is local and does not stop the performance.

Performance scenes are named snapshots with quantized recall and smoothstep morphing for compatible numeric targets. A versioned `.eliset` performance set can store composition/deck state, master effects, AUTO PERF settings, transport/audio settings, global modulation routes, Modulator Bank, MIDI mappings and scene snapshots. It is separate from `.eliav`, allowing one composition to be reused across live sets.

## Asynchronous generator rendering and text performance

Static generator rasterization uses one application-owned background worker shared by preview and projector. Each request contains a copied settings snapshot, raster dimensions, a static fingerprint and a monotonically increasing per-layer revision. The ordered pending queue keeps at most one waiting snapshot per layer; a new edit replaces the previous pending snapshot. Worker output contains CPU pixels only. Each output renderer accepts only the latest revision and uploads while its own OpenGL context is current.

Static text content and typography are CPU-rasterized. Text motion is evaluated by the existing compositor shader from per-frame uniforms; changing animation mode/speed/amount does not invalidate the static text texture. The editor offers Live Preview, commit-on-pause, Apply Immediately, Draft/Balanced/High/Maximum preview quality, optional full-resolution 1600×900 Apply, a 1–20 Hz text raster update cap, texture freeze, last-valid fallback and EDITING/RASTERIZING/READY/FAILED/FROZEN status.

This is an asynchronous CPU raster pipeline, not a promise of unlimited generator complexity or guaranteed frame rate. Performance with four simultaneous video decks, several generator layers, effects, audio reactivity and projector output must be measured on the target hardware.

## Recording and output validation

Preview and projector are independent OpenGL outputs sharing CPU-side source snapshots; each renderer uploads its own textures. Projector output and A/V timing need target-machine validation.

Master-output recording and audio muxing are not implemented. If added later, recording should tap the fully composited master image after layer composition and effects, use bounded immutable frame handoff and a dedicated encoder worker, and keep encoding off Qt paint/UI callbacks.

## M6 relationship

M5 provides the performance-control, generator, rendering and diagnostics foundation. M6 — Advanced VJ Environment — will add the operator-facing live mixer and media-bin triggering model. A compact show surface, coordinated multi-clip triggering, mixing and transitions are tracked in [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md); they are not claimed as existing M5 features.

## Verification

The current Quality workflow performs Python compilation and Ruff checks only; the former pytest/unit-test suite is not present. It does not execute GUI/OpenGL, SONATA, audio-device or projector tests.

Manual target-machine checks remain required for:

- Full 384-bar SONATA timing and session restart.
- MIDI device/fader behaviour if hardware MIDI is used.
- Physical audio input/system-loopback reconnect and sustained capture.
- Four-deck continuous text editing with generators/effects/audio active.
- Preview/projector synchronization, hot-plug and long-duration stability.

# M5 — Per-Layer Performance Modifiers

## Purpose

The global Modulation Matrix is useful for broad mappings, but it is not enough when a composition contains several generators that should respond differently. A per-layer modifier stack gives every layer its own explicit source-to-parameter objects.

Modifiers are stored in the owning Layer record and travel with the composition. They are evaluated on the application tick, after normalized audio, transport and Sonic Pi control sources have been collected. Audio and OSC workers do not modify layers, widgets or GPU resources.

## Where to find it

1. Select a layer in the LYS dock.
2. Open PERF MODIFIERS · PER LY beneath SELECTED LY TRANSFORM.
3. Choose a source, target, response curve, polarity and depth.
4. Click ADD MODIFIER, or use one of the quick rhythmic buttons:
   - BT — add a short pulse on every beat.
   - DOWNBT — add a pulse on the first beat of each bar.
   - PHRASE — add a pulse at the start of each four-bar phrase.
5. Start the internal transport or SONATA in Sonic Pi. The rhythm readout and modifier meters show the live source values.

The quick buttons select a useful default target for the selected layer:

| Layer type | Beat / downbeat / phrase target |
| --- | --- |
| Geometry | Generator animation amount |
| Text Art | Letter spacing (or text animation amount when a text motion mode is active) |
| Waveform | Waveform amplitude |
| Particles | Particle size |
| Animated overlay | Overlay playback speed |
| Video layer | Layer scale |

The custom source/target controls let the user choose other compatible targets.

## Sources

| Source | Behaviour |
| --- | --- |
| transport.beat_pulse | Short decaying pulse on every beat |
| transport.downbeat_pulse | Same pulse, only on beat 1 of a bar |
| transport.phrase_pulse | Same pulse on the first bar of each four-bar phrase |
| transport.bar_phase | Normalized position through the current bar |
| transport.phase | Normalized position through the current beat |
| transport.intensity | Current scene intensity |
| audio.rms, audio.peak | Overall input energy |
| audio.low, audio.mid, audio.high | Frequency-band energy |
| audio.onset, audio.beat_confidence | Transient / beat-analysis signals |
| macro.energy, macro.cutoff | Sonic Pi values received through /eli_lab/v1 |

The beat pulse occupies the first 22% of a beat and then decays to zero. The bar and beat phases are derived from the internal transport or from the time elapsed since the latest accepted Sonic Pi bar event. When transport is stopped or an external clock becomes stale, the rhythmic pulse sources return to zero.

## Targets

A layer modifier can affect layer opacity, rotation, scale and X/Y position; generator animation speed/amount and type-specific density, rotation, text, waveform or particle values; Particle System 2.0 emission rate, particle radius, lifetime, turbulence, force and source reformation; numeric per-layer FX controls; or animated-image overlay playback speed and frame hold. Advanced master transforms and temporal feedback use the global Modulation Matrix target registry.

Generator targets are filtered by selected layer type in the UI. A Text Art layer always offers font size and letter spacing; text-animation speed and amount appear only when a text motion mode is active. This means the quick PHRASE action has an immediate visible effect even when text animation is set to none. A Waveform layer offers amplitude and frequency.

## Response controls

- Depth sets the fraction of the target's registered range contributed by the source.
- Positive moves upward from the parameter's saved baseline as the source rises.
- Bipolar moves around the baseline in both directions.
- Linear, Smoothstep and Exponential shape the normalized source.
- Attack and release smoothing prevent abrupt jumps.

Multiple modifiers may target one parameter; their offsets are summed and clamped to the target's safe range.

## Live feedback and precedence

Each modifier row shows its source-to-target mapping, depth and a live meter. The Layer dock's transform sliders and opacity row, and the Generators panel's active parameter controls, reflect the live values while a modifier is running.

Manual edits temporarily yield the affected layer modifiers for three seconds so direct operation remains possible. Layer locks suspend modifiers and restore their saved baseline. Removing or disabling the last modifier for a target restores the baseline. A configured per-layer modifier takes priority over a global Modulation Matrix route aimed at the same selected-layer parameter.

## Project persistence

Modifier definitions are saved with each layer. Runtime smoothing, live meter values and temporary manual-override timers are not persisted. While saving, AVTranslator writes the pre-modulation parameter values into the project snapshot; the live composition continues running unchanged. Reopening a project starts with its saved baseline and its modifier definitions, ready for a new transport/audio/Sonic Pi session.

# M6 — Advanced Performance Controls

**Status:** Performance Macro System implementation is merged to `main` in [PR #30](https://github.com/ilyaminineli/eli_lab-av-translator/pull/30). The normal Windows Quality workflow checks Python compilation and Ruff; keyboard, MIDI, OSC, audio-device and live GPU behaviour still require target-machine validation. The [Live Performance Timeline](M6_LIVE_PERFORMANCE_TIMELINE.md) is now merged as PR #31 and uses these macros for scheduled modulation events.

## A. Performance Macro System

The Performance Macro layer sits above the existing normalized modulation architecture. It does not introduce a second effect or target engine: each macro publishes a normalized source value that can feed the existing global Modulation Matrix and per-layer performance modifier engine.

### Built-in macros

Every macro has a normalized value in the inclusive range 0–1.

| Macro | Intended control domain |
| --- | --- |
| **CHAOS** | Glitch, rotation, chromatic displacement and feedback motion |
| **DNST** | Mosaic/tile density, kaleidoscope slices, text reveal steps and particle emission |
| **DPTH** | Transform mix, zoom, feedback amount, trails and layer positioning |
| **DEC** | Feedback persistence, layer-FX mix, particle lifetime and trails |
| **PRESSURE** | Contrast, edge/threshold treatment, distortion and particle forces |
| **FRAG** | Pixelation, pixel sorting, displacement scale, glyph motion and particle spread |

The initial value for each built-in macro is 0.0. Default master and per-layer mappings are installed without replacing operator-authored routes or assignments. The per-layer engine applies mappings only to compatible, unlocked layers. Target settings that require CPU rasterization are deliberately excluded from the default live density mapping; text reveal and particle controls use existing shader/simulation targets.

### Input sources and manual control

A macro can use one continuous input source at a time, or remain in manual mode. The source selector offers available audio-analysis features, normalized transport/rhythm signals, Sonic Pi's `macro.energy` and `macro.cutoff`, and outputs from the Modulator Bank. Modulator Bank outputs are evaluated before macro inputs, so a follower/LFO can feed a macro and that macro can then fan out to multiple targets.

A manual change temporarily takes priority over an assigned continuous source, then the continuous source resumes. The current defaults use 35 ms attack and 260 ms release smoothing. The six macro definitions, source assignments, values, smoothing settings and keyboard shortcuts are saved in project and scene state.

### Keyboard

Each macro has an editable keyboard shortcut. The default shortcuts are:

| Macro | Default shortcut |
| --- | --- |
| CHAOS | `Ctrl+Alt+1` |
| DNST | `Ctrl+Alt+2` |
| DPTH | `Ctrl+Alt+3` |
| DEC | `Ctrl+Alt+4` |
| PRESSURE | `Ctrl+Alt+5` |
| FRAG | `Ctrl+Alt+6` |

A shortcut toggles its macro between 0.0 and 1.0. It is an endpoint toggle, not a key-pressure or hold-to-modulate control. Shortcuts are application-wide while the main window is active.

### MIDI CC and notes

The existing MIDI Learn workflow includes all six Performance Macro targets. A learned CC or note message can therefore control one macro, which in turn fans out to its configured master and per-layer destinations. MIDI note velocity is normalized to 0–1; note-off is delivered as zero. Existing mapping range, curve and pickup behaviour remains in the MIDI mapping engine.

### OSC and Sonic Pi

The versioned OSC protocol retains the existing `/eli_lab/v1/macro/set` route. After the normal session ID and sequence number, the message carries a macro name and a normalized value:

```text
/eli_lab/v1/macro/set <session_id> <sequence> chaos 0.75
/eli_lab/v1/macro/set <session_id> <sequence> density 0.40
/eli_lab/v1/macro/set <session_id> <sequence> depth 0.60
/eli_lab/v1/macro/set <session_id> <sequence> decay 0.85
/eli_lab/v1/macro/set <session_id> <sequence> pressure 0.50
/eli_lab/v1/macro/set <session_id> <sequence> fragment 0.70
```

The accepted names are `energy`, `cutoff`, `chaos`, `density`, `depth`, `decay`, `pressure` and `fragment`. Existing `energy` and `cutoff` messages continue to feed the M4/M5 control state; the six new names additionally update their corresponding Performance Macro value. OSC macro values are held for at least five seconds or two bars, whichever is longer, matching the existing bar-based freshness policy.

### Persistence and lifecycle

- `.eliav` project files persist macro definitions and input/shortcut settings.
- Performance Scene snapshots capture and restore macro configuration and values alongside the Modulator Bank and modulation routes.
- Performance Sets reuse project serialization, so the same macro setup travels with the set.
- Loading a project or scene sanitizes references to missing Modulator Bank sources.
- Removing a Modulator Bank source clears macros that refer to it.
- The macro engine runs on the application tick. MIDI/OSC callbacks only submit normalized events through the existing bounded event path; they do not mutate Qt widgets, composition state or OpenGL resources.

### Current boundaries

- The first increment provides six built-in macros; it does not provide user-created macro definitions or arbitrary macro graphs.
- Each macro accepts one continuous source at a time. Multi-target fan-out is supported through the existing modulation and layer-modifier engines.
- Keyboard shortcuts toggle between endpoints; they do not provide analog keyboard pressure or key-down/key-up envelopes.
- The current panel exposes source selection and direct value control. Fine-grained input range, input curve, inversion and attack/release editing are not exposed as separate panel controls in this increment.
- Master/layer routing is a set of safe defaults, not a claim that every parameter of every generator is available on every layer.
- Quality CI cannot verify Qt shortcut conflicts, physical MIDI hardware, Sonic Pi rehearsal, shader compilation on the target GPU or projector performance.

## Verification checklist

- [ ] Python compilation and Ruff pass on the PR head.
- [ ] Open a project, change macro source/shortcut/value, save, restart, and confirm the values/configuration restore.
- [ ] Recall a VJ scene and confirm its macro configuration and value state restore.
- [ ] Move one MIDI CC through its range and verify a selected macro and its multiple targets respond; verify MIDI note-on/note-off behaviour.
- [ ] Send all six OSC macro names with valid session/sequence data and verify normalized updates; send out-of-range values and unknown names and verify rejection.
- [ ] Test one audio band, one Sonic Pi macro and one Modulator Bank follower as macro inputs.
- [ ] Verify keyboard toggles do not collide with the application's normal commands.
- [ ] Confirm the default macro controls do not cause per-frame CPU generator rasterization.
- [ ] Run a sustained live test with master feedback, text, legacy particles and Particle System 2.0 on the target Windows GPU.

# M6 — Advanced VJ Environment

**Status:** M6-A1, M6-B1, M6-C1, M6-D1/D2 and M6-E1 are merged to `main`. E1 delivers rich runs, practical vertical layouts, text paths and texture-space GPU animation; E2 glyph instancing and E3 presets/text feedback remain future slices. This live-performance follow-up adds AUTO PERF targets for the newer typography, layer-FX and Particle System 2.0 controls, continuous particle emission, adaptive compact/4:3 workspace sizing, and a Queer text pool. Target-Windows GPU and projector validation remains open.  
**First workstream:** A. A proper live mixer.  
**Design references:** live-mixer / media-bin workflows in Resolume Arena, VDMX media bins and TouchDesigner performance interfaces. These are interaction references, not a requirement to clone another product's UI.

## Goal

Evolve the existing four-deck playback and composition foundation into an operator-first live VJ environment. The operator should be able to prepare sources before a show, trigger one or several clips deliberately, understand what is happening on every deck, and intervene quickly without leaving the performance surface.

M6 should build on the current media library, four PyAV decks, layer model, automation, transport quantization and preview/projector renderers. It should not replace the decoder architecture or move media decoding, composition mutation or OpenGL ownership into UI widgets.

## A. A proper live mixer

### A1. Operator model

Design a dedicated live-mixer surface around the four existing video decks:

- Persistent deck identity and clear deck state (empty, loading, ready, playing, held/paused or failed, as applicable to the final transport model).
- A compact per-deck view of the loaded clip, thumbnail, playback/segment position, loop/one-shot mode and relevant transport state.
- Direct access to load, play/trigger, stop, restart, hold/freeze and deck lock without navigating through layer editing panels.
- Clear indication of the relationship between a deck, its media source and the composition layer it feeds.
- Keep detailed media management, generator authoring, effects and modulation in their existing specialist panels; the live surface should be optimized for operation rather than exposing every parameter at once.

**Initial implementation checkpoint — M6-A1**

The first operator-surface increment adds four persistent deck cards with clip identity, cached library thumbnail/metadata, playback position, duration feedback and the associated composition-layer name. Each card exposes LOAD, PLAY, PAUSE, HOLD/UNHOLD, RESTART and STOP, plus the existing loop and lock controls. LOAD opens the Media Library with that deck preselected; browsing does not replace its current source. Deck status refreshes independently of the render cadence.

HOLD pauses only the selected deck's decoder and retains its most recently presented frame. The preview and projector continue to consume their existing shared CPU frame snapshots and renderer-local GPU resources. No decoder or OpenGL ownership has moved into the widgets.

This is an initial A1 foundation, not the completion of all A1 requirements. Media-bin preparation and trigger routing belong to A2; more advanced seeking, speed/reverse and segment editing need their own decoder/timestamp design and acceptance checks.

### A2. Media bins and clip triggering

Introduce performance-oriented media bins that turn the indexed Media Library into a triggerable source bank:

- Create and manage named bins or collections of clips for a show.
- Browse/search/filter the indexed media and add or remove clips without moving or duplicating source files.
- Trigger a clip into an explicitly selected deck.
- Support selecting multiple bin items and triggering them together, assigning them to selected/available decks with deterministic, visible target mapping.
- Make the difference between selecting a clip, loading it into a deck and triggering playback unmistakable.
- Preserve current deck playback while browsing or preparing another trigger; browsing must not accidentally replace an on-air source.
- Define predictable behaviour when more clips are selected than available decks: report the conflict and do not silently discard or overwrite sources.

### A3. Synchronized multi-trigger behaviour

Multiple clip launches should be treated as one operator action:

- Support immediate launch first.
- Design an optional quantized launch mode using the existing internal/Sonic Pi beat, bar and phrase clock.
- A multi-trigger action should share one launch boundary so clips intended to start together do not drift because of sequential UI callbacks.
- Define the launch policy for decks already playing: replace, queue, or reject according to an explicit operator setting/action.
- Provide visible feedback for pending quantized launches and a clear cancel path before the boundary.
- Keep the trigger system independent from the OSC protocol; it should consume the existing normalized transport events.

### A4. Mixing and transitions

Define a coherent live mixing model on top of the current composition/layer pipeline:

- Establish how deck output is blended into the composition and how the operator adjusts per-deck level/opacity.
- Design an A/B or group selection model and a crossfade/transition control that can be operated without opening layer properties.
- Keep hard cuts deterministic and low-latency; add dissolve and any stylized transitions only with measured GPU cost and a clear fallback.
- Preserve the existing per-layer blend modes and effects; do not introduce a second competing source of truth for the same layer properties.
- Provide clear feedback for which sources are on-air, pending, held or excluded from automation.

The exact A/B grouping, crossfader curve, transition duration and whether preview/cue is a separate render output are design decisions to settle before implementing the mixer UI. Do not imply that a dedicated preview bus or a broadcast-style program/preview architecture already exists.

### A5. Live-performance integration

- Make media-bin triggers available to manual operation and to explicit automation actions.
- Allow optional beat/bar/phrase quantization and retain immediate manual override.
- Respect layer/deck locks and manual ownership; AUTO PERF must not unexpectedly replace a manually protected source.
- Keep user actions observable in the existing performance diagnostics and, where appropriate, in a bounded event/action history.
- Persist bin definitions, clip references, deck assignments and operator preferences in a versioned format. Do not persist transient decoder handles or GPU objects.
- Define missing-media and moved-path recovery without deleting original media.

## Delivery sequence

| Slice | Intended result |
| --- | --- |
| M6-A0 — Interaction specification | Complete in the M6 design document: deck states, bin model, multi-select target mapping, trigger semantics, quantization and transition decisions. |
| M6-A1 — Live deck surface | Initial implementation on `m6/a1-live-deck-surface`: four deck cards, clip identity/metadata/thumbnail, position feedback, layer mapping, direct transport, frame hold, restart, loop and lock. Remaining A1 refinements and target-machine rehearsal are open. |
| M6-A2 — Media bins | Named performance bins, clip assignment and explicit deck-targeted trigger actions. |
| M6-A3 — Multi-trigger and quantization | Atomic multi-deck launch, common quantized boundary, pending/cancel feedback and defined collision policy. |
| M6-A4 — Mix and transitions | Operator-facing A/B/group/crossfade controls, deterministic hard cut and measured dissolve/transition path. |
| M6-A5 — Performance integration | Persistence, lock/manual-override rules, diagnostics, keyboard operation and automation integration. |

## B. Scene and composition banks

The VJ Scene Bank promotes the existing Performance Scene Bank into a full composition snapshot system. A scene should capture video assignments, layer topology and transforms, generator/text state, layer/master effects, palette, modulation routes and Modulator Bank definitions. It should be a visual instrument state rather than a small effect preset.

The implementation reuses the versioned `PerformanceScene` model to preserve existing project and performance-set compatibility. B1 adds complete deck and modulation capture/recall, operator cue metadata, MIDI/OSC scene triggers, internal/external clock quantization and compatible random scene selection.

See [M6-B — VJ Scene and Composition Banks](M6_B_SCENE_COMPOSITION_BANK.md) for the full payload, recall safety rules, transition boundary and B0–B4 delivery sequence.

**Current B1 boundary:** compatible numeric parameters morph using the configured curve. Media source, text/generator content and other discrete settings currently use an explicit cut. Dual-scene crossfade, midpoint source switching, fade-through-black, scene sequences and per-parameter locks are not yet implemented.

## C. Advanced visual transformations

The advanced visual path extends the existing ModernGL compositor without moving image processing to the CPU. C1 introduces the first GPU-side geometry and temporal effects:

- Kaleidoscope radial symmetry, polar-coordinate remapping, mosaic/tile and directional luminance-gated scan displacement.
- A displacement map sourced from another layer's existing GPU texture, with RG/luma interpretation and scale/amount controls.
- Edge extraction and ordered dithering alongside the existing posterize controls.
- A per-output feedback engine backed by a bounded five-texture GPU history ring. Controls include amount, decay, zoom, rotation, translation, colour shift, distortion, motion-difference-driven warp, block displacement, blend mode and up to three frames of delay.
- Feedback freeze and generation-based reset; history remains local to each output's GL context and is never serialized as a GPU resource.

The C1 directional scan-sort and motion-driven warp are intentionally shader approximations, not a full GPU sort algorithm or a dense optical-flow solver. Full pixel sorting, high-quality flow estimation, dedicated line-composition tools and multi-stage temporal transitions remain later C slices. See [M6-C — Advanced Visual Transformations](M6_C_ADVANCED_VISUAL_TRANSFORMATIONS.md).

## D. Advanced particle simulation

Preserve the original `particles` generator as a cheap procedural field. Particle System 2.0 is a separate generator type with its own GPU simulation state, fixed-step physics and trail buffers.

### D1 — General-purpose GPU particle foundation

The D1 implementation adds:

- Point, circle and rectangular emitters.
- Deterministic seeded spawning and respawning, with independently seeded populations.
- One to four populations per system, each with its own GPU position/velocity and age/lifetime state.
- Particle lifetime, initial velocity and spread, acceleration, drag and velocity integration.
- Procedural turbulence and attraction, repulsion and orbit force fields.
- Constant, grow, shrink and pulse size-over-lifetime curves.
- GPU trail accumulation.
- Fixed 60 Hz simulation steps, capped at four substeps per render to bound catch-up work.
- Resource ceilings: 8192 particles per system, four systems per output renderer and 16384 particles total per output. Allocation is deterministic by layer order.
- Renderer-local floating-point state textures and half-resolution trail targets. No per-particle CPU simulation or GPU readback is used.

The populations currently share the system-level physics controls but receive stable seed offsets, small emitter offsets, colour variation and size/speed variation. This gives multiple independent streams without multiplying the control surface in the first slice.

### D2 — Source and path emitters

The current development branch extends the simulation shader with:

- Editable path/polyline emission (up to 64 normalized points), including tangent-following launch direction.
- Video brightness, image alpha/luminance silhouette and contour/edge sampling from an existing video or overlay layer texture.
- Deterministic thresholded source selection with 1–16 candidate probes per particle respawn.
- Source target storage and configurable reform strength. When reform is enabled, target positions refresh from the current source at a selectable 0.1–10 second interval, with sampled coordinates mapped through the source layer transform.
- UI source selection, map mode, threshold, probe count, sample cadence, reformation and path-point editing.

Source sampling and particle reformation run in the output renderer's GPU context. A missing source frame disables that source path safely; no CPU particle simulation or duplicate source-frame upload is introduced.

### D1/D2 boundaries

Per-population overrides, per-population modulation targets, advanced vector/collision fields and higher-level shape authoring remain future D3 work. Target-GPU shader and visual acceptance for D1/D2 is still required.

### Particle System 2.0 acceptance

- The original Particle Field remains available and retains its existing look and settings.
- Particle System 2.0 can be added, saved, reopened and edited as a normal composition layer.
- Repeated playback with the same seed and settings produces the same spawn sequence.
- Lifetime, velocity, acceleration, turbulence, force fields, size curves and trails visibly affect the simulation.
- Multiple populations render with stable, distinct seed/colour/size variation.
- The per-renderer particle and system ceilings are enforced even with multiple visible particle layers.
- Video/image source emission is thresholded, and contour/alpha/luma modes behave correctly for the selected layer.
- Source target resampling and reform strength reconstruct the current source silhouette after dispersion.
- Preview and projector own independent simulation state and trail textures.
- Resize, layer removal and GL-context teardown release all simulation and trail resources.
- A 4-deck composition with the maximum particle budget maintains responsive rendering on the target performance GPU.

See [M6-D — Advanced Particle Simulation](M6_D_ADVANCED_PARTICLE_SIMULATION.md).

## E. Typography as an independent visual instrument

The Text Art system is being extended as a first-class typographic instrument rather than just repairing the current single-style text renderer.

### E1 — Rich composition, vertical layout and path typography

The E1 branch adds:

- Optional rich-text runs with independent typeface, size, weight, fill, tracking, outline and shadow. The editor accepts a bounded JSON array; existing one-style layers remain supported.
- Horizontal mixed-language run composition and practical Japanese vertical columns in right-to-left or left-to-right order.
- Text on circular, arc and custom polyline paths, using up to 64 normalized path points.
- Additional GPU-side shader modes: reverse typewriter reveal, dissolve, flicker, character-cell displacement, vertical reveal, scattered glyph motion, segmented collision-style movement and mechanical scrolling.
- A separate typography layout module called by the existing CPU raster worker. The compositor animates the cached texture with uniforms; animation-only changes do not start a new raster job.

The new shader effects are bounded texture-space approximations, not one independently simulated GPU instance per glyph. The vertical writer is a practical column compositor with orientation heuristics; full OpenType vertical forms and shaping remain future work.

### E1 boundaries and next work

True glyph-level animation, semantic word/character timing, per-character entrance/exit schedules, deterministic kanji replacement, real word collision physics, dedicated text-feedback routing, and named typographic presets are not claimed as E1 features.

E2 should introduce a bounded GPU glyph atlas and per-glyph instance data so position, scale, rotation, alpha, colour and timing can be evaluated without creating Qt/Python objects per frame. E3 can add saved typographic compositions and a dedicated text feedback route.

See [M6-E — Typography as an Independent Visual Instrument](M6_E_TYPOGRAPHY.md) for the implementation boundaries, pipeline contract, E2 proposal and target-GPU acceptance checklist.

## Acceptance criteria

M6-A is ready for operator rehearsal when:

1. A show can be prepared in named media bins without disturbing current deck playback.
2. Any single clip can be loaded and triggered into a chosen deck through the live surface.
3. A multi-selection can be mapped to available decks predictably and launched as one action.
4. Quantized multi-trigger starts share the same beat/bar/phrase boundary and can be cancelled before launch.
5. Deck source, playback, pending trigger, lock and failure states are visible without opening a separate layer editor.
6. Manual protection and layer/deck locks prevent automation from unexpectedly replacing an operator-controlled source.
7. Four-deck playback and projector output remain synchronized with the existing composition pipeline.
8. Missing media and deck errors are isolated and recoverable; one failed source does not freeze the mixer.
9. The UI remains responsive while media bins are browsed, clips are queued and all four decoders are active.
10. A representative live set can be saved, reopened and rehearsed with the same bins and source assignments.

## Performance and reliability constraints

- Preserve bounded decoder and control queues.
- Keep media I/O and decode work off the UI thread.
- A trigger is a control-plane event; the decoder worker remains the owner of media decoding.
- Avoid allocating new decoder threads on every trigger without a defined retirement policy.
- Do not create or transfer OpenGL objects between the preview and projector contexts.
- Record per-deck decode/render timing and dropped-frame metrics during acceptance testing.
- Test four simultaneous H.264 1080p sources first, then representative higher-bitrate media on the target performance computer.

## Explicitly outside this initial M6-A scope

- Unlimited decks or unbounded simultaneous decoders.
- A complete node-based compositing graph.
- Full audio mixing or replacing Sonic Pi as the audio engine.
- Master-output recording and audio/video muxing; these remain a separate deferred delivery item unless the milestone scope is explicitly expanded.
- Claiming target-hardware readiness based only on compilation/lint CI.

## Relationship to earlier milestones

M0–M5 remain the foundation. M5 code is merged to `main`; its static quality workflow passed on `358dc597`. M5's live SONATA, audio-device and projector stress checks remain manual sign-off tasks and should be carried forward in the project validation log rather than treated as passed. M6 development can proceed in parallel with those hardware checks.

See [M6-B — VJ Scene and Composition Banks](M6_B_SCENE_COMPOSITION_BANK.md), [ROADMAP.md](ROADMAP.md), [ARCHITECTURE.md](ARCHITECTURE.md) and [M5 Completion Handoff](M5_COMPLETION_HANDOFF.md).

## F. Advanced performance controls

**The Performance Macro System is merged to `main` in PR #30.** Six built-in macros — CHAOS, DNST, DPTH, DEC, PRESSURE and FRAG — fan one 0–1 control value out to multiple master and compatible per-layer targets. They can be driven manually, by keyboard toggle, MIDI CC/note, OSC, audio/transport sources or Modulator Bank outputs. The macro definitions and assignments are persisted with projects and performance sets.

See [M6 — Advanced Performance Controls](M6_ADVANCED_PERFORMANCE_CONTROLS.md) for the full source, routing, persistence and validation boundaries.

## G. Live Performance Timeline

**The initial timeline implementation is merged to `main` in [PR #31](https://github.com/ilyaminineli/eli_lab-av-translator/pull/31).** The timeline is a project-persisted bar/beat show plan that runs beside the internal or Sonic Pi transport. Target-Windows musical rehearsal and projector acceptance remain open.

Supported event types are scene markers, phrase markers, saved-scene recall, deck/clip triggers, master effect changes, Text Art regeneration, palette changes, Performance Macro modulation and transition cues. Each event has an authored bar/beat, label, enabled state and validated JSON payload. Same-beat events run in insertion order.

The LIVE PERF TMLN dock exposes the event list, editor, arm/disarm, rewind and the eight-section example structure. Event actions use existing app services and are processed on the application/UI tick. AUTO PERF and Modulator Bank modulation can continue generating variation inside the timeline structure.

Sonic Pi currently reports one clock event per bar. The timeline interpolates beat positions locally from that packet's BPM and timestamp; this is not a per-beat OSC clock or frame-accurate sync. Scene transitions retain the current numeric morph and discrete cut behaviour. Project loading restores timeline definitions but does not automatically arm playback.

See [M6 — Live Performance Timeline](M6_LIVE_PERFORMANCE_TIMELINE.md) for event payloads, clock handling, persistence, limits and acceptance checks.

# M6-B — VJ Scene and Composition Banks

**Status:** B0 interaction model documented; B1 full-scene capture/recall and trigger foundation implemented on `m6/b1-vj-scene-bank`. Windows operator rehearsal and the B2–B4 work remain open.

## Goal

Promote the existing Performance Scene Bank from a small musical/effect snapshot into a first-class **VJ Scene Bank**. A scene is a visual instrument state, not just a master-effect preset. It should restore the full composition context and the control system that makes that composition performable.

The current `PerformanceScene` model and persistence format are retained for backwards compatibility. The UI presents this as the VJ Scene Bank; this avoids maintaining a second competing scene store.

## Scene payload

A captured scene includes:

- Composition canvas dimensions and background.
- Layer identity, order, visibility, lock state, position, scale, rotation and opacity.
- Video layer/deck relationships and the saved deck source assignments, segment in/out, loop mode and playback state.
- Layer blend modes and layer effect settings/chains.
- Generator type and settings, including Text Art content, font and animation parameters.
- Overlay source references and overlay playback/mask settings.
- Master effect settings and preset identity.
- Palette identity.
- Automation settings and internal transport configuration.
- Performance intensity and macro values.
- Global modulation routes.
- Modulator Bank definitions and reusable presets.
- Scene-level OSC cue, recall quantization, tags and transition metadata.

A scene stores media paths and stable IDs, not the original media, decoded frame buffers, decoder threads, GPU textures or OpenGL objects.

## Capture and recall semantics

### Capture

- Capturing a scene does not modify the current composition.
- Existing scene IDs are updated in place.
- OSC cue names must be unique within the VJ Scene Bank and use the protocol-safe 1–64 character identifier alphabet (letters, numbers, period, underscore, colon or hyphen).
- Scene definitions are persisted in ordinary projects and performance sets.
- Older project/performance-set scenes remain loadable; fields added by B1 have defaults.

### Recall

- The composition, layer stack, master effects, global modulation routes and Modulator Bank are restored from the scene.
- Video decks are restored from their saved file paths and segment settings.
- Current operator locks take precedence: locked layers and locked decks are not replaced by recall.
- If a saved deck source is missing, the current source on that deck is retained and a recoverable diagnostic event is emitted.
- Overlay runtime players are rebuilt from the restored layer definitions. GPU resources remain owned by each renderer.
- Media remains external; scenes never embed or copy source footage.

### Compatible-scene selection

The RANDOM COMPATIBLE action filters scenes by canvas dimensions and layer topology (layer IDs, source types, generator types and overlay kinds). It then selects from that filtered bank. This deliberately avoids random recalls that silently add/remove an incompatible layer structure.

## Triggering and synchronization

- Each scene can have a unique OSC cue name. A matching `/eli_lab/v1/cue/trigger` cue recalls that scene.
- MIDI target choices include each saved VJ scene. Note or CC activation triggers recall; release resets the trigger edge so a later press can trigger again.
- Scene recall quantization supports immediate, next beat, next bar and next phrase.
- Internal transport schedules against its existing beat/bar/phrase clock.
- When Sonic Pi is the active external clock, pending recalls are scheduled against its incoming beat/bar events instead of starting a second internal clock.

## Transition model — current boundary

B1 improves the existing numeric scene morph:

- Compatible numeric layer parameters and supported master-effect values interpolate over the requested duration.
- The scene's configured curve is stored and used (linear, smoothstep, ease-in or ease-out).
- Discrete content currently uses an explicit **cut** policy: media source changes, text content, generator type/settings, blend modes, visibility/order changes and other non-interpolable data are switched as part of recall.

The transition metadata is versioned and stored with each scene, but B1 does **not** claim to implement dual-scene crossfading, fade-through-black or midpoint discrete switching yet. Those require a dedicated scene transition runtime and measured compositor/deck behaviour.

## Remaining implementation slices

| Slice | Scope |
| --- | --- |
| M6-B0 — Interaction specification | Complete: scene payload, recall safety, compatibility rule, OSC/MIDI triggering and discrete-versus-continuous transition boundary. |
| M6-B1 — Full scene snapshots | Implemented on `m6/b1-vj-scene-bank`: deck assignments, composition/layers, effects, palette, automation/transport, modulation routes, Modulator Bank, OSC cues, MIDI targets and compatible random selection. |
| M6-B2 — Scene transition engine | Interpolate compatible numeric values; add explicit midpoint switching and fade-through-black for media/text/generator changes; define crossfade behaviour where two source states can coexist; expose duration, curve and switch policy. |
| M6-B3 — Scene sequences | Ordered scene playlists, per-step quantization/duration, loop/one-shot mode, next/previous/stop controls and transport-synchronized progression. |
| M6-B4 — Parameter locks and bank management | Per-parameter automation/recall locks, named scene groups/banks, import/export, duplicate/rename and stronger compatibility diagnostics. |

## Acceptance criteria

B is ready for operator rehearsal when:

1. A scene round-trips all supported composition, deck, effect and modulation state through both a project and a performance set.
2. Recall preserves live locked layers/decks and reports missing media without stopping unrelated playback.
3. Scene cues can be triggered by OSC and MIDI and respect the configured quantization.
4. Random selection never chooses a scene with an incompatible composition topology.
5. Compatible numeric values morph predictably, while discrete source/text changes follow a visible, deterministic transition policy.
6. Scene sequences run against internal transport and Sonic Pi clock without drift or duplicated clocks.
7. Scene/parameter locks prevent autonomous performance and recall from overwriting protected operator decisions.
8. Four-deck preview/projector rendering remains stable while scenes are captured, recalled and transitioned.

## Engineering constraints

- Preserve the existing four-deck decoder architecture and bounded frame/event queues.
- Do not place decoding, media I/O or OpenGL ownership in UI widgets.
- Do not persist runtime handles, current GPU resources or transient MIDI hardware state.
- Validate scene payloads before changing the active composition.
- A failed scene asset must remain local to its layer/deck; it must not freeze the application.
- Keep a legacy read path for existing project and `.eliset` files.

# M6-C — Advanced Visual Transformations

## Objective

Add image-space geometry and temporal processing that turns the compositor into a more expressive VJ instrument. Effects must remain on the GPU, operate after the current layer stack, and keep each output window's OpenGL resources private to its own context.

C is intentionally staged. The first implementation concentrates on the two highest-value foundations identified in the milestone brief: persistent feedback and displacement maps. The initial slice also adds a compact set of geometry and tonal transforms that fit the existing GLSL post pass.

## C1 — GPU geometry and feedback foundation

### Geometry and image transforms

| Control | C1 implementation | Behaviour |
| --- | --- | --- |
| Kaleidoscope | Implemented | Radial wedge folding with slice count, rotation and zoom. |
| Polar coordinates | Implemented | Remaps the rectangular image into angular/radial coordinates. |
| Mosaic / tile | Implemented | Quantizes image sampling to a configurable tile grid. |
| Directional pixel sort | Approximation | Luminance-gated horizontal scan displacement, not a full row/region sorting algorithm. |
| Displacement map | Implemented | Samples another layer's existing source texture as an RG or luma displacement field. |
| Posterize + dithering | Implemented | Extends the existing tonal reduction with an ordered 4×4-style threshold pattern. |
| Edge extraction | Implemented | Four-neighbour luminance-gradient edge pass for graphic/line-based looks. |
| Datamosh-style blocks | Feedback approximation | Time-quantized block displacement of the retained feedback image. |
| Optical-flow distortion | Feedback approximation | Temporal luma-difference and image-gradient-driven warp; not a dense optical-flow solver. |

Geometry transforms can be composed with the existing master colour effects. Displacement maps are selected by layer source ID; selecting OFF or a missing source safely disables the map rather than sampling an unrelated texture.

### Feedback engine

The feedback engine sits after the master post-processing pass:

1. Compose layers into the compositor's existing ping-pong targets.
2. Apply master filters and geometry transforms into a renderer-local post target.
3. Sample the delayed feedback history and combine it with the current post image.
4. Write the new result to the next history texture when not frozen.
5. Present the result to that output window's framebuffer.

The history is a bounded five-texture ring per output context. The selected delay supports the previous frame through three additional frames of delay. This avoids an unbounded temporal queue and all CPU readback/copy paths. Preview and projector outputs have independent history because they do not share GL objects or contexts.

### Feedback controls

| Parameter | Meaning |
| --- | --- |
| Enable | Enables temporal feedback. |
| Amount | Mixes retained imagery with the current composited frame. |
| Decay | Multiplies retained colour on each feedback pass. |
| Zoom / rotation / X-Y offset | Transforms the historical image before it is fed back. |
| Colour shift | Adds an RGB split to the retained image. |
| Distortion | Adds a procedural spatial warp to the history sample. |
| Motion-driven warp | Uses temporal luminance difference and local history gradients to deform the history sample. |
| Datamosh blocks | Applies time-quantized block displacement to retained imagery. |
| Blend mode | Normal, add, screen, multiply or difference. |
| Temporal delay | Selects up to three frames behind the latest completed history frame. |
| Freeze | Stops advancing the stored history while continuing to display the current input combined with the frozen history. |
| Reset | Advances a reset generation; every output context clears its own history on its next render. |

Reset and resize clear the entire ring. Frozen history is not overwritten. Feedback settings are persisted through the existing `EffectSettings` project and VJ Scene serialization; GPU textures, current history index and retained frames are runtime-only.

## Performance and safety constraints

- No CPU image copies or texture readbacks in the feedback loop.
- Feedback buffers are owned and released by the corresponding `Compositor` and GL context.
- The five-texture history ring is allocated lazily on first feedback use; when allocated, it is resized with that output and released with its GL context.
- Raw RGBA8 history storage is approximately 39.6 MiB per 1920×1080 output or 158.2 MiB per 3840×2160 output, before driver overhead. Preview and projector each allocate their own ring only when feedback is enabled.
- History length is fixed and resize-aware; no unbounded frame retention.
- The displacement source is an existing compositor texture. It is never uploaded a second time for use as a map.
- The feedback pass is bypassed when disabled or when amount is zero.
- Freeze does not stop decoders or layer composition; it freezes only the retained feedback memory.
- Reset uses a monotonic generation so both preview and projector clear independently even though the UI action is shared.
- GPU memory cost is proportional to output dimensions and the fixed history length. Validate at the target output sizes before considering larger history.

## Acceptance checks

### Static/software checks

- Python compilation and Ruff pass on the branch.
- Legacy projects load with defaults for all newly introduced transform/feedback fields.
- New fields survive project and VJ Scene round-trip because they are part of the existing `EffectSettings` serialization.
- The preview and projector each allocate, resize and release independent feedback textures.
- Shader samplers use explicit texture units and do not sample from the framebuffer currently being written.
- Missing displacement source and disabled feedback both degrade to the ordinary post pass.

### Manual GPU/visual checks

- Kaleidoscope slice count, rotation and zoom stay centred and stable at 16:9 and non-16:9 output sizes.
- Polar remapping, mosaic, pixel-sort approximation, displacement-map RG/luma modes, edge extraction and ordered dithering produce expected image changes.
- Feedback starts with a clean seed frame, retains trails with decay, and changes predictably with amount/zoom/rotation/translation/colour shift/blend.
- A 0–3 frame temporal delay selects the correct older history slot after the ring fills.
- Freeze holds history while live content continues; unfreeze resumes updates; reset clears immediately on both preview and projector render ticks.
- Resize and context recreation do not preserve stale feedback textures or produce black frames after release.
- Run both outputs simultaneously at the intended projector resolution; monitor GPU memory, render time and dropped frames.

## C2 — Higher-quality image analysis and sorting

- A true directional pixel-sort pass that gathers and orders selected row/column segments by luminance or a chosen channel.
- Better edge extraction (Sobel/Canny-style thresholds), line extraction, contour emphasis and graphic line compositions.
- Dither pattern options and colour-channel/bit-depth control.
- Region masks and sort thresholds with independent X/Y direction, scan length and temporal gating.

## C3 — Motion and temporal composition

- Dense or pyramidal optical-flow estimation, with explicit GPU cost and fallback quality tiers.
- Vector-field displacement, motion trails and directional smears derived from actual frame motion.
- Dedicated datamosh transition modes with keyframeable block size, motion-vector retention and source switching.
- Optional temporal delay beyond the small C1 history ring only after memory/latency profiling.

## C4 — Scene, MIDI/OSC and automation integration

The new settings are included in the existing EffectSettings model, so scenes capture and recall them with other master effects. The live-performance integration now exposes numeric master transform, displacement and feedback parameters as bounded Modulation Matrix / AUTO PERF / MIDI targets. Transform-specific values become visible when the corresponding transform mode is selected; feedback parameters take effect when feedback is enabled. Reset and freeze remain explicit operator actions rather than automatic modulation targets.

## Scope boundary

C1 does not claim full optical flow, exact GPU pixel sorting, a dedicated vector-field editor, or an unlimited feedback delay buffer. Those are deliberate later work rather than approximations hidden behind full-effect names.

# M6-D — Advanced Particle Simulation

## Status

**D1 + D2 are merged to `main`.** This follow-up adds continuous rate-based emission, Auto Performance routing, and short hidden-layer state retention. Static CI can validate Python and lint; target-GPU shader, continuous-emission and projector acceptance still require Windows testing. The original `particles` procedural field remains unchanged.

## Objective

Preserve the existing `particles` procedural field and introduce a separate `particle_system_2` generator with a GPU-resident particle simulation. Particle System 2.0 is a physics system, not a replacement or rename of the inexpensive legacy generator.

## D1 — General-purpose GPU foundation

### Delivered capability

| Capability | D1 state |
| --- | --- |
| Point emitter | Implemented |
| Circle emitter | Implemented |
| Rectangle emitter | Implemented |
| Path / polyline emitter | D2 implemented (up to 64 normalized points) |
| Video luminance emitter | D2 implemented |
| Image alpha / luminance silhouette emitter | D2 implemented |
| Contour / edge emitter | D2 implemented |
| Video/image source reformation | D2 implemented |
| Deterministic seed and respawn sequence | Implemented |
| Multiple independent populations | Implemented (1–4 per system) |
| Particle lifetime / respawn | Implemented |
| Initial velocity and random spread | Implemented |
| Acceleration and drag | Implemented |
| Turbulence field | Implemented |
| Attraction / repulsion / orbit force field | Implemented |
| GPU particle trails | Implemented |
| Size over lifetime | Constant, grow, shrink, pulse |
| Per-population individual parameter overrides | D3 |

### Physics and deterministic behaviour

Particles are represented by three GPU state records per particle:

- Position and velocity.
- Age, lifetime, respawn cycle and per-particle size variation.
- Source target position, target-active flag and last source-resampling phase.

A fixed 60 Hz simulation step integrates acceleration, drag, turbulence and the selected radial force field. Render stalls are bounded to four simulation substeps per render; excess elapsed time is capped rather than creating an unbounded catch-up loop.

The spawn sequence uses the configured system seed together with stable particle index, population seed and respawn cycle. Changing the seed, total count or population count rebuilds the initial GPU state. Ordinary continuous control changes update shader uniforms without moving per-particle state through the CPU.

### Live-event emission

Particle System 2.0 now has a continuous emission-rate control (0–3000 particles/second; default 600). A deterministic per-particle/per-fixed-step probability gate spreads births over time instead of launching the entire initial population as one synchronized burst. The rate is divided across independent populations, so population count does not multiply the requested overall rate. The hard particle cap remains in force: emission selects available/dead particles and never allocates unbounded state.

The emission rate is exposed to AUTO PERF and can respond to energy and beat pulses. Existing speed, particle radius, lifetime, turbulence, force strength, trail persistence and source-reform strength are also modifier targets. This makes the system respond continuously to event signals while retaining the existing fixed-step GPU simulation and bounded resource model.

The compositor retains a particle system for up to six seconds after its layer becomes temporarily inactive, allowing brief cuts and automation changes without immediately discarding simulation/trail state. Layer removal, render failure, output-context teardown or expiry still releases resources.

Each system may contain one to four populations. D1 populations share emitter and physics settings but have separate state textures and seeds, stable small emitter offsets, and distinct speed/size/colour variation. This provides layered motion without duplicating all controls in the first UI.

### Resource ceilings

- Maximum 8192 particles per system layer.
- Maximum four active Particle System 2.0 layers per output renderer.
- Maximum 16384 particles total per output renderer.
- Budget is allocated deterministically in composition layer order. If earlier layers consume the budget, later systems are capped or omitted; they do not silently create more GPU state.
- Simulation uses three fixed-size RGBA32F ping-pong texture pairs for state, metadata and source targets.
- Trail accumulation uses two RGBA8 render targets at half output resolution to constrain memory and fill rate.
- Existing video/image source textures are sampled directly by the renderer-local GPU simulation; the particle system does not upload a duplicate source image.
- The editable path is uploaded as a compact RG32F texture only when its points change.
- CPU memory is used only to initialize bounded state buffers and upload the small path definition; per-frame integration, source sampling, respawning, force evaluation and trail accumulation stay on the GPU.

At 8192 particles, position/velocity, metadata and source-target ping-pong state consumes approximately 768 KiB per system, excluding driver overhead. Trail memory is the larger cost: two half-resolution RGBA8 targets use about 4 MiB per 1080p output layer or 15.8 MiB per 4K output layer. Preview and projector each own these resources independently.

### Integration

Particle System 2.0 is a normal composition layer and uses the existing layer transform, opacity, blend mode and layer-effect path. Its settings are stored in `Layer.generator_settings`, so project and VJ Scene persistence use the existing composition serialization. The renderer owns GPU objects; they are never serialized.

The legacy `particles` field continues to use its existing fragment-shader path and its old density/speed/size/spread/trail/mode controls. It is not migrated to Particle System 2.0 automatically.

## D1 + D2 acceptance checks

### Static/software checks

- Python compilation and Ruff pass.
- Legacy `particles` settings and rendering remain unchanged.
- `particle_system_2` settings normalize and clamp count, population count, emitter, physics, force and visual ranges.
- New layers save/reopen through existing composition serialization.
- The CPU generator raster service is not asked to rasterize Particle System 2.0.
- Emission-rate changes produce continuous, distributed births over multiple lifetimes; the configured rate remains consistent across 1–4 populations.
- AUTO PERF can modulate emission rate, speed, radius, lifetime, turbulence, force, trail persistence and source reformation.
- Brief hide/show or cut intervals shorter than the retention window do not recreate the GPU simulation; removed layers and expired inactive systems are released.
- The compositor caps active systems and total particles and releases resources when layers are removed.

### Manual GPU checks

- Point, circle and rectangle emitter shapes are correct.
- Same seed/settings reproduce the same spawn sequence over repeated runs.
- Different populations have independent stable streams and readable colour/size separation.
- Lifetime/respawn, initial direction/spread, acceleration, drag and each force mode behave as expected.
- Turbulence has stable motion at different frame rates and after brief render stalls.
- Size curves and trail persistence produce smooth results without unbounded accumulation.
- Resize, hide/show, remove/re-add and context recreation do not leak GPU objects or leave stale trails.
- Four-deck video playback plus 16384 particles remains responsive at the intended projector resolution.

## D2 — Path, image and video emitters

**Implemented in the current development branch; GPU/visual acceptance remains open.**

- Point, circle and rectangle emitters remain available.
- A path/polyline emitter samples an editable list of up to 64 normalized points from a compact GPU path texture. Emission can follow a selected cardinal direction or the local path tangent.
- Video-luminance emission samples an existing video/overlay layer's GPU texture and preferentially spawns in bright regions.
- Image-silhouette emission supports alpha or luminance maps, allowing transparent PNG overlays as well as opaque grayscale imagery.
- Contour emission measures four-neighbour luminance gradients in the source texture and uses edge strength for candidate selection.
- Source sampling is deterministic per particle/respawn seed. Each spawn checks a bounded 1–16 candidates and applies a configurable threshold.
- Source controls include the chosen video/image layer, map mode, threshold, probe count and resample interval (0.1–10 seconds).
- Sampled source coordinates are mapped through the source layer's position, scale and rotation so emitted particles line up with the footage in the composition.
- Reformation stores each particle's sampled source coordinate as a GPU target. With reform enabled, a spring force pulls particles back toward the source silhouette; targets refresh from the current source frame at the chosen interval, so moving footage can change the shape being reconstructed.
- Missing source textures safely disable source sampling for that simulation step. When no candidate satisfies the threshold, that respawn is suppressed and retried rather than generating a false bright-region particle.

The path points are saved in the layer's generator settings. Source textures remain the renderer's existing layer textures. Particle positions, source targets and trails remain GPU-only and are not written to projects.

### Additional D2 manual checks

- Path, point, circle and rectangle emitters display the expected shape and tangent mode.
- Video brightness thresholding, image alpha/luma silhouette and contour sampling respond to the selected layer texture.
- Reform strength and resample interval pull a dispersed cloud toward the current source mask.
- Source removal or missing frames degrade safely without GPU or application failure.
- Preview and projector use independent but repeatable source-emission and reformation state.

## D3 — Advanced emitter and population authoring

- Per-population emitter, count, colour, lifetime, speed, size and force overrides.
- Per-population curves and modulation/MIDI/OSC targets.
- Additional vector fields, collision/mask forces and more advanced target-shape reformation.
- Optional render-scale, trail-resolution and simulation-quality controls with clear GPU-budget feedback.

## Scope boundary

D1/D2 does not claim per-population independent authoring, dense video motion tracking, codec-level datamoshing or advanced collision/vector-field solvers. Those remain D3 work rather than being approximated as full features.

# M6-E — Typography as an Independent Visual Instrument

**Implementation branch:** `m6/e1-typographic-instrument`  
**Current slice:** E1 — rich runs, vertical layout, text paths and GPU texture-space motion  
**Status:** E1 is merged to `main`. Rich runs, vertical layouts, text paths and texture-space shader modes are implemented. Target-Windows visual and GPU validation remains open.

## Goal

Treat Text Art as an authored visual instrument rather than a single string rendered with one font. Typography should support multiple voices within a layer, Japanese vertical composition, spatial paths and time-based motion while retaining the renderer's strict separation between content/layout work and frame-rate animation.

E1 extends the existing text pipeline. It does not replace the asynchronous raster service and does not create GPU resources from the worker thread.

## E1 — Rich composition and animated texture

### Rich text runs

A text layer accepts an optional `text_runs` array. Each run can override:

- Text content.
- Typeface family, pixel size and weight.
- Fill colour and letter spacing.
- Outline colour and width.
- Shadow enablement.

The editor exposes this as a bounded JSON array (maximum 64 runs and 8192 combined characters after normalization). When no runs are supplied, the existing single-style text editor and legacy layout are retained. Each run is shaped/rasterized as part of one immutable CPU snapshot; the resulting image is uploaded independently by each render context.

Example:

```json
[
  {"text":"記憶は", "font_family":"Noto Sans JP", "font_size":180, "font_weight":900, "color":"#F2EEE6"},
  {"text":"まだここにある", "font_size":92, "font_weight":500, "color":"#C35C75", "letter_spacing":3}
]
```

### Japanese and multilingual layout

The advanced layout path supports:

- Horizontal mixed-script flow, including run changes inside the same composition.
- Vertical right-to-left columns (`vertical_rl`).
- Vertical left-to-right columns (`vertical_lr`).
- Practical upright handling for CJK glyph clusters and rotated ASCII alphanumeric clusters.
- Newline-driven column breaks.

This is a practical vertical compositor, not yet complete CJK typography. Full OpenType vertical alternates (`vert` / `vrt2`), script-specific punctuation positioning, ruby annotations, kinsoku line breaking and a comprehensive grapheme/shaping engine remain open.

### Text on paths

Supported path modes:

- `circle`: closed circular path with wrapping.
- `arc`: open arc.
- `custom`: polyline authored as normalized canvas coordinates (x/y from 0 to 1), up to 64 points.

Glyph clusters are placed along a cached path-length sample and rotated to follow the local tangent. Path generation and placement happen in the background raster job; the path is not rebuilt every render frame.

### GPU-side animation

Existing modes remain available: type-on, word/column reveal, line wave, jitter, crawl and signal glitch.

E1 adds:

- Reverse typewriter reveal.
- Dissolve.
- Flicker.
- Character-cell displacement.
- Vertical reveal.
- Scattered glyph-cell movement.
- Segmented collision-style movement.
- Mechanical scrolling.

These modes use existing compositor uniforms and the text texture. Motion-only edits do not invalidate the static text raster or enqueue a CPU raster job. The modes are deterministic functions of texture coordinates and the renderer's animation clock. Text scrolling and mechanical scrolling shift the source through the layer viewport without wrapping the opposite texture edge into view; displaced samples outside the valid texture region are alpha-clipped rather than clamped into stretched edge glyphs.

**Important implementation boundary:** The new E1 animation modes are texture-space/grid treatments. They do not yet provide one GPU instance per glyph. "Character displacement", "scattered glyphs" and "word collisions" are therefore visual approximations, not independent glyph-body simulation. Likewise, reverse typewriter and vertical reveal are wipes over the text texture, not per-character event schedules.

## Pipeline and performance contract

1. UI edits update an editing buffer and committed, normalized layer settings.
2. Text content, rich-run shaping, vertical layout and path placement are captured in an immutable settings snapshot.
3. The shared `GeneratorRasterService` coalesces obsolete requests and performs CPU rasterization on its single worker. It does not create or mutate OpenGL resources.
4. A completed raster is accepted only when its revision and fingerprint are still current.
5. Each output renderer uploads the accepted pixels while its own GL context is current.
6. The compositor evaluates text animation uniforms every frame. It does not invoke the rasterizer for animation-only changes.

The existing raster-rate limit, preview quality, freeze and last-valid-texture recovery remain in effect. Preview and projector textures remain context-local.

## Not implemented in E1

These features require a different representation or an additional workflow; they must not be inferred from the E1 texture modes:

- GPU glyph atlas plus per-glyph instance data.
- Independent per-character position, rotation, scale, alpha and velocity.
- Per-word and per-character start/end timing tracks.
- True glyph-level typewriter, dissolve and entrance/exit scheduling.
- Deterministic character/kanji substitution using a preloaded glyph set.
- Real word-to-word collision/physics.
- Text-fragment emission into Particle System 2.0.
- A dedicated text-only feedback send/return. E1 text is part of the ordinary composition and can enter the existing master feedback path.
- Named, saved typographic composition presets.

## E2 — Glyph-level animation engine

Recommended next slice:

- Build a bounded per-output glyph atlas with stable glyph keys and a texture/SSBO-compatible instance representation appropriate for the project's OpenGL 3.3 target.
- Keep shaping, glyph discovery, atlas packing and text-to-instance generation off the frame loop; update instance data only when content or layout changes.
- Animate glyph transform, alpha, colour and timing in the vertex/fragment shader using a shared clock.
- Add independent character and word schedules, entrance/exit curves, vertical writing reveal, scatter/reform and real deterministic glyph replacement.
- Define explicit fallback for missing glyphs and atlas-capacity overflow.
- Set hard limits for glyph count, atlas dimensions and per-output memory; expose diagnostics and predictable degradation.

E2 should retain a baked-text fallback for text with unsupported shaping/features, and must not create a Python/Qt object per glyph per frame.

## E3 — Presets and typographic signal routing

- Save/load named typographic compositions including runs, writing mode, path and animation configuration.
- Add an explicit text feedback send/return or feedback source selection, with bounded history and per-output ownership.
- Allow text fragments or selected glyph events to drive Particle System 2.0 and modulation targets without coupling their lifecycle to the text editor.

## Acceptance checklist

### Static layout

- [ ] Rich run arrays save, reopen and preserve styles, including Japanese/English mixed runs.
- [ ] Plain-text layers without runs remain backward-compatible and visually unchanged.
- [ ] Empty plain-text field with non-empty rich runs still renders.
- [ ] Vertical RL/LR layout handles kana, kanji, punctuation, Latin words and line breaks without clipping or invalid font state.
- [ ] Circle/arc/custom paths handle short and long text, including wrap/clipping behaviour.
- [ ] Editing rich-run JSON with invalid syntax reports a recoverable UI error and retains the last valid texture.

### Animation and integration

- [ ] Every text animation mode can be selected, changed live and saved in a project.
- [ ] Animation-only changes do not start a raster job; content/layout changes produce one coalesced background job.
- [ ] Preview and projector receive identical settings while keeping separate GL texture resources.
- [ ] Text participates in existing layer effects, transforms, blend modes and master feedback as expected.
- [ ] Rapid edits do not allow stale raster completions to replace a newer text revision.

### Target-machine validation

- [ ] Shader compilation on the target Windows GPU.
- [ ] Fullscreen projector, resize, preview/projector independence and sustained animation.
- [ ] Rich Japanese/English, vertical writing and custom paths at High/Maximum raster quality.
- [ ] 4-deck composition with multiple text layers, other generators, layer FX and master feedback.
- [ ] AUTO PERF / Modulation Matrix changes text motion speed, amount and reveal-step density without requesting a CPU raster every frame.
- [ ] Record FPS, render time, upload time, raster duration and dropped frames.

Static compilation/lint CI does not satisfy the target-GPU checklist. Until that rehearsal is performed, E1 should be treated as implementation-ready for review rather than hardware-validated.

# M6 — Live Performance Timeline

This is subsection C of the separate **M6 — Advanced Performance Controls** workstream. It is distinct from M6-C Advanced Visual Transformations in the broader Advanced VJ Environment roadmap.

**Implementation status:** Merged to `main` in [PR #31](https://github.com/ilyaminineli/eli_lab-av-translator/pull/31), merge commit `c9b9f884`. The Performance Macro System is merged in [PR #30](https://github.com/ilyaminineli/eli_lab-av-translator/pull/30) and is used by the timeline's modulation events. Target-Windows musical rehearsal and projector acceptance remain open.

## Purpose

The Live Performance Timeline is a saved, musical event plan that runs alongside the existing internal or Sonic Pi transport. It adds deliberate structure to a show without replacing AUTO PERF or the current generative variation system.

Events are positioned by **bar and beat**, not by video frame or wall-clock timestamp. A show can contain section and phrase markers as well as actions that recall scenes, control decks, change effects, regenerate text, change palettes, drive Performance Macros and cue transitions.

The timeline is an application control-plane service. Clock/network workers only deliver validated events; event actions run through the application tick on the UI thread. They reuse existing deck, scene, EffectSettings, generator, palette and macro APIs.

## Musical position and playback

Each event has:

- A 1-based bar number.
- A 1-based beat number (1–16, checked against the active meter at playback).
- An event type, display label, JSON payload and enabled flag.

The timeline is limited to 512 events and bar positions up to 1,000,000. Events at the same bar/beat execute in their authored insertion order. Events are one-shot during a pass. Rewinding/restarting the transport makes later events eligible again; disarming stops event dispatch without deleting the plan.

### Internal transport

The existing InternalTransport emits bar and beat events. The timeline consumes those positions on the normal application/UI tick. Arming while stopped prepares playback from bar 1. Arming during a running internal show starts from the current position and waits for the next musical position, so it does not unexpectedly replay the current cue.

### Sonic Pi transport

The existing `/eli_lab/v1/clock/bar` message reports a bar index, BPM and beats per bar. The current SONATA integration sends a bar clock rather than one OSC message for each beat. Between bar messages, AVTranslator interpolates the beat position from the last received bar timestamp and the reported BPM using the monotonic application clock.

This is musical-clock interpolation, not an exact hardware/MIDI clock or frame-sync guarantee. Event dispatch is bounded by the application tick cadence. A fresh bar packet is expected at least once per bar; timeline interpolation is suspended when the most recent bar packet is older than approximately 1.5 bars. If a timeline is armed before the first external bar packet, the first packet establishes the current song position. Earlier events are treated as elapsed rather than fired as a burst.

Projects persist the event definitions, not the armed state or playback cursor. Opening a project or performance set never starts a timeline automatically.

## Event types

| Event | Behaviour |
| --- | --- |
| `scene_marker` | Descriptive section marker such as INTRO, PEAK or BREAKDOWN. Publishes a marker event and updates the timeline status; it does not recall a VJ scene. |
| `phrase_marker` | Descriptive phrase marker at an authored bar/beat position. |
| `scene_recall` | Recalls an existing VJ Scene Bank scene, with an optional numeric morph duration. |
| `clip_trigger` | Operates one of the four video decks, or loads a media-library asset into the selected deck and applies the requested action. |
| `effect_change` | Applies an existing master effect preset and optional whitelisted EffectSettings overrides. |
| `text_regenerate` | Generates new Text Art content using the selected layer's saved language, theme, count and dictionary settings. Can address a specific Text Art layer, or defaults to the first unlocked Text Art layer. |
| `palette_change` | Applies a named palette to unlocked generator layers. |
| `modulation` | Sets one normalized Performance Macro (0–1) for a specified number of bars. The macro's assigned continuous source can resume after the manual hold. |
| `transition_cue` | Recalls an existing VJ Scene with a configured numeric morph duration. Discrete media/text/generator changes retain the scene bank's current cut policy. |

### Payload examples

The timeline editor shows a type-specific hint and a JSON payload editor. These are representative event payloads:

Scene recall:

```json
{"scene_id": "intro-scene", "morph_seconds": 0.0}
```

Load a media-library asset into deck A and start it:

```json
{"deck_id": "deck_a", "action": "play", "asset_id": "media-asset-id"}
```

Change feedback controls:

```json
{
  "preset_name": "Digital Damage",
  "settings": {
    "feedback_enabled": true,
    "feedback_amount": 0.68,
    "feedback_decay": 0.94
  }
}
```

Regenerate one Text Art layer:

```json
{"layer_id": "text-layer-id", "seed": 20261113}
```

Change palette:

```json
{"palette": "Fuji · 藤"}
```

Drive CHAOS for four bars:

```json
{"macro_id": "chaos", "value": 0.82, "duration_bars": 4}
```

The clip action can be `load`, `play`, `pause`, `hold`, `release`, `restart`, `stop` or `seek`. Supplying an `asset_id` first loads that asset into the selected deck. The current VideoDeck.load implementation autostarts its decoder; use the subsequent deck action to pause/hold/stop as required.

Effect changes accept only known EffectSettings fields and validated enum values. They do not permit arbitrary application attributes or renderer objects.

## Generative variation alongside the timeline

The timeline is intentionally additive. AUTO PERF and the Modulator Bank can continue to produce generative variation while the timeline places structural cues around it. For example, a timeline can mark a new section, recall a known composition, change a palette, trigger text regeneration and push a Performance Macro to a new intensity; AUTO PERF can continue making its own interval/bar/phrase-aware decisions inside that section.

A marker by itself does not change automation style or lock a section's appearance. Use scene recall, effect, palette, text or macro events when the show needs an explicit state change. Manual deck locks and layer locks remain respected for the corresponding actions.

## Authoring surface

The **LIVE PERF TMLN** dock provides:

- A sorted bar/beat event list with event type and label.
- Enable/disable checkboxes.
- Bar, beat, event type, label and JSON payload editing.
- Add, update and remove actions.
- ARM / DISARM and REWIND.
- An insertable eight-marker example structure matching bars 1, 17, 33, 49, 65, 81, 97 and 113.

The editor intentionally exposes payload JSON for the first increment instead of adding a large number of type-specific forms. It validates the complete event before saving it and shows type-specific payload guidance.

## Persistence and safety

- Definitions are stored under `app_state.performance_settings.performance_timeline` in the existing project payload.
- Performance sets include the timeline automatically because they reuse the project snapshot.
- Event count, bar/beat, payload size/depth, identifiers, numeric ranges, effect fields, macro IDs, deck IDs and palette names are validated.
- Missing scenes, media assets, decks or Text Art layers produce a skipped-event result rather than terminating timeline playback.
- The cursor and armed state are runtime-only and are not restored from a saved project.
- Timeline actions use existing APIs; they do not directly allocate GL resources or issue renderer commands.

## Current boundaries

- The first increment is bar/beat based. SMPTE timecode, arbitrary millisecond positions, frame-accurate external clock and per-frame authoring are not implemented.
- Sonic Pi beat positions are interpolated between bar packets using the last received BPM. The current protocol does not send every beat as a packet.
- Scene recall reuses the existing scene morph/cut behaviour. Dual-scene crossfades, midpoint switching and fade-through-black are not implemented here.
- Phrase markers are user-authored labels at bar/beat positions; the timeline does not infer musical phrases from audio.
- The timeline can coexist with AUTO PERF, but does not yet provide section-scoped automation profiles, nested timelines, conditional branches or generative probability rules per event.
- Target-Windows live musical rehearsal, full SONATA timing, deck/media stress and projector acceptance remain manual validation work. A successful compile/Ruff workflow does not replace those checks.

## Acceptance checklist

- [ ] A timeline can be authored, saved, reopened and edited without resuming playback.
- [ ] Internal transport triggers bar/beat events once and in stable authored order.
- [ ] Sonic Pi bar packets establish a timeline position and beat interpolation advances between bars.
- [ ] Arming mid-show does not replay earlier cues; transport restart/rewind enables a new pass.
- [ ] Disabled events do not execute.
- [ ] All nine event types validate payloads and execute through the application thread.
- [ ] Missing scene/media/layer references are reported and do not stop subsequent events.
- [ ] AUTO PERF and macro sources continue operating alongside the timeline.
- [ ] A representative 113-bar show is rehearsed on the target Windows machine with scene, deck, effect, text, palette and modulation events.
- [ ] Timing, late-packet behaviour, manual lock handling, UI responsiveness and projector output are recorded during acceptance.

# M6 — Live Performance and Workspace Integration

## Status

Implemented on `m6/auto-performance-live-particles-4x3-queer-pools`. This follow-up connects the merged C1/D1-D2/E1 capabilities to the existing AUTO PERF and modulation systems. Python/ruff and target-Windows GPU validation must be recorded independently; static checks do not establish shader or projector acceptance.

## A. AUTO PERF coverage

The existing per-layer modifier engine and global Modulation Matrix remain the routing foundations. New parameters are registered with bounded target ranges rather than added as special-case animation code.

### Per-layer targets

- Particle System 2.0: continuous emission rate, particle radius, lifetime, speed, spread, turbulence, force strength, trail persistence and source-reformation strength.
- Text Art shader motion: speed, amount and reveal-step/column density. These are compositor uniforms; layout and glyph rasterization remain outside the render loop.
- Per-layer FX: mix, monochrome, invert, threshold, posterize, hue, saturation, contrast, brightness, scanlines and chromatic aberration.
- Existing layer transform, opacity, generator and animated-overlay targets remain available.

The global Modulation Matrix also includes bounded numeric targets for C1 master transforms, displacement and feedback: transform mix, kaleidoscope controls, mosaic tile count, pixel-sort amount/threshold, edge extraction, dithering, displacement amount/scale and feedback amount/decay/zoom/rotation/translation/colour shift/distortion/motion warp/datamosh/delay. The new defaults use beat, onset, phrase, energy, cutoff and audio-band sources.

Discrete choices remain operator decisions. AUTO PERF does not select a transform mode, choose a displacement source, toggle temporal feedback, freeze history or issue a feedback reset. Numeric routes take effect when the corresponding effect is enabled by the operator.

## B. Particle System 2.0 as a live instrument

### Continuous emission

Particle System 2.0 now exposes a bounded emission rate from 0 to 3000 particles per second, defaulting to 600. A deterministic gate in the fixed-step GPU simulation distributes births over time rather than starting the complete population as a one-shot burst.

The requested rate is divided by the number of independent populations. Emission uses dead/available particle slots, so the existing per-system and per-output limits remain authoritative; no unbounded CPU or GPU allocation is introduced.

### Event routing

AUTO PERF can shape live emission and motion with:

- Energy and beat pulses → emission rate.
- Onsets → speed and force accents.
- Low-frequency energy → force strength.
- Cutoff → turbulence.
- Phrase energy → trails and source reformation.
- Beat/downbeat → particle radius.

The editor reflects live modifier values, but pauses its slider synchronisation while a control has focus or is actively dragged. Changes are applied to simulation uniforms without recreating particle state.

### State continuity

The compositor keeps a particle-system instance resident for up to six seconds after its layer becomes temporarily inactive. This is intended for short cuts, brief deck/layer changes and automation transitions. Removing the layer, a render failure, output-context teardown or expiry still releases the GPU resources.

Resource limits remain four active systems and 16384 particles total per output, with at most 8192 particles per system. Preview and projector own independent simulation state in their respective GL contexts.

## C. Wide and 4:3 workspace layout

The main Qt workspace now distinguishes compact layouts by window width and aspect ratio. Its default dock layout uses narrower side columns and a shorter deck region on compact/4:3 windows, and it relaxes dock minimum sizes so the central composition editor remains usable.

The initial window geometry and minimum size are bounded by the available primary-screen area. User-saved dock arrangements are preserved; responsive rebalancing is applied to the built-in default layout and after the operator restores that default.

This changes the editor workspace, not the saved composition dimensions. The central PERF preview is framed at 16:9 even when the surrounding editor uses a compact or 4:3 layout. The compositor's existing `canvas_fit_scale` keeps the project canvas at its configured aspect ratio and letterboxes it into an output whose aspect differs. It does not stretch content or silently rewrite a 16:9 project to 4:3. Fullscreen output on a 4:3 display therefore keeps a 16:9 image with letterboxing. A separate per-project canvas-aspect selector remains future work.

## D. Queer text pool and dictionary hygiene

Text Art adds a selectable **Queer / クィア** theme in English, Japanese and bilingual modes. Its curated vocabulary includes the word **QUEER**, gender-expression and identity language, pronoun terms, chosen names, chosen family and short self-definition phrases.

English words read from repository dictionary files pass through an additional normalization and denylist check before they enter the random pool. The explicitly curated pool is separate and retains **QUEER**. This filter is a defensive safeguard, not a guarantee of exhaustive moderation: local dictionary files remain editable and should continue to be reviewed by the project maintainer.

## E. Acceptance checklist

### Static / integration checks

- [ ] Python 3.12 compileall passes.
- [ ] Ruff passes.
- [ ] AUTO PERF default installation preserves existing custom routes and modifiers.
- [ ] All new modulation target IDs have a matching getter/setter and bounded target specification.
- [ ] Numeric master targets are included in the MIDI learn value snapshot.
- [ ] Continuous emission rate normalizes to 0–3000 and is divided across 1–4 populations.
- [ ] Queer theme survives project settings normalization in all language modes.
- [ ] Existing dictionary files cannot reintroduce known offensive English headwords through random text sampling.

### Manual Windows / GPU checks

- [ ] Test emission at zero, low and high rates over several particle lifetimes.
- [ ] Check that rate remains consistent when population count changes.
- [ ] Confirm beat/onset/energy routes alter emission and motion without resetting the system.
- [ ] Hide/show or cut a particle layer within six seconds and confirm simulation continuity; remove it and confirm cleanup.
- [ ] Enable each master transform / feedback mode and verify its AUTO PERF values are visible and musically stable.
- [ ] Verify per-layer FX automation when layer FX are enabled; confirm disabled FX remain bypassed.
- [ ] Confirm text motion and reveal-step targets update without repeated CPU raster jobs.
- [ ] Run text scrolling and mechanical scrolling through multiple loop boundaries; no wrapped edge glyphs or out-of-bounds smearing should appear.
- [ ] Test default workspace and restored custom layouts at 16:9 and 4:3 resolutions.
- [ ] Verify the project canvas is letterboxed, not stretched, when output aspect differs.
- [ ] Check Queer, English, Japanese and bilingual dictionary sampling against maintained repository dictionary files.
- [ ] Run four-deck playback plus Particle System 2.0 and feedback at the target projector resolution; record FPS, GPU memory and dropped frames.

Static CI is necessary but does not replace these target-Windows, OpenGL and projector checks.
Agreed. And I want to correct one thing from my previous proposal: **I would not create a separate M5 Legacy mode.** That would preserve the very division we are trying to eliminate.

What you are describing is a single visual instrument that becomes more sophisticated without becoming more predictable.

The chaotic visual language of the first build should become the foundation of the new director, not an optional effect that can be switched on.

# **M7 — Unified Generative Audiovisual Instrument**

Proposed governing direction

**Core objective:** Combine unrestricted visual composition, intelligent musical direction, procedural graphics, advanced image processing and a professional live-performance environment.

The application should be capable of producing extremely chaotic images while retaining intelligent control over musical progression, transitions, visual density and performance structure.

## **1. One visual engine, three interacting principles**

I would replace the idea of separate visual behaviours with three continuous principles.

[André Chi Sing Yuen: eine kosmopolitische Perspektive zwischen eurasischer Tradition und der Modernität der digitalen Kunst](https://images.openai.com/static-rsc-4/-yUpsDnyILEEOi1NDSSHxYg2IRFXfe89JbJRVPYnq5jkLFmJi3rYPcwcZ5gEGGHJf5culSMXBxvbr4seqPGl7G8g_67h5vs8elOsGLz_g6ItSNqEfQ4CEELAdkfdLSB04nvXmfSXmJXNL2WGMJlObuhyl7v2rwKUbKeDmh2upaY?purpose=inline)

**CHAOTIC — Visual freedom**

Unrestricted spatial composition, overlapping video, displaced layers, randomized typography, abrupt cuts, distortion, feedback and visual collisions.

Its purpose is to generate unexpected results.

[Piano. Interactive, audio-reactive 3D typography :: Behance](https://images.openai.com/static-rsc-4/qDl3Kv9fBgzplssutBME8z8u75DbSb8_eHpzFlClDjeTcbH1Oza4opCsa0V7CMNQ71RuPrRiQP015CFbxnzpbw9CF0MoV_w00QTWYBXVTS56pHz1vfgqzv1fyLw09TQ5znrq2PSwpX6KvhmmkK6SYW5VUNxFJDT9gneAYOyBtSs?purpose=inline)

**GENERATIVE — Intelligent decisions**

Musical context, energy, phrase awareness, procedural variation, visual memory, adaptive layer selection and performance macros.

Its purpose is to make unexpected results meaningful.

[OpenProcessing - Creative Coding for the Curious Mind](https://images.openai.com/static-rsc-4/6NKbLC9MvZ0EwZLwV_NZLjNpG5SRqpWkj5u4YNXT7sf1sxhN9T2e0NZ4guaSSDzBkHcHLK6DoQ31lsZj_hlFNJmDWDUUI9p8LgLsJaf1a_fmbuKoh7escCsK2cJcoqnfAVZDGVUVUsa3vEt46NxHZVAtM4MWrT1na4nBIG9pTRU?purpose=inline)

**STRCD — Compositional intelligence**

Visual anchors, recurring motifs, restrained transitions, deliberate negative space, palette continuity and temporal pacing.

Its purpose is to provide direction without suppressing experimentation.

These are not three independent engines. They are three influences on the same decision-making system.

### **How they should interact**

Consider a musical performance:

| Musical section | Director behaviour                                                                 |
| --------------- | ---------------------------------------------------------------------------------- |
| Intro           | Establish visual motifs, but allow unpredictable composition                       |
| Development     | Increase layer interaction, movement and variation                                 |
| Pre-peak        | Increase density, spatial chaos and temporal activity                              |
| Peak            | Allow full-canvas collisions, aggressive feedback, text and particle interventions |
| Breakdown       | Reduce activity, but retain occasional unexpected visual events                    |
| Outro           | Gradually resolve visual elements, without necessarily returning to a clean layout |

The important part is that the director should understand the overall musical structure while being free to generate unpredictable images inside it.

A breakdown should not automatically mean a neat, minimalist composition. A peak should not simply mean maximum saturation.

The director needs to make decisions based on the actual composition, recent changes and musical context.

## **2. Remove artificial restrictions from the current architecture**

This is where I would concentrate the initial M7 engineering work.

I inspected the current `core/automation.py`, `core/generative_director.py` and `ui/automation_panel.py`.

These are the changes I would make:

| Current limitation                        | M7 direction                                                       |
| ----------------------------------------- | ------------------------------------------------------------------ |
| Maximum two layers per variation          | Dynamic selection across all eligible layers                       |
| Mandatory preservation of an anchor       | Optional anchor with adjustable persistence                        |
| Six predefined layout patterns            | Continuous spatial composition and probabilistic layout generation |
| Video-only automatic layout changes       | Video, text, geometry, particles and overlays participate          |
| Primarily smoothstep layout morphing      | Multiple transition behaviours operating together                  |
| Fixed variation intervals                 | Adaptive intervals informed by music, density and visual activity  |
| Restricted rotation and positioning       | Full transform freedom, including off-screen placement             |
| Limited independent layer interaction     | Relationships between multiple layers                              |
| Randomized effects after transitions only | Configurable and context-aware effect mutation                     |

There should still be resource budgets for rendering, decoding and GPU allocation. Removing visual restrictions does not mean removing technical safety limits.

### **The more intelligent alternative**

Instead of `max_layers_per_variation`, introduce a dynamic variation budget.

The director can decide whether to modify one layer, several layers or the entire composition based on:

- Musical energy and section.
- Current visual density.
- Number of active layers.
- CHAOS and FRAG macro values.
- How recently each layer has changed.
- GPU and rendering performance.
- Operator-authored locks and priorities.

An anchor becomes a probability or persistence preference rather than an enforced rule.

The layout engine should also be able to create relationships between layers: shared centres, overlapping transforms, opposing movement, nested geometry, synchronized rotations and deliberate collisions.

This produces organized chaos rather than merely random object placement.

# **3. M7 visual instruments**

I want to retain all five instruments from your original plan. They should become first-class parts of the application's composition system.

## **A. Generative Drawing Engine**

High priority

[Geometric spiral pattern on a black background.](https://images.openai.com/static-rsc-4/ICzvwFwix30e5iZBwHANsRfq7eEvPdbZNzameEoafG-fjfvfsqKuPIMouvK1AX3IO0J_Y06TQS5WLm_1iWBzC2egB3UJkx3GFOaxCuqVZZPdNYDiz4Zlns3trhFlGiQFHEH-Lt9dSfCuHuT4vKmu94Wd7AfDWoWQnULqNSowinyesXKnJ-cxHWAhxhR7-Zwo?purpose=inline)

[sketch_220810c :: Behance](https://images.openai.com/static-rsc-4/FR0VBBBcyvVbVu-5kWaBKM4iTuvuUJzA0xF8tDiaJB1W97YIg23Obm8JXvIVHbuK0p-o78cUf9V4-4VGnlvhSpUqj6GhrLO5fwYKky7ItCkjTac7wKqbs675zbwDfcHYri-WPRO7fJ0YD0-iqTC59tHr-3FEV3AzxJVwLhRPYdk?purpose=inline)

[Fork: Curl Noise by rupertxrussell | Turtletoy](https://images.openai.com/static-rsc-4/dRBJs7CvgX16xS5UjgfEPSxGBkfeCEHx_f6yQaj87238BX75buOMIHbR3OWtTUJEI4Jmcw89H03v3wGTqrGGT64OgksT72F0BOq1DsOOOHpDx7XXSqYSAA7kL02r3k7w-D5sJW5fXmtbDGtn8YJriRcUs8lInQQAn_QGYmfc0lY?purpose=inline)

15

This should be a new procedural drawing instrument, not another variation of the existing Geometry generator.

**Proposed capabilities:**

- Bézier curves and editable vector paths.
- Animated stroke reveal and drawing sequences.
- Persistent line accumulation.
- Procedural hatching and crosshatching.
- Recursive geometry and branching structures.
- Contour generation from video, images and procedural sources.
- Spiral, radial and field-driven constructions.
- Distortion of paths using noise, audio and vector fields.
- Repetition, symmetry and geometric subdivision.
- Independent stroke width, colour and opacity.
- Dynamic path generation and seeded reproducibility.

The interesting part will be allowing drawing to interact with the footage and other generators.

For example, a video frame could generate contours, which then become a set of animated paths. These paths could accumulate over time, distort under audio modulation and eventually feed into the feedback engine.

**Implementation recommendation:** keep path authoring and procedural geometry generation outside the frame loop. Render the resulting data through a dedicated GPU instrument.

## **B. Temporal Feedback Engine**

Existing M6 foundation — extend

[Das ist das Feedback, 2024 von Steve Pavlovsky: Kunstdruck](https://images.openai.com/static-rsc-4/N0teVnJjuYPj0XAF5h2DhTVlg3CMBhZ4KOhOlH6XdheR2WFzaRAjHZAZ1LuIUTotV5shR125ZzqoD6qmiCrdqtfKuDlfy7Pwr2yCQdYs_EERJ4_pU5AdqO35KrhSxpywtGktWPEOpAU3taufiY0SRZzegsmr4wHJaUg6qFVQ3gM?purpose=inline)

[pixel sorting Glitch](https://images.openai.com/static-rsc-4/Vqcc2yYkrhsW0yF35-4sOs7i_Z6Jag1rgHg844RwdvkrnY33eH00aDdW2fQ8BU3zWM32hDX3dBIYAkKlGaoeEY9bmKdsHGMg4QDRTQ5PcXREBo8Csom9lNsnVugwHUBHpiSvbk9WP7o3zb0LNiULJdd8SsmSY1RGgDefdh1ChsWyOs6iwOX4damsiocFH-lE?purpose=inline)

[Glitch Video Synthesizer -VANDALIZER-MEZKALIN- Circuit Bent Video Processor, Analog Video Synth, Video Enhancer - Etsy](https://images.openai.com/static-rsc-4/SmRTl0bNCp4Wyk_RPCQqyOKPNYxfdTy42-8oYXWmPs0ZBcAe6I_81jXAIB_e493ylb9IZZa7XoaHUTDINqkvKjbjZqVTGOcN4etluAdFYiOnSaHE4WWswjtZ9yqMcU9mUy7FvB1sGCjxecWAAoM2K2J7BiEd308y5PdccphSGU4?purpose=inline)

14

We already have an important foundation in `rendering/feedback.py`.

I would not replace it or create another feedback renderer.

The current M6 implementation has a five-texture history ring, feedback transformations, decay, colour shifts, motion-driven warping and datamosh-style blocks.

M7 should make this visual memory much more expressive.

**Proposed additions:**

- Multiple independently controllable feedback sources.
- Layer-specific feedback send amounts.
- Text-only and generator-only feedback routing.
- Independent feedback transformation chains.
- Recursive zoom and rotation combinations.
- Accumulation and decay envelopes.
- Frame stutter and temporal echo behaviour.
- Feedback modulation by audio bands and Performance Macros.
- Selective feedback freezing.
- Scene-specific feedback states.
- More elaborate temporal transitions between source images.

A particularly interesting possibility is allowing the drawing engine to receive feedback from the compositor, then use that feedback as an input for another round of drawing.

That creates a recursive relationship between images and procedural graphics.

The feedback implementation must remain bounded and GPU-native. Preview and projector must continue owning independent rendering resources.

## **C. Advanced Signal Visualizer**

[CEC — eContact! 19.2 — Vector Synthesis: An investigation into sound-modulated light by Derek Holzer](https://images.openai.com/static-rsc-4/VfC4444f_YHYfY0RATYnkNDWOat30DPTNHhjJV8g8Y99BLnJIDSggA80l3Q52vhCWmZrh33agBqcTznWQj0oPo9uuwQSrqXt-kqBwffeZQOShOJVLeD4uBCyyeWGAzyYCNsGg0m_Auxmu5sB-07uvaK4hLIJpkk9BOxujnDJGLs?purpose=inline)

[Making a spectrogram with Geometry Nodes — Blender Conference 2025](https://images.openai.com/static-rsc-4/OZMEXv4MqMqXrXMa4-Wpwi4KDJrRbOwh10NQ7uOnPdH83ZSPaAOUmtKwaC-IrIo6WtHkYHMvBjzauojLydWEJ3f9PyrsCI9fWHFLeBV4KP2c3snyuQHSsrKw3D0NS8lVGOST2y1i9RF4f4st442lliVA68QvUCskM_8CPMQIqcU?purpose=inline)

[Sound Visualizer :: Behance](https://images.openai.com/static-rsc-4/MElBoBEmThFySal_8NE3G_1VEVvs5-ar2lff1HTi6L65TdJ8xF5j1-CRdkMgvabbcs9CgTCwIW-izji4Rf4nultzal0bMGb66dTIqLAV4qyQbfMku-bXCsYwmhu1atPGev71NC30xCKQWpgl_5PTMd7csfGkSDxsVP3UaExBo-s?purpose=inline)

16

This should evolve beyond the current waveform generator.

I would introduce several visual instruments:

| Instrument         | Function                                               |
| ------------------ | ------------------------------------------------------ |
| Oscilloscope       | Time-domain waveform representation                    |
| Phase Scope        | Stereo phase and Lissajous visualization               |
| Spectrogram        | Frequency history over time                            |
| Frequency Geometry | Geometry generated from spectral data                  |
| Spectral Particles | Emission and motion driven by frequency bands          |
| Signal Field       | Spatial fields driven by audio signals                 |
| Wave Deformation   | Geometry deformation driven by amplitude and frequency |

The important architecture decision is to use the existing audio-analysis and modulation foundation rather than create a separate audio-analysis pipeline.

These instruments should also support non-audio sources: transport, Sonic Pi macros, modulation signals and procedural inputs.

For example, CHAOS could alter the geometry of a phase scope, while the low-frequency band controls its structural radius.

## **D. Procedural Printmaking**

High priority

[日和崎尊夫 木口木版画『殖』(日和崎尊夫) / アブストラクト古書店 / 古本、中古本、古書籍の通販は「日本の古本屋」](https://images.openai.com/static-rsc-4/T304N_jjtNAEo5Fvw9NHpSY9-PlyoSl9UdxNXJsni5YceQNRaebg-cMX6cWAa22yByWGBpMDb4zTGI9qiPCAvVgNVJkyn6a82HZIhIm7DYLx88CkWsd-F_hRurbXrauWwrCQGVlL6TAi7oJiJCuNtLkmhJjVaOc_GO8FeM5emlw?purpose=inline)

[Destroy All Monsters Magazine | 百年](https://images.openai.com/static-rsc-4/03_pbe3YC8y5FucDRNvzXnictuieuOQmPVJ2AsiBGudczU_lh2UdCGveHy0fwD10HByOvTHw208FELNXXo-4d9xbASS1XoSlFnEy9xSpL_d16_yTGgl90xobZSyXNUqJo20oxHmOyRqOkKj4nkYk1w9POE5CFBJITnwa3X0Be8k?purpose=inline)

[Abstract vector woodcut engraving undulating lines horizontal banner.](https://images.openai.com/static-rsc-4/D9w8bsX3yi6eHAPt_dqfiBwcuaQ_Tv1qR9fnk3Rb3dQPuLX4HspUZ2cySYGTgqUH1FWT_smJ99R4WXG0dN8BqFX9jMKa9aXpIuqpMzvSDWKObG2iZgjzsVuqT_2CNMGk70gQO5HyNtDmUbHj0MPl0O1xknc3ILcK7l1bx7tpxnI6JlrSmnJKld7ydA9ss0wK?purpose=inline)

17

This is particularly promising because it provides an entirely different graphic character from ordinary digital glitch effects.

**Proposed processing instruments:**

- Halftone.
- Xerox / photocopy.
- Engraving.
- Stochastic hatching.
- Crosshatching.
- Paper grain and paper texture.
- Ink spread and bleed.
- Print misregistration.
- Multiple ink plates.
- Threshold-based contour extraction.
- Ordered and stochastic dithering.
- Colour separation and channel offsets.

I would implement it as a proper procedural print-processing system rather than a collection of unrelated filters.

For example:

**Example printmaking pipeline**

Original video / drawing / text

Contour and tonal extraction

Halftone / stochastic hatching / engraving

Ink plates / misregistration / paper treatment

**GPU compositor and feedback**

The processing stages should be independently adjustable, reorderable and automatable.

Printmaking should also be available as a source for feedback, not just as a final image treatment.

## **E. 3D Visual Generator**

Research and architecture phase

[Warping the Grid :: Behance](https://images.openai.com/static-rsc-4/UmK_hFTsDoNrggHXtJQpOJhNNsxjvdK2Q69e96z0M5VCZnbb7O3cszZOuuNdtSYzub4eouWD_trHU5QHAwsDL4AeFvGFy8Lukz9I0zH81Ru8JUb3r-H7M3EDJSdva2RhQAoDQAccfEUL8dSjx8w3aOo342OH6sY9CFAm9sK3R9k?purpose=inline)

[The One Rule That Unites All Great Design: Foundation in Form & Structure | Bobr AI](https://images.openai.com/static-rsc-4/FqlR9VPhJxKCbkt-opT9DtUWp32p4SX67Dw9LN-6KDkAZtonps9cOuCcLTilRHQzCm_mTt7vpcP8K3MGMRM4iSv9_b2WhIdAldOkbAxHu-JCj6Tr48I173iSqr6AxZpJQtmJWO4I4SzE9ORozrmr5QGQrNNfvx5jvjWrz9HHqBQ?purpose=inline)

[Various TouchDesigner Animations :: Behance](https://images.openai.com/static-rsc-4/ZIh2pfdOE3V4WI4XMzzgCCWpHe7ko95mLFPq3vcxVZfhVAbetw8wsOoayGS-qH2REInkFhd4ZJIILCIQEnLsENoCYt1bwvA5ffRclD6sNI194y9O5Z5OjX18eKZ7QCnR3wtWjauS9kz1EMJ46LE05cpjvU7aZ-O92zaNa_PMNrk?purpose=inline)

16

I agree with your original recommendation: do not force a 3D engine into the existing 2D compositor.

I would create a separate rendering module with its own lifecycle.

Initial scope:

- Procedural meshes.
- Wireframe and solid rendering.
- Rotating geometric structures.
- Surface and vertex displacement.
- Instanced geometry.
- Camera position, rotation, zoom and projection.
- Basic lighting.
- Audio-reactive mesh deformation.
- Procedural materials.

The integration contract should allow the 3D renderer to provide an image source to the existing composition system.

Each output context must own its own rendering resources, just as the existing preview and projector renderers do.

I would begin with a technical proof of concept before committing to a full 3D feature set.

# **4. Performance Director — connect everything**

This is the most important architectural part of M7.

The visual instruments should not operate independently of the existing Performance Macros.

I would extend the six macros as the common control vocabulary.

| Macro    | Existing purpose               | Expanded M7 responsibility                                     |
| -------- | ------------------------------ | -------------------------------------------------------------- |
| CHAOS    | Glitch, rotation, displacement | Spatial freedom, mutation probability and drawing irregularity |
| DNST  | Tiles, geometry, particles     | Layer density, drawing complexity and spectral populations     |
| DPTH    | Transform and feedback         | Recursive geometry, spatial transforms and feedback intensity  |
| DEC    | Feedback and trails            | Ink persistence, trails, accumulated strokes and visual memory |
| PRESSURE | Contrast and distortion        | Thresholds, hatching density, ink treatment and deformation    |
| FRAG | Pixelation and displacement    | Layer fragmentation, typography scattering and temporal cuts   |

This should remain the existing normalized modulation architecture, not a competing second macro system.

I would also introduce a shared concept called **Visual Activity**.

The director could estimate the current activity of the composition using:

- Number of visible layers.
- Spatial overlap.
- Transform intensity.
- Amount of temporal feedback.
- Active particle and drawing populations.
- Effect-stack activity.
- Current transition activity.

It could then make decisions based on whether the image is visually underactive, balanced or overloaded.

That would make the director genuinely intelligent instead of simply increasing randomization whenever musical energy rises.

# **5. UI redesign — a proper VJ workspace**

This should become an explicit M7 workstream.

The existing interface has functional panels, but `MainWindow` currently organizes most of the application around Qt docks. The composition inspector occupies the central workspace, while the actual preview is another dock tabbed alongside performance controls.

That is not the ideal arrangement for an operator-first VJ application.

The adaptive 4:3 and compact layout work from M6 is worth keeping, but M7 should go further.

[Resolume Arena - Download - CHIP](https://images.openai.com/static-rsc-4/00U_a6TB_EbZ-_Y64PNpt-DQu9-FUJgJiVsDwbR5FVtghf8Wz7LKxN8OfaHeSSD600-y9NNGRM7gYVr4YDPws99Usriu79MDiLw_UmXkABjXxkgeRUO8q2Gxfj0RuoEMPlK6NKugZRWigXck3xHXgCr78578Pl5i8A__sYJ_VYk?purpose=inline)

[OP Snippets - Derivative](https://images.openai.com/static-rsc-4/C1Eja98DA_KTbloRDmIKbl6zvYjII9Qr3vRT0fS190WxR0blY8xE3Pgmo-Askqi0kSo5FI9LFX-rdQNFy-OTvd7dzdJE1bN9Tum9bPcpLxqDIcZ18T02K433Tnw3y7lV3Y4TBAXY7zWc08WYwAcWznJh5Rn69Sb1dN-179M4_h0?purpose=inline)

[Training – Resolume](https://images.openai.com/static-rsc-4/AFmFfYzmdZe9Z9mTkQcDwxsptRw2Zlp9HXd3IXLHpjDPoUDCs63oxlY3L_Vl-wThjrsmZzqcg67lkf8UdxVTwwV4_6B_0t2T-FidNwn7j-SX7UKhbX9oDDbVplW-7PggugeBwOvbzQ2fz_8vCd7CRJrx-Lj5cK-ptvdwmLug_Uw?purpose=inline)

11

I propose three application workspaces, with the performance workspace becoming the primary environment.

**01 — PERF**

Primary workspace

[Resolume VJ Software & Media Server](https://images.openai.com/static-rsc-4/kzt-yCxINwblaJtkIwNmLOiveTgSpOLf70VNcLdrRa8_FLjho43oosCwiWBi6I5xvSSGoha-P_P1qxuF_N4N7lFap83BJ6SVfJD1XzC8bP5FWdQ-QLS3dd0pF6Yq5Bw6I1bxXIg87RFULPcKGvgawrjl0AcjbUAP-4hsJ5who74?purpose=inline)

[resolume.com](https://resolume.com/?utm_source=chatgpt.com)

The central canvas should be large and immediately visible.

- Live preview / projector status.
- Video deck strip.
- Layer visibility and quick controls.
- Performance Macros.
- Visual activity and transport indicators.
- Timeline and scene triggers.
- Quick FX and generator controls.

**02 — COMPOSE**

[Notch | IBM’s Celebration of Innovation](https://images.openai.com/static-rsc-4/0wsT_Lk1BVogLIq7NIEOabZDMCzm5Awa6gsYVY9_EJ6Qh0BumDOLhsI_PeH-I4WV2B1Y1ASPMiHPXfNYao1fI2pIs_ZB0cX63DVVEgQc0hAPM21MbBSS0T7wLBCxeJHbOl_rkQNyXOruO05bZP2wDJZ-cvL6cMRQ_aPhBFOHgVU?purpose=inline)

[notch.one](https://www.notch.one/madewithnotch/ibms-celebration-of-innovation-notch-cognitive-in-motion/?utm_source=chatgpt.com)

Designed for creating and editing compositions.

- Central composition canvas.
- Layer stack and hierarchy.
- Generator and effect inspectors.
- Typography and drawing editors.
- Feedback routing.
- Visual assets and presets.

**03 — PREPARE**

[VJ.Tools Library | Prep with the music on](https://images.openai.com/static-rsc-4/xwA3sTv9KIBoiApnFmeUoL6QOxSpUS1XrT4flmll3Ik9kL68T0fUHRcotKgfhnQx8wU7n2HFbc96IPGNRL9Pnbroj_4sNsCP9W7PNnJlzYmWE96OHU6igEOcUhNIH3afFM15XR_6B99TN148zHH0Zr35cHoezQZewlx2g_4WS2s?purpose=inline)

[vj.tools](https://vj.tools/?utm_source=chatgpt.com)

Designed for preparing a performance.

- Media library and collection management.
- Deck assignment.
- Scene and composition banks.
- Performance timeline editing.
- MIDI / OSC configuration.
- Saved show configurations.

### **UI details I would prioritize**

**A. Context-sensitive inspector**

Selecting a text layer shows typography controls. Selecting a drawing layer shows path and stroke controls. Selecting video shows transform, blend and source controls.

No need to display every parameter for every layer.

**B. Quick controls versus advanced controls**

Every instrument should have an accessible quick-control surface and an expanded editor.

For example, the drawing engine's quick surface might contain Density, Chaos, Motion and Colour. Its advanced editor exposes path geometry, curve points, stroke accumulation and rendering settings.

**C. Performance control surface**

The six Performance Macros should be prominently accessible without opening a separate settings panel.

The timeline, musical position, active scene and section should remain visible during performances.

**D. UI consistency**

I would establish common component patterns for:

- Sliders and value displays.
- Colour selection.
- Layer selection.
- Effect chains.
- Generator parameter groups.
- Modulation assignment.
- Keyboard and MIDI mapping.
- Preset selection.

**E. Responsive layouts**

Keep support for 16:9, compact desktop and 4:3 projector-oriented screens. The interface must remain practical at different resolutions, without reducing everything to tiny controls.

Most importantly, the live canvas must never become a secondary element of the application.

# **6. Revised M7 development sequence**

Here is how I would organize the entire milestone.

## **M7 roadmap**

1. **M7-A — Unified Visual Director**

   Foundation
   - Fix the current automation runtime bug.
   - Remove artificial variation restrictions.
   - Introduce dynamic variation budgets.
   - Implement unrestricted spatial composition.
   - Introduce layer relationships and interactions.
   - Improve adaptive musical decisions.
   - Integrate all six Performance Macros.
   - Preserve the existing M6 systems.
2. **M7-B — Performance UI Redesign**
   - New Perform, Compose and Prepare workspaces.
   - Large central composition preview.
   - Redesigned performance surface.
   - Context-sensitive instrument inspectors.
   - Consistent component system.
   - Responsive layouts and persistent workspace states.
3. **M7-C — Generative Drawing Engine**
   - Vector and Bézier geometry.
   - Recursive structures.
   - Animated strokes.
   - Hatching and contours.
   - GPU rendering and procedural interaction.
4. **M7-D — Temporal and Visual Processing Expansion**
   - Extend M6 feedback.
   - Layer-specific feedback routing.
   - Temporal echoes and stutter.
   - Procedural printmaking.
   - Effect-stack integration.
5. **M7-E — Advanced Signal Visualizer**
   - Phase scopes.
   - Spectrogram.
   - Frequency geometry.
   - Spectral particles.
   - Audio-driven deformation.
   - Sonic Pi and modulation integration.
6. **M7-F — 3D Rendering Foundation**
   - Separate renderer module.
   - Procedural geometry.
   - Wireframes and meshes.
   - Camera system.
   - Compositor source integration.
7. **M7-G — Integration and Release Validation**
   - Project persistence.
   - Scene and performance-set persistence.
   - Full GPU resource testing.
   - Preview/projector consistency.
   - Long-duration performance.
   - UI and workflow validation.

The order is intentional: the Unified Visual Director and UI should come first because all the subsequent instruments need a stable way to participate in composition and performance.

# **7. Engineering rules for M7**

I would make these non-negotiable acceptance principles:

| Area          | Rule                                                                       |
| ------------- | -------------------------------------------------------------------------- |
| Rendering     | GPU-first, no unnecessary CPU image processing per frame                   |
| Architecture  | Reuse shared modulation, composition and rendering services                |
| Variation     | No arbitrary two-layer limit or compulsory anchor                          |
| Randomness    | Seedable, weighted, state-aware and musically informed                     |
| GPU resources | Bounded allocation and deterministic cleanup                               |
| Typography    | Keep static rasterization asynchronous                                     |
| Drawing       | Keep procedural geometry independent from frame-loop authoring             |
| Feedback      | Reuse the existing temporal history system                                 |
| 3D            | Separate rendering module and output integration                           |
| UI            | Operator-first, contextual, responsive                                     |
| Persistence   | All new instruments and meaningful parameters survive project/scene reload |
| Testing       | Regression tests plus actual Windows/GPU/projector acceptance              |

I would particularly emphasize **visual regression testing**.

The M5 screenshots should become reference compositions. M7 should be able to recreate their visual density and unpredictability while using the newer feedback, typography, particle, musical and modulation systems.

It should then demonstrate improvements beyond those original compositions, rather than merely reproducing them.

## **8. What M7 should ultimately achieve**

[Maximum the Hormone team with ATARASHII GAKKO! for fierce 'SHIMI' music video | Electric Bloom Webzine](https://images.openai.com/static-rsc-4/SNhIz1VtVa48tyzoJwOL5bgsP18DM-zM_byPHgLoQ1oQUP4FEts3J-PMTjrTkBFWK5GTYI35gokT8EpsEuxxk3BNAJ4yX6blbhCzpR-2zufBswWZcg-tpOOxTTtl1358OS2B-rcZfX8FX4UKuCnBOLLtvr7gCZERo2b4snf-FZo?purpose=inline)

[021022 :: Behance](https://images.openai.com/static-rsc-4/KwnifEpQFME-V7VcMxiEBql8HNeM7iklbFACgDSuTWjRhI28N21uFttDreaXQOQbBQHQN6Uqfb_xP0lfbATcJlBYUANCF5yrCaVeiIdz_CCoeAi4XXyVhJUQ9dhSnCoK8sigSqEGxuVLH7lpqnrUiWf4xzzQD0ysqr_ss4Oxxwg?purpose=inline)

[TOOL's Concert Visuals Are Super Trippy - Metal Injection](https://images.openai.com/static-rsc-4/riBsDhxHermUY456FhT2kjKohNmw6nD8kHeNhCibfD-cSxALkAwjt4nd3Q5sfVjXoNFnyIDGx_zic9kHJuHejNAKX2rBw-zoRDPhPecoFB538J7ILLgpVBZ4jzo2FDHQV66KsuYOmufmwxf5zhoTo72xXHUWMLKcSVP9eiTl3ZE?purpose=inline)

18

I think the final identity of eli_lab AVTranslator should be:

**A generative audiovisual performance environment where video, typography, drawing, particles, geometry, sound and temporal image processing are all part of one continuously evolving visual composition.**

Not a conventional video mixer with random effects.

Not a conventional generative art application.

Not a conventional audio visualizer.

It should combine all three into an instrument with its own aesthetic identity.

And there is one principle I would keep throughout M7:

**The director should understand the composition, but it should never be afraid to destroy it.**

That is the balance between Chaotic, Generative and Structured Hybrids that I would use as the governing design principle for the milestone.

---

# M7 implementation log

## M7-A — Unified Visual Director · initial code slice

**Branch:** `m7/unified-visual-director`

### Implemented in this branch

- Added a dynamic variation budget derived from eligible layers, musical drive, CHAOS, DNST and FRAG.
- Removed the two-layer selection ceiling from `GenerativeVariationDirector.select_layers()`.
- Made anchor and background-source preservation opt-in; retained serialized fields for old performance plans.
- Expanded spatial variation beyond video to visible/unlocked video, generator and overlay layers.
- Added higher-variance scale/rotation/opacity/blend choices, off-canvas placement, clustered overlap, and probabilistic abrupt transitions alongside morphs.
- Replaced the old two-step performance style gating with a unified director selection path.
- Fixed the misspelled `_select_variation_layer_ids` call.
- Changed AUTO PERF UI wording to describe one unified director and adaptive scope.

### Remaining M7-A work

- Add operator-authored per-layer priorities and explicit mutation categories to the adaptive selection budget.
- Extend Visual Activity with renderer-side feedback history, particle population, effect-stack load and active-transition telemetry.
- Add further regression cases for legacy project-plan migration, all synchronization modes, manual generator/overlay/FX edits and long-session stability.
- Complete target-Windows testing for live GPU composition, preview/projector parity, sustained performance and saved-show recovery.

### Validation status

At commit `ddbff4e`, the M7 branch passed whole-project Python compilation, targeted Ruff and all 16 regression tests. Interactive Windows UI, GPU preview/projector parity, long-duration rendering and packaged one-file acceptance remain manual release gates.

## UI technology decision — M7-B

The desktop surface remains implemented with Qt Widgets (`QMainWindow`, `QDockWidget`, `QToolBar`, and widget-based panels). The application now uses the native **Fusion** style with a project-owned QSS design system. There is no runtime dependency on Qt Material.

- Keep the existing Qt Widgets and OpenGL / ModernGL composition architecture. A styling pass must not change render-context ownership, layer state, preview/projector lifecycle or performance behaviour.
- Use a restrained monochrome palette shared with the website: `#090909` page/background, `#101010` raised surface, `#151515` inset surface, `#eeeeee` primary text, `#a3a3a3` muted text and `#303030` rules.
- Use the website-aligned typographic hierarchy without bundling fonts: Newsreader with Georgia fallback for English display headings; Yu Mincho / Noto Serif JP for Japanese headings; DM Mono with Consolas / Cascadia Mono fallback for uppercase action captions, group titles and metadata; Segoe UI / Yu Gothic UI for body and editable field text. Resolve families from the operating system.
- Keep monochrome control icons, generous workspace spacing, compact metadata and clear selected/hover/focus states. Advanced settings can be progressively grouped, but no existing performance or composition controls are removed.
- Preserve the existing OpenGL / ModernGL rendering widgets and output contexts; stylesheet changes must not alter render-context ownership or preview/projector lifecycle.

The first M7 shell remains PERF / COMPOSE / PREPARE tabs and existing Qt Widgets; the current visual redesign replaces the old dark-red base theme with the site's editorial monochrome system. More substantial inspector hierarchy and quick/advanced grouping are follow-on work, to be done without dropping functionality.

## M7-A / M7-B implementation update · 14 November 2026

### M7-A — Unified Visual Director

- The interval-driven and musical-event paths now use the same variation selection, layout mutation, generator variation and particle-peak services. The timer path is consolidated in `_tick_unified_time_events()`; the old internal method name remains only as a delegating compatibility wrapper.
- Dynamic variation scope combines eligible visible/unlocked layer count, musical energy/intensity/section, CHAOS, DNST and FRAG.
- Strong musical/macro drive can produce a global variation burst. The universal two-layer ceiling is removed.
- A first **composition-only Visual Activity** estimate measures layer count, approximate overlap, transform intensity, off-canvas amount and source diversity. It influences the dynamic variation budget. Feedback history, particle population and effect-stack telemetry are not yet part of this score.
- Spatial mutation now chooses relationship patterns: independent, shared-centre, opposed, nested and orbital placement. It retains seed compositions, but does not require fixed panels.
- The six M6 Performance Macros remain the shared modulation vocabulary. The director consumes existing macro values rather than introducing a parallel macro architecture.
- Anchor and background-source protection remain optional and default to off. Existing serialized fields are retained for compatibility.
- Added focused tests for uncapped layer selection, optional anchors, cross-source layout mutation, timer and bar paths, Visual Activity and relationship strategies.

### M7-B — Performance UI Redesign · first shell

- Added central **PERF / COMPOSE / PREPARE** tabs with persisted workspace selection and Ctrl+1 / Ctrl+2 / Ctrl+3 shortcuts.
- PERF reuses the existing live `PerformanceView` and displays the existing six-macro control group below it. The group is moved from the advanced control panel rather than duplicated.
- COMPOSE hosts the existing generator/composition editor.
- PREPARE contains central tabs for the footage library and visual asset library.
- Old preview/media dock shells are hidden after both fresh startup and saved-layout restoration; menu actions now switch to workspaces.
- The initial dark-red Qt Material base was replaced by a native Fusion stylesheet owned by `ui/theme.py`; the unused Qt Material package was removed from runtime dependencies and the PyInstaller collection.
- Added the editorial `e·` wordmark to the toolbar, increased workspace padding and replaced the application/executable icon with the matching monochrome serif mark.

### Validation boundary

The M7 branch workflow passed at commit `ddbff4e`: whole-tree Python compilation, targeted Ruff across the changed M7 modules and all 16 regression tests succeeded. This validates the automated code changes, not the interactive application. Actual Windows UI, GPU preview/projector parity, long-duration rendering, responsive-screen behaviour and the packaged one-file executable still require target-machine acceptance.

## M7-A final hardening slice · per-layer cooldowns and manual overrides

- Added a configurable per-layer cooldown (default 1.5 s; zero disables it). High musical energy, CHAOS, DNST, FRAG or peak sections shorten the cooldown, with a 120 ms floor.
- Dynamic selection now considers only visible, unlocked layers whose cooldown has expired and which are not under a recent manual override. A maximal musical peak can still reach every eligible layer; no two-layer cap is reintroduced.
- Automatic layout, generator, overlay, layer-FX and clip-switch mutations record the affected layer's last-change time.
- Existing application notifications for direct layer-property edits and selected generator/overlay controls now pause automation for that layer. A manual edit cancels an in-flight layout morph.
- Manual generator-parameter edits invalidate the cached peak-boost baseline. Ordinary transform edits pause particle automation but retain the baseline so temporary boosts can still restore correctly.
- Added five regression tests for adaptive/disabled cooldowns, layer eligibility expiry, manual-override precedence, layout protection and particle-baseline handling.
- The cooldown is exposed in AUTO PERF and serialized with the existing automation settings.

**Session boundary:** the current M7 implementation stops here. The drawing, printmaking, advanced feedback routing, signal-visualizer, 3D renderer and further workspace/inspector redesign remain for the next implementation session.

## M7-B UI continuity and localization slice · 14 November 2026

### Implemented

- Condensed the About dialog to the product name/version, one-line purpose, author and source link.
- Removed persistent instructional paragraphs from AUTO PERF, the macro and OSC panels, generator/overlay controls, the unified director, modulation editor, layer modifiers and media browser. Operational status and error feedback remain visible.
- Added a global hover-hint filter controlled from Settings. Tooltip text and accessibility names remain attached to controls and can be shown again by re-enabling hints.
- Added a compact Settings dialog with language, hover-hint and last-session recovery preferences.
- Expanded Japanese localization across static controls and choices in the asset library, media browser, decks, AUTO PERF, visual director, generators, typography, effects, layers, modulator bank, performance controls, timeline and main workspaces. A shared Qt widget pass translates labels, buttons, group titles, placeholders, tab names, menu actions and catalogued tooltips / accessible names without rewriting the underlying panel logic.
- Added a language-aware UI typeface stack: Segoe UI for English; Yu Gothic UI and Meiryo UI as Japanese-first Windows choices, followed by BIZ UDGothic and Noto Sans JP fallbacks. The application does not bundle proprietary system fonts.
- Moved timeline payload explanations from the always-visible ACTION paragraph to contextual hover help; the global Settings preference controls whether that help appears. Removed the static asset-browser instruction and shortened the initial AUTO PERF state label. Operational feedback remains visible.
- Added a user-data recovery snapshot based on the existing .eliav project serializer. It checkpoints after edits (debounced), every 30 seconds and on close, then restores on next launch when enabled.
- Recovery restores decks and composition as an editable session while leaving deck playback, Performance Mode automation and external live services stopped. Named project paths remain separate from the recovery file.

### Next implementation priorities

1. **M7-A — Visual Activity telemetry:** extend the composition-only score with feedback history, particle population, effect-stack load and active-transition data.
2. **M7-A — Operator priorities:** add per-layer priority and mutation-category controls to the adaptive selection budget.
3. **M7-B — Inspector design:** separate quick controls from advanced controls, reduce panel density and complete responsive refinement across the existing Qt Widgets workspaces.
4. **Localization:** finish Japanese coverage across every panel, dialog, menu, status message and validation error; add a consistent language-switch/restart policy.
5. **Acceptance:** run the full Windows UI workflow on the target machine, including session recovery with missing media, paused deck restoration, repeated app restarts, preview/projector parity and packaged one-file startup.

The larger drawing, printmaking, advanced feedback routing, signal visualizer and 3D renderer directions remain later M7 feature work; they should follow the inspector and renderer telemetry foundations rather than be mixed into this continuity slice.

## M7-B Japanese UI and product-language slice · 14 November 2026

### Implemented

- Added a shared phrase-based Japanese localization layer for the existing Qt interface. Static labels, group titles, button text, combo-box choices, placeholders, workspace tabs, menu actions, tooltips and accessible names are translated on startup when Japanese is selected.
- Added language-specific application font families. English uses Segoe UI with Noto Sans / Arial fallbacks; Japanese uses Yu Gothic UI, Meiryo UI and BIZ UDGothic before Noto Sans JP / Noto Sans CJK JP fallbacks. These are system font names, not bundled font assets.
- The musical timeline no longer renders the long payload explanation as a permanent ACTION label. Each event type places its explanation on the JSON payload editor as hover help, and the Japanese catalog includes those descriptions.
- Removed the asset browser's persistent “Select an asset…” instruction and shortened the initial AUTO PERF label. The remaining preview prompt and hidden dock helper sentences were reduced to concise state/section labels. The generator panel's live feedback area remains because it reports actual actions and errors rather than static onboarding copy.
- Moved video / animated-image / still-image overlay guidance to contextual hover help. This removes a stale reference to an overlay hint label that was never constructed; selecting an overlay no longer depends on that missing widget.
- Added regression tests for Japanese control translation, preserved user-entered text, translated tooltips, font preference order, timeline hover-help behaviour and image-overlay selection/help.
- Added [PRODUCT_OVERVIEW.md](PRODUCT_OVERVIEW.md), an artist-facing description with practical audience fit and explicit “not for” cases.
- Added [WEBSITE_PLAN.md](WEBSITE_PLAN.md), defining an old-fashioned dark field-manual / archival website direction, application-matched colour tokens, navigation, downloads, manual/wiki structure and a Markdown-first content-source map.

### Audience fit grounded in current capabilities

The strongest fit is **VJs and live visual performers**: the four-deck collage, live layer controls, effects, scenes, macros and projector output form the centre of the application.

Other credible use cases are **electronic musicians and Sonic Pi performers** who want OSC-controlled visuals; **audiovisual/media artists** combining prepared footage and procedural material; **generative artists and creative coders** who want an existing composition/performance surface; and **typography-led artists** working with animated English/Japanese text.

The product overview also explains where the application is not a good substitute: conventional non-linear editing, DAW/audio production, full 3D authoring or final master recording. These are capability-based audience hypotheses, not conclusions from user surveys or market research.

### Remaining work and acceptance boundary

- Japanese localization now includes translated dynamic status/error templates, dialog prompts, multiline confirmation copy, table/tree headers and progress-bar formats. Some native Windows file-dialog chrome and external runtime-provided names remain OS-controlled or source-dependent.
- The Settings language selection now updates the application font stack and retranslates the live widget tree without restarting. Dynamic text setters retain their source string, so changing back to English restores the original text rather than translating user-entered content.
- The English/Japanese website is implemented as plain HTML/CSS. The only website HTML file at the repository root is `index.html`; all other pages, localized guides and the shared stylesheet are organized under `site/`. The Markdown reference corpus remains under `docs/` for LLM/development use. GitHub Pages should use **Deploy from a branch → main → /(root)**.
- The Japanese Windows typography proof now loads a test-only Noto Sans JP font in CI, checks glyph coverage and renders an image. This validates the translation/font path in the runner, not installed font availability on every target Windows PC.
- Automated UI tests cover translation mechanics, tooltip behaviour, dynamic dialog/status copy and table/progress labels. Actual visual QA on the user's Windows machine, especially projector layout and long-duration operation, still requires target-hardware review.

Remaining product-language work is now mainly coverage of native OS dialogs and source-dependent dynamic strings, followed by a broader visual redesign of high-density inspector panels and quick/advanced control grouping without removing functionality.

## M7-B typography and build handoff · 15 November 2026

- Completed the desktop typography pass across ordinary labels, list/table rows, combo and numeric values, action buttons, checkboxes, group captions, menus, dock titles and tooltips. Display headings remain Newsreader / Georgia in English and Yu Mincho / Noto Serif JP in Japanese; technical controls use DM Mono with system monospace fallbacks; editable text fields retain the Windows sans-serif stack.
- The application does not bundle font binaries and adds no font-related Python dependency. The UI uses installed system families and remains readable when the preferred face is absent.
- The Windows build now derives its executable display name and icon from `config.py`, checks `config.APP_VER` against `pyproject.toml`, validates the final `eli-lab-mark.ico` before packaging, and records resolved package versions in the build report.
- Runtime requirements remain aligned between `pyproject.toml` and `requirements.txt`. The `dev` extra now includes both Ruff and pytest, matching `requirements-dev.txt`.
- Build/test acceptance: compile, Ruff, pytest and the Japanese typography proof run in the Windows Quality workflow. The local one-file build additionally runs `pip check`, import checks and the packaged `--self-check`. Actual GUI, OpenGL/projector and sustained-performance acceptance still requires the Windows performance machine.

# **M7 — Unified Generative Audiovisual Instrument**

Proposed governing direction

**Core objective:** Combine unrestricted visual composition, intelligent musical direction, procedural graphics, advanced image processing and a professional live-performance environment.

The application should be capable of producing extremely chaotic images while retaining intelligent control over musical progression, transitions, visual density and performance structure.

## **1. One visual engine, three interacting principles**

I would replace the idea of separate visual behaviours with three continuous principles.

[André Chi Sing Yuen: eine kosmopolitische Perspektive zwischen eurasischer Tradition und der Modernität der digitalen Kunst](https://images.openai.com/static-rsc-4/-yUpsDnyILEEOi1NDSSHxYg2IRFXfe89JbJRVPYnq5jkLFmJi3rYPcwcZ5gEGGHJf5culSMXBxvbr4seqPGl7G8g_67h5vs8elOsGLz_g6ItSNqEfQ4CEELAdkfdLSB04nvXmfSXmJXNL2WGMJlObuhyl7v2rwKUbKeDmh2upaY?purpose=inline)

**CHAOTIC — Visual freedom**

Unrestricted spatial composition, overlapping video, displaced layers, randomized typography, abrupt cuts, distortion, feedback and visual collisions.

Its purpose is to generate unexpected results.

[Piano. Interactive, audio-reactive 3D typography :: Behance](https://images.openai.com/static-rsc-4/qDl3Kv9fBgzplssutBME8z8u75DbSb8_eHpzFlClDjeTcbH1Oza4opCsa0V7CMNQ71RuPrRiQP015CFbxnzpbw9CF0MoV_w00QTWYBXVTS56pHz1vfgqzv1fyLw09TQ5znrq2PSwpX6KvhmmkK6SYW5VUNxFJDT9gneAYOyBtSs?purpose=inline)

**GENERATIVE — Intelligent decisions**

Musical context, energy, phrase awareness, procedural variation, visual memory, adaptive layer selection and performance macros.

Its purpose is to make unexpected results meaningful.

[OpenProcessing - Creative Coding for the Curious Mind](https://images.openai.com/static-rsc-4/6NKbLC9MvZ0EwZLwV_NZLjNpG5SRqpWkj5u4YNXT7sf1sxhN9T2e0NZ4guaSSDzBkHcHLK6DoQ31lsZj_hlFNJmDWDUUI9p8LgLsJaf1a_fmbuKoh7escCsK2cJcoqnfAVZDGVUVUsa3vEt46NxHZVAtM4MWrT1na4nBIG9pTRU?purpose=inline)

**STRCD — Compositional intelligence**

Visual anchors, recurring motifs, restrained transitions, deliberate negative space, palette continuity and temporal pacing.

Its purpose is to provide direction without suppressing experimentation.

These are not three independent engines. They are three influences on the same decision-making system.

### **How they should interact**

Consider a musical performance:

| Musical section | Director behaviour                                                                 |
| --------------- | ---------------------------------------------------------------------------------- |
| Intro           | Establish visual motifs, but allow unpredictable composition                       |
| Development     | Increase layer interaction, movement and variation                                 |
| Pre-peak        | Increase density, spatial chaos and temporal activity                              |
| Peak            | Allow full-canvas collisions, aggressive feedback, text and particle interventions |
| Breakdown       | Reduce activity, but retain occasional unexpected visual events                    |
| Outro           | Gradually resolve visual elements, without necessarily returning to a clean layout |

The important part is that the director should understand the overall musical structure while being free to generate unpredictable images inside it.

A breakdown should not automatically mean a neat, minimalist composition. A peak should not simply mean maximum saturation.

The director needs to make decisions based on the actual composition, recent changes and musical context.

## **2. Remove artificial restrictions from the current architecture**

This is where I would concentrate the initial M7 engineering work.

I inspected the current `core/automation.py`, `core/generative_director.py` and `ui/automation_panel.py`.

These are the changes I would make:

| Current limitation                        | M7 direction                                                       |
| ----------------------------------------- | ------------------------------------------------------------------ |
| Maximum two layers per variation          | Dynamic selection across all eligible layers                       |
| Mandatory preservation of an anchor       | Optional anchor with adjustable persistence                        |
| Six predefined layout patterns            | Continuous spatial composition and probabilistic layout generation |
| Video-only automatic layout changes       | Video, text, geometry, particles and overlays participate          |
| Primarily smoothstep layout morphing      | Multiple transition behaviours operating together                  |
| Fixed variation intervals                 | Adaptive intervals informed by music, density and visual activity  |
| Restricted rotation and positioning       | Full transform freedom, including off-screen placement             |
| Limited independent layer interaction     | Relationships between multiple layers                              |
| Randomized effects after transitions only | Configurable and context-aware effect mutation                     |

There should still be resource budgets for rendering, decoding and GPU allocation. Removing visual restrictions does not mean removing technical safety limits.

### **The more intelligent alternative**

Instead of `max_layers_per_variation`, introduce a dynamic variation budget.

The director can decide whether to modify one layer, several layers or the entire composition based on:

- Musical energy and section.
- Current visual density.
- Number of active layers.
- CHAOS and FRAG macro values.
- How recently each layer has changed.
- GPU and rendering performance.
- Operator-authored locks and priorities.

An anchor becomes a probability or persistence preference rather than an enforced rule.

The layout engine should also be able to create relationships between layers: shared centres, overlapping transforms, opposing movement, nested geometry, synchronized rotations and deliberate collisions.

This produces organized chaos rather than merely random object placement.

# **3. M7 visual instruments**

I want to retain all five instruments from your original plan. They should become first-class parts of the application's composition system.

## **A. Generative Drawing Engine**

High priority

[Geometric spiral pattern on a black background.](https://images.openai.com/static-rsc-4/ICzvwFwix30e5iZBwHANsRfq7eEvPdbZNzameEoafG-fjfvfsqKuPIMouvK1AX3IO0J_Y06TQS5WLm_1iWBzC2egB3UJkx3GFOaxCuqVZZPdNYDiz4Zlns3trhFlGiQFHEH-Lt9dSfCuHuT4vKmu94Wd7AfDWoWQnULqNSowinyesXKnJ-cxHWAhxhR7-Zwo?purpose=inline)

[sketch_220810c :: Behance](https://images.openai.com/static-rsc-4/FR0VBBBcyvVbVu-5kWaBKM4iTuvuUJzA0xF8tDiaJB1W97YIg23Obm8JXvIVHbuK0p-o78cUf9V4-4VGnlvhSpUqj6GhrLO5fwYKky7ItCkjTac7wKqbs675zbwDfcHYri-WPRO7fJ0YD0-iqTC59tHr-3FEV3AzxJVwLhRPYdk?purpose=inline)

[Fork: Curl Noise by rupertxrussell | Turtletoy](https://images.openai.com/static-rsc-4/dRBJs7CvgX16xS5UjgfEPSxGBkfeCEHx_f6yQaj87238BX75buOMIHbR3OWtTUJEI4Jmcw89H03v3wGTqrGGT64OgksT72F0BOq1DsOOOHpDx7XXSqYSAA7kL02r3k7w-D5sJW5fXmtbDGtn8YJriRcUs8lInQQAn_QGYmfc0lY?purpose=inline)

15

This should be a new procedural drawing instrument, not another variation of the existing Geometry generator.

**Proposed capabilities:**

- Bézier curves and editable vector paths.
- Animated stroke reveal and drawing sequences.
- Persistent line accumulation.
- Procedural hatching and crosshatching.
- Recursive geometry and branching structures.
- Contour generation from video, images and procedural sources.
- Spiral, radial and field-driven constructions.
- Distortion of paths using noise, audio and vector fields.
- Repetition, symmetry and geometric subdivision.
- Independent stroke width, colour and opacity.
- Dynamic path generation and seeded reproducibility.

The interesting part will be allowing drawing to interact with the footage and other generators.

For example, a video frame could generate contours, which then become a set of animated paths. These paths could accumulate over time, distort under audio modulation and eventually feed into the feedback engine.

**Implementation recommendation:** keep path authoring and procedural geometry generation outside the frame loop. Render the resulting data through a dedicated GPU instrument.

## **B. Temporal Feedback Engine**

Existing M6 foundation — extend

[Das ist das Feedback, 2024 von Steve Pavlovsky: Kunstdruck](https://images.openai.com/static-rsc-4/N0teVnJjuYPj0XAF5h2DhTVlg3CMBhZ4KOhOlH6XdheR2WFzaRAjHZAZ1LuIUTotV5shR125ZzqoD6qmiCrdqtfKuDlfy7Pwr2yCQdYs_EERJ4_pU5AdqO35KrhSxpywtGktWPEOpAU3taufiY0SRZzegsmr4wHJaUg6qFVQ3gM?purpose=inline)

[pixel sorting Glitch](https://images.openai.com/static-rsc-4/Vqcc2yYkrhsW0yF35-4sOs7i_Z6Jag1rgHg844RwdvkrnY33eH00aDdW2fQ8BU3zWM32hDX3dBIYAkKlGaoeEY9bmKdsHGMg4QDRTQ5PcXREBo8Csom9lNsnVugwHUBHpiSvbk9WP7o3zb0LNiULJdd8SsmSY1RGgDefdh1ChsWyOs6iwOX4damsiocFH-lE?purpose=inline)

[Glitch Video Synthesizer -VANDALIZER-MEZKALIN- Circuit Bent Video Processor, Analog Video Synth, Video Enhancer - Etsy](https://images.openai.com/static-rsc-4/SmRTl0bNCp4Wyk_RPCQqyOKPNYxfdTy42-8oYXWmPs0ZBcAe6I_81jXAIB_e493ylb9IZZa7XoaHUTDINqkvKjbjZqVTGOcN4etluAdFYiOnSaHE4WWswjtZ9yqMcU9mUy7FvB1sGCjxecWAAoM2K2J7BiEd308y5PdccphSGU4?purpose=inline)

14

We already have an important foundation in `rendering/feedback.py`.

I would not replace it or create another feedback renderer.

The current M6 implementation has a five-texture history ring, feedback transformations, decay, colour shifts, motion-driven warping and datamosh-style blocks.

M7 should make this visual memory much more expressive.

**Proposed additions:**

- Multiple independently controllable feedback sources.
- Layer-specific feedback send amounts.
- Text-only and generator-only feedback routing.
- Independent feedback transformation chains.
- Recursive zoom and rotation combinations.
- Accumulation and decay envelopes.
- Frame stutter and temporal echo behaviour.
- Feedback modulation by audio bands and Performance Macros.
- Selective feedback freezing.
- Scene-specific feedback states.
- More elaborate temporal transitions between source images.

A particularly interesting possibility is allowing the drawing engine to receive feedback from the compositor, then use that feedback as an input for another round of drawing.

That creates a recursive relationship between images and procedural graphics.

The feedback implementation must remain bounded and GPU-native. Preview and projector must continue owning independent rendering resources.

## **C. Advanced Signal Visualizer**

[CEC — eContact! 19.2 — Vector Synthesis: An investigation into sound-modulated light by Derek Holzer](https://images.openai.com/static-rsc-4/VfC4444f_YHYfY0RATYnkNDWOat30DPTNHhjJV8g8Y99BLnJIDSggA80l3Q52vhCWmZrh33agBqcTznWQj0oPo9uuwQSrqXt-kqBwffeZQOShOJVLeD4uBCyyeWGAzyYCNsGg0m_Auxmu5sB-07uvaK4hLIJpkk9BOxujnDJGLs?purpose=inline)

[Making a spectrogram with Geometry Nodes — Blender Conference 2025](https://images.openai.com/static-rsc-4/OZMEXv4MqMqXrXMa4-Wpwi4KDJrRbOwh10NQ7uOnPdH83ZSPaAOUmtKwaC-IrIo6WtHkYHMvBjzauojLydWEJ3f9PyrsCI9fWHFLeBV4KP2c3snyuQHSsrKw3D0NS8lVGOST2y1i9RF4f4st442lliVA68QvUCskM_8CPMQIqcU?purpose=inline)

[Sound Visualizer :: Behance](https://images.openai.com/static-rsc-4/MElBoBEmThFySal_8NE3G_1VEVvs5-ar2lff1HTi6L65TdJ8xF5j1-CRdkMgvabbcs9CgTCwIW-izji4Rf4nultzal0bMGb66dTIqLAV4qyQbfMku-bXCsYwmhu1atPGev71NC30xCKQWpgl_5PTMd7csfGkSDxsVP3UaExBo-s?purpose=inline)

16

This should evolve beyond the current waveform generator.

I would introduce several visual instruments:

| Instrument         | Function                                               |
| ------------------ | ------------------------------------------------------ |
| Oscilloscope       | Time-domain waveform representation                    |
| Phase Scope        | Stereo phase and Lissajous visualization               |
| Spectrogram        | Frequency history over time                            |
| Frequency Geometry | Geometry generated from spectral data                  |
| Spectral Particles | Emission and motion driven by frequency bands          |
| Signal Field       | Spatial fields driven by audio signals                 |
| Wave Deformation   | Geometry deformation driven by amplitude and frequency |

The important architecture decision is to use the existing audio-analysis and modulation foundation rather than create a separate audio-analysis pipeline.

These instruments should also support non-audio sources: transport, Sonic Pi macros, modulation signals and procedural inputs.

For example, CHAOS could alter the geometry of a phase scope, while the low-frequency band controls its structural radius.

## **D. Procedural Printmaking**

High priority

[日和崎尊夫 木口木版画『殖』(日和崎尊夫) / アブストラクト古書店 / 古本、中古本、古書籍の通販は「日本の古本屋」](https://images.openai.com/static-rsc-4/T304N_jjtNAEo5Fvw9NHpSY9-PlyoSl9UdxNXJsni5YceQNRaebg-cMX6cWAa22yByWGBpMDb4zTGI9qiPCAvVgNVJkyn6a82HZIhIm7DYLx88CkWsd-F_hRurbXrauWwrCQGVlL6TAi7oJiJCuNtLkmhJjVaOc_GO8FeM5emlw?purpose=inline)

[Destroy All Monsters Magazine | 百年](https://images.openai.com/static-rsc-4/03_pbe3YC8y5FucDRNvzXnictuieuOQmPVJ2AsiBGudczU_lh2UdCGveHy0fwD10HByOvTHw208FELNXXo-4d9xbASS1XoSlFnEy9xSpL_d16_yTGgl90xobZSyXNUqJo20oxHmOyRqOkKj4nkYk1w9POE5CFBJITnwa3X0Be8k?purpose=inline)

[Abstract vector woodcut engraving undulating lines horizontal banner.](https://images.openai.com/static-rsc-4/D9w8bsX3yi6eHAPt_dqfiBwcuaQ_Tv1qR9fnk3Rb3dQPuLX4HspUZ2cySYGTgqUH1FWT_smJ99R4WXG0dN8BqFX9jMKa9aXpIuqpMzvSDWKObG2iZgjzsVuqT_2CNMGk70gQO5HyNtDmUbHj0MPl0O1xknc3ILcK7l1bx7tpxnI6JlrSmnJKld7ydA9ss0wK?purpose=inline)

17

This is particularly promising because it provides an entirely different graphic character from ordinary digital glitch effects.

**Proposed processing instruments:**

- Halftone.
- Xerox / photocopy.
- Engraving.
- Stochastic hatching.
- Crosshatching.
- Paper grain and paper texture.
- Ink spread and bleed.
- Print misregistration.
- Multiple ink plates.
- Threshold-based contour extraction.
- Ordered and stochastic dithering.
- Colour separation and channel offsets.

I would implement it as a proper procedural print-processing system rather than a collection of unrelated filters.

For example:

**Example printmaking pipeline**

Original video / drawing / text

Contour and tonal extraction

Halftone / stochastic hatching / engraving

Ink plates / misregistration / paper treatment

**GPU compositor and feedback**

The processing stages should be independently adjustable, reorderable and automatable.

Printmaking should also be available as a source for feedback, not just as a final image treatment.

## **E. 3D Visual Generator**

Research and architecture phase

[Warping the Grid :: Behance](https://images.openai.com/static-rsc-4/UmK_hFTsDoNrggHXtJQpOJhNNsxjvdK2Q69e96z0M5VCZnbb7O3cszZOuuNdtSYzub4eouWD_trHU5QHAwsDL4AeFvGFy8Lukz9I0zH81Ru8JUb3r-H7M3EDJSdva2RhQAoDQAccfEUL8dSjx8w3aOo342OH6sY9CFAm9sK3R9k?purpose=inline)

[The One Rule That Unites All Great Design: Foundation in Form & Structure | Bobr AI](https://images.openai.com/static-rsc-4/FqlR9VPhJxKCbkt-opT9DtUWp32p4SX67Dw9LN-6KDkAZtonps9cOuCcLTilRHQzCm_mTt7vpcP8K3MGMRM4iSv9_b2WhIdAldOkbAxHu-JCj6Tr48I173iSqr6AxZpJQtmJWO4I4SzE9ORozrmr5QGQrNNfvx5jvjWrz9HHqBQ?purpose=inline)

[Various TouchDesigner Animations :: Behance](https://images.openai.com/static-rsc-4/ZIh2pfdOE3V4WI4XMzzgCCWpHe7ko95mLFPq3vcxVZfhVAbetw8wsOoayGS-qH2REInkFhd4ZJIILCIQEnLsENoCYt1bwvA5ffRclD6sNI194y9O5Z5OjX18eKZ7QCnR3wtWjauS9kz1EMJ46LE05cpjvU7aZ-O92zaNa_PMNrk?purpose=inline)

16

I agree with your original recommendation: do not force a 3D engine into the existing 2D compositor.

I would create a separate rendering module with its own lifecycle.

Initial scope:

- Procedural meshes.
- Wireframe and solid rendering.
- Rotating geometric structures.
- Surface and vertex displacement.
- Instanced geometry.
- Camera position, rotation, zoom and projection.
- Basic lighting.
- Audio-reactive mesh deformation.
- Procedural materials.

The integration contract should allow the 3D renderer to provide an image source to the existing composition system.

Each output context must own its own rendering resources, just as the existing preview and projector renderers do.

I would begin with a technical proof of concept before committing to a full 3D feature set.

# **4. Performance Director — connect everything**

This is the most important architectural part of M7.

The visual instruments should not operate independently of the existing Performance Macros.

I would extend the six macros as the common control vocabulary.

| Macro    | Existing purpose               | Expanded M7 responsibility                                     |
| -------- | ------------------------------ | -------------------------------------------------------------- |
| CHAOS    | Glitch, rotation, displacement | Spatial freedom, mutation probability and drawing irregularity |
| DNST  | Tiles, geometry, particles     | Layer density, drawing complexity and spectral populations     |
| DPTH    | Transform and feedback         | Recursive geometry, spatial transforms and feedback intensity  |
| DEC    | Feedback and trails            | Ink persistence, trails, accumulated strokes and visual memory |
| PRESSURE | Contrast and distortion        | Thresholds, hatching density, ink treatment and deformation    |
| FRAG | Pixelation and displacement    | Layer fragmentation, typography scattering and temporal cuts   |

This should remain the existing normalized modulation architecture, not a competing second macro system.

I would also introduce a shared concept called **Visual Activity**.

The director could estimate the current activity of the composition using:

- Number of visible layers.
- Spatial overlap.
- Transform intensity.
- Amount of temporal feedback.
- Active particle and drawing populations.
- Effect-stack activity.
- Current transition activity.

It could then make decisions based on whether the image is visually underactive, balanced or overloaded.

That would make the director genuinely intelligent instead of simply increasing randomization whenever musical energy rises.

# **5. UI redesign — a proper VJ workspace**

This should become an explicit M7 workstream.

The existing interface has functional panels, but `MainWindow` currently organizes most of the application around Qt docks. The composition inspector occupies the central workspace, while the actual preview is another dock tabbed alongside performance controls.

That is not the ideal arrangement for an operator-first VJ application.

The adaptive 4:3 and compact layout work from M6 is worth keeping, but M7 should go further.

[Resolume Arena - Download - CHIP](https://images.openai.com/static-rsc-4/00U_a6TB_EbZ-_Y64PNpt-DQu9-FUJgJiVsDwbR5FVtghf8Wz7LKxN8OfaHeSSD600-y9NNGRM7gYVr4YDPws99Usriu79MDiLw_UmXkABjXxkgeRUO8q2Gxfj0RuoEMPlK6NKugZRWigXck3xHXgCr78578Pl5i8A__sYJ_VYk?purpose=inline)

[OP Snippets - Derivative](https://images.openai.com/static-rsc-4/C1Eja98DA_KTbloRDmIKbl6zvYjII9Qr3vRT0fS190WxR0blY8xE3Pgmo-Askqi0kSo5FI9LFX-rdQNFy-OTvd7dzdJE1bN9Tum9bPcpLxqDIcZ18T02K433Tnw3y7lV3Y4TBAXY7zWc08WYwAcWznJh5Rn69Sb1dN-179M4_h0?purpose=inline)

[Training – Resolume](https://images.openai.com/static-rsc-4/AFmFfYzmdZe9Z9mTkQcDwxsptRw2Zlp9HXd3IXLHpjDPoUDCs63oxlY3L_Vl-wThjrsmZzqcg67lkf8UdxVTwwV4_6B_0t2T-FidNwn7j-SX7UKhbX9oDDbVplW-7PggugeBwOvbzQ2fz_8vCd7CRJrx-Lj5cK-ptvdwmLug_Uw?purpose=inline)

11

I propose three application workspaces, with the performance workspace becoming the primary environment.

**01 — PERF**

Primary workspace

[Resolume VJ Software & Media Server](https://images.openai.com/static-rsc-4/kzt-yCxINwblaJtkIwNmLOiveTgSpOLf70VNcLdrRa8_FLjho43oosCwiWBi6I5xvSSGoha-P_P1qxuF_N4N7lFap83BJ6SVfJD1XzC8bP5FWdQ-QLS3dd0pF6Yq5Bw6I1bxXIg87RFULPcKGvgawrjl0AcjbUAP-4hsJ5who74?purpose=inline)

[resolume.com](https://resolume.com/?utm_source=chatgpt.com)

The central canvas should be large and immediately visible.

- Live preview / projector status.
- Video deck strip.
- Layer visibility and quick controls.
- Performance Macros.
- Visual activity and transport indicators.
- Timeline and scene triggers.
- Quick FX and generator controls.

**02 — COMPOSE**

[Notch | IBM’s Celebration of Innovation](https://images.openai.com/static-rsc-4/0wsT_Lk1BVogLIq7NIEOabZDMCzm5Awa6gsYVY9_EJ6Qh0BumDOLhsI_PeH-I4WV2B1Y1ASPMiHPXfNYao1fI2pIs_ZB0cX63DVVEgQc0hAPM21MbBSS0T7wLBCxeJHbOl_rkQNyXOruO05bZP2wDJZ-cvL6cMRQ_aPhBFOHgVU?purpose=inline)

[notch.one](https://www.notch.one/madewithnotch/ibms-celebration-of-innovation-notch-cognitive-in-motion/?utm_source=chatgpt.com)

Designed for creating and editing compositions.

- Central composition canvas.
- Layer stack and hierarchy.
- Generator and effect inspectors.
- Typography and drawing editors.
- Feedback routing.
- Visual assets and presets.

**03 — PREPARE**

[VJ.Tools Library | Prep with the music on](https://images.openai.com/static-rsc-4/xwA3sTv9KIBoiApnFmeUoL6QOxSpUS1XrT4flmll3Ik9kL68T0fUHRcotKgfhnQx8wU7n2HFbc96IPGNRL9Pnbroj_4sNsCP9W7PNnJlzYmWE96OHU6igEOcUhNIH3afFM15XR_6B99TN148zHH0Zr35cHoezQZewlx2g_4WS2s?purpose=inline)

[vj.tools](https://vj.tools/?utm_source=chatgpt.com)

Designed for preparing a performance.

- Media library and collection management.
- Deck assignment.
- Scene and composition banks.
- Performance timeline editing.
- MIDI / OSC configuration.
- Saved show configurations.

### **UI details I would prioritize**

**A. Context-sensitive inspector**

Selecting a text layer shows typography controls. Selecting a drawing layer shows path and stroke controls. Selecting video shows transform, blend and source controls.

No need to display every parameter for every layer.

**B. Quick controls versus advanced controls**

Every instrument should have an accessible quick-control surface and an expanded editor.

For example, the drawing engine's quick surface might contain Density, Chaos, Motion and Colour. Its advanced editor exposes path geometry, curve points, stroke accumulation and rendering settings.

**C. Performance control surface**

The six Performance Macros should be prominently accessible without opening a separate settings panel.

The timeline, musical position, active scene and section should remain visible during performances.

**D. UI consistency**

I would establish common component patterns for:

- Sliders and value displays.
- Colour selection.
- Layer selection.
- Effect chains.
- Generator parameter groups.
- Modulation assignment.
- Keyboard and MIDI mapping.
- Preset selection.

**E. Responsive layouts**

Keep support for 16:9, compact desktop and 4:3 projector-oriented screens. The interface must remain practical at different resolutions, without reducing everything to tiny controls.

Most importantly, the live canvas must never become a secondary element of the application.

# **6. Revised M7 development sequence**

Here is how I would organize the entire milestone.

## **M7 roadmap**

1. **M7-A — Unified Visual Director**

   Foundation
   - Fix the current automation runtime bug.
   - Remove artificial variation restrictions.
   - Introduce dynamic variation budgets.
   - Implement unrestricted spatial composition.
   - Introduce layer relationships and interactions.
   - Improve adaptive musical decisions.
   - Integrate all six Performance Macros.
   - Preserve the existing M6 systems.
2. **M7-B — Performance UI Redesign**
   - New Perform, Compose and Prepare workspaces.
   - Large central composition preview.
   - Redesigned performance surface.
   - Context-sensitive instrument inspectors.
   - Consistent component system.
   - Responsive layouts and persistent workspace states.
3. **M7-C — Generative Drawing Engine**
   - Vector and Bézier geometry.
   - Recursive structures.
   - Animated strokes.
   - Hatching and contours.
   - GPU rendering and procedural interaction.
4. **M7-D — Temporal and Visual Processing Expansion**
   - Extend M6 feedback.
   - Layer-specific feedback routing.
   - Temporal echoes and stutter.
   - Procedural printmaking.
   - Effect-stack integration.
5. **M7-E — Advanced Signal Visualizer**
   - Phase scopes.
   - Spectrogram.
   - Frequency geometry.
   - Spectral particles.
   - Audio-driven deformation.
   - Sonic Pi and modulation integration.
6. **M7-F — 3D Rendering Foundation**
   - Separate renderer module.
   - Procedural geometry.
   - Wireframes and meshes.
   - Camera system.
   - Compositor source integration.
7. **M7-G — Integration and Release Validation**
   - Project persistence.
   - Scene and performance-set persistence.
   - Full GPU resource testing.
   - Preview/projector consistency.
   - Long-duration performance.
   - UI and workflow validation.

The order is intentional: the Unified Visual Director and UI should come first because all the subsequent instruments need a stable way to participate in composition and performance.

# **7. Engineering rules for M7**

I would make these non-negotiable acceptance principles:

| Area          | Rule                                                                       |
| ------------- | -------------------------------------------------------------------------- |
| Rendering     | GPU-first, no unnecessary CPU image processing per frame                   |
| Architecture  | Reuse shared modulation, composition and rendering services                |
| Variation     | No arbitrary two-layer limit or compulsory anchor                          |
| Randomness    | Seedable, weighted, state-aware and musically informed                     |
| GPU resources | Bounded allocation and deterministic cleanup                               |
| Typography    | Keep static rasterization asynchronous                                     |
| Drawing       | Keep procedural geometry independent from frame-loop authoring             |
| Feedback      | Reuse the existing temporal history system                                 |
| 3D            | Separate rendering module and output integration                           |
| UI            | Operator-first, contextual, responsive                                     |
| Persistence   | All new instruments and meaningful parameters survive project/scene reload |
| Testing       | Regression tests plus actual Windows/GPU/projector acceptance              |

I would particularly emphasize **visual regression testing**.

The M5 screenshots should become reference compositions. M7 should be able to recreate their visual density and unpredictability while using the newer feedback, typography, particle, musical and modulation systems.

It should then demonstrate improvements beyond those original compositions, rather than merely reproducing them.

## **8. What M7 should ultimately achieve**

[Maximum the Hormone team with ATARASHII GAKKO! for fierce 'SHIMI' music video | Electric Bloom Webzine](https://images.openai.com/static-rsc-4/SNhIz1VtVa48tyzoJwOL5bgsP18DM-zM_byPHgLoQ1oQUP4FEts3J-PMTjrTkBFWK5GTYI35gokT8EpsEuxxk3BNAJ4yX6blbhCzpR-2zufBswWZcg-tpOOxTTtl1358OS2B-rcZfX8FX4UKuCnBOLLtvr7gCZERo2b4snf-FZo?purpose=inline)

[021022 :: Behance](https://images.openai.com/static-rsc-4/KwnifEpQFME-V7VcMxiEBql8HNeM7iklbFACgDSuTWjRhI28N21uFttDreaXQOQbBQHQN6Uqfb_xP0lfbATcJlBYUANCF5yrCaVeiIdz_CCoeAi4XXyVhJUQ9dhSnCoK8sigSqEGxuVLH7lpqnrUiWf4xzzQD0ysqr_ss4Oxxwg?purpose=inline)

[TOOL's Concert Visuals Are Super Trippy - Metal Injection](https://images.openai.com/static-rsc-4/riBsDhxHermUY456FhT2kjKohNmw6nD8kHeNhCibfD-cSxALkAwjt4nd3Q5sfVjXoNFnyIDGx_zic9kHJuHejNAKX2rBw-zoRDPhPecoFB538J7ILLgpVBZ4jzo2FDHQV66KsuYOmufmwxf5zhoTo72xXHUWMLKcSVP9eiTl3ZE?purpose=inline)

18

I think the final identity of eli_lab AVTranslator should be:

**A generative audiovisual performance environment where video, typography, drawing, particles, geometry, sound and temporal image processing are all part of one continuously evolving visual composition.**

Not a conventional video mixer with random effects.

Not a conventional generative art application.

Not a conventional audio visualizer.

It should combine all three into an instrument with its own aesthetic identity.

And there is one principle I would keep throughout M7:

**The director should understand the composition, but it should never be afraid to destroy it.**

That is the balance between Chaotic, Generative and Structured Hybrids that I would use as the governing design principle for the milestone.

---

# M7 implementation log

## M7-A — Unified Visual Director · initial code slice

**Branch:** `m7/unified-visual-director`

### Implemented in this branch

- Added a dynamic variation budget derived from eligible layers, musical drive, CHAOS, DNST and FRAG.
- Removed the two-layer selection ceiling from `GenerativeVariationDirector.select_layers()`.
- Made anchor and background-source preservation opt-in; retained serialized fields for old performance plans.
- Expanded spatial variation beyond video to visible/unlocked video, generator and overlay layers.
- Added higher-variance scale/rotation/opacity/blend choices, off-canvas placement, clustered overlap, and probabilistic abrupt transitions alongside morphs.
- Replaced the old two-step performance style gating with a unified director selection path.
- Fixed the misspelled `_select_variation_layer_ids` call.
- Changed AUTO PERF UI wording to describe one unified director and adaptive scope.

### Remaining M7-A work

- Add operator-authored per-layer priorities and explicit mutation categories to the adaptive selection budget.
- Extend Visual Activity with renderer-side feedback history, particle population, effect-stack load and active-transition telemetry.
- Add further regression cases for legacy project-plan migration, all synchronization modes, manual generator/overlay/FX edits and long-session stability.
- Complete target-Windows testing for live GPU composition, preview/projector parity, sustained performance and saved-show recovery.

### Validation status

At commit `ddbff4e`, the M7 branch passed whole-project Python compilation, targeted Ruff and all 16 regression tests. Interactive Windows UI, GPU preview/projector parity, long-duration rendering and packaged one-file acceptance remain manual release gates.

## UI technology decision — M7-B

The desktop surface remains implemented with Qt Widgets (`QMainWindow`, `QDockWidget`, `QToolBar`, and widget-based panels). The application now uses the native **Fusion** style with a project-owned QSS design system. There is no runtime dependency on Qt Material.

- Keep the existing Qt Widgets and OpenGL / ModernGL composition architecture. A styling pass must not change render-context ownership, layer state, preview/projector lifecycle or performance behaviour.
- Use a restrained monochrome palette shared with the website: `#090909` page/background, `#101010` raised surface, `#151515` inset surface, `#eeeeee` primary text, `#a3a3a3` muted text and `#303030` rules.
- Use the website-aligned typographic hierarchy without bundling fonts: Newsreader with Georgia fallback for English display headings; Yu Mincho / Noto Serif JP for Japanese headings; DM Mono with Consolas / Cascadia Mono fallback for uppercase action captions, group titles and metadata; Segoe UI / Yu Gothic UI for body and editable field text. Resolve families from the operating system.
- Keep monochrome control icons, generous workspace spacing, compact metadata and clear selected/hover/focus states. Advanced settings can be progressively grouped, but no existing performance or composition controls are removed.
- Preserve the existing OpenGL / ModernGL rendering widgets and output contexts; stylesheet changes must not alter render-context ownership or preview/projector lifecycle.

The first M7 shell remains PERF / COMPOSE / PREPARE tabs and existing Qt Widgets; the current visual redesign replaces the old dark-red base theme with the site's editorial monochrome system. More substantial inspector hierarchy and quick/advanced grouping are follow-on work, to be done without dropping functionality.

## M7-A / M7-B implementation update · 14 November 2026

### M7-A — Unified Visual Director

- The interval-driven and musical-event paths now use the same variation selection, layout mutation, generator variation and particle-peak services. The timer path is consolidated in `_tick_unified_time_events()`; the old internal method name remains only as a delegating compatibility wrapper.
- Dynamic variation scope combines eligible visible/unlocked layer count, musical energy/intensity/section, CHAOS, DNST and FRAG.
- Strong musical/macro drive can produce a global variation burst. The universal two-layer ceiling is removed.
- A first **composition-only Visual Activity** estimate measures layer count, approximate overlap, transform intensity, off-canvas amount and source diversity. It influences the dynamic variation budget. Feedback history, particle population and effect-stack telemetry are not yet part of this score.
- Spatial mutation now chooses relationship patterns: independent, shared-centre, opposed, nested and orbital placement. It retains seed compositions, but does not require fixed panels.
- The six M6 Performance Macros remain the shared modulation vocabulary. The director consumes existing macro values rather than introducing a parallel macro architecture.
- Anchor and background-source protection remain optional and default to off. Existing serialized fields are retained for compatibility.
- Added focused tests for uncapped layer selection, optional anchors, cross-source layout mutation, timer and bar paths, Visual Activity and relationship strategies.

### M7-B — Performance UI Redesign · first shell

- Added central **PERF / COMPOSE / PREPARE** tabs with persisted workspace selection and Ctrl+1 / Ctrl+2 / Ctrl+3 shortcuts.
- PERF reuses the existing live `PerformanceView` and displays the existing six-macro control group below it. The group is moved from the advanced control panel rather than duplicated.
- COMPOSE hosts the existing generator/composition editor.
- PREPARE contains central tabs for the footage library and visual asset library.
- Old preview/media dock shells are hidden after both fresh startup and saved-layout restoration; menu actions now switch to workspaces.
- The initial dark-red Qt Material base was replaced by a native Fusion stylesheet owned by `ui/theme.py`; the unused Qt Material package was removed from runtime dependencies and the PyInstaller collection.
- Added the editorial `e·` wordmark to the toolbar, increased workspace padding and replaced the application/executable icon with the matching monochrome serif mark.

### Validation boundary

The M7 branch workflow passed at commit `ddbff4e`: whole-tree Python compilation, targeted Ruff across the changed M7 modules and all 16 regression tests succeeded. This validates the automated code changes, not the interactive application. Actual Windows UI, GPU preview/projector parity, long-duration rendering, responsive-screen behaviour and the packaged one-file executable still require target-machine acceptance.

## M7-A final hardening slice · per-layer cooldowns and manual overrides

- Added a configurable per-layer cooldown (default 1.5 s; zero disables it). High musical energy, CHAOS, DNST, FRAG or peak sections shorten the cooldown, with a 120 ms floor.
- Dynamic selection now considers only visible, unlocked layers whose cooldown has expired and which are not under a recent manual override. A maximal musical peak can still reach every eligible layer; no two-layer cap is reintroduced.
- Automatic layout, generator, overlay, layer-FX and clip-switch mutations record the affected layer's last-change time.
- Existing application notifications for direct layer-property edits and selected generator/overlay controls now pause automation for that layer. A manual edit cancels an in-flight layout morph.
- Manual generator-parameter edits invalidate the cached peak-boost baseline. Ordinary transform edits pause particle automation but retain the baseline so temporary boosts can still restore correctly.
- Added five regression tests for adaptive/disabled cooldowns, layer eligibility expiry, manual-override precedence, layout protection and particle-baseline handling.
- The cooldown is exposed in AUTO PERF and serialized with the existing automation settings.

**Session boundary:** the current M7 implementation stops here. The drawing, printmaking, advanced feedback routing, signal-visualizer, 3D renderer and further workspace/inspector redesign remain for the next implementation session.

## M7-B UI continuity and localization slice · 14 November 2026

### Implemented

- Condensed the About dialog to the product name/version, one-line purpose, author and source link.
- Removed persistent instructional paragraphs from AUTO PERF, the macro and OSC panels, generator/overlay controls, the unified director, modulation editor, layer modifiers and media browser. Operational status and error feedback remain visible.
- Added a global hover-hint filter controlled from Settings. Tooltip text and accessibility names remain attached to controls and can be shown again by re-enabling hints.
- Added a compact Settings dialog with language, hover-hint and last-session recovery preferences.
- Expanded Japanese localization across static controls and choices in the asset library, media browser, decks, AUTO PERF, visual director, generators, typography, effects, layers, modulator bank, performance controls, timeline and main workspaces. A shared Qt widget pass translates labels, buttons, group titles, placeholders, tab names, menu actions and catalogued tooltips / accessible names without rewriting the underlying panel logic.
- Added a language-aware UI typeface stack: Segoe UI for English; Yu Gothic UI and Meiryo UI as Japanese-first Windows choices, followed by BIZ UDGothic and Noto Sans JP fallbacks. The application does not bundle proprietary system fonts.
- Moved timeline payload explanations from the always-visible ACTION paragraph to contextual hover help; the global Settings preference controls whether that help appears. Removed the static asset-browser instruction and shortened the initial AUTO PERF state label. Operational feedback remains visible.
- Added a user-data recovery snapshot based on the existing .eliav project serializer. It checkpoints after edits (debounced), every 30 seconds and on close, then restores on next launch when enabled.
- Recovery restores decks and composition as an editable session while leaving deck playback, Performance Mode automation and external live services stopped. Named project paths remain separate from the recovery file.

### Next implementation priorities

1. **M7-A — Visual Activity telemetry:** extend the composition-only score with feedback history, particle population, effect-stack load and active-transition data.
2. **M7-A — Operator priorities:** add per-layer priority and mutation-category controls to the adaptive selection budget.
3. **M7-B — Inspector design:** separate quick controls from advanced controls, reduce panel density and complete responsive refinement across the existing Qt Widgets workspaces.
4. **Localization:** finish Japanese coverage across every panel, dialog, menu, status message and validation error; add a consistent language-switch/restart policy.
5. **Acceptance:** run the full Windows UI workflow on the target machine, including session recovery with missing media, paused deck restoration, repeated app restarts, preview/projector parity and packaged one-file startup.

The larger drawing, printmaking, advanced feedback routing, signal visualizer and 3D renderer directions remain later M7 feature work; they should follow the inspector and renderer telemetry foundations rather than be mixed into this continuity slice.

## M7-B Japanese UI and product-language slice · 14 November 2026

### Implemented

- Added a shared phrase-based Japanese localization layer for the existing Qt interface. Static labels, group titles, button text, combo-box choices, placeholders, workspace tabs, menu actions, tooltips and accessible names are translated on startup when Japanese is selected.
- Added language-specific application font families. English uses Segoe UI with Noto Sans / Arial fallbacks; Japanese uses Yu Gothic UI, Meiryo UI and BIZ UDGothic before Noto Sans JP / Noto Sans CJK JP fallbacks. These are system font names, not bundled font assets.
- The musical timeline no longer renders the long payload explanation as a permanent ACTION label. Each event type places its explanation on the JSON payload editor as hover help, and the Japanese catalog includes those descriptions.
- Removed the asset browser's persistent “Select an asset…” instruction and shortened the initial AUTO PERF label. The remaining preview prompt and hidden dock helper sentences were reduced to concise state/section labels. The generator panel's live feedback area remains because it reports actual actions and errors rather than static onboarding copy.
- Moved video / animated-image / still-image overlay guidance to contextual hover help. This removes a stale reference to an overlay hint label that was never constructed; selecting an overlay no longer depends on that missing widget.
- Added regression tests for Japanese control translation, preserved user-entered text, translated tooltips, font preference order, timeline hover-help behaviour and image-overlay selection/help.
- Added [PRODUCT_OVERVIEW.md](PRODUCT_OVERVIEW.md), an artist-facing description with practical audience fit and explicit “not for” cases.
- Added [WEBSITE_PLAN.md](WEBSITE_PLAN.md), defining an old-fashioned dark field-manual / archival website direction, application-matched colour tokens, navigation, downloads, manual/wiki structure and a Markdown-first content-source map.

### Audience fit grounded in current capabilities

The strongest fit is **VJs and live visual performers**: the four-deck collage, live layer controls, effects, scenes, macros and projector output form the centre of the application.

Other credible use cases are **electronic musicians and Sonic Pi performers** who want OSC-controlled visuals; **audiovisual/media artists** combining prepared footage and procedural material; **generative artists and creative coders** who want an existing composition/performance surface; and **typography-led artists** working with animated English/Japanese text.

The product overview also explains where the application is not a good substitute: conventional non-linear editing, DAW/audio production, full 3D authoring or final master recording. These are capability-based audience hypotheses, not conclusions from user surveys or market research.

### Remaining work and acceptance boundary

- Japanese localization now includes translated dynamic status/error templates, dialog prompts, multiline confirmation copy, table/tree headers and progress-bar formats. Some native Windows file-dialog chrome and external runtime-provided names remain OS-controlled or source-dependent.
- The Settings language selection now updates the application font stack and retranslates the live widget tree without restarting. Dynamic text setters retain their source string, so changing back to English restores the original text rather than translating user-entered content.
- The English/Japanese website is implemented as plain HTML/CSS. The only website HTML file at the repository root is `index.html`; all other pages, localized guides and the shared stylesheet are organized under `site/`. The Markdown reference corpus remains under `docs/` for LLM/development use. GitHub Pages should use **Deploy from a branch → main → /(root)**.
- The Japanese Windows typography proof now loads a test-only Noto Sans JP font in CI, checks glyph coverage and renders an image. This validates the translation/font path in the runner, not installed font availability on every target Windows PC.
- Automated UI tests cover translation mechanics, tooltip behaviour, dynamic dialog/status copy and table/progress labels. Actual visual QA on the user's Windows machine, especially projector layout and long-duration operation, still requires target-hardware review.

Remaining product-language work is now mainly coverage of native OS dialogs and source-dependent dynamic strings, followed by a broader visual redesign of high-density inspector panels and quick/advanced control grouping without removing functionality.

## M7-B typography and build handoff · 15 November 2026

- Completed the desktop typography pass across ordinary labels, list/table rows, combo and numeric values, action buttons, checkboxes, group captions, menus, dock titles and tooltips. Display headings remain Newsreader / Georgia in English and Yu Mincho / Noto Serif JP in Japanese; technical controls use DM Mono with system monospace fallbacks; editable text fields retain the Windows sans-serif stack.
- The application does not bundle font binaries and adds no font-related Python dependency. The UI uses installed system families and remains readable when the preferred face is absent.
- The Windows build now derives its executable display name and icon from `config.py`, checks `config.APP_VER` against `pyproject.toml`, validates the final `eli-lab-mark.ico` before packaging, and records resolved package versions in the build report.
- Runtime requirements remain aligned between `pyproject.toml` and `requirements.txt`. The `dev` extra now includes both Ruff and pytest, matching `requirements-dev.txt`.
- Build/test acceptance: compile, Ruff, pytest and the Japanese typography proof run in the Windows Quality workflow. The local one-file build additionally runs `pip check`, import checks and the packaged `--self-check`. Actual GUI, OpenGL/projector and sustained-performance acceptance still requires the Windows performance machine.
# SONATA Expanded — Sonic Pi / AVTranslator Integration Notes

## Source inspected

Repository: [`ilyaminineli/sonicpi_eli_lab`](https://github.com/ilyaminineli/sonicpi_eli_lab)  
Patch: [`04_LIVE/SEULPIRLEAMBACY/SONATA_expanded.rb`](https://github.com/ilyaminineli/sonicpi_eli_lab/blob/main/04_LIVE/SEULPIRLEAMBACY/SONATA_expanded.rb)

The M4 sender is installed in the live patch at the musical control points only. It does not instrument the 93 synth/drum loops.

## Musical clock and form

- Tempo: **92 BPM**.
- Meter: **4 beats per bar**.
- Form: **384 bars**, approximately **16 minutes 42 seconds** at 92 BPM.
- Structure: **16 scene changes**, including the final `end` scene.
- The bar clock increments `sp_b_count`, cues `sp_b`, then sleeps for four beats.
- Scene changes update `sp_sc` and `sp_int`, then cue `sp_sc_change`.
- The synchronized macro loop updates `sx_m_e` (energy), `sx_m_c` (filter cutoff) and `sx_macro_phr` (phrase index).
- The local `F:` sample root remains Sonic Pi's responsibility; AVTranslator does not index those samples.

## Stable scene IDs and intensities

| Scene ID | Duration | Intensity |
| --- | ---: | ---: |
| `in` | 16 bars | 0.12 |
| `exp` | 24 bars | 0.28 |
| `tm_a` | 24 bars | 0.45 |
| `trns` | 16 bars | 0.34 |
| `dev` | 32 bars | 0.62 |
| `fr` | 32 bars | 0.84 |
| `ssp` | 24 bars | 0.24 |
| `rtrns` | 16 bars | 0.46 |
| `rc` | 16 bars | 0.70 |
| `rc_w` | 40 bars | 1.00 |
| `peak` | 56 bars | 1.00 |
| `intd` | 24 bars | 0.30 |
| `s_s` | 28 bars | 1.00 |
| `rls` | 24 bars | 0.42 |
| `c` | 12 bars | 0.14 |
| `end` | final marker | 0.00 |

`sp_b_count` increments before `sp_b` is cued, so OSC `bar_index` is **1-based**.

## Patch sender configuration

At the top of `SONATA_expanded.rb`, the helper exposes three values:

- `$sp_av_enabled = true` — set to `false` for an audio-only rehearsal.
- `$sp_av_host = "127.0.0.1"` — explicit AVTranslator bind address.
- `$sp_av_port = 57121` — match the UDP port shown in the AUD / CTRL dock.

A unique session identifier is generated at patch start from a wall-clock timestamp with a microsecond component; it does not depend on the patch's seeded musical random generator, so rapid restarts receive distinct IDs. A shared sequence counter increments for each outgoing message inside a short mutex-protected sender section, so concurrent musical loops cannot reuse or reorder sequence numbers. The helper uses Sonic Pi's `osc_send(host, port, path, *args)` API and does not depend on Sonic Pi's incoming OSC port. If AVTranslator is closed, local UDP sends are harmless; the patch's audio structure and cues continue to run.

## One-button autonomous connection

1. Prepare the composition and choose the local audio source in AUD / CTRL. For actual analysis of the sound playing from Sonic Pi, select the system-loopback device. Choose Sonic Pi macros only to run without local audio capture.
2. Verify the OSC bind address and port. Same-computer use defaults to 127.0.0.1:57121. COPY SONATA SETTINGS copies the address and port lines for the patch.
3. Press PERF MODE in the main toolbar. The application starts the OSC receiver automatically, starts the selected local audio capture if requested, installs missing default modulation curves and AUTO PERF assignments, and arms phrase-aware automation.
4. Run SONATA_expanded.rb in Sonic Pi. The first transport/start or clock/bar packet switches the mode from ARMED to LIVE and starts AUTO PERF. Scene changes and phrase cues then drive visual variations.
5. Watch AUD / CTRL for receiver freshness, audio source state, modulation outputs and AUTO PERF status. Stop SONATA to stop automation; press STOP PERF MODE to release resources owned by the mode and restore generated mapping baselines.

The mode may also reuse an OSC receiver that was started manually. It will not close a receiver or audio stream that was already running before Performance Mode took ownership. Sonic Pi is an OSC control source, not an audio-device entry: normalized energy/cutoff and transport continue to work without local audio capture, while system loopback adds real audio-band/onset analysis.

For a remote Sonic Pi computer, bind to the AVTranslator computer's reachable LAN IPv4 address and set $sp_av_host to the same address. Do not use 127.0.0.1 for a remote sender; loopback only reaches the machine on which the receiver runs.

## Version 1 wire protocol

Namespace: `/eli_lab/v1`. Every event begins with a string session ID and positive integer sequence number. Sequence numbers increase across all event types for one patch run. Restart the patch to generate a new session ID.

| Address | Arguments after session ID + sequence | Event |
| --- | --- | --- |
| `/transport/start` | BPM (float), beats/bar (int) | `transport.start` |
| `/transport/stop` | none | `transport.stop` |
| `/transport/tempo` | BPM (float) | `transport.tempo` |
| `/clock/bar` | 1-based bar (int), BPM (float), beats/bar (int) | `clock.bar` |
| `/scene/select` | scene ID (string), intensity (float 0..1), bar (int; `0` only for the initial pre-clock scene marker, otherwise 1-based) | `scene.select` |
| `/scene/intensity` | intensity (float 0..1) | `scene.intensity` |
| `/macro/set` | name (`energy`, `cutoff`, `chaos`, `density`, `depth`, `decay`, `pressure` or `fragment`), value (float 0..1) | `macro.set` |
| `/cue/trigger` | cue name (identifier) | `cue.trigger` |
| `/source/heartbeat` | none | `source.heartbeat` |

The initial `in` scene is announced before the first clock tick and therefore carries `bar_index=0` as a pre-clock marker; the first `/clock/bar` is bar 1. Every subsequent scene event is emitted after the preceding scene's bar-counted form block and carries the current 1-based bar index. The cutoff normalization is `clamp((sx_m_c - 48.0) / 70.0, 0.0, 1.0)`. Energy is already normalized in the patch. Macro messages are sent once per bar; a phrase cue is sent on four-bar boundaries. The M6 Performance Macro receiver also accepts the six built-in names `chaos`, `density`, `depth`, `decay`, `pressure` and `fragment` on this same route. Each updates its normalized 0–1 macro value and can drive multiple master/per-layer targets. The existing SONATA patch continues to use `energy` and `cutoff`; no change to its 93 loops or its existing sender is required. Bar messages are emitted once per bar, and a separate heartbeat is sent every four bars. The application treats SONATA as clock authority, disables its internal test clock on `transport/start` or, as a packet-loss fallback, the first accepted `clock/bar`, and derives the M3 `transport.phase` modulation source from the most recent bar clock. Macro values feed the existing M3 modulation matrix and the generated M5 routes/modulators, including smoothing, hold, lock, manual-override and intensity-ceiling behaviour.

### M5 Modulator Bank connection

M5 consumes the same M4 signals without changing the OSC protocol or the SONATA patch:

- `macro.energy` and `macro.cutoff` are available as direct layer-modifier sources and as inputs to reusable **Control Follower** modulators.
- Both macros can trigger ADSR envelopes using a configurable normalized threshold.
- Control Followers can be assigned to waveform amplitude/frequency, geometry, text, particles and other compatible layer targets. A follower can drive multiple assignments; no additional OSC message is needed per visual object.
- Follower attack/release smoothing interpolates the once-per-bar SONATA macro updates at the application tick rate.
- A macro source is considered stale after a bounded window (at least five seconds or two current bars, whichever is longer). Stale values are omitted, so follower assignments release to their baselines instead of holding the last received cutoff/energy value.

The 93 SONATA audio loops remain untouched. OSC still carries only the transport, scene, macro and cue intent described above.

For example, an additional live patch can set CHAOS to 0.75 with `/eli_lab/v1/macro/set` followed by its normal session ID, next sequence number, the string `chaos` and a float value `0.75`. The same route accepts the other five built-in macro names. Values outside 0–1 and unregistered names are rejected; OSC macro values remain live for at least five seconds or two bars, whichever is longer.

## Receiver safety and application threading

- Default bind is loopback; binding to another interface is an explicit user choice.
- Only known versioned addresses, exact argument counts, strict OSC types, registered macro names and safe numeric ranges are accepted.
- Session IDs are retained in a bounded 64-session replay history and cannot be reused within that window. Packets from a superseded session and duplicate/out-of-order sequences are rejected.
- Input is rate-limited (60 messages/second by default) and the M3 event queue remains bounded.
- The receiver runs on one dedicated daemon worker. It only creates validated `ControlEvent` objects and submits them to the queue.
- The main application tick drains a bounded number of events, updates performance-control state and applies modulation. Qt widgets, composition state and OpenGL resources are never touched by the OSC worker.
- The AUD / CTRL dock shows listening/live/stale status, last address, active session, accepted/rejected/dropped counts and last packet age.

A lost packet does not block the clock: the next bar or macro packet is handled independently. Malformed datagrams are discarded and counted; the receiver remains available. A stale sender is recovered by restarting SONATA with a fresh session ID. If STOP PERF MODE was pressed, arm Performance Mode again before restarting the patch; the mode starts or reuses the receiver automatically.

## Test without Sonic Pi

With AVTranslator running and OSC started on loopback port 57121:

    python scripts/osc_test_sender.py --host 127.0.0.1 --port 57121

The script sends start, bar, scene, energy/cutoff, heartbeat, phrase and end events. It is a manual diagnostic sender. The repository's former unit-test suite was removed at the user's request; current CI performs compilation and Ruff checks only.

## Live rehearsal checklist

1. Start AVTranslator and press PERF MODE. Confirm the receiver is listening on `127.0.0.1:57121` and the mode is ARMED.
2. In Sonic Pi, leave `$sp_av_enabled = true`, verify host and port, then run SONATA. Confirm the mode moves to LIVE.
3. Confirm BPM 92, bar positions 1 through 384, all 16 scene IDs, energy/cutoff movement, four-bar phrase cues and final stop.
4. Stop/restart the patch and confirm the new session is accepted while delayed packets from the prior session are rejected.
5. Press STOP PERF MODE and confirm SONATA audio continues. Re-arm Performance Mode, restart SONATA and confirm a fresh OSC session becomes LIVE.

**Validation boundary:** the OSC protocol and sender insertion are implemented. The complete 384-bar performance has not been executed inside Sonic Pi by the current quality workflow; timing and machine-specific rehearsal remain a manual sign-off.
