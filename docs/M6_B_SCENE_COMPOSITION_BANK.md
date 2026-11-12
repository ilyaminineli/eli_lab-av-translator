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
- OSC cue names must be unique within the VJ Scene Bank.
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
|---|---|
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
