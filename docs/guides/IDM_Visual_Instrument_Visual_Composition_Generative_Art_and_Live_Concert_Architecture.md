# IDM Visual Instrument

## Visual Composition, Generative Art & Live Concert Architecture

**A companion reference for designing a music-aware visual generation system for IDM concerts**  
**Documentation family:** IDM Generative Instrument Library  
**Volume:** 11 — Visual Composition & Live Visual Performance  
**Status:** Reference philosophy, compositional manual, and implementation architecture  
**Version:** 1.0  
**Audience:** Creative coders, visual artists, VJs, music-software developers, technical artists, projection designers, shader programmers, composers, and live-performance engineers  
**Primary domain:** Generative concert visuals for IDM and experimental electronic music

---

# Abstract

A visual system for an IDM concert should do more than display waveforms, react to bass energy, or attach a collection of effects to a beat detector. It should function as a second compositional instrument: one that receives musical structure, interprets relationships, develops visual material, manages attention, creates continuity and contrast, and remains performable in real time.

This volume defines a philosophy and architecture for such a system. It treats visuals as compositions made from objects, scenes, motifs, patterns, motion gestures, transformations, spatial relationships, and temporal forms. It connects those visual entities to the musical ontology and generative architecture established in the ten companion manuals, while preserving the independence of visual composition. A musical motif may inspire a visual motif, but the visual system must not reduce every note to a shape or every frequency band to a colour.

The manual covers:

- the identity and responsibilities of a live visual instrument;
- the relationship between visual composition and the existing IDM music-generation library;
- a canonical visual ontology and data model;
- music-aware, audio-reactive, and performer-controlled input modes;
- audiovisual mapping as a semantic and compositional process;
- visual motifs, patterns, phrases, forms, motion grammars, and scene architecture;
- generative image families, procedural systems, hybrid media, and rendering methods;
- perceptual orchestration, visual attention, density, depth, and legibility;
- live performance, cueing, overrides, synchronization, projection, and multi-output systems;
- GPU rendering, software architecture, protocols, safety, evaluation, and implementation planning.

The central proposition is:

> **The visual instrument should compose with the music, not merely react to its waveform. It should understand enough about the musical work to create visual relationships that have identity, memory, development, contrast, and form.**

This does not mean that the visual system must imitate the music literally. It means the system should be able to choose when to synchronise, when to diverge, when to reinforce, when to contradict, when to remain still, and when to become an independent foreground.

---

# How to use this manual

## 1. Scope

This document is dedicated to visuals for live IDM and experimental-electronic performances, and to software capable of generating those visuals. It is simultaneously:

1. a **visual composition manual** for defining visual language, material, motion, scenes, and concert-scale form;
2. a **mapping manual** for translating musical intent and sound into visual behaviour;
3. a **generative-system specification** for building reusable visual algorithms and scene directors;
4. a **live-performance manual** for cueing, control, synchronization, output, and recovery;
5. a **developer reference** for data models, rendering architecture, testing, and safety.

It is not a tutorial for one specific visual application, a catalogue of visual effects, a replacement for the music-generation manuals, or an instruction to use one particular rendering framework. The architecture is deliberately implementation-neutral.

## 2. Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement strength.

- **MUST / MUST NOT:** required to preserve artistic, safety, data, or runtime integrity.
- **SHOULD / SHOULD NOT:** strong recommendation; a deviation requires a documented reason.
- **MAY:** optional capability.
- **Visual intention:** the desired perceptual or artistic effect of a visual passage.
- **Visual estimate:** a computational prediction about the rendered or perceived result, not a universal fact about every screen or viewer.
- **Music-aware input:** structured musical data supplied by the composition or audio engine.
- **Audio-reactive input:** features inferred from an audio signal when structured musical data is unavailable or insufficient.
- **Commit:** acceptance of a visual candidate or edit into the authoritative visual project.
- **Live override:** a bounded, temporary performer action that takes precedence over an automatic visual plan.

## 3. A crucial distinction: visualizer, VJ system, and visual instrument

These categories overlap, but they are not identical.

| System | Primary behaviour | Typical limitation |
| --- | --- | --- |
| Audio visualizer | Displays measured or inferred audio features | Often has no memory of musical form or visual identity |
| VJ playback system | Selects, layers, mixes, and manipulates prepared media | May not understand the structure of the music or the media's internal motifs |
| Generative visual system | Creates images or motion procedurally | May generate activity without a meaningful visual composition |
| Music-aware visual instrument | Interprets musical structure, composes visual material, and supports live control | Requires a coherent model, a reliable timing architecture, and a visual grammar |

The goal of this volume is the fourth category. It can include the first three as modes or subsystems, but must not be limited to them.

## 4. The epistemic rule

The system MUST distinguish four kinds of information:

1. **Musical fact:** a section boundary, note event, motif identity, pattern cycle, or tempo-map event explicitly supplied by the composition system.
2. **Audio observation:** an RMS envelope, onset estimate, spectral centroid, detected beat, or other signal-derived feature.
3. **Visual intention:** a composer-authored direction such as “the background should gradually become the foreground”.
4. **Visual outcome estimate:** a prediction about attention, density, contrast, legibility, motion intensity, or rendering cost.

These categories must not be silently conflated. A detected transient is not necessarily a kick. A high spectral centroid is not necessarily perceived brightness. A section boundary supplied by the composition engine is more authoritative than a visual beat detector guessing that a new section has begun.

---

# Part I — The philosophy of live IDM visuals

## 5. Visuals are a parallel compositional voice

A live visual performance shares time with music, but it does not need to duplicate the music. Its relationship to the composition can take many forms:

- **Unison:** visual events coincide with important musical events.
- **Reinforcement:** visual behaviour strengthens the identity of a musical gesture.
- **Complement:** visuals reveal a different dimension of the same material.
- **Counterpoint:** visual motion or structure develops independently while remaining related.
- **Call and response:** one medium introduces an idea and the other answers it.
- **Transformation:** a musical process is translated into a different visual process.
- **Interruption:** a visual cut, freeze, rupture, or omission marks a musical event.
- **Independence:** visuals temporarily establish their own time, material, or attention structure.

The system should be capable of all these relationships. It should not be locked to permanent beat synchronisation.

## 6. Concert visuals are not the same as desktop visuals

A concert image is encountered under unusual conditions: the audience may be far from the screen, the screen may be very wide or physically irregular, ambient light may be high, the performer may partially obscure the projection, several surfaces may be visible at once, and the image may need to remain meaningful while the audience is moving or looking elsewhere.

A concert visual system therefore needs to consider:

- distance and viewing angle;
- screen aspect ratio, resolution, pixel pitch, and physical scale;
- projector black level, brightness, contrast, focus, and ambient light;
- LED-wall brightness, scan behaviour, colour calibration, and moiré risk;
- safe title and detail sizes;
- motion readability from a distance;
- output latency, frame pacing, and synchronization;
- audience comfort and photosensitivity;
- the artist's ability to intervene without breaking the visual composition;
- graceful degradation when a GPU, source, network, or output fails.

A beautiful 1440-pixel desktop image is not automatically a good concert image. The system must test the actual output surface or a credible simulation of it.

## 7. Visual identity is more important than constant novelty

A visual set should have a vocabulary. It may contain several unrelated-looking scenes, but those scenes should have a reason to coexist: shared geometry, texture, movement principles, palette relationships, recurring symbols, spatial habits, or a common treatment of time.

The visual identity may be:

- geometric and diagrammatic;
- organic and fluid;
- typographic and editorial;
- photographic and documentary;
- synthetic and spatial;
- noisy, degraded, or archival;
- monochromatic and material-driven;
- colourful and spectral;
- hybrid, switching between incompatible materials deliberately.

No one of these directions is a definition of IDM visuals. The visual system should support distinct identities and preserve them across a performance.

## 8. Visual complexity is not visual quality

An image can be technically elaborate yet perceptually empty. A minimal line, a slow camera movement, a held composition, or a single object can be more powerful than a full-screen particle field.

The system must distinguish:

- **algorithmic complexity:** how much computation or procedural structure produces the image;
- **image complexity:** how many shapes, textures, colours, edges, and motion sources are visible;
- **perceptual complexity:** how much attention and interpretation the image demands;
- **formal complexity:** how many relationships and transformations occur across time.

These dimensions may move independently. The visual director should be able to reduce the visible image while increasing formal or perceptual tension.

## 9. Twenty-four principles for the visual instrument

1. **Compose, do not merely react.** Visuals MUST have visual material, identity, and development independent of raw audio levels.
2. **Preserve musical meaning.** When structured music data exists, the system SHOULD use it before relying on audio inference.
3. **Do not translate every note literally.** Musical data is a source of relationships and gestures, not a command to draw a symbol for every event.
4. **Use visual memory.** Recurring musical material SHOULD be capable of recurring visual identity.
5. **Variation should preserve lineage.** A transformed visual motif should remain traceably related to its source when that relationship is intentional.
6. **Silence and stillness are valid.** The renderer MUST support meaningful low-activity and no-motion states.
7. **A scene needs a purpose.** Every scene SHOULD have an attentional, formal, or material function.
8. **A transition is a compositional event.** Scene changes MUST not be reduced to arbitrary crossfades.
9. **Motion needs hierarchy.** Not every object should move with equal speed, scale, or prominence.
10. **Contrast needs space.** Bright, dense, fast, or highly detailed passages SHOULD be balanced by quieter visual states where useful.
11. **Do not hard-code genre stereotypes.** No visual formula should be mandatory for IDM.
12. **Separate intent from implementation.** “Fragments assemble” is an intention; a particle system is only one possible implementation.
13. **Use stable clocks.** Musical, audio, performance, and GPU clocks MUST be distinguished and reconciled.
14. **Prefer event semantics over fragile threshold guesses.** Known motif and section events SHOULD be transmitted directly.
15. **Audio analysis remains useful.** It SHOULD complement semantic input and enable external-audio use.
16. **Mapping must be inspectable.** Every important mapping rule MUST have a defined input, scope, transform, output, and smoothing policy.
17. **Randomness must be bounded and reproducible when requested.** A visual variation should be reproducible by seed or saved state when it is accepted.
18. **Live controls must be safe.** Performer actions MUST be bounded, reversible where possible, and visible in system state.
19. **The output surface is part of the composition.** Aspect ratio, crop, brightness, and viewing distance MUST inform design.
20. **Performance is a creative requirement.** A beautiful generator that drops frames during the set is not a successful live instrument.
21. **Failure must preserve continuity.** Loss of an input or generator MUST lead to a safe fallback rather than a blank or uncontrolled output.
22. **Safety is designed in.** Flashing, high-contrast patterns, and rapid motion MUST be assessed before performance.
23. **The audience is not a debugging screen.** Diagnostic overlays and unreviewed interfaces MUST not appear on public output.
24. **The performer remains an author.** The system MUST allow direct intervention, manual scene choices, and intentional deviation from the automatic plan.

---

# Part II — How this volume connects to the ten existing manuals

The visual system should reuse the conceptual work already established. It must not invent a second, incompatible theory of music merely because it is dealing with images.

## 10. Companion-volume map

| Existing volume | Relevant concepts to reuse | How they apply to visuals |
| --- | --- | --- |
| [**1. IDM Field Guide for Composers, Producers, and Programmers**](<IDM_Field_Guide_for_Composers_Producers_and_Programmers(1).md>) | IDM as dance-music materials treated as exploratory composition; pulse, meter, breakbeat, repetition, phase, mathematical systems, listening | Establish the musical vocabulary that visual scenes interpret. See Parts I–V and the mathematics/programmer sections. |
| [**2. Advanced Composition and Generative Systems**](<IDM_Advanced_Composition_and_Generation_Appendix(1).md>) | Listener expectation, auditory grouping, phrase syntax, long-form time, generative composition, complete work development | Build visual expectation, phrase behaviour, long-range visual form, and a complete concert arc. See Parts I–V and VII–VIII. |
| [**3. IDM Composition Atlas**](<IDM_Composition_Atlas_Patterns_Phrases_and_Track_Structures(1).md>) | 24 rhythmic pattern families, 12 pattern relationships, motif families, phrase functions, 18 track-form models, transition design | Derive visual pattern families, motif transformations, visual phrases, section functions, and scene transitions. See Parts II–V and VII–IX. |
| [**4. IDM Sound Design Manual**](<IDM_Sound_Design_Synthesis_and_Hybrid_Sound_Architecture(1).md>) | Sound objects, micro-/instrument-/track identity, hybrid structures, spectral and temporal behaviour, effects as transformations | Treat visual elements as designed objects with identity, excitation, envelope, material, motion, space, and transformability. See Parts I, V, VI, and IX. |
| [**5. Generative Instrument: Philosophy, Principles & Design Constitution**](<IDM_Generative_Instrument_Philosophy_Principles_and_Design_Constitution(1).md>) | Artistic intent, decision hierarchy, accepted material, constraints, mutation contracts, human agency, reproducibility | Govern visual generation, preservation, bounded mutation, candidate selection, and performer control. See Parts II, IV–VII, X–XII. |
| [**6. Musical Ontology, Representation & Composition Data Architecture**](<Musical_Ontology_Representation_and_Composition_Data_Architecture(1).md>) | Canonical entities, graph relationships, stable IDs, exact time, provenance, schema versioning, contracts | Reuse musical IDs and time semantics; add visual entities as a linked graph, not a duplicate musical model. See Parts II–V, VII–XII. |
| [**7. Generative Intelligence, Algorithms & Decision-Making**](<Generative_Intelligence_Algorithms_and_Decision_Making(1).md>) | Hierarchical planning, algorithm families, candidate generation, selection, uncertainty, mutation, adaptive directors | Build visual planners, candidate scenes, procedural generators, state machines, and selection/evaluation systems. See Parts II–XII and XV–XVIII. |
| [**8. Perceptual Orchestration, Attention & Musical Scene Architecture**](<IDM_Perceptual_Orchestration_Attention_and_Musical_Scene_Architecture(1).md>) | Auditory object, figure/ground, salience, attention, density, masking, scene state, spatial organisation | Translate the listener-centred model into visual attention, visual grouping, density, scene depth, and cross-modal focus. See Parts II–XIV. |
| [**9. Audio Engine, Rendering, Routing & Reproducible Production**](<IDM_Audio_Engine_Rendering_Routing_and_Reproducible_Production(1).md>) | Real-time execution, event scheduling, clock domains, graph execution, latency, preview, render manifests, performance and recovery | Apply the same engineering discipline to visual event scheduling, rendering, output routing, frame budgets, state snapshots, and show manifests. See Parts I–V, IX–XIV, and XVIII–XX. |
| [**10. Creative Interaction, Composer Agency & Generative UX**](<Creative_Interaction_Composer_Agency_and_Generative_UX(1).md>) | Semantic controls, live mode, bounded delegation, undo/history, local editing, audition, explanation, accessibility | Design the visual workspace, performer controls, cue browsing, scene audition, variation browser, and safe override model. See Parts III–XVI and XVIII–XXII. |

## 11. Key cross-volume translation rules

### 11.1 Musical motif is not the same entity as visual motif

A `Motif` in the musical ontology remains a musical object. A `VisualMotif` is a visual object or behaviour that may be derived from, associated with, or in counterpoint to one or more musical motifs. The visual motif has its own identity, parameters, lineage, and transformations.

### 11.2 Musical section is not a visual scene

A musical `Section` may contain several visual scenes, one continuous scene, or a scene that deliberately ignores the section boundary. The relationship is represented explicitly through mapping or cue data.

### 11.3 Audio features are not musical semantics

RMS, spectral flux, centroid, and band energy describe signal properties. They do not reveal motif identity, phrase function, or formal intent. If the composition system provides these semantics, visual generation SHOULD use them directly.

### 11.4 Perceptual architecture applies to both modalities, but not identically

The music perceptual manual discusses auditory grouping and attention. The visual instrument needs visual grouping and visual attention models. Similar concepts can be shared at the abstract level—foreground, background, salience, density, continuity—but their measurements and mechanisms are different.

### 11.5 The audio renderer and visual renderer share production principles, not execution code

The visual renderer has a frame clock, GPU resources, scene state, output transforms, and video surfaces. It should reuse concepts such as immutable render jobs, provenance, preflight, fallback, and reproducibility, but it is not simply an audio engine with pictures.

---

# Part III — The visual ontology

## 12. A visual composition is a connected work

A list of effects or a stack of layers is not a sufficient representation of a live visual set. The system must know which objects belong to a scene, which motifs recur, which events change them, what musical material they are related to, and what transformations are permitted.

A project should represent at least the following entities.

| Entity | Meaning |
| --- | --- |
| `VisualBrief` | Artistic intention and constraints for a visual work or concert set |
| `VisualIdentity` | Stable visual vocabulary: palette, materials, geometry, motion principles, textures, and references |
| `VisualScore` | The planned visual trajectory over musical or performance time |
| `VisualScene` | A perceptual and compositional state made from objects, layers, space, and behaviour |
| `VisualObject` | A designed visual entity with identity and properties |
| `VisualLayer` | A compositing or spatial grouping unit |
| `VisualRole` | Foreground, midground, background, accent, transition, environment, or another declared role |
| `VisualMotif` | A recognisable shape, image, gesture, transformation, or behaviour that may recur |
| `VisualPattern` | A repeatable temporal arrangement of visual events or behaviours |
| `VisualPhrase` | A perceptible visual unit with a beginning, continuation, interruption, and ending |
| `VisualCue` | A planned event or state change triggered by score, audio, time, or performer input |
| `VisualEvent` | A timed occurrence such as spawn, morph, cut, reveal, freeze, or camera change |
| `MotionGesture` | A movement description: orbit, drift, pulse, fall, rotate, fracture, assemble, dissolve, etc. |
| `VisualTransformation` | A bounded operation applied to a visual object, motif, scene, or material |
| `MappingRule` | A declared relationship from a music/audio/control source to a visual parameter or action |
| `SourceBinding` | A reference to a musical entity, audio feature, external control, or input channel |
| `FeatureStream` | A time-varying signal or semantic stream used by mapping rules |
| `SceneTransition` | A designed relationship between outgoing and incoming scene states |
| `OutputSurface` | A physical or virtual display target with geometry, resolution, colour, and transform properties |
| `OutputProfile` | A configuration for one or more surfaces and delivery interfaces |
| `LiveOverride` | A performer action with declared scope, duration, priority, and restoration behaviour |
| `SafetyProfile` | Constraints and screening settings for visual hazards and audience comfort |
| `VisualSnapshot` | A saved, reproducible visual state with generator and input provenance |
| `ShowManifest` | The full performance configuration, cues, versions, assets, surfaces, and fallback plan |

These entities SHOULD have stable identifiers and typed relationships. They can be stored in a graph, document database, relational schema, or hybrid model.

## 13. Visual identity and visual-object identity

A `VisualIdentity` describes the visual world of a project or show. It should not be a single style name such as “glitch” or “abstract”. It should define a coherent set of choices:

- geometry vocabulary;
- image-source vocabulary;
- material and texture vocabulary;
- palette and colour behaviour;
- line, edge, and surface treatment;
- camera and spatial conventions;
- motion grammar;
- compositing and degradation methods;
- typographic or symbolic rules;
- allowed contrasts and deliberate exceptions.

A `VisualObject` represents one identifiable object within that world. It may be generated from a shader, particle system, mesh, drawing, typography, sampled video, image sequence, live camera, or hybrid source.

A visual object should expose:

- source method and source asset, if any;
- geometry or image representation;
- material and texture parameters;
- position, scale, orientation, depth, and bounds;
- animation state and motion history;
- visual role and salience intention;
- source relationships and lineage;
- permitted transformations;
- lifecycle and removal policy.

## 14. The visual relationship graph

Useful relationship types include:

- `derived_from` — visual material derived from a musical motif or earlier visual object;
- `responds_to` — visual event controlled by a musical or audio event;
- `accompanies` — visual material associated with a musical region without direct control;
- `transforms` — one object or scene state becomes another;
- `foregrounds` — an object is intended to become the main visual figure;
- `backgrounds` — an object establishes the visual ground;
- `reinforces` — two visual objects or audio/visual events are coordinated;
- `contrasts_with` — elements intentionally differ in motion, material, palette, or timing;
- `prepares` — one scene anticipates a later event;
- `returns_as` — an earlier visual motif reappears in transformed form;
- `occupies` — an object belongs to a layer, plane, region, or output surface;
- `synchronised_with` — a cue is time- or phase-related to a musical event;
- `independent_of` — an object is explicitly not driven by a particular source.

The graph allows the system to know why a visual object exists, not merely where it is drawn.

## 15. Visual time-scales

Visual composition should operate across multiple scales just as musical composition does.

| Scale | Visual decisions | Example |
| --- | --- | --- |
| Frame | pixel, sample, point, vertex, local shader state | one frame of a distortion field |
| Gesture/event | spawn, flash-safe accent, rotation impulse, reveal, cut | an object appears when a motif starts |
| Pattern | repeating motion or visual cycle | a group of points rotates through seven positions |
| Phrase | visual gesture with direction and closure | scattered fragments gather and then disperse |
| Section | persistent scene identity and scene-state change | a geometric field becomes an organic environment |
| Track | visual arc, motif memory, opening, return, ending | a recurring object gradually changes its material |
| Concert set | continuity, inter-track transition, overall visual world | motifs from earlier tracks remain as traces in later scenes |

A system limited to frame-by-frame audio response is missing most of the composition.

---

# Part IV — Input architecture and musical synchronization

## 16. Three input modes and one authority hierarchy

The system should support three complementary input families:

1. **Structured music input** from the music generator or DAW/sequencer.
2. **Audio analysis input** from live or recorded audio.
3. **Performer input** from controllers, keyboard, MIDI, OSC, or a visual control surface.

When all are available, a useful authority hierarchy is:

1. Explicit performer override within its declared scope.
2. Explicit visual cue or visual-score event.
3. Structured musical event and semantic state.
4. Engine telemetry and per-voice data.
5. Audio-derived feature estimate.
6. Internal visual motion and procedural time.

This hierarchy is not absolute for every parameter. For example, live audio amplitude may be the preferred driver for a material's micro-motion, while a score-authored section transition should remain governed by the composition timeline. The system must define source priority per mapping rule.

## 17. Structured musical input

For music created by the companion generator, the ideal input is not a stereo mix alone. The music system can provide data that would be difficult or impossible to infer reliably from audio.

Useful messages include:

- composition started, paused, resumed, stopped, and completed;
- tempo-map and meter-map changes;
- bar, beat, subdivision, and cycle positions;
- section and phrase boundaries;
- motif, pattern, and voice identity;
- event onset, duration, velocity, articulation, and role;
- rhythmic relationship events such as interlock, omission, phase displacement, or return;
- density and attention intentions from the perceptual planner;
- transition plans and planned moments of silence or reduction;
- explicit visual annotations authored by the composer.

A structured event SHOULD include a persistent source ID and at least one timestamp in a declared clock domain. Where practical, it should also include musical time so that visuals can remain locked to the score when playback is paused or tempo changes.

### Example semantic event

```json
{
  "event_id": "evt_00742",
  "event_type": "motif_entry",
  "source_entity_id": "motif_metal_02",
  "composition_id": "comp_001",
  "section_id": "section_B",
  "phrase_id": "phrase_B03",
  "voice_id": "voice_percussion_metal",
  "musical_position": {
    "bar": 33,
    "beat": 1,
    "subdivision": "0/1",
    "quarter_note": "128/1"
  },
  "transport_time_seconds": 82.758,
  "duration_quarters": "4/1",
  "role": "foreground_accent",
  "intensity": 0.72,
  "seed": 19321
}
```

This event does not dictate a specific graphic. It gives the visual director a meaningful fact from which it can select, continue, transform, or ignore visual material according to the current visual score.

## 18. Audio-derived features

Audio analysis is useful when the music is external, improvised, or not fully represented by a structured score. It is also useful for fine-grained sound-reactive motion.

Potential features include:

| Feature | What it describes | Possible visual use |
| --- | --- | --- |
| RMS / short-term energy | signal level over a window | scale, opacity, deformation amplitude |
| Peak envelope | rapid amplitude excursions | transient accent or object excitation |
| Onset strength / spectral flux | change in spectral content | spawn, fracture, particle impulse |
| Low / mid / high band energy | energy within selected frequency ranges | separate material channels or spatial layers |
| Spectral centroid | spectral centre of mass | spectral spread, edge detail, perceived material shift |
| Spectral flatness | noise-like versus tonal spectrum | transition between granular and coherent textures |
| Chroma / pitch class profile | pitch-class energy estimate | pitch-field palette or harmonic-state selection |
| Fundamental-frequency estimate | probable pitch of a source | contour, orbit, or length relationships |
| Stereo width / correlation | channel relationship | lateral spread or spatial density |
| Beat and tempo estimate | inferred pulse | timing grid when no score clock exists |
| Novelty / change score | feature-space change over time | scene transition proposal or visual variation |

Audio features are estimates. Their window sizes introduce latency; their values can be unstable; and multiple sources can contaminate the analysis. Every feature stream SHOULD expose its window, hop size, smoothing, normalisation, calibration, and confidence or validity state.

### 18.1 Avoid the naïve frequency-band visualizer

A weak design maps low frequencies to scale, mid frequencies to rotation, and high frequencies to particle count, then leaves those relationships running for the entire performance. The result is technically reactive but visually monotonous.

A better design uses audio features as *modulators* within a larger compositional state. A low-band pulse may affect a sculpture only while it is foregrounded. High-band activity may alter surface detail but not the global composition. A transient may trigger a visual gesture only when the current scene permits it.

### 18.2 Normalisation and calibration

Feature values MUST be calibrated to the actual input. Do not assume that a fixed amplitude threshold works for every track or sound system.

Recommended operations include:

- DC and noise-floor handling;
- rolling percentile or adaptive-range normalisation;
- attack and release smoothing;
- hysteresis for state changes;
- outlier limiting;
- confidence gating;
- per-input calibration presets;
- separate mappings for rehearsal, soundcheck, and show conditions.

## 19. Performer input

Performer controls may include:

- scene launch and scene selection;
- visual density and visual motion energy;
- palette selection;
- foreground-object selection;
- transition mode;
- freeze, hold, or clear;
- controlled variation and seed selection;
- camera or spatial depth macro;
- texture, degradation, or feedback amount;
- manual cue trigger;
- emergency fallback or safe-output action.

A performer control must have a known scope and feedback. “More chaos” is insufficient unless the system defines which properties may become less stable and which invariants remain protected.

## 20. Clock domains

A live visual system usually has at least four clocks:

1. **Musical clock:** bars, beats, subdivisions, tempo map, phrase positions.
2. **Audio clock:** sample frames and the audio device's timebase.
3. **Performance clock:** a monotonic wall-clock used for live events and external synchronization.
4. **Render clock:** frame index, GPU presentation time, and display refresh.

These clocks MUST NOT be treated as interchangeable.

A musical event may occur at a known score position, be scheduled at an audio sample frame, be transmitted with an OSC timetag, and finally be sampled by a GPU frame. The system needs explicit conversion and late-event policies.

### 20.1 Event scheduling

- Schedule future known events rather than polling for them after they have passed.
- Interpolate continuous parameters between received updates.
- Keep event timestamps separate from the frame on which they are rendered.
- Define a maximum tolerated visual response delay per event class.
- Define what happens to late, duplicated, missing, or out-of-order messages.
- Use a monotonic clock for duration and watchdog calculations.
- When a tempo map changes, update musical-to-wall-time conversion without rewriting musical identity.

### 20.2 Frame-rate independence

Visual motion MUST be expressed in time units or delta-time-aware state updates, not as “move 2 pixels per frame”. Otherwise the same patch behaves differently at 30, 60, and 120 frames per second.

Use deterministic time steps where simulation stability requires them, and interpolate render state for display. Separate simulation update rate from presentation rate where possible.

---

# Part V — The audiovisual mapping architecture

## 21. Mapping is a compositional decision

A mapping rule should not be a hidden cable from an input channel to a shader parameter. It is a declared transformation with a purpose, scope, range, and priority.

The recommended pipeline is:

```text
Musical event / Audio feature / Performer input
                    |
                    v
              Source adapter
                    |
                    v
             Feature or event model
                    |
                    v
             Semantic mapping rule
                    |
                    v
          Visual parameter / cue proposal
                    |
                    v
              Visual director
                    |
                    v
              Scene graph state
                    |
                    v
             Renderer and outputs
```

The visual director may accept, delay, transform, combine, or ignore a proposal based on the current scene, visual brief, attention plan, safety limits, and performer overrides.

## 22. Mapping-rule contract

Every reusable mapping rule SHOULD declare:

- unique ID and version;
- source type and source entity or feature;
- event, continuous, categorical, or structural mode;
- target visual entity and parameter;
- input and output units;
- minimum and maximum values;
- transformation curve or lookup method;
- smoothing and interpolation policy;
- threshold and hysteresis if relevant;
- update rate and allowed latency;
- priority and conflict policy;
- random seed policy if stochastic;
- safety clamp;
- missing-data and stale-data behaviour;
- explanation of intended musical/visual relationship.

### Example: onset to geometry impulse

```json
{
  "mapping_id": "map_onset_fracture_01",
  "version": 1,
  "source": {
    "type": "audio_feature",
    "feature": "onset_strength",
    "channel": "full_mix"
  },
  "target": {
    "visual_object_id": "object_crystal_field",
    "parameter": "fracture_impulse"
  },
  "mode": "event_impulse",
  "input_range": [0.0, 1.0],
  "threshold": 0.68,
  "hysteresis": 0.08,
  "output_range": [0.0, 0.75],
  "curve": "ease_out_quadratic",
  "smoothing_ms": 45,
  "cooldown_ms": 90,
  "priority": 40,
  "missing_input": "hold_last_then_decay",
  "safety_limit": 0.75,
  "intent": "Use strong attacks to excite a fractured surface without making every transient a full-screen cut."
}
```

## 23. Mapping modes

### 23.1 Continuous mapping

A continuously varying feature modulates a property such as opacity, rotation speed, deformation, particle emission, or camera drift. Use smoothing, rate limits, and bounded ranges.

### 23.2 Event mapping

An event triggers an action such as spawn, reveal, cut, collapse, morph, or light-safe accent. Event mappings need duplicate protection and timing rules.

### 23.3 Structural mapping

A section, phrase, motif, or formal event selects a visual state, scene, palette, or developmental behaviour. Structural mappings should normally be score-aware.

### 23.4 Categorical mapping

A value such as `foreground`, `background`, `breakdown`, `return`, or `transition` selects a visual role or state. Categorical mappings should use explicit enums rather than fuzzy string matching.

### 23.5 Gesture mapping

An input gesture such as a knob sweep, pad press, or controller movement generates a visual action. The system should distinguish a momentary gesture from a latched state.

### 23.6 Stochastic mapping

A feature or event selects among bounded alternatives. The candidate set, probabilities, seed, and selection history should be preserved when reproducibility is requested.

## 24. Mapping musical ideas without literalism

| Musical concept | Possible visual interpretation | Literal interpretation to avoid as a default |
| --- | --- | --- |
| Stable pulse | persistent grid, oscillation, orbit, repeated camera or shape gesture | flashing the whole screen on every kick |
| Syncopation | displaced visual accent, interrupted geometry, off-grid motion | moving every object to each detected onset |
| Polymeter | independent rotating loops, layered periodic systems | random motion with no stable cycle |
| Motif | recognisable shape, gesture, contour, or transformation family | assigning one note to one fixed colour |
| Motif variation | transform one property while preserving identity | replacing the visual whenever the notes change |
| Breakdown | remove, isolate, enlarge, slow, or expose an existing visual object | automatically fade to black whenever audio gets quiet |
| Return | bring back a recognisable visual object with altered state | replay the exact same clip regardless of context |
| Noise / texture | granular fields, irregular material, particle or surface instability | adding generic static to every noisy frequency band |
| Harmonic stasis | sustained geometry, stable colour field, slow internal mutation | freezing the entire image indefinitely |
| Transition | visual preparation, transformation, interruption, or scene migration | a generic crossfade at every bar boundary |

A mapping is successful when it preserves the *relationship* rather than copying the surface form.

## 25. Avoid mapping conflicts

Several rules may target the same visual parameter. The system must define whether they combine, override, or remain mutually exclusive.

Recommended precedence:

1. hard safety limit;
2. explicit performer override;
3. committed visual cue;
4. section/phrase director state;
5. musical semantic mapping;
6. audio-reactive modulation;
7. internal procedural modulation.

For additive or multiplicative combinations, define the operation explicitly and clamp its result. Never let two uncoordinated controllers fight over the same parameter every frame.

---

# Part VI — Visual composition: motifs, patterns, phrases, and forms

## 26. Write a visual proposition

Before selecting effects or algorithms, describe the visual work in one or two sentences. A proposition should establish material, motion, attention, and developmental direction.

Examples:

- “A sparse field of mechanical marks gradually reveals that its irregular movements are fragments of one hidden rotating system.”
- “One soft organic volume survives while geometric structures around it fracture, disappear, and return in altered form.”
- “A typographic and diagrammatic world changes from precise notation to unstable spatial architecture, then reconstructs itself from traces.”
- “A single object remains recognisable while its material, scale, depth, and relationship to the frame evolve across the performance.”

A proposition is not a storyboard. It is a principle that can guide multiple scenes and generative alternatives.

## 27. Build a small visual vocabulary

A useful first version of a visual identity can be built from:

- three principal visual materials;
- two or three geometric or image-source families;
- one primary motion grammar;
- one secondary motion grammar;
- one palette with deliberate exceptions;
- one spatial convention;
- one treatment of transitions;
- one or two recurring visual motifs.

This is not a limit on variety. It is a way to establish visual identity before expanding it.

## 28. Visual motif families

A `VisualMotif` should be recognisable through one or more stable properties. Examples:

1. **Contour motif:** a distinctive outline, path, or silhouette.
2. **Motion motif:** an orbit, fall, drift, tremor, fold, or acceleration pattern.
3. **Spatial motif:** an object that repeatedly appears at a particular depth or region.
4. **Texture motif:** a grain, scan, noise, line, or material signature.
5. **Typographic motif:** recurring fragments, alignment, spacing, or text behaviour.
6. **Colour motif:** a restrained palette relationship or colour transition.
7. **Framing motif:** a repeated crop, border, window, or compositional enclosure.
8. **Transformation motif:** a recurring sequence such as split → rotate → reassemble.
9. **Absence motif:** a stable empty area, missing object, or deliberately blank field.
10. **Composite motif:** an identity made from multiple layers that may separate and reunite.

### 28.1 Motif identity test

A motif remains recognisable if the system can change one or two properties while preserving a core subset. Store the invariants and allowed variations explicitly. For example, a shape may retain its contour family and movement direction while its colour, scale, particle density, and surface material vary.

## 29. Visual pattern families

Visual patterns are repeatable behaviours, not merely loops of frames.

| Pattern family | Behaviour | Musical analogy |
| --- | --- | --- |
| Pulse field | repeated expansion, contraction, or illumination-safe emphasis | stable pulse |
| Displaced accent | one visual impulse occurs off the main cycle | syncopation |
| Rotating cycle | a system changes position over a periodic path | rotating/odd-length rhythm |
| Unequal-cycle interlock | several periodic visual systems overlap | polymetric interlock |
| Phase drift | duplicate patterns slowly move out of alignment | phase displacement |
| Omission | a normally recurring element disappears | omission pattern |
| Burst | short cluster of actions separated by quiet spans | irregular burst |
| Sparse punctuation | isolated object or gesture appears in a mostly static image | sparse accent |
| Density cloud | many small elements form a collective texture | dense percussion cloud |
| Call and response | separate visual groups alternate gestures | rhythmic dialogue |
| Unison/fusion | multiple objects align and behave as one | reinforcement/unison |
| Counter-motion | one layer moves against the dominant motion | counter-accent/counterpoint |
| Hierarchical motion | a slow parent cycle contains faster child cycles | pulse and subdivision |
| Accumulation | objects or detail are added over time | progressive accumulation |
| Erosion | objects, edges, or detail are removed | subtractive form |
| Fracture and repair | coherent form breaks into pieces, then reconnects | break/edit and motif transformation |
| Scan / traverse | a visual process moves systematically across the field | linear rhythmic traversal |
| Memory echo | earlier positions or forms remain as traces | delay/repetition and motif memory |
| Stutter / hold | a motion segment is repeated or frozen | ratchet / repeated fill |
| Morphing cycle | an object passes through a recurring transformation path | transformed ostinato |

Do not implement every pattern family as a separate hard-coded effect. Many can be represented as reusable motion grammars and event schedules.

## 30. Visual phrase functions

A visual phrase should have a perceptible direction. Useful functions include:

- **Establish:** reveal an object, material, or rule.
- **Continue:** preserve an identity while allowing internal motion.
- **Develop:** alter a meaningful property or relationship.
- **Answer:** introduce a related but distinct visual gesture.
- **Interrupt:** stop, cut, obscure, or displace an established behaviour.
- **Accumulate:** add elements, layers, or detail.
- **Reduce:** remove elements or motion to expose the remaining structure.
- **Reveal:** show an underlying arrangement or previously hidden layer.
- **Transform:** change the material or organisation of an existing object.
- **Return:** reactivate a remembered motif.
- **Close:** complete, suspend, dissolve, or deliberately leave a process unresolved.

A visual phrase need not match the musical phrase length. It may begin before a musical phrase, cross several musical phrases, or deliberately resist the musical segmentation. Its relation should be authored or generated according to a declared rule.

## 31. Visual form across a complete track

The Composition Atlas defines formal models such as progressive accumulation, subtractive erosion, stable anchor with changing surface, rotating-cycle form, fragment-to-whole, call-and-response, episodic mosaic, false return, long plateau, multi-movement form, and cyclic return with altered memory.

Each has a useful visual analogue:

| Musical formal model | Visual formal strategy |
| --- | --- |
| Progressive accumulation | Add objects, visual streams, detail, or spatial depth while preserving a recognisable anchor |
| Subtractive erosion | Remove layers, edges, texture, colour, or motion until a reduced visual identity remains |
| Stable anchor, changing surface | Keep one object, grid, or spatial rule stable while changing its material and behaviour |
| Repeated motif, changing rhythm | Preserve visual shape identity but alter recurrence, duration, accent, or motion timing |
| Repeated rhythm, changing pitch world | Preserve visual timing while changing geometry, palette, material, or spatial organisation |
| A/B contrast with transformed return | Use distinct scene families, then restore the first with a changed property |
| Rotating-cycle form | Several visual cycles gradually re-align or diverge |
| Fragment-to-whole | Begin with isolated visual pieces and reveal their larger structure |
| One motif, many identities | Re-realise one visual motif as geometry, typography, particles, image, or 3D object |
| Call-and-response form | Alternate visual groups, surfaces, or compositional regions |
| Episodic mosaic | Use self-contained visual episodes connected by a recurring identity or transition motif |
| False return | Bring back a familiar scene cue but with a missing, altered, or displaced element |
| Long plateau with internal change | Maintain a stable composition while small transformations accumulate |
| Multi-movement / suite | Give movements distinct visual worlds while preserving a set-wide identity |
| Pulse transformation | Change the dominant motion rate, cycle, or visual subdivision |
| Breakdown as revelation | Remove active layers and expose a hidden object or process |
| Fixed process path | Follow an authored visual procedure, with controlled local variation |
| Cyclic return with altered memory | Return to a prior visual motif carrying traces of previous sections |

These are strategies, not presets. One musical form may support many visual forms, and a visual composition may have its own formal arc.

## 32. Build a visual score

A `VisualScore` is a plan for the visual development of a track or set. It can be fully authored, generated, partially authored, or adapted live.

For each musical section, specify:

- current visual identity and scene family;
- primary visual object or motif;
- foreground/midground/background roles;
- movement and density intention;
- relation to musical motifs and patterns;
- palette or material state;
- transition into the section;
- transition out of the section;
- allowed generation operations;
- protected visual material;
- performer intervention points;
- safety and output constraints.

### Visual-score worksheet

```text
TRACK / MOVEMENT:
VISUAL PROPOSITION:
VISUAL IDENTITY:

SECTION:
MUSICAL FUNCTION:
VISUAL FUNCTION:
PRIMARY MOTIF:
SECONDARY MATERIAL:
FOREGROUND:
MIDGROUND:
BACKGROUND:
MOTION GRAMMAR:
DENSITY / DETAIL:
PALETTE / MATERIAL:
MUSIC-TO-VISUAL RELATION:
TRANSITION IN:
TRANSITION OUT:
ALLOWED MUTATIONS:
PROTECTED ELEMENTS:
LIVE CONTROL POINTS:
SAFETY NOTES:
```

---

# Part VII — Visual material, generators, and hybrid systems

## 33. Visual material families

The system should support several families of visual material. They can be combined, but each family has different strengths and computational costs.

### 33.1 Geometric and diagrammatic systems

Lines, grids, curves, polygons, axes, diagrams, lattices, recursive subdivisions, coordinate systems, and geometric constructions.

Useful for:

- rhythmic regularity and displacement;
- pattern interlock and phase;
- precise movement and visual counterpoint;
- technical, editorial, or machine-like visual identities;
- stable anchors with evolving details.

Potential algorithms:

- parametric curves;
- procedural meshes;
- subdivision and tessellation;
- Voronoi and Delaunay structures;
- graph drawing;
- geometric transformations;
- instanced geometry.

### 33.2 Particle and point systems

Particles can represent accents, fragments, populations, trails, dust, sparks, swarms, or abstract masses.

Useful for:

- accumulation and erosion;
- note/event density;
- motif fragmentation;
- flow and turbulence;
- source-to-target assembly;
- interaction between independent cycles.

A particle system needs explicit lifecycle rules: birth, age, motion, interaction, material, boundary, decay, and maximum count. Unbounded particle accumulation is a performance and compositional defect.

### 33.3 Raster, texture, and image-processing systems

Procedural textures, gradients, scanlines, displacement, blur, thresholding, feedback buffers, masks, image transforms, and image compositing.

Useful for:

- material identity;
- visual memory and temporal echoes;
- degradation, erosion, smearing, and feedback;
- transitions between clean and damaged states;
- hybrid combinations of sampled and procedural imagery.

### 33.4 Typography and symbolic systems

Text can be a visual object rather than a caption. Letterforms, fragments, glyphs, symbols, numbers, and abstract notation can be animated, rearranged, distorted, repeated, or spatialised.

Typography should be intentional. If text is not meant to be read, it can be treated as a material; if it is meant to be read, size, contrast, duration, language, and viewing distance become part of the design.

### 33.5 Organic and fluid systems

Flow fields, curl noise, reaction-diffusion, cellular patterns, soft bodies, fluid-like warping, branching, growth, and biological forms.

Useful for:

- slow transformation;
- continuous visual environments;
- growth and decay;
- motion that contrasts with rigid rhythmic structures;
- visualising long-term energy or density without literal beat flashes.

### 33.6 Three-dimensional and spatial systems

Meshes, volumes, point clouds, camera systems, lighting, depth, projection, and spatial transformations.

Useful for:

- depth and scale;
- movement through a virtual environment;
- recurring objects viewed from changing angles;
- large-scale visual forms;
- mapping to physical stage geometry.

### 33.7 Sampled and recorded imagery

Field recordings, camera feeds, archival material, macro photography, scanned objects, video fragments, and image sequences can be treated as source materials.

They may remain recognisable, become abstract, be fragmented, or be re-synthesised into new procedural material. The Sound Design Manual's distinction between source-preserving, source-obscuring, and source-erasing transformation has a useful visual analogue.

### 33.8 Hybrid visual systems

A hybrid object may combine:

- a scanned or photographed source;
- procedural geometry;
- particles generated from image edges;
- a shader-based deformation;
- feedback trails;
- 3D depth and camera motion;
- typography or symbolic marks.

The layers should contribute to one identity. A hybrid object is not automatically coherent just because multiple techniques are present.

## 34. Motion grammar

Motion is one of the main compositional materials of live visuals. Define motion as a reusable gesture with parameters and identity.

Common gesture families:

- pulse / expand / contract;
- drift / float / hover;
- orbit / rotate / precess;
- translate / scan / traverse;
- fall / rise / cascade;
- fold / unfold;
- split / fracture / scatter;
- gather / assemble / align;
- stretch / compress;
- wobble / tremor / oscillate;
- grow / branch / bloom;
- dissolve / evaporate / erode;
- smear / trail / echo;
- reveal / conceal / mask;
- zoom / dolly / track / pan;
- freeze / hold / resume.

Each gesture should define:

- initial state;
- target state or path;
- duration or cycle;
- easing and velocity profile;
- spatial bounds;
- reversibility;
- interruption behaviour;
- combination rules;
- maximum acceleration or displacement where comfort matters.

### 34.1 Motion should not be permanently tied to amplitude

A visual object may be excited by audio energy but continue its own movement after the transient. It may slow during a musical breakdown, or move faster while the overall audio level falls. The visual director should be able to control the gesture envelope independently from the signal envelope.

## 35. Colour and visual material

Colour is a compositional parameter, not a universal decoder of musical meaning.

The system may support:

- fixed palettes;
- section palettes;
- palette families associated with motifs;
- gradual palette transformation;
- temperature and saturation relationships;
- contrast and luminance roles;
- monochrome or limited-colour modes;
- controlled exceptions for emphasis.

Do not assume a universal mapping such as low frequencies = red or minor harmony = blue. Such associations can be authored by the artist, but they are not universal perceptual laws. Store them as project-specific mappings.

A palette should define more than RGB swatches. It should describe foreground/background contrast, luminance range, accent use, saturation, transparency, and the conditions under which colours may change.

## 36. Visual effects as transformations

Effects should be represented as meaningful transformations rather than as a random chain of filters.

Examples:

- displacement changes spatial identity;
- blur changes edge definition and attention;
- feedback creates temporal memory;
- posterisation changes tonal structure;
- thresholding changes image segmentation;
- colour remapping changes material identity;
- pixelation changes spatial resolution and texture;
- masking changes visibility and figure-ground relation;
- temporal echo preserves traces of earlier motion;
- warping changes shape and continuity;
- compositing fuses or separates visual objects.

Every effect should declare its input, output, parameter ranges, statefulness, memory use, latency, and reset behaviour. Stateful feedback systems need bounded buffers and a defined response to scene changes.

---

# Part VIII — Perceptual orchestration for the visual scene

## 37. A screen is not a scene

One output surface may contain several perceived objects, and multiple output surfaces may form one perceived scene. The visual engine should describe the intended scene independently from the number of tracks, layers, or windows in the rendering graph.

A visual scene can contain:

- a foreground figure;
- midground objects with independent movement;
- background texture or spatial environment;
- accent events;
- recurring motifs;
- visual gaps and negative space;
- a frame, mask, border, or compositional enclosure;
- a controlled region of ambiguity.

## 38. Figure, ground, and visual attention

The Perceptual Orchestration manual establishes the importance of figure-ground relationships, grouping, salience, and attention for music. The visual instrument should create a visual equivalent without assuming that auditory and visual perception operate identically.

At any moment, define:

- **Foreground:** the visual object the audience should most readily notice.
- **Midground:** supporting forms that contribute movement and context.
- **Background:** the visual field that establishes space, material, or atmosphere.
- **Accent:** a temporary visual event.
- **Latent material:** an object or motif that remains present but inactive, dimmed, occluded, or outside the main attention region.

Roles may change over time. A background object can become the foreground after the rest of the scene is removed. A small repeated mark may become the primary figure after a large object disappears.

## 39. Visual salience

Visual salience is influenced by several properties:

- luminance and contrast;
- colour contrast and saturation;
- size and occupied area;
- spatial location;
- motion speed, direction, and acceleration;
- edge density and detail;
- temporal novelty;
- isolation and negative space;
- repetition and learned expectation;
- competition from other elements.

No single formula can reliably predict attention for every audience, viewing distance, screen, and context. The software can estimate competing salience and expose its assumptions, but human review remains necessary.

### 39.1 Salience budget

A practical scene can assign a limited number of high-salience roles:

- one primary figure;
- zero to two secondary figures;
- a restrained number of accent events;
- one or more background systems.

This is a design heuristic, not a strict rule. A deliberate swarm or visual overload can be a valid composition, but it should be treated as an intentional scene state.

## 40. Visual density and perceptual load

Track these dimensions separately:

- object count;
- edge density;
- texture density;
- spatial frequency distribution;
- motion density;
- event density;
- colour and luminance contrast;
- scene-transition rate;
- text or symbol information density;
- visual salience competition.

A scene with 100 slow, faint points may feel sparse. A scene with one rapidly changing high-contrast object may feel dense. The director should not use particle count as a substitute for visual load.

## 41. Visual grouping and stream formation

Objects may be perceived as one group when they share:

- motion direction or timing;
- shape or material;
- colour and luminance;
- spatial proximity;
- common transformation;
- a shared boundary or container;
- repeated temporal relationships.

To fuse several objects into one visual entity, synchronise one or more of these properties. To separate them, create meaningful differences in motion, location, colour, scale, or timing.

## 42. Negative space and stillness

Negative space is not wasted output. It gives the audience a stable reference, provides room for a later gesture, and can make a small change more consequential.

The engine SHOULD support:

- static holds;
- near-black or low-luminance scenes;
- one-object scenes;
- isolated foreground movement;
- large unoccupied regions;
- transitions that reveal rather than add;
- a complete pause in visual activity without losing the underlying scene state.

## 43. Spatial depth and physical surfaces

For a single screen, depth may be conveyed through scale, occlusion, blur, parallax, shading, and movement. For multiple screens or projection surfaces, the scene may be distributed physically.

Represent:

- logical scene coordinates;
- physical output coordinates;
- camera and view transforms;
- surface geometry and warp maps;
- overlap regions and edge blends;
- per-surface safe regions;
- brightness and colour calibration metadata.

The logical composition should not depend on one particular projector resolution. Output adaptation belongs to the surface/output layer.

---

# Part IX — Scene architecture, transitions, and live visual form

## 44. Scene as a stateful composition

A `VisualScene` should include:

- scene identity and role;
- active visual objects and layers;
- scene graph or composition tree;
- spatial environment and camera;
- mapping rules and active input bindings;
- visual score position;
- current salience plan;
- motion and simulation state;
- safety constraints;
- transition eligibility;
- fallback scene or recovery state.

A scene is not just a preset. It is a persistent state that can evolve, be interrupted, or be resumed.

## 45. Scene state machine

A useful scene lifecycle is:

```text
INACTIVE
   |
   v
PREPARED -> ENTERING -> ACTIVE -> EXITING
                ^         |          |
                |         v          v
             RESUME <- HELD       ARCHIVED
                          
Any state -> SAFE_FALLBACK (on critical failure)
```

The actual implementation may have more states. The important requirement is that scene transitions are explicit, cancellable where appropriate, and recoverable.

## 46. Transition families

1. **Cut:** immediate replacement. Useful for deliberate rupture, not as a default.
2. **Dissolve:** gradual blend between scene states.
3. **Morph:** transform an existing object or composition into another.
4. **Assembly:** fragments combine into the new scene.
5. **Erosion:** the outgoing scene loses detail until the next scene is revealed.
6. **Mask reveal:** a new scene appears through a moving or expanding region.
7. **Displacement transition:** one image or geometry pushes, warps, or displaces another.
8. **Camera transition:** move through, around, or away from a scene object.
9. **Palette transition:** retain geometry while changing material and colour identity.
10. **Attention transfer:** one object becomes less salient while another becomes the figure.
11. **Temporal echo:** the outgoing scene persists as a trace within the incoming scene.
12. **Negative transition:** remove activity and allow a deliberate visual pause before re-entry.
13. **Split / merge:** one scene divides into several regions or multiple regions converge.
14. **Hard reset:** deliberately clear procedural state and begin a new visual world.

Every transition should declare duration, trigger, easing, preserved objects, discarded objects, interruption policy, and whether the outgoing scene remains available for a return.

## 47. Transition design in three stages

A useful transition often has:

1. **Preparation:** introduce a cue, alter focus, or reveal an instability in the current scene.
2. **Transformation:** change the current material, state, space, or relationship.
3. **Establishment:** allow the new visual identity to become legible.

Not every transition needs all three stages. A deliberate cut may be the correct form. But the decision should be musical and visual, not accidental.

## 48. Multi-track concert continuity

The visual system should support a concert set as a larger form than the individual tracks.

Possible continuity strategies:

- a visual motif persists between songs;
- one palette family changes gradually across the set;
- the end of one track becomes the opening state of the next;
- each track has a separate visual world but shares a framing or motion rule;
- a live camera or stage object remains constant while generated environments change;
- earlier motifs return later with altered material;
- the set has a visual prologue, interlude, and final state.

Do not automatically reset every visual system at every track boundary. Decide whether the visual memory should continue, freeze, clear, or transform.

---

# Part X — Generative algorithms and the visual director

## 49. Algorithm families

The visual engine should use multiple algorithm families, each assigned to an appropriate visual problem.

| Algorithm family | Suitable visual responsibilities | Common risk |
| --- | --- | --- |
| Rule-based systems | exact cue behaviour, deterministic scene states, safety limits | brittle if rules become an unmaintainable list |
| Finite-state machines | scene lifecycle, transitions, performance modes | state explosion if all details are encoded as states |
| Grammars / rewriting systems | motif families, recursive geometry, visual phrase structures | output may become formally repetitive |
| Parametric geometry | curves, meshes, grids, repeated structures | mathematically precise but visually sterile |
| Particle systems | fragmentation, accumulation, trails, fields | unbounded counts and generic “busy” imagery |
| Cellular automata | local interaction, emergence, texture growth | difficult to guide at large formal scales |
| L-systems | branching, growth, recursive structures | familiar organic patterns can become cliché |
| Noise and flow fields | drift, turbulence, organic motion, surface deformation | too much noise removes identity and legibility |
| Reaction-diffusion | organic pattern formation and texture | high computation and difficult visual control |
| Feedback systems | temporal memory, trails, recursive image evolution | uncontrolled accumulation, brightness, or instability |
| Attractors and dynamical systems | evolving trajectories and complex repeatable motion | chaotic behaviour can become unbounded or unperformable |
| Procedural typography | text fragments, glyph fields, spatial language | poor readability if intended text is too small or fast |
| Image analysis | derive geometry or particles from sampled imagery | dependency on source quality and preprocessing |
| Search / evolutionary methods | explore visual candidates under a visual brief | optimisation can overfit numerical proxies |
| Learned models | source transformation, semantic image generation, style-conditioned output | unpredictable latency, licensing, consistency, and control |

## 50. Assign algorithms by responsibility

Do not build one universal visual algorithm that controls every layer. Separate:

- visual-score planner;
- scene selector/director;
- motif and object generators;
- motion systems;
- mapping engine;
- transition planner;
- compositor;
- output renderer;
- performance controller;
- safety analyser.

A procedural generator proposes visual material. The visual director decides where and when it belongs. The performer can accept or override a bounded decision.

## 51. Hierarchical visual direction

The director should work at several levels:

1. **Show director:** manages continuity across the concert set.
2. **Track director:** interprets the musical arc of one piece.
3. **Section director:** selects and develops a scene state.
4. **Phrase director:** manages visual gestures and transitions.
5. **Object director:** controls motif-specific behaviour.
6. **Event renderer:** executes frame-level and event-level changes.

A lower level MUST NOT silently invalidate a higher-level constraint. For example, an object generator should not exceed a show-wide safety limit or replace a protected visual motif without permission.

## 52. Candidate generation and visual selection

When the system explores alternatives:

1. Interpret the visual intention.
2. Generate a bounded set of candidates.
3. Validate resource, safety, identity, and output constraints.
4. Estimate visual role, density, contrast, continuity, and relation to the music.
5. Compare alternatives.
6. Expose them for performer/composer review where appropriate.
7. Commit the chosen candidate or retain it as a temporary live state.

A candidate should be a proposal, not an irreversible state change. Preserve seed, generator version, parameters, source assets, and mapping state for reproducibility.

## 53. Deterministic and stochastic visual behaviour

The system should support:

- deterministic replay;
- seeded variation;
- constrained random choices;
- continuous stochastic motion within bounds;
- unseeded exploratory behaviour when explicitly desired.

Separate random streams by subsystem or object. A new particle emitter should not change the random sequence of a motif generator unless that dependency is intentional. This prevents small implementation changes from completely altering a show.

## 54. Explainable visual decisions

The system should be able to provide short, inspectable explanations such as:

- “The scene changed because the composition entered the breakdown section.”
- “The metallic motif returned; its contour is preserved while its motion cycle is phase-shifted.”
- “The foreground layer was reduced to expose the background object.”
- “Audio analysis proposed an accent, but the current scene's cooldown prevented a second event.”
- “The performer override is holding the palette; automatic palette changes are temporarily suspended.”

Explanations should reflect real decision records, not be invented after the fact.

---

# Part XI — Live performance and composer/performer agency

## 55. Live visuals are an instrument

The performer needs more than a collection of effect sliders. The live interface should expose meaningful actions and safe control over the visual score.

The system should support at least four modes:

1. **Score mode:** the visual score drives scene and cue progression automatically.
2. **Generative mode:** the system explores bounded variations within the current visual identity.
3. **Performance mode:** the operator triggers scenes, transitions, freezes, and semantic macros.
4. **Hybrid mode:** score progression remains active while the performer can intervene at any time.

The hybrid mode is generally the most expressive target, but all modes should be available for rehearsal and debugging.

## 56. Performer controls should express visual consequences

Recommended semantic macros:

| Control | Intended consequence | Must not secretly do |
| --- | --- | --- |
| Visual Density | change object count, texture, or information load within declared bounds | change every parameter randomly |
| Motion Energy | alter motion amplitude, rate, and acceleration envelope | increase unsafe flashing or camera motion without limit |
| Fragmentation | split, scatter, or break visual objects | discard motif identity without permission |
| Coherence | increase grouping, alignment, or shared movement | erase all contrast |
| Depth | alter spatial layering and camera perspective | change output geometry or projector calibration |
| Material | move between selected texture/synthesis states | load arbitrary heavy assets during performance |
| Palette | select or interpolate a known palette | violate safety or contrast requirements |
| Focus | select the primary visual figure | hide protected information or the performance state |
| Memory | increase/decrease trails or retained image history | allow unlimited feedback accumulation |
| Variation | enable bounded alternative forms | replace committed scenes destructively |
| Freeze / Hold | preserve a defined scene state | block the render loop or stop safety monitoring |
| Scene Launch | request a prepared scene or cue | bypass preflight and resource checks |

Every macro should show its active range and affected objects or layers. Multiple macros should not create hidden coupling.

## 57. Manual override model

A `LiveOverride` should declare:

- ID and performer/source;
- target scene/object/parameter/cue;
- override value or gesture;
- priority;
- start time and duration;
- latch or momentary behaviour;
- restoration rule;
- conflict policy;
- cancellation method.

Example: a performer may hold the current visual scene for 16 musical beats while the music continues. The visual director should remember the missed cues and follow an explicit policy: skip, queue, merge, or re-enter at the next safe transition. It should not unexpectedly execute a backlog of every missed visual event.

## 58. Rehearsal, soundcheck, and show modes

The application should distinguish:

- **Authoring:** visual design, scene editing, mapping, and score construction.
- **Rehearsal:** full playback with logs, overlays, and performance controls.
- **Soundcheck:** input calibration, output alignment, display calibration, and signal verification.
- **Show:** minimal interface, preloaded assets, safety limits, stable output, and no unreviewed diagnostics.
- **Recovery:** safe fallback and diagnostics after a failure.

The public output should never show a debug window, shader compilation warning, missing texture placeholder, or unapproved UI panel.

## 59. Emergency and fallback controls

Provide clearly separated actions for:

- pause visual generation;
- hold current safe frame;
- switch to a prepared fallback scene;
- fade to a safe neutral state;
- reset a faulty generator;
- reload a prepared scene;
- disable a source or output;
- restore normal score following.

An emergency control MUST have predictable behaviour and should not depend on the system successfully completing a complex animation first.

---

# Part XII — Software architecture and rendering pipeline

## 60. Reference architecture

A practical implementation can be organised as follows:

```text
                 MUSIC / PERFORMANCE SOURCES
          +----------------+-------------------+
          |                |                   |
    Structured score   Audio input        Performer input
          |                |                   |
          v                v                   v
     Music adapter    Audio analyser     Control adapter
          |                |                   |
          +----------------+-------------------+
                           |
                           v
                    TIMING & EVENT BUS
                           |
                           v
                   FEATURE / SEMANTIC BUS
                           |
                           v
                    VISUAL MAPPING ENGINE
                           |
                           v
                    VISUAL SCORE DIRECTOR
                           |
               +-----------+------------+
               |                        |
               v                        v
        Scene / cue planner       Safety / constraints
               |                        |
               +-----------+------------+
                           |
                           v
                     SCENE GRAPH
                           |
                           v
                 GENERATORS / SHADERS
                           |
                           v
                     COMPOSITOR
                           |
                           v
                    OUTPUT MANAGER
               +-----------+------------+
               |            |            |
             HDMI/DP       Spout/NDI   Lighting bridge
               |            |            |
               +------------+------------+
                           |
                           v
                  TELEMETRY / RECORDING
```

The architecture is logical, not a mandate for separate processes. A small application may combine several modules. The responsibilities should nevertheless remain explicit.

## 61. Module responsibilities

### 61.1 Music adapter

Consumes structured events, score positions, tempo/meter maps, section and phrase IDs, motif/pattern IDs, and perceptual intentions. Converts them into the visual engine's canonical input schema without changing musical identity.

### 61.2 Audio analyser

Consumes live or recorded audio and produces calibrated feature streams. It SHOULD support selectable analysis windows and report latency/confidence. It MUST NOT pretend to identify exact musical semantics unless a model has produced a labelled estimate with uncertainty.

### 61.3 Timing and event bus

Normalises timestamps, queues future events, handles late/duplicate/out-of-order messages, and distributes data to the mapping and visual director. The bus should be bounded and observable.

### 61.4 Mapping engine

Applies declared mapping rules, curves, smoothing, hysteresis, limits, and conflict policy. It outputs proposals and control streams rather than drawing directly.

### 61.5 Visual score director

Owns show, track, section, and phrase visual state. Selects scenes and visual operations, manages continuity, respects performer override, and determines transitions.

### 61.6 Scene graph

Stores active visual objects, layers, transformations, camera, materials, spatial relationships, and state. It should support efficient updates and stable object identity.

### 61.7 Generator and shader layer

Creates and transforms visual material. Expensive resources should be prepared or precompiled before they are needed in the show.

### 61.8 Compositor

Combines layers and renders a logical frame. It should support alpha, masks, blend modes, colour management, output transforms, and per-surface composition where required.

### 61.9 Output manager

Manages display devices, fullscreen windows, texture sharing, network video, mapping transforms, refresh and frame presentation. It reports output loss and recovery.

### 61.10 Telemetry and recording

Records frame time, dropped frames, GPU and memory use, input delay, event lateness, scene changes, safety interventions, and show-state snapshots. Logs must not block rendering.

## 62. Renderer technology choices

The manual does not prescribe one stack. Common implementation strategies include:

| Strategy | Strengths | Trade-offs |
| --- | --- | --- |
| Node-based real-time environment (e.g. TouchDesigner) | fast visual prototyping, dataflow, audio/MIDI/OSC integration, live output tools | application-specific project format, licensing/deployment constraints, less control over custom architecture |
| Custom C++/GPU engine | control of timing, resource lifetime, shader pipeline, output, performance | larger engineering cost, more responsibility for editor and workflow |
| Python orchestration + GPU renderer | rapid algorithm development, accessible tooling, clear separation between high-level control and GPU work | Python should not become the per-pixel renderer or an unbounded real-time callback path |
| WebGPU-based renderer | modern GPU abstraction and web deployment potential | ecosystem and platform support must be validated for the deployment target; specification maturity and implementation support can change |
| Hybrid application | use a mature visual environment for routing/output and custom modules for domain-specific generation | integration complexity, data contracts, clock synchronisation, and failure boundaries need care |

For a Windows workstation with a discrete NVIDIA GPU, a practical prototype may use Python or a native application for orchestration and a GPU-centric renderer for high-resolution image work. If the target machine is similar to the previously discussed RTX 4060 environment, design quality tiers and resolution scaling rather than assuming every scene can run at full native resolution indefinitely.

### 62.1 GPU responsibilities

Good GPU tasks include:

- full-screen shader transformations;
- particle and point rendering;
- instanced geometry;
- texture feedback and compositing;
- image-space effects;
- compute-based simulation where appropriate;
- multi-resolution and multi-pass rendering.

CPU responsibilities commonly include:

- score interpretation;
- event scheduling;
- mapping rules;
- scene-state decisions;
- file and asset management;
- UI and performer control;
- logging and diagnostics.

Do not transfer every event to the GPU or every pixel calculation to Python. Choose the execution domain according to data volume, update frequency, and latency needs.

## 63. Frame budget and adaptive quality

At 60 frames per second the nominal frame interval is about 16.67 ms; at 30 frames per second it is about 33.33 ms. The renderer must fit CPU submission, GPU execution, compositing, and presentation within the actual display pipeline budget.

Track:

- CPU frame preparation time;
- GPU frame time;
- render queue depth;
- presentation interval;
- dropped or late frames;
- memory and texture residency;
- generator simulation time;
- event-to-visible-response latency.

Use a tiered quality model:

- **High:** full resolution, full particle count, expensive shader passes, high-quality antialiasing.
- **Balanced:** target output resolution with bounded effects and moderate simulation counts.
- **Performance:** reduced internal resolution, fewer particles, lower-cost effects, simpler geometry.
- **Fallback:** known-safe scene with low CPU/GPU load.

Quality changes should preserve composition semantics. Reducing quality must not unexpectedly change the scene identity or timing of cues.

## 64. Asset and shader lifecycle

- Preload assets required by the next scene.
- Compile shaders before show time or during an explicit preparation state.
- Warm up render passes and caches.
- Define missing-asset fallbacks.
- Bound texture and buffer memory.
- Dispose of GPU resources on the correct thread/context.
- Avoid synchronous disk access during critical rendering.
- Save the last valid scene state before risky reloads.

## 65. Output interfaces and protocols

Use each protocol for the kind of data it is designed to transport.

| Interface | Suitable role | Notes |
| --- | --- | --- |
| HDMI / DisplayPort | direct local video output | usually the simplest path to a projector or LED processor input |
| Spout (Windows) | GPU texture sharing between local applications | useful when the visual engine feeds another VJ, streaming, or compositing application |
| NDI | network video transport between compatible systems | useful for remote or networked video routing; test bandwidth, latency, and network reliability |
| OSC | semantic events, parameters, cues, timing, and application control | appropriate for rich visual control messages; define namespaces and timestamp policy |
| MIDI 1.0 / MIDI 2.0 | performance gestures, note/event triggers, macro control | useful for controller integration; not a substitute for a full visual scene graph |
| Art-Net / sACN | lighting-fixture control via DMX-style data over Ethernet | lighting control is related to the show but is not the same as high-resolution video output |
| LTC / timecode integrations | synchronisation with external playback and show systems | use when the performance architecture requires an external time reference |

A project should not use lighting protocols as a replacement for full-frame video transport. Conversely, it should not use NDI or texture-sharing protocols to control individual lighting fixtures.

---

# Part XIII — Output surfaces, projection, and stage integration

## 66. Output surfaces are first-class entities

A show can use one projector, a wide LED wall, several independent screens, projection mapping, or a mixture. Each surface should be represented with:

- unique ID;
- physical or logical dimensions;
- resolution and refresh capabilities;
- orientation and aspect ratio;
- pixel aspect ratio if applicable;
- colour and luminance metadata;
- input/output interface;
- calibration transform;
- safe region;
- edge blend or overlap data;
- fallback profile.

The visual score should refer to logical scene space. Surface-specific rendering transforms adapt the composition to the physical venue.

## 67. Projection and LED considerations

### 67.1 Projectors

Consider:

- native resolution and scaling;
- lens, throw, focus, and geometric distortion;
- black floor and ambient light;
- contrast and peak brightness;
- surface colour and texture;
- keystone and warp correction;
- edge blending for multiple projectors;
- content safe areas around physical obstacles.

### 67.2 LED walls

Consider:

- actual pixel dimensions and pixel pitch;
- processor scaling and refresh behaviour;
- panel colour calibration;
- black levels and low-brightness detail;
- moiré and fine-pattern aliasing;
- scan behaviour and camera interaction if the show is filmed;
- safe regions around seams and structural gaps.

### 67.3 Multiple surfaces

Surfaces may form one panoramic image or separate visual channels. The system should support both:

- one shared scene rendered through several viewports;
- independent scenes with shared timing;
- a master visual scene with per-surface layers;
- screen-to-screen call and response;
- spatial movement that crosses surfaces;
- intentionally disconnected images.

Do not assume all surfaces have identical aspect ratios, refresh rates, brightness, or colour response.

## 68. Visual layout and legibility

For each venue/output profile, preview:

- crop and overscan;
- projection distortion;
- image scaling;
- safe margins;
- minimum line width;
- detail visibility at audience distance;
- text readability where relevant;
- brightness and dark detail;
- colour behaviour after output conversion.

A visual detail that exists at the renderer's native resolution may disappear on the actual surface. Design for the output, not only for the development monitor.

## 69. Concert lighting and visual projection are different systems

The visual software may send lighting cues, but lighting control should be treated as a separate output adapter with its own safety, addressing, networking, and fixture semantics. A colour or brightness intention in the visual scene should not automatically become a lighting command unless the operator has explicitly enabled that mapping.

---

# Part XIV — Safety, accessibility, and audience comfort

## 70. Photosensitivity and flashing content

Safety screening is a required part of a concert visual instrument. Fast flashes, high-contrast repeated patterns, saturated red flashes, and particular spatial-frequency patterns can create risks for some viewers.

The W3C WCAG 2.2 guidance for Success Criterion 2.3.1 says content should not contain more than three flashes in any one-second period unless it remains below defined general-flash and red-flash thresholds. WCAG is a web-content accessibility standard, not a complete concert-video regulation. It is still a useful conservative design reference for a software system that generates rapidly changing visual content. See the [W3C explanation of Guideline 2.3](https://www.w3.org/WAI/WCAG22/Understanding/seizures-and-physical-reactions) and [Success Criterion 2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold).

A 2025 Epilepsy Foundation Working Group consensus paper also advises media designers to avoid bright flashing patterns in the 10–20 Hz range, repetitive colour flashes, and certain oscillating or static stripe patterns. See [Visually-provoked seizures: Consensus of the Epilepsy Foundation Working Group](https://pubmed.ncbi.nlm.nih.gov/41283196/).

The implementation must not assume that “three flashes per second” is the only safety issue. Area, luminance, contrast, colour, spatial pattern, and viewing conditions matter.

### 70.1 Safety requirements

The system SHOULD:

- avoid rapid full-screen flashes as a default visual effect;
- include a flash/pattern screening stage for rendered sequences and live-generated states;
- limit high-contrast alternation and rapid saturated-red changes;
- detect periodic motion and pattern changes, not only hard cuts;
- assess the size of the affected region;
- provide a show-wide safety profile that cannot be bypassed accidentally;
- log safety interventions;
- include manual review of generated sequences;
- allow a low-flash / reduced-motion performance mode.

### 70.2 Live generation safety

A live generator can create states that were not present in offline tests. Therefore:

- safety limits MUST be enforced at the compositor/output stage as well as in generators;
- candidate generation MUST respect the safety profile;
- performer overrides MUST NOT disable hard safety constraints by default;
- stochastic systems MUST be screened across representative seeds and runtime states;
- a conservative fallback scene MUST be available;
- any deliberate exception must be an explicit, reviewed decision by the show team, not a hidden parameter.

No automated screening system can guarantee safety for every individual or viewing environment. Do not present a warning notice as a substitute for safe design.

## 71. Motion comfort

Rapid camera movement, repeated zooms, strong optical flow, high acceleration, and large-field motion can be uncomfortable for some viewers.

Provide controls for:

- maximum camera speed and acceleration;
- screen-space displacement;
- rotation speed;
- optical-flow intensity;
- motion blur;
- reduced-motion mode;
- stable horizon or reference frame where appropriate;
- static fallback and low-motion scenes.

## 72. Visual accessibility

Accessibility is not only a concern for the authoring UI. The public visual work should consider:

- sufficient contrast for meaningful text and symbols;
- not encoding essential meaning with colour alone;
- avoiding fast-changing fine detail that is only visible on a development monitor;
- allowing reduced motion for previews and control interfaces;
- offering alternative low-flash show profiles;
- maintaining legible navigation and control feedback for operators;
- avoiding unnecessary sensory overload in every scene.

## 73. Safety analysis architecture

A safety analysis pass should inspect:

- frame-to-frame luminance changes;
- repeated flash rate;
- high-saturation red transitions;
- spatial frequency and stripe patterns;
- affected image area;
- periodic high-contrast motion;
- frame sequences over time, not isolated still images.

Store the analyser version, thresholds, output profile, and review result in the `ShowManifest`. An offline safety check does not replace live output monitoring.

---

# Part XV — Workflows: from musical composition to concert visuals

## 74. Workflow A — Create the visual brief

1. Read the musical `CompositionBrief` and the completed arrangement.
2. Define the visual proposition in one or two sentences.
3. Choose a visual identity with a small material vocabulary.
4. Decide whether the visual work should follow, complement, or counterpoint the music.
5. Define output surfaces and practical venue constraints.
6. Define motion, brightness, detail, and safety limits.
7. State what must remain recognisable through the track.
8. Create a `VisualBrief` and a first `VisualIdentity` record.

## 75. Workflow B — Analyse the musical form

Use the Composition Atlas and the music generator's ontology to identify:

- sections and phrase boundaries;
- primary motifs and their transformations;
- anchor patterns and independent cycles;
- density and energy changes;
- breakdowns, returns, false returns, and endings;
- moments of rhythmic or timbral surprise;
- intended foreground/background changes.

Do not simply cut the visual scene at every bar. Identify moments that have a visual consequence.

## 76. Workflow C — Design the visual score

For each section:

1. Select a scene family or continuing scene state.
2. Assign foreground, midground, and background roles.
3. Select one or two recurring visual motifs.
4. Define motion grammar and pattern behaviour.
5. Decide which music semantics should affect the scene.
6. Decide which audio features may provide micro-modulation.
7. Define the transition from the previous section.
8. Define whether the scene should be remembered for a later return.
9. Set performer intervention points.
10. Validate the complete visual arc.

## 77. Workflow D — Build the visual generators

For each generator, define:

- visual family and intended role;
- input schema;
- initial conditions;
- deterministic seed behaviour;
- parameter constraints;
- update and render cost;
- lifecycle and reset rules;
- output objects or texture layers;
- transition behaviour;
- safety properties;
- test scenes and reference frames.

A generator that only looks good in its authoring view is not ready for concert use.

## 78. Workflow E — Rehearse with full music context

Rehearse the complete track or set, not only short loops. Confirm:

- section transitions;
- tempo changes;
- late and missing events;
- visual memory and motif return;
- motion density over long durations;
- live control behaviour;
- pause/resume and restart;
- fallback operation;
- output scaling and frame pacing;
- safety under different random seeds.

## 79. Workflow F — Build the show package

The package should include:

- visual project file;
- visual score and cue list;
- musical source references or event manifest;
- visual identity and scene definitions;
- generator versions and seeds;
- all external assets with provenance/licensing notes;
- shader and code versions;
- output profiles for each venue/surface;
- controller mappings;
- safety profile and screening report;
- fallback scenes;
- performance instructions and recovery procedures;
- a show manifest with checksums.

---

# Part XVI — Worked visual-composition examples

## 80. Example A — Stable anchor, unstable surface

**Musical source:** a stable kick or pulse anchors the track while metallic percussion and upper patterns change, displace, and fragment.

**Visual proposition:** a stable geometric frame remains present while a surface of marks, fragments, and particles changes its internal organisation.

**Visual plan:**

- The anchor motif is a stable central or off-centre geometric structure.
- The pulse modulates one restrained property, such as a slow expansion or subtle light response.
- Upper percussion events create small local marks or short-lived geometric fragments.
- Pattern identity controls the shape and spacing of those fragments.
- Phase displacement changes the relationship between the fragment field and anchor, not the whole camera.
- At a breakdown, upper fragments disappear, revealing the anchor as a complete object.
- On return, the anchor remains but the fragment field has a changed material or phase.

**Why it works:** the visual system represents the relationship between stable and unstable layers rather than firing all visual parameters from the kick and treble bands.

## 81. Example B — Rotating cycles and visual phase

**Musical source:** two or more unequal rhythmic cycles produce a recurring but shifting alignment.

**Visual proposition:** several circular or polygonal systems rotate at related but unequal rates. They periodically align and then separate.

**Visual plan:**

- Each musical cycle maps to a visual cycle with a declared period.
- Their phase relationship is derived from score time, not random frame updates.
- A particular alignment event can trigger a visual grouping or temporary fusion.
- A cycle omission may create a pause or leave one structure empty.
- The visual system preserves cycle identity across section transitions.

**Why it works:** it makes the structure of the rhythm perceptible through a parallel system without forcing a literal waveform display.

## 82. Example C — Fragment-to-whole

**Musical source:** a track begins with fragments, develops a motif, and eventually reveals a larger form.

**Visual proposition:** the audience initially sees isolated pieces that gradually reveal themselves as components of one object or environment.

**Visual plan:**

- Early scenes display isolated fragments with incomplete spatial relationships.
- Motif recurrence stabilises their shape or movement identity.
- Phrase endings allow fragments to align or briefly form a recognisable contour.
- The central development assembles a larger object.
- A false return may show the familiar fragments but with one missing component.
- The final section reveals or refuses to reveal the complete object.

**Why it works:** the visual narrative uses memory and expectation, rather than increasing particle count merely because the music gets louder.

## 83. Example D — Long plateau with internal change

**Musical source:** a stable groove continues for a long period while subtle timbral and rhythmic changes accumulate.

**Visual proposition:** one sustained scene changes through small, traceable transformations.

**Visual plan:**

- Maintain a stable composition and visual anchor.
- Map phrase-level material changes to gradual alterations of texture or geometry.
- Use occasional accents sparingly.
- Let background memory grow slowly but with bounded feedback.
- Delay a scene transition until a true formal change or performer decision.

**Why it works:** it avoids false visual climax. The audience can remain inside one environment while learning to notice its evolution.

## 84. Example E — False return / interrupted scene memory

**Musical source:** a familiar section or motif appears to return, but one important musical element is absent or displaced.

**Visual proposition:** a remembered visual scene returns with a meaningful omission.

**Visual plan:**

- Store a snapshot or reproducible state of the earlier visual motif.
- On the false return, restore its visual identity but suppress one expected layer or change its spatial position.
- Let the absence remain visible for a phrase.
- Resolve, transform, or keep the missing component absent according to the music's subsequent direction.

**Why it works:** it uses visual memory as a compositional resource.

## 85. Example F — Two-movement concert piece

**Musical source:** a two-movement composition with different rhythmic and timbral identities.

**Visual proposition:** the first movement establishes a precise, bounded visual world; the second transforms its rules into a more fluid environment.

**Visual plan:**

- Movement I uses a stable geometric frame, limited palette, and measured movement.
- The inter-movement transition gradually dissolves the grid but retains one recurring motif.
- Movement II uses fluid deformation, larger depth movement, and a more diffuse texture.
- The recurring motif appears as a trace or contour inside the new environment.
- The ending either restores the original frame in altered form or leaves the new world unresolved.

**Why it works:** the set gains contrast without losing identity.

---

# Part XVII — Data contracts and reference schemas

The following JSON examples are illustrative reference records. The Musical Ontology manual remains authoritative for musical entity IDs and time semantics. The visual instrument adds visual entities and links to those IDs; it does not redefine the music objects.

## 86. Visual brief

```json
{
  "visual_brief_id": "vbrief_001",
  "version": 1,
  "title": "Mechanical Drift",
  "proposition": "A stable geometric world slowly breaks into independent moving fragments, then returns as a transformed object.",
  "visual_identity_id": "vid_mechanical_01",
  "relationship_to_music": "complementary_counterpoint",
  "preferred_materials": ["line_geometry", "raster_feedback", "metallic_texture"],
  "motion_grammar": ["rotate", "fracture", "gather", "drift"],
  "constraints": {
    "max_full_frame_flash_rate_hz": 0.0,
    "allow_high_contrast_strobe": false,
    "allow_unbounded_feedback": false,
    "max_particle_count": 120000,
    "reduced_motion_available": true
  },
  "output_profile_id": "out_profile_projector_01"
}
```

## 87. Visual scene

```json
{
  "visual_scene_id": "scene_B_01",
  "version": 1,
  "role": "development",
  "visual_identity_id": "vid_mechanical_01",
  "objects": [
    {"visual_object_id": "obj_anchor_grid", "role": "foreground_anchor", "locked": true},
    {"visual_object_id": "obj_fragment_field", "role": "midground_motion", "locked": false},
    {"visual_object_id": "obj_feedback_trace", "role": "background_memory", "locked": false}
  ],
  "attention_plan": {
    "primary": "obj_anchor_grid",
    "secondary": ["obj_fragment_field"],
    "background": ["obj_feedback_trace"]
  },
  "transition_in": "transition_assemble_02",
  "transition_out": "transition_erosion_01",
  "safety_profile_id": "safety_concert_default"
}
```

## 88. Mapping rule

```json
{
  "mapping_id": "map_section_motif_01",
  "version": 1,
  "source": {
    "type": "musical_semantic",
    "entity_type": "Motif",
    "entity_id": "motif_metal_02",
    "event": "motif_entry"
  },
  "target": {
    "type": "visual_action",
    "visual_object_id": "obj_fragment_field",
    "action": "activate_motion_motif"
  },
  "mode": "structural_event",
  "priority": 60,
  "seed_policy": "composition_seed_plus_mapping_id",
  "missing_source": "ignore_and_log",
  "intent": "Make the recurring metallic motif visible through a recurring but transformable fragment gesture."
}
```

## 89. Performer override

```json
{
  "override_id": "override_014",
  "source": "controller_pad_2",
  "target": {
    "type": "scene_parameter",
    "scene_id": "scene_B_01",
    "parameter": "visual_density"
  },
  "mode": "momentary",
  "value": 0.28,
  "priority": 90,
  "started_at_monotonic_ns": 928104500000,
  "release_policy": "return_to_director_value",
  "safety_clamped": true
}
```

## 90. Output surface

```json
{
  "surface_id": "surface_main_projector",
  "name": "Main projection",
  "kind": "projector",
  "native_resolution": [1920, 1080],
  "refresh_rate_hz": 60.0,
  "aspect_ratio": "16:9",
  "logical_rect": [0, 0, 1, 1],
  "calibration_profile": "cal_main_venue_A",
  "safe_region": [0.04, 0.04, 0.92, 0.92],
  "colour_profile": "venue_projector_A",
  "fallback_profile": "fallback_low_motion_01"
}
```

## 91. Show manifest

```json
{
  "show_manifest_id": "show_2026_11_26_A",
  "show_version": "1.0.0",
  "visual_project_id": "vproject_001",
  "music_project_ids": ["comp_001", "comp_002"],
  "visual_engine_version": "0.1.0",
  "generator_versions": {
    "particle_field": "2.1.0",
    "geometry_grammar": "1.3.0",
    "feedback_compositor": "1.0.2"
  },
  "random_seed_root": 19321,
  "output_profile_ids": ["out_profile_projector_01"],
  "safety_profile_id": "safety_concert_default",
  "asset_manifest": "assets_manifest.json",
  "fallback_scene_id": "scene_safe_static_01"
}
```

---

# Part XVIII — Testing, evaluation, and reference laboratory

## 92. Test the visual instrument as a creative system

A system can render at 60 FPS and still produce poor visuals. It can produce beautiful still frames and fail during a concert. Evaluation must cover technical, compositional, perceptual, operational, and safety quality separately.

### 92.1 Technical tests

- stable frame pacing;
- maximum GPU and memory budget;
- no unbounded object, texture, or feedback accumulation;
- deterministic replay when enabled;
- correct clock conversion;
- bounded input latency;
- missing/out-of-order event recovery;
- output-device loss and recovery;
- scene preload and shader warm-up;
- safe fallback activation;
- no public debug leakage.

### 92.2 Compositional tests

- visual motifs remain recognisable through permitted mutation;
- visual scenes have distinct roles;
- section transitions are intentional;
- visual memory and returns work;
- visual density follows the brief rather than only audio amplitude;
- stillness and negative space can occur;
- visual form can diverge from musical form without losing declared relationships;
- a live override does not destroy the committed score.

### 92.3 Mapping tests

- every mapping has a declared source and target;
- input range and output range are respected;
- missing data has a defined response;
- duplicate event IDs do not create duplicate actions;
- stale events are handled according to policy;
- competing mappings resolve deterministically;
- smoothing and hysteresis behave as declared;
- safety limits override ordinary mappings.

### 92.4 Perceptual and human evaluation

Use listening/viewing studies or structured expert review to evaluate:

- whether the primary visual figure is identifiable;
- whether visual motion relates meaningfully to the music;
- whether motif returns are recognisable;
- whether the visual work becomes monotonous or overactive;
- whether transitions feel prepared or arbitrary;
- whether the output is legible at actual viewing distance;
- whether the work's visual identity is coherent across the set.

Do not reduce all artistic qualities to one “visual quality score”.

## 93. Golden visual fixtures

Maintain a reference laboratory of:

- known musical event sequences;
- reference visual scores;
- deterministic scene states;
- golden rendered frames;
- golden short sequences;
- known mapping outputs;
- expected transition states;
- performance benchmarks;
- safety-test sequences;
- failure and recovery scenarios.

Golden-frame comparison should allow a tolerance for GPU and driver differences where pixel-perfect identity is not guaranteed. In those cases, compare structural or perceptual properties as well as image hashes.

## 94. Reference concert test suite

At minimum, test these musical scenarios:

1. straight stable pulse;
2. sparse kick with active upper percussion;
3. ghost-note breakbeat;
4. rotating odd-length cycle;
5. unequal-cycle interlock;
6. phase-displaced duplicate;
7. irregular burst pattern;
8. long plateau with subtle development;
9. breakdown and return;
10. false return or interrupted refrain;
11. fragment-to-whole form;
12. multi-movement composition;
13. tempo change;
14. deliberate silence;
15. live improvisational passage;
16. abrupt stop and restart;
17. missing semantic event stream with audio fallback;
18. loss and restoration of one output surface.

## 95. Safety reference suite

Test:

- rapid full-screen luminance changes;
- repeated high-contrast alternating patterns;
- saturated-red transitions;
- periodic stripe and grid motion;
- large-area repeated pulses;
- high-speed camera movement;
- stochastic visual generation across multiple seeds;
- performer macro extremes;
- scene transitions during an active visual burst.

An approved scene should pass the project's chosen screening process and manual review before being allowed into a show package.

---

# Part XIX — Development roadmap

## 96. Phase 0 — Visual-system foundation

**Goal:** create a stable renderer and visual project model.

Implement:

- visual project and visual brief;
- visual identity and scene entities;
- stable visual object IDs;
- one renderer backend;
- one output surface;
- scene load/save;
- deterministic static scenes;
- frame-time telemetry;
- safe fallback scene.

**Acceptance:** the program can load a project, render a known scene, save a snapshot, and recover from a scene failure.

## 97. Phase 1 — Musical and audio input

**Goal:** receive meaningful music data and audio features.

Implement:

- structured musical event adapter;
- timing and event bus;
- audio input and feature analysis;
- OSC and MIDI input adapters;
- clock-domain conversion;
- event deduplication and late-event policy;
- mapping-rule schema.

**Acceptance:** a test composition can drive a visual scene using semantic events, while an external audio file can drive the fallback feature mode.

## 98. Phase 2 — Visual composition grammar

**Goal:** generate reusable visual objects, motifs, patterns, phrases, and scenes.

Implement:

- geometry generator;
- particle generator;
- texture/feedback generator;
- motion gesture library;
- visual motif lineage;
- visual phrase and scene transitions;
- visual score editor or authoring representation.

**Acceptance:** one complete track can be accompanied by a visual score with recognisable motif returns and controlled formal development.

## 99. Phase 3 — Visual director and intelligence

**Goal:** plan, select, and develop visual scenes in context.

Implement:

- show, track, section, and phrase directors;
- candidate scene generation;
- visual evaluation and constraints;
- mapping conflict resolution;
- deterministic random streams;
- scene memory and return behaviour;
- explanation and decision records.

**Acceptance:** the director can choose among multiple candidates, explain its state transitions, and preserve accepted material.

## 100. Phase 4 — Live performance and control

**Goal:** make the system performable by a human operator.

Implement:

- hybrid score/performance mode;
- semantic macro controls;
- scene launch and cue control;
- freeze/hold and fallback actions;
- bounded overrides;
- history/snapshot/recovery;
- rehearsal and show modes.

**Acceptance:** a performer can intervene without losing the visual score or causing an uncontrolled state transition.

## 101. Phase 5 — Venue and production readiness

**Goal:** support real concert output and repeatable deployment.

Implement:

- multi-surface output profiles;
- calibration and projection mapping;
- Spout/NDI or other required output adapters;
- lighting output adapter if required;
- adaptive quality tiers;
- safety screening and runtime safety clamps;
- show manifest and asset validation;
- startup preflight and failure recovery.

**Acceptance:** the complete set can be rehearsed and executed using a versioned show package, validated output profile, and tested fallback path.

---

# Part XX — Failure modes and anti-patterns

## 102. Common visual-system mistakes

### 102.1 The permanent audio spectrum

Every scene is a waveform, spectrum, or bar graph. It is a valid visual mode but not a complete visual language.

**Correction:** use audio analysis as one source of control within a wider scene architecture.

### 102.2 Every kick causes a flash

The whole image responds to the kick irrespective of musical role or formal context.

**Correction:** distinguish anchors, accents, phrase events, and structural events. Use restrained local changes and explicit safety limits.

### 102.3 One feature controls everything

RMS drives scale, particles, colour, rotation, blur, and camera movement simultaneously.

**Correction:** use a mapping registry, parameter ownership, and limited mapping scopes.

### 102.4 Random effects are mistaken for generative art

The system changes random parameters but has no persistent visual identity or developmental plan.

**Correction:** generate candidates within a visual vocabulary and visual score.

### 102.5 Visual scenes are just presets

A scene has a name and a set of parameters but no identity lineage, transition logic, or memory.

**Correction:** treat scenes as stateful compositions with objects, relationships, and allowed transformations.

### 102.6 The image never rests

Every beat, note, and frequency band changes something.

**Correction:** include stillness, held composition, negative space, and low-motion scenes as normal states.

### 102.7 Visual form duplicates musical form too literally

A new bar launches a new scene; a breakdown always fades to black; a climax always increases particle count.

**Correction:** translate formal function, not bar labels.

### 102.8 The GPU is treated as infinite

The system increases resolution, particle count, feedback history, and shader passes until a live frame stalls.

**Correction:** budget resources, preflight, track frame time, and provide adaptive quality tiers.

### 102.9 Python controls every pixel

The main CPU process generates per-pixel data, writes textures repeatedly, or performs blocking image work during the render loop.

**Correction:** use Python or another high-level layer for orchestration and use GPU shaders/native code for high-volume rendering.

### 102.10 Safety is checked only after the show

A live random generator may produce unreviewed high-risk flashes or patterns.

**Correction:** safety clamps must operate at runtime and the output stage, with offline sequence screening and manual review.

### 102.11 The performer has only destructive controls

A single button regenerates the scene, changes several unrelated settings, or discards the current state.

**Correction:** use scoped semantic controls, bounded overrides, and snapshots.

### 102.12 The output is not tested on the real surface

Fine detail, dark values, typography, and colour relationships change on the projector or LED wall.

**Correction:** use venue profiles, test patterns, calibration, and actual output rehearsal.

---

# Part XXI — Acceptance criteria and developer checklist

## 103. Visual composition integrity

- [ ] The visual project has an explicit visual proposition and identity.
- [ ] Scenes contain persistent visual objects and relationships.
- [ ] Motif returns preserve their intended identity.
- [ ] Visual patterns have defined cycles and timing behaviour.
- [ ] Visual phrases and sections have clear functions.
- [ ] The visual score can diverge from musical form intentionally.
- [ ] Stillness and negative space are supported.
- [ ] The system does not equate complexity with quality.

## 104. Music integration

- [ ] Structured score events are preferred when available.
- [ ] Audio analysis reports its features, windows, latency, and confidence.
- [ ] Musical IDs are referenced, not copied into incompatible parallel entities.
- [ ] Musical, audio, performance, and render clocks remain distinct.
- [ ] Tempo and meter changes are handled.
- [ ] Late, duplicate, and missing events have defined behaviour.
- [ ] Performer override priority is explicit.

## 105. Generation and control

- [ ] Generators have bounded parameters and resource limits.
- [ ] Randomness can be seeded and reproduced.
- [ ] Candidate generation is separate from commit.
- [ ] Mapping conflicts have declared resolution rules.
- [ ] Live overrides have scope, duration, and restoration policies.
- [ ] The performer can freeze, hold, recover, and switch to a fallback.
- [ ] Explanations reflect recorded decisions.

## 106. Rendering and venue readiness

- [ ] Frame pacing and GPU time are measured.
- [ ] Adaptive quality preserves scene semantics.
- [ ] Assets and shaders are prepared before performance.
- [ ] Output profiles exist for actual surfaces.
- [ ] Projection geometry and safe regions are validated.
- [ ] Missing output devices do not crash the application.
- [ ] Show startup preflight validates required assets and devices.
- [ ] The show manifest records versions, mappings, seeds, and output settings.

## 107. Safety and evaluation

- [ ] Flash and pattern screening is available.
- [ ] Runtime safety limits override mappings and ordinary performer controls.
- [ ] Reduced-motion and low-flash profiles exist.
- [ ] Visual content has been reviewed at realistic viewing scale.
- [ ] Golden visual fixtures and reference music scenarios exist.
- [ ] Performance, artistic, operational, and safety quality are evaluated separately.

---

# Appendix A — Canonical visual vocabulary

## A1. Recommended visual roles

- `foreground_anchor`
- `foreground_accent`
- `foreground_motif`
- `midground_motion`
- `midground_structure`
- `background_environment`
- `background_memory`
- `transition_material`
- `spatial_boundary`
- `latent_object`
- `negative_space`

## A2. Recommended visual-event types

- `spawn`
- `remove`
- `reveal`
- `conceal`
- `move`
- `morph`
- `fracture`
- `assemble`
- `rotate`
- `pulse`
- `freeze`
- `resume`
- `fade`
- `cut`
- `mask`
- `displace`
- `change_material`
- `change_palette`
- `change_camera`
- `change_scene`
- `hold`
- `reset`

## A3. Recommended motion-gesture vocabulary

`pulse`, `drift`, `orbit`, `scan`, `fall`, `rise`, `fold`, `unfold`, `fracture`, `scatter`, `gather`, `align`, `stretch`, `compress`, `tremor`, `grow`, `branch`, `dissolve`, `erode`, `smear`, `echo`, `reveal`, `conceal`, `zoom`, `pan`, `track`, `freeze`, `resume`.

## A4. Recommended mapping modes

`continuous`, `event_impulse`, `structural_event`, `categorical_state`, `performer_gesture`, `seeded_choice`, `time_curve`, `manual_override`.

---

# Appendix B — Example OSC namespace

OSC is a transport for messages, not the entire visual ontology. Define a stable namespace, version it, and pass structured payloads where possible.

Suggested families:

```text
/idmvis/v1/show/start
/idmvis/v1/show/stop
/idmvis/v1/transport/position
/idmvis/v1/transport/tempo
/idmvis/v1/section/enter
/idmvis/v1/phrase/enter
/idmvis/v1/motif/trigger
/idmvis/v1/pattern/state
/idmvis/v1/audio/feature
/idmvis/v1/visual/cue
/idmvis/v1/visual/scene
/idmvis/v1/visual/macro
/idmvis/v1/visual/override
/idmvis/v1/output/status
/idmvis/v1/safety/state
/idmvis/v1/telemetry/frame
```

Rules:

1. Include a protocol version in the namespace.
2. Define units and value ranges.
3. Use timetags or a declared timestamp field for scheduled events.
4. Identify event source and sequence number where ordering matters.
5. Keep high-rate continuous control separate from low-rate semantic events.
6. Do not send an entire scene graph as a stream of tiny messages every frame; send state changes and let the renderer maintain state.
7. Define timeout, reconnect, and stale-message behaviour.

The Open Sound Control 1.0 specification describes a message-based, transport-independent protocol for communication among computers, sound synthesizers, and multimedia devices. See [Open Sound Control Specification 1.0](https://github.com/CNMAT/OpenSoundControl.org/blob/master/spec-1_0.md).

---

# Appendix C — Technical references and implementation links

These links are starting points for implementation. They are not endorsements of a particular stack, and library/API support should be checked for the target operating system and hardware before choosing a dependency.

## C1. Real-time visual environments and GPU rendering

- [TouchDesigner documentation](https://docs.derivative.ca/) — node-based real-time media environment. Useful for prototyping audio/MIDI/OSC input, procedural networks, image compositing, and live output.
- [TouchDesigner CHOP documentation](https://docs.derivative.ca/CHOP) — procedural channel operators and input/control integration, including audio, MIDI, and OSC.
- [TouchDesigner GLSL TOP](https://docs.derivative.ca/GLSL_TOP) — shader-based image processing and compute workflows.
- [TouchDesigner TOP documentation](https://docs.derivative.ca/TOP) — image generation, transform, compositing, feedback, rendering, and texture operations.
- [TouchDesigner Perform Mode](https://docs.derivative.ca/Perform_Mode) — a performance-oriented output window separate from the authoring/network workspace.
- [W3C WebGPU specification](https://www.w3.org/TR/webgpu/) — GPU compute and graphics API for web environments; verify implementation support and status for the intended deployment.

## C2. Control, timing, and music protocols

- [Open Sound Control 1.0 specification](https://github.com/CNMAT/OpenSoundControl.org/blob/master/spec-1_0.md) — message syntax, bundles, and time-tagged communication.
- [MIDI.org MIDI 2.0 overview](https://midi.org/midi-2-0) — MIDI 2.0 extends MIDI 1.0 and retains backward-compatibility priorities; useful for expressive controller and event integration.
- [MIDI 2.0 UMP and Protocol Specification](https://midi.org/universal-midi-packet-ump-and-midi-2-0-protocol-specification) — Universal MIDI Packet and MIDI 2.0 protocol reference.

## C3. Video and texture transport

- [Spout](https://leadedge.github.io/) — GPU-accelerated texture sharing between Windows applications.
- [Spout2](https://spout2.com/) — current Windows texture-sharing ecosystem and SDK information.
- [NDI SDK documentation](https://docs.ndi.video/all/developing-with-ndi/sdk) — network video integration for compatible applications and systems.

## C4. Lighting transport

- [Art-Net official site](https://art-net.org.uk/) — Art-Net protocol information and specification resources.
- [Art-Net 4 specification](https://art-net.org.uk/art-net-specification/) — Ethernet transport of DMX512/RDM lighting data; use it for lighting fixtures, not as a full-frame image protocol.

## C5. Safety and accessibility

- [W3C WCAG 2.2 — Seizures and Physical Reactions](https://www.w3.org/WAI/WCAG22/Understanding/seizures-and-physical-reactions) — explains the intent and scope of WCAG Guideline 2.3.
- [W3C Success Criterion 2.3.1 — Three Flashes or Below Threshold](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold) — web-content guidance on flashing content and thresholds.
- [Epilepsy Foundation Working Group consensus: Visually-provoked seizures](https://pubmed.ncbi.nlm.nih.gov/41283196/) — expert consensus that includes recommendations for media designers.

---

# Appendix D — Cross-reference index to the ten companion volumes

Use the following as a practical reading path when implementing a visual feature.

| Visual-system problem | First reference | Additional references |
| --- | --- | --- |
| Create a visual motif from musical material | Volume 3 — Composition Atlas, motif families and development | Volume 6 — Ontology; Volume 7 — Generative Intelligence |
| Make visual pattern cycles mirror polymeter | Volume 3 — rhythmic pattern relationships | Volume 1 — mathematical foundations; Volume 6 — time model |
| Design a visual material or hybrid image object | Volume 4 — Sound Design Manual, sound-object and hybrid-structure concepts | Volume 1 — production/programming; Volume 9 — rendering architecture |
| Create scene attention and figure/ground | Volume 8 — Perceptual Orchestration | Volume 2 — listener, expectation, and perception |
| Build a visual scene planner | Volume 7 — Generative Intelligence | Volume 5 — decision hierarchy; Volume 6 — ontology |
| Preserve visual identity through variation | Volume 5 — mutation contracts and invariants | Volume 6 — identity/provenance; Volume 10 — history and agency |
| Synchronise visuals with generated music | Volume 6 — time/event representation | Volume 9 — real-time scheduling and latency |
| Build live performer controls | Volume 10 — interaction modes and semantic controls | Volume 5 — human agency; Volume 9 — real-time execution |
| Build audio-reactive fallback | Volume 1 — audio feature analysis and programmer's guide | Volume 8 — perceptual feature analysis; Volume 9 — signal/clock execution |
| Make a complete concert visual arc | Volume 3 — track forms and transitions | Volume 2 — long-form composition; Volume 8 — attention trajectory |
| Build reproducible show files | Volume 9 — render manifests and production packages | Volume 6 — serialization and provenance; Volume 5 — project integrity |
| Screen visual safety | This volume, Part XIV | W3C and Epilepsy Foundation references in Appendix C |

---

# Appendix E — Visual feature specification template

Every major visual feature should be specified before implementation.

```text
FEATURE NAME:
FEATURE ID / VERSION:

ARTISTIC INTENTION:
What should the audience see or perceive?

MUSICAL RELATIONSHIP:
Which musical entities or audio features influence it?
Is the relationship synchronised, complementary, independent, or in counterpoint?

VISUAL ENTITIES:
Which scenes, objects, motifs, layers, or surfaces are affected?

GENERATION METHOD:
Which algorithm or renderer creates the result?

INPUTS:
Data type, timestamp, units, range, confidence, update frequency.

OUTPUTS:
Visual properties, events, image layers, or scene changes.

IDENTITY AND MUTATION:
What must remain recognisable?
What may change?
What is forbidden?

TIME AND SYNCHRONISATION:
Clock domain, latency, interpolation, late-event policy.

PERFORMANCE BUDGET:
CPU, GPU, memory, frame-time, asset requirements.

LIVE CONTROL:
Available performer controls, override scope, restoration policy.

SAFETY:
Flash, luminance, contrast, pattern, motion, and fallback constraints.

FAILURE BEHAVIOUR:
Missing input, GPU failure, missing asset, stale event, output loss.

TESTS:
Unit, mapping, timing, golden-frame, long-run, safety, and live rehearsal.

ACCEPTANCE CRITERIA:
Observable conditions required for release.
```

---

# Final declaration — Visual composition as an independent musical partner

The purpose of an IDM concert visual instrument is not to decorate a composition, to show the audience that the software can analyse a spectrum, or to make every musical event visible. Its purpose is to create a second time-based artwork that can remember, anticipate, transform, contradict, support, and extend the music.

A visual system should know when a motif returns. It should understand that an irregular rhythm may be a stable identity rather than random noise. It should distinguish a local accent from a structural change. It should be able to preserve a visual object while changing its material, or destroy an object while preserving its motion identity. It should recognise that a breakdown can reveal rather than empty, and that a climax can become more powerful through subtraction rather than accumulation.

The music-generation system supplies a rich source of semantic information. The visual system should use that information without becoming subordinate to it. It should be allowed to build its own motifs, its own phrases, its own attention trajectory, and its own form.

The performer should remain able to intervene. The system should remain reproducible when required, unpredictable only within declared boundaries, safe under tested limits, and dependable under live conditions.

**The ideal result is not a screen that reacts to the track. It is a visual composition that performs alongside the track.**

---

**End of Volume 11 — IDM Visual Instrument: Visual Composition, Generative Art & Live Concert Architecture**

# Appendix F — Direct links to the ten companion manuals

The links below point to the exact uploaded editions used when preparing this volume. Keep these files together in one directory for the relative links to work. If you rename a file, update the corresponding link.

1. [IDM Field Guide for Composers, Producers, and Programmers](<IDM_Field_Guide_for_Composers_Producers_and_Programmers(1).md>)
2. [Advanced Composition and Generative Systems](<IDM_Advanced_Composition_and_Generation_Appendix(1).md>)
3. [IDM Composition Atlas](<IDM_Composition_Atlas_Patterns_Phrases_and_Track_Structures(1).md>)
4. [IDM Sound Design Manual](<IDM_Sound_Design_Synthesis_and_Hybrid_Sound_Architecture(1).md>)
5. [IDM Generative Instrument: Philosophy, Principles & Design Constitution](<IDM_Generative_Instrument_Philosophy_Principles_and_Design_Constitution(1).md>)
6. [Musical Ontology, Representation & Composition Data Architecture](<Musical_Ontology_Representation_and_Composition_Data_Architecture(1).md>)
7. [Generative Intelligence, Algorithms & Decision-Making](<Generative_Intelligence_Algorithms_and_Decision_Making(1).md>)
8. [Perceptual Orchestration, Attention & Musical Scene Architecture](<IDM_Perceptual_Orchestration_Attention_and_Musical_Scene_Architecture(1).md>)
9. [Audio Engine, Rendering, Routing & Reproducible Production](<IDM_Audio_Engine_Rendering_Routing_and_Reproducible_Production(1).md>)
10. [Creative Interaction, Composer Agency & Generative UX](<Creative_Interaction_Composer_Agency_and_Generative_UX(1).md>)
