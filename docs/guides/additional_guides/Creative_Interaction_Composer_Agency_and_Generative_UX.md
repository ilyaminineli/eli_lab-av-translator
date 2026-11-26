# Creative Interaction, Composer Agency & Generative UX

## A design and engineering manual for human–machine collaboration in generative music systems

**Collection:** IDM Generative Instrument Documentation Library  
**Volume:** 10 — Creative Interaction & Composer Agency  
**Primary audience:** Product architects, interaction designers, music-software developers, generative-system researchers, composers, audio engineers and QA teams  
**Document role:** Human-facing interaction specification and creative-workflow constitution  
**Status:** Reference manual; implementation-neutral  

---

## Abstract

A generative music system is not complete when it can produce plausible musical material. It becomes a useful instrument when a composer can understand what it is doing, direct its behaviour, audition alternatives, preserve discoveries, revise decisions and finish a work without losing authorship or control.

This document defines the interaction philosophy and user-experience architecture for an intelligent compositional instrument. It treats the composer and the generative system as participants in a continuing creative process. The software may propose, transform, analyse, explain, compare and render; the human may request, constrain, select, edit, reject, preserve, reinterpret or delegate. Neither participant should be forced into a single fixed role.

The manual specifies principles for composer agency, mixed-initiative interaction, semantic controls, local and global generation, auditioning, comparison, editing, history, undo, branching, explainability, preference learning, accessibility, responsiveness, failure recovery and evaluation. It defines canonical interaction concepts and reference data contracts, describes concrete workflows, and provides acceptance criteria that developers can test.

Its central thesis is simple:

> **A generative instrument should expand the composer's agency, not replace it, obscure it, or make the composer negotiate with an unpredictable black box.**

The interface is not decoration placed on top of a generation engine. It is the mechanism through which musical intention enters the system, machine proposals become understandable, human decisions become durable, and a generative process becomes an authored composition.

---

# Part I — Foundations: the instrument as a creative relationship

## 1. Scope and relationship to the other volumes

This document defines how a person interacts with the IDM Generative Instrument. It does not attempt to repeat the musical theory, sound-design knowledge, algorithm catalogue, perceptual models or audio-engine implementation details already covered elsewhere in the collection.

It assumes the following companion volumes exist:

1. **IDM Field Guide for Composers, Producers and Programmers** — the broad musical and technical foundation.
2. **Advanced Composition and Generation Appendix** — advanced compositional and computational methods.
3. **IDM Composition Atlas** — patterns, phrases, development and track structures.
4. **IDM Sound Design, Synthesis and Hybrid Sound Architecture** — timbre, synthesis, processing and sound-object construction.
5. **IDM Generative Instrument: Philosophy, Principles & Design Constitution** — governing principles, invariants and system identity.
6. **Musical Ontology, Representation & Composition Data Architecture** — canonical musical entities, relationships, time and persistence.
7. **Generative Intelligence, Algorithms & Decision-Making** — generation, planning, evaluation and selection algorithms.
8. **Perceptual Orchestration, Attention & Musical Scene Architecture** — perceptual scene, salience, grouping and density.
9. **Audio Engine, Rendering, Routing & Reproducible Production** — real-time playback, routing, rendering and export.

This tenth volume defines the interaction layer that makes those capabilities usable by a composer. It owns user-visible control semantics, workflow orchestration, state transitions, decision history, audition and comparison behaviour, error recovery and creative feedback.

### 1.1 What this document is not

It is not:

- a visual branding guide;
- a catalogue of buttons or widgets without behavioural contracts;
- a tutorial for one specific GUI framework;
- a replacement for the musical ontology;
- a claim that every composer wants the same degree of automation;
- a proposal to hide algorithmic complexity behind a few vague sliders;
- a justification for autonomous generation that cannot be inspected or reversed.

The aim is to specify a coherent instrument. A particular product may expose different workspaces or levels of detail, but it should preserve the principles and contracts defined here.

## 2. The fundamental interaction philosophy

A traditional instrument maps a musician's gesture to a musical consequence. A generative instrument adds another layer: the gesture may express an intention, request a possibility, define a constraint or delegate a bounded decision to an algorithm.

This produces a three-part loop:

1. **Human intention:** what the composer wants to explore, preserve or change.
2. **System interpretation and proposal:** how the software translates that intention into candidate musical actions.
3. **Human judgement and continuation:** how the composer auditions, accepts, edits, rejects or redirects the result.

The loop must remain visible and interruptible. The composer should not have to guess whether a control changed a parameter, regenerated material, committed a result or merely altered a preview.

### 2.1 The instrument is neither a passive tool nor an autonomous author

A purely passive tool waits for exact instructions. A fully autonomous generator makes decisions without requiring meaningful human involvement. A creative instrument should support a spectrum between these positions.

At one end, it behaves like a precise editor: the composer directly moves a note, changes a pattern, edits automation or routes an instrument. At the other, it can propose a whole arrangement or explore several alternatives. Between them, it can complete a phrase, suggest a counter-rhythm, generate a variation or analyse the consequences of a change.

The system should allow the composer to choose the level of delegation for each task, not force one global automation philosophy.

### 2.2 Agency is the ability to make consequential choices

Agency is not measured by the number of sliders, menus or exposed parameters. A control is meaningful only when the composer can understand its scope, anticipate its general consequences, observe the result and retain the ability to revise it.

A system with 400 obscure controls may offer less agency than a system with 20 well-defined musical controls and a transparent advanced mode.

### 2.3 Surprise must remain usable

Generative music benefits from surprise. But surprise becomes frustrating when the user cannot identify what changed, reproduce a promising result, or steer away from an unwanted outcome.

The design goal is not to eliminate uncertainty. It is to make uncertainty bounded, interpretable and recoverable.

---

# Part II — Constitutional interaction principles

## 3. Thirty principles for creative interaction

These principles should guide product design, feature implementation and code review.

### Principle 1 — Human authorship remains explicit

The composer can identify which material was generated, suggested, selected, edited, frozen, manually authored or committed. Machine contribution must not be hidden behind ambiguous ownership labels.

### Principle 2 — Every generative action has a declared scope

A request must state whether it affects an event, pattern, voice, phrase, section, sound object, arrangement or whole composition. The software must not silently widen the scope.

### Principle 3 — Preserve accepted work by default

Generation creates candidates. It does not overwrite committed material unless the user explicitly requests replacement or has configured an equally explicit automation policy.

### Principle 4 — Preview is not commitment

Auditioning, rendering a candidate, changing a control and applying a candidate are distinct actions and states.

### Principle 5 — Controls describe consequences

A control label should describe a musical or operational consequence, not an unexplained internal parameter. Advanced technical values may be available, but they should not be the only way to express intent.

### Principle 6 — Local actions stay local

Changing one phrase should not alter unrelated sections, sound assignments or global structure unless the user approves the dependency consequences.

### Principle 7 — The user can widen the scope deliberately

When a local change has dependencies, the application should offer an intelligible choice: preserve dependent material, update selected dependants, or propagate the change across a defined scope.

### Principle 8 — Reversibility is a core capability

Meaningful creative actions should be undoable, redoable or recoverable through version history. Destructive operations must be clearly identified.

### Principle 9 — Musical history is legible

History entries should describe the object and musical consequence, not merely the name of an internal function.

### Principle 10 — Candidates are comparable

Alternative generations should be auditioned in a common musical context, with consistent transport, level and surrounding material wherever possible.

### Principle 11 — Explainability is contextual

The system should explain what it changed, what it preserved, what constraints it followed and why the candidate may satisfy the request. It should not pretend that its explanation proves artistic quality.

### Principle 12 — Uncertainty is disclosed

When a request is ambiguous, a sound dependency is missing or a generation result is low-confidence, the interface should say so and offer useful choices.

### Principle 13 — Delegation is bounded

A delegated task has a defined scope, allowed operations, protected objects, limits and a clear completion state.

### Principle 14 — The composer can interrupt

Long generation, analysis, audition or rendering tasks must expose cancellation or a safe stop point. The system should not make the interface unavailable while it works.

### Principle 15 — Musical intent is more stable than low-level settings

The user should be able to preserve an intention such as “retain the identity of this motif” even when the underlying pattern is transformed or re-orchestrated.

### Principle 16 — Do not punish exploration

Users should be able to try alternatives without fear of losing the current result. Candidate spaces, snapshots and branches should make experimentation cheap.

### Principle 17 — The system distinguishes suggestion from instruction

A generated recommendation is not a command. A user-authored constraint is not merely a preference. The interface must distinguish them.

### Principle 18 — Technical complexity is progressively disclosed

Simple workflows should remain approachable. Advanced musical and engineering detail should be available when needed, without blocking the basic task.

### Principle 19 — The interface should teach through consequence

When the system introduces an unfamiliar control, it should make the result audible or visible, rather than relying only on abstract descriptions.

### Principle 20 — Sound is a first-class interface output

For music software, visual feedback cannot replace auditioning. The interface should make listening, A/B comparison, context switching and focused inspection central actions.

### Principle 21 — Silence and absence are valid edits

The interface must support removing, muting, freezing, thinning and leaving space, not only adding material.

### Principle 22 — Preferences require context

A composer rejecting one syncopated pattern does not necessarily dislike syncopation everywhere. Feedback should be scoped to the object, task and context in which it was given.

### Principle 23 — A learned preference must be inspectable and reversible

When the system adapts to user choices, the composer should be able to inspect, reset or disable that adaptation.

### Principle 24 — The application must not fabricate certainty

Explanations, similarity scores, predicted perceptual effects and quality metrics should be presented as estimates or observations, not as objective artistic truth.

### Principle 25 — Failure preserves the last valid state

A failed generation, plug-in load, render or migration must not leave the composition half-mutated or silently discard accepted work.

### Principle 26 — The system remembers why a result exists

Accepted material should retain provenance: source candidate, transformation, seed or generation configuration when available, user edits and the decision that committed it.

### Principle 27 — No hidden coupling between unrelated controls

A semantic control must not unexpectedly change unrelated musical dimensions. Necessary coupling should be declared and explained.

### Principle 28 — Accessibility improves the instrument for everyone

Keyboard access, readable feedback, scalable interface elements, clear focus, captions or text alternatives for visual/audio analysis, and configurable input methods are product requirements, not optional decoration.

### Principle 29 — The UI must reflect actual system state

A displayed state such as “frozen,” “rendered,” “committed” or “saved” must correspond to the authoritative backend state. Optimistic display must be reconciled with failures.

### Principle 30 — Creative control must survive automation

Automation may perform work, but it must not make the composition opaque, impossible to edit or difficult to recover.

---

# Part III — The agency model

## 4. Agency dimensions

Composer agency should be designed as a collection of independent dimensions rather than a single “manual versus automatic” switch.

### 4.1 Initiative

Who proposes the next action?

- **Human-initiated:** the user requests a specific operation.
- **System-suggested:** the system identifies an opportunity and waits for permission.
- **System-initiated within a contract:** the system acts inside an explicitly delegated task.
- **Continuous co-creation:** both parties may propose actions during an active session.

### 4.2 Control granularity

At what scale can the user intervene?

- event;
- gesture or articulation;
- pattern;
- voice or instrument;
- motif;
- phrase;
- section;
- full composition;
- sound-design object;
- mix or routing domain;
- export or production package.

### 4.3 Decision authority

Who has final authority over a result?

- **Human approval required:** candidate cannot become committed without user action.
- **Human-configured auto-commit:** a defined operation may commit automatically inside a strict contract.
- **System-managed:** the system controls a subsystem while remaining observable and reversible.

### 4.4 Transparency

How much of the system's reasoning is visible?

- outcome-only summary;
- changed/preserved summary;
- constraint and decision trace;
- algorithmic details and diagnostics;
- full reproducibility record.

Transparency should be adjustable, but the minimum changed/preserved summary should be available for every consequential generation action.

### 4.5 Reversibility

How easily can the action be recovered?

- immediately undoable;
- recoverable from history;
- reversible through a candidate branch;
- destructive with confirmation and backup;
- externally irreversible, such as publishing or overwriting a user-managed file.

### 4.6 Agency profile

A task should declare an agency profile rather than inherit unexplained global behaviour.

Example:

```yaml
agency_profile:
  initiative: human_initiated
  decision_authority: human_approval_required
  granularity: phrase
  transparency: changed_and_preserved
  reversibility: snapshot_and_undo
  auto_commit: false
```

A different task—such as generating exploratory percussion candidates—might permit system-suggested initiative and automatic candidate creation while still requiring explicit selection before commitment.

## 5. Interaction modes

### 5.1 Direct editing mode

The user edits an object directly. The system updates the canonical model and provides immediate feedback.

Use for:
- note and event editing;
- automation edits;
- sound parameter edits;
- routing and gain changes;
- manual arrangement changes;
- phrase and section boundaries.

Requirements:
- visible selection and edit target;
- precise snap and timing options;
- clear value feedback;
- undo/redo;
- no hidden regeneration;
- no silent edits to linked objects.

### 5.2 Generative exploration mode

The system produces multiple candidates without replacing the current committed material.

Use for:
- motif alternatives;
- rhythmic variations;
- phrase completions;
- alternative bass lines;
- sound-design variants;
- arrangement possibilities;
- section transitions.

Requirements:
- explicit scope;
- candidate identity;
- seed/configuration provenance;
- comparable audition context;
- select, reject, pin and regenerate actions;
- no implicit commitment.

### 5.3 Collaborative development mode

The user and system iteratively modify the same material.

Use for:
- developing a motif through several transformations;
- constructing a phrase through proposals and edits;
- orchestrating a pattern across instruments;
- adapting a section while preserving its identity.

Requirements:
- current authoritative version is explicit;
- every proposal references its parent version;
- conflicts are surfaced;
- user edits are not silently overwritten;
- the system can explain the delta between versions.

### 5.4 Delegated task mode

The user gives the system a bounded task.

Example: “Create three alternative transitions into the second section. Preserve the main motif, current tempo map and accepted bass line. Use only existing sound sources. Do not alter the rest of the arrangement.”

A delegated task must define:

- objective;
- target scope;
- protected objects;
- allowed transformations;
- resource limits;
- candidate count or stopping condition;
- whether auto-commit is allowed;
- cancellation behaviour;
- expected report.

### 5.5 Performance or live-interaction mode

The user manipulates a composition or generative process in real time.

Requirements differ from offline editing:
- predictable response time;
- safe parameter ranges;
- no blocking generation in the audio callback;
- smoothing of continuous controls;
- clear indication of queued versus applied changes;
- bounded CPU use;
- emergency stop or bypass;
- stable transport and recovery semantics.

---

# Part IV — Interaction ontology and state model

## 6. Canonical interaction entities

The interaction model should reuse the musical ontology from Volume 6 and the decision records from Volume 7. It adds user-facing entities that describe intent, proposals, choices and actions.

| Entity | Purpose |
|---|---|
| `InteractionIntent` | What the composer wants to accomplish |
| `InteractionCommand` | A concrete requested operation |
| `AgencyProfile` | Who initiates and approves the task |
| `GenerationRequest` | Request sent to the generation subsystem |
| `CandidateSet` | Group of alternative results |
| `Candidate` | One proposed musical result |
| `CandidateEvaluation` | Analysis and comparison data |
| `AuditionSession` | Playback context for inspecting alternatives |
| `SelectionDecision` | User or policy selection of a candidate |
| `CommitOperation` | Applies a selected candidate to the project |
| `EditTransaction` | A reversible set of user-visible edits |
| `HistoryEntry` | Human-readable record of a change |
| `ProjectBranch` | Alternative composition history |
| `PreferenceSignal` | Contextual feedback about a result |
| `Explanation` | Summary of change, constraints and rationale |
| `InteractionSession` | A bounded working context |

### 6.1 Identity and referential integrity

Every interaction object should reference stable IDs from the musical ontology. A candidate should point to the composition version and target entity from which it was generated. A commit should point to the selected candidate and record the exact target version it expected to modify.

A command must not target an object by a mutable display name alone. It should use a stable object identifier and validate that the object still exists and belongs to the expected project version.

### 6.2 Interaction state is not musical state

The selected candidate, open comparison panel, active tool, focused parameter and current audition position are UI/session state. They must not accidentally mutate the composition.

Conversely, a committed motif change is composition state and must persist independently of whether a panel remains open.

Keep these state domains separate:

1. **Composition state:** musical entities and their committed relationships.
2. **Generation state:** active requests, candidate sets and generator progress.
3. **Interaction state:** selection, focus, layout, active tool and open panels.
4. **Playback state:** transport, audition context, preview routing and playhead.
5. **Persistence state:** saved version, dirty status, autosave and recovery data.
6. **Rendering state:** queued, active, completed, failed or cancelled jobs.

## 7. Candidate lifecycle

A generated result should pass through explicit states.

```text
REQUESTED
   |
   v
GENERATING
   |
   v
CANDIDATE_CREATED
   |
   v
VALIDATING -----> REJECTED (invalid)
   |
   v
READY_TO_AUDITION
   |
   +----> PINNED
   |
   +----> SELECTED
   |          |
   |          v
   |       COMMIT_PENDING
   |          |
   |          v
   |       COMMITTED
   |
   +----> REJECTED_BY_USER
   |
   +----> ARCHIVED
```

The implementation may use additional states such as `STALE`, `SUPERSEDED`, `EXPIRED` or `FAILED`, but it must not collapse generation, selection and commitment into one boolean.

### 7.1 State definitions

- `REQUESTED`: the system accepted the request for processing.
- `GENERATING`: candidate computation is active.
- `CANDIDATE_CREATED`: output exists but has not passed validation.
- `VALIDATING`: schema, constraints, dependencies and basic musical invariants are checked.
- `READY_TO_AUDITION`: candidate is safe to inspect.
- `PINNED`: user marked it for retention during exploration.
- `SELECTED`: user or explicitly configured policy chose it.
- `COMMIT_PENDING`: the target version and dependencies are being revalidated.
- `COMMITTED`: candidate was applied as a new composition revision.
- `REJECTED_BY_USER`: user declined it.
- `REJECTED`: system rejected it due to a failed invariant or validation rule.
- `ARCHIVED`: retained for reference but no longer active in the candidate workspace.
- `STALE`: its parent target changed after generation, so it needs review before commitment.
- `FAILED`: generation or supporting infrastructure failed.
- `CANCELLED`: task was cancelled before completion.

### 7.2 Stale candidate protection

A candidate generated from version 12 of a phrase must not silently overwrite version 13. Before commitment, compare the candidate's parent version with the current target version.

Possible policies:

- reject commit and explain the conflict;
- rebase the candidate if the change is provably non-conflicting;
- allow explicit force-commit after showing the affected differences;
- regenerate against the current version.

The default should be safe rejection, not silent overwrite.

---

# Part V — Expressing intention through controls

## 8. Semantic controls

A good generative interface offers controls that map to meaningful creative intentions while preserving access to technical detail.

### 8.1 Three layers of control

**Layer A — Intent controls**

Examples:
- more fragmented;
- less predictable;
- more restrained;
- more rhythmically displaced;
- retain motif identity;
- create stronger contrast;
- increase space between events;
- make the section feel more unstable;
- introduce material gradually.

**Layer B — Musical controls**

Examples:
- motif transformation amount;
- syncopation range;
- event-density target;
- register distribution;
- phrase-length distribution;
- repetition interval;
- rhythmic displacement range;
- number of independent voices;
- allowed pitch classes;
- transition duration.

**Layer C — Technical controls**

Examples:
- probability thresholds;
- Markov temperature;
- search depth;
- mutation operator weights;
- candidate count;
- random seed;
- solver budget;
- model temperature;
- DSP or render quality settings.

Layer A should be approachable without the user needing to know Layer C. Layers B and C should be progressively disclosed and remain accessible to expert users.

### 8.2 Semantic controls need a contract

Every semantic control must document:

- the intention it represents;
- the musical dimensions it may affect;
- the dimensions it must preserve;
- its valid range;
- whether it is local or global;
- whether it is continuous or discrete;
- whether it is immediate, queued or generation-triggering;
- its interaction with other controls;
- how it is explained;
- how it is tested.

Example:

```yaml
control:
  id: rhythmic_fragmentation
  label: "Fragmentation"
  intent: "Increase discontinuity and interruption in the target pattern."
  affects:
    - event_grouping
    - rest_distribution
    - phrase_boundary_density
    - motif_segmentation
  preserves_by_default:
    - target_tempo
    - protected_pitch_material
    - project_meter
  scope: selected_pattern
  kind: generation_parameter
  range: [0.0, 1.0]
  default: 0.35
  application: generate_candidates
```

### 8.3 Avoid false simplicity

A single slider called “Creativity” may be useful as a broad exploratory control, but it is not a sufficient model of creative intent. It can combine several dimensions only if the user can inspect what it changes and override the mapping.

Prefer controls with legible consequences. If an aggregate control is retained, label it as a macro and show its underlying dimensions in an advanced panel.

## 9. Scope controls

Every generation or editing interface should make the target scope visible.

A scope selector may include:

- selected event;
- selected pattern;
- selected voice;
- selected motif family;
- selected phrase;
- selected section;
- selected sound object;
- selected track or bus;
- whole composition.

The UI should display the target in the object hierarchy and, when meaningful, on the timeline. A user must be able to answer: “What exactly will this action change?” before applying it.

### 9.1 Scope inheritance

When the user selects a phrase and requests “generate variations,” the request should default to that phrase. The system may consult linked motifs or companion voices for context, but it must not edit them without an explicit propagation rule.

### 9.2 Dependency awareness

If a motif is shared across several sections, a motif edit may affect many dependants. The interface should show a dependency preview:

- update only the selected occurrence;
- update all linked occurrences;
- create a new motif version and leave other uses unchanged;
- break the relationship and make this occurrence independent.

The composer should not need to understand the database graph to make this choice. Present the musical consequences, with graph details available for advanced inspection.

## 10. Constraints, preferences and protected material

These concepts must not be conflated.

- **Hard constraint:** result is invalid if violated.
- **Soft preference:** result may violate it, but the system should explain the trade-off.
- **Protected material:** object is not changed by the current task.
- **Frozen material:** object is locked against generation and editing until explicitly unfrozen.
- **Reference material:** object may guide generation but is not itself edited.
- **Context material:** object informs the request but is not a target.

The interface should show these roles clearly and provide commands to change them.

### 10.1 Constraint preview

Before an expensive or broad generation operation, display a concise summary:

- target: second-section percussion phrase;
- protected: bass motif, tempo map, section boundaries;
- hard constraints: 4/4 meter, 2-bar duration, existing sound palette;
- preferences: moderate density, high syncopation, retain kick identity;
- allowed mutations: rest placement, accent position, ornament density;
- candidates requested: 6;
- commit policy: user approval required.

This preview reduces ambiguity and prevents a common failure: generating something that is technically interesting but answers a different question from the one the composer intended.

---

# Part VI — Core creative workflows

## 11. The general interaction cycle

A robust generative workflow follows this sequence:

1. **Select context.** The composer selects the target and relevant surrounding material.
2. **Express intention.** The composer chooses a task or describes a desired consequence.
3. **Set boundaries.** The composer confirms scope, constraints, protected material and agency profile.
4. **Generate proposals.** The system creates alternatives in isolation from committed state.
5. **Validate.** The system checks structural validity, constraints and dependency compatibility.
6. **Audition.** The composer listens to candidates in context.
7. **Inspect.** The composer compares differences and explanations.
8. **Select or revise.** The composer accepts, rejects, pins or requests another mutation.
9. **Commit.** The system applies the chosen result as a new revision.
10. **Verify.** The system confirms the updated composition and makes the action undoable.

A workflow may skip steps when appropriate, but the semantic distinctions remain. For example, a one-click regeneration may launch generation and validation together, but it must still create candidates rather than silently replace committed music.

## 12. Workflow A — Discovering a musical idea

**Goal:** explore possible starting material without prematurely committing to one direction.

Recommended interaction:

1. Choose a broad artistic brief or material role.
2. Select a small set of constraints.
3. Request a modest number of candidates.
4. Audition candidates individually and in a shared context.
5. Pin interesting fragments.
6. Combine or develop pinned fragments in a separate branch.
7. Commit only when the idea has a meaningful role in the composition.

Useful interface elements:
- brief editor;
- candidate gallery;
- compact waveform or piano-roll preview;
- playback controls;
- pin/keep action;
- “show differences” view;
- candidate provenance panel.

Do not force the user to specify every note or technical parameter before the first exploration. The purpose is ideation.

## 13. Workflow B — Developing an existing motif

**Goal:** create variations while preserving recognisable identity.

1. Select a motif and one or more occurrences.
2. Choose the dimension to develop: rhythm, contour, duration, articulation, register, orchestration or fragmentation.
3. Choose identity preservation strength.
4. Generate candidates.
5. Compare each candidate against the source.
6. Review what changed and what remained invariant.
7. Commit as a new motif version or as a local occurrence variant.

The interface should distinguish a transformation from an unrelated replacement. Show lineage explicitly: source motif → transformation operation → candidate version.

## 14. Workflow C — Regenerating one local region

**Goal:** repair or replace a weak phrase without damaging the rest of the track.

1. Select the exact phrase or region.
2. Mark the surrounding context used for generation.
3. Explicitly set the edit boundary.
4. Protect neighbouring phrases and shared motifs unless propagation is requested.
5. Generate alternatives.
6. Audition with pre-roll and post-roll so transitions can be judged.
7. Commit using an atomic replacement operation.
8. Run continuity and dependency checks.

A local replacement should preserve all unaffected event IDs and content hashes where possible. This is useful for reliable undo, comparison and regression testing.

## 15. Workflow D — Arranging a section

**Goal:** ask the system to propose a section-level development while the composer retains formal control.

The composer defines:
- section role;
- duration or boundary constraints;
- motifs to introduce or preserve;
- voices that may enter, exit or transform;
- density and attention goals;
- transition conditions;
- sound palette restrictions;
- protected neighbouring sections.

The system may create arrangement proposals, but each proposal should describe its structural changes: entrance, withdrawal, transformation, register shift, material recurrence, texture change or transition gesture.

The composer should be able to accept individual decisions rather than only the entire arrangement.

## 16. Workflow E — Sound-design exploration

**Goal:** explore alternative sound identities for a musical object without breaking its musical role.

The user selects a sound object or instrument role and chooses whether to preserve:
- pitch behaviour;
- articulation;
- duration envelope;
- transient timing;
- stereo position;
- loudness range;
- modulation character;
- effect routing.

The generation engine may propose synthesis, sample, resynthesis or hybrid alternatives. The interface should distinguish sound identity from performance identity. A new timbre can preserve the original MIDI or event behaviour; alternatively, the user may ask for a new performance gesture too.

Preview should be loudness-matched where possible so a louder candidate is not automatically perceived as better. The UI should display when loudness matching or processing has changed the raw candidate.

## 17. Workflow F — Delegating a bounded task

A delegated task should appear as a visible job with:

- plain-language task summary;
- target scope;
- protected content;
- progress state;
- candidates found;
- resource consumption if relevant;
- cancellation control;
- completion report;
- unresolved warnings.

The composer can inspect intermediate candidates if the task supports streaming proposals. The system must not make the composition feel locked while the job runs.

---

# Part VII — Audition, comparison and selection

## 18. Audition is a core operation

A music-generation interface must make auditioning more than a play button. The user needs to compare musical consequences in context.

### 18.1 Audition contexts

Support at least:

- **Solo:** target material only.
- **Context:** target plus surrounding musical layers.
- **Full mix:** whole composition.
- **A/B:** alternate between two candidates at the same musical position.
- **Sequence:** audition several candidates in order.
- **Loop:** repeat a selected region.
- **Pre-roll/post-roll:** include surrounding events to inspect transitions.
- **Stem focus:** audition selected buses or roles.

### 18.2 Common-context comparison

When candidates are compared, keep unchanged context identical wherever possible. Otherwise, the composer may attribute an effect to the candidate when it was caused by a different mix, transport position or surrounding performance.

### 18.3 Level matching

A louder candidate may seem more exciting even when it is not musically better. Where practical, comparison playback should provide a level-matched mode. The interface should disclose the use of gain compensation and allow the raw level to be inspected.

### 18.4 Playback synchronisation

Switching candidates should preserve musical position. If a candidate has a different duration, the interface should define whether the comparison follows bar position, event alignment or elapsed time. Do not silently restart from an unrelated point.

### 18.5 Preview isolation

Candidate audition must not alter the main mix, automation, plug-in state or project transport in a way that persists after audition. Use a preview graph or controlled preview routing. Restore the previous state reliably when the audition ends.

### 18.6 Candidate audition status

A candidate may be:
- not auditioned;
- auditioning;
- auditioned in isolation;
- auditioned in context;
- auditioned in full mix;
- marked for review;
- selected;
- rejected.

These states are useful for large candidate sets and should be represented independently of candidate validity.

## 19. Candidate comparison

Comparison should show both the musical result and the difference from the source.

### 19.1 Difference dimensions

Depending on the target, show:
- event additions and removals;
- timing changes;
- pitch changes;
- motif relationship changes;
- register changes;
- density changes;
- voice or instrument changes;
- articulation changes;
- automation changes;
- sound-design changes;
- routing changes;
- section-boundary changes.

### 19.2 Comparison language

Prefer contextual explanations:

> Candidate B preserves the original downbeat accents, shifts three secondary hits later in the bar, removes one repeated ornament and adds a rest before the phrase ending.

Avoid unsupported claims such as:

> Candidate B is 23% more creative.

A numerical measure can be displayed if it has a defined method and interpretation, but it must not masquerade as an objective verdict.

### 19.3 Candidate gallery design

Each candidate card or row should communicate:
- stable candidate ID or short label;
- source object;
- transformation requested;
- seed or reproducibility reference;
- preview duration;
- validation status;
- audition status;
- notable differences;
- warnings;
- pin/select/reject actions.

Large candidate sets should support sorting by user-defined criteria, filtering by constraints, grouping by transformation family and preserving pinned results.

## 20. Selection is a decision, not a playback event

Playing a candidate does not mean accepting it. Selecting a candidate for closer review is not necessarily the same as committing it to the composition.

Keep at least these actions distinct:

- audition;
- pin;
- compare;
- mark for later;
- select;
- commit;
- reject;
- archive.

For small workflows, some controls may be combined visually, but the state model must preserve the semantic distinction.

---

# Part VIII — Editing, mutation and preservation

## 21. Editing levels

The interface should support edits at multiple abstraction levels.

### 21.1 Event-level editing

- move, resize, delete or duplicate event;
- change pitch or velocity;
- edit articulation;
- change microtiming;
- add or remove expression data.

### 21.2 Pattern-level editing

- change event grouping;
- alter accents;
- change rests;
- rotate or displace a cycle;
- change pattern length;
- derive a variation;
- edit a pattern's relationship with another voice.

### 21.3 Motif-level editing

- edit motif contour or rhythm;
- preserve selected intervals or accent structure;
- create a motif version;
- edit occurrence-level variations;
- inspect lineage.

### 21.4 Phrase-level editing

- replace or regenerate a phrase;
- extend or contract duration;
- create response or continuation;
- alter phrase boundary;
- preserve opening or ending gesture;
- control relationship with neighbouring phrases.

### 21.5 Section-level editing

- move, duplicate or restructure a section;
- change role or energy trajectory;
- alter entrance/exit behaviour;
- transform material across sections;
- regenerate orchestration while preserving form.

### 21.6 Production-level editing

- change sound source;
- edit processing chain;
- change routing;
- freeze or unfreeze a track;
- update render profile;
- export selected buses or stems.

## 22. Mutation intent and contracts

Every generative edit should have a mutation contract. The contract identifies target objects, allowed changes, protected properties, expected relationships and commit policy.

Example:

```yaml
mutation_contract:
  id: mutate_phrase_rhythm_01
  target:
    phrase_id: phrase_verse_a_02
  operation: rhythmic_variation
  allowed_changes:
    - event_onsets
    - rest_distribution
    - accent_pattern
    - ornament_count
  preserve:
    - phrase_duration
    - pitch_sequence
    - motif_identity
    - section_boundary
  constraints:
    meter: "7/8"
    max_event_density: 0.72
  context:
    include_previous_phrase: true
    include_next_phrase: true
  dependencies:
    update_shared_motif: false
  selection:
    candidates: 5
    auto_commit: false
```

### 22.1 Preservation report

After generation, provide a report:

- preserved properties;
- changed properties;
- soft preferences not met;
- constraints met or violated;
- dependencies considered;
- any unresolved uncertainty.

### 22.2 User edits after generation

If the composer manually edits a candidate, the system should create a user-edited descendant rather than treating the edit as an untracked mutation. The original candidate remains available for comparison and recovery.

### 22.3 Rebase and conflict handling

If the source material changes while a candidate is open, the application should detect the stale parent version. It may offer rebase, regenerate or compare against the current state. It must not overwrite newer manual work without explicit approval.

## 23. Freeze, lock, pin and protect

These terms have distinct meanings:

- **Pin:** keep a candidate visible or protected from automatic cleanup.
- **Lock:** prevent editing or mutation of an object.
- **Freeze:** commit a performance or rendered state for computational or production reasons.
- **Protect:** declare that the current task must not change an object.
- **Preserve:** specify properties that a transformation should retain, while allowing other aspects to change.

The interface and internal API should not use these terms interchangeably.

---

# Part IX — History, undo, branching and project continuity

## 24. History as a creative memory

History should not be treated only as a technical debugging log. It is part of the composer's working memory.

A useful history record explains:
- what object changed;
- what operation occurred;
- what the composer requested;
- what the system changed;
- what was preserved;
- which candidate or source version was used;
- whether the action was manual, generated or automatic;
- whether it can be reversed;
- what dependencies were affected.

Good history label:

`Replaced 2-bar percussion phrase — kept kick anchors, varied metallic accents`

Poor history label:

`apply_candidate() returned true`

## 25. Undo and redo

Undo must restore the previous valid state, including relevant musical relationships and references.

### 25.1 Transaction boundaries

A user-visible operation should be atomic where possible. A phrase replacement that affects events, pattern references and provenance should either commit all related changes or none.

### 25.2 Grouped operations

Continuous gestures may create many internal updates. They should normally appear as one meaningful undo step when the user perceives them as one action.

Example: dragging a note across 30 frames should not require 30 undo operations.

### 25.3 Undo across generation

Undo must reverse a committed generation, not necessarily erase the candidate history. The candidate may remain available for reuse. Keep composition revision history separate from candidate workspace history.

### 25.4 Selective undo

Selective undo is powerful but can be dangerous when operations have dependencies. If a selective undo would invalidate later work, the system should show the conflict and offer a safe alternative. Do not implement object-level undo as though all actions are independent.

### 25.5 Redo semantics

Redo should reapply the exact prior operation and result, not run generation again with a new random seed. Re-execution is a separate action labelled “regenerate.”

## 26. Branching and snapshots

Creative exploration often requires non-linear history.

Support:
- named snapshots;
- temporary candidate branches;
- composition branches;
- comparison between branches;
- restore branch as current;
- merge selected objects from one branch into another;
- branch provenance.

A branch is not necessarily a complete duplicate of all audio assets. It can reference immutable project assets and store only versioned changes, provided references remain valid.

### 26.1 Branch merge

Merging should operate at meaningful musical scopes. The user may import a phrase, motif, sound object or section from another branch without replacing the entire project.

Before merging, show conflicts such as:
- source motif version differs;
- tempo map changed;
- section duration changed;
- sound asset missing;
- automation references a removed parameter.

### 26.2 Autosave and crash recovery

Autosave should preserve both committed project state and important user decisions. Candidate caches may be recoverable separately. On restart, the app should distinguish:
- latest saved project;
- recovered unsaved project state;
- incomplete generation tasks;
- incomplete renders;
- temporary previews that can be discarded.

Never mark a recovered project as fully saved before the user or persistence subsystem confirms the save.

---

# Part X — Explainability and trust

## 27. A practical explanation model

Explainability should answer practical questions, not produce an elaborate narrative for its own sake.

For each significant operation, the interface should answer:

1. **What did the system do?**
2. **What did it change?**
3. **What did it preserve?**
4. **Which constraints did it follow?**
5. **What assumptions did it make?**
6. **What can the composer do next?**

### 27.1 Explanation levels

**Level 1 — Summary**

A short natural-language description.

**Level 2 — Musical delta**

A list or visual diff of changes to notes, events, motifs, phrases, roles or structure.

**Level 3 — Constraint trace**

Which constraints were satisfied, softened or violated; which objects were protected; and which dependencies were considered.

**Level 4 — Algorithmic trace**

Generation method, configuration, seed, candidate ranking dimensions and computational warnings.

**Level 5 — Developer diagnostics**

Structured logs, timing, solver status, validation output and subsystem errors.

Most composers need Levels 1–3. Developers and expert users may require Levels 4–5.

### 27.2 Do not overstate causal explanations

A system may know which operators it used without knowing why a result is artistically compelling. Explanations should distinguish:
- recorded facts about the operation;
- computed measurements;
- inferred interpretations;
- speculative suggestions.

Do not write “the system created tension” as a verified fact if it only increased event density or syncopation. Prefer “the candidate increases syncopation and shortens the rest before the phrase ending; this may create a stronger sense of interruption.”

### 27.3 Explanation should link to inspection

A statement such as “the rhythm is more fragmented” should link to the affected events or pattern view. “The bass motif was preserved” should allow the user to inspect that motif.

### 27.4 Explainable failure

When generation fails, explain the actual blocking condition:
- no valid candidate found within the search budget;
- hard constraints conflict;
- target object changed during generation;
- required sound resource is unavailable;
- renderer failed;
- plug-in state could not be restored.

Avoid generic “Something went wrong” when a more specific safe explanation is available.

## 28. Trust and predictability

Trust comes from a consistent relationship between request and consequence.

A composer should learn:
- what a control affects;
- how much variation to expect;
- whether the result is deterministic;
- whether the same request can produce different candidates;
- how to reproduce an accepted candidate;
- what will be overwritten;
- what remains protected.

### 28.1 Controlled surprise

Use bounded exploration:
- define the target and constraints;
- generate alternatives with diverse but valid strategies;
- display why candidates differ;
- preserve candidate seeds and configurations;
- allow the user to increase or reduce exploration.

### 28.2 Confidence and uncertainty

If a system estimates that a candidate may violate a preference or is only weakly related to a source motif, show this as an uncertainty or warning. Do not hide it inside a single composite score.

### 28.3 No dark patterns

Do not make destructive or broad generation the most visually prominent default action. Do not pressure users to accept candidates through manipulative ranking, fake urgency or hidden defaults. Make rejection and cancellation as straightforward as acceptance.

---

# Part XI — Preference learning and adaptation

## 29. Contextual preference signals

The instrument may learn from explicit choices, but preferences must be contextual.

A preference signal should include:
- user action (accept, reject, pin, edit, compare);
- target type;
- musical context;
- requested task;
- candidate features relevant to that context;
- whether the user supplied an explanation;
- confidence or strength if explicitly expressed.

Example: rejecting a dense 7/8 percussion variation during a sparse breakdown should not become a universal rule against dense 7/8 percussion.

### 29.1 Explicit versus inferred preferences

- **Explicit:** “Avoid busy hi-hats in this section.”
- **Inferred:** the user repeatedly chooses less dense candidates.

The UI should distinguish them. Inferred preferences should remain tentative and editable.

### 29.2 Preference scopes

- current operation;
- selected object;
- current section;
- current composition;
- current project;
- optional global profile.

Default learning scope should be narrow. Broader adaptation should require clear user control.

### 29.3 Learning controls

Provide:
- inspect learned preferences;
- edit a preference;
- remove a preference;
- reset current project preferences;
- disable learning;
- distinguish temporary session context from persistent profile settings.

### 29.4 Do not infer identity from creative choices

The system should learn task-relevant creative preferences, not infer sensitive personal traits from musical behaviour. Keep preference data focused on the creative task and under the user's control.

---

# Part XII — Interface architecture and workspaces

## 30. Workspace principles

The product may have multiple workspaces, but their state and navigation should remain coherent.

A practical structure could include:

1. **Composition workspace:** timeline, sections, phrases, voices and arrangement.
2. **Generation workspace:** task brief, constraints, candidate gallery and generation history.
3. **Pattern and motif workspace:** event editing, transformation and lineage.
4. **Sound workspace:** instrument, synthesis, effects and sound-object audition.
5. **Mix and routing workspace:** buses, FX, metering and stem previews.
6. **Evaluation workspace:** diagnostics, perceptual analysis and comparison.
7. **Project and export workspace:** versions, manifests, render jobs and output packages.

This is a logical decomposition, not a requirement for seven separate windows. The application can use panels, tabs, dockable regions or contextual modes.

## 31. Persistent context

A composer should not lose the current musical target when moving between workspaces.

The application should preserve:
- selected object;
- selected time range;
- current candidate set;
- pinned candidate IDs;
- audition position;
- active constraints;
- current branch;
- current comparison pair;
- active generation task.

If a workspace cannot act on a selected object, explain why rather than silently changing selection.

## 32. Progressive disclosure

Use three levels:

- **Essential:** common controls needed for ordinary work.
- **Advanced:** detailed musical and generator settings.
- **Expert/developer:** diagnostic and algorithmic internals.

Do not hide essential safety or preservation information inside an advanced panel. The user should always see scope, protected content and commit behaviour.

## 33. Visual representation rules

Visuals should make musical relationships inspectable.

Useful representations include:
- timeline and section map;
- piano roll or event lane;
- rhythmic grid and cycle view;
- motif lineage graph;
- dependency map;
- candidate comparison diff;
- orchestration role map;
- automation curves;
- routing graph;
- generation task queue;
- history timeline;
- branch map.

Do not require every composer to understand every representation. Provide a coherent default view and link advanced views contextually.

### 33.1 Avoid visual overload

The application should not display every analytical feature at once. Use selection, filters, overlays and focus modes. Maintain a stable visual hierarchy between composition, generation status, warnings and diagnostics.

### 33.2 Colour is not the only channel

Use labels, icons, shapes, line styles or text in addition to colour to indicate candidate status, warnings, locks, frozen objects and selection. This improves accessibility and reduces ambiguity.

---

# Part XIII — Interaction patterns and control contracts

## 34. Core interaction patterns

### 34.1 Generate candidates

Input: target, intent, constraints, agency profile, candidate count and generation configuration.

Output: candidate set, status, provenance and warnings.

The action must not change committed composition state.

### 34.2 Regenerate selected candidate

Input: candidate ID, changed parameters and preservation contract.

Output: a new candidate linked to its parent. Do not mutate the original candidate in place.

### 34.3 Commit candidate

Input: candidate ID, target version, commit mode and dependency policy.

Preconditions:
- candidate is valid and selectable;
- target object exists;
- target version matches or a conflict policy is explicitly applied;
- all hard constraints pass;
- the user has authority to commit.

Output: new composition revision and history entry.

### 34.4 Pin candidate

Pinning preserves a candidate in the active exploration set. It does not commit it.

### 34.5 Reject candidate

Rejection changes candidate state and may provide a preference signal if the user chooses. Rejection must not delete the candidate unless the user explicitly requests deletion.

### 34.6 Create snapshot

Snapshot captures a named composition state or a specified scope. It must record all required dependency references.

### 34.7 Compare versions

Comparison should identify musical and technical changes at the requested granularity. The user should be able to switch from summary to detail.

### 34.8 Freeze preview

A preview freeze should be distinguishable from a production freeze. A preview cache must not be mistaken for an authoritative render or a committed musical edit.

## 35. Interaction command contract

Every command should define:

- command ID;
- actor (human, system policy, background task);
- target IDs;
- expected project and target versions;
- scope;
- intent;
- hard constraints;
- soft preferences;
- protected objects;
- agency profile;
- idempotency key where relevant;
- cancellation support;
- expected response state.

Example command schema:

```json
{
  "command_id": "cmd_01J9PHRASEVAR",
  "type": "generation.request",
  "actor": {"type": "human", "id": "local_user"},
  "project_id": "project_001",
  "expected_project_revision": 42,
  "target": {
    "entity_type": "Phrase",
    "entity_id": "phrase_verse_a_02",
    "expected_entity_revision": 7
  },
  "intent": {
    "goal": "create_rhythmic_variations",
    "description": "Make the phrase more fragmented while retaining its identity"
  },
  "constraints": {
    "hard": ["preserve_duration", "preserve_pitch_material"],
    "soft": ["moderate_density", "retain_downbeat_anchor"]
  },
  "protected_entity_ids": ["bass_motif_01", "section_boundary_02"],
  "agency_profile": {
    "decision_authority": "human_approval_required",
    "auto_commit": false
  },
  "generation": {
    "candidate_count": 5,
    "seed": 41827
  }
}
```

### 35.1 Command acknowledgement

An acknowledgement should say whether the command was accepted, queued, rejected or completed. It should not return “success” merely because the UI button was pressed.

### 35.2 Idempotency

Repeated network or UI requests must not accidentally create duplicate commits. Commands that may be retried should include idempotency keys and clear operation identity.

### 35.3 Cancellation

Cancellation should be a first-class command. The UI must distinguish cancellation requested from cancellation completed. If an operation has passed an irreversible commit point, explain what can still be safely cancelled.

---

# Part XIV — Responsiveness, preview and asynchronous work

## 36. Responsiveness is part of musical feel

The interaction layer must feel immediate for direct edits and responsive for longer generation tasks.

Not every algorithm can respond instantly, but the application should acknowledge the action, show progress, preserve ongoing work and allow cancellation where feasible.

### 36.1 Fast feedback categories

- **Immediate:** selection, focus, parameter display, local visual edits.
- **Near-immediate:** lightweight analysis, local preview updates, small pattern transforms.
- **Asynchronous:** large candidate search, full-section planning, high-quality resynthesis, offline render.

These are product categories, not universal millisecond guarantees. Actual budgets should be measured on supported hardware and documented.

### 36.2 Do not block the audio thread

Generation, UI layout, file access, model inference, disk I/O, plug-in discovery and expensive analysis must not run inside a real-time audio callback. The audio engine and UI should communicate through bounded, thread-safe mechanisms defined by the audio-engine architecture.

### 36.3 Progress feedback

A useful progress message includes:
- task name;
- target scope;
- current stage;
- completion estimate only when reliable;
- cancel control;
- warning count;
- whether partial candidates are available.

Do not invent precise progress percentages when the algorithm cannot estimate its remaining work.

### 36.4 Progressive candidate delivery

For suitable algorithms, deliver valid candidates as they become available. Mark the set as incomplete while more candidates may arrive. The composer can audition early results, but the interface must indicate that ranking or diversity may change as generation continues.

### 36.5 Preview quality disclosure

If preview uses reduced sample rate, simplified synthesis, cached effects, lower oversampling or a different instrument approximation, show that distinction. The composer should know whether the preview is representative of final output.

---

# Part XV — Accessibility and inclusive interaction

## 37. Accessibility is a product requirement

A professional creative instrument should support different physical, sensory, cognitive and interaction needs. Accessibility should be built into the interaction model rather than added after the interface is complete.

Use WCAG 2.2 as an applicable web-interface reference where relevant, and translate its principles appropriately for desktop software. WCAG is not a complete accessibility specification for every desktop DAW workflow, but it provides testable guidance on perceivability, operability and understandable controls.[^1]

### 37.1 Keyboard access

All essential functionality should have keyboard access:
- navigation between workspaces;
- selection of tracks, phrases and candidates;
- audition and transport;
- generation and cancellation;
- commit, reject, undo and redo;
- editing and value adjustment;
- access to warnings and history.

Keyboard shortcuts should be discoverable, remappable where practical and consistent.

### 37.2 Focus and selection clarity

Keyboard focus and musical selection are different states. Represent them separately. A selected phrase should not lose its musical selection just because the user moves focus to a candidate panel.

Focus indicators must remain visible. Modals should not trap users unexpectedly, and closing a panel should return focus to a predictable location.

### 37.3 Visual accessibility

- support scalable text and interface elements;
- use sufficient contrast;
- do not rely on colour alone;
- support reduced motion where relevant;
- provide readable labels for icon-only controls;
- expose waveform and analysis meaning through text where practical.

### 37.4 Auditory accessibility

Not every user can rely on the same auditory feedback. Provide visual or textual status for generation state, transport, clipping, render completion, warnings and comparison differences. Where musical audio itself cannot be fully represented non-auditorily, offer supplementary event and structure views.

### 37.5 Cognitive load

Use consistent terminology, predictable layouts, concise error messages, clear defaults and progressive disclosure. Avoid changing control meaning between workspaces.

### 37.6 Input flexibility

Support mouse, keyboard and, where practical, MIDI controllers or alternative input devices. Gestural controls should have non-gesture alternatives. Avoid requiring a precise drag gesture when the same operation can be performed through a numeric or keyboard method.

---

# Part XVI — Failure handling and recovery

## 38. Failure states must preserve agency

The interface should make failure visible, localised and recoverable.

### 38.1 Generation failure

Possible causes:
- conflicting hard constraints;
- no candidates within the search budget;
- model or generator unavailable;
- timeout or resource limit;
- invalid candidate structure;
- target changed while generation was running.

Required behaviour:
- preserve the original composition;
- retain any valid candidates already created;
- report the blocking condition;
- provide an actionable choice (relax a soft preference, change scope, increase budget, regenerate, cancel);
- create no partial commit.

### 38.2 Render failure

Show which render job failed, preserve the source project, retain logs and allow retry. Do not report a partial audio package as a complete export.

### 38.3 Save failure

Keep the in-memory project marked dirty. Provide a safe retry or alternate save path. Do not clear the dirty state until persistence is confirmed.

### 38.4 Plug-in or asset missing

Keep the musical structure visible. Identify missing dependencies and provide replacement or relink options. Do not silently substitute a different sound source without clearly indicating the change.

### 38.5 Stale state conflict

If an external or background process modified the target, show the conflict and offer compare, rebase, regenerate or cancel.

### 38.6 Recovery after interruption

On restart, recover the last valid composition revision and explain whether incomplete tasks were cancelled, resumed or discarded. Never silently treat incomplete background work as committed.

---

# Part XVII — Evaluation of the interaction system

## 39. UX quality dimensions

The application should be evaluated on more than feature completeness.

| Dimension | Evaluation question |
|---|---|
| Intent expression | Can the composer communicate the desired musical change? |
| Scope clarity | Can the composer predict what will be affected? |
| Controllability | Can the composer steer results toward a desired outcome? |
| Predictability | Do controls behave consistently? |
| Surprise quality | Are unexpected results useful and recoverable? |
| Audition efficiency | Can candidates be compared without friction? |
| Preservation | Does accepted material remain safe? |
| Reversibility | Can mistakes be undone or recovered? |
| Explainability | Can the composer understand changes and limitations? |
| Workflow continuity | Can the composer move between workspaces without losing context? |
| Accessibility | Can different users operate essential functions? |
| Completion | Can users finish and export a composition without workaround-heavy processes? |

Research on music co-creation systems has reported that novelty and ease of use can coexist with limitations in controllability and predictability. These should therefore be evaluated independently, not inferred from general satisfaction alone.[^2]

## 40. Evaluation methods

Use complementary methods:

- task-based usability tests;
- think-aloud sessions with composers;
- expert review by producers and composers;
- interaction-log analysis;
- time-to-completion measures;
- candidate-selection studies;
- preference consistency tests;
- accessibility audits;
- controlled comparison of interaction designs;
- longitudinal use studies.

### 40.1 Task scenarios

Example evaluation tasks:

1. Generate five variations of a selected pattern while preserving its downbeat anchors.
2. Compare three candidates in the full arrangement and select one.
3. Replace one phrase without changing its neighbouring phrase.
4. Undo a committed change and restore the prior version.
5. Recover a pinned candidate after closing and reopening the project.
6. Explain why a candidate is marked stale.
7. Cancel a long generation task without losing accepted work.
8. Find and correct a missing sound dependency before export.

### 40.2 Quantitative measures

Possible measures include:
- task completion rate;
- time to complete task;
- number of unintended edits;
- number of recovery actions;
- number of accepted candidates;
- rate of repeated regeneration due to poor controllability;
- candidate comparison time;
- undo frequency and success;
- user-rated confidence in scope and result;
- accessibility task completion.

These metrics must be interpreted in context. More accepted candidates do not necessarily mean better creative support; a composer may reject many alternatives as part of productive exploration.

### 40.3 Qualitative measures

Ask composers:
- Did you feel in control of the process?
- Did the system surprise you productively?
- Could you understand what changed?
- Did you feel safe experimenting?
- Did the tool preserve your musical identity?
- Did the interface help you make decisions, or make decisions for you?
- What did you avoid using because you did not trust it?

### 40.4 Avoid a single UX score

A single score hides trade-offs. Report multiple dimensions and preserve qualitative findings. A tool can be easy to operate yet musically restrictive; it can be highly controllable but cognitively demanding. Those are different design problems.

---

# Part XVIII — Implementation architecture and delivery roadmap

## 41. Interaction subsystem boundaries

A practical architecture should separate:

1. **Interaction Controller:** receives commands and validates user intent.
2. **Agency Policy Service:** resolves initiative, approval and delegation rules.
3. **Scope Resolver:** maps user selection to canonical musical entities.
4. **Generation Orchestrator:** submits tasks and tracks progress.
5. **Candidate Repository:** stores candidate sets and lifecycle states.
6. **Audition Controller:** manages preview context and playback synchronisation.
7. **Comparison Service:** computes and presents deltas.
8. **Commit Service:** validates versions and applies changes atomically.
9. **History Service:** records user-visible actions and supports undo/redo.
10. **Branch Manager:** creates snapshots and manages non-linear history.
11. **Explanation Service:** assembles summaries and traces from authoritative records.
12. **Preference Service:** stores scoped user feedback and adaptation state.
13. **Notification and Recovery Service:** communicates background progress, failures and recovery.

These may be implemented as modules within one process. The boundaries are logical responsibility boundaries, not mandatory microservices.

## 42. Interaction event model

Use explicit events such as:

```text
interaction.intent_created
interaction.command_submitted
interaction.command_acknowledged
interaction.command_rejected
interaction.task_started
interaction.task_progressed
interaction.task_cancel_requested
interaction.task_cancelled
generation.candidate_created
generation.candidate_validated
generation.candidate_rejected
generation.candidate_pinned
generation.candidate_selected
generation.candidate_staled
candidate.audition_started
candidate.audition_stopped
candidate.comparison_created
composition.commit_requested
composition.commit_succeeded
composition.commit_conflicted
composition.commit_failed
history.entry_created
history.undo_applied
history.redo_applied
branch.created
branch.restored
preference.signal_recorded
explanation.generated
```

Events should carry stable entity IDs, project revision, task ID, actor, timestamp, correlation ID and relevant payload. The authoritative composition model remains the source of truth; UI event streams should not become an alternative unvalidated composition database.

## 43. Delivery phases

### Phase A — Safe interaction foundation

Implement:
- explicit target scope;
- generation request panel;
- candidate lifecycle;
- audition without commitment;
- select/reject/pin;
- atomic commit;
- undo/redo;
- clear task status and errors.

Acceptance: no generation action can silently overwrite committed material.

### Phase B — Comparison and local editing

Implement:
- A/B audition;
- common context playback;
- candidate difference view;
- local regeneration;
- preservation reports;
- stale candidate detection;
- grouped edit transactions.

Acceptance: a selected local edit preserves unrelated musical entities and can be fully undone.

### Phase C — History and creative continuity

Implement:
- named snapshots;
- candidate persistence;
- project branches;
- object-level provenance;
- merge or import selected material;
- recovery after application restart.

Acceptance: a composer can recover a previously pinned idea and compare it with the current committed version.

### Phase D — Mixed-initiative collaboration

Implement:
- contextual suggestions;
- bounded delegated tasks;
- explainable task reports;
- adaptive agency profiles;
- preference controls;
- partial candidate delivery.

Acceptance: automatic actions remain within explicit scopes and approval policies.

### Phase E — Professional creative UX

Implement:
- accessibility pass;
- remappable controls;
- advanced diagnostics;
- large-project candidate management;
- performance-mode interaction;
- workflow analytics and user-study feedback.

Acceptance: essential workflows remain reliable across supported input methods, project sizes and hardware profiles.

---

# Part XIX — Reference workflows in detail

## 44. Example: a phrase-generation session

**Initial state:** the composer has an accepted two-bar 7/8 percussion phrase. Its kick anchors are important, but the secondary accents feel too regular.

**User intent:** make the phrase more fragmented, preserve the kick anchors, retain the phrase duration and produce five alternatives.

### System interpretation

The interaction controller resolves the selected phrase and reads its current revision. The scope resolver identifies the pattern, linked motif references and neighbouring context. The agency policy requires human approval. The generator receives the phrase plus the hard constraints and soft preferences.

### Candidate creation

The system creates five candidates. Each candidate has:
- unique ID;
- source phrase ID and revision;
- generator configuration and seed;
- changed event list;
- preserved kick-anchor references;
- validation report;
- short explanation.

### Audition

The composer compares candidates in the same arrangement context. The system keeps the transport position aligned to the phrase start and uses common preview routing. The composer pins candidate 3 and candidate 5.

### Selection

The composer chooses candidate 5. Before commit, the system verifies that the original phrase is still at the expected revision. It is.

### Commit

The system creates a new phrase revision and one history entry. The original phrase remains available in history and candidate provenance. The project dirty state updates. The user can undo the commit or create a branch.

### Why this matters

The system has not merely produced five patterns. It has supported a complete creative decision while preserving context, authorship and recoverability.

## 45. Example: delegated arrangement task

**User request:** “Create three transition proposals from the sparse middle section into the final movement. Preserve the lead motif and tempo map. You may change percussion, texture and bass orchestration, but do not move section boundaries.”

The task contract should specify:
- target: transition region;
- context: end of middle section and beginning of final movement;
- protected: lead motif, tempo map, section boundaries;
- allowed: percussion changes, texture changes, bass orchestration;
- candidate count: three;
- commit: manual approval;
- render: preview quality;
- report: structural changes and protected-property checks.

A successful result should provide three different transition strategies, not three nearly identical random variations. The composer should be able to audition each and import only selected layers.

## 46. Example: learning a contextual preference

The composer rejects several candidates because the hi-hat layer is too active during a sparse texture passage. The application may ask whether the user wants to record a preference for this section or task.

It should not silently infer a global preference against active hi-hats. If the user confirms, save a scoped preference such as:

```yaml
preference:
  subject: hi_hat_activity
  desired_direction: lower
  scope:
    project_id: project_001
    section_id: section_middle_sparse
  confidence: explicit
  source: user_confirmation
```

The preference may influence future candidate ranking in that context. It should remain visible and editable.

---

# Part XX — Developer contracts and acceptance templates

## 47. Feature specification template

Every interaction feature should be documented using a consistent template.

```yaml
feature:
  id: UX-LOCAL-REGENERATE
  name: Local Regeneration
  intent: "Regenerate selected musical material without altering unrelated content."

  user:
    primary_role: composer
    prerequisites:
      - project_open
      - target_selected

  scope:
    allowed_targets:
      - Pattern
      - MotifOccurrence
      - Phrase
    default_scope: selected_target

  agency:
    initiative: human_initiated
    approval: required
    auto_commit: false

  state:
    creates_candidates: true
    mutates_committed_state: false
    undoable_after_commit: true

  invariants:
    - preserve_non_target_entities
    - check_target_revision_before_commit
    - preserve_protected_dependencies
    - record_provenance

  failure:
    preserve_last_valid_state: true
    expose_cause: true
    allow_retry: true

  acceptance:
    - target_scope_is_visible
    - candidates_are_auditionable
    - unrelated_entities_are_unchanged
    - commit_is_atomic
    - undo_restores_prior_revision
```

## 48. Acceptance checklist

A feature is not complete until developers can answer yes to the applicable items.

### Intent and scope
- [ ] The user can tell what action will occur.
- [ ] The target scope is visible.
- [ ] Protected objects are visible.
- [ ] Hard constraints and soft preferences are distinct.
- [ ] The control has a documented semantic contract.

### Generation and audition
- [ ] Candidate generation does not overwrite committed material.
- [ ] Candidate states are explicit.
- [ ] Candidates have provenance.
- [ ] Audition does not persistently alter the main mix or project state.
- [ ] Comparison uses a consistent context.
- [ ] Preview limitations are disclosed.

### Selection and commitment
- [ ] Selection is distinct from audition.
- [ ] Commit validates target versions.
- [ ] Dependency policy is explicit.
- [ ] Commit is atomic.
- [ ] Successful commit creates a history entry.

### Editing and recovery
- [ ] Manual edits after generation are tracked.
- [ ] Undo and redo restore exact states.
- [ ] Redo does not rerun stochastic generation.
- [ ] Stale candidates are detected.
- [ ] Failure preserves the last valid state.
- [ ] Recovery after restart is tested.

### Explainability and learning
- [ ] The system shows what changed and what was preserved.
- [ ] Uncertainty is not represented as certainty.
- [ ] Inferred preferences are distinguishable from explicit preferences.
- [ ] Preference scopes are editable and resettable.

### Accessibility and responsiveness
- [ ] Essential functionality is keyboard accessible.
- [ ] Focus is visible and predictable.
- [ ] Status is not communicated by colour alone.
- [ ] Long tasks do not block essential interaction.
- [ ] Generation and rendering can be cancelled where safe.
- [ ] Error messages provide actionable information.

---

# Part XXI — Anti-patterns and prohibited shortcuts

## 49. Anti-pattern catalogue

### 49.1 One-click destructive generation

**Problem:** “Generate” replaces current music with no candidate stage or confirmation.

**Why it fails:** the composer cannot explore safely and may lose accepted material.

**Preferred approach:** create candidates; allow explicit commit.

### 49.2 Unbounded regenerate button

**Problem:** a button changes a large number of dimensions with no stated scope.

**Why it fails:** results are difficult to predict, compare or reproduce.

**Preferred approach:** show target, constraints and allowed mutations.

### 49.3 Opaque creativity slider

**Problem:** a single slider controls unrelated parameters with no explanation.

**Why it fails:** the user cannot form a reliable mental model.

**Preferred approach:** expose meaningful dimensions and show macro mappings.

### 49.4 Automatic global preference learning

**Problem:** every rejection changes the system globally.

**Why it fails:** context-specific choices become inaccurate universal rules.

**Preferred approach:** scoped, transparent and reversible preference signals.

### 49.5 History as a raw event log

**Problem:** history shows function names or parameter IDs.

**Why it fails:** composers cannot understand what happened.

**Preferred approach:** human-readable musical action labels with technical details available.

### 49.6 Preview modifies the project

**Problem:** audition changes plug-in state, transport or automation and leaves it changed.

**Why it fails:** comparison becomes unreliable and creative state is damaged.

**Preferred approach:** isolated preview path and restoration contract.

### 49.7 Candidate ranking without explanation

**Problem:** system declares one candidate “best” without a defined basis.

**Why it fails:** ranking hides trade-offs and may encode inappropriate preferences.

**Preferred approach:** show ranking dimensions and let the composer choose.

### 49.8 Hidden state changes

**Problem:** controls appear to finish before backend state is committed.

**Why it fails:** UI and composition become inconsistent.

**Preferred approach:** explicit pending, succeeded and failed states.

### 49.9 Blocking background work

**Problem:** generation or analysis freezes transport and editing.

**Why it fails:** the tool interrupts the musical thought process.

**Preferred approach:** asynchronous jobs, progress, cancellation and partial results.

### 49.10 False precision

**Problem:** subjective creative judgements are presented as exact universal numbers.

**Why it fails:** users may over-trust arbitrary measurements.

**Preferred approach:** define metrics, disclose limitations and retain qualitative judgement.

---

# Part XXII — Research and design references

The following sources provide useful foundations for this manual. They are not implementation mandates; they should inform design decisions and be interpreted in the context of music-making.

1. **Bougueng Tchemeube, R. et al. (2023).** “Evaluating Human-AI Interaction via Usability, User Experience and Acceptance Measures for MMM-C: A Creative AI System for Music Composition.” *Proceedings of IJCAI 2023*, pp. 5769–5778. DOI: `10.24963/ijcai.2023/640`. The study is useful for separating usability, experience, acceptance, controllability and predictability in music co-creation systems. https://www.ijcai.org/proceedings/2023/640
2. **Thelle, N. J. W. (2022).** *Mixed-initiative music making: Collective agency in interactive music systems.* Norwegian Academy of Music doctoral research. Useful for thinking about interaction as a reciprocal creative process rather than one-way command execution. https://nmh.no/en/research/projects/notto-thelle-completed-phd
3. **Hutchins, E. L., Hollan, J. D. & Norman, D. A. (1985).** “Direct Manipulation Interfaces.” *Human–Computer Interaction*, 1, 311–338. Foundational discussion of directness, the relationship between intention and available action, and representations that behave like the objects they represent. https://hci.ucsd.edu/hollan/direct-manip.pdf
4. **Shneiderman, B. and later HCI literature on direct manipulation.** The practical principles of visible objects, rapid incremental operations, immediate feedback and reversibility are useful for composition interfaces. See the discussion in the *Oxford Handbook of Human-Computer Interaction* chapter on graphical user interfaces: https://academic.oup.com/book/60808/chapter/529002273
5. **W3C (2024).** *Web Content Accessibility Guidelines (WCAG) 2.2.* W3C Recommendation, 12 December 2024. Use as a reference for perceivability, operability, understandable interaction and robust content in web-facing UI components; adapt carefully to desktop application contexts. https://www.w3.org/TR/wcag/
6. **W3C Web Accessibility Initiative.** *Accessibility Principles.* Practical guidance on keyboard operation, input flexibility and adequate time. https://www.w3.org/WAI/fundamentals/accessibility-principles/
7. **Interaction Design Foundation.** *Interaction Design Patterns — Undo and History.* A secondary reference for history models, object-based undo and the complexity of selective undo. Verify design decisions against primary HCI research and the application's own data model. https://ixdf.org/literature/book/the-glossary-of-human-computer-interaction/interaction-design-patterns
8. **Research on authorship and creative AI interaction.** “Negotiating Authorship: Sound, Gesture and Generative AI.” Useful as a current example of research into how control and authorship are negotiated in generative audio systems. https://vcdrc.aut.ac.nz/our-research/negotiating-authorship-sound%2C-gesture-and-generative-ai

---

# Appendix A — Reference data contracts

The examples below are illustrative JSON contracts. They should be adapted to the canonical schema and validation system defined in the Musical Ontology volume. IDs are examples, not reserved production values.

## A1. Interaction intent

```json
{
  "intent_id": "intent_001",
  "project_id": "project_001",
  "actor_id": "composer_local",
  "target": {
    "entity_type": "Phrase",
    "entity_id": "phrase_002",
    "revision": 4
  },
  "goal": "increase_fragmentation",
  "description": "Create a more interrupted phrase without losing its motif identity.",
  "scope": "phrase",
  "hard_constraints": [
    "preserve_duration",
    "preserve_pitch_contour"
  ],
  "soft_preferences": [
    "moderate_density",
    "retain_original_opening_gesture"
  ],
  "protected_entities": ["phrase_003", "bass_motif_01"],
  "agency_profile_id": "agency_manual_approval"
}
```

## A2. Candidate set

```json
{
  "candidate_set_id": "cset_001",
  "request_id": "request_001",
  "source_project_revision": 42,
  "target_entity_id": "phrase_002",
  "target_revision": 4,
  "status": "ready_to_audition",
  "candidates": [
    {
      "candidate_id": "cand_001",
      "revision": 1,
      "status": "ready_to_audition",
      "seed": 41827,
      "parent_candidate_id": null,
      "validation": {
        "valid": true,
        "hard_constraints_passed": true,
        "warnings": []
      },
      "diff_summary": {
        "events_added": 2,
        "events_removed": 1,
        "events_moved": 3
      }
    }
  ]
}
```

## A3. Audition session

```json
{
  "audition_session_id": "aud_001",
  "project_id": "project_001",
  "candidate_ids": ["cand_001", "cand_002"],
  "mode": "context_ab",
  "context_range": {
    "start_beat": 48,
    "end_beat": 64
  },
  "sync_mode": "musical_position",
  "level_match": true,
  "preview_graph_id": "preview_graph_001",
  "restoration_required": true
}
```

## A4. Selection decision

```json
{
  "decision_id": "decision_001",
  "actor_id": "composer_local",
  "candidate_id": "cand_002",
  "decision": "selected_for_commit",
  "context": {
    "task": "phrase_variation",
    "target_entity_id": "phrase_002"
  },
  "comment": "Better rhythmic interruption while retaining the opening identity."
}
```

## A5. Commit operation

```json
{
  "commit_id": "commit_001",
  "candidate_id": "cand_002",
  "target_entity_id": "phrase_002",
  "expected_target_revision": 4,
  "dependency_policy": "update_selected_occurrence_only",
  "atomic": true,
  "create_history_entry": true,
  "create_snapshot": true
}
```

## A6. History entry

```json
{
  "history_entry_id": "hist_001",
  "project_id": "project_001",
  "revision_before": 42,
  "revision_after": 43,
  "actor": "composer_local",
  "operation": "commit_candidate",
  "target": {
    "entity_type": "Phrase",
    "entity_id": "phrase_002"
  },
  "label": "Replaced phrase rhythm — preserved opening motif",
  "undo_available": true,
  "provenance": {
    "candidate_id": "cand_002",
    "generation_request_id": "request_001"
  }
}
```

## A7. Preference signal

```json
{
  "preference_signal_id": "pref_001",
  "source": "explicit_user_feedback",
  "action": "reject",
  "subject": "event_density",
  "direction": "lower",
  "scope": {
    "project_id": "project_001",
    "section_id": "section_sparse_middle"
  },
  "context": {
    "task": "percussion_variation"
  },
  "persistence": "project_scoped",
  "user_confirmed": true
}
```

---

# Appendix B — Interaction event payload examples

## B1. Candidate generated

```json
{
  "event": "generation.candidate_created",
  "event_id": "evt_001",
  "correlation_id": "request_001",
  "timestamp": "2026-01-01T12:00:00Z",
  "project_id": "project_001",
  "project_revision": 42,
  "candidate_id": "cand_001",
  "target_entity_id": "phrase_002",
  "candidate_index": 1,
  "candidate_count_expected": 5
}
```

## B2. Commit conflict

```json
{
  "event": "composition.commit_conflicted",
  "event_id": "evt_002",
  "correlation_id": "commit_001",
  "project_id": "project_001",
  "target_entity_id": "phrase_002",
  "expected_revision": 4,
  "actual_revision": 5,
  "resolution_options": [
    "compare_versions",
    "rebase_candidate",
    "regenerate",
    "cancel"
  ]
}
```

## B3. Task cancelled

```json
{
  "event": "interaction.task_cancelled",
  "event_id": "evt_003",
  "task_id": "task_009",
  "cancel_requested_by": "composer_local",
  "completion_state": "cancelled",
  "valid_candidates_retained": 2,
  "composition_mutated": false
}
```

---

# Appendix C — Composer-facing language guide

The language of the interface shapes the composer's mental model. Use consistent terms.

| Prefer | Avoid when possible | Reason |
|---|---|---|
| Generate candidates | Apply AI | Describes the action without hype |
| Commit candidate | Accept AI | Makes state transition explicit |
| Preserve motif identity | Keep similarity | Explains musical purpose |
| Regenerate phrase | Randomise | Makes target scope clear |
| Protected material | Locked stuff | Precise and consistent |
| Pinned candidate | Favourite output | Distinguishes retention from commitment |
| Stale candidate | Broken result | Explains that the source changed |
| Compare versions | Show AI differences | Works for manual and generated edits |
| Delegated task | Autonomous mode | Clarifies that the task has a bounded contract |
| Inferred preference | Learned taste | Makes uncertainty visible |

Avoid anthropomorphic explanations that claim the software has feelings, taste or intention. It is acceptable to use accessible metaphors in the interface, but technical reports should describe the actual operation.

---

# Appendix D — Design review questions

Before releasing a creative interaction feature, reviewers should ask:

1. What creative problem does this feature solve?
2. What is the smallest useful scope?
3. What does the composer control directly?
4. What does the system decide?
5. Can the composer see the target and protected material?
6. Does the operation create candidates or mutate committed state?
7. How can the user audition and compare the result?
8. How can the user reject or recover from it?
9. Does the operation preserve musical identity where requested?
10. How does the interface explain the result?
11. What happens if the target changes while the task is running?
12. What happens if generation or rendering fails?
13. Does the feature work with keyboard-only interaction?
14. Does it preserve focus and selection across workspaces?
15. Is its state persisted and restored correctly?
16. Does it introduce hidden coupling?
17. How will developers test its invariants?
18. How will composers evaluate its usefulness?

If these questions cannot be answered, the feature is not fully specified.

---

# Appendix E — Final constitutional summary

The purpose of a generative music interface is not to make the machine appear creative. It is to make creative work more possible, more inspectable and more fluid for the person using it.

The system should provide a meaningful balance of:

- **Agency:** the composer can direct consequential decisions.
- **Exploration:** the system can propose possibilities the composer did not anticipate.
- **Control:** requests have clear scope and predictable boundaries.
- **Surprise:** candidates can be genuinely unexpected without becoming arbitrary.
- **Memory:** accepted work, rejected ideas and important decisions remain recoverable.
- **Transparency:** the system communicates what it changed and what it preserved.
- **Reversibility:** experimentation does not threaten the integrity of the composition.
- **Continuity:** the composer can move from ideation to arrangement, sound design, mixing and export without losing context.
- **Respect:** the system supports the composer's authorship instead of competing with it.

A successful generative instrument is not one that makes the greatest number of decisions. It is one that makes the right decisions available to the right participant at the right level of control.

The final measure is not how autonomous the software appears. It is whether the composer can make a better, more personal, more coherent and more ambitious musical work with it—and remain meaningfully in charge of that work.

---

## Document maintenance

This manual should be reviewed whenever the interaction model, candidate lifecycle, agency policy, history system, preference-learning behaviour or creative workflow changes materially.

A change to a core interaction contract should include:
- an updated schema or API contract;
- migration considerations where persisted state is affected;
- acceptance tests for the affected invariants;
- a UX review of scope, clarity and reversibility;
- an updated example workflow;
- a record of why the change is compatible with the IDM Generative Instrument Constitution.

**Governing rule:** no interaction feature is complete merely because its control works. It is complete when its musical intent, scope, result, consequences, recovery path and effect on composer agency are all understandable and testable.
