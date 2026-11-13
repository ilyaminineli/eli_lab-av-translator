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

The Audio / Control dock also has two route presets: **ADD AUDIO-REACTIVE ROUTES** and **ADD SONIC PI ROUTES**. They add starter mappings from audio bands/onsets or Sonic Pi energy/cutoff and transport state. Existing operator-authored routes are preserved; the presets do not silently replace a route that already owns a target.

Generator targets act on the currently selected, unlocked, compatible generator. Overlay playback targets apply only to an animated image overlay. Auto Performance targets change the corresponding live director settings; locks and manual overrides continue to take precedence. The modulation worker boundary remains unchanged: routes are evaluated on the application tick, not in audio or OSC workers.

### 4. Persistence and lifecycle

- Projects persist transport settings, audio analysis configuration, modulation routes and scene profiles.
- Projects do not persist live input-device handles, running capture threads, replay buffers or live analysis frames.
- Older projects without M3 performance settings load safe defaults.
- Project load/reset and application shutdown stop capture, clear transient audio data and reset modulation runtime state.

### 5. UI and application integration

- New dock: **AUDIO / CONTROL**.
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
