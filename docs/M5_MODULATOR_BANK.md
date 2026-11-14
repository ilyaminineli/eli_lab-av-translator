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

Active modulators and user presets are saved in the current AV Translator project. Imported/exported preset files can be reused in other projects.

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
