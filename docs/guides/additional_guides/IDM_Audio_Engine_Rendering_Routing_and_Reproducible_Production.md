# Audio Engine, Rendering, Routing & Reproducible Production

## An Engineering and Production Architecture Manual for the IDM Generative Instrument

**Volume 9 of the IDM Generative Instrument documentation library**  
**Scope:** audio execution, instrument hosting, signal routing, mixing infrastructure, timing, real-time playback, offline rendering, reproducibility, export, and production validation.  
**Audience:** audio software developers, DSP engineers, generative-music researchers, technical producers, and developers responsible for turning musical data into dependable audio deliverables.

---

## Abstract

A composition system does not become a complete musical instrument when it can generate notes, patterns, motifs, or arrangements. It becomes a usable production instrument only when its musical decisions can be executed, auditioned, edited, rendered, inspected, reproduced, and exported without losing their meaning.

This manual defines the audio-execution and production architecture required by the IDM Generative Instrument. It explains how to represent a signal-processing graph; how instruments, effects, buses, sends, returns, sidechains, and master paths relate; how musical time is converted into sample time; how automation is scheduled; how latency is measured and compensated; how real-time playback differs from offline rendering; how preview and pre-render systems should behave; and how a finished production package can be made complete and reproducible.

The central architectural rule is separation with traceable contracts:

- the **composition model** describes what the music is;
- the **realisation plan** describes how musical material is assigned to sound-producing resources;
- the **audio graph** describes how signals are processed and routed;
- the **execution engine** schedules and runs that graph;
- the **render job** captures a specific, immutable production state;
- the **delivery package** preserves the output and enough provenance to understand or recreate it.

These layers must be connected, but they must not be collapsed into one mutable collection of tracks, plug-ins, callbacks, and file-writing functions.

This is an architecture manual, not a recommendation to adopt one framework, plug-in format, operating system, sample rate, or mastering target. The examples are reference designs. A production implementation may use JUCE, a custom C++ engine, SuperCollider, a plug-in host, a Python orchestration layer, an external renderer, or a hybrid. The contracts and invariants should remain valid across those choices.

---

# How to use this manual

## 1. Scope

This document owns the path from a prepared musical realisation to audible output and production delivery. It focuses on execution, signal flow, rendering, and reproducibility.

It does **not** redefine:

- the philosophy of the instrument;
- the ontology of motifs, patterns, phrases, sections, and musical material;
- the algorithms responsible for composition and candidate selection;
- perceptual orchestration and attention planning;
- the detailed synthesis and sound-design vocabulary;
- genre-specific arrangement grammar.

Those subjects are defined in the earlier volumes. This manual specifies how to realise and preserve their decisions in an audio system.

## 2. Relationship to the other volumes

| Volume | Responsibility | Relationship to this manual |
|---|---|---|
| Philosophy, Principles & Design Constitution | Governing principles and creative agency | Establishes why accepted decisions, editability, and reproducibility must be protected |
| Musical Ontology, Representation & Composition Data Architecture | Canonical entities, relationships, time, provenance | Supplies the musical and project data consumed by realisation and execution |
| Generative Intelligence, Algorithms & Decision-Making | Candidate generation, planning, selection, mutation | Supplies committed musical decisions and generation provenance |
| Perceptual Orchestration, Attention & Musical Scene Architecture | Listener-centred grouping, attention, density, scene roles | Supplies perceptual intent that may inform gain, spatial, routing, and arrangement decisions |
| Sound Design, Synthesis & Hybrid Sound Architecture | Sound sources, synthesis, sampling, DSP, effects as sound design | Supplies instrument definitions and sound-processing intentions |
| Composition Atlas | Track forms, patterns, phrases, development | Supplies the compositional structure to be realised |
| IDM Field Guide and Advanced Appendix | Broad musical and mathematical background | Supply domain knowledge, not engine implementation authority |

## 3. Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are used as implementation requirements:

- **MUST / MUST NOT**: required for a conforming implementation.
- **SHOULD / SHOULD NOT**: recommended unless a documented reason justifies another design.
- **MAY**: optional capability.

A project may support a feature partially, but it must report the unsupported or degraded behaviour rather than silently pretending to provide it.

## 4. The central rule: a render is a versioned realisation, not merely an audio file

A WAV file alone does not reveal:

- which composition revision produced it;
- which instrument and plug-in versions were active;
- which sample assets were referenced;
- which tempo map and automation were executed;
- which routing and effect states were used;
- how random or modulation seeds were initialised;
- which renderer, sample rate, channel layout, and export settings were selected;
- whether the file was a full mix, stem, freeze, preview, or intermediate.

Therefore, every production render MUST have a render manifest. The manifest is part of the work's provenance, not optional administrative metadata.

---

# Part I — The production architecture

## 5. The layers of the audio-production system

A dependable implementation separates at least eight layers.

### 5.1 Musical composition layer

Contains composition identity, sections, phrases, voices, roles, motifs, patterns, events, tempo and meter maps, and musical relationships. It says what should happen in musical terms.

Examples:

- a bass voice plays a transformed motif during Section B;
- a percussion role enters at a specified musical position;
- a phrase contains a note event with a defined pitch, duration, articulation, and expressive data;
- an automation gesture belongs to a phrase or sound object.

This layer MUST NOT contain a device handle, audio callback pointer, operating-system path that is required for musical identity, or an assumption about a particular plug-in host.

### 5.2 Sound realisation layer

Maps musical roles and voices to sound-producing resources:

- internal synthesiser;
- sample instrument;
- drum voice;
- external plug-in;
- resampling instrument;
- hybrid instrument;
- rendered audio asset;
- MIDI or network-controlled external device.

The realisation layer defines how a musical voice becomes one or more signal sources. It should preserve the distinction between a musical role, a voice, an instrument definition, and a concrete instrument instance.

### 5.3 Signal graph layer

Describes audio and control connections:

- instrument outputs;
- insert effects;
- sends and returns;
- subgroups;
- sidechain inputs;
- parallel paths;
- multichannel routing;
- master processing;
- output destinations.

This graph is independent from the arrangement's visual layout. Reordering tracks in the interface must not accidentally change the signal path.

### 5.4 Execution layer

Runs the signal graph and consumes scheduled events. It owns:

- audio-device interaction;
- block processing;
- real-time thread coordination;
- voice allocation;
- event dispatch;
- parameter updates;
- graph state transitions;
- latency reporting;
- underrun and overrun handling.

### 5.5 Render layer

Creates an offline or real-time capture from a defined state. It owns:

- render range;
- pre-roll and post-roll;
- effect-tail handling;
- channel layout;
- sample rate and sample format;
- deterministic settings;
- output file writing;
- interruption and recovery;
- render progress and diagnostics.

### 5.6 Analysis and metering layer

Measures the output and provides information about technical and production properties:

- sample peak;
- true peak estimate;
- integrated and short-term loudness where relevant;
- loudness range where relevant;
- RMS or energy statistics;
- DC offset;
- clipping;
- silence and dropout;
- channel correlation and balance;
- spectral and transient diagnostics;
- file integrity.

Measurements are evidence for a producer, not a substitute for listening.

### 5.7 Project persistence layer

Stores the composition, graph, instrument states, assets, automation, routing, render history, and version metadata. It must support safe saving, migration, missing-asset reports, and recovery.

### 5.8 Delivery layer

Builds a complete output package containing the requested mix, stems, MIDI, project data, assets or asset references, documentation, and render manifest.

## 6. Reference system topology

```text
                 COMPOSITION / MUSICAL MODEL
                            |
                            v
                    SOUND REALISATION
                            |
             +--------------+--------------+
             |                             |
             v                             v
       Instrument State              Event / Automation
             |                             |
             +--------------+--------------+
                            v
                     AUDIO GRAPH
                            |
               +------------+------------+
               |            |            |
               v            v            v
            Preview       Realtime      Offline
            Renderer      Playback      Renderer
               |            |            |
               +------------+------------+
                            v
                    ANALYSIS / METERS
                            |
                            v
                    RENDER MANIFEST
                            |
                            v
                    DELIVERY PACKAGE
```

This topology is conceptual. A specific engine may fuse layers for performance, but its data contracts and state ownership should remain distinguishable.

## 7. One source of truth, multiple execution projections

The project model is the source of truth. Playback graphs, render graphs, visual mixer layouts, stem plans, and MIDI exports are projections or compiled views of that state.

The engine MUST NOT maintain unrelated copies of the same musical or routing truth that can diverge silently.

For example:

- the track view is a presentation of voices and routing assignments;
- the mixer view is a presentation of graph nodes and control parameters;
- the render graph is a compiled, validated execution plan;
- the stem list is a delivery projection over routing and print policy;
- the MIDI export is a projection of supported musical event data.

Each projection should identify the project revision from which it was built.

---

# Part II — The audio graph and signal-flow model

## 8. Why routing must be represented as a graph

Audio routing is not just a left-to-right list of effects. It is a network of signal dependencies.

A graph representation supports:

- serial insert chains;
- parallel processing;
- send/return effects;
- subgroups;
- multi-output instruments;
- sidechain control paths;
- external inputs and outputs;
- multichannel processing;
- feedback effects;
- stem taps;
- analysis taps;
- bus-to-bus routing.

A linear chain can be represented as a graph, but a graph cannot always be represented safely as one linear chain.

## 9. Canonical node categories

A useful minimum vocabulary is:

| Node category | Responsibility |
|---|---|
| Instrument source | Produces audio from musical events or internal state |
| Audio asset source | Plays a recorded or previously rendered asset |
| MIDI/event processor | Transforms event data before an instrument receives it |
| Audio processor | Transforms audio samples |
| Utility processor | Gain, pan, polarity, channel mapping, trim, delay |
| Mixer bus | Sums compatible input streams and applies bus-level processing |
| Send node | Creates a controlled branch of a signal |
| Return node | Receives one or more send paths |
| Sidechain input | Supplies a control signal to a processor |
| Meter/analyser | Observes audio without changing it, unless explicitly designed as a processor |
| Capture/tap node | Records or routes a defined graph point for stems or diagnostics |
| Output node | Sends audio to a device, file writer, or another engine |
| Feedback node | Creates an explicitly delayed feedback relationship |

Node type should not be inferred from a display name. A node must have a declared processing contract.

## 10. Canonical node record

A node record should contain, at minimum:

```json
{
  "id": "node-bass-synth-01",
  "type": "instrument_source",
  "name": "Bass voice",
  "revision": 3,
  "enabled": true,
  "input_ports": [],
  "output_ports": [
    {
      "id": "main-out",
      "media": "audio",
      "channel_layout": "stereo",
      "channel_count": 2
    }
  ],
  "latency_frames": 0,
  "tail_frames": 0,
  "state_ref": "instrument-state-bass-01",
  "capabilities": {
    "realtime": true,
    "offline": true,
    "deterministic": true,
    "midi_input": true,
    "audio_input": false
  }
}
```

This is an illustrative schema, not a mandatory JSON standard. A typed implementation may use classes, structs, database tables, or another serialisation format.

## 11. Connections and port contracts

A connection must identify both endpoints, both ports, and the signal type.

```json
{
  "id": "connection-041",
  "source": {"node_id": "node-bass-synth-01", "port_id": "main-out"},
  "destination": {"node_id": "node-bass-eq-01", "port_id": "main-in"},
  "signal_type": "audio",
  "channel_mapping": [0, 1],
  "gain_db": 0.0,
  "enabled": true
}
```

A connection MUST be rejected or explicitly adapted when its channel count or signal type is incompatible. Implicit downmixing, upmixing, mono summing, or channel reordering can create audible changes and must never be invisible.

## 12. Graph validation

Before execution, validate:

1. Every referenced node exists.
2. Every referenced port exists.
3. Port media types match.
4. Channel layouts are compatible or an explicit mapper exists.
5. Disabled nodes and connections have defined behaviour.
6. Every audible source reaches a valid output or an intentionally disconnected sink.
7. There are no accidental cycles.
8. Every feedback cycle contains an explicit delay or feedback primitive with a defined minimum delay and stability policy.
9. Sidechain paths are distinguishable from audible paths.
10. The graph has a well-defined processing order.
11. Latency and tail metadata are valid or can be measured.
12. Render and playback projections preserve the intended routing semantics.

## 13. Cycles and feedback

A normal processing graph is usually expected to be a directed acyclic graph (DAG), allowing a topological processing order.

Feedback is musically valuable, but an unrestricted zero-delay cycle cannot be processed as an ordinary DAG. Model feedback explicitly through a delay, feedback buffer, or dedicated processor whose behaviour is defined across blocks.

A feedback edge should declare:

- minimum delay in samples or frames;
- feedback gain or bounded transfer rule;
- channel mapping;
- filtering within the loop, if present;
- reset behaviour;
- tail behaviour;
- stability or overload safeguards;
- deterministic-render behaviour.

Do not silently insert arbitrary delays to make an invalid graph run. Report the modification and make it visible to the user.

## 14. Serial, parallel, send, return, and subgroup patterns

### 14.1 Serial insert chain

```text
Instrument -> Trim -> Filter -> Saturation -> Spatial Processor -> Bus
```

Use when each stage should process the output of the previous stage.

### 14.2 Parallel processing

```text
                         +-> Dry path ---------+
Instrument -> Split -----+                      +-> Sum -> Bus
                         +-> Parallel FX -------+
```

The graph must define whether the parallel branch is latency-compensated and whether the branch contains a wet-only processor. A parallel branch that contains an unreported dry signal may create unintended level build-up or comb filtering.

### 14.3 Send and return

```text
Bass Bus ---- send level ----> Shared Reverb Return ----> Mix Bus
Percussion -- send level ----> Shared Reverb Return ----> Mix Bus
Texture Bus - send level ----> Shared Reverb Return ----> Mix Bus
```

Sends should have declared pre-fader or post-fader semantics. A pre-fader send remains independent of the source fader; a post-fader send follows it. The interface must show this distinction.

### 14.4 Subgroup

```text
Kick ----+
Snare ---+--> Percussion Bus --> Processing --> Master
Metal ---+
```

A subgroup enables coherent processing and stem capture. However, the system must define whether individual track inserts and the group processing are both included in each printed stem.

### 14.5 Sidechain control path

```text
Kick detector ---- control path ----> Bass compressor
Bass audio --------------------------> Compressor audio input
```

The sidechain source is a control dependency, not necessarily an audible route. It must not be double-counted in the mix or stem export.

## 15. Feedback and intentional nonlinearity

Feedback can create unstable or chaotic results. That is not a reason to prohibit it; it is a reason to model it explicitly.

A production engine should distinguish:

- bounded feedback intended for normal use;
- experimental feedback with user-visible risk;
- runaway or numerically unstable processing;
- invalid graph cycles.

Possible safeguards include bounded feedback gain, DC blocking, denormal handling, output protection, maximum tail duration, and a user-controlled emergency mute. Protection must not silently rewrite artistic parameters without recording the intervention.

---

# Part III — Channel formats, buses, and spatial routing

## 16. Audio channel layout is explicit data

Channel count is not enough. Two 6-channel signals may represent different layouts.

Represent both:

- number of channels;
- semantic layout or channel labels;
- channel ordering;
- ambisonic or other encoded format metadata where applicable.

Possible layouts include:

- mono;
- stereo;
- dual mono;
- 5.1 and other defined speaker layouts;
- discrete multichannel;
- first- or higher-order ambisonic formats;
- application-specific channel sets.

The engine must not infer speaker positions from channel count alone.

## 17. Channel mapping

Every conversion between layouts must be explicit. Examples include:

- mono to stereo duplication or spatial placement;
- stereo to mono summing;
- surround downmixing;
- discrete channel remapping;
- ambisonic encoding or decoding;
- multi-output instrument routing.

The mapping should define coefficients, channel labels, and any normalisation convention. A downmix may change phase, balance, perceived loudness, and spatial image. It should be testable and visible.

## 18. Multi-output instruments

Drum machines, samplers, granular instruments, and hybrid synthesizers may produce multiple outputs:

- kick;
- snare;
- hats;
- percussion;
- tonal layer;
- noise layer;
- effect return;
- direct and room microphones.

Treat these as named output ports of one instrument instance. This preserves the relationship to the source instrument while allowing independent routing, mixing, and stem printing.

## 19. Master output versus monitor output

The engine should distinguish the creative mix bus from the physical monitoring output.

The monitor path may contain:

- hardware calibration;
- room correction;
- monitor gain;
- headphone crossfeed;
- device-specific channel mapping.

These operations MUST NOT accidentally appear in the exported master unless the user explicitly chooses to print them.

A robust design has a clear boundary:

```text
Project Master -> Render Capture
              \-> Monitor Processing -> Audio Device
```

This prevents monitor calibration, output attenuation, or interface-specific routing from contaminating deliverables.

---

# Part IV — Time, transport, and event execution

## 20. The engine has several clocks

A production system must distinguish:

1. **Musical time:** bars, beats, quarter-note position, subdivisions, and musical duration.
2. **Sample time:** integer sample-frame position in a particular render or stream.
3. **Wall-clock time:** operating-system time.
4. **Device time:** the clock and reported timing of the audio device or server.
5. **External transport time:** time reported by a DAW, synchronisation system, or external device.

These domains have different semantics. Never use wall-clock time as a substitute for sample time when scheduling audio events.

## 21. Musical time to sample time

The ontology volume defines canonical musical positions and tempo maps. The audio engine consumes their compiled mapping.

For a constant tempo `B` beats per minute, with a quarter-note beat, the duration of one quarter note is:

\[
T_q = \frac{60}{B}
\]

At sample rate `f_s`, the number of samples per quarter note is:

\[
N_q = f_s \frac{60}{B}
\]

For variable tempo, integrate the tempo map over musical time. The exact formula depends on how tempo is interpolated between map points (step, linear in BPM, linear in period, or another declared curve). The interpolation rule must be part of the tempo-map contract.

Use high-precision intermediate calculations, then quantise to the engine's sample frame according to one documented rounding policy. Keep the original musical position so event quantisation does not destroy the composition's timing identity.

## 22. Sample-frame scheduling

Every scheduled event should eventually compile into an execution event containing:

- absolute or block-relative sample position;
- event type;
- target instrument or processor;
- payload;
- ordering priority for simultaneous events;
- source musical event ID;
- generation or edit provenance;
- cancellation or replacement identity, if needed.

The renderer must process events at their correct offset within the audio block. Applying all events only at block boundaries introduces timing error.

## 23. Same-sample event ordering

Define deterministic ordering for events that share a sample position. For example:

1. transport and graph-state boundaries;
2. note-off or voice termination events;
3. parameter and controller updates;
4. note-on and trigger events;
5. post-event capture or marker events.

This is only a reference policy. Some instruments require note-off/note-on ordering for legato retrigger or same-pitch behaviour. The ordering contract must be explicit, testable, and consistent in real-time and offline paths.

## 24. Note lifecycle

A note event is not just a pitch and a start time. It may contain:

- note-on position;
- note-off position;
- velocity or attack intensity;
- release velocity if supported;
- channel, group, or per-note identity;
- pitch and tuning context;
- expression data;
- articulation;
- voice or instrument target;
- source musical identity.

The engine must handle stuck-note prevention, panic/reset, overlapping notes, voice stealing, sustain semantics, note IDs where available, and transport discontinuities.

## 25. Tempo changes and live transport

At a tempo-map boundary, scheduled events should retain their musical positions. Their sample positions must be recalculated or obtained from a compiled tempo-map function, not accumulated using a stale samples-per-beat constant.

At seek, stop, loop, or transport restart:

- flush or reconcile future events;
- restore automation state at the new position;
- define how active notes are stopped or reconstructed;
- reset or preserve effect state according to an explicit policy;
- reinitialise phase-dependent modulation if required;
- avoid replaying stale events.

## 26. Automation execution

Automation curves belong to musical or parameter state, but execution requires sample-time events or control-rate updates.

Support at least:

- stepped values;
- linear ramps;
- exponential or logarithmic ramps where meaningful;
- cubic or other smooth curves;
- parameter-specific smoothing;
- tempo-synchronised shapes;
- audio-rate modulation where supported;
- sample-accurate parameter points when required by the processor.

A user-facing automation curve must have a declared interpolation method. Do not assume all parameters should be interpolated linearly: frequency, time, gain, and percentage controls often require different parameter mappings.

### 26.1 Parameter domains

Keep separate:

- stored normalised value;
- physical or musical value;
- DSP coefficient;
- displayed value and unit.

For a frequency parameter, for example, linear interpolation in a 0–1 normalised domain may be perceptually inappropriate. Use a documented mapping.

### 26.2 Smoothing

Smoothing prevents clicks and abrupt coefficient changes, but its time constant changes musical behaviour. Smoothing must be parameter-specific and must not be applied blindly to transient triggers, discrete mode changes, or sample-accurate events.

## 27. Transport and synchronisation interfaces

Internal transport should be authoritative for offline rendering. During external sync, the engine should expose a clearly defined clock authority and report lock state, drift, and discontinuities.

Relevant protocols and APIs include:

- MIDI Clock, MIDI Time Code, and MIDI transport messages;
- OSC messages and time tags;
- host-provided plug-in transport context;
- JACK transport and time information;
- DAW-specific or application-specific sync adapters.

OSC is message-based and supports bundles with timetags, but the protocol does not itself guarantee clock synchronisation; the participating systems need a shared timing assumption or clock-synchronisation mechanism. See the OSC 1.0 specification.[^7]

---

# Part V — Real-time playback architecture

## 28. Real-time and offline processing are different operating modes

They should share musical and DSP semantics, but they have different execution constraints.

### Real-time playback prioritises

- meeting every audio deadline;
- stable latency;
- responsive transport and controls;
- continuity under load;
- graceful degradation when resources are exhausted;
- predictable memory and CPU behaviour.

### Offline rendering prioritises

- correct complete execution;
- reproducibility;
- maximum available quality within resource limits;
- complete effect tails;
- reliable file writing;
- resumability and diagnostics;
- consistent output independent of playback buffer size where possible.

Offline rendering may run faster or slower than real time. It should not be forced to simulate wall-clock playback unless the instrument or external device requires it.

## 29. Real-time thread rules

The audio callback or real-time processing thread must perform bounded work.

It SHOULD NOT:

- allocate or free memory;
- perform file or network I/O;
- wait on a mutex that may be held by another thread;
- call UI or graphics routines;
- perform plug-in scanning or asset loading;
- log synchronously to disk or console;
- perform unpredictable graph construction;
- access resources whose worst-case execution time is unknown.

It SHOULD:

- process preallocated buffers;
- consume lock-free or bounded command queues where appropriate;
- use prepared DSP state;
- perform bounded parameter/event dispatch;
- report diagnostics through a preallocated queue or atomic counters;
- handle overload in a defined manner.

PortAudio's callback documentation explicitly warns against memory allocation, file access, blocking operations, and other unpredictable work in a high-priority callback.[^1][^2] The exact constraints differ by API, but the underlying rule is general.

## 30. Thread ownership

A practical division is:

| Thread or execution domain | Responsibilities |
|---|---|
| UI/main thread | Controls, visualisation, editing, user interaction |
| Project/background worker | Loading assets, parsing, indexing, migrations, graph preparation |
| Audio thread | Bounded real-time DSP and scheduled event execution |
| Render worker | Offline rendering, file writing, analysis, progress reporting |
| Analysis worker | Non-real-time spectral analysis, waveform generation, diagnostics |
| Plug-in worker or host context | Plug-in lifecycle operations and any work required by the plug-in API |

The exact number of threads is implementation-dependent. The ownership boundaries are not.

## 31. Graph changes without audio glitches

Never mutate a live graph in an uncontrolled way.

A safer procedure is:

1. Build a new graph snapshot off the audio thread.
2. Validate graph connections, ports, channel layouts, and resource readiness.
3. Prepare processor state and buffers.
4. Calculate latency and execution order.
5. Transfer the new graph to the audio engine through a bounded handoff mechanism.
6. Switch at a safe block boundary.
7. Retire the old graph only when the audio thread can no longer access it.

Possible techniques include immutable graph snapshots, double-buffered state, reference-counted deferred reclamation, or real-time-safe command queues. The implementation must avoid freeing a processor while the audio thread may still be processing it.

## 32. Buffer size and deadline budget

For block size `N` and sample rate `f_s`, the block duration is:

\[
T_b = \frac{N}{f_s}
\]

The audio graph must finish its work within the available processing deadline, with headroom for scheduling and platform variation.

A block size of 128 frames at 48 kHz, for example, represents approximately 2.67 ms of audio. Smaller blocks reduce buffering latency but increase callback frequency and overhead. Larger blocks can improve throughput while increasing latency. There is no universally optimal setting.

The engine should expose:

- current sample rate;
- actual callback block size or block-size range;
- callback CPU load;
- underrun/overrun counters;
- peak execution time if measurable;
- reported input/output latency;
- device and driver identity.

## 33. Overload behaviour

When real-time capacity is exceeded, the engine must not fail silently.

Possible responses:

- report an xrun or audio dropout;
- temporarily reduce nonessential visualisation or analysis;
- reduce optional oversampling only if the user has enabled adaptive quality and the change is disclosed;
- suspend nonessential background tasks;
- offer a higher-latency buffer setting;
- switch to a pre-rendered clip if the transition is safe and the user has enabled this mode;
- stop playback with a clear diagnostic if continuity cannot be maintained.

Do not silently remove notes, bypass random effects, or change musical parameters to hide a performance problem.

---

# Part VI — Plug-ins, instruments, and external resources

## 34. Instrument lifecycle

Every instrument or plug-in instance should have a lifecycle:

1. Discover or instantiate.
2. Read capabilities and ports.
3. Configure sample rate, block limits, and channel layout.
4. Load state and assets.
5. Prepare resources.
6. Activate.
7. Start processing.
8. Receive events and automation.
9. Stop processing.
10. Deactivate.
11. Save state if required.
12. Release resources.

Lifecycle transitions must be explicit and serialised. A processor must not be used before preparation succeeds.

## 35. Plug-in formats and host adapters

The engine may support internal processors and external plug-in formats. Do not bake one format's concepts into the core ontology.

Potential adapters include:

- VST3;
- CLAP;
- Audio Units on supported Apple systems;
- LV2 in relevant environments;
- native internal DSP modules;
- external process or network-based instruments.

Each adapter should translate its format's lifecycle, buses, parameters, automation, state, latency, and threading contracts into the engine's canonical interface.

Steinberg's VST3 documentation separates audio processing from the edit controller and specifies that real-time processing must avoid memory allocation. Its parameter automation model includes time-offset points within processing blocks.[^3][^4]

CLAP likewise defines explicit main-thread and audio-thread requirements, including guidance against allocation, blocking locks, and I/O on the audio thread.[^5][^6]

These are useful examples of the broader host design problem, not reasons to make VST3 or CLAP the internal data model.

## 36. Processor capability declaration

Each processor should declare:

- supported sample rates or range;
- supported block sizes or range;
- input and output buses;
- channel layouts;
- MIDI/event input and output;
- parameter identifiers and ranges;
- automation capabilities;
- reported latency;
- tail length or tail behaviour;
- real-time capability;
- offline capability;
- deterministic-render claim and its scope;
- state save/load support;
- bypass semantics;
- sidechain support;
- resource dependencies.

Capabilities should be queried and validated before a render begins.

## 37. Parameter identity

A parameter needs a stable ID independent of its display name, display order, or plug-in UI location.

A parameter record should define:

- stable parameter ID;
- display name;
- value type;
- normalised range;
- physical range and units;
- default value;
- step count or discrete choices;
- interpolation policy;
- smoothing policy;
- automation support;
- read-only or writable status;
- version/migration behaviour.

Do not identify parameters by array index alone. Plug-in updates may reorder them.

## 38. Plug-in state and presets

A render snapshot must include the complete state required to reproduce processing, not merely a preset name.

State may include:

- parameter values;
- internal plug-in state blob;
- modulation and routing configuration;
- sample or impulse-response references;
- plug-in version and format;
- external resource paths or packaged resources;
- state schema and migration version.

A state blob from a third-party plug-in may not be portable across plug-in versions, operating systems, CPU architectures, or licences. Report this limitation in the manifest.

## 39. Missing and incompatible plug-ins

If a plug-in is missing, the engine must not silently replace it with a different instrument or bypass it without notice.

Offer explicit recovery options:

- locate the exact plug-in;
- render from a previously frozen audio asset;
- use a user-approved substitute;
- bypass the processor and mark the output as degraded;
- cancel the render.

Every substitution must be recorded in the render report.

## 40. External hardware and network instruments

External devices create additional timing and reproducibility challenges:

- round-trip latency;
- MIDI and OSC timing jitter;
- analogue conversion;
- device configuration;
- firmware differences;
- clock drift;
- state recall limitations;
- noise and environmental variation.

An external hardware part should be considered unreproducible unless its state and recording process are captured adequately. The system may support a re-record workflow with a reference test tone, loopback, alignment marker, and documented device configuration.

---

# Part VII — Latency, compensation, and tails

## 41. Latency is a graph property

Latency may come from:

- audio buffers;
- lookahead processors;
- linear-phase filters;
- oversampling filters;
- FFT-based processing;
- convolution;
- external hardware;
- network paths;
- plug-in internal buffering.

The engine should track latency in samples or frames at the current sample rate, with any additional unit conversions explicitly represented.

## 42. Plugin-reported and measured latency

Prefer a processor's declared latency when the API provides a valid report. Validate that the report is updated when configuration changes.

Some processors have content-dependent or mode-dependent latency. Where necessary, support measured latency or a user override, but label the source of the value:

- declared;
- measured;
- user-entered;
- estimated;
- unknown.

Unknown latency must not be represented as zero without a visible warning.

## 43. Path latency and compensation

For each audible path, calculate total latency from source to the relevant summing point. To align parallel paths, delay shorter paths by the difference to the longest relevant path, subject to user settings and resource constraints.

Latency compensation must consider:

- audio paths;
- sidechain paths where temporal alignment matters;
- parallel sends;
- multi-output sources;
- external hardware returns;
- stem capture points;
- render and monitor paths.

A delay inserted for compensation is not the same as a creative delay effect. Keep them distinct in the graph and UI.

JACK's latency API, for example, treats capture and playback latency as graph properties and accommodates paths with minimum and maximum latency values.[^8]

## 44. Automation and latency

Automation must be aligned to the intended audible event. If a processor introduces latency, its parameter automation and audio path must remain correctly related. The engine needs a clear convention for whether automation time refers to source time, processor input time, or compensated output time.

The convention should be uniform and documented, with adapters responsible for converting to plug-in-specific time-offsets.

## 45. Effect tails and render termination

Effects may continue producing audio after the last note or event:

- reverb decay;
- delay feedback;
- granular buffers;
- convolution tails;
- resonator decay;
- feedback networks;
- instrument release envelopes.

A render range therefore needs a tail policy:

- fixed tail duration;
- per-processor declared tail;
- measured silence threshold with maximum duration;
- manual tail endpoint;
- truncate at exact range.

A silence detector alone is not sufficient for every generative texture. A quiet tail may be intentional and may later swell. Provide a configurable maximum and a visible tail decision.

## 46. Loop rendering

Loop rendering needs special treatment because effect tails and persistent state may cross the loop boundary.

Support at least two explicit modes:

1. **Hard loop:** render exactly the requested range; state at the end is not joined to the beginning.
2. **Continuous loop preparation:** render enough pre-roll and tail or use a defined state-wrap strategy, then inspect the seam.

Do not promise a seamless loop simply because the file length is an exact number of bars.

---

# Part VIII — Mixing, gain staging, and master path

## 47. Internal signal precision

Use an internal floating-point representation with sufficient headroom for intermediate processing. 32-bit floating-point is a common practical choice; 64-bit may be useful for selected high-precision operations or summing contexts. The correct choice depends on performance, numerical requirements, and processor interoperability.

The system should not confuse internal floating-point headroom with permission to ignore clipping at fixed-point output or at nonlinear plug-ins.

## 48. Gain staging

Every audio node should have a clear input and output level convention.

The mixer should expose:

- trim before inserts;
- insert processing;
- channel fader;
- pan or spatial control;
- sends;
- bus assignment;
- meter position selection.

Metering should distinguish pre-insert, post-insert, pre-fader, post-fader, bus input, bus output, and master output when those views are available.

## 49. Peak, loudness, and headroom are different concepts

Track and master evaluation should not rely on one meter.

- **Sample peak** measures the largest stored sample value.
- **True peak** estimates inter-sample peak level using oversampled reconstruction methods.
- **RMS or energy metrics** describe signal energy over a specified window.
- **Integrated loudness** estimates programme loudness across a specified measurement interval and gating method.
- **Short-term and momentary loudness** describe shorter windows.
- **Loudness range** describes variation over time under a defined method.

A technically safe peak does not guarantee an appropriate loudness or a good-sounding mix.

## 50. Loudness standards are delivery-context rules, not universal artistic targets

ITU-R BS.1770 defines algorithms for programme loudness and true-peak measurement; BS.1770-5 is the current in-force recommendation identified by the ITU source consulted for this manual.[^9]

EBU R 128 version 5.0 recommends an average programme loudness of -23 LUFS alongside Loudness Range and Maximum True Peak Level descriptors for its broadcast context.[^10] That value must **not** be treated as a universal target for IDM masters, streaming releases, games, club playback, or every music deliverable.

The application should allow delivery profiles to define targets and tolerances. A delivery profile should identify:

- target platform or use;
- measurement standard;
- integrated loudness target, if applicable;
- true-peak ceiling, if applicable;
- loudness-range expectations, if applicable;
- measurement duration and gating;
- whether normalisation is measurement-only or applied processing;
- whether any deviation is permitted.

A mastering decision remains a creative and distribution decision, not an engine default.

## 51. Master processing

Master-chain processors should be ordinary graph nodes with explicit state and latency. They should not be hidden in the file writer.

Support separate print options:

- project master including master inserts;
- pre-master mix before selected finalisation processors;
- alternate master chains;
- unprocessed reference mix;
- monitor-only processing excluded.

The export interface must make clear which chain is printed.

## 52. Dither and integer output

Dither is relevant when reducing word length to a fixed-point integer representation. It should be applied once at the appropriate final conversion stage, not repeatedly at intermediate stages.

For floating-point delivery, dither may not be appropriate in the same way. The engine should document its bit-depth and dither choices rather than adding noise by default without explaining why.

## 53. Clipping and overload policy

The engine should identify:

- clipping at an instrument output;
- clipping inside an effect or plug-in, where detectable;
- bus overload;
- master sample peak exceedance;
- true-peak ceiling exceedance;
- file conversion overflow.

Do not auto-limit or normalise every output silently. Offer optional protection and record any applied limiter, gain change, or normalisation.

---

# Part IX — Preview, freeze, and pre-render architecture

## 54. Preview is a production mode, not a separate interpretation of the music

A preview exists to make a composition easy to audition. It may use reduced quality or cached audio for responsiveness, but it must preserve the same musical decisions, timing, routing semantics, and meaningful parameter relationships as the final render.

A preview system should declare its quality profile:

- sample rate;
- block size;
- oversampling mode;
- instrument quality mode;
- effect quality mode;
- convolution or IR quality;
- analysis resolution;
- plug-in render mode;
- caching policy;
- latency mode.

A preview is allowed to be approximate only where the approximation is explicit and musically safe. For example, a low-quality oscillator mode may be acceptable while editing, but a preview that omits all bus effects may misrepresent the composition and should be labelled accordingly.

## 55. Preview fidelity levels

A useful application can offer different fidelity profiles:

| Profile | Goal | Typical compromise |
|---|---|---|
| Interactive | Fast editing and audition | Reduced oversampling or lower-cost quality settings |
| Full-chain preview | Hear the actual routing and effects | May render slower or use larger buffers |
| Section preview | Inspect one region with pre-roll and tails | May reuse cached upstream material |
| Final-quality audition | Match delivery render as closely as possible | High CPU and longer preparation |
| Offline final | Produce the authoritative deliverable | No real-time deadline; complete quality and validation |

Each profile should state whether it is bit-identical, parameter-equivalent, or merely perceptually representative of the final render.

## 56. Pre-render and freeze use cases

Pre-rendering is valuable when:

- a complex instrument is expensive to calculate;
- a long convolution or spectral effect dominates CPU;
- a source has stable content during a section;
- the same material is auditioned repeatedly;
- a real-time session cannot comfortably run every processor;
- the user wants a frozen snapshot for reliable playback;
- stems need to be inspected independently of live generation.

Pre-rendering should not be limited to entire tracks. The engine may cache individual nodes, groups, sections, or graph subtrees.

## 57. Cache identity and invalidation

A cache key must include every dependency that affects the cached result.

A simplified cache identity may contain:

```json
{
  "cache_schema": 2,
  "project_revision": "rev-0084",
  "source_entity_revisions": ["voice-4:r9", "pattern-12:r3"],
  "graph_subtree_hash": "sha256:...",
  "instrument_state_hash": "sha256:...",
  "asset_hashes": ["sha256:...", "sha256:..."],
  "automation_hash": "sha256:...",
  "tempo_map_hash": "sha256:...",
  "render_profile_hash": "sha256:...",
  "sample_rate": 48000,
  "channel_layout": "stereo",
  "random_stream_state": "seed-set-01"
}
```

If a dependency changes, the cache is stale. The cache system must never return audio from an earlier state while labelling it as current.

Dependency-aware invalidation should be targeted. Changing one instrument state should not force a full project re-render if only one graph subtree depends on it. Conversely, a tempo-map change may invalidate every tempo-synchronised event, delay, LFO, granular process, or time-based automation path that depends on musical time.

## 58. Freeze semantics

A frozen object is a committed audio realisation of a known upstream state.

A freeze record should include:

- source node or graph subtree;
- source revision and dependency hashes;
- start and end positions;
- pre-roll and post-roll;
- sample rate and channel layout;
- output asset and checksum;
- whether effects are included;
- whether automation is printed;
- whether the original source is retained;
- replacement/bypass policy;
- unfreeze conditions.

Freezing must be reversible where possible. The original musical and instrument data should remain available. A frozen file is an execution shortcut, not a replacement for the composition's identity.

## 59. Pre-rendered effect and stem channels

A useful architecture can render expensive channel processing once and then route the resulting audio to multiple audition contexts.

However, the application must distinguish:

- pre-rendered instrument output;
- pre-rendered track including inserts;
- pre-rendered subgroup;
- printed send/return effect;
- printed full stem;
- final master.

These are not interchangeable. For example, a pre-rendered track with its send effect printed cannot later be sent to the same shared return without double-counting the effect.

The cache metadata should state exactly which part of the signal chain has already been printed.

## 60. Preview transitions and state continuity

When switching between live and frozen paths, align:

- sample position;
- latency;
- gain;
- channel mapping;
- automation state;
- note and effect state;
- loop and transport position.

A short crossfade may prevent a click, but it does not correct a timing or gain mismatch. The engine should validate alignment before switching.

---

# Part X — Offline rendering and render-job orchestration

## 61. A render job is an immutable execution request

A render job should capture a stable snapshot of:

- project revision;
- composition revision;
- sound realisation revision;
- audio graph revision;
- processor states;
- assets and their hashes;
- automation and tempo maps;
- random seeds and state;
- sample rate and format;
- channel layout;
- render range;
- pre-roll and post-roll;
- effect-tail policy;
- quality profile;
- output and naming policy;
- renderer version.

After the job starts, edits to the live project should not mutate its state. The job can either render the captured snapshot or be cancelled and restarted with a new snapshot.

## 62. Render-job states

Use an explicit state machine:

```text
CREATED
   |
   v
VALIDATING ---> REJECTED
   |
   v
PREPARING
   |
   v
RENDERING <---- PAUSED (where supported)
   |
   v
FINALISING
   |
   v
ANALYSING
   |
   v
PACKAGING
   |
   v
COMPLETED
```

Additional terminal or recovery states may include:

- CANCELLED;
- FAILED;
- INTERRUPTED;
- COMPLETED_WITH_WARNINGS;
- OUTPUT_VALIDATION_FAILED.

The UI should show the actual stage and actionable error information. A progress bar that reaches 100% before the file is finalised and validated is misleading.

## 63. Preflight validation

Before rendering, validate:

- every instrument can be instantiated or restored;
- all assets resolve and pass integrity checks;
- all plug-in states can be loaded;
- graph validation succeeds;
- channel layouts are compatible;
- no unsupported processor mode is required;
- all automation references valid parameters;
- the render range is valid;
- all required output paths are writable;
- sufficient storage is available where it can be estimated;
- the selected format supports the requested channel count and format;
- the render profile is internally consistent;
- the random-state policy is defined;
- the tail policy is defined.

A missing optional resource may produce a warning. A missing required instrument or asset should normally block a faithful render.

## 64. Pre-roll and warm-up

Some processors require prior samples or state evolution before the desired render start:

- lookahead limiters;
- convolution engines;
- feedback delays;
- oscillators with free-running phase;
- stateful filters;
- granular buffers;
- spectral processors;
- instruments whose release or modulation states depend on earlier events.

The render job should support pre-roll in musical or sample time. It should specify whether the output file includes the pre-roll or discards it after the engine reaches the desired state.

## 65. Block-independent rendering

Offline rendering should be correct across different processing block sizes unless a processor's contract explicitly requires otherwise.

Tests should compare renders produced with multiple block sizes. Differences may occur because of plug-in implementation details, floating-point summation order, or block-based modulation, but unexpected musical timing differences or missing events are defects.

## 66. Chunked rendering and resumability

Large projects may be rendered in chunks. Chunking is safe only when state continuity is preserved or explicitly reconstructed.

A chunk boundary may require state transfer for:

- instrument voices and envelopes;
- delay and reverb buffers;
- filter state;
- modulation phase;
- granular playback buffers;
- random number generator state;
- plug-in internal state;
- compressor and limiter envelopes;
- automation interpolation.

A render system should not assume that each chunk can be started from silence. If state cannot be serialised safely, use a continuous render stream or deterministic warm-up strategy and mark the limitation.

## 67. Parallel rendering

Independent stems or independent graph branches may be rendered in parallel when their dependencies and state allow it.

Parallel work must not change the final result through uncontrolled shared state. For example, two branches must not consume the same global random-number stream in a race-dependent order.

Prefer:

- independent random streams per entity or task;
- immutable input snapshots;
- explicit task dependencies;
- deterministic merge order where bitwise repeatability is required;
- per-task diagnostic records;
- resource budgets for CPU, memory, and disk throughput.

Parallel rendering is an optimisation, not a guarantee of identical floating-point output across all platforms.

## 68. Render cancellation and recovery

Cancellation should be safe at defined boundaries. A cancelled job must not leave a file that appears to be a valid completed master.

Use temporary output paths, completion markers, and atomic finalisation where supported. Preserve partial outputs only in a clearly labelled recovery area.

If the application crashes during rendering, it should be able to report:

- the last completed stage;
- the last confirmed render position;
- whether the partial file is recoverable;
- which outputs are incomplete;
- whether the job can be resumed or must restart.

---

# Part XI — Reproducibility and render provenance

## 69. Reproducibility is multidimensional

A system should not use the word *reproducible* without defining what is reproduced.

Distinguish:

1. **Musical reproducibility:** the same notes, events, structure, and musical decisions are recreated.
2. **Graph reproducibility:** the same routing and processor configuration are recreated.
3. **Parameter reproducibility:** the same parameter and automation states are restored.
4. **State reproducibility:** processor and instrument internal states are restored.
5. **Sample reproducibility:** the rendered samples are bit-identical.
6. **Perceptual reproducibility:** results are equivalent within an explicitly defined listening or measurement tolerance.
7. **Environment reproducibility:** the software, libraries, assets, plug-ins, and relevant platform context are preserved.

A project may achieve musical reproducibility while failing bit-identical sample reproducibility because of external plug-ins, hardware, floating-point differences, or nondeterministic processing.

## 70. Determinism policy

Each processor and render mode should declare a determinism category:

| Category | Meaning |
|---|---|
| D0 — Deterministic | Same input and state produce identical output under the declared environment and execution conditions |
| D1 — Seeded stochastic | Random behaviour is controlled by stored seeds and stable stream ownership |
| D2 — Environment-dependent | Results depend on plug-in version, hardware, platform, or external resource state |
| D3 — External or live | Output depends on hardware, network, performance, or uncontrolled external conditions |
| D4 — Unknown | The processor's determinism cannot be established |

The category is not a quality ranking. Stochastic and hardware-dependent sound may be artistically desirable. The requirement is to document what can and cannot be reproduced.

## 71. Random-number stream architecture

Do not use one process-global random generator for the entire project.

Prefer named streams scoped to stable entities or tasks:

- composition-level seed;
- section-generation seed;
- voice-generation seed;
- instrument-instance seed;
- effect seed;
- render-dither seed;
- analysis or visualisation seed.

A seed record should identify the algorithm and version as well as the seed value. A stable derivation method may derive a child stream from the project seed and a stable entity ID.

A single global stream can produce order-dependent results: adding one random decision early in the render shifts every later random value. Independent streams reduce this coupling.

## 72. Hidden state

A render may depend on state that is not visible in parameter values:

- free-running oscillator phase;
- noise generator state;
- random modulation state;
- delay buffers;
- reverb buffers;
- envelope followers;
- plug-in internal caches;
- sample round-robin counters;
- voice allocation history;
- external device state.

Where possible, store or deterministically reconstruct such state. Where impossible, classify the dependency and warn the user.

## 73. Asset and dependency integrity

Every required asset should have:

- stable project-relative identity;
- original file name;
- media type;
- size;
- checksum (preferably SHA-256 or another documented strong hash);
- sample rate and channel metadata for audio;
- duration or frame count;
- licence or provenance fields where the project tracks them;
- embedding or external-reference policy.

An asset name is not an identity. Two files named `texture.wav` may contain different audio.

## 74. Plug-in and renderer environment capture

The manifest should record, when available:

- application version and build ID;
- audio engine version;
- DSP module versions;
- plug-in format;
- plug-in identifier and vendor;
- plug-in version;
- preset or state checksum;
- operating system and architecture;
- audio sample rate and channel layout;
- relevant library versions;
- external hardware identifiers and configuration where relevant.

Do not claim that this guarantees portability. It improves diagnosis and makes environment differences explicit.

## 75. Render manifest: reference schema

```json
{
  "manifest_schema": "1.0",
  "render_id": "render-2026-11-26-001",
  "created_utc": "2026-11-26T18:30:00Z",
  "project": {
    "project_id": "project-eli-001",
    "project_revision": "rev-0084",
    "composition_id": "composition-01",
    "composition_revision": "rev-0032"
  },
  "engine": {
    "application_version": "0.9.0",
    "audio_engine_version": "0.4.2",
    "renderer_version": "offline-renderer-3",
    "sample_rate": 48000,
    "internal_format": "float32",
    "block_size": 512
  },
  "output": {
    "kind": "full_mix",
    "container": "wav",
    "encoding": "pcm_s24le",
    "channels": 2,
    "channel_layout": "stereo",
    "frames": 123456789,
    "duration_seconds": 2572.016,
    "file_sha256": "..."
  },
  "render_range": {
    "start_qn": "0/1",
    "end_qn": "1728/1",
    "preroll_frames": 48000,
    "tail_policy": "declared_then_silence_check",
    "max_tail_seconds": 20.0
  },
  "reproducibility": {
    "determinism_category": "D1",
    "master_seed": 246801,
    "seed_algorithm": "documented-pcg-family-v1",
    "seed_stream_policy": "per-entity"
  },
  "dependencies": {
    "assets": [],
    "processors": [],
    "external_devices": []
  },
  "routing_graph_hash": "sha256:...",
  "automation_hash": "sha256:...",
  "warnings": [],
  "validation": {
    "status": "passed",
    "checks": []
  }
}
```

The values above are illustrative. In particular, the seed algorithm name must correspond to an actual implemented and versioned generator, not a placeholder copied into production.

## 76. Hashes and canonical serialisation

A graph or state hash is only meaningful if the serialisation is canonical.

Define:

- stable field ordering or canonical JSON rules;
- numeric serialisation precision;
- normalisation of paths and identifiers;
- treatment of absent versus default-valued fields;
- version tags;
- exclusion of volatile UI state;
- inclusion of all state that affects audio.

A UI window position should not invalidate an audio cache. A changed impulse response must.

## 77. Bit-identical versus perceptual comparison

Bitwise file equality is strong but can be too strict for cross-platform reproducibility. Perceptual comparison is useful but can hide errors if the tolerance is poorly chosen.

Use a layered approach:

1. Compare musical event and composition hashes.
2. Compare graph and processor-state hashes.
3. Compare render settings and dependency manifest.
4. If same environment and deterministic category, compare PCM checksums.
5. Otherwise compare aligned audio using defined technical and perceptual metrics.
6. Retain representative listening tests for changes that metrics cannot adjudicate.

Never use a single correlation value as proof of equivalence. A one-sample alignment shift can reduce correlation while remaining perceptually subtle; a phase or routing error can also produce misleading summaries.

---

# Part XII — Export, stems, MIDI, and production packages

## 78. Output types

The delivery system should treat the following as distinct deliverables:

- full mix;
- master print;
- pre-master print;
- instrument stems;
- role stems;
- subgroup stems;
- effect-return stems;
- dry stems;
- wet stems;
- MIDI files;
- project file;
- sound-source and preset data;
- render manifest;
- README and dependency report;
- optional analysis reports.

A user should be able to choose what is included without changing the composition itself.

## 79. Stem definitions must be explicit

A stem is a defined capture point or collection of graph paths, not merely a file generated from a track name.

Every stem definition should identify:

- stem ID and display name;
- source nodes or role/voice references;
- capture point in the graph;
- included inserts;
- included sends and returns;
- pre- or post-fader position;
- whether master processing is included;
- channel layout;
- render range;
- pre-roll/tail policy;
- alignment origin;
- output format.

## 80. Stem print policies

Support clear policies such as:

### 80.1 Track stem, post-insert, pre-fader

Includes track inserts but not the channel fader. Useful for flexible mixing when the fader is to be rebuilt downstream.

### 80.2 Track stem, post-fader

Includes track inserts and fader level. Useful when preserving the generated balance.

### 80.3 Dry stem

Captures the source before selected track effects. Define whether instrument-internal effects remain part of the source.

### 80.4 Wet stem

Captures the processed source, or the source plus its dedicated effect return. These are different configurations and must have different labels.

### 80.5 Role stem

Combines multiple tracks or voices belonging to a musical role, such as percussion, bass, texture, or melodic material.

### 80.6 Effect-return stem

Prints a shared return bus independently. If printed, the corresponding track stems should not also include that return unless the package explicitly intends duplicated wet content.

### 80.7 Mastered stem

Includes master-bus processing. It is not directly additive with other mastered stems in the same way as pre-master stems.

## 81. Stem alignment invariant

All stems belonging to one package MUST share:

- the same sample rate;
- the same channel convention where applicable;
- the same start sample or declared timeline origin;
- the same nominal duration;
- the same tempo-map context;
- the same render snapshot;
- consistent tail policy.

Do not trim each stem independently to its first audible transient. That destroys alignment.

If stems have different channel layouts or lengths by design, record that explicitly in the package manifest.

## 82. Additivity and stem reconciliation

When the package claims that stems reconstruct the mix, test that claim.

Define the expected summing and processing policy. A simple pre-master stem set may reconstruct a pre-master mix if all relevant paths are included exactly once and no nonlinear shared bus processing changes the result. A set of stems printed before a shared compressor or limiter will not necessarily sum to the mastered output.

A stem report should state one of:

- **reconstructs master exactly**;
- **reconstructs pre-master exactly**;
- **reconstructs under documented linear processing**;
- **non-additive by design**;
- **not verified**.

## 83. MIDI export is a musical projection

MIDI export should preserve supported note, controller, articulation, and timing data while reporting limitations.

Potential limitations include:

- plug-in internal modulation not expressible as MIDI;
- audio-only granular or spectral transformations;
- per-note expressions unavailable in MIDI 1.0;
- proprietary automation;
- tuning systems not represented by basic note numbers;
- complex nested patterns collapsed into events;
- microtiming quantised by an export resolution;
- audio effects not represented in the file.

Support MIDI 1.0 as a broad interoperability target. MIDI 2.0 and Universal MIDI Packet can provide richer resolution and per-note expression where devices and software support them. The MIDI Association describes MIDI 2.0 as an extension of MIDI 1.0 with higher-resolution data and expanded per-note control, with compatibility to MIDI 1.0 a design priority.[^11][^12]

The project format remains the authoritative representation when an interchange format cannot express the full musical model.

## 84. Audio file formats and choices

Useful delivery formats include:

| Format | Typical purpose | Important considerations |
|---|---|---|
| WAV/RIFF PCM | Broad uncompressed interchange | Metadata and large-file limitations depend on variant and tooling |
| RF64 | Large WAV-compatible PCM files | Designed to exceed the classic RIFF size limit |
| Broadcast Wave Format (BWF) | Audio exchange with production metadata | Extends WAVE with broadcast metadata chunks |
| AIFF | Uncompressed interchange in compatible environments | Confirm metadata and workflow support |
| FLAC | Lossless compressed archive/delivery | Lossless, but not suitable where a recipient requires PCM WAV |
| Float WAV | Internal or high-headroom intermediate | Ensure downstream software supports the chosen subtype |
| MP3/AAC/Opus | Listening copies or distribution-specific encodes | Lossy; not a substitute for the high-quality archive master |

EBU Tech 3285 defines Broadcast Wave Format as a WAVE-based format extended with metadata for audio exchange, and its version 2 includes loudness metadata provisions.[^13][^14]

## 85. Sample rate and bit depth policy

Do not assume that the highest available sample rate is automatically the best production choice.

Sample-rate selection should consider:

- source and instrument requirements;
- plug-in oversampling and internal processing;
- delivery requirements;
- CPU and storage cost;
- resampling quality;
- spectral content;
- compatibility.

Bit-depth selection should consider:

- internal floating-point processing;
- final integer delivery;
- dither requirements;
- file size;
- recipient workflow.

A practical application may offer common rates such as 44.1, 48, 88.2, and 96 kHz, but should not hard-code them as the only valid values if the engine supports others.

## 86. Resampling and channel conversion

Resampling must use a documented quality mode and preserve duration, channel relationships, and timing alignment.

Quality choices may include:

- fast/preview;
- high-quality production;
- linear-phase or minimum-phase filters where supported;
- asynchronous sample-rate conversion for clock-domain boundaries.

Channel rematrixing and sample-format conversion should be separate operations from rate conversion so that each can be tested.

FFmpeg's resampler documentation describes sample-rate conversion, channel-layout rematrixing, and sample-format/packing conversion as related but distinct capabilities of its resampling layer.[^15]

## 87. Complete production package

A typical package structure may be:

```text
Project_Export/
├── README.md
├── manifest.json
├── audio/
│   ├── master/
│   │   ├── Project_Master.wav
│   │   └── Project_PreMaster.wav
│   ├── stems/
│   │   ├── 01_Percussion.wav
│   │   ├── 02_Bass.wav
│   │   ├── 03_Melodic.wav
│   │   ├── 04_Texture.wav
│   │   └── 05_Effect_Returns.wav
│   └── reference/
│       └── Listening_Copy.mp3
├── midi/
│   ├── Full_Composition.mid
│   ├── Percussion.mid
│   ├── Bass.mid
│   └── Melodic_Voices.mid
├── project/
│   ├── composition.json
│   ├── musical_graph.json
│   ├── audio_graph.json
│   ├── automation.json
│   ├── instrument_states/
│   └── render_profiles/
├── assets/
│   ├── asset_manifest.json
│   └── [embedded or packaged source assets]
├── reports/
│   ├── render_report.json
│   ├── loudness_report.json
│   ├── stem_reconciliation.json
│   └── diagnostics.txt
└── checksums.sha256
```

This is a reference structure. Large sample libraries and third-party plug-ins may need to remain external, but their identities, versions, paths, and checksums should be recorded where possible.

## 88. README requirements

The package README should explain:

- project and composition title;
- render date and application version;
- what each audio file contains;
- sample rate, bit depth, channel layout, and duration;
- stem naming and routing policy;
- whether stems reconstruct a mix;
- MIDI limitations;
- required external assets or plug-ins;
- known reproducibility limitations;
- how to open the project;
- which file is the authoritative master.

---

# Part XIII — Analysis, metering, and validation

## 89. Measurement is not listening

Meters are necessary for technical quality assurance, but they cannot fully judge timbre, groove, emotional impact, arrangement, or artistic appropriateness.

The engine should present measurements with:

- units;
- time windows;
- measurement standard;
- channel aggregation method;
- gating method where relevant;
- implementation/version;
- measurement limitations.

## 90. Minimum technical analysis set

For a full mix and, where practical, each stem, calculate:

- sample peak;
- true peak or an explicitly labelled estimate;
- integrated loudness when a standard is selected;
- short-term and momentary loudness where relevant;
- loudness range where relevant;
- RMS or energy statistics;
- DC offset;
- clipping sample count;
- silence/dropout regions;
- channel count and layout;
- file duration and frame count;
- file checksum.

Optional diagnostics include:

- stereo correlation;
- mid/side energy;
- spectral centroid and bandwidth;
- spectral flux;
- transient density;
- low-frequency energy distribution;
- crest factor;
- phase correlation by band;
- inter-channel level difference;
- tail decay estimate.

These optional metrics should not be presented as objective measures of artistic quality.

## 91. Output validation gates

Use separate gates for separate claims.

### Gate A — File integrity

- file opens;
- header and encoding are valid;
- sample rate and channels match the manifest;
- frame count matches expected length;
- file is non-empty;
- checksum can be calculated;
- no partial-file marker remains.

### Gate B — Signal integrity

- no unexpected NaN or infinity values;
- no unexpected all-zero output;
- no unexplained discontinuity;
- no unexpected clipping;
- no missing channel;
- no unintended silence or dropout;
- valid tail handling.

### Gate C — Routing integrity

- all expected sources reached the intended destination;
- no source was accidentally omitted;
- no send or return was double-counted;
- no channel mapping was applied unexpectedly;
- no master or monitor processor was printed contrary to the selected profile.

### Gate D — Package integrity

- every requested file exists;
- manifest and file checksums agree;
- stems share alignment;
- MIDI exports exist where requested;
- project data and required assets are present or their external status is declared;
- README accurately describes the package.

### Gate E — Production review

- audition the master;
- audition representative stems;
- compare preview and final render;
- inspect endings and tails;
- check transitions and loop boundaries where relevant;
- inspect technical report;
- confirm delivery-profile compliance.

Passing the first four gates does not imply that the music is artistically successful. Production review remains distinct.

## 92. Loudness validation

If a delivery profile invokes EBU R 128, ITU-R BS.1770, or another standard, use a verified implementation and preserve the exact profile version and measurement settings.

The current ITU page identifies BS.1770-5, approved in November 2023, as in force for loudness and true-peak measurement.[^9] EBU R 128 version 5.0, published in November 2023, defines broadcast-oriented programme loudness and associated descriptors.[^10]

The application should not hard-code broadcast loudness targets into all project masters. For an IDM music release, target level and true-peak ceiling should be selected according to the release context, mastering approach, and recipient requirements.

## 93. Stem reconciliation test

If the user requests additive stems:

1. Render the reference mix from the same immutable render snapshot.
2. Render the stems using the declared capture points.
3. Align the stems to the common origin.
4. Sum them according to the declared policy.
5. Apply only the processing that the policy says belongs after the stem sum.
6. Compare against the reference output.
7. Report sample-accurate or tolerance-based differences.

If the stems are intended to be non-additive, the report must say so and explain why.

## 94. Preview-versus-final comparison

A preview may differ because of quality settings, plug-in render mode, sample rate, oversampling, or cached sources. The system should identify the differences and offer a comparison report.

At minimum, compare:

- arrangement and event timing;
- duration and start position;
- routing topology;
- active processors;
- parameter values;
- channel layout;
- loudness and peak statistics;
- aligned waveform difference where meaningful.

The goal is not necessarily bit identity. The goal is to prevent unexplained differences.

---

# Part XIV — Performance, scaling, and application integration

## 95. Cost model

Audio-engine performance is not adequately described by one CPU percentage.

Track at least:

- per-node processing time where feasible;
- total graph processing time;
- callback deadline utilisation;
- render throughput relative to real time;
- peak memory;
- audio buffer memory;
- cache size;
- asset decoding cost;
- file-writing throughput;
- plug-in load time;
- graph preparation time;
- analysis overhead;
- underrun/overrun count.

A graph with many lightweight nodes may behave differently from one containing a few expensive spectral processors.

## 96. Scheduling and parallelism

A graph can be partitioned into independent branches. However, parallelism is only useful when branch cost exceeds the scheduling overhead and when dependencies are respected.

Consider:

- CPU topology;
- number of independent branches;
- processor thread-safety;
- plug-in restrictions;
- memory bandwidth;
- cache locality;
- deterministic merge order;
- real-time scheduling overhead.

A plug-in that is not safe for concurrent processing must not be called concurrently merely because the graph has parallel branches.

## 97. GPU processing

GPU acceleration may benefit selected workloads:

- large FFT batches;
- convolution banks;
- spectral transforms;
- neural synthesis or analysis;
- large parallel granular operations;
- visualisation and audio-analysis workloads.

It may be counterproductive for small, latency-sensitive processors due to transfer and launch overhead.

The engine should benchmark each workload and support CPU fallback. A GPU path should not be assumed faster or bit-identical to the CPU path.

## 98. Python and high-level language integration

A Python application can orchestrate composition, graph construction, UI, offline rendering, analysis, and project management. It should be cautious about placing the entire real-time audio callback and all DSP in an interpreter-level event loop.

Possible architecture:

```text
Python / Qt Application
   |-- composition and project model
   |-- generator and decision systems
   |-- graph editor and parameter UI
   |-- render-job orchestration
   |-- analysis and package management
   |
   +--> Native or dedicated audio engine
           |-- real-time processing
           |-- instrument/plug-in execution
           |-- sample-accurate scheduling
           |-- low-latency device I/O
           |-- offline renderer
```

A pure Python or high-level callback may be useful for prototypes and offline tasks, but hard real-time guarantees are difficult when interpreter execution, garbage collection, memory allocation, or library calls have unpredictable timing.

Use bounded queues or explicit command messages to cross from the UI/generator domain into the audio execution domain. Do not call UI widgets or Python object-heavy operations from a native real-time callback.

## 99. UI and audio state

The UI should not read mutable DSP memory unsafely while the audio thread writes it.

Use atomic snapshots, lock-free meter queues, double-buffered analysis data, or a documented synchronisation mechanism. Visualisation should be decimated to the display rate and should not determine audio callback deadlines.

## 100. Application shutdown and crash safety

A safe shutdown should:

1. stop accepting new render or transport commands;
2. stop transport and release active notes;
3. stop or drain audio processing according to engine policy;
4. save or report unsaved project changes;
5. finalise or mark incomplete render jobs;
6. release plug-ins after processing has stopped;
7. close audio devices;
8. persist diagnostic information.

Do not destroy the audio graph while the device callback may still reference it.

---

# Part XV — Reference subsystem contracts

## 101. Audio engine interface

A conceptual engine API might expose:

```text
prepare(project_snapshot, device_config) -> PreparationResult
start_transport(position) -> TransportResult
stop_transport(mode) -> TransportResult
seek(position) -> TransportResult
submit_event_batch(events) -> QueueResult
submit_parameter_batch(changes) -> QueueResult
publish_graph(graph_snapshot) -> GraphSwapResult
get_engine_status() -> EngineStatus
get_meter_snapshot() -> MeterSnapshot
shutdown() -> ShutdownResult
```

The real-time execution contract should be narrower than the application API. Expensive operations such as `prepare` and graph construction must happen outside the callback.

## 102. Render service interface

```text
create_job(render_request, project_snapshot) -> RenderJob
validate_job(job_id) -> ValidationReport
prepare_job(job_id) -> PreparationReport
run_job(job_id) -> RenderProgress
cancel_job(job_id) -> CancellationResult
get_job_status(job_id) -> RenderJobStatus
get_manifest(job_id) -> RenderManifest
validate_output(job_id) -> OutputValidationReport
package_delivery(job_id, package_profile) -> PackageResult
```

Every operation should return structured status and diagnostics. Long-running operations should be asynchronous from the UI's point of view, while their internal execution remains well-defined.

## 103. Mixer and graph-editor interface

The graph editor should operate on graph transactions:

```text
begin_graph_edit(base_revision)
add_node(node_spec)
remove_node(node_id)
connect_ports(source, destination, mapping)
set_node_parameter(node_id, parameter_id, value)
set_send_mode(connection_id, pre_or_post)
validate_graph()
commit_graph_edit() -> new_revision
```

A graph edit should either commit as a valid new revision or fail with diagnostics. Partial application of an invalid graph should not become the live engine state.

## 104. Metering interface

Meter data should be reported with stable identifiers and defined positions in the graph:

```json
{
  "node_id": "bus-percussion",
  "tap_id": "post_fader",
  "sample_rate": 48000,
  "channels": 2,
  "window_frames": 2048,
  "sample_peak_dbfs": [-3.1, -3.4],
  "rms_dbfs": [-16.2, -16.7],
  "timestamp_sample": 9123840,
  "dropped_updates": 0
}
```

Meter snapshots should not require the UI to access DSP buffers directly.

## 105. Export service interface

```text
create_export_plan(project_snapshot, export_profile) -> ExportPlan
validate_export_plan(plan) -> ExportValidation
render_mix(plan) -> RenderArtifact
render_stems(plan) -> [RenderArtifact]
export_midi(plan) -> MidiArtifact
collect_project_data(plan) -> ProjectArtifact
build_manifest(plan, artifacts) -> Manifest
validate_package(package) -> PackageValidation
finalise_package(package) -> FinalPackage
```

The export plan should declare the stem policy, output format, MIDI limitations, asset policy, and package structure before rendering begins.

---

# Part XVI — Failure modes and anti-patterns

## 106. Common architectural mistakes

### 106.1 The mixer is a UI fiction

The interface shows faders and effects, but the renderer ignores them or uses a separate processing path.

**Required correction:** preview, mixer audition, stem rendering, and full rendering must compile from the same canonical graph and state, subject only to declared quality modes.

### 106.2 Effects are preview-only or render-only

A track sounds different in the mixer and in the export because one path omits an effect, automation lane, sidechain, or send return.

**Required correction:** shared graph compilation and render-equivalence tests.

### 106.3 One global effect chain

Every source receives the same effects regardless of role, routing, or user intent.

**Required correction:** graph nodes, per-source inserts, shared returns, subgroups, and explicit routing.

### 106.4 Track order determines routing

Reordering tracks changes the signal flow.

**Required correction:** stable node IDs and explicit graph connections.

### 106.5 Real-time work blocks on UI or storage

The callback allocates, logs, loads a sample, queries a widget, or waits for a lock.

**Required correction:** pre-load resources and use bounded message queues. Keep I/O and UI work outside the audio callback.[^1][^2]

### 106.6 Offline renderer restarts every block

Effect buffers, oscillator phases, random states, and envelopes are reset at chunk boundaries.

**Required correction:** persistent engine state across the render, with explicit state transfer if chunked.

### 106.7 Stems are trimmed independently

Every stem starts at its first audible event, so the package is no longer aligned.

**Required correction:** common origin and shared render range.

### 106.8 Shared returns are printed twice

Wet effects are included in track stems and also exported as separate effect-return stems.

**Required correction:** explicit inclusion policy and stem reconciliation.

### 106.9 Plug-in state is represented only by a preset name

A render cannot be recreated because the plug-in state, version, or assets are missing.

**Required correction:** state capture, dependency manifest, and freeze option.

### 106.10 Every export is automatically normalised

A creative mix is changed without user consent.

**Required correction:** separate measurement from processing; make normalisation explicit and record it.

### 106.11 Monitor correction is printed into the master

Room correction, headphone crossfeed, or monitor attenuation changes the deliverable.

**Required correction:** separate monitor path from project master path.

### 106.12 Cache has no dependency model

A changed effect or asset continues to play stale audio.

**Required correction:** dependency hashes and targeted invalidation.

### 106.13 A successful file write is called a successful production

The file exists but may be silent, clipped, incomplete, misaligned, or missing requested outputs.

**Required correction:** multi-stage output validation and a render report.

### 106.14 Reproducibility is promised without environment capture

A third-party plug-in, external device, or GPU path changes output.

**Required correction:** determinism categories and explicit dependency capture.

### 106.15 One loudness target is hard-coded

A broadcast recommendation is mistaken for a universal music mastering rule.

**Required correction:** delivery profiles and context-specific measurement.

## 107. Failure semantics

Errors should identify:

- stage;
- node or resource ID;
- operation;
- error code;
- human-readable explanation;
- recoverability;
- whether output is complete or partial;
- possible next action;
- diagnostic context.

Do not swallow a plug-in error and continue as if the sound was rendered correctly.

---

# Part XVII — Worked production architectures

## 108. Example A: a minimal internal-synth composition

### Goal

Render a short IDM composition using internal synthesis, a small number of effects, and complete reproducibility.

### Graph

```text
Kick Synth ----> Kick EQ -----------+
Snare Synth ---> Snare Saturation ---+--> Drum Bus --> Master
Hat Sampler ---> Hat Filter ---------+

Bass Synth ----> Bass Filter --> Bass Saturation --> Bass Bus --> Master

Texture Synth -> Granular FX ----------------------> Texture Bus -> Master

Shared Reverb Send <------ Drum/Bass/Texture sends
        |
        v
   Reverb Return ----------------------------------------------> Master
```

### Render plan

- 48 kHz;
- stereo;
- 32-bit float internal processing;
- 24-bit PCM WAV output;
- deterministic per-entity random streams;
- full mix plus drum, bass, texture, and reverb-return stems;
- MIDI export for supported note and trigger data;
- full project snapshot and render manifest.

### Required checks

- full mix plays correctly;
- stems share an origin and duration;
- effect return is not double-counted;
- MIDI timing matches musical events within declared export resolution;
- render hash and dependency manifest are stored.

## 109. Example B: expensive granular and spectral sound design

### Goal

Use CPU-intensive granular sources and FFT-based effects without making interactive playback unreliable.

### Strategy

1. Keep musical events and automation live.
2. Pre-render stable granular source segments where their state is not being edited.
3. Cache each segment with asset, seed, automation, graph, and quality-profile hashes.
4. Use a live preview mode for changing parameters.
5. Re-render only invalidated regions or graph subtrees.
6. Run final full-quality offline rendering from an immutable snapshot.
7. Compare preview and final render for timing and structural equivalence.

### Important constraint

If a texture depends on continuous state or feedback from earlier bars, segment rendering must preserve its state. Do not render each bar independently unless the sound architecture is explicitly designed for independent bar-level instances.

## 110. Example C: full effect-chain and stem package

### Goal

Provide a mix, dry stems, processed stems, effect-return stems, and MIDI.

### Export definitions

| Output | Capture point | Includes master processing? |
|---|---|---|
| Master | Project master output | Yes, according to selected master profile |
| Dry bass | Bass instrument output before inserts | No |
| Wet bass | Bass path after inserts, before shared returns | No |
| Bass reverb return | Dedicated reverb return bus | No |
| Percussion stem | Percussion subgroup post-fader | No |
| Texture stem | Texture subgroup post-fader | No |

The package README must state that the wet bass and reverb return are separate and should be summed according to the original bus balance. The stem reconciliation report should verify the declared pre-master reconstruction if the selected graph makes that possible.

## 111. Example D: external hardware sound source

### Goal

Integrate a hardware synthesizer into a reproducible project.

### Procedure

1. Record device make/model, firmware, patch or parameter state, MIDI configuration, clock mode, and audio interface routing.
2. Send a known test sequence and alignment marker.
3. Capture audio through the configured input path.
4. Measure round-trip latency and compensate the recorded capture.
5. Record the audio into the project as an immutable take.
6. Store the take checksum and device metadata.
7. Use the captured audio for future deterministic project playback.

The hardware itself remains an external dependency. The captured take is the reproducible realisation used by the project unless the user explicitly re-records the hardware.

## 112. Example E: multi-movement long-form composition

### Goal

Render a long work with changing tempo, different sound palettes, long reverb tails, and many independent stems.

### Procedure

- compile the full musical timeline from the project model;
- validate tempo and meter maps;
- prepare all instrument resources;
- validate each movement's graph state;
- define whether instrument state continues across movement boundaries;
- define whether effects are reset, allowed to decay, or carried forward;
- create one immutable render snapshot per movement plus a global manifest;
- render movements sequentially if state crosses boundaries;
- render independent stems in parallel only where state and dependencies allow;
- join or package the output without altering sample alignment;
- validate every movement and the full work.

This approach allows a long-form composition to remain manageable without pretending that independent sections are always independent audio systems.

---

# Part XVIII — Testing, benchmarks, and acceptance criteria

## 113. Test categories

The audio production system should have:

- unit tests for DSP and utility processors;
- graph validation tests;
- property-based routing tests;
- event scheduling tests;
- tempo-map conversion tests;
- automation interpolation tests;
- plug-in lifecycle tests;
- real-time stress tests;
- offline-render tests;
- cache invalidation tests;
- stem alignment tests;
- stem reconciliation tests;
- MIDI round-trip tests;
- manifest and package tests;
- long-duration stability tests;
- listening tests.

## 114. Essential automated tests

### 114.1 Routing identity

A known source routed through a known unity path should produce the expected output within numerical tolerance.

### 114.2 Channel mapping

Test mono/stereo and multichannel mappings, including channel order and downmix coefficients.

### 114.3 Event offset

Schedule an impulse or note at a known sample offset inside a block and verify its output alignment.

### 114.4 Tempo-map transition

Place events before, at, and after tempo changes. Verify that their musical positions map to the expected sample positions.

### 114.5 Automation boundaries

Test stepped, ramped, and curved automation at block boundaries and at sub-block sample offsets.

### 114.6 Latency compensation

Create paths with known latency differences and verify the compensated output alignment.

### 114.7 Effect-tail preservation

Use known delay/reverb fixtures and verify tail policy and render length.

### 114.8 Preview/final equivalence

Use a deterministic simple graph and confirm that preview and final output differ only according to declared quality settings.

### 114.9 Cache invalidation

Change each dependency class in turn and verify that the relevant cache is invalidated and unrelated caches remain valid.

### 114.10 Stem reconstruction

Render known additive stems and verify their declared reconstruction relationship.

### 114.11 Render interruption

Cancel and restart jobs. Confirm that incomplete files are never labelled as completed.

### 114.12 Manifest completeness

Verify that every output has a manifest entry, hash, format, duration, and source revision.

## 115. Property tests

Useful invariants include:

- a graph with incompatible ports cannot commit;
- every audible source has a declared route or explicit disconnection;
- every feedback cycle has a delay primitive;
- every stem has a declared capture point;
- every render job refers to immutable revisions;
- every cache key includes all declared dependencies;
- a project save/load round trip preserves graph connectivity;
- a frozen node retains its source lineage;
- a stopped transport does not continue emitting stale scheduled notes;
- a graph swap does not free resources still in use by the audio thread;
- an export package cannot pass validation while required files are missing.

## 116. Performance benchmarks

Benchmark across:

- multiple sample rates;
- multiple block sizes;
- increasing voice counts;
- increasing effect counts;
- parallel and serial graphs;
- multi-output instruments;
- high-latency processors;
- large sample libraries;
- long-form offline renders;
- high channel counts;
- concurrent analysis and visualisation.

Report hardware and environment with benchmark results. A CPU percentage without sample rate, block size, graph composition, hardware, and plug-in list is not reproducible evidence.

## 117. Audio regression fixtures

Maintain a small but diverse fixture library:

1. single impulse through a routing graph;
2. oscillator with known phase and envelope;
3. note sequence across a tempo change;
4. automation ramp with sample-offset points;
5. serial and parallel effects;
6. sidechain compression fixture;
7. feedback delay fixture;
8. convolution tail fixture;
9. multi-output drum instrument;
10. multichannel mapping fixture;
11. additive stem fixture;
12. stochastic but seeded granular fixture;
13. plug-in state restore fixture;
14. interrupted offline render fixture;
15. external audio capture with alignment marker.

Each fixture should have a project snapshot, expected structural properties, expected render manifest, and reference audio or quantitative tolerances.

## 118. Definition of done for an audio-production feature

A feature is not complete because its control appears in the UI.

A feature is complete only when:

- its data model is defined;
- its signal or event semantics are documented;
- it integrates with the canonical graph;
- its real-time and offline behaviour are defined;
- its latency and tail behaviour are represented;
- its state is serialised;
- its cache dependencies are declared;
- its exports are specified;
- its failure modes are visible;
- it has automated tests;
- it has a representative listening fixture;
- it is reflected in the relevant manual and release notes.

---

# Part XIX — Implementation roadmap

## 119. Stage 1 — Canonical graph and offline renderer

Priority: foundational.

Deliver:

- typed audio nodes and ports;
- explicit channel layouts;
- graph validation;
- serial and parallel routing;
- internal instrument sources;
- file and sample sources;
- offline block renderer;
- WAV output;
- simple master bus;
- render manifest;
- file validation.

Acceptance: a small project can be rendered offline through the same graph model used by the mixer.

## 120. Stage 2 — Live playback and transport

Deliver:

- audio-device abstraction;
- bounded real-time callback;
- transport and seek;
- sample-accurate event dispatch;
- preloaded instrument resources;
- meter snapshots;
- underrun diagnostics;
- safe shutdown.

Acceptance: the same prepared graph can play in real time without blocking operations in the callback.

## 121. Stage 3 — Mixer and routing completeness

Deliver:

- per-channel inserts;
- pre/post-fader sends;
- shared returns;
- subgroups;
- sidechains;
- multi-output instruments;
- master and monitor-path separation;
- explicit stem capture points.

Acceptance: every visible mixer operation changes the canonical graph and is audible in preview and offline render.

## 122. Stage 4 — Automation, latency, and plug-in hosting

Deliver:

- stable parameter IDs;
- automation interpolation;
- parameter smoothing;
- plug-in adapters;
- processor lifecycle;
- latency reporting;
- path compensation;
- tail metadata;
- state save/load.

Acceptance: automated parameters, latency, and processor state survive save/load and render correctly.

## 123. Stage 5 — Preview, pre-render, and cache

Deliver:

- quality profiles;
- per-node and per-subgraph caches;
- dependency hashes;
- freeze/unfreeze workflow;
- stale-cache detection;
- live/frozen handoff;
- expensive effect pre-render.

Acceptance: changing one dependency invalidates the correct cache and never plays stale audio as current.

## 124. Stage 6 — Stems and full production package

Deliver:

- explicit stem definitions;
- dry/wet policies;
- role stems;
- effect-return stems;
- MIDI export;
- project export;
- README and manifest;
- checksums;
- package validation;
- stem reconciliation.

Acceptance: a user can export a complete, documented production package and reconstruct the declared reference mix where the stem policy promises it.

## 125. Stage 7 — Advanced reproducibility and production QA

Deliver:

- per-entity random streams;
- determinism categories;
- environment manifests;
- sample-accurate and perceptual regression testing;
- loudness and true-peak profiles;
- long-form render recovery;
- render comparison tools;
- benchmark suite.

Acceptance: the application can explain what is reproducible, identify what is not, and validate every generated deliverable.

---

# Part XX — Developer checklists

## 126. Audio graph checklist

- [ ] Nodes have stable IDs and declared types.
- [ ] Ports declare media type and channel layout.
- [ ] Connections declare channel mapping.
- [ ] Sidechain paths are separate from audible paths.
- [ ] Feedback uses explicit delay/state primitives.
- [ ] Graph validation runs before execution.
- [ ] Graph revisions are immutable after commit.
- [ ] Live graph swaps are safe for the audio thread.
- [ ] Latency and tail metadata are present.

## 127. Real-time engine checklist

- [ ] Callback avoids allocation and blocking I/O.
- [ ] UI and rendering work are off the audio thread.
- [ ] Resources are prepared before activation.
- [ ] Event dispatch supports sample offsets.
- [ ] Same-sample ordering is deterministic.
- [ ] Transport discontinuities are handled.
- [ ] Metering is read through safe snapshots.
- [ ] Underruns and overload are visible.
- [ ] Shutdown cannot free active audio resources.

## 128. Offline renderer checklist

- [ ] Render jobs use immutable project snapshots.
- [ ] Plugin and asset validation happens before rendering.
- [ ] Tempo maps and automation are compiled correctly.
- [ ] Pre-roll and tail policy are defined.
- [ ] State continues correctly across blocks and chunks.
- [ ] Cancellation cannot create a false completed output.
- [ ] Output files are validated after writing.
- [ ] Manifest and checksums are generated.

## 129. Reproducibility checklist

- [ ] Random streams are scoped and versioned.
- [ ] Processor determinism categories are recorded.
- [ ] Asset hashes are stored.
- [ ] Plug-in versions and state are captured.
- [ ] Renderer and DSP versions are recorded.
- [ ] Render profile and routing graph are hashed.
- [ ] Environment limitations are explicit.
- [ ] Cache keys include every audio dependency.

## 130. Export checklist

- [ ] Master and pre-master options are distinct.
- [ ] Stem capture points are documented.
- [ ] Dry, wet, send, and return semantics are clear.
- [ ] Stems share a common alignment origin.
- [ ] Stem additivity claims are tested.
- [ ] MIDI limitations are reported.
- [ ] Sample rate, bit depth, and channel layout are recorded.
- [ ] Monitor-only processing is excluded unless requested.
- [ ] README, manifest, and checksums are included.
- [ ] The project and required assets are included or declared external.

---

# Part XXI — Design decisions that should remain stable

## 131. Ten non-negotiable production principles

1. **The composition model is not the audio graph.** Musical meaning and signal execution are connected but separate.
2. **The audio graph is explicit.** Routing must never depend on UI order or hidden assumptions.
3. **Real-time processing is bounded.** The audio thread does not perform unbounded I/O, allocation, or blocking work.
4. **Preview and final rendering share semantics.** They may differ in declared quality, not in hidden musical decisions.
5. **Every render is a snapshot.** A render job is immutable and identifies its source revision.
6. **Latency and tails are first-class properties.** They cannot be approximated away silently.
7. **Stems have declared meanings.** Their capture points and additivity are documented and testable.
8. **Reproducibility has levels.** Do not promise bit identity when the environment or processor cannot provide it.
9. **Delivery is validated.** File existence is not proof of a complete production package.
10. **Measurements inform, not replace, listening.** Technical correctness and artistic success are separate axes.

## 132. The production system as a creative instrument

The audio engine is not merely a final technical stage. Its capabilities shape what the composer can explore.

A dependable engine enables:

- long feedback structures without unpredictable failure;
- complex parallel processing with clear routing;
- multi-output and multi-role sound sources;
- pre-rendering of computationally expensive textures;
- editable effects and automation;
- precise transitions and sample-accurate events;
- reliable audition of alternatives;
- repeatable production decisions;
- complete and useful stem exports;
- preservation of a work's sound identity.

The system should make complex production possible without making its state opaque. A composer should be able to discover how a sound reaches the master, inspect the processor state, render an alternative, compare it, and return to an earlier result without reconstructing the entire session manually.

A strong audio engine protects creative agency by making the consequences of production decisions understandable and reversible.

---

# Appendix A — Canonical reference records

## A1. Processor capability record

```json
{
  "processor_id": "processor-spectral-freeze-01",
  "processor_type": "audio_effect",
  "version": "1.2.0",
  "ports": {
    "inputs": [{"id": "main-in", "media": "audio", "layout": "stereo"}],
    "outputs": [{"id": "main-out", "media": "audio", "layout": "stereo"}]
  },
  "capabilities": {
    "realtime": true,
    "offline": true,
    "sidechain": false,
    "automation": true,
    "state_serialisation": true,
    "determinism": "D1"
  },
  "processing": {
    "latency_frames": 2048,
    "tail": {"kind": "unbounded_until_reset", "maximum_seconds": 30.0},
    "supported_sample_rates": [44100, 48000, 88200, 96000]
  },
  "parameters": [
    {
      "id": "freeze_amount",
      "name": "Freeze Amount",
      "type": "float",
      "normalised_range": [0.0, 1.0],
      "unit": "%",
      "smoothing_ms": 12.0,
      "automation": true
    }
  ]
}
```

## A2. Stem definition record

```json
{
  "stem_id": "stem-texture-wet",
  "name": "Texture — Wet",
  "capture": {
    "node_ids": ["bus-texture"],
    "tap": "post_fader",
    "include_master_processing": false
  },
  "effects": {
    "track_inserts": true,
    "shared_returns": false,
    "dedicated_returns": true
  },
  "format": {
    "container": "wav",
    "encoding": "pcm_s24le",
    "sample_rate": 48000,
    "channel_layout": "stereo"
  },
  "alignment": {
    "origin": "project_start",
    "common_length": true,
    "tail_policy": "package_max_tail"
  },
  "reconstruction": {
    "claim": "non_additive_by_design",
    "reason": "Master bus contains shared nonlinear processing"
  }
}
```

## A3. Render profile record

```json
{
  "profile_id": "profile-final-master-01",
  "mode": "offline_final",
  "sample_rate": 48000,
  "internal_format": "float32",
  "output_container": "wav",
  "output_encoding": "pcm_s24le",
  "channel_layout": "stereo",
  "oversampling": "processor_defined_high_quality",
  "dither": "triangular_at_final_integer_conversion",
  "include_master_chain": true,
  "include_monitor_chain": false,
  "tail_policy": {
    "kind": "declared_then_bounded_silence_check",
    "maximum_seconds": 30
  },
  "determinism_policy": "record_and_reproduce_seeded_state"
}
```

The example dither setting is illustrative. The final policy should be chosen for the target encoding and production workflow.

---

# Appendix B — Example render preflight algorithm

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    code: str
    message: str
    entity_id: str | None = None


@dataclass
class PreflightReport:
    diagnostics: list[Diagnostic] = field(default_factory=list)

    @property
    def can_render(self) -> bool:
        return not any(d.severity == Severity.ERROR for d in self.diagnostics)


def validate_render_request(project, graph, profile, assets, processors) -> PreflightReport:
    report = PreflightReport()

    if project is None:
        report.diagnostics.append(Diagnostic(
            Severity.ERROR, "PROJECT_MISSING", "No project snapshot was supplied."
        ))
        return report

    if profile.sample_rate <= 0:
        report.diagnostics.append(Diagnostic(
            Severity.ERROR, "INVALID_SAMPLE_RATE", "Sample rate must be positive."
        ))

    if not graph.validate_connections():
        report.diagnostics.append(Diagnostic(
            Severity.ERROR, "GRAPH_INVALID", "Audio graph validation failed."
        ))

    for asset in assets:
        if not asset.exists:
            report.diagnostics.append(Diagnostic(
                Severity.ERROR, "ASSET_MISSING", f"Required asset is missing: {asset.name}", asset.id
            ))
        elif not asset.checksum_matches:
            report.diagnostics.append(Diagnostic(
                Severity.ERROR, "ASSET_CHECKSUM_MISMATCH",
                f"Asset does not match the recorded checksum: {asset.name}", asset.id
            ))

    for processor in processors:
        if not processor.can_restore_state:
            report.diagnostics.append(Diagnostic(
                Severity.ERROR, "PROCESSOR_STATE_UNAVAILABLE",
                f"Processor state cannot be restored: {processor.name}", processor.id
            ))
        if processor.determinism == "D4":
            report.diagnostics.append(Diagnostic(
                Severity.WARNING, "DETERMINISM_UNKNOWN",
                f"Processor determinism is unknown: {processor.name}", processor.id
            ))

    if profile.include_monitor_chain:
        report.diagnostics.append(Diagnostic(
            Severity.WARNING, "MONITOR_CHAIN_INCLUDED",
            "Monitor-only processing is included in the requested render."
        ))

    return report
```

The code is an illustrative validation pattern. Production code should define concrete types, exception handling, resource ownership, and actual graph/asset APIs.

---

# Appendix C — Example block renderer pseudocode

```text
prepare immutable render snapshot
initialise instruments, processors, and random streams
calculate graph execution order and latency
warm up state using configured pre-roll

for each output block:
    determine absolute sample range for block
    collect all events falling inside block
    sort events by sample offset and declared priority

    cursor = 0
    for each event group:
        render audio from cursor to event offset
        apply event group at exact offset
        cursor = event offset

    render remaining samples in block
    pass buffers through graph in validated order
    apply explicit feedback state transitions
    write requested capture points to output buffers
    update bounded meter snapshots
    advance absolute sample position

flush declared tails according to tail policy
finalise audio files
calculate checksums and measurements
validate all outputs
write manifest and package report
```

This pseudocode illustrates the separation between event scheduling, graph processing, capture, and file finalisation. Real implementations may schedule events per processor or use vectorised/block event structures.

---

# Appendix D — Production diagnostic examples

| Code | Meaning | Suggested response |
|---|---|---|
| `GRAPH_CYCLE_INVALID` | A cycle has no explicit feedback delay | Inspect routing and insert an intentional feedback primitive |
| `CHANNEL_LAYOUT_MISMATCH` | Source and destination layouts are incompatible | Add a declared channel mapper |
| `PLUGIN_MISSING` | Required plug-in cannot be found | Locate, freeze, substitute with approval, or cancel |
| `PLUGIN_STATE_RESTORE_FAILED` | Stored state could not be loaded | Report processor and version mismatch |
| `LATENCY_UNKNOWN` | A processor's latency is not known | Measure, configure, or report uncompensated path |
| `TAIL_UNBOUNDED` | Processor cannot declare a finite tail | Require a configured maximum or manual render endpoint |
| `AUDIO_UNDERRUN` | Real-time engine missed an audio deadline | Inspect callback load, graph cost, buffer size, and background tasks |
| `CACHE_STALE` | Cached audio does not match current dependencies | Invalidate and re-render affected nodes |
| `STEM_ALIGNMENT_FAILED` | Stem origins or durations differ unexpectedly | Re-render from common range and snapshot |
| `STEM_RECONCILIATION_FAILED` | Stems do not match declared reconstruction | Inspect capture points, sends, returns, and nonlinear processing |
| `OUTPUT_CLIPPING` | Output exceeds selected peak policy | Inspect gain structure or apply an explicit mastering process |
| `OUTPUT_SILENT` | Output contains unexpected silence | Inspect routing, instrument activation, event scheduling, and asset loading |
| `MANIFEST_INCOMPLETE` | Required provenance is missing | Complete dependency or environment capture |
| `PACKAGE_INCOMPLETE` | Requested deliverables are missing | Rebuild or repair package before marking complete |

---

# Appendix E — References and technical reading

The sources below are technical references for the architecture. Standards and APIs evolve; implementation work should verify the current version and licence terms before adopting them.

1. **PortAudio — Writing a Callback Function.** Guidance on real-time callback constraints, including avoiding memory allocation, I/O, mutex operations, and unpredictable system calls.  
   https://portaudio.com/docs/v19-doxydocs/writing_a_callback.html

2. **PortAudio — Callback Tips.** Practical notes on keeping callback work bounded and moving I/O and other expensive tasks to foreground threads.  
   https://github.com/PortAudio/portaudio/wiki/Tips_Callbacks

3. **Steinberg — VST 3 API Documentation.** Processor/controller separation, lifecycle, threading model, and plug-in host integration.  
   https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical%2BDocumentation/API%2BDocumentation/Index.html

4. **Steinberg — Parameters and Automation.** Parameter identity, automation queues, sample-offset points, and host/controller responsibilities.  
   https://steinbergmedia.github.io/vst3_dev_portal/pages/Technical%2BDocumentation/Parameters%2BAutomation/Index.html

5. **CLAP — Audio Plugin API.** A plug-in ABI with explicit extensions and thread specifications.  
   https://github.com/free-audio/clap

6. **CLAP — Thread Check Extension and Plugin Lifecycle.** Main-thread/audio-thread responsibilities, activation, and processing lifecycle.  
   https://github.com/free-audio/clap/blob/main/include/clap/ext/thread-check.h  
   https://github.com/free-audio/clap/blob/main/include/clap/plugin.h

7. **Open Sound Control — Specification 1.0.** Message structure, address spaces, bundles, and time tags.  
   https://opensoundcontrol.stanford.edu/spec-1_0.html

8. **JACK Audio Connection Kit — Latency Functions.** Capture/playback latency and graph-path latency reporting.  
   https://jackaudio.org/api/group__LatencyFunctions.html

9. **ITU-R BS.1770-5 — Algorithms to measure audio programme loudness and true-peak audio level.** Recommendation approved in November 2023 and listed as in force on the ITU page consulted.  
   https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/en

10. **EBU R 128, Version 5.0 — Loudness normalisation and permitted maximum level of audio signals.** Broadcast-context programme loudness recommendation, published November 2023.  
    https://tech.ebu.ch/publications/r128

11. **MIDI Association — MIDI 2.0.** Overview of MIDI 2.0 and its relationship to MIDI 1.0.  
    https://midi.org/midi-2-0

12. **MIDI Association — Universal MIDI Packet and MIDI 2.0 Protocol Specification.** UMP and MIDI 2.0 protocol definition.  
    https://midi.org/universal-midi-packet-ump-and-midi-2-0-protocol-specification

13. **EBU Tech 3285 — BWF: A Format for Audio Data Files in Broadcasting.** Broadcast Wave Format specification and metadata structure.  
    https://tech.ebu.ch/publications/tech3285/

14. **EBU Tech 3285 Version 2 — Broadcast Wave Format Specification.** Technical specification PDF.  
    https://www.ebu.ch/files/live/sites/tech/files/shared/tech/tech3285.pdf

15. **FFmpeg — Resampler Documentation.** Sample-rate conversion, channel-layout rematrixing, and sample-format conversion.  
    https://www.ffmpeg.org/ffmpeg-resampler.html

16. **FFmpeg — Filters Documentation, `loudnorm`.** EBU R 128 loudness normalisation filter and single-/double-pass operation.  
    https://ffmpeg.org/ffmpeg-filters.html#loudnorm

17. **JUCE — AudioProcessorGraph.** Example of graph-based audio processing, nodes, ports, and connections.  
    https://docs.juce.com/develop/classjuce_1_1AudioProcessorGraph.html

18. **JACK Audio Connection Kit — API Overview.** Client model, synchronous graph execution, low-latency operation, transport, ports, and ring buffers.  
    https://jackaudio.org/api/

---

# Final principle

The audio engine is the part of the generative instrument where musical intention becomes a physical signal. It must be powerful enough to support experimental sound, complex routing, unstable textures, long-form structures, and hybrid instruments, while remaining understandable, editable, measurable, and dependable.

The correct objective is not to make every render identical under every possible circumstance. It is to make the system honest about its dependencies, explicit about its signal flow, accurate about its timing, safe in real-time operation, complete in offline rendering, and reproducible to the greatest degree the chosen instruments and environment permit.

**A production system is trustworthy when it can explain what it rendered, how it rendered it, what was included, what was omitted, what can be reproduced, and what remains dependent on the outside world.**
