# Musical Ontology, Representation & Composition Data Architecture

## A Developer's Architecture Manual for the IDM Generative Instrument

**Document type:** Foundational technical and conceptual specification  
**Collection role:** Volume 6 — the canonical musical data model  
**Audience:** Music-software architects, algorithmic-composition researchers, audio developers, MIDI and notation developers, tool builders, and composers working with generative systems  
**Status:** Reference architecture and implementation guidance  
**Version:** 1.0  

---

## Abstract

A generative music system cannot compose intelligently if it represents music only as a list of notes, a collection of MIDI clips, or a set of audio tracks. Those representations are useful, but they are not sufficient as the system's internal understanding of a musical work.

A composition contains intentions, identities, materials, motifs, patterns, voices, roles, phrases, sections, relationships, transformations, constraints, performance instructions, sound-producing instruments, routing, automation, and renderable events. Some of these entities contain other entities; some overlap in time; some derive from others; some refer to the same material from different perspectives. A simple tree cannot express all of those relationships without losing information or creating duplication.

This manual defines a **Musical Ontology and Composition Data Architecture** for a generative instrument. It establishes a canonical vocabulary, a layered data model, typed relationships, stable identity and provenance, exact musical-time representation, event and pattern semantics, pitch and tuning representation, material lineage, constraints, candidate and commitment states, sound-realisation separation, serialization, versioning, APIs, validation, and test requirements.

The central architectural proposition is:

> **The project must represent the musical work at the level at which compositional decisions are made, while retaining enough precise performance and realisation data to reproduce what is heard.**

The architecture is intentionally technology-neutral. JSON examples are used for readability, but the model can be implemented in Python, Rust, C++, TypeScript, Kotlin, Swift, or another language. A production implementation may use relational tables, document storage, graph storage, binary event buffers, or a hybrid persistence layer. Those are implementation choices; the semantic contracts in this manual are the stable part.

This manual is designed to work with *IDM Generative Instrument: Philosophy, Principles & Design Constitution*. The constitution establishes why the system must preserve identity, intention, human agency, explicit mutations, reproducibility, and separation of responsibilities. This volume defines how those principles become representable and enforceable data structures.

---

# How to use this manual

This is not a universal music notation standard and should not be treated as a replacement for MIDI, MusicXML, OSC, or a DAW project format. It defines an internal canonical model for a generative composition system. Interchange formats should be adapters around that model.

Developers should read Parts I–VII before implementing a data model. Parts VIII–XIII specify how the model is persisted, queried, edited, validated, and exchanged. Parts XIV–XVII provide reference schemas, worked examples, test cases, and an implementation sequence.

## Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe requirement strength:

- **MUST / MUST NOT:** required for architectural correctness or data integrity.
- **SHOULD / SHOULD NOT:** recommended default; a documented exception is possible.
- **MAY:** optional capability.

A feature that departs from a SHOULD-level recommendation must document why. A feature that violates a MUST-level rule is incompatible with this architecture until the violation is resolved or the architecture is explicitly amended.

## Relationship to the other manuals

| Reference | Responsibility of that manual | Responsibility of this manual |
|---|---|---|
| IDM Field Guide for Composers, Producers, and Programmers | IDM context, musical grammar, foundations | Represent those concepts precisely as data |
| Advanced Composition and Generation Appendix | Advanced compositional and generative methods | Define entities, states, relationships, and interfaces those methods operate on |
| IDM Composition Atlas | Patterns, phrases, motifs, track structures, compositional development | Define the canonical representation of those objects |
| IDM Sound Design, Synthesis and Hybrid Sound Architecture | Synthesis, effects, hybrid sound, timbre and processing | Represent sound sources and their relationship to score and performance data |
| IDM Generative Instrument Constitution | Philosophy, principles, invariants, subsystem responsibilities | Turn those principles into data contracts, schemas, and validation |

This document does not prescribe a single algorithm, synthesis engine, genre template, database, programming language, or user interface.

---

# Part I — The central model: a composition is a connected musical work

## 1. Why a note list is not a composition model

A note list records events. It does not necessarily record why those events exist, what musical idea they instantiate, what they are derived from, what role they fulfil, which phrase they belong to, or which transformations are allowed to change them.

Consider a four-bar percussion figure. A note-only system may store kick, snare, and metallic-hit events. A composition-aware system can additionally represent:

- the figure as a reusable pattern definition;
- one use of that definition as a pattern instance at a specific location;
- the source motif from which the metallic rhythm was derived;
- the phrase containing the instance;
- the section in which the phrase appears;
- the voice that performs it;
- the role that voice fulfils at that moment;
- the relation between the percussion pattern and the bass rhythm;
- the transformation that displaced selected accents;
- the constraints that kept the kick anchors unchanged;
- the candidate state before acceptance;
- the committed state after the composer selected it;
- the sound source, patch, routing and automation that realise the events.

These are not decorative annotations. They are the information required to make meaningful edits without destroying the larger composition.

A robust system must therefore distinguish at least three things:

1. **Musical objects** — ideas and structures such as motifs, patterns, phrases, sections, voices, and roles.
2. **Musical events** — timed actions such as notes, triggers, rests, gestures, and control changes.
3. **Sound realisations** — instruments, samples, synthesis patches, effect graphs, performance controls, and rendered audio.

They are connected, but they are not interchangeable.

## 2. The layered architecture

The recommended model has seven semantic layers. They may be implemented in one application or distributed across services, but their responsibilities must remain distinguishable.

### Layer A — Intent and constraints

Represents what the composer is trying to achieve and what must or should remain true.

Canonical objects:

- `CompositionBrief`
- `CompositionIdentity`
- `ArtisticIntent`
- `ConstraintSet`
- `Constraint`
- `Goal`
- `Exclusion`
- `Preference`

This layer describes desired properties, not the resulting notes.

### Layer B — Musical structure

Represents the large and small formal organisation of a work.

Canonical objects:

- `Composition`
- `Movement`
- `Section`
- `Phrase`
- `Passage`
- `Transition`
- `FormalPlan`
- `StructuralMarker`

This layer describes the work's temporal and developmental architecture.

### Layer C — Musical material and relationships

Represents reusable or evolving ideas.

Canonical objects:

- `Material`
- `Motif`
- `PatternDefinition`
- `HarmonyContext`
- `PitchCollection`
- `RhythmicCell`
- `Gesture`
- `Transformation`
- `MaterialLineage`

This layer describes what musical substance is used and how it relates to other substance.

### Layer D — Score and performance events

Represents what happens, when it happens, and how it is expressed.

Canonical objects:

- `Voice`
- `RoleAssignment`
- `PatternInstance`
- `Event`
- `NoteEvent`
- `TriggerEvent`
- `ControlEvent`
- `AutomationLane`
- `PerformanceExpression`
- `TempoMap`
- `MeterMap`
- `TuningContext`

This layer describes timed musical behaviour. It is the primary bridge between composition logic and playback.

### Layer E — Sound realisation

Represents how musical events become sound.

Canonical objects:

- `InstrumentDefinition`
- `InstrumentInstance`
- `Patch`
- `SampleAsset`
- `SynthesisGraph`
- `EffectGraph`
- `ParameterDefinition`
- `ParameterBinding`
- `RoutingGraph`
- `MixBus`

This layer describes sound-producing resources and their configuration.

### Layer F — Generation, decision and editing state

Represents how a musical object was proposed, selected, transformed, frozen, or edited.

Canonical objects:

- `Candidate`
- `GenerationRun`
- `DecisionRecord`
- `MutationRecord`
- `EditTransaction`
- `Revision`
- `FrozenRegion`
- `EvaluationReport`
- `ProvenanceRecord`

This layer protects authorship, traceability, reproducibility, and non-destructive editing.

### Layer G — Execution and delivery

Represents how the project is played, rendered, exported, or transferred to another application.

Canonical objects:

- `PlaybackConfiguration`
- `RenderProfile`
- `RenderJob`
- `RenderArtifact`
- `ExportManifest`
- `InterchangePackage`
- `ExternalReference`

This layer must not silently redefine musical meaning. It is an execution and delivery view of the project.

## 3. The canonical source of truth

The **native composition project** is the authoritative representation of the work.

A MIDI file, MusicXML document, audio stem, waveform preview, plugin state, or DAW export is a projection or interchange representation. It may preserve some aspects of the project and omit others.

The project MUST be able to preserve information that common interchange formats cannot fully express, including:

- material identity and lineage;
- motif-to-pattern derivation;
- phrase and section relationships;
- multiple concurrent metrical layers;
- arbitrary microtiming;
- non-note gestures and sound events;
- semantic roles;
- generator constraints and decision records;
- exact instrument and effect graph state where available;
- automation semantics;
- candidate history and accepted-state history.

The canonical project MUST NOT depend on an exported MIDI file or rendered audio being available in order to reconstruct its musical structure.

---

# Part II — Canonical ontology: what entities mean

## 4. Entity catalogue

The following table defines the core entity set. Applications MAY introduce specialised entities, but they SHOULD map to these concepts or document why a separate concept is necessary.

| Entity | Definition | Important distinction |
|---|---|---|
| `Project` | Persistent container for one or more related compositions and their assets | Not the composition itself |
| `CompositionBrief` | Structured statement of artistic intent and constraints | Describes desired work, not actual events |
| `CompositionIdentity` | Persistent characteristics that make the work recognisable | Not a fixed style label |
| `Composition` | A complete musical work or work-in-progress | Can contain movements or sections |
| `Movement` | Large-scale formal division | Optional; not every track needs movements |
| `Section` | Major formal region with a role in the work's architecture | Not merely a fixed number of bars |
| `Phrase` | Bounded unit of musical statement, response, development, or continuation | Can be asymmetric and may cross conventional bar boundaries |
| `Passage` | A selected temporal region, often used for editing, analysis, or playback | Does not imply formal function |
| `Transition` | A relationship and process connecting formal regions | Not just a riser or fill |
| `Voice` | An independent stream of musical or sonic activity | Not necessarily one MIDI channel or instrument |
| `Role` | Context-dependent function performed by a voice or material | Not a permanent instrument property |
| `Material` | Reusable musical substance with identity and provenance | Broader than notes or a pattern |
| `Motif` | Recognisable musical idea capable of recurrence and transformation | May be rhythmic, pitch-based, timbral, spatial, or composite |
| `PatternDefinition` | Reusable rule or event arrangement describing a repeatable structure | Not a specific occurrence on the timeline |
| `PatternInstance` | A placed, parameterised use of a pattern definition | Has its own timing, overrides, and context |
| `Event` | Atomic or bounded timed occurrence | Not every event is a pitched note |
| `Gesture` | A shaped musical or performance action over time | Often continuous, expressive, or multidimensional |
| `HarmonyContext` | Local harmonic interpretation and pitch relationship context | Not necessarily a chord symbol |
| `TonalRegion` | A local pitch-centre, mode, tuning, or collection context | May be ambiguous or non-functional |
| `TempoMap` | Mapping between musical position and tempo behaviour | Distinct from a global BPM scalar |
| `MeterMap` | Mapping of metric organisation over musical time | Distinct from the event grid itself |
| `TuningContext` | Reference tuning and pitch interpretation rules | Distinct from note spelling |
| `Transformation` | Defined operation that derives one material or event state from another | Must retain provenance |
| `Constraint` | Testable rule or boundary that generation/editing must respect | Distinct from a preference or goal |
| `Candidate` | Proposed, not-yet-committed result | Must not overwrite accepted material |
| `DecisionRecord` | Trace of a consequential generation or editing decision | Not an assertion that the decision is artistically correct |
| `InstrumentDefinition` | Reusable sound-producing capability or template | Distinct from an instantiated part in a composition |
| `InstrumentInstance` | A configured instrument assigned to a composition context | Can reference a shared definition |
| `Patch` | Concrete configuration of synthesis or instrument parameters | May be external or only partially serialisable |
| `EffectGraph` | Directed graph of audio transformations | Distinct from the musical event graph |
| `RoutingGraph` | Connectivity between instruments, buses, sends, and outputs | Not a formal or compositional relationship |
| `AutomationLane` | Time-varying control signal with a declared target | Not inherently tied to MIDI CC |
| `RenderArtifact` | A produced audio, MIDI, notation, or package file | Derivative of the native project |

## 5. Project, composition, and document boundaries

A project is a persistence and workspace boundary. A composition is a musical work. A project may contain several compositions, drafts, alternate versions, reference materials, and render profiles.

A composition MUST have its own stable identity even when it is stored inside a larger project. It MUST NOT be identified solely by a filename or visible title.

A project may contain:

- one primary composition;
- alternate arrangements;
- movement sketches;
- candidate generations;
- reference compositions;
- sound-design studies;
- archived versions;
- export manifests.

A project file is not merely a serialized UI session. It is a durable representation of musical and production state.

## 6. Voice versus role versus instrument

These three concepts must never be collapsed into a single `Track` object.

### Voice

A voice is an independent stream of activity. It may contain pitched notes, percussion events, gestures, textures, or control events. A voice can be realised by one instrument or several sound sources.

### Role

A role describes what a voice or material is doing in a particular context. Examples include:

- pulse anchor;
- syncopated counter-rhythm;
- bass foundation;
- harmonic field;
- melodic foreground;
- motif carrier;
- transitional texture;
- high-frequency punctuation;
- background noise field;
- spectral response;
- silence or absence marker.

Roles are contextual. A voice may act as a background texture in one section and as a foreground motif in another. A voice may perform multiple roles simultaneously, but the system SHOULD represent these assignments explicitly rather than relying on an ambiguous free-text label.

### Instrument

An instrument is a sound-producing resource. One instrument can realise multiple voices; one voice can be distributed across several instruments or layers.

### Why this distinction matters

If a developer assumes one track equals one instrument equals one role, the architecture becomes too rigid for composite sounds, layered percussion, split-band basses, parallel processing, resampled motifs, or dynamic orchestration.

A good model therefore treats voice, role, and instrument as separate objects connected by explicit assignments.

## 7. Motif versus pattern versus material

These terms are related but not synonymous.

### Material

The broadest term. Material is any identifiable substance that can be reused, transformed, or related to other substance. It may be a note sequence, a rhythm, a sound object, a sample fragment, a spectral shape, an automation gesture, or a composite of these.

### Motif

A motif is a recognisable idea. Recognition may depend on contour, interval structure, rhythmic profile, timbral signature, accent placement, spectral movement, spatial trajectory, or some combination.

A motif SHOULD carry identity features describing what aspects are essential and what aspects are variable.

### Pattern definition

A pattern definition describes a repeatable temporal or generative structure. It may be:

- explicit events;
- a rule or grammar;
- a probability distribution;
- a set of constraints;
- a transformation recipe;
- an algorithm with parameters.

A pattern definition need not itself have a fixed timeline location.

### Pattern instance

A pattern instance is one use of a pattern definition. It has a start position, duration or cycle, phase, parameter values, overrides, and contextual references.

### Important consequence

The same motif may be represented by several patterns. The same pattern definition may be instantiated in several sections. A pattern instance may transform a source motif while preserving only selected identity features.

## 8. Phrase, section, and passage

A phrase is a musical unit; a section is a formal region; a passage is a temporal selection.

A phrase may be contained in a section but cross bar boundaries. A section may include several phrases, overlapping transitions, and non-phrase textures. A passage may select any range regardless of formal function.

The architecture MUST NOT define phrase boundaries solely by bar count. It SHOULD permit phrase boundaries to be proposed, edited, and evaluated independently of meter.

## 9. Event versus gesture

An event is a time-bounded occurrence. A gesture is a shaped behaviour over time.

A note-on is an event. A pitch glide with a specific envelope is a gesture. A repeated granular cloud may be a pattern of trigger events controlled by a larger density gesture. A continuous filter movement is an automation gesture.

A gesture may expand into events during rendering, but the original gesture should remain available in the project if it carries compositional meaning.

---

# Part III — Relationships and the composition graph

## 10. Why a composition is a graph, not only a tree

A tree is useful for containment: a project contains a composition, a composition contains sections, a section contains phrases. But music contains many non-hierarchical relationships.

Examples:

- Motif B is derived from motif A.
- A bass phrase answers a percussion phrase.
- Two patterns share an accent structure.
- A sound object is a timbral transformation of a melodic motif.
- A voice doubles another voice only during one passage.
- A section recalls material from a previous movement.
- A sample fragment is derived from a prior render.
- One event synchronises with a metrical layer different from the primary meter.

These relationships require a graph model.

The recommended architecture is a **typed property graph** or an equivalent relational representation with explicit edge records. The implementation need not use a graph database.

## 11. Relationship categories

Use distinct relationship types for distinct meanings.

### 11.1 Containment relationships

Examples:

- `contains`
- `belongs_to`
- `has_phrase`
- `has_event`
- `has_instance`

Containment expresses structural ownership. It should normally be acyclic.

### 11.2 Derivation relationships

Examples:

- `derived_from`
- `transformed_from`
- `resampled_from`
- `extracted_from`
- `inspired_by`

Derivation records lineage, not mere similarity.

### 11.3 Musical relationship edges

Examples:

- `answers`
- `supports`
- `contrasts_with`
- `doubles`
- `shadows`
- `interlocks_with`
- `anticipates`
- `resolves_to`
- `shares_pulse_with`
- `displaces`
- `orchestrates`
- `recontextualises`

These edges may be time-scoped. A voice can answer another voice only in a particular phrase.

### 11.4 Assignment relationships

Examples:

- `performs`
- `realised_by`
- `assigned_role`
- `routed_to`
- `controlled_by`
- `uses_patch`
- `uses_asset`

Assignment edges should record their validity interval or context when they change across the composition.

### 11.5 Reference relationships

Examples:

- `references`
- `quotes`
- `reprises`
- `alludes_to`

These indicate conceptual or musical reference. They do not necessarily imply direct derivation.

## 12. Relationship record schema

A relationship is a first-class object when it carries timing, strength, transformation, or provenance data.

```json
{
  "id": "rel_7d92a6",
  "type": "answers",
  "source_id": "phrase_perc_02",
  "target_id": "phrase_bass_02",
  "scope": {
    "composition_id": "cmp_001",
    "start_qn": { "n": 32, "d": 1 },
    "end_qn": { "n": 48, "d": 1 }
  },
  "attributes": {
    "response_delay_qn": { "n": 1, "d": 2 },
    "relationship_strength": 0.82
  },
  "created_by": "composition_director",
  "provenance_id": "prov_013"
}
```

The exact fields will vary by relationship type. A schema registry SHOULD define mandatory and optional fields for every supported edge.

## 13. Graph integrity rules

The application MUST validate:

1. Every relationship endpoint resolves to an existing entity or an explicitly external reference.
2. Containment relationships do not create illegal cycles.
3. Derivation history is acyclic unless a specialised iterative-process model explicitly permits cyclic dependency.
4. Time-scoped relationships have valid intervals.
5. Role and instrument assignments resolve to valid objects.
6. Deleting an entity does not silently leave dangling references.
7. Relationship types are registered and versioned.
8. A relationship's semantic type is not inferred only from its label text.

A composition may contain feedback-like creative relationships, but these should be represented as an iterative transformation process or dependency cycle with explicit semantics, not as an accidental reference loop.

## 14. Graph views and projections

The same canonical graph should support multiple projections:

- **Formal view:** movements, sections, phrases, transitions.
- **Timeline view:** events, pattern instances, automation, meter and tempo.
- **Material view:** motifs, patterns, transformations, lineage.
- **Orchestration view:** voices, roles, instruments, assignments.
- **Sound view:** patches, effect graphs, routing, assets.
- **Generation view:** candidates, decision records, constraints, evaluation.
- **Export view:** MIDI tracks, stems, render artifacts, manifests.

A projection is a view, not a duplicate source of truth. If a UI edits a projection, its changes MUST be translated into canonical operations against the underlying entities.

---

# Part IV — Canonical identity, metadata, and provenance

## 15. Stable identifiers

Every persistent entity MUST have a stable identifier independent of its visible name, list position, or file path.

Recommended characteristics:

- globally unique within practical project ecosystems;
- opaque to users unless a readable alias is useful;
- stable across rename and reordering;
- immutable after creation;
- references resolvable after save/load;
- compatible with import and merge workflows.

UUIDv7, UUIDv4, ULID, or another suitably unique identifier scheme may be used. The chosen representation must be documented. Do not use array indices as persistent identifiers.

### 15.1 Internal ID versus external alias

Use an internal immutable ID and optional readable aliases.

```json
{
  "id": "0194b7d2-3a0a-7d2d-9e31-a9cb79bfe321",
  "alias": "motif_glass_01",
  "name": "Glass Motif"
}
```

The alias may change. The ID must not.

### 15.2 Logical identity versus revision identity

A persistent entity may have multiple revisions. Keep the logical entity ID stable and assign distinct revision IDs or version references to immutable snapshots.

This supports:

- undo/redo;
- candidate comparison;
- branch-based exploration;
- historical reconstruction;
- safe collaboration;
- reproducible rendering.

## 16. Common entity envelope

All persistent entities SHOULD follow a common metadata envelope.

```json
{
  "id": "entity_001",
  "entity_type": "motif",
  "schema_version": "1.0.0",
  "name": "Glass Motif",
  "created_at": "2026-11-26T18:30:00Z",
  "updated_at": "2026-11-26T18:45:00Z",
  "created_by": {
    "kind": "generator",
    "id": "motif_generator_v3"
  },
  "revision": 4,
  "status": "accepted",
  "tags": ["metallic", "syncopated", "short-cell"],
  "metadata": {},
  "provenance_id": "prov_001"
}
```

The common envelope should remain small. Domain-specific data belongs in typed payloads, not in a giant universal object with hundreds of optional fields.

## 17. Provenance model

Provenance records how an object came into existence and how it changed.

A provenance record SHOULD capture:

- source entities;
- transformation or generator operation;
- algorithm and version;
- configuration and parameters;
- random seed and random-stream identity where relevant;
- software build or commit identifier;
- timestamp;
- user or subsystem responsible;
- parent revision;
- decision record;
- asset hashes if external data was involved.

Example:

```json
{
  "id": "prov_001",
  "operation": "rhythmic_displacement",
  "operation_version": "2.1.0",
  "inputs": ["motif_001"],
  "parameters": {
    "displacement_qn": { "n": 1, "d": 8 },
    "preserve_anchor_events": true,
    "affected_event_ids": ["evt_12", "evt_18"]
  },
  "randomness": {
    "mode": "deterministic",
    "seed": 42017,
    "stream_id": "rhythm_mutation_03"
  },
  "software": {
    "application_version": "0.9.0",
    "build_id": "git:8f9b3d1"
  },
  "parent_revisions": ["rev_motif_001_3"]
}
```

Provenance MUST describe actual inputs and operations. It MUST NOT invent an explanation after the fact to make an opaque generation seem intentional.

## 18. Stable material identity

Material identity is multidimensional. A motif may remain recognisable while its notes, timing, register, instrumentation, or sound source change.

A material identity profile SHOULD allow feature dimensions such as:

- rhythmic contour;
- interval contour;
- pitch-class or scale-degree profile;
- accent structure;
- phrase position;
- duration ratios;
- timbral descriptors;
- spectral envelope;
- transient profile;
- spatial behaviour;
- articulation pattern;
- relation to other material.

The system SHOULD distinguish:

- **invariants:** features that define identity and must remain stable;
- **soft identity features:** features that may change within a budget;
- **free dimensions:** features that may change without threatening identity;
- **contextual features:** features that matter only in a particular section or role.

Do not define motif identity through a single similarity score. A scalar may be useful for ranking candidates, but identity decisions must retain feature-level evidence and allow human review.

---

# Part V — Musical time, meter, tempo, and event coordinates

## 19. Time is a first-class domain, not a display convention

A generative composition system must represent time precisely enough to support:

- tuplets and nested subdivisions;
- swing and microtiming;
- tempo changes;
- meter changes;
- polymeter and phase relationships;
- events crossing bar lines;
- looped and non-looped structures;
- sample-accurate rendering;
- interchange with MIDI and audio systems.

Storing only `bar`, `beat`, and `sixteenth` is insufficient. Storing only floating-point seconds is also insufficient.

The canonical model SHOULD use an exact rational musical coordinate as its primary score time, then derive display labels and audio time through maps.

## 20. Canonical musical position: quarter-note units

Use **quarter-note units (QN)** as the canonical musical duration coordinate unless the application has a well-documented alternative.

A position is a rational value:

```json
{ "n": 13, "d": 8 }
```

This means 13/8 quarter-note units.

A duration is also rational:

```json
{ "n": 3, "d": 16 }
```

This means 3/16 of a quarter-note unit.

Rational storage avoids cumulative floating-point drift when events are repeatedly transformed, quantised, displaced, or composed across nested tuplets.

An implementation MAY store a reduced numerator and denominator in memory. It SHOULD normalise fractions to their lowest terms for canonical serialization.

### 20.1 Why use a rational representation?

For example, a tupletted event at 1/3 of a beat cannot be represented exactly by many binary floating-point formats. Repeated calculations can produce values that drift slightly away from the intended grid. Rational arithmetic preserves exact relationships until conversion to sample time is required.

### 20.2 Internal precision and limits

A production system MUST define maximum numerator and denominator sizes, overflow behaviour, and a fallback for pathological denominators. It MUST NOT silently round a rational value because it exceeds a storage limit. A rounding operation must be explicit and recorded.

## 21. Tempo map

A tempo map describes the relationship between musical position and elapsed time.

A tempo event should include:

- start position in QN;
- tempo value;
- tempo beat unit;
- interpolation mode to the next event, if any;
- optional curve parameters;
- source or editing provenance.

Example:

```json
{
  "id": "tempo_map_001",
  "unit": "quarter_note",
  "events": [
    {
      "at_qn": { "n": 0, "d": 1 },
      "bpm": 92.0,
      "interpolation_to_next": "constant"
    },
    {
      "at_qn": { "n": 64, "d": 1 },
      "bpm": 96.0,
      "interpolation_to_next": "linear"
    },
    {
      "at_qn": { "n": 96, "d": 1 },
      "bpm": 88.0,
      "interpolation_to_next": "constant"
    }
  ]
}
```

A tempo value without a beat unit is ambiguous. A tempo of 120 beats per minute may refer to quarter notes, dotted quarters, half notes, or another unit. The model must state the beat unit.

### 21.1 Mapping QN to seconds

For a constant quarter-note tempo `B`, a QN distance `q` maps to:

\[
 t = q \cdot \frac{60}{B}
\]

For a variable tempo curve `B(q)`, elapsed time is:

\[
 t(q) = \int_0^q \frac{60}{B(u)}\,du
\]

A tempo map implementation MUST define how interpolation is evaluated and how the inverse mapping from seconds to QN is calculated.

### 21.2 Tempo map requirements

- Tempo events must be ordered and unambiguous.
- Interpolation must be explicit.
- Discontinuities must be supported when musically intended.
- Curves must be numerically stable and bounded.
- Conversion routines must be deterministic within the declared precision.
- Rendering must use the same tempo map semantics as preview playback.

## 22. Meter map and metric layers

Meter is not identical to event-grid resolution. A composition can use a conventional meter, an additive meter, a changing meter, or several concurrent metric layers.

A meter event SHOULD include:

- start QN;
- numerator and denominator;
- beat grouping (for example 3+2+2);
- beat unit;
- bar numbering policy;
- optional display label.

Example:

```json
{
  "id": "meter_map_001",
  "events": [
    {
      "at_qn": { "n": 0, "d": 1 },
      "numerator": 7,
      "denominator": 8,
      "grouping": [2, 2, 3]
    },
    {
      "at_qn": { "n": 28, "d": 1 },
      "numerator": 4,
      "denominator": 4,
      "grouping": [2, 2]
    }
  ]
}
```

The meter map controls bar and beat interpretation. It does not require every event to align with a beat or bar.

### 22.1 Polymeter

A composition may contain multiple `MetricLayer` objects. Each layer defines its own cycle length, phase origin, grouping, and interpretation of accents.

A polymetric relationship should be represented as a relationship between metric layers or patterns, not flattened into one misleading time signature.

### 22.2 Bar and beat labels are derived

Bar numbers, beat numbers, and subdivision labels should be calculated from the meter map. They should not be the only stored position representation because meter changes can make the labels ambiguous or mutable.

## 23. Swing, groove, and microtiming

Swing and groove are not necessarily properties of a single note. They may be properties of a pattern, a voice, a metric layer, a performance template, or a local transformation.

The architecture should distinguish:

- score position;
- intended grid position;
- performed position;
- rendered sample position.

A groove transformation may map a straight score coordinate to a performed coordinate. That mapping should be explicit and non-destructive.

Example:

```json
{
  "id": "groove_001",
  "type": "subdivision_warp",
  "scope": "pattern_instance_001",
  "grid_unit_qn": { "n": 1, "d": 2 },
  "mapping": "long_short",
  "ratio": 0.61,
  "strength": 0.75,
  "preserve_anchor_events": true
}
```

Microtiming should be represented as a precise offset in QN, a performed-time offset, or an explicitly defined timing warp. Avoid ambiguous fields such as `humanize: 0.2` without units, scope, and interpretation.

## 24. Multiple time domains

The project should distinguish at least these time domains:

| Domain | Purpose |
|---|---|
| Musical QN | Canonical score and composition position |
| Metric position | Bar, beat, grouping, and cycle interpretation |
| Performed time | Groove, timing deviation, rubato, and performance offset |
| Wall-clock/audio seconds | Playback and render scheduling |
| Sample position | Exact audio-buffer and sample-frame location |
| Asset time | Position within a sample or recorded source |

Conversions between domains must be explicit. A sample slice position is not a score QN position. A bar/beat label is not a sample offset.

## 25. Event ordering

Events may share a position. The system must define deterministic ordering for simultaneous events where order changes execution.

A recommended canonical sort key is:

1. start QN;
2. event phase or execution priority;
3. event type priority where required;
4. stable event ID.

For same-position note-off and note-on pairs, the chosen ordering policy must avoid stuck notes and unintended overlap. The policy should be instrument-aware where necessary and documented in the playback adapter.

Do not assume that sorting by floating-point seconds alone is sufficient.

---

# Part VI — Pitch, harmony, tuning, and non-pitched material

## 26. Pitch is not merely a MIDI note number

A MIDI note number is a useful interchange value, but it does not contain every relevant aspect of pitch.

The internal pitch model should separate:

- sounding pitch;
- pitch spelling or notation identity;
- pitch-class identity;
- scale-degree identity within a context;
- tuning reference;
- deviation from equal temperament;
- pitch trajectory over time.

A note may have a sounding pitch but no conventional note spelling. A spectral or percussive event may have several resonant frequencies rather than one pitch.

## 27. Recommended pitch object

```json
{
  "absolute_pitch": {
    "reference": "C0_equal_temperament",
    "cents": 6900.0
  },
  "spelling": {
    "step": "A",
    "alteration_semitones": 0,
    "octave": 4
  },
  "contextual_pitch": {
    "scale_degree": 6,
    "chromatic_offset_cents": 0
  },
  "tuning_context_id": "tuning_12tet_440"
}
```

The exact reference convention is an implementation decision, but it must be globally documented and consistent.

## 28. Tuning context

A `TuningContext` should describe:

- reference frequency;
- reference pitch;
- tuning system;
- period ratio;
- division or scale definition where relevant;
- mapping from symbolic pitch to sounding frequency;
- whether deviations are fixed or context-dependent.

The system SHOULD support 12-tone equal temperament as a common default without hard-coding it as the only possible tuning system.

## 29. Harmony context

Harmony should be represented contextually rather than forcing all material into chord symbols.

A `HarmonyContext` may define:

- pitch collection;
- tonal centre or ambiguous centre;
- chord or sonority interpretation;
- bass reference;
- functional interpretation if applicable;
- modal or non-functional characteristics;
- harmonic tension descriptors;
- validity interval;
- confidence or ambiguity metadata.

A harmonic context may be absent, plural, unstable, or intentionally contradictory.

## 30. Non-pitched and multi-pitched sound events

The event model must support events whose musical identity is not a single note:

- unpitched percussion;
- metallic resonances;
- noise bursts;
- granular clouds;
- sample triggers;
- multi-partial resonant events;
- spectral gestures;
- texture beds;
- field-recording fragments.

An event may contain optional pitch features, spectral features, or a reference to a sound object. It must not be forced into a pitch-only schema.

---

# Part VII — Patterns, motifs, events, and performance representation

## 31. Event base model

An event is a time-bounded or instantaneous occurrence with a stable ID, a type, timing, and a typed payload.

```json
{
  "id": "evt_001",
  "event_type": "note",
  "start_qn": { "n": 9, "d": 8 },
  "duration_qn": { "n": 1, "d": 4 },
  "voice_id": "voice_lead_01",
  "role_assignments": ["role_foreground_motif"],
  "payload": {
    "pitch": {
      "absolute_pitch": {
        "reference": "C0_equal_temperament",
        "cents": 6900.0
      }
    },
    "velocity": 0.72,
    "articulation": "staccato"
  },
  "provenance_id": "prov_note_001"
}
```

The base model should not grow into a universal object with dozens of unrelated nullable properties. Use typed event payloads.

## 32. Recommended event types

A useful initial event registry includes:

| Type | Purpose | Example payload |
|---|---|---|
| `note` | Pitched note event | Pitch, duration, velocity, articulation |
| `trigger` | Trigger a sample, instrument, or sound object | Asset or instrument reference, velocity, slice |
| `percussion_hit` | Unpitched or partly pitched percussion event | Instrument key, intensity, articulation |
| `control` | Discrete control change | Parameter ID, value |
| `automation_point` | Control value at a position | Target, value, interpolation |
| `gesture` | Continuous or shaped action | Curve, dimensions, duration |
| `rest` | Explicit absence or rest when semantically important | Scope, duration, type |
| `marker` | Structural or navigational point | Marker type, label |
| `sample_slice` | Trigger a region within an audio asset | Asset ID, source range, playback mode |
| `spectral_event` | Event defined partly by spectral state | Partial set, envelope, analysis reference |
| `texture_event` | Start/stop or shape a sustained texture | Texture source, density, evolution |
| `tempo_event` | Change the tempo map | BPM, unit, curve |
| `meter_event` | Change metric interpretation | Numerator, denominator, grouping |

Implementations MAY introduce new types through a registry. Unknown event types must be preserved by compatible readers as opaque typed payloads where possible, rather than discarded.

## 33. Note event semantics

A note event should include:

- start position;
- sounding pitch or pitch trajectory;
- nominal duration;
- velocity or excitation intensity;
- articulation;
- channel or performance expression only where relevant;
- optional note-level expression;
- voice reference;
- provenance.

A note's nominal duration is not always identical to its audible duration. A synthesizer release envelope, sample tail, pedal, reverb, or effect may extend sound beyond note-off. Score duration and rendered duration must remain distinct.

Velocity is not a universal loudness unit. It is an expressive control whose interpretation belongs to the instrument mapping.

## 34. Pattern definition and pattern instance

A `PatternDefinition` is reusable and context-independent as far as practical. A `PatternInstance` gives it a location, phase, parameterisation, and local context.

### Pattern definition example

```json
{
  "id": "pattern_def_odd_07",
  "entity_type": "pattern_definition",
  "name": "Seven-step metallic cycle",
  "pattern_kind": "event_sequence",
  "cycle_duration_qn": { "n": 7, "d": 4 },
  "events": [
    { "id": "pe_1", "offset_qn": { "n": 0, "d": 1 }, "type": "trigger", "key": "metal_a", "velocity": 0.82 },
    { "id": "pe_2", "offset_qn": { "n": 3, "d": 4 }, "type": "trigger", "key": "metal_b", "velocity": 0.56 },
    { "id": "pe_3", "offset_qn": { "n": 5, "d": 4 }, "type": "trigger", "key": "metal_a", "velocity": 0.71 }
  ],
  "identity_profile": {
    "preserve": ["cycle_length", "accent_order"],
    "flexible": ["velocity", "timbre_key", "microtiming"]
  }
}
```

### Pattern instance example

```json
{
  "id": "pattern_inst_031",
  "pattern_definition_id": "pattern_def_odd_07",
  "start_qn": { "n": 24, "d": 1 },
  "repeat_count": 4,
  "phase_offset_qn": { "n": 1, "d": 8 },
  "voice_id": "voice_metal_01",
  "overrides": {
    "velocity_scale": 0.88,
    "timbre_key_map": {
      "metal_a": "metal_glass_02"
    }
  },
  "section_id": "section_b"
}
```

## 35. Pattern representation modes

The architecture should support multiple pattern representations:

1. **Explicit event pattern:** stores events directly.
2. **Rule pattern:** generates events by applying a set of rules.
3. **Probabilistic pattern:** describes distributions or conditional probabilities.
4. **Constraint pattern:** defines valid event relationships without fixing all events.
5. **Hybrid pattern:** combines explicit anchors with generative regions.
6. **Gesture pattern:** defines continuous or multidimensional motion.

A pattern definition should declare its representation mode, supported parameters, cycle behaviour, deterministic requirements, and expansion rules.

## 36. Repetition and pattern expansion

A pattern instance may be expanded into concrete events for playback, editing, or export. Expansion should not destroy the source pattern definition or instance.

The system should distinguish:

- source pattern;
- instance parameters;
- expanded event cache;
- manually edited expanded events;
- committed overrides.

If the source pattern changes, the system must know whether the instance should update, remain frozen, or become detached. This is a dependency-management decision, not an accidental side effect.

## 37. Voice and role assignment model

A `Voice` describes an independent stream. A `RoleAssignment` associates a voice or material with a function over a time range.

```json
{
  "id": "role_assign_014",
  "target_id": "voice_metal_01",
  "role_id": "role_rhythmic_counterline",
  "scope": {
    "start_qn": { "n": 24, "d": 1 },
    "end_qn": { "n": 52, "d": 1 }
  },
  "priority": "primary",
  "attributes": {
    "attention_level": 0.64,
    "density_budget": "medium"
  }
}
```

Role taxonomies should be extensible. The core schema should not require every project to use a fixed list of IDM-specific role names.

---

# Part VIII — Constraints, artistic intent, and mutation contracts as data

## 38. CompositionBrief data model

A CompositionBrief is a structured request for a composition. It should contain semantic fields rather than a single prompt string alone.

Recommended dimensions:

- intent statement;
- listening experience;
- emotional or perceptual trajectory;
- material vocabulary;
- rhythmic behaviour;
- pitch and harmony behaviour;
- structural tendencies;
- sound identity;
- density and attention expectations;
- duration and delivery;
- constraints;
- exclusions;
- unresolved questions.

The brief may contain prose, but prose should be supplemented with structured fields where the system must make reliable decisions.

### CompositionBrief example

```json
{
  "id": "brief_001",
  "schema_version": "1.0.0",
  "intent": {
    "summary": "A restless but restrained electronic composition built from fragile rhythmic objects.",
    "listener_experience": ["uneasy", "intimate", "gradually opening"],
    "avoid": ["festival-drop structure", "constant maximal density"]
  },
  "form": {
    "preferred_models": ["gradual_accumulation", "fragment_return"],
    "duration_seconds_target": 240,
    "allow_asymmetrical_sections": true
  },
  "rhythm": {
    "complexity_preference": 0.78,
    "groove_character": ["uneven", "interlocking", "microtimed"],
    "permitted_meter_changes": true
  },
  "pitch": {
    "harmonic_character": ["modal", "ambiguous", "small-pitch-field"],
    "tuning_context_id": "tuning_12tet_440"
  },
  "sound": {
    "material_vocabulary": ["metallic", "granular", "soft-transient", "field-recording"],
    "spatial_character": ["close", "diffuse", "selectively-wide"]
  },
  "constraints": [
    { "id": "c_01", "kind": "hard", "target": "project.render.sample_rate", "operator": "equals", "value": 48000 },
    { "id": "c_02", "kind": "soft", "target": "composition.rhythmic_density", "operator": "prefer_range", "value": [0.25, 0.72] }
  ]
}
```

A number such as `complexity_preference: 0.78` must have a documented scale and meaning. If no common calibration exists, store it as a qualitative preference or a structured profile rather than pretending it is an objective universal quantity.

## 39. Constraints, preferences, and goals

These concepts must be distinct.

### Hard constraint

A condition that must be satisfied for an operation or candidate to be valid.

### Soft constraint / preference

A condition that should be favoured but may be violated with a recorded trade-off.

### Goal

A desired result that may be approached through several different musical solutions.

### Exclusion

A prohibited result or transformation.

### Invariant

A property that must remain unchanged during a specified operation or scope.

Each constraint should declare:

- target scope;
- predicate or evaluation function;
- severity;
- owner;
- evaluation phase;
- failure behaviour;
- whether override is allowed;
- override reason requirements.

## 40. Constraint example

```json
{
  "id": "constraint_freeze_kick_anchor",
  "kind": "invariant",
  "scope": {
    "entity_ids": ["pattern_inst_kick_01"],
    "start_qn": { "n": 0, "d": 1 },
    "end_qn": { "n": 64, "d": 1 }
  },
  "predicate": {
    "type": "event_onset_set_equal",
    "event_filter": { "voice_id": "voice_kick" }
  },
  "owner": "mutation_engine",
  "override_policy": "requires_explicit_user_approval"
}
```

## 41. MutationContract

A mutation contract declares what an operation is allowed to change, what it must preserve, what dependencies it may affect, and how its result will be evaluated.

Recommended fields:

- target entity or region;
- operation name and version;
- permitted dimensions;
- protected dimensions;
- scope and boundaries;
- dependency impact policy;
- allowed deviation or mutation budget;
- candidate-generation count;
- deterministic seed policy;
- evaluation requirements;
- commit policy;
- rollback information.

Example:

```json
{
  "id": "mutation_023",
  "operation": "increase_rhythmic_unpredictability",
  "version": "1.2.0",
  "target": "pattern_inst_031",
  "scope": {
    "start_qn": { "n": 24, "d": 1 },
    "end_qn": { "n": 52, "d": 1 }
  },
  "may_change": ["event_offsets", "accent_weights", "ornament_events"],
  "must_preserve": ["cycle_length", "anchor_event_ids", "voice_assignment"],
  "mutation_budget": {
    "max_onset_shift_qn": { "n": 1, "d": 8 },
    "max_added_events_ratio": 0.18
  },
  "dependency_policy": "do_not_mutate_dependents_without_approval",
  "candidate_policy": {
    "count": 8,
    "commit_automatically": false
  },
  "evaluation": ["identity_coherence", "rhythmic_contrast", "density_budget"]
}
```

## 42. Mutation is transactional

A mutation must not overwrite accepted material as it is being computed.

Recommended lifecycle:

1. Read a stable source revision.
2. Validate the mutation contract.
3. Build candidate revisions.
4. Validate schema and hard constraints.
5. Evaluate musical and technical consequences.
6. Present candidates or select according to an explicit policy.
7. Commit the selected revision atomically.
8. Record lineage and decision evidence.
9. Preserve rollback capability.

This is a data-integrity requirement as much as a user-experience requirement.

---

# Part IX — Sound realisation, instruments, automation, and routing

## 43. Keep musical score and sound realisation separate

A note or pattern should not contain a hard-coded plugin implementation as its only meaning.

The musical event says what happens. The sound-realisation layer says how it is produced.

The same musical phrase may be realised by:

- a synthesizer;
- a sample instrument;
- a physical-modelled resonator;
- a layered hybrid patch;
- an external plugin;
- a rendered audio fragment;
- several parallel sound sources.

Conversely, the same instrument may realise multiple voices or roles.

## 44. Instrument definition versus instrument instance

An `InstrumentDefinition` describes reusable capabilities and default mappings. An `InstrumentInstance` is the configured use of that instrument in a composition.

The definition may contain:

- supported event types;
- parameter definitions;
- note and trigger mapping;
- pitch range;
- polyphony capabilities;
- expression capabilities;
- supported tuning behaviour;
- default patch or asset references;
- latency characteristics.

The instance may contain:

- instrument definition reference;
- patch reference;
- local parameter overrides;
- voice assignments;
- routing assignments;
- instrument-specific automation mappings;
- state snapshot or external plugin state reference.

## 45. Semantic parameter model

Do not expose every plugin parameter directly as a compositional control.

A parameter definition should distinguish:

- semantic identity;
- native implementation parameter;
- unit and range;
- normalisation curve;
- scope;
- interpolation mode;
- modulation capability;
- default value;
- capability constraints.

Example:

```json
{
  "id": "semantic_filter_brightness",
  "label": "Brightness",
  "unit": "normalised",
  "range": { "min": 0.0, "max": 1.0 },
  "mapping": {
    "kind": "log_frequency",
    "native_parameter": "cutoff_hz",
    "native_range": [80.0, 16000.0]
  },
  "smoothing": {
    "kind": "one_pole",
    "time_ms": 12
  }
}
```

A semantic macro such as `brightness` may bind to several native controls across different instruments. The mapping belongs to the realisation layer, not the motif or score layer.

## 46. Automation lanes

An automation lane defines a time-varying control signal. It should include:

- target parameter ID;
- scope;
- time domain;
- curve representation;
- interpolation mode;
- value units;
- minimum and maximum bounds;
- precedence rules;
- source and provenance.

Possible curve representations:

- discrete points;
- linear segments;
- cubic or Bezier curves;
- step sequences;
- periodic LFO description;
- stochastic or bounded random process;
- data-driven envelope;
- gesture capture.

Automation should not be limited to raw MIDI CC values.

## 47. Effect graph

An effect graph is a directed audio-processing graph. It should describe nodes, edges, parameter states, channel formats, latency, and feedback semantics.

The architecture must support:

- serial chains;
- parallel branches;
- multiband splits and merges;
- send/return networks;
- sidechain relationships;
- feedback networks;
- instrument-level and bus-level processing;
- external plugin nodes;
- bypass and dry/wet states.

The graph must distinguish a valid feedback network with explicit delay/stability handling from an accidental zero-delay cycle.

## 48. Routing graph

A routing graph describes signal connectivity. It is independent of musical derivation and section hierarchy.

A source may route to multiple destinations. A bus may aggregate several sources. A sidechain route may affect processing without carrying audible output.

Routing edges should identify:

- source port;
- destination port;
- channel map;
- gain or send level;
- route type;
- latency compensation requirement;
- activation scope if routing varies over time.

## 49. External instruments and opaque state

Some plugin state cannot be represented as portable semantic parameters. The system may need to store an opaque state blob or external preset reference.

It MUST record:

- plugin identifier;
- plugin format and version where known;
- manufacturer and plugin name;
- binary or state hash;
- parameter mapping version;
- missing-plugin fallback behaviour;
- portability status.

An unavailable plugin must not silently be replaced by a different instrument without notifying the user. The project should preserve the original state and provide a missing-dependency diagnostic.

---

# Part X — Data architecture, persistence, and project packages

## 50. Recommended storage architecture

A single JSON file is easy to inspect but may become inefficient for large event collections, sample libraries, waveform caches, and audio assets. A rigid relational schema can be efficient but may slow experimentation with new musical entity types.

A hybrid model is recommended:

1. **Manifest and metadata:** readable structured document.
2. **Canonical entities:** JSON, relational rows, or equivalent typed records.
3. **High-volume event data:** indexed event tables or binary blocks with stable IDs.
4. **Assets:** external files stored by path and content hash.
5. **Caches:** disposable derived data.
6. **History:** append-only decisions, operations, revisions, and provenance records.
7. **Schemas and migrations:** versioned alongside the project format.

The exact storage engine is an implementation choice. The canonical semantics are not.

## 51. Project package layout

One possible package structure:

```text
my_composition.idmproj/
├── manifest.json
├── project.json
├── compositions/
│   └── main/
│       ├── composition.json
│       ├── structure.json
│       ├── materials.json
│       ├── voices.json
│       ├── events/
│       │   ├── percussion.events
│       │   ├── bass.events
│       │   └── textures.events
│       ├── instruments.json
│       ├── automation.json
│       ├── routing.json
│       └── constraints.json
├── history/
│   ├── decisions.jsonl
│   ├── mutations.jsonl
│   └── revisions.jsonl
├── schemas/
│   ├── project.schema.json
│   ├── composition.schema.json
│   └── event.schema.json
├── assets/
│   ├── samples/
│   ├── impulses/
│   ├── patches/
│   └── external-state/
├── cache/
│   ├── previews/
│   ├── waveforms/
│   └── analysis/
└── exports/
    ├── audio/
    ├── stems/
    ├── midi/
    └── manifests/
```

This is illustrative. A production project may use a database file or compressed archive. Cache and export folders may be external. The package contract should state what is required to reconstruct the composition and what may be safely deleted.

## 52. Required versus derived data

Classify project data:

### Required source data

- composition and entity records;
- event data or canonical pattern source;
- tempo and meter maps;
- material lineage;
- sound-realisation configuration required for faithful reconstruction;
- asset references and content hashes;
- constraints and committed decisions;
- schema versions.

### Reconstructable derived data

- waveform thumbnails;
- visual timeline caches;
- expanded pattern event caches;
- analysis features;
- temporary preview renders;
- cached graph layouts.

### Optional archival data

- candidate generations;
- decision explanations;
- intermediate audio renders;
- human evaluation notes;
- external references.

The project manifest must identify which category applies to each data group.

## 53. Asset references and content addressing

An asset reference should not depend only on an absolute filesystem path.

Recommended fields:

- asset ID;
- relative path or URI;
- content hash;
- media type;
- sample rate and channel count where relevant;
- frame count or duration;
- import metadata;
- license or provenance metadata where applicable;
- missing-asset policy.

Content hashes can detect silent asset replacement and support deduplication. A path may change while the asset identity remains stable.

## 54. Atomic save and recovery

Saving must be transactional or recoverable. Avoid overwriting the only valid project state before a new state is fully written and validated.

Recommended sequence:

1. Create a new snapshot or temporary write target.
2. Write entity data and assets metadata.
3. Write manifest and schema version.
4. Validate references and integrity.
5. Flush and close files.
6. Atomically replace the previous snapshot or commit a transaction.
7. Preserve recovery metadata.

The application should detect incomplete writes and provide recovery options rather than silently opening a partial state.

---

# Part XI — Serialization, interchange, and adapters

## 55. Native format versus interchange formats

No single interchange format captures every concern in this architecture.

The native model is the complete source of truth. Interchange formats are adapters, each with a defined fidelity boundary.

### MIDI 1.0 / Standard MIDI Files

Useful for timed note and controller interchange, instrument trigger sequences, and compatibility with a wide ecosystem. It does not natively encode the full composition graph, rich motif lineage, arbitrary semantic roles, all instrument states, or the entire project ontology.

### MIDI 2.0

Extends MIDI 1.0's protocol model. It offers increased resolution and richer per-note control, while the MIDI Association describes MIDI 2.0 as an extension rather than a replacement for MIDI 1.0. The architecture should keep MIDI 1.0 interoperability and provide MIDI 2.0 capabilities through an adapter where supported. See the [MIDI Association's MIDI 2.0 overview](https://midi.org/midi-2-0) and [UMP / MIDI 2.0 Protocol specification page](https://midi.org/universal-midi-packet-ump-and-midi-2-0-protocol-specification).

### MusicXML

Useful for exchanging notated scores and parts. It is designed for digital sheet-music interchange, not as a complete representation of arbitrary sound-design graphs, generative provenance, or a DAW production state. Consult the [MusicXML 4.0 reference](https://www.w3.org/2021/06/musicxml40/) and its schema resources.

### OSC

Useful for runtime communication among applications, controllers, synthesizers, and multimedia systems. It is a message protocol, not a persistent composition database. See the [Open Sound Control 1.0 specification](https://github.com/CNMAT/OpenSoundControl.org/blob/master/spec-1_0.md).

### Audio files

WAV, AIFF, FLAC, and other audio formats preserve rendered sound, not the complete editable structure that produced it. Store render settings and source project revision in the render manifest.

## 56. Interchange fidelity report

Every importer and exporter should produce a fidelity report.

Example:

```json
{
  "format": "standard_midi_file",
  "direction": "export",
  "source_revision": "rev_0042",
  "preserved": [
    "note_events",
    "tempo_map",
    "meter_map",
    "basic_controller_events"
  ],
  "approximated": [
    "microtiming_resolution",
    "per_note_expression"
  ],
  "omitted": [
    "motif_lineage",
    "composition_roles",
    "effect_graph",
    "candidate_history"
  ],
  "warnings": [
    "Some semantic relationships cannot be represented in Standard MIDI Files."
  ]
}
```

An exporter must never imply that a lossy conversion preserved all information.

## 57. Import strategy

Importers should:

1. Preserve original source metadata.
2. Parse into a temporary import model.
3. Validate source structure.
4. Map supported concepts into canonical entities.
5. retain unsupported data as opaque metadata where feasible;
6. record approximations and omissions;
7. allow preview before committing;
8. commit as a new revision or imported composition.

Do not destructively merge imported material into the active composition without a preview and explicit mapping policy.

## 58. Export strategy

Exporters should operate on a stable composition snapshot. They should declare their target format, export profile, fidelity limitations, and conversion choices.

Exports must not mutate the source composition. If export requires transformations, those transformations belong to a temporary export projection or derived snapshot.

---

# Part XII — Query, editing, and subsystem APIs

## 59. Architecture by commands and queries

Separate operations that change the project from operations that inspect it.

### Commands

Examples:

- `CreateComposition`
- `AddSection`
- `CreateMotif`
- `InstantiatePattern`
- `ApplyTransformation`
- `AssignRole`
- `SetTempoMap`
- `FreezeRegion`
- `CommitCandidate`
- `RenderComposition`

Commands should declare intent and required inputs. They should return a result, validation report, or structured failure.

### Queries

Examples:

- `GetCompositionGraph`
- `GetTimelineRange`
- `FindMaterialDependents`
- `GetPhraseLineage`
- `GetRoleAssignments`
- `GetRenderDependencies`
- `GetCandidateComparison`

Queries should not mutate project state.

## 60. Command contract

Every consequential command should include:

- command ID;
- target entity IDs;
- source revision or expected revision;
- operation and version;
- parameters;
- constraints;
- actor (user or subsystem);
- idempotency key where needed;
- transaction scope.

It should return:

- success or failure status;
- created or changed entity IDs;
- new revision ID;
- validation report;
- provenance ID;
- warnings;
- rollback or undo reference.

## 61. Example command: instantiate pattern

```json
{
  "command": "InstantiatePattern",
  "command_id": "cmd_0101",
  "expected_project_revision": 42,
  "payload": {
    "pattern_definition_id": "pattern_def_odd_07",
    "start_qn": { "n": 24, "d": 1 },
    "repeat_count": 4,
    "voice_id": "voice_metal_01",
    "section_id": "section_b",
    "phase_offset_qn": { "n": 1, "d": 8 }
  },
  "policy": {
    "preserve_source_definition": true,
    "create_candidate": false
  }
}
```

## 62. Example query: find dependents before mutation

```json
{
  "query": "FindMaterialDependents",
  "payload": {
    "entity_id": "motif_001",
    "relationship_types": [
      "derived_from",
      "transformed_from",
      "instantiates"
    ],
    "include_time_scopes": true,
    "include_frozen_entities": true
  }
}
```

This query allows the mutation system to determine whether a change has consequences beyond the target entity.

## 63. Subsystem interface contracts

The following subsystem responsibilities follow the constitution. The exact module names may differ.

| Subsystem | Inputs | Outputs | Must not own |
|---|---|---|---|
| Brief Interpreter | CompositionBrief, project context | Intent model, constraints, unresolved questions | Final event data |
| Composition Director | Intent, identity, global constraints | Formal plan, high-level decisions | Sample-accurate playback |
| Structure Planner | Formal plan, materials, duration | Movements, sections, phrases, transitions | Plugin state |
| Material Manager | Motifs, patterns, lineage | Material records and dependency graph | Audio routing |
| Generator Services | Constraints, source material, context | Candidate material or events | Automatic commitment of candidates |
| Orchestrator | Voices, roles, instruments, perceptual goals | Assignments and attention plan | Rewriting source motifs silently |
| Sound Realiser | Events, instruments, patches | Sound configuration and renderable signal graph | Formal structure |
| Evaluator | Candidate/project snapshots, test profiles | Evidence, metrics, diagnostics | Silent destructive edits |
| Mutation Engine | Target, contract, constraints | Candidate revisions | Unapproved dependent mutation |
| Renderer | Stable snapshot, render profile | Audio and render manifest | Changing score semantics |
| Creative Interface | Project state and command API | User actions and views | Owning canonical data |

## 64. Event-driven updates

Subsystems may publish domain events when project state changes.

Examples:

- `CompositionCreated`
- `SectionCommitted`
- `MaterialDerived`
- `PatternInstantiated`
- `MutationCandidateCreated`
- `CandidateCommitted`
- `ConstraintViolated`
- `InstrumentMissing`
- `RenderCompleted`

An event should describe a committed fact, not a future intention. For example, `CandidateRequested` is a command or request; `CandidateCreated` is a fact after creation succeeds.

Consumers should be idempotent where possible. Duplicate delivery must not duplicate committed musical entities.

---

# Part XIII — Validation, evaluation boundaries, and error semantics

## 65. Validation is layered

A single `is_valid` Boolean is insufficient. The project should have distinct validation levels.

### Level 1 — Schema validation

Are required fields present? Are types, ranges, and enumerations valid?

### Level 2 — Referential validation

Do referenced entities, assets, instruments, and relationships exist?

### Level 3 — Structural validation

Is the containment graph valid? Are section boundaries coherent? Are required parent relationships present?

### Level 4 — Temporal validation

Are event durations valid? Are rational positions legal? Are tempo and meter maps consistent? Are automation intervals and pattern cycles well-defined?

### Level 5 — Musical contract validation

Do hard constraints and mutation invariants hold? Has protected material changed? Are declared role and relationship requirements satisfied?

### Level 6 — Realisation validation

Are instrument mappings valid? Are patch parameters supported? Are routing graphs executable? Are feedback paths safe according to engine rules?

### Level 7 — Render validation

Can the project be rendered? Are stems synchronised? Are output formats valid? Are assets available?

### Level 8 — Perceptual and artistic evaluation

Does the result meet stated goals? Is it intelligible, coherent, compelling, or intentionally ambiguous? This is not the same as schema validity.

## 66. Validation report

A validation report should include:

- project and revision IDs;
- validation profile and version;
- level and severity;
- issue code;
- affected entity IDs;
- concise explanation;
- evidence or measured values;
- suggested repair where appropriate;
- whether the issue blocks an operation.

Example:

```json
{
  "report_id": "validation_2026_11_26_001",
  "project_revision": 42,
  "status": "valid_with_warnings",
  "issues": [
    {
      "code": "ASSET_MISSING",
      "severity": "warning",
      "entity_id": "sample_asset_07",
      "message": "The referenced sample asset could not be found.",
      "blocks_render": true,
      "suggested_action": "Relink the asset or select an approved fallback."
    },
    {
      "code": "SOFT_CONSTRAINT_DEVIATION",
      "severity": "info",
      "entity_id": "section_c",
      "message": "Perceptual density is above the preferred range.",
      "blocks_render": false,
      "evidence": { "estimated_density": 0.81, "preferred_max": 0.72 }
    }
  ]
}
```

## 67. Error taxonomy

Use stable machine-readable error codes. Avoid relying on human-readable exception text for programmatic behaviour.

Suggested categories:

- `SCHEMA_*`
- `REFERENCE_*`
- `GRAPH_*`
- `TIME_*`
- `PITCH_*`
- `CONSTRAINT_*`
- `MUTATION_*`
- `GENERATION_*`
- `INSTRUMENT_*`
- `ROUTING_*`
- `ASSET_*`
- `RENDER_*`
- `EXPORT_*`
- `MIGRATION_*`
- `RECOVERY_*`

Failures should distinguish invalid input, missing dependency, unsupported capability, conflict, timeout, cancellation, and internal error.

## 68. Musical evaluation is not data validation

A structurally valid composition may be musically weak. A structurally unusual composition may be artistically successful.

The architecture must maintain separate technical validation and musical evaluation reports. Automated metrics should provide evidence, not absolute artistic verdicts.

A candidate can therefore be:

- structurally valid;
- renderable;
- technically clean;
- perceptually crowded;
- developmentally weak;
- artistically promising.

Those states are not contradictory.

---

# Part XIV — Versioning, migrations, and compatibility

## 69. Version three different things separately

The system should distinguish:

1. **Project format version:** the serialization and package contract.
2. **Entity schema version:** the shape and semantics of a particular entity type.
3. **Algorithm or operation version:** the behaviour of a generator, transformer, evaluator, or renderer.

An algorithm update must not automatically imply that the project schema changed. A schema change must not silently reinterpret previously stored musical data.

## 70. Semantic versioning policy

A project format may use semantic versioning or a clearly defined major/minor/patch scheme:

- **Major:** incompatible semantic or structural change.
- **Minor:** backward-compatible new capabilities or optional fields.
- **Patch:** clarifications or non-semantic fixes.

The project manifest should store the version of each relevant schema or a schema registry revision.

## 71. Migration principles

A migration must:

- declare source and target versions;
- be deterministic where practical;
- preserve unknown extension data;
- avoid deleting unsupported fields without an explicit policy;
- produce a migration report;
- operate on a copy or transactional snapshot;
- validate the migrated project;
- preserve the original project until migration is confirmed.

Never make a migration that silently rounds musical time, changes pitch interpretation, removes material relationships, or substitutes missing instruments without reporting it.

## 72. Unknown fields and forward compatibility

A reader should preserve unknown optional fields in an extension namespace where feasible. A reader must not invent semantics for unknown fields.

Unknown critical fields or unsupported schema features should cause a clear compatibility warning or a blocked operation, not silent data loss.

## 73. Plugin and capability versioning

Instrument and plugin capabilities should be discoverable and versioned. A saved patch may depend on a plugin version, parameter mapping version, or external resource. The project must declare whether a dependency is required, recommended, or optional.

---

# Part XV — Reference schemas and worked representations

The following examples are illustrative reference payloads, not a complete JSON Schema registry. Production implementations should turn them into typed language models and formal schemas.

## 74. Project manifest

```json
{
  "format": "idm-generative-project",
  "format_version": "1.0.0",
  "project_id": "project_001",
  "name": "Untitled IDM Study",
  "created_at": "2026-11-26T18:00:00Z",
  "modified_at": "2026-11-26T18:45:00Z",
  "primary_composition_id": "composition_001",
  "schema_registry": {
    "composition": "1.0.0",
    "event": "1.0.0",
    "material": "1.0.0",
    "relationship": "1.0.0"
  },
  "assets": {
    "manifest_path": "assets/manifest.json",
    "hash_algorithm": "sha256"
  },
  "capabilities_required": [
    "rational_musical_time",
    "typed_event_payloads",
    "material_lineage"
  ]
}
```

## 75. Composition root

```json
{
  "id": "composition_001",
  "entity_type": "composition",
  "schema_version": "1.0.0",
  "name": "Glass and Ash",
  "brief_id": "brief_001",
  "identity_id": "identity_001",
  "duration_qn_estimate": { "n": 384, "d": 1 },
  "tempo_map_id": "tempo_map_001",
  "meter_map_id": "meter_map_001",
  "tuning_context_id": "tuning_12tet_440",
  "root_section_ids": ["section_a", "section_b", "section_c"],
  "voice_ids": ["voice_perc", "voice_bass", "voice_texture"],
  "constraint_set_id": "constraints_001",
  "status": "in_progress",
  "current_revision": 42
}
```

## 76. Composition identity

```json
{
  "id": "identity_001",
  "entity_type": "composition_identity",
  "identity_dimensions": {
    "rhythmic_character": ["asymmetric", "interlocking", "fragmented"],
    "material_character": ["metallic", "granular", "dry-transient"],
    "pitch_character": ["small-pitch-field", "ambiguous-centre"],
    "formal_character": ["accumulative", "cyclic-return"],
    "perceptual_character": ["restless", "intimate", "selectively-dense"]
  },
  "invariants": [
    "motif_glass_01_accent_profile",
    "bass_voice_register_identity"
  ],
  "flexible_dimensions": [
    "instrumentation",
    "surface_density",
    "section_length"
  ]
}
```

## 77. Section and phrase structure

```json
{
  "id": "section_b",
  "entity_type": "section",
  "name": "Interference Field",
  "formal_function": "development",
  "start_qn": { "n": 64, "d": 1 },
  "end_qn": { "n": 160, "d": 1 },
  "phrase_ids": ["phrase_b1", "phrase_b2", "phrase_b3"],
  "material_ids": ["motif_glass_01", "motif_bass_02"],
  "role_plan_id": "role_plan_b",
  "transition_in_id": "transition_ab",
  "transition_out_id": "transition_bc"
}
```

A section may have overlapping transition material. If an implementation requires strictly disjoint formal intervals, the transition should be represented as a separate layer or scope rather than forcing the section boundary to describe every audible event.

## 78. Material record

```json
{
  "id": "motif_glass_01",
  "entity_type": "motif",
  "name": "Glass Motif",
  "material_kind": "composite_rhythmic_tonal",
  "source_pattern_id": "pattern_def_glass_01",
  "identity_profile": {
    "features": {
      "accent_sequence": [1, 0, 1, 1, 0, 0, 1],
      "interval_contour": [0, 2, -1, 0],
      "duration_ratio": [1, 0.5, 1.5, 1]
    },
    "invariants": ["accent_sequence"],
    "flexible": ["register", "timbre", "ornamentation"]
  },
  "lineage": {
    "derived_from": ["source_recording_fragment_04"],
    "transformations": ["transient_extraction", "pitch_mapping"]
  },
  "provenance_id": "prov_motif_001"
}
```

## 79. Voice and assignment

```json
{
  "id": "voice_perc",
  "entity_type": "voice",
  "name": "Percussive Objects",
  "event_types": ["trigger", "percussion_hit", "gesture"],
  "default_instrument_instance_ids": ["inst_metal_sampler", "inst_noise_synth"],
  "role_assignments": ["role_assign_014", "role_assign_018"]
}
```

## 80. Automation example

```json
{
  "id": "automation_brightness_01",
  "entity_type": "automation_lane",
  "target": {
    "instrument_instance_id": "inst_texture_01",
    "semantic_parameter_id": "semantic_filter_brightness"
  },
  "time_domain": "musical_qn",
  "scope": {
    "start_qn": { "n": 64, "d": 1 },
    "end_qn": { "n": 96, "d": 1 }
  },
  "curve": {
    "kind": "cubic_bezier",
    "points": [
      { "at_qn": { "n": 64, "d": 1 }, "value": 0.18 },
      { "at_qn": { "n": 76, "d": 1 }, "value": 0.68 },
      { "at_qn": { "n": 96, "d": 1 }, "value": 0.34 }
    ]
  },
  "provenance_id": "prov_auto_001"
}
```

---

# Part XVI — Testing and reference project requirements

## 81. Why musical data needs property-based tests

Example-based tests are necessary but not sufficient. The data model contains many combinations of meter, tuplets, tempo maps, cross-boundary events, pattern instances, and graph relationships. Property-based tests should generate a wide range of valid and invalid cases.

## 82. Core invariants

The following invariants should be tested continuously.

### Identity invariants

- Entity IDs remain stable across rename and reorder.
- A relationship endpoint always resolves or is explicitly external.
- Revision IDs are unique.
- A material derivation record retains its source and operation.

### Time invariants

- Rational arithmetic remains exact through supported transformations.
- Tempo conversion and inverse conversion are within declared tolerance.
- Tempo-map interpolation is deterministic.
- Meter labels are derived consistently.
- Cross-bar and cross-meter events preserve absolute musical position.
- Pattern expansion produces stable event positions.

### Graph invariants

- Containment cycles are rejected.
- Invalid derivation cycles are rejected.
- Time-scoped relationships remain within valid bounds or declare their extension.
- Deleting a referenced object triggers a defined policy.

### Mutation invariants

- Frozen events remain unchanged.
- A mutation modifies only permitted dimensions.
- Candidate creation does not modify accepted revisions.
- Commit creates a new revision.
- Rollback restores the prior accepted state.

### Interchange invariants

- Import/export round trips preserve all supported fields.
- Unsupported fields appear in fidelity reports.
- Export does not alter the source project.
- MIDI note durations and simultaneous event ordering are stable within target-format limitations.

### Rendering invariants

- A stable snapshot and render profile produce deterministic output when deterministic rendering is supported and requested.
- Preview and final render interpret tempo, pitch, automation, and instrument assignment consistently.
- Stems begin at the same declared timeline origin or carry explicit offsets.
- Missing dependencies are reported.

## 83. Reference projects

Maintain a small, versioned reference-project suite. It should not be a collection of only simple four-bar loops.

Recommended cases:

1. Straight 4/4 with ordinary note events.
2. 7/8 with explicit 2+2+3 grouping.
3. Additive meter with a section boundary mid-cycle.
4. Two simultaneous polymetric layers.
5. Nested tuplets.
6. Swing plus local microtiming.
7. Tempo ramps and discontinuities.
8. Motif transformed into a percussion pattern.
9. A phrase that crosses a bar boundary.
10. A section with overlapping transition material.
11. A motif shared by two voices with different instrumentation.
12. A non-pitched spectral event.
13. A long gesture rendered into many low-level control points.
14. A candidate mutation that must preserve frozen anchors.
15. A parallel effect graph with a feedback branch.
16. A project with missing external plugins.
17. A project with an unavailable sample asset.
18. MIDI export with known fidelity losses.
19. Save/load/migration from a previous schema version.
20. A large event project that tests indexing and performance.

Each reference project should include expected entity counts, graph relationships, timing checks, validation output, and—where appropriate—reference renders.

## 84. Golden files and audio regression

Golden files are useful, but binary comparisons can be too strict when rendering involves non-deterministic plugins, platform-specific floating-point behaviour, or time-varying modulation.

For audio regression, use a layered approach:

- exact comparison where deterministic output is guaranteed;
- tolerance-based waveform comparison where appropriate;
- loudness and peak checks;
- spectral and temporal feature comparison;
- listening tests for meaningful sonic changes.

Never claim that an audio difference is musically harmless solely because a numerical threshold passed.

## 85. Performance requirements

The data model should support:

- efficient range queries by QN;
- lookup by entity ID;
- dependency traversal;
- incremental pattern expansion;
- cached derived projections;
- streaming large event collections;
- lazy asset loading;
- indexing by voice, section, event type, and time.

Performance optimisation must not make the canonical semantics ambiguous. An event cache can be rebuilt; a lost material lineage cannot.

---

# Part XVII — Implementation roadmap

## 86. Stage 0 — Canonical vocabulary and registry

Before coding complex features, agree on:

- entity names;
- relationship types;
- event type registry;
- time units;
- pitch conventions;
- identifier scheme;
- status and lifecycle vocabulary;
- error taxonomy.

**Acceptance:** developers use the same terms for the same concepts, and a glossary plus registry exists in source control.

## 87. Stage 1 — Core project and entity store

Implement:

- project manifest;
- stable IDs;
- entity envelope;
- composition root;
- containment graph;
- entity references;
- persistence and load/save validation.

**Acceptance:** create, save, reload, rename, reorder, and retrieve a composition without ID instability or dangling references.

## 88. Stage 2 — Musical time and events

Implement:

- rational QN coordinates;
- tempo map;
- meter map;
- metric layers;
- typed event payloads;
- deterministic sorting;
- time conversion utilities.

**Acceptance:** tuplets, tempo changes, cross-bar events, polymetric layers, and exact save/load round trips pass tests.

## 89. Stage 3 — Structure, material, and lineage

Implement:

- sections and phrases;
- voices and roles;
- materials, motifs, pattern definitions, pattern instances;
- typed graph relationships;
- provenance and transformations.

**Acceptance:** a pattern can be instantiated, transformed, traced to its source, and queried through every related phrase and section.

## 90. Stage 4 — Intent, constraints, candidates, and mutations

Implement:

- CompositionBrief;
- identity profiles;
- hard and soft constraints;
- MutationContract;
- candidate lifecycle;
- transaction and rollback;
- decision records.

**Acceptance:** a generator can propose a candidate without touching accepted material, and a commit or rejection is fully traceable.

## 91. Stage 5 — Sound realisation

Implement:

- instrument definitions and instances;
- semantic parameters;
- patch references;
- sample assets;
- effect graphs;
- routing graphs;
- automation lanes.

**Acceptance:** a score can be re-realised with a different sound source without changing the source motif or event identity.

## 92. Stage 6 — Interchange and export

Implement adapters for:

- Standard MIDI Files;
- MIDI 2.0 where supported;
- MusicXML where notation representation is useful;
- OSC for runtime communication;
- audio rendering and stems;
- project package export.

**Acceptance:** every adapter has a documented mapping, fidelity report, and round-trip test for supported data.

## 93. Stage 7 — Advanced collaboration and scalability

Only after the core semantics are stable, consider:

- concurrent editing;
- project branching;
- distributed generation;
- remote render workers;
- CRDT or operation-log collaboration;
- large-scale graph analytics;
- incremental dependency evaluation.

Do not introduce distributed complexity before stable identity, revisioning, and transactional editing work correctly in a single-user project.

---

# Appendix A — Canonical enumerations and registries

These are recommended starting registries. Implementations may extend them, but should avoid silently redefining existing values.

## A1. Entity status

- `draft`
- `candidate`
- `accepted`
- `committed`
- `frozen`
- `rejected`
- `archived`
- `superseded`

The exact state machine should define legal transitions. `rejected` and `superseded` should preserve history rather than delete an entity.

## A2. Candidate lifecycle

- `generated`
- `validated`
- `evaluated`
- `presented`
- `selected`
- `committed`
- `rejected`
- `expired`

A candidate may be regenerated or forked, but a committed candidate should become an accepted revision with clear lineage.

## A3. Role examples

- `pulse_anchor`
- `rhythmic_counterline`
- `backbeat`
- `sub_bass_foundation`
- `bass_counterline`
- `harmonic_field`
- `foreground_motif`
- `melodic_response`
- `ornamental_voice`
- `texture_bed`
- `transitional_texture`
- `high_frequency_punctuation`
- `spectral_response`
- `spatial_field`
- `silence_marker`

Role registries should support user-defined roles with descriptions, expected capabilities, and optional perceptual behaviours.

## A4. Relationship type examples

- `contains`
- `derived_from`
- `transformed_from`
- `instantiates`
- `answers`
- `supports`
- `contrasts_with`
- `doubles`
- `shadows`
- `interlocks_with`
- `reprises`
- `anticipates`
- `resolves_to`
- `performs`
- `realised_by`
- `assigned_role`
- `routed_to`
- `controlled_by`
- `references`

Every relation definition should specify directionality, allowed source and target entity types, whether a time scope is required, and whether cycles are permitted.

---

# Appendix B — Suggested formal schema strategy

## B1. Use a schema registry

Keep schemas in version control with:

- entity type;
- schema version;
- validation rules;
- examples;
- migration notes;
- compatibility notes;
- owner subsystem.

JSON Schema 2020-12 is a reasonable option for validating JSON serialization. It is not mandatory. A typed-language model can provide stronger compile-time guarantees, and a database schema can enforce persistence constraints. Many implementations will use more than one validation layer. The official [JSON Schema specification page](https://json-schema.org/specification) identifies 2020-12 as the current released specification at the time this manual was prepared.

## B2. Avoid the universal nullable object

Do not create one `MusicalObject` class with hundreds of optional properties such as `pitch`, `sample_path`, `bpm`, `filter_cutoff`, `section_id`, `velocity`, `effect_chain`, and `probability` all mixed together.

Use:

- a small common entity envelope;
- discriminated typed payloads;
- explicit relationships;
- extension namespaces;
- versioned registries.

## B3. Strictness and extensibility

Core invariants should be strict. Extensions should be possible through namespaces or registered types.

A safe pattern is:

```json
{
  "entity_type": "gesture",
  "schema_version": "1.0.0",
  "payload": {
    "gesture_kind": "spectral_morph",
    "dimensions": ["centroid", "bandwidth", "partial_density"]
  },
  "extensions": {
    "vendor.example.analysis": {
      "feature_vector_version": 3
    }
  }
}
```

Unknown extension fields can be preserved without being interpreted as core semantics.

---

# Appendix C — Data integrity and deletion policies

## C1. Never cascade-delete creative history by default

Deleting a motif that has been used to derive patterns, phrases, and sound objects can destroy a large part of the project's provenance.

Prefer archival, tombstone, or detach operations.

## C2. Deletion modes

- `archive`: hide from normal views; preserve all references.
- `detach`: remove a relationship while preserving both endpoints.
- `replace_reference`: explicitly redirect relationships to another entity.
- `hard_delete`: permitted only when no protected references remain or after explicit confirmation and archival policy.

## C3. Dependency impact report

Before deleting or modifying a shared entity, return:

- direct dependents;
- transitive dependents;
- frozen dependents;
- committed uses;
- external exports based on it;
- proposed impact actions.

The user should never discover after the fact that changing one motif silently altered multiple accepted sections.

---

# Appendix D — Developer review checklist

Before merging a change to the composition data architecture, ask:

### Ontology

- Does this introduce a genuinely new musical concept, or is an existing entity sufficient?
- Are similar terms being conflated?
- Is the object a definition, an instance, an event, a relationship, or a sound realisation?

### Identity and provenance

- Does the object have a stable ID?
- Can its source and transformation history be traced?
- Can it be revised without losing prior states?

### Time and pitch

- Are units explicit?
- Are rational positions preserved?
- Does the model support tempo and meter changes?
- Does it avoid assuming every sound has a single equal-tempered pitch?

### Graph integrity

- Are relationship types explicit?
- Are cycles valid or invalid by contract?
- Can dependent objects be found before mutation?

### Human agency

- Is generation separate from commitment?
- Can the user inspect and reject candidates?
- Can local edits preserve unrelated material?

### Persistence and interoperability

- Is the schema versioned?
- Is save/load deterministic?
- Are unknown fields handled safely?
- Are lossy conversions reported?

### Validation

- Are schema, reference, temporal, musical, realisation, and render checks distinct?
- Are test cases included?
- Can the feature be diagnosed when it fails?

---

# Appendix E — Glossary

**Absolute pitch coordinate:** A numeric representation of sounding pitch relative to a declared reference convention.

**Automation lane:** A time-varying control signal associated with a declared semantic parameter.

**Candidate:** A proposed revision not yet committed to the accepted composition state.

**Canonical model:** The authoritative internal representation whose semantics are independent of a particular export format or UI.

**Composition graph:** The network of musical entities and typed relationships that describes a work.

**Composition identity:** A set of recognisable characteristics and invariants that help preserve the identity of a work across transformations.

**CompositionBrief:** A structured statement of artistic intent, desired listening experience, material vocabulary, constraints, and delivery requirements.

**Constraint:** A testable rule or preference that governs generation or editing.

**Derivation:** A traceable relationship in which one entity is produced from another through an operation or transformation.

**Event:** A timed occurrence with a typed payload.

**Gesture:** A shaped action or control trajectory over time.

**Instrument definition:** A reusable description of a sound-producing capability or template.

**Instrument instance:** A particular configured use of an instrument within a composition.

**Material:** Reusable musical substance with identity and lineage.

**Metric layer:** An independent temporal grouping or cycle interpretation that may coexist with other layers.

**Microtiming:** Timing variation relative to a declared musical grid or intended position.

**Motif:** A recognisable musical idea that can recur or be transformed.

**Mutation contract:** A formal description of what an operation may change, what it must preserve, and how its result will be validated.

**Pattern definition:** A reusable event sequence, rule, probability model, constraint set, or hybrid representation.

**Pattern instance:** A placed and parameterised use of a pattern definition.

**Phrase:** A musical unit with a statement, response, continuation, development, or other functional relationship.

**Provenance:** Records describing how an entity was created, derived, modified, or imported.

**QN:** Quarter-note units, the recommended canonical musical time coordinate in this architecture.

**Realisation:** The sound-producing interpretation of musical data through instruments, synthesis, samples, effects, and routing.

**Role:** A context-dependent musical function performed by a voice or material.

**Section:** A major formal region of a composition.

**Tombstone:** A retained record that an entity was removed or archived, preserving historical identity and reference integrity.

**Voice:** An independent stream of musical or sonic activity.

---

# References and further reading

The architecture is a proposed internal model. The following standards and specifications are relevant to its interoperability and validation layers; they do not define the complete ontology in this manual.

1. **The MIDI Association — MIDI 2.0.** Describes MIDI 2.0 as an extension of MIDI 1.0, not a replacement, and outlines the protocol's expanded resolution and per-note expression capabilities.  
   https://midi.org/midi-2-0

2. **The MIDI Association — Universal MIDI Packet (UMP) and MIDI 2.0 Protocol Specification.** Technical reference for UMP and MIDI 2.0 protocol mapping.  
   https://midi.org/universal-midi-packet-ump-and-midi-2-0-protocol-specification

3. **The MIDI Association — Standard MIDI Files.** Reference page for Standard MIDI File specifications and related recommendations.  
   https://midi.org/standard-midi-files

4. **W3C Music Notation Community Group — MusicXML 4.0.** Music notation interchange format and technical documentation.  
   https://www.w3.org/2021/06/musicxml40/

5. **MusicXML — For Developers.** Documentation and version information for MusicXML implementations.  
   https://www.musicxml.com/for-developers/

6. **Open Sound Control 1.0 Specification.** Message protocol for communication among computers, synthesizers, and multimedia devices.  
   https://github.com/CNMAT/OpenSoundControl.org/blob/master/spec-1_0.md

7. **JSON Schema Specification.** The official specification and validation vocabulary reference; 2020-12 is the current released specification at the time of writing.  
   https://json-schema.org/specification

8. **W3C Music Notation Community Group.** Background on MusicXML, SMuFL, and ongoing work on machine-readable music representation.  
   https://www.w3.org/community/music-notation/

---

# Final declaration

A generative instrument must be able to remember more than the notes it has produced. It must remember what those notes belong to, what they were derived from, what function they perform, what transformations are permitted, and how the composer chose to preserve or change them.

The data model is therefore not a neutral storage detail. It shapes what the software can understand, what it can safely change, what it can explain, and what it can finish.

The architecture defined here establishes one governing rule:

> **Represent musical meaning before reducing it to performance events; preserve the relationships that make the work coherent; and treat every export, render, and interface as a view of the canonical composition—not as a replacement for it.**

A system built on this foundation can generate notes, but it can also preserve motifs, understand structure, trace transformations, respect constraints, support human authorship, and reproduce the work it has helped create.

That is the foundation required for an actual generative compositional instrument.
