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
