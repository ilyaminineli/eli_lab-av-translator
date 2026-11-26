# Project format

Project files use the .eliav extension and contain UTF-8 JSON.

Top-level fields:

- format: must equal eli_lab_av_translator.
- schema_version: current version is 2.
- project: project metadata such as name.
- composition: canvas dimensions, frame rate, background and ordered layers.
- decks: deck IDs, media paths, segment in/out points, loop state and collection references.
- app_state.effects: master effect values and selected look.
- app_state.automation_settings: cut timing, segment length, loop probability and automatic variation settings.

Version 2 remains backward-compatible with version 1 projects. Missing effect and automation settings use application defaults.

A project stores references to footage, not the footage itself. Media paths are absolute in the first implementation. Missing files are logged when loading.

Writes are atomic: data is serialized to a sibling temporary file and moved into place only after the write completes.


## Visual identity extension (M7-C0)

The current project schema remains version 2. Composition payloads may now include an additive `visual_objects` array. Each layer includes a `visual_object_id` stable identifier that references exactly one record in that array.

Each VisualObject record has its own `schema_version` (currently 1) and stores:

- `object_id` and `layer_id` stable association IDs.
- `role` and `material` semantic descriptors.
- `identity` geometry, palette, motion and material identity traits.
- `lineage` origin, parent object, motif reference and source-object IDs.
- `mutation_contract` preserve/allow/forbid declarations.
- `revision` object data revision.

Legacy version-1 and version-2 project compositions without `visual_objects` remain loadable. The loader synthesizes a legacy VisualObject for each layer in memory; the next save writes the identity records. Performance-scene snapshots and performance sets use the same Composition serialization, so they retain the same stable IDs.

VisualEvent records are currently an in-memory model and are not yet persisted as a project-level event score. No GPU handles, texture data, simulation state or runtime clock timestamps are serialized as VisualObject state.

## Visual motif extension (M7-C1.1)

The current project schema remains version 2 and the performance-set format remains version 1. A composition may include an additive `visual_motifs` array. Each VisualMotif has its own `schema_version` (currently 1) and stores:

- `motif_id`: stable authored motif identity, independent of any layer or VisualObject ID.
- `name` and `family`: authored name and one of the Volume 11 families: contour, motion, spatial, texture, typographic, colour, framing, transformation, absence or composite.
- `identity`: a VisualIdentity record describing the motif's recognisable geometry, palette, motion, material and typed traits.
- `parameters`: up to 64 authored scalar parameters. Numeric values must be finite and within ±1,000,000,000; strings are at most 128 characters. Nested runtime state is not stored here.
- `description`: optional authored description (at most 512 characters).
- `revision`: non-negative authored-data revision.

`Composition.visual_motifs` is the authoritative registry, keyed by motif ID. A VisualMotif is not a VisualObject and does not own a renderable layer. Multiple layer-backed VisualObjects may explicitly reference the same motif via `VisualObject.lineage.motif_id`; every realization keeps its own independent `object_id`. The loader never infers a motif reference from visual similarity or generator settings.

Legacy compositions without `visual_motifs` remain valid and load with an empty motif registry. A VisualObject may retain a historical motif ID whose definition is not present; this unresolved reference is preserved rather than silently fabricating an authored motif. Removing a layer removes its VisualObject but does not delete the authored motif. Explicit motif removal is rejected while any live VisualObject references it.

The additive field is carried through .eliav projects, performance-set composition snapshots and embedded scene snapshots by the shared Composition serializer. No GPU state, render handles, frame data or musical motif objects are stored in the VisualMotif record. Musical motif relationships remain a distinct C3 mapping concern.

## Motif recognition contract (M7-C1.2)

A VisualMotif may carry additive fields within motif schema version 1:

- `invariants`: up to 64 field-path/value pairs. Paths point to an existing authored field in `identity` or `parameters`; the stored scalar value must exactly match that authored field, including its scalar type.
- `allowed_variations`: up to 64 unique field paths that exist in the authored identity/parameter map. A field cannot be both invariant and variable.
- `seed`: optional non-negative unsigned 64-bit integer. It is persisted for reproducibility; the actual seeded variation engine is a later C1.5 slice.

The supported path forms are `identity.geometry_signature`, `identity.palette_identity`, `identity.motion_identity`, `identity.material_identity`, `identity.traits.<name>` and `parameters.<name>`. This is declarative authorship, not automatic variation: a future operation must choose only declared fields and preserve every invariant. A legacy C1.1 motif without these fields loads with empty invariants/variations and no seed.


## Motion grammar extension (M7-C1.4)

The current project schema remains version 2 and the performance-set format remains version 1. Composition may contain two additive registries:

- motion_gestures: ordered serialization of records keyed by gesture_id.
- visual_patterns: ordered serialization of records keyed by pattern_id.

A MotionGesture has schema version 1 and stores a stable ID, authored name, one bounded transform kind (translate, rotate, scale, opacity, deform, orbit, palette, material, camera, hold or composite), up to 32 bounded scalar parameters, an easing (linear, smoothstep, ease_in, ease_out, ease_in_out, step or sine), a reversible flag and a non-negative revision. Parameter numbers must be finite and within ±1,000,000,000; strings are at most 128 characters. Gesture definitions are renderer-independent and contain no target layer IDs or GPU state.

A VisualPatternStep has schema version 1 and stores a stable step ID, registered gesture_id, start_fraction in [0, 1), duration_fraction in (0, 1], intensity in [0, 1] and an optional grouping label. Start/duration values are fractions of the pattern cycle, not seconds or beats. A duration that crosses the end of a cycle wraps to the next cycle.

A VisualPattern has schema version 1 and stores a stable ID, name, one of the authored pattern families (pulse_field, displaced_accent, rotating_cycle, unequal_cycle_interlock, phase_drift, omission, burst, sparse_punctuation, density_cloud, call_and_response, unison_fusion, counter_motion, hierarchical_motion, accumulation, erosion, fracture_repair, scan_traverse, memory_echo, stutter_hold or morphing_cycle), positive cycle_length, cycle_unit, timing_basis, normalized phase, up to 64 ordered steps, optional unsigned 64-bit seed and non-negative revision. Cycle limits are 86,400 seconds or 4,096 beats/bars.

Timing is deliberately explicit:

- cycle_unit=seconds requires timing_basis=visual_clock.
- cycle_unit=beats or bars requires timing_basis=authored_music.
- Audio-analysis values, including RMS, spectrum, onset and estimated tempo, are not accepted as an authored musical clock. Mapping observations to visual intent belongs to a separately specified later system.

Composition owns both registries. A pattern may only be registered when all step gesture references exist; removing a referenced gesture is rejected until the consuming patterns are removed or edited. Each composition is limited to 256 gestures and 256 patterns. Old compositions without either field load with empty registries. These additive fields are carried by the shared Composition serializer through .eliav, .eliset and embedded scene snapshots. No project/set schema version bump is required.

These are data definitions only. No autonomous scheduler, audio listener, renderer object or GPU resource is serialized or created by the grammar models.


## Seeded variation candidate artifact (M7-C1.5)

A `VisualMotifVariation` is a standalone, self-verifying candidate record, not part of the live Composition registries. It contains motif ID and revision, source VisualObject ID, optional VisualPattern ID/revision, the authored motif/pattern seeds, a seed salt, the derived 64-bit seed, selected field paths, full variation rules, selected values and a deterministic variation ID. It may be serialized separately through its own `to_dict/from_dict` methods, but it is not automatically embedded in a project or performance set until a later acceptance flow explicitly adopts a candidate.

Each variation rule targets exactly one path already declared in `VisualMotif.allowed_variations`. Uniform rules declare `value_type` (`integer` or `number`) and finite bounds; choice rules declare 2–32 unique scalar values of the same type as the authored field. Invariant paths are never eligible. A SHA-256-derived root seed includes motif identity/revision, stable object identity, optional pattern identity/revision, authored seeds and seed salt. A separate hash-derived random stream per field makes output independent of rule order. Candidate deserialization validates both the rule bounds/choices and the deterministic ID.

Candidate generation is pure and does not mutate the motif, Composition, VisualObject or Layer. Applying or accepting a candidate is a later explicit mutation operation.
