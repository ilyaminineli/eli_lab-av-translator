# M6 — Advanced VJ Environment

**Status:** M6-A1, M6-B1, M6-C1, M6-D1/D2 and M6-E1 are merged to `main`. E1 delivers rich runs, practical vertical layouts, text paths and texture-space GPU animation; E2 glyph instancing and E3 presets/text feedback remain future slices. This live-performance follow-up adds AUTO PERFORMANCE targets for the newer typography, layer-FX and Particle System 2.0 controls, continuous particle emission, adaptive compact/4:3 workspace sizing, and a Queer text pool. Target-Windows GPU and projector validation remains open.  
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
- Respect layer/deck locks and manual ownership; AUTO PERFORMANCE must not unexpectedly replace a manually protected source.
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

**The Performance Macro System is merged to `main` in PR #30.** Six built-in macros — CHAOS, DENSITY, DEPTH, DECAY, PRESSURE and FRAGMENT — fan one 0–1 control value out to multiple master and compatible per-layer targets. They can be driven manually, by keyboard toggle, MIDI CC/note, OSC, audio/transport sources or Modulator Bank outputs. The macro definitions and assignments are persisted with projects and performance sets.

See [M6 — Advanced Performance Controls](M6_ADVANCED_PERFORMANCE_CONTROLS.md) for the full source, routing, persistence and validation boundaries.

## G. Live Performance Timeline

**The initial timeline implementation is on `m6/live-performance-timeline`; it is not yet merged.** The timeline is a project-persisted bar/beat show plan that runs beside the internal or Sonic Pi transport.

Supported event types are scene markers, phrase markers, saved-scene recall, deck/clip triggers, master effect changes, Text Art regeneration, palette changes, Performance Macro modulation and transition cues. Each event has an authored bar/beat, label, enabled state and validated JSON payload. Same-beat events run in insertion order.

The LIVE PERFORMANCE TIMELINE dock exposes the event list, editor, arm/disarm, rewind and the eight-section example structure. Event actions use existing app services and are processed on the application/UI tick. AUTO PERFORMANCE and Modulator Bank modulation can continue generating variation inside the timeline structure.

Sonic Pi currently reports one clock event per bar. The timeline interpolates beat positions locally from that packet's BPM and timestamp; this is not a per-beat OSC clock or frame-accurate sync. Scene transitions retain the current numeric morph and discrete cut behaviour. Project loading restores timeline definitions but does not automatically arm playback.

See [M6-C — Live Performance Timeline](M6_LIVE_PERFORMANCE_TIMELINE.md) for event payloads, clock handling, persistence, limits and acceptance checks.
