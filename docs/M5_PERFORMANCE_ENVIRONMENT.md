# M5 — Performance Environment

## Scope and status

M5 connects the M3 transport/audio layer, M4 Sonic Pi bridge, per-layer modifier stacks, Modulator Bank and AUTO PERFORMANCE into a one-button autonomous show. The M5 software implementation is merged to `main`. Live SONATA, audio-device and target-projector acceptance remain manual validation tasks; master-output recording and audio/video muxing are not implemented and are tracked as a separate deferred deliverable.

Press PERFORMANCE MODE, then run SONATA in Sonic Pi. The first transport/start or clock/bar event starts the armed generative session; phrase and scene cues drive visual changes. The normalized mapping contract remains shared across video layers, geometry, text, waveform, particles, animated overlays and AUTO PERFORMANCE.

## Unified mapping coverage

| Domain | Supported target families |
|---|---|
| Composition geometry | opacity, position X/Y, scale, rotation |
| Procedural geometry | motion speed/amount, density, rotation |
| Text Art | animation speed/amount, font size, letter spacing |
| Waveform | amplitude and frequency |
| Particles | speed, size, spread, trails |
| Animated overlays | playback speed and frame hold |
| AUTO PERFORMANCE | cut/segment timing, layout/effect/generator intervals, loop/switch probability |
| Master output | global modulation matrix effect targets |

Audio bands, onset/beat confidence, normalized transport phases/pulses, scene intensity, Sonic Pi energy/cutoff and Modulator Bank sources are shareable inputs. A target is offered only when its owner can apply it. Per-layer modifiers retain their current baseline, lock, manual override and ownership rules.

## Autonomous Performance Mode

See [M5 Autonomous Performance](M5_AUTONOMOUS_PERFORMANCE.md) for the operator sequence. The mode starts or reuses OSC, optionally starts loopback capture, enables generated default routes/modulators/layer curves, and waits for Sonic Pi. Sonic Pi energy/cutoff and scene/phrase events can drive the visual performance even when no audio device is selected. A system-loopback device adds real audio-band/onset analysis.

The default global routes cover master look, clip switching, cut timing, segment length and automation intervals. Per-layer AUTO curves cover video, geometry, text, waveform, particles and animated overlays. Defaults use stable IDs and are non-destructive: custom routes are kept, generated mappings are disabled when the mode stops, and saving an active show stores those generated mappings disabled.

AUTO PERFORMANCE supports random, structured and generative styles with time, bar, phrase and hybrid sync. Phrase mode uses musical cues instead of a parallel wall-clock randomizer. If the footage pool is empty, generators, text, effects and layout automation can still run.

## MIDI controls and performance sets

The optional MIDI adapter uses `mido`; native `python-rtmidi` is an optional backend, not a startup dependency. Device discovery is explicit. Port callbacks enqueue compact normalized events into a bounded queue; the application tick drains them and applies mappings outside the callback. The AUDIO / CONTROL panel exposes discovery, connect/disconnect, Learn Next Controller, a target selector, per-mapping range/curve/pickup editing, and mapping update/removal.

Mappings support CC, note and pitch wheel messages, device/channel/number filters, target IDs, min/max scaling, linear/smoothstep/exponential curves and pickup. Pickup holds until the incoming physical control crosses or approaches the current virtual value. Mapping definitions persist, but physical positions and pickup latch state do not. Device loss is local and does not stop the performance.

Performance scenes are named snapshots with quantized recall and smoothstep morphing for compatible numeric targets. A versioned `.eliset` performance set can store composition/deck state, master effects, AUTO PERFORMANCE settings, transport/audio settings, global modulation routes, Modulator Bank, MIDI mappings and scene snapshots. It is separate from `.eliav`, allowing one composition to be reused across live sets.

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
