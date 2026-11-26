# Parallel AI Agent Prompt — M7-C0 Completion

Use this prompt with an AI coding agent that has access to the repository.

---

You are a senior Python software architect and implementation engineer working on:

Repository: https://github.com/ilyaminineli/eli_lab-av-translator  
Working base branch: m7/m7-c0-visual-ontology  
Programme: M7 — Unified Generative Audiovisual Instrument  
Current target: finish M7-C0 without beginning M7-C1.

## Governing reference — read first

The document below is the project's BIBLE for visual-system decisions. Read the entire document before proposing or changing architecture:

docs/guides/IDM_Visual_Instrument_Visual_Composition_Generative_Art_and_Live_Concert_Architecture.md

Treat its vocabulary, normative requirements, data model, feature-specification template, safety rules and acceptance criteria as authoritative. In particular, preserve the distinctions between:

- Musical fact.
- Audio observation.
- Visual intention.
- Visual outcome estimate.

Do not reduce the visual system to audio-reactive effects. Visual identity, memory, lineage, figure/ground, visual phrases, performer agency, reproducibility, real-time reliability and safety are core requirements.

Also read:
- docs/M7.md — current M7 sequence, C0 status, architecture audit and exit criteria.
- docs/ROADMAP.md — product roadmap and independent M0–M6 release gates.
- docs/ARCHITECTURE.md — runtime ownership and GPU lifecycle.
- docs/PROJECT_FORMAT.md — current .eliav format.
- core/visual_model.py
- core/composition.py
- core/layer_manager.py
- core/application.py
- core/performance_timeline.py
- core/performance_environment.py
- core/automation.py
- core/performance_service.py
- core/modulation.py
- core/performance_modifiers.py
- tests/test_visual_model.py
- .github/workflows/quality.yml

Do not assume the roadmap checkbox means a feature is complete. Verify the current branch contents and recent changes yourself before editing.

## Current architecture and constraints

The existing Layer remains the renderable unit. VisualObject is a renderer-independent identity record associated with one layer. Do not replace Layer with a new scene graph.

Current C0 work already introduced:
- VisualObject, VisualIdentity, VisualLineage, VisualMutationContract and VisualEvent in core/visual_model.py.
- Layer.visual_object_id, appended to the dataclass to preserve positional constructor compatibility.
- Composition.visual_objects registry, legacy-object synthesis, add/remove/replace lifecycle and serialization.
- LayerManager source replacement creates a new object identity with parent lineage; generic updates cannot rewrite layer/object IDs.
- Locked-layer scene recall preserves the live VisualObject through Composition.replace_layer.
- Additive .eliav composition serialization; project schema remains v2.
- Initial focused tests in tests/test_visual_model.py.

The implementation is not yet complete:
- Mutation contracts are not enforced across every automatic/authored mutation route.
- VisualEvent is not connected to the performance timeline or semantic mapping layer.
- Historical .eliav/.eliset fixtures and application-level scene recall tests remain incomplete.
- Windows GitHub Actions Quality validation is required.

Non-negotiable architectural constraints:
1. No Qt, ModernGL, GPU handles, textures, framebuffers or renderer objects in the visual ontology.
2. Preview and projector keep separate GL contexts, textures, simulation and feedback history.
3. Old .eliav v1/v2 and .eliset files must continue to load. Do not bump format versions without a proven need.
4. Keep all runtime queues and work bounded.
5. Keep audio observations separate from semantic musical events.
6. Preserve layer locks, manual override priority, automation ownership and project recovery behaviour.
7. Do not add dependencies unless essential and explicitly justified.
8. Do not implement M7-C1 motifs/motion grammar yet; finish C0 first.
9. Never rewrite unrelated modules merely to make a cleaner architecture.
10. Do not claim GPU performance or hardware acceptance from static checks.

## Your assignment

Work on the remaining C0 tasks in small, independently reviewable slices.

### Task A — Complete the mutation-contract audit and integration

Audit every path that can mutate visual state, including:
- LayerManager and direct layer edits.
- AutomationDirector and the AUTO PERF system.
- Application modulation and performance-modifier application.
- Performance macros, MIDI/OSC target routing and scene morphing.
- Scene recall, random layout/variation and generator-setting mutation.

Produce a concise mutation-path map before coding. Identify which changes are:
- Operator-authored edits.
- Automatic mutations.
- Scheduled visual events.
- Source replacement.
- Destructive lifecycle operations.
- Renderer-only transient updates.

Then integrate contract validation at the correct semantic boundary. Do not blindly place checks in every numeric setter if that would make ordinary UI editing or existing automation unusable. Preserve the default contract's identity fields and allowed visual properties, and define a deliberate policy for generator settings, effect settings, source replacement, object deletion and future fracture/assembly operations.

Requirements:
- Identity and lineage fields cannot be rewritten by ordinary transforms.
- Source replacement creates a new object identity and records lineage.
- Forbidden operations are rejected before partially mutating the composition.
- Multi-property transformations are atomic or have a tested rollback strategy.
- Locked layers and performer overrides retain precedence.
- Every rejected mutation is diagnosable without crashing the live render loop.
- Manual artist actions remain possible through explicit, scoped operations.

Add tests for accepted and rejected changes on each important mutation boundary.

### Task B — Make persistence and migration verifiable

Trace and test all persistence routes:
- .eliav project save/load through ProjectManager.
- VJ PerformanceScene capture/recall.
- .eliset performance-set save/load.
- Session-recovery project writes.
- Existing legacy projects with no visual_objects.
- Locked-layer preservation when a scene snapshot is recalled.

Use small historical fixtures generated from the actual old payload shape. Verify:
- Legacy layer IDs and all previous layer properties remain intact.
- Loading synthesizes stable VisualObject IDs.
- Saving and reopening keeps those IDs.
- VisualObject registry and layer references remain one-to-one.
- Orphan records, duplicate IDs and malformed schemas fail safely with actionable errors.
- A recovered project does not start devices, transport or autonomous performance.

Do not change schema versions just because a new field exists. Prefer additive optional metadata and explicit migration code.

### Task C — Connect the VisualEvent contract without creating a second timeline engine

Audit core/performance_timeline.py, ControlEvent, OSC protocol and InternalTransport first.

Decide whether VisualEvent should be:
- the canonical domain event embedded by the existing PerformanceTimeline, or
- a validated adapter around the existing timeline event schema.

Do not create a duplicate transport, clock, event queue or scheduler.

Define:
- event identity and source;
- supported visual event types;
- immediate, performance-seconds and bar/beat time domains;
- ordering and sequence rules;
- stale, duplicate, late and out-of-order behaviour;
- conversion between the existing timeline event schema and VisualEvent;
- safe failure behaviour when an object or target layer no longer exists.

Integrate only the minimum C0 contract needed. Leave richer semantic mapping, motif recurrence and visual phrase planning for M7-C1/C2/C3.

Add tests proving that existing timeline events and .eliset files remain backward-compatible.

### Task D — Quality and C0 exit review

Run:
- python -m compileall -q .
- python -m ruff check on all changed Python files and tests.
- python -m pytest -q.
- The repository's Windows GitHub Actions Quality workflow.

Add tests for any seam you modify. Do not restore an old deleted test suite wholesale; keep the new suite focused on current architecture and durable contracts.

Update docs/M7.md, docs/ROADMAP.md, docs/ARCHITECTURE.md and docs/PROJECT_FORMAT.md only after the implementation is verified. Mark checklist items honestly. State which checks ran and which require Eli's Windows performance computer.

## Collaboration and git rules

- Start from the latest m7/m7-c0-visual-ontology branch, not main.
- Work in a separate worktree/branch if another agent is modifying the same working branch.
- Do not force-push.
- Do not rewrite or squash existing history.
- Do not change the governing Volume 11 manual unless explicitly asked.
- Keep commits small and descriptive.
- Avoid touching core/visual_model.py or core/composition.py unless the audit proves a required model-level correction; coordinate before changing shared C0 files.
- Do not create a pull request or merge into main unless explicitly requested.
- Before finishing, inspect the complete diff against main for accidental changes.

## Required final report

Return:
1. The mutation-path audit map.
2. The exact code paths changed and why.
3. The final C0 data and lifecycle invariants.
4. Persistence compatibility results.
5. Test commands and actual results, including the GitHub Actions run URL/status.
6. Known limitations and hardware-only acceptance still open.
7. A recommendation for the next milestone, but do not start it.

Be precise. Separate implemented, tested, CI-verified and hardware-verified capabilities. Never report a test as passed unless it actually ran and passed.
