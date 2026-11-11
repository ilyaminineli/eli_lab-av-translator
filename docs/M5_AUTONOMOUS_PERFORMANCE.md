# M5 — Autonomous Performance Mode

## Operator workflow

The intended live workflow is deliberately short:

1. Prepare a composition with video decks and/or generator layers.
2. In AUDIO / CONTROL, select a system-loopback device for local FFT analysis, or select Sonic Pi macros only.
3. In AUTO PERFORMANCE, choose a style, musical synchronisation mode and session duration. The default is Generative + Phrase synchronised + Until stopped.
4. Press PERFORMANCE MODE in the main toolbar.
5. Run SONATA Expanded in Sonic Pi.
6. Perform. Stop the Sonic Pi patch to stop AUTO PERFORMANCE at its transport/stop event; press STOP PERFORMANCE MODE to release resources and generated routing.

Performance Mode starts the OSC receiver automatically using the address and port in AUDIO / CONTROL. The default is 127.0.0.1:57121. The receiver may already be running; in that case, the mode reuses it and does not claim ownership of it.

The first accepted Sonic Pi transport/start or clock/bar event changes the mode from ARMED to LIVE and starts the armed AUTO PERFORMANCE session. Starting the mode before running the patch is therefore safe: it waits for Sonic Pi rather than inventing a local musical clock. If the patch is already running and its OSC stream is still live, AUTO PERFORMANCE starts immediately when the mode is armed.

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

### Modulator Bank

Performance Mode ensures the built-in Sonic Pi energy/cutoff followers, beat/onset envelopes and phrase LFO exist. These become reusable named sources in the Modulator Bank and can feed multiple compatible layer targets. Existing modulator definitions with those AUTO names are re-enabled rather than duplicated.

### AUTO PERFORMANCE

The mode arms AUTO PERFORMANCE and waits for the Sonic Pi transport. Phrase/scene cues then drive random, structured or generative visual decisions. Generative mode increases variation with energy and intensity; scene IDs classify sections such as intro, development, peak, breakdown and outro. Cut probability, segment length, layout/effect/generator intervals and loop/switch probabilities are also modulation targets.

In Phrase mode the scheduled wall-clock randomizer is gated off. Changes are evaluated at phrase/scene cues; bar events can add small generative cuts in Bar/Hybrid modes. Time and Hybrid settings retain interval-based behaviour. This avoids two independent random schedulers fighting the musical form.

If no playable video clips are loaded, AUTO PERFORMANCE can still operate on generators, text, layout, overlays and effects. Video cuts are simply skipped until footage is available.

## State and ownership

The mode tracks whether it started the OSC receiver and audio capture. Stop only closes services the mode owns. A receiver or audio stream that was already running before the mode started remains available afterward. When SONATA sends transport/stop, the current AUTO PERFORMANCE pass stops and the mode re-arms; running the patch again starts a fresh pass without toggling Performance Mode.

Generated defaults use stable AUTO identifiers. Stop disables only those generated routes, Modulator Bank definitions and per-layer modifiers, evaluates the release path, and restores their baselines. User-authored routes and modifiers remain configured and enabled.

Saving a project or performance set while Performance Mode is live writes the generated defaults as disabled. A project therefore opens in an idle state; pressing Performance Mode re-enables the defaults. The saved plan retains receiver address/port, local audio selection, automation style/sync and session duration, but not active hardware handles, worker threads or a live session state.

## Diagnostics and recovery

The AUDIO / CONTROL mode status displays OFF, ARMED, LIVE or DEGRADED. Its tooltip and the application diagnostics expose OSC status/counters, last-message age, audio state/queue/drop counters, bounded control queue state, active route/modulator counts, AUTO section/energy/cutoff and video/decode/render metrics. The main status bar follows the active projector renderer when a projector window is open; when the local preview dock is hidden, it explicitly reports LOCAL PREVIEW IDLE rather than implying that the projector's OpenGL context failed to initialise.

If Sonic Pi is not started, the mode remains ARMED. If its OSC stream becomes stale, the mode returns to a waiting state and stale musical macros expire. If local audio capture fails, the mode continues in Sonic Pi-macro mode. A receiver startup failure is shown as DEGRADED and can be corrected by stopping/rearming the mode.

## Validation boundary

The software lifecycle and source/target wiring are implemented. Target-machine validation is still required for the actual 384-bar SONATA rehearsal, loopback device selection/reconnect, long-duration performance and projector behaviour. This milestone does not claim master-output video recording or audio/video muxing; those remain separate delivery items.
