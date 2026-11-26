# Architecture

## Product and runtime boundaries

eli_lab AVTranslator is a Windows-first live audiovisual/VJ performance environment with native packaging for Windows x64 and Linux x86_64. The application combines four independent video decks, composition layers, procedural generators, overlays, GPU effects and renderer-independent performance controls. M5 adds autonomous show orchestration and a shared asynchronous generator-raster pipeline; M6 adds the VJ scene, transformation, particle, typography and live-performance foundations. M7 is evolving the application into a generative visual composition instrument. Its governing design reference is the [IDM Visual Instrument manual](guides/IDM_Visual_Instrument_Visual_Composition_Generative_Art_and_Live_Concert_Architecture.md).

The main ownership boundaries are:

- **UI** owns Qt widgets, editor state, dock/window lifecycle and operator controls.
- **Application core** owns the composition, project state, service coordination, event application and automation/performance ticks.
- **Media** owns discovery, metadata, thumbnails, decoder workers and bounded video/image frame queues.
- **Generators** own normalized settings, CPU rasterization and the application-shared raster job service.
- **Rendering** owns per-window OpenGL resources, video/generator textures, composition and post-processing.
- **Effects** own master and per-layer effect settings/presets.
- **Performance control** owns normalized transport, scene, audio, OSC/MIDI, modulation, modifier and Performance Mode state.
- **Visual model** owns renderer-independent object identity, role/material descriptors, lineage, mutation contracts and visual-event data. It references composition layers but owns no Qt or GPU resources.

Worker threads publish immutable or copied CPU-side data. They do not update Qt widgets, mutate the composition or create/change OpenGL resources.

## Visual identity and event lifecycle

M7-C0 adds a renderer-independent visual ontology without replacing the existing Layer composition model.

- Each Layer has a stable visual_object_id. The field is appended to the dataclass to preserve existing positional constructor compatibility.
- Composition owns the authoritative visual_objects registry. Each VisualObject references exactly one renderable layer in the current C0 model.
- Composition.add_layer registers the object, remove_layer removes the paired object, and replace_layer atomically replaces both the renderable layer and its identity record.
- A source-defining change through LayerManager.update_layer creates a new VisualObject ID and records the previous object as its lineage parent. Ordinary transform changes retain identity.
- Object identity stores role, material, geometry/palette/motion traits and provenance separately from transient layer transforms.
- VisualMutationContract is enforced by the LayerManager candidate/commit boundary, VisualEvent executor actions and the injected VisualMutationAdapter. The adapter is shared by AutomationDirector, the Application's ModulationMatrix target writer and LayerPerformanceModifierEngine. It runs mutations on detached Layer candidates, computes a bounded top-level diff and commits through LayerManager; rejected changes never reach the live composition. Generic transforms preserve object identity; source-defining changes require explicit source_replacement intent and create lineage. Lock checks are repeated at commit time. Operator locking cancels the layer's live AUTO PERF morph and restores temporary AUTO PERF and per-layer modifier baselines before writing the lock bit; locked layers therefore cannot be left receiving future automated writes. Existing manual-override windows and ownership rules remain in their originating performance-control engines.
- Composition layer replacement/removal update the existing layers list in place, keeping runtime services that bind to that list from retaining a stale reference after an automated mutation. The identity registry is still staged and swapped atomically. Historical default mutation allow-lists are migrated in memory to include the added settings fields; custom allow-lists are not widened.
- VisualEvent is renderer-independent and bar/beat events can be embedded in the existing PerformanceTimeline. The existing transport/clock, one-shot cursor and bounded application tick remain the only timing infrastructure. Timeline bar/beat is 1-based; same-position events fire in stable authored order; duplicate timeline and embedded visual-event IDs are rejected; late arrivals behind the cursor are not replayed; rewind/restart makes later events eligible again. Immediate and performance-seconds dispatch remain unscheduled. Initial execution is limited to reveal, conceal, fade, move and rotate; missing or locked targets are skipped.
- Legacy compositions with no visual_objects field synthesize one legacy object per layer during loading. Project schema version 2 remains unchanged because the new composition data is additive and optional.
- Performance-scene recall preserves a locked live layer's VisualObject through Composition.replace_layer rather than mutating the candidate layer list directly.

The ontology must remain independent of GPU state. Preview and projector may share the same serialized VisualObject data, but each output continues to own its own GL context, textures, feedback history and particle simulation.

## Rendering lifecycle

1. Qt creates a `QOpenGLWidget` context for the local preview or projector output.
2. `PerformanceView.initializeGL` creates that window's ModernGL wrapper and compositor.
3. Each video decoder produces timestamped CPU frames into its bounded queue. PyAV random-access seeks are attempted when available; if the container rejects a seek with `av.error.PermissionError`, the decoder falls back to sequential reading and discards frames until it reaches the requested timestamp. Genuine open/decode failures remain fatal and are reported normally.
4. The application tick consumes each deck queue and updates shared latest-frame snapshots.
5. Preview and projector renderers read the same CPU snapshots independently.
6. Each `RenderEngine` uploads only unseen revisions into textures owned by its own GL context.
7. The compositor blends visible video, generator and overlay layers into ping-pong framebuffers, applying per-layer FX.
8. The master GLSL pass applies tonal processing, geometric remapping and optional layer-texture displacement.
9. When enabled, a renderer-local feedback engine samples its own bounded GPU history ring and writes the next history frame; no history texture is read back to the CPU or shared between output contexts.
10. The final framebuffer is drawn into that output window's Qt framebuffer.

The two outputs share application/composition state and CPU frame snapshots. They do **not** share GL texture objects or GL contexts. The main Qt workspace also adapts its default dock constraints and sizing to compact/4:3 window shapes; saved user layouts are retained. Output rendering independently fits the project's configured composition canvas to the target aspect ratio without stretching (letterbox fit). Feedback history is also per-renderer: preview and projector maintain independent GPU rings that are resized, reset and released with their own GL context. Project files persist feedback settings and reset generation, never frame history or GL handles.

## GPU particle simulation lifecycle

The legacy `particles` generator remains a procedural shader field in the layer compositor. The separate `particle_system_2` generator is owned by each output's `Compositor` and never uses the shared CPU generator-raster worker.

- Each particle-system layer owns ping-pong RGBA32F state, metadata and source-target textures with framebuffer pairs. Position, velocity, age, lifetime, respawn cycle, size variation and optional reformation targets remain on the GPU.
- Simulation advances at a fixed 60 Hz step with at most four substeps per render. Spawn randomness is derived from the configured seed, particle index and respawn cycle; no CPU particle arrays are updated per frame.
- A deterministic per-substep birth gate spreads particles over time according to the configured emission rate. The requested particles/second is divided across populations; AUTO PERF may modulate rate, speed, size, lifetime, turbulence, force, trail persistence and source reformation from live beat/onset/energy signals.
- Systems remain resident for up to six seconds after a layer becomes temporarily inactive, preserving simulation/trail continuity across brief cuts. Removed, failed or expired systems are released; output teardown releases all renderer-local resources.
- Point/circle/rectangle/path emitters are evaluated in the simulation shader. Video-luminance, image alpha/luma silhouette and contour emitters sample an existing layer texture with a bounded deterministic candidate search on respawn; sampled local coordinates are mapped through the source layer's transform.
- When reformation is active, particle target coordinates are periodically refreshed from the current source frame. A GPU spring force returns particles toward those source positions, allowing footage to break apart and re-form without CPU particle updates.
- A system contains one to four independently seeded populations. They share physics settings in D1/D2 but have stable emitter offsets and visual variation.
- Particle sprites accumulate into a pair of renderer-local RGBA8 trail targets at half output resolution. The resulting texture enters the normal layer compositor, so position/scale/opacity/blend and layer effects remain shared with other layers.
- The compositor enforces at most four active Particle System 2.0 layers and 16384 particles total per output, with at most 8192 per system. Allocation follows layer order so the resource ceiling is deterministic. State, metadata and source-target ping-pong storage uses approximately 96 bytes per particle (about 768 KiB at 8192 particles), before driver overhead.
- Layer removal, output resize and context teardown release simulation, path, source-target and trail resources. Projects and VJ scenes persist the settings, normalized path points and seed, never GPU state textures or transient particle positions.

Preview and projector deliberately run independent simulations in their own GL contexts. A matching seed/settings yields the same deterministic spawn sequence, but neither renderer shares mutable simulation or trail resources.

## Generator raster lifecycle

Static generator rasterization is owned by one `GeneratorRasterService` created by `Application` and shared by all output renderers.

- The service uses a single condition-driven background worker. It creates CPU pixel arrays only.
- Requests carry a copied settings snapshot, dimensions, fingerprint and monotonically increasing per-layer revision.
- An ordered pending map holds at most one waiting snapshot per layer. A newer request replaces that layer's pending snapshot instead of adding an obsolete keystroke to a backlog.
- There is at most one active raster job globally. Starts are throttled per layer (8 Hz by default), waveform rerasterization is capped at 4 Hz, and text retains an additional global 4 Hz limit. Newer settings replace pending work while a layer is waiting for its next slot.
- Geometry and waveform live previews rasterize at 75% of the canonical dimensions (1200×675); text preview remains at 50% (800×450). The service API can still request canonical 1600×900 output.
- The renderer caches each layer's static-content fingerprint. GPU-only animation changes skip both fingerprint hashing and raster requests; a changed static setting recomputes the fingerprint and replaces the pending snapshot.
- Completion or failure is accepted only when the job's revision and fingerprint still match the newest request. Renderers validate again when receiving the signal and before uploading.
- The service caches the latest completed CPU snapshot. Each renderer performs its own upload only while its own GL context is current.
- Deleting layers, project reset/load and application shutdown invalidate pending/completed work. The previous valid texture can remain displayed while a replacement is generated or when a replacement fails.

Static text content and typography are rasterized on the CPU worker and cached by the existing latest-request-wins raster service. The E1 typography path supports up to 64 styled rich-text runs, horizontal mixed-language flow, vertical right-to-left / left-to-right composition, and circular, arc or custom-polyline text paths. Path point limits and rich-run payload limits are normalized before rasterization. A renderer uploads the completed CPU image only while its own GL context is current.

Text motion is kept separate from content layout. The compositor receives compact per-frame uniforms for type-on, word/column reveal, line wave, jitter, crawl, signal glitch, reverse reveal, dissolve, flicker, cell displacement, vertical reveal, scattered-cell displacement, segmented collision-style movement and mechanical scrolling. Changing these motion controls does not request a new CPU raster. The new E1 modes are texture-space shader treatments; they do not yet represent independently simulated/shaped glyph instances, semantic word collisions or character substitution. Vertical CJK layout is a practical column compositor with script-orientation heuristics, not a complete OpenType vertical-form/shaping implementation.

Text editing keeps a UI buffer separate from committed layer settings. The operator can pause live preview, commit after a typing pause, apply immediately, select 25/50/75/100% preview quality, request full-resolution 1600×900 output, rate-limit text raster starts, freeze the currently displayed texture and retain the last valid result after a failure. Pipeline state is exposed to the editor.

## Performance-control lifecycle

M3 introduced the normalized transport/audio/control model. M4 adds the versioned `/eli_lab/v1` OSC adapter. M5 connects those sources to Performance Mode, AUTO PERF, the Modulator Bank and per-layer performance modifiers.

1. Audio, OSC, MIDI and internal transport adapters validate input and publish normalized events or feature snapshots.
2. Network/device callbacks place bounded items into thread-safe queues; they do not mutate composition or UI state.
3. The application tick drains a bounded batch, updates performance-control state and evaluates modulation/modifiers.
4. Registered targets update existing layer, generator, effect or automation settings subject to range, lock, manual-override and ownership rules.
5. Performance Mode installs only missing defaults, tracks which services it started and releases only resources it owns when stopped.
6. Project files persist user-facing configuration and stable IDs, not live device handles, worker threads, active GL resources or transient signal buffers.
7. The Performance Macro engine evaluates one normalized source per built-in macro after Modulator Bank outputs are available. Its `performance_macro.*` sources fan into the same global target and per-layer modifier engines; no parallel effect/target engine is introduced.
8. Keyboard, MIDI and OSC macro updates are applied on the application thread. Continuous input is smoothed, manual input briefly takes priority, and OSC macro freshness follows the bounded musical-clock window.

Sonic Pi macros are normalized musical controls, not raw audio. System loopback is needed for local RMS/FFT/onset analysis of the sound output.

## Runtime resources and writable data

Read-only packaged resources (icons, textures, sketches and dictionaries) are resolved from the source tree during development or from the frozen application bundle at runtime. PyInstaller's one-file bootloader extracts bundled data into its runtime directory; bundled module `__file__` paths resolve inside that extraction root. The runtime hook also supplies safe stdout/stderr sinks for a windowed executable.

Writable data is kept separately under:

`%LOCALAPPDATA%\eli_lab\AVTranslator\`

This includes the SQLite media database, thumbnail cache and logs. User footage, project files and user-added asset roots remain external and are never written into the temporary one-file extraction directory.

## Packaging and checks

The local native one-file build is `scripts/build_pyinstaller.py`, using the repository-local `.venv` and `AVTranslator.spec`. It supports 64-bit CPython 3.12–3.14 on Windows x64 and Linux x86_64, installs the pinned build requirements, checks imports and dependencies, compiles the source, creates a one-file executable and runs its `--self-check`. Native `python-rtmidi` support is optional.

The manual **Cross-platform Versioned Builds** workflow builds Windows and Linux on their respective native runners in one dispatch, then creates versioned ZIP archives with selectable Stored, Deflate, BZIP2 or LZMA compression. See [Cross-platform builds](BUILD_CROSS_PLATFORM.md) and [Windows build troubleshooting](BUILD_PYINSTALLER_WINDOWS.md). CI does not replace target-machine GUI, GPU, audio-device or projector acceptance.

## Project data

`.eliav` projects persist composition/layers, deck assignments, effects, Performance Macro definitions/source assignments/shortcuts and performance configuration. VJ Scene snapshots include macro configuration and values. `.eliset` performance sets reuse project serialization and persist a reusable performance setup, including deck state, automation/performance settings, scenes and MIDI mappings. Composition serialization includes the VisualObject registry and stable layer associations. Media files are referenced by path and are not embedded. Runtime handles, GPU objects and transient frame/audio queues are recreated when a project/set is loaded.

## M6 direction

M6 — Advanced VJ Environment — is in active development. The current four video decks remain the playback foundation; M6 builds operator controls on the existing decode, composition and GPU ownership boundaries. The Performance Macro follow-up adds a shared 0–1 control layer above modulation and per-layer targets. See [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md) and [M6 Advanced Performance Controls](M6_ADVANCED_PERFORMANCE_CONTROLS.md).
