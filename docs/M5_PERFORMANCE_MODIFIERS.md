# M5 — Per-Layer Performance Modifiers

## Purpose

The global Modulation Matrix is useful for broad mappings, but it is not enough when a composition contains several generators that should respond differently. A per-layer modifier stack gives every layer its own explicit source-to-parameter objects.

Modifiers are stored in the owning Layer record and travel with the composition. They are evaluated on the application tick, after normalized audio, transport and Sonic Pi control sources have been collected. Audio and OSC workers do not modify layers, widgets or GPU resources.

## Where to find it

1. Select a layer in the LAYERS dock.
2. Open PERFORMANCE MODIFIERS · PER LAYER beneath SELECTED LAYER TRANSFORM.
3. Choose a source, target, response curve, polarity and depth.
4. Click ADD MODIFIER, or use one of the quick rhythmic buttons:
   - BEAT — add a short pulse on every beat.
   - DOWNBEAT — add a pulse on the first beat of each bar.
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

Modifier definitions are saved with each layer. Runtime smoothing, live meter values and temporary manual-override timers are not persisted. While saving, AV Translator writes the pre-modulation parameter values into the project snapshot; the live composition continues running unchanged. Reopening a project starts with its saved baseline and its modifier definitions, ready for a new transport/audio/Sonic Pi session.
