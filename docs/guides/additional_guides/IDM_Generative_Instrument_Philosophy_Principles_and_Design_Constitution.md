# IDM Generative Instrument
## Philosophy, Principles & Design Constitution

**A governing document for developers of algorithmic, procedural, and intelligent electronic-music composition systems**

- **Document type:** Foundational philosophy, architecture constitution, and engineering reference
- **Status:** Proposed canonical baseline
- **Version:** 1.0
- **Date:** 26 November 2026
- **Audience:** Music-software architects, generative-system developers, composers, sound designers, researchers, technical artists, and evaluators
- **Scope:** Compositional intelligence, musical intent, system boundaries, generative decision-making, creative agency, evaluation, and implementation governance

---

# Preamble — Why this constitution exists

A music-generation program can produce notes, rhythms, audio, and even convincing stylistic surfaces without composing a meaningful work. It can generate a thousand patterns without understanding which one belongs in a particular section. It can produce an intricate rhythm that has no relationship to the bass, a beautiful timbre that obscures the musical foreground, or a technically polished render whose form has no direction.

The problem is not a lack of algorithms. It is the absence of a coherent philosophy governing how those algorithms are used.

This document defines that philosophy.

An **IDM Generative Instrument** is not simply a random pattern generator, an automatic sequencer, a preset browser, a MIDI exporter, or a machine that imitates a catalogue of stylistic surface features. It is a compositional environment that proposes, develops, organises, evaluates, revises, and realises musical material under an explicit artistic intention.

The term *instrument* is deliberate. An instrument gives a human being expressive control, exposes meaningful possibilities, responds to gestures, preserves performance and material, and invites exploration. A generative instrument adds the ability to propose musical relationships and develop material, but it does not eliminate the composer’s authorship or judgement.

The system must therefore combine two forms of discipline:

1. **Musical discipline:** every decision must be considered in relation to musical identity, context, perception, development, and form.
2. **Engineering discipline:** every decision must be represented, traceable, reproducible when required, testable, and safely editable.

Neither discipline is optional. A system that is musically imaginative but unreliable is not a dependable instrument. A system that is technically elegant but compositionally shallow is not an intelligent composition system.

This constitution establishes the principles that all subsystems, algorithms, interfaces, and future features must respect.

---

# How to use this document

## 1. Authority and normative language

This is a **governing specification**, not a tutorial or a list of optional ideas. The words below have precise meanings:

- **MUST / MUST NOT** — a binding requirement. Violating it is a defect unless an explicitly approved exception is documented.
- **SHOULD / SHOULD NOT** — a strong recommendation. A deviation requires a reason and an understood trade-off.
- **MAY** — an optional capability that can be implemented when appropriate.
- **INVARIANT** — a property that must remain true across operations, transformations, and subsystem boundaries.
- **CONTRACT** — a defined agreement about inputs, outputs, permissions, side effects, and failure behaviour.
- **MUTATION** — a controlled transformation of existing musical material.
- **COMMIT** — the act of accepting a proposed result into the authoritative composition state.
- **CANDIDATE** — a generated possibility that has not yet been committed.

A feature is not compliant merely because its code runs. It must preserve the contracts relevant to its operation.

## 2. What this constitution governs

This document governs:

- The artistic and compositional identity of the software.
- The relationship between intention and generated output.
- The hierarchy of musical decisions.
- The meaning and authority of musical data.
- The boundaries between planners, generators, evaluators, renderers, and interfaces.
- The use of randomness, constraints, search, and optimisation.
- The preservation and transformation of musical identity.
- Human agency, creative interaction, and explainability.
- Evaluation and quality assurance.
- Reproducibility, provenance, and project integrity.
- The method by which new features are proposed, implemented, tested, and accepted.

## 3. What this constitution does not prescribe

It does not require one particular algorithm, synthesis method, programming language, UI framework, genre template, tempo range, meter, harmonic language, or rendering engine.

A Markov model, grammar, constraint solver, evolutionary search, neural model, hand-authored rule system, or hybrid method may be appropriate. The constitution judges them by the musical and engineering responsibilities they fulfil, not by novelty or fashion.

It also does not claim to define the one correct form of IDM. IDM is historically broad, internally diverse, and resistant to a single compositional formula. The software must support a range of experimental electronic practices rather than encode one narrow stereotype.

## 4. Relationship to the four domain manuals

The existing guides form the domain-specific knowledge base. This constitution governs how that knowledge is translated into software behaviour.

| Reference volume | Primary responsibility | Relationship to this constitution |
|---|---|---|
| **IDM: A Field Guide for Composers, Producers, and Programmers** | Historical context, core musical grammar, mathematics, programming orientation, production, and listening | Establishes the broad domain vocabulary and working context |
| **IDM: Advanced Composition and Generative Systems** | Perception, phrase syntax, counterpoint, long-form development, orchestration, generative approaches, scheduling, and software models | Provides advanced compositional and generative methods |
| **IDM Composition Atlas** | Pattern families, pattern relationships, bass and melodic cells, phrase functions, track forms, and complete blueprints | Provides practical compositional material and formal options |
| **IDM Sound Design Manual** | Timbre, synthesis, modulation, effects, hybrid sound structures, spatial design, and sound-object construction | Provides the sound-realisation vocabulary |
| **This constitution** | Philosophy, principles, system responsibilities, decision rights, contracts, and governance | Defines what the software is allowed and expected to do with the domain knowledge |

When a detailed musical technique is needed, consult the relevant domain manual. When deciding how a subsystem should behave, how its decisions should be constrained, or how a feature should be validated, consult this constitution.

If a future guide conflicts with a binding principle here, the conflict must be resolved explicitly. A domain manual must not silently override a system invariant.

---

# Part I — The identity of the generative instrument

## 1. Definition

An **IDM Generative Instrument** is a creative software system that transforms explicit and implicit musical intentions into candidate compositions, develops those compositions through controlled musical operations, supports human selection and revision, and realises accepted material as editable and reproducible musical projects and audio.

The defining capability is not the quantity of material it can generate. It is its ability to maintain meaningful relationships between:

- intention and result;
- local events and larger structures;
- repetition and change;
- independent musical layers;
- sound identity and musical role;
- surprise and intelligibility;
- automatic decisions and human authorship;
- symbolic composition and rendered sound.

A system that produces an interesting two-bar loop has demonstrated local generation. A system that can explain how that loop relates to a phrase, how the phrase develops through a section, how the section contributes to the whole work, and how the composer can revise any of these relationships has demonstrated compositional architecture.

## 2. Generator, assistant, instrument, and co-creator

These terms describe different interaction models. They must not be used interchangeably.

### 2.1 Generator

A generator produces material from parameters, rules, seeds, or models. It may operate without a human present. Generation alone does not imply musical understanding or useful compositional control.

### 2.2 Assistant

An assistant responds to a human’s request, offers alternatives, performs bounded operations, and explains relevant decisions. It should not assume that a suggestion is accepted.

### 2.3 Instrument

An instrument exposes a stable set of expressive controls and a responsive relationship between gesture and result. It should be discoverable, playable, and predictable enough to build skill, while retaining depth and surprise.

### 2.4 Co-creative system

A co-creative system participates in an iterative exchange: the person directs, the system proposes, the person evaluates, and both actions influence the next state. The person remains able to inspect, revise, reject, and preserve the result.

The system MAY support all four modes, but it MUST make the active mode clear. It MUST NOT describe an unreviewed candidate as a finished, human-approved composition.

## 3. The central distinction: generation is not composition

Generation answers: *What material could occur?*

Composition answers additional questions:

- Why should this material occur here?
- What earlier material does it remember or transform?
- What expectation does it establish?
- What does it contrast with?
- What does it cause the listener to notice?
- How does it affect the direction of the work?
- What should happen because it occurred?
- When should it stop, return, or be abandoned?

The software MUST distinguish **material production** from **compositional decision-making**. It MAY combine them inside one implementation, but the conceptual responsibilities must remain identifiable and testable.

## 4. The purpose is expressive possibility, not genre imitation

IDM is not reducible to high BPM, unusual time signatures, glitch edits, complex breakbeats, obscure synthesis, or frequent parameter changes. Those may be useful materials, but they are not sufficient evidence of a compelling composition.

The software SHOULD support the broader possibilities of experimental electronic composition:

- groove and anti-groove;
- stable pulse and unstable surface;
- asymmetry and metric regularity;
- tonal, modal, atonal, and noise-based organisation;
- repetition, process, fragmentation, and transformation;
- delicate, sparse, aggressive, dense, and atmospheric states;
- acoustic, synthetic, sampled, resynthesised, and hybrid sound objects;
- dance-oriented continuity and deep-listening form.

A composition MAY be simple, repetitive, quiet, slow, or sparse. Complexity is an available resource, not an admission requirement.

## 5. The system's artistic promise

The system promises to help a composer explore possibilities that are difficult, tedious, or cognitively expensive to construct manually. It does not promise that every generated result will be good, original, or suitable.

Its value should be measured by whether it helps the composer:

1. discover viable ideas;
2. make relationships audible and editable;
3. develop material with less mechanical friction;
4. explore alternatives without losing the current work;
5. preserve successful decisions;
6. recognise weaknesses;
7. finish and export a coherent work.

The system MUST make failure recoverable. It SHOULD make good ideas easier to notice, preserve, and develop.

---

# Part II — The constitutional principles

The following principles are binding design guidance. Each principle includes the software consequence that follows from it.

## Principle 1 — Artistic intention precedes implementation

A feature must begin with a musical or creative problem, not with an available algorithm or an attractive interface control.

**Software consequence:** every substantial generative feature MUST state what musical intention it serves, what input expresses that intention, what result it is expected to produce, and how the result will be evaluated.

A feature request such as “add more randomness” is incomplete. A better request is “allow a percussion layer to become less predictable over an eight-bar span while preserving the kick anchor and the recognisable identity of the phrase.”

## Principle 2 — Music is a system of relationships

Musical entities gain meaning through relationships: repetition, contrast, support, interruption, doubling, displacement, response, transformation, anticipation, and return.

**Software consequence:** generated entities SHOULD retain explicit relationships to the materials, phrases, sections, and decisions that give them context. The system MUST NOT treat every track as an unrelated list of events.

## Principle 3 — A composition has identity

A composition must retain a recognisable identity even as its material changes. Identity may arise from rhythm, pitch, contour, timbre, process, register, spatial behaviour, phrase syntax, or the combination of these dimensions.

**Software consequence:** the project SHOULD carry an explicit identity model or set of identity-bearing commitments. A mutation MUST identify which identity dimensions it preserves, relaxes, or changes.

Identity is not the same as keeping all notes unchanged. A motif can be recognisable after transposition, truncation, rhythmic expansion, timbral substitution, or reinterpretation if the relevant defining features survive.

## Principle 4 — Hierarchy governs musical decisions

Local choices exist inside larger contexts. An event belongs to a pattern; a pattern contributes to a phrase; a phrase performs a section-level function; a section contributes to the whole form.

**Software consequence:** lower-level operations MUST respect higher-level constraints unless an authorised operation explicitly changes those constraints. A note generator must not silently invalidate a frozen motif. A pattern mutation must not unexpectedly rewrite the section plan.

## Principle 5 — Repetition establishes memory

Repetition gives the listener a reference frame. It makes later deviation perceptible and allows material to acquire identity.

**Software consequence:** variation engines SHOULD know what is being repeated, how often it has appeared, what features establish recognition, and what degree of change is currently appropriate.

Repetition is not automatically a flaw. The system MUST NOT add variation merely because a loop has repeated a predetermined number of times.

## Principle 6 — Variation must have a relationship to its source

Variation is meaningful when the listener can perceive a relationship between the original and the changed material, unless the change is deliberately designed as rupture or replacement.

**Software consequence:** transformations SHOULD retain lineage and declare their transformation type. The engine SHOULD distinguish continuation, ornamentation, revoicing, displacement, fragmentation, expansion, reduction, reinterpretation, and replacement.

## Principle 7 — Surprise is contextual

An event is surprising relative to an established expectation. The same event may feel predictable in one context and disruptive in another.

**Software consequence:** surprise generation SHOULD consider local musical context, recent history, structural position, and the composition's current state. Global random probability alone is insufficient to model musical surprise.

## Principle 8 — Complexity must serve perception

Complexity is valuable when it reveals, intensifies, destabilises, or transforms a musical idea. Complexity without perceptual purpose can become noise in the structural sense, even when the audio is not literally noisy.

**Software consequence:** the system SHOULD distinguish event density, rhythmic complexity, spectral density, harmonic activity, timbral movement, and perceptual attention. It MUST NOT collapse these into a single “complexity” parameter without an explicit mapping.

## Principle 9 — Every layer must have a role or a deliberate reason not to have one

A layer may anchor, support, answer, interrupt, shadow, contradict, decorate, destabilise, or become the foreground. Some layers are intentionally ambiguous, but ambiguity itself can be a design choice.

**Software consequence:** generated voices SHOULD have a role description or a declared exploratory status. Role-aware constraints SHOULD guide register, activity, articulation, density, and timbral selection.

## Principle 10 — Independence must produce interaction

Independent patterns are useful because they can create interlocking relationships. Independence without interaction can result in unrelated layers competing for attention.

**Software consequence:** when several voices are generated independently, the system SHOULD evaluate their combined behaviour after generation. Independent creation MUST NOT be treated as proof of successful orchestration.

## Principle 11 — Silence and omission are compositional actions

A rest, missing layer, withheld entrance, abrupt cut, or reduction in density can carry more meaning than another event.

**Software consequence:** absence MUST be representable in the composition model as an intentional state or event, not only as missing data. The system SHOULD generate subtraction and withdrawal as first-class developmental operations.

## Principle 12 — Sound is part of the composition, not decoration after it

Timbre, envelope, space, distortion, resonance, noise, and processing can carry motif, rhythm, harmony, form, and memory.

**Software consequence:** symbolic composition and sound realisation MUST communicate through stable musical roles and event semantics. The engine SHOULD allow timbral and spatial parameters to participate in development, while keeping their implementation distinct from the abstract musical intention.

## Principle 13 — Energy is multidimensional

Loudness is not the same as energy, and energy is not the same as density. A quiet passage can be tense; a loud passage can be static; a sparse passage can be overwhelming.

**Software consequence:** global form planning SHOULD use several independent dimensions such as activity, register, transient strength, spectral brightness, harmonic tension, rhythmic insistence, spatial scale, and perceived intensity. One scalar “energy” curve may be used as a summary, but it MUST NOT erase the underlying dimensions.

## Principle 14 — The listener is part of the system model

The composition is not only a data structure or waveform. It is an organised experience unfolding in perception and time.

**Software consequence:** evaluation SHOULD consider attention, foreground/background, masking, grouping, expectation, contrast, and memory. Signal-level validity is necessary but does not establish perceptual success.

## Principle 15 — Local coherence and global direction are different responsibilities

A phrase can be internally coherent while the full track lacks direction. A track can have a compelling arc while containing a deliberately unstable phrase.

**Software consequence:** evaluation MUST operate at multiple timescales. Event- and pattern-level checks cannot substitute for phrase-, section-, and composition-level evaluation.

## Principle 16 — Constraints are creative material

Restrictions can define identity and make exploration productive. A frozen pulse, restricted pitch field, limited sound palette, or fixed duration can focus invention.

**Software consequence:** constraints MUST be explicit, typed, scoped, and inspectable. The engine SHOULD distinguish hard constraints, soft preferences, temporary goals, and optional suggestions.

## Principle 17 — A constraint must have an owner

When two requirements conflict, the system needs a predictable way to determine which one prevails.

**Software consequence:** every constraint SHOULD have a scope, source, priority, and resolution policy. The engine MUST NOT silently discard a constraint because a later generator found it inconvenient.

## Principle 18 — Randomness must be governed

Randomness is a method of exploring possibilities, not a substitute for musical judgement.

**Software consequence:** random decisions SHOULD use explicit seeds, bounded distributions, contextual weights, and recorded decision provenance. The system MUST support deterministic replay where reproducibility is requested.

## Principle 19 — Candidates are not commitments

Generation produces proposals. A proposal becomes part of the composition only through an explicit selection or commit operation, whether initiated by the user or by a documented autonomous policy.

**Software consequence:** candidate state MUST be separate from authoritative project state. Rejected candidates MUST NOT overwrite accepted material. Autonomous commit behaviour MUST be visible and reversible.

## Principle 20 — Human agency is a first-class requirement

The composer must remain able to inspect, compare, edit, reject, preserve, and override generated material.

**Software consequence:** the interface MUST distinguish suggested, accepted, frozen, edited, and rejected states. The software MUST NOT trap the user in an opaque generation loop or make manual editing unnecessarily difficult.

## Principle 21 — Controls must have musical semantics

A control should correspond to a comprehensible musical intention rather than expose an arbitrary parameter with a misleading label.

**Software consequence:** semantic controls MUST document their scope, expected effects, side effects, and protected dimensions. If a control changes several parameters, the mapping must be inspectable and predictable enough to learn.

## Principle 22 — Explain decisions without pretending to explain art completely

The system should explain what rule, constraint, relationship, or context influenced a decision. It should not claim that a numerical score proves artistic quality.

**Software consequence:** decision records SHOULD include reasons and evidence. Explanations MUST be factual descriptions of the system's operation, not anthropomorphic claims about feelings or inspiration.

## Principle 23 — Reproducibility protects creative work

A composer must be able to return to a successful state, reproduce a render, or understand why a new result differs.

**Software consequence:** project state, generator versions, seeds, relevant parameters, material lineage, and rendering configuration SHOULD be preserved. A random seed alone is not sufficient if algorithms, assets, plug-ins, or versioned resources have changed.

## Principle 24 — Editability is part of output quality

A beautiful audio file that cannot be revised may be an acceptable final deliverable in some contexts, but it is not a complete editable project.

**Software consequence:** the system SHOULD preserve symbolic material, source references, automation, routing, sound definitions, and export metadata whenever possible. Audio-only output MUST be labelled as such.

## Principle 25 — A composition should be finishable

A generator that can endlessly add detail but cannot support endings, closure, release, or deliberate abandonment is incomplete as a composition system.

**Software consequence:** the architecture MUST support formal completion states, ending strategies, stopping criteria, and finalisation workflows. “Continue generating” cannot be the only available response to an unfinished composition.

## Principle 26 — Simplicity is a valid artistic outcome

The software must not equate sophistication with the number of tracks, parameters, notes, algorithms, or transformations used.

**Software consequence:** sparse, repetitive, static, minimal, and highly constrained compositions MUST remain valid outcomes. Evaluation should reward fulfilment of the brief, not maximal activity.

## Principle 27 — Technical correctness and artistic success are separate axes

A technically correct file may be musically weak. A musically compelling draft may contain a clipping transient or an unfinished render. These conditions require different diagnostics.

**Software consequence:** the system MUST separate technical validation, musical diagnostics, and subjective artistic evaluation. Passing one category MUST NOT imply passing the others.

## Principle 28 — Failure must be visible and recoverable

A failed generation, missing plug-in, invalid parameter, or rendering error must not silently corrupt accepted musical material.

**Software consequence:** operations SHOULD be transactional. Errors MUST be reported with relevant context, and the last known-good state MUST remain recoverable.

## Principle 29 — Musical diversity must not become arbitrary inconsistency

A system should support different compositional identities, but each generated result should still be internally governed by its own brief and material relationships.

**Software consequence:** diversity should be explored across candidates, not produced by unconstrained switching of every parameter within one composition.

## Principle 30 — The architecture should preserve room for discovery

The constitution must be firm about invariants without prescribing every artistic outcome. A creative instrument must leave space for results that its designers did not anticipate.

**Software consequence:** hard requirements should protect integrity, while musical preferences should remain adjustable and discoverable. The system MUST NOT turn every aesthetic recommendation into a universal prohibition.

---

# Part III — The musical ontology: what the software believes exists

This section establishes conceptual definitions. It does not replace the separate Musical Ontology and Data Architecture manual proposed for the collection; it defines the minimum shared vocabulary that every module must use consistently.

## 6. The composition as a structured work

A composition is an organised, time-dependent network of musical entities and relationships. It is not merely a rendered file or a flat collection of tracks.

A useful conceptual hierarchy is:

```text
Composition Brief
└── Composition
    ├── Movement / Global Span
    │   ├── Section
    │   │   ├── Phrase
    │   │   │   ├── Motif / Material Object
    │   │   │   │   ├── Pattern / Voice Behaviour
    │   │   │   │   │   └── Musical Event
    │   │   │   └── Relationship / Transformation
    │   │   └── Section-level transition
    │   └── Long-range formal relationship
    └── Realisation
        ├── Instrument / Sound Object
        ├── Routing and Processing
        ├── Performance and Automation
        └── Render / Export
```

This hierarchy is conceptual, not a rule that every composition must contain every entity or have a strictly nested structure. A process-based composition may not use conventional phrases. A sound collage may organise by material and transition. A generative work may have branches or parallel timelines. The model must support these cases without forcing them into an unsuitable song template.

## 7. Canonical terms

### 7.1 Artistic intent

The declared creative direction of a work: its desired character, processes, materials, constraints, and intended listening experience.

### 7.2 Composition brief

A structured, editable representation of artistic intent. It is not a prompt string alone. It has fields, priorities, scope, and unresolved choices.

### 7.3 Composition identity

A set of recognisable characteristics and commitments that distinguish the work and constrain acceptable transformations.

### 7.4 Material

A reusable musical substance or idea: a rhythmic cell, pitch contour, sound object, spectral gesture, noise process, sample fragment, or other identifiable source.

### 7.5 Motif

A recognisable idea whose identity may be carried by rhythm, interval, contour, timbre, register, articulation, spatial behaviour, or a combination of dimensions.

### 7.6 Pattern

A repeatable or cyclic organisation of events or absences. A pattern may be rhythmic, melodic, harmonic, timbral, spatial, or procedural.

### 7.7 Voice

A perceptually or functionally coherent musical line or layer. A voice may be rendered by one instrument, several instruments, or a changing sound source.

### 7.8 Role

The compositional function a voice or material performs in context, such as anchor, foreground, response, support, counterline, punctuation, texture, or destabiliser.

### 7.9 Phrase

A unit of musical behaviour with a recognisable function or sense of completion, not necessarily a fixed number of bars.

### 7.10 Section

A larger formal region with a distinct state, function, or relationship to other regions.

### 7.11 Transformation

A defined operation that changes selected properties of material while stating what is preserved, altered, and potentially lost.

### 7.12 Event

An atomic occurrence with musical meaning and execution data: onset, duration or release behaviour, pitch or control value, intensity, voice, articulation, and relevant context.

### 7.13 Realisation

The mapping from abstract musical intent and symbolic events to sound sources, performance behaviour, processing, and rendered audio.

### 7.14 Candidate

A possible result produced for inspection or selection. A candidate is not yet authoritative project state.

### 7.15 Commitment

A selected decision that becomes part of the authoritative composition state.

## 8. Relationships are first-class objects

The system SHOULD represent important musical relationships explicitly rather than infer all meaning from coincidental event similarity.

Examples include:

- derived-from;
- answers;
- interrupts;
- doubles;
- shadows;
- reinforces;
- contrasts-with;
- precedes;
- follows;
- transforms;
- returns-as;
- shares-pulse-with;
- displaces;
- harmonises-with;
- occupies-same-attention-region-as;
- replaces;
- continues;
- anticipates;
- resolves;
- deliberately-avoids.

Not every relationship needs a complex object model. The important requirement is that the project can preserve the relationship when it matters to composition, explanation, mutation, or evaluation.

## 9. Material identity is multidimensional

A material should not be identified only by a MIDI event hash or sample filename. Its identity may depend on multiple dimensions.

| Dimension | Example identity feature | Possible transformation |
|---|---|---|
| Rhythm | Accent sequence, duration ratios, onset contour | Displacement, augmentation, fragmentation |
| Pitch | Interval sequence, pitch classes, contour | Transposition, inversion, modal reinterpretation |
| Register | Centre, range, movement profile | Octave transfer, expansion, compression |
| Timbre | Spectral envelope, attack, noise character | Resynthesis, filtering, source substitution |
| Articulation | Staccato, legato, decay, gate behaviour | Lengthening, shortening, accent change |
| Space | Position, width, depth, movement | Rotation, narrowing, distance change |
| Process | Repetition, accumulation, erosion, phase | Acceleration, reversal, interruption |

The system SHOULD allow identity to be weighted by context. For one motif, rhythm may be essential while pitch is flexible. For another, a spectral gesture may be the defining feature.

---

# Part IV — Authority, hierarchy, and decision ownership

## 10. The decision hierarchy

The default hierarchy is:

1. **Project integrity and explicit user commitments** — saved work, locked material, explicit exclusions, and project safety.
2. **Artistic intent** — the declared identity and desired experience.
3. **Global composition architecture** — movement plan, overall process, duration, and large-scale direction.
4. **Section architecture** — section identity, function, contrast, and transition responsibilities.
5. **Phrase architecture** — phrase functions, motif use, local tension, and cadence or interruption behaviour.
6. **Voice and role design** — the relationship between independent layers.
7. **Material and pattern design** — rhythms, motifs, harmonic cells, sound gestures, and transformations.
8. **Event and performance detail** — note positions, velocities, articulation, microtiming, and controller motion.
9. **Sound realisation and rendering** — synthesis, effects, routing, and output formatting.

This hierarchy is a default authority model, not a claim that sound design is less artistic than form. It prevents a low-level technical operation from silently changing a high-level artistic decision.

A sound-realisation decision may reveal that a symbolic plan is impractical or sonically weak. It may therefore propose a revision to a higher level. It MUST NOT unilaterally rewrite that level. The revision must pass through an authorised decision path.

## 11. Decision ownership

Every subsystem must have a defined decision domain.

| Subsystem | Owns | Must not silently own |
|---|---|---|
| Brief interpreter | Mapping stated intent to structured goals and constraints | Final composition decisions not authorised by the brief |
| Composition director | Global direction, section states, long-range pacing | Note-level details except where needed for a global decision |
| Form planner | Section order, duration proposals, transition goals | Rewriting accepted motifs without permission |
| Phrase planner | Phrase function and local development | Global identity changes |
| Material manager | Material registry, identity, lineage, versioning | Artistic selection without policy or user authority |
| Pattern generators | Candidate patterns within declared constraints | Accepting candidates or changing unrelated layers |
| Pitch/harmony planner | Pitch organisation and voice-leading proposals | Overriding protected rhythmic or structural commitments |
| Orchestrator | Voice roles, register, density, interaction, attention | Changing source material beyond its contract |
| Sound designer / realiser | Mapping roles and events to sound and processing | Rewriting symbolic musical intent without an approved proposal |
| Evaluator | Diagnostics, evidence, warnings, scores where justified | Automatically rejecting or rewriting material unless authorised |
| Mutation engine | Applying bounded transformations | Mutating material outside the declared scope |
| Renderer | Executing the accepted project state as audio | Changing composition state during rendering |
| User interface | Exposing controls, choices, history, and status | Becoming the hidden source of musical truth |

The architecture MAY combine several responsibilities in one class or service, but their contracts must remain separable.

## 12. Conflict resolution

When requirements conflict, resolve them in this order:

1. Protect project integrity and explicit user commitments.
2. Respect hard constraints.
3. Respect higher-priority artistic intent.
4. Preserve composition identity commitments.
5. Satisfy section- and phrase-level goals.
6. Optimise local musical quality.
7. Apply soft preferences.
8. Use defaults only where no meaningful requirement exists.

If two hard constraints conflict, the system MUST report an unresolved conflict. It MUST NOT invent a silent compromise and claim success.

When a soft preference cannot be satisfied, the system SHOULD record the trade-off or offer alternatives.

## 13. Hard constraints, soft preferences, and goals

### Hard constraint

A requirement that must be satisfied for the operation to be valid. Examples: fixed duration, frozen motif, prohibited note range, no change to selected section, required sample rate, or a locked event sequence.

### Soft preference

A desirable characteristic that may be violated if the alternative is better or necessary. Examples: prefer fewer layers, avoid excessive high-frequency activity, lean toward asymmetric phrases, or keep the bass mostly stable.

### Goal

A desired outcome that may be approached but not guaranteed. Examples: increase tension, create a feeling of weightlessness, make the second half more fragmented, or bring a motif back in an altered form.

### Exclusion

A declared forbidden operation or material class. Exclusions may be hard or soft and must be scoped.

The data model MUST distinguish these categories. A text label such as “priority” is insufficient unless its semantics are defined.

---

# Part V — The composition brief and artistic intent

## 14. The CompositionBrief is a first-class project object

The project SHOULD begin with a structured brief, even if the initial brief is small or incomplete.

The brief is not a prompt that gets discarded after generation. It is a persistent reference against which major decisions can be interpreted and evaluated.

A brief should be editable throughout the process. Changes to the brief must create a visible revision and identify which existing decisions may now be inconsistent.

## 15. Recommended brief dimensions

### 15.1 Intent statement

A short description of the work's purpose or central proposition. It may be poetic, technical, or both.

### 15.2 Listening experience

Describe the intended relationship with the listener: immersive, kinetic, intimate, disorienting, meditative, abrasive, playful, fragile, detached, narrative, or another combination.

These are descriptive hypotheses, not guaranteed emotional effects.

### 15.3 Material vocabulary

List the principal materials: breakbeat fragments, metallic resonances, sparse bass cells, tonal fragments, granular air, clipped noise, field recordings, synthetic percussion, or other sources.

### 15.4 Behavioural vocabulary

Describe what the materials should do: rotate, accumulate, erode, answer, fragment, converge, drift, repeat, collide, or disappear.

### 15.5 Formal intention

Specify the desired scale and process: multi-movement, gradual accumulation, cyclic rotation, fragment collage, contrast blocks, continuous evolution, or a more conventional section arc.

### 15.6 Rhythmic and pitch boundaries

These may include pulse, tempo region, meter, grid flexibility, pitch field, harmonic stability, tuning approach, or deliberate absence of tonal hierarchy.

### 15.7 Sound identity

Define the broad source and processing vocabulary without requiring every instrument to be selected in advance.

### 15.8 Constraints and exclusions

State what must remain fixed, what should be avoided, and which aspects are open to exploration.

### 15.9 Duration and delivery

Define target length, expected ending behaviour, export requirements, and whether the result must remain fully editable.

### 15.10 Unresolved questions

The brief SHOULD allow uncertainty to remain explicit. The system may explore alternatives rather than forcing a premature answer.

## 16. Example CompositionBrief

The following is an illustrative specification, not a mandatory template or genre recipe.

```yaml
composition_brief:
  schema_version: 1
  title: "Rotating Machinery / Quiet Horizon"
  intent:
    statement: >
      Build a piece from an unstable mechanical rhythm that gradually
      reveals a fragile, recurring tonal idea. The ending should feel
      like the system has withdrawn rather than reached a conventional climax.
    listening_experience:
      - kinetic
      - uncanny
      - intimate
      - gradually exposed

  identity:
    rhythmic:
      anchor: "slow, sparse low-frequency pulse"
      surface: "asymmetric metallic and granular cycles"
      allowed_instability: "high in upper layers, low in anchor"
    pitch:
      vocabulary: "small pitch field with chromatic interruptions"
      hierarchy: "partially tonal, not continuously functional"
    timbre:
      source_families:
        - sampled mechanical impacts
        - resonant synthesis
        - granular texture
        - restrained tonal source
    development:
      - accumulation
      - phase displacement
      - fragmentation
      - partial return
      - subtraction

  form:
    mode: "continuous process with distinct regions"
    target_duration_seconds: 300
    ending: "withdrawal with residual material"
    fixed_section_count: false

  constraints:
    hard:
      - id: "anchor_identity"
        scope: "composition"
        rule: "preserve the recognisable low-frequency pulse family"
      - id: "editable_output"
        scope: "delivery"
        rule: "retain symbolic events and project metadata"
    soft:
      - id: "avoid_uniform_density"
        rule: "do not keep all layers active at the same time"
      - id: "preserve_negative_space"
        rule: "allow significant periods of reduced activity"

  exploration:
    open_questions:
      - "Should the tonal idea emerge from the resonator or a separate voice?"
      - "Should the final return be recognisable or only implied?"
    candidate_policy:
      generate_alternatives: true
      auto_commit: false

  delivery:
    full_mix: true
    stems: true
    midi: true
    project_manifest: true
```

The actual schema may evolve. Its semantics must remain documented and versioned.

## 17. Brief interpretation contract

The brief interpreter MUST:

- preserve the original user language or source values;
- map intent into typed goals and constraints;
- mark inferred values as inferred rather than user-specified;
- expose ambiguity and conflict;
- avoid treating poetic language as a precise numeric command without a declared mapping;
- retain unresolved questions;
- provide a summary that the composer can correct.

The interpreter SHOULD distinguish literal requirements from aesthetic descriptions. “Exactly 128 bars” is a precise structural constraint. “Restless but weightless” is a creative direction that requires interpretation and exploration.

---

# Part VI — The generative decision philosophy

## 18. Generate possibilities; do not confuse possibility with quality

The system should not assume that the first valid candidate is the best candidate. It should support candidate generation, constraint checking, evaluation, comparison, and selection as separate stages.

A canonical decision cycle is:

```text
Intent / Context
      ↓
Candidate generation
      ↓
Hard-constraint validation
      ↓
Relationship and context analysis
      ↓
Multi-dimensional evaluation
      ↓
Candidate comparison
      ↓
Human selection or authorised policy
      ↓
Commit to project state
      ↓
Record provenance and decision
```

Some real-time or low-latency features may need to commit a result immediately. In that case, the policy must be explicit, the result should remain reversible where possible, and the system should preserve enough information to reconstruct the decision.

## 19. Algorithm neutrality

No algorithm is inherently intelligent because of its category. Rule-based, stochastic, evolutionary, constraint-based, search-based, machine-learning, and hybrid approaches can all be useful.

Algorithm choice should follow the problem:

- A Euclidean process may be useful for distributing pulses.
- A grammar may be useful for controlled structural transformations.
- A Markov model may be useful for local transition behaviour.
- A constraint solver may be useful for satisfying interacting requirements.
- An evolutionary method may be useful for searching a candidate space under a defined fitness model.
- A hierarchical planner may be useful for coordinating decisions across time scales.
- A learned model may be useful for proposing material from examples or representations.
- A human-in-the-loop process may be best when aesthetic judgement cannot be safely automated.

The project SHOULD select the simplest method that can satisfy the musical and operational requirements without foreclosing future expansion.

## 20. Multi-objective judgement

Musical quality is not one number. A candidate may be rhythmically compelling but poorly orchestrated, structurally coherent but unoriginal, sonically beautiful but unrelated to the brief, or technically clean but formally inert.

The system SHOULD evaluate candidates across distinct dimensions, such as:

- brief alignment;
- identity preservation;
- local coherence;
- relationship to existing material;
- rhythmic interest;
- pitch and harmonic behaviour;
- phrase function;
- structural contribution;
- perceptual clarity;
- contrast and development;
- originality or novelty, where meaningfully defined;
- technical feasibility;
- editability and reproducibility.

It SHOULD use a combination of hard constraints, lexicographic priorities, Pareto-style comparison, weighted preferences, or human selection as appropriate.

It MUST NOT treat an arbitrary aggregate score as proof of artistic quality. If a score is displayed, its dimensions and limitations must be visible.

## 21. Context-sensitive generation

Generation should account for:

- the material already present;
- the current phrase and section function;
- recently heard patterns and motifs;
- the expected next event or state;
- the composition identity;
- the current attention map;
- the desired degree of novelty;
- frozen or protected material;
- constraints inherited from higher levels.

A pattern that is compelling in isolation may be wrong in context. Candidate audition and evaluation should therefore occur in musical context whenever feasible.

## 22. Novelty is not novelty for its own sake

The system SHOULD support distinct forms of novelty:

- surface novelty: a new event or ornament;
- relational novelty: a new interaction between known layers;
- transformational novelty: a new version of established material;
- structural novelty: a new formal relationship;
- timbral novelty: a new sound identity;
- process novelty: a new way for material to evolve.

Novelty can be useful, but a new event is not automatically a meaningful event. The system SHOULD test whether novelty contributes to the current intention.

## 23. Repetition, entropy, and bounded randomness

A generative system should be able to create stable repetition, gradual drift, bounded variation, sudden rupture, and return. These are different behaviours and should not be represented by one undifferentiated randomness control.

Recommended controls include:

- variation rate;
- transformation scope;
- novelty budget;
- identity preservation strength;
- recurrence preference;
- allowed deviation range;
- event probability by role;
- section-dependent variation policy.

These controls SHOULD be expressed semantically at the user level and mapped to implementation parameters internally.

## 24. Decision record

Every substantial autonomous decision SHOULD produce a record containing:

- decision identifier;
- timestamp or project-time position;
- subsystem and generator version;
- parent material or context;
- input constraints;
- candidate identifiers;
- selected result;
- random seed or stochastic state where applicable;
- evaluation evidence;
- reason or policy for selection;
- affected project entities;
- reversible operation or rollback reference.

A decision record is not an essay. It is an auditable description of what the system did.

---

# Part VII — Mutation contracts and protection of identity

## 25. Mutation must be explicit

A mutation is a controlled transformation of existing musical material. It is not unrestricted regeneration disguised as editing.

Every non-trivial mutation MUST define:

1. **Target:** what entity or region may change?
2. **Scope:** event, pattern, phrase, voice, section, or full composition?
3. **Purpose:** what musical goal should the operation serve?
4. **Preserve set:** what must remain unchanged?
5. **Change set:** what may be altered?
6. **Forbidden set:** what must not be altered?
7. **Dependencies:** which relationships or derived data may need updating?
8. **Validation:** how will success and failure be determined?
9. **Provenance:** how will the new material relate to the original?
10. **Rollback:** how can the operation be reversed?

## 26. Mutation classes

The following categories SHOULD be distinguished:

- **Variation:** a limited change that preserves recognisable identity.
- **Development:** a change that advances the material or gives it a new function.
- **Reorchestration:** a change in sound source, register, role allocation, or distribution while preserving selected musical content.
- **Reinterpretation:** a change in how material is perceived or functionally understood.
- **Fragmentation:** the extraction or rearrangement of parts of material.
- **Expansion:** increasing duration, range, density, or internal detail.
- **Reduction:** removing or simplifying elements while preserving selected identity features.
- **Displacement:** shifting temporal or metric position.
- **Transformation:** changing one or more defining dimensions under a declared mapping.
- **Replacement:** substituting a new object for the old one; lineage may be retained, but identity is not assumed.
- **Rupture:** an intentional break from established material or expectation.

The system MUST NOT call a replacement a variation simply because both operations produce new notes.

## 27. Example mutation contract

```yaml
mutation:
  id: "mutate-upper-percussion-07"
  operation: "controlled_rhythmic_variation"
  target:
    entity: "pattern"
    id: "upper-percussion-A"
    scope: "current-phrase"

  purpose:
    - "increase local rhythmic tension"
    - "retain the section's pulse identity"

  preserve:
    - "kick-anchor-onsets"
    - "phrase-duration"
    - "primary-accent-family"

  may_change:
    - "secondary-onset-positions"
    - "ghost-event-count"
    - "accent-strength"

  must_not_change:
    - "tempo-map"
    - "frozen-bass-material"
    - "section-boundaries"

  limits:
    max_onset_displacement_subdivisions: 2
    max_added_events_per_phrase: 3

  validation:
    - "hard_constraints_pass"
    - "anchor_identity_preserved"
    - "no_unintended_phrase_length_change"
    - "audition_in_context"

  provenance:
    parent_material_id: "upper-percussion-A"
    record_transformation: true
    deterministic_seed: 84217
```

The numbers are illustrative. A real system should use values appropriate to its time representation and musical context.

## 28. Mutation budgets

A mutation budget limits how much an operation can change. It may apply to event count, pitch distance, onset displacement, spectral movement, duration, layer count, or another relevant dimension.

A mutation budget is not a universal law. It is a mechanism for making scope explicit and preventing accidental overreach.

The system SHOULD support different budgets for:

- exploratory candidates;
- conservative variation;
- phrase development;
- section transformation;
- deliberate rupture.

## 29. Frozen material and dependency protection

Material may be frozen at different levels:

- freeze exact event data;
- freeze identity features but permit limited variation;
- freeze timing but permit pitch or timbre changes;
- freeze phrase duration but permit internal changes;
- freeze the source object but allow reorchestration;
- freeze only the relationship to another entity.

A freeze operation MUST have a defined meaning. A vague “locked” state that different modules interpret differently is not acceptable.

When an entity changes, the system SHOULD detect affected dependants: derived motifs, linked patterns, automation mappings, evaluation results, caches, and rendered previews. It MUST invalidate or update those dependencies safely.

---

# Part VIII — Perception, orchestration, and the listening model

This constitution does not reproduce the full perceptual-orchestration manual. It establishes the principle that perceptual organisation must be an explicit concern across the system.

## 30. The mix is not the only place where perception is managed

Perceptual clarity is influenced by composition, register, articulation, density, rhythmic placement, source identity, timbre, spatial position, and mixing. A problem created by composition should not automatically be delegated to EQ or compression.

The system SHOULD consider perceptual relationships before rendering and again after audio realisation.

## 31. Attention is a limited resource

A listener cannot attend equally to every detail at every moment. A composition can create foreground, background, temporary focus, distraction, ambiguity, and reorientation.

The system SHOULD be able to describe intended attention, even if it cannot perfectly predict actual human perception.

An attention plan might identify:

- primary foreground;
- secondary foreground;
- supporting layer;
- ambient or background layer;
- deliberately obscured material;
- material waiting to emerge;
- material that should recede.

These roles may change over time.

## 32. Perceptual density is not event count

The system MUST distinguish at least conceptually between:

- event density;
- onset density;
- rhythmic complexity;
- pitch activity;
- spectral occupancy;
- transient density;
- modulation activity;
- spatial activity;
- perceived attention competition.

A sparse set of long resonant sounds may occupy a large perceptual space. A dense collection of short, similar clicks may be grouped into one texture. The system should avoid assuming that more events always mean more perceived density.

## 33. Orchestration is relationship design

Orchestration is not merely assigning presets to tracks. It is the design of how voices coexist and interact.

The orchestration subsystem SHOULD evaluate:

- functional overlap;
- register overlap;
- transient competition;
- spectral overlap;
- rhythmic coincidence;
- articulation compatibility;
- masking risk;
- stereo and depth conflicts;
- identity similarity;
- intentional unison or doubling.

Overlap is not inherently bad. It becomes a problem when it undermines the intended listening relationship.

## 34. Energy and tension are state descriptions, not master controls

The composition director may track energy, tension, density, instability, and attention. These are high-level descriptions of musical state.

The system SHOULD avoid mapping a single “energy” value directly to all of volume, tempo, note density, distortion, brightness, and track count. Such coupling often produces crude and predictable results.

A better model uses several dimensions, each with its own sources, target range, inertia, and permissible influence over lower-level parameters.

---

# Part IX — Evaluation, criticism, and musical quality

## 35. The system must evaluate different kinds of success separately

There are at least four evaluation domains:

1. **Technical validity:** can the project be processed, rendered, saved, reopened, and exported correctly?
2. **Musical validity:** do the entities and relationships satisfy the declared musical constraints and internal logic?
3. **Perceptual effectiveness:** are the intended musical roles, changes, and contrasts likely to be audible and intelligible?
4. **Artistic value:** does the work feel compelling, expressive, coherent, original, or otherwise successful for its purpose?

These domains overlap, but they are not interchangeable.

## 36. Evaluation must be plural

There is no single reliable number that measures musical quality in all cases. Recent reviews of music-generation evaluation describe a range of objective, subjective, qualitative, quantitative, output-focused, and interaction-focused methods, and note the lack of universally standardised evaluation protocols. See Lerch et al., *Survey on the Evaluation of Generative Models in Music* (2025/2026), and the later review by related researchers and contributors listed in the references.

**Constitutional requirement:** the system SHOULD combine diagnostics suited to each question and MUST document what each metric can and cannot establish.

## 37. Evaluation dimensions

### 37.1 Intent alignment

Does the result reflect the CompositionBrief? Which parts of the brief are satisfied, contradicted, or unresolved?

### 37.2 Identity coherence

Does the composition retain recognisable features? Are changes consistent with declared development or rupture?

### 37.3 Local musical coherence

Do events, patterns, and voices interact in an understandable or intentionally challenging way?

### 37.4 Development

Does the material evolve, return, accumulate, erode, transform, or otherwise progress according to the formal intention?

### 37.5 Formal direction

Do sections have functions? Are transitions meaningful? Does the ending perform a deliberate action?

### 37.6 Perceptual organisation

Are important foreground elements audible? Is density managed? Are masking and competition intentional?

### 37.7 Diversity and originality

Does the system avoid producing only trivial variations of the same output? Does the result have a distinct idea? These questions require care: novelty metrics can identify statistical difference, but not necessarily artistic originality.

### 37.8 Technical quality

Does the project render without missing events, clipping, discontinuities, invalid automation, sample-rate errors, or synchronisation defects?

### 37.9 Creative usability

Can the composer inspect, revise, and develop the result? Does the system make a useful contribution to the user's process?

## 38. Diagnostics must explain evidence

A diagnosis should describe an observable condition, its scope, its likely implication, and a possible action.

Weak diagnostic:

> Musicality: 54/100.

Better diagnostic:

> The upper percussion layer introduces new onset positions in every phrase, but its accent profile does not relate to the main rhythmic motif. The result increases event variety without creating a clear call-and-response or counter-accent relationship. Consider preserving one accent landmark across the next phrase.

The system may offer suggestions, but it SHOULD distinguish evidence from interpretation.

## 39. Automated evaluation must not claim artistic authority

Automated checks are useful for detecting invalid data, repeated patterns, density extremes, range violations, broken dependencies, clipping, and other observable properties.

They are less reliable at deciding whether a particular irregularity is expressive, whether a phrase feels inevitable, or whether a strange sound is emotionally effective.

The evaluator SHOULD report confidence and limitations. It MUST NOT silently discard material because it violates a conventional rule when the brief or context suggests that the violation may be intentional.

## 40. Human listening is a formal evaluation method

The system SHOULD support structured audition and comparison:

- solo and full-context playback;
- level-matched A/B comparison when relevant;
- looped phrase comparison;
- section-to-section comparison;
- before-and-after mutation comparison;
- reference playback;
- annotation and preference recording;
- blind comparison where useful.

The software should preserve what was compared and what the composer selected, while avoiding the assumption that one person's choice is a universal truth.

## 41. Regression compositions

The project SHOULD maintain a versioned suite of reference compositions covering different behaviours:

- sparse and minimal;
- dense and highly layered;
- asymmetrical and polymetric;
- tonal and non-tonal;
- process-based;
- motif-driven;
- sample-heavy;
- synthesis-heavy;
- long-form and multi-movement;
- deliberately unstable or fragmentary.

A code change should be evaluated against relevant reference projects. A system that improves one style while silently breaking another must expose that trade-off.

---

# Part X — Human agency and creative interaction

## 42. The composer remains the author of the project

The software may generate, recommend, transform, or autonomously commit within a selected mode. It MUST preserve the human's ability to understand and control the work.

Authorship is not determined solely by who generated a note. It is also shaped by intention, selection, editing, organisation, performance, and final responsibility. The software should not make legal or philosophical claims about authorship on the user's behalf.

## 43. Separate candidate state from accepted state

The interface and internal model SHOULD distinguish:

- generated candidate;
- auditioned candidate;
- selected candidate;
- committed material;
- manually edited material;
- frozen material;
- rejected candidate;
- archived candidate.

Rejecting a candidate should not destroy the original. Accepting a candidate should create a clear state transition and retain a rollback path.

## 44. Local regeneration is a fundamental capability

The user SHOULD be able to request a new version of one selected entity without regenerating unrelated parts of the work.

Local regeneration MUST respect dependencies and protected material. If a local change affects harmony, orchestration, automation, or formal timing, the system should identify those consequences and request or apply an explicit update policy.

## 45. Semantic controls

A control labelled “more fragmented” should produce a more fragmented musical behaviour, not simply randomise note positions. A control labelled “more unstable” should identify which dimension becomes unstable: timing, pitch, repetition, timbre, harmony, or form.

Every semantic control SHOULD define:

- its musical meaning;
- affected entities;
- protected entities;
- parameter mapping;
- expected range of outcomes;
- known side effects;
- reversibility;
- how it interacts with other controls.

## 46. Explainability without false certainty

A useful explanation reports the decision path:

- which material was considered;
- which constraints applied;
- which alternatives were available;
- what relationship was targeted;
- why a candidate was chosen under the current policy.

It should not claim a human-like internal experience. It should not say “I felt the track needed tension.” It may say “the section plan requested increased rhythmic instability while preserving the low-frequency anchor; this candidate changes the upper pattern's accent placement.”

## 47. The interface must reveal the state of the work

At minimum, the composer should be able to tell:

- what is authoritative project material;
- what is only a candidate;
- what is frozen;
- what is currently being mutated;
- what constraints are active;
- what decisions were made automatically;
- what changed since the previous state;
- whether the preview reflects the current project;
- whether a render is complete and valid.

Hidden state is a source of distrust and mistakes.

---

# Part XI — Project integrity, reproducibility, and rendering

## 48. The project is the source of truth

The saved project state, not a transient preview buffer or UI widget, must be the authoritative representation of the composition.

The architecture MUST avoid making the interface the only place where critical musical state exists. Saving and reopening a project must not depend on the original UI session remaining alive.

## 49. Deterministic and exploratory modes

The system SHOULD support at least two operational modes:

### Deterministic mode

Given the same project state, generator version, assets, configuration, seed, and relevant dependencies, the system should reproduce the same symbolic result and, where the audio environment permits, the same or demonstrably equivalent render.

### Exploratory mode

The system may produce new candidates using stochastic methods, but every candidate should have enough recorded state to be inspected and, where practical, regenerated.

The UI MUST make clear which mode is active.

## 50. A seed is not a complete reproducibility record

A seed alone does not guarantee reproduction if any of the following have changed:

- generator algorithm or version;
- library data;
- plug-in version;
- sample asset;
- preset content;
- parameter defaults;
- time conversion logic;
- floating-point implementation;
- random-number generator;
- processing order;
- external dependency.

The project SHOULD record relevant versions and asset identifiers. If exact audio reproduction is impossible because of external nondeterministic components, the software should report that limitation.

## 51. Rendering must not change the composition

The renderer executes accepted project state. It MUST NOT mutate the authoritative musical arrangement as a side effect of exporting audio.

Any render-specific transformations, such as randomised analogue modelling or non-deterministic synthesis, must be treated as render configuration and recorded.

## 52. Preview and final render must share meaning

A real-time preview may use lower quality, reduced polyphony, shorter tails, simplified oversampling, or other performance compromises. It MUST preserve the same musical timing, event interpretation, routing intent, and automation semantics unless clearly labelled as an approximation.

A preview that omits an effect, ignores automation, or substitutes an entirely different synthesis path can mislead composition decisions. Such differences must be explicit.

## 53. Export is part of the instrument

A complete delivery workflow SHOULD support, where relevant:

- full mix;
- stems;
- individual tracks or voices;
- MIDI or another symbolic representation;
- automation data;
- sound-source and preset references;
- routing information;
- project metadata;
- a manifest of assets and versions;
- render settings;
- documentation sufficient to reopen or reconstruct the project.

The software MUST distinguish a full editable package from a mix-only export.

---

# Part XII — Architecture principles for developers

This constitution does not mandate a particular software architecture, but the following separation of responsibilities is strongly recommended.

## 54. Separate intention, score, sound, and execution

The implementation SHOULD distinguish at least these conceptual layers:

1. **Intent layer** — brief, goals, constraints, identity, and unresolved questions.
2. **Composition layer** — form, sections, phrases, motifs, voices, roles, and relationships.
3. **Event layer** — time-positioned notes, triggers, articulations, controls, and automation events.
4. **Realisation layer** — instruments, samples, synthesis graphs, effects, routing, and spatial parameters.
5. **Execution layer** — scheduling, audio buffers, plug-in processing, and rendering.
6. **Interaction layer** — editing, audition, candidate management, visualisation, and project navigation.
7. **Evaluation layer** — diagnostics, metrics, listening tests, and quality gates.

The layers communicate through documented contracts. A realisation change should not require changing the abstract composition model. A different UI should not require rewriting musical decision logic.

## 55. Use a shared musical clock

All subsystems MUST agree on musical time semantics. Time conversion should be centralised and testable.

The system SHOULD distinguish:

- musical position;
- musical duration;
- tempo map;
- meter map;
- event performance offset;
- absolute seconds;
- audio sample position.

Rational or otherwise exact representations SHOULD be used where they prevent accumulated timing error. The system must explicitly define how tuplets, swing, polymeter, tempo changes, and sample-accurate execution interact.

## 56. Keep musical identity separate from implementation identity

A voice called “metallic response” may be realised by a sample, a resonator, FM synthesis, a physical model, or a hybrid chain. The musical role should remain meaningful if the sound source is replaced.

The data model SHOULD distinguish:

- musical role identifier;
- material identity;
- instrument definition;
- plug-in or engine implementation;
- render instance.

This makes the project more portable and allows sound-design development without corrupting composition semantics.

## 57. Prefer explicit state transitions

Composition state changes should be described as operations with inputs, outputs, validation, and reversibility.

A generator should not modify a global mutable object in ways that are invisible to the caller. A render process should not accidentally alter a project. A UI selection should not mutate musical data until an explicit action invokes a mutation or commit operation.

## 58. Use transactional operations

For any operation that may alter accepted material:

1. capture the relevant prior state or create an immutable version;
2. construct the proposed changes;
3. validate the proposal;
4. check dependencies;
5. commit atomically;
6. record the decision;
7. expose undo or rollback.

If validation fails, the accepted state must remain intact.

## 59. Avoid hidden coupling

A parameter should not unexpectedly affect unrelated systems. If “complexity” changes pitch density, rhythm density, sound brightness, and track count, those relationships must be explicit and inspectable.

The project SHOULD favour named mappings, typed interfaces, dependency graphs, and testable control policies over scattered callbacks and implicit global state.

## 60. Version the contracts

Data schemas, generator interfaces, mutation contracts, and render manifests SHOULD carry versions. When a contract changes, provide a migration path or a clear incompatibility message.

A project file should not silently reinterpret old values under new semantics.

---

# Part XIII — Anti-patterns and prohibited shortcuts

The following are common ways a generative music project can become musically or technically shallow. They are not all prohibited in every context, but each requires explicit justification.

## 61. Randomness theatre

**Symptom:** the program changes many parameters and calls the result creative.

**Why it fails:** the changes may be independent, redundant, or unrelated to the composition.

**Required correction:** bind random exploration to a musical purpose, scope, identity, and evaluation policy.

## 62. Complexity inflation

**Symptom:** the system adds notes, tracks, fills, modulations, or effects whenever a section needs development.

**Why it fails:** activity increases but meaning does not.

**Required correction:** include subtraction, return, omission, role exchange, and timbral reinterpretation among the available developmental operations.

## 63. Loop multiplication

**Symptom:** a track is made longer by duplicating loops and adding occasional fills.

**Why it fails:** duration is mistaken for form.

**Required correction:** define phrase and section functions, material lineage, transitions, and long-range development.

## 64. Genre preset masquerading as composition

**Symptom:** the software selects a tempo, drum kit, sound palette, and pattern template and declares an IDM composition complete.

**Why it fails:** stylistic surface is substituted for musical relationships.

**Required correction:** treat style as a vocabulary or prior, not a complete compositional plan.

## 65. One-size-fits-all arrangement

**Symptom:** all compositions use the same intro, build, drop, breakdown, and outro structure.

**Why it fails:** the system's formal imagination is narrower than the musical domain.

**Required correction:** support process-based, cyclic, fragmentary, multi-movement, subtractive, and nonlinear structures as well as familiar song forms.

## 66. Single scalar quality score

**Symptom:** all musical judgements are compressed into one opaque score.

**Why it fails:** distinct qualities conflict and are not always commensurable.

**Required correction:** expose dimensions, constraints, evidence, uncertainty, and human choice.

## 67. Mutation without lineage

**Symptom:** a new pattern replaces an old one and the relationship is lost.

**Why it fails:** the system cannot explain, reverse, compare, or develop its own material.

**Required correction:** retain parent-child lineage and operation metadata.

## 68. UI as database

**Symptom:** the project exists primarily in widgets, callbacks, or transient preview structures.

**Why it fails:** saving, testing, headless generation, and rendering become fragile.

**Required correction:** maintain an authoritative project model independent of presentation.

## 69. Preview / render divergence

**Symptom:** the preview uses different effects, automation, or event timing from the final export without notice.

**Why it fails:** the composer makes decisions based on a false representation of the project.

**Required correction:** share semantics and report unavoidable preview approximations.

## 70. Destructive regeneration

**Symptom:** pressing generate overwrites accepted material.

**Why it fails:** exploration becomes risky and the user loses agency.

**Required correction:** create candidates, compare, commit, and provide rollback.

## 71. Unbounded feature coupling

**Symptom:** a new feature changes unrelated systems through shared mutable state or implicit side effects.

**Why it fails:** the project becomes difficult to reason about and regressions multiply.

**Required correction:** contracts, clear ownership, transactional operations, and integration tests.

## 72. Evaluation by visual activity

**Symptom:** a complex interface, waveform, or parameter animation is mistaken for evidence of a sophisticated composition.

**Why it fails:** representation and musical value are different.

**Required correction:** test actual data, relationships, audio, and listening outcomes.

## 73. Endless generation without completion

**Symptom:** the engine can make variations but cannot decide when the work is finished.

**Why it fails:** generation has no formal stopping or closure model.

**Required correction:** define composition completion criteria, ending strategies, and export states.

## 74. Unexplained automatic authority

**Symptom:** the system changes accepted material without stating which policy authorised it.

**Why it fails:** automatic behaviour becomes unpredictable and difficult to trust.

**Required correction:** record the policy, scope, and reversible state transition.

---

# Part XIV — The development workflow: from principle to feature

## 75. Every major feature begins with a musical problem statement

A feature proposal MUST answer:

1. What musical or creative problem exists?
2. Which users or workflows experience it?
3. What does the composer need to be able to do?
4. What existing musical entities and relationships are involved?
5. What is the smallest useful version?
6. What must remain unchanged?
7. How will success be observed or tested?

“Add a new generator” is not a sufficient problem statement.

## 76. Define the feature contract before implementation

The contract should specify:

- inputs and defaults;
- outputs and schemas;
- state changes;
- hard and soft constraints;
- ownership boundaries;
- dependencies;
- deterministic behaviour;
- failure modes;
- validation rules;
- undo and rollback behaviour;
- logging and diagnostics;
- expected performance envelope.

## 77. Implement from the musical model outward

Recommended order:

1. Define the musical concept and intended behaviour.
2. Define the data representation.
3. Define the operation and mutation contracts.
4. Implement the algorithm independently of the UI.
5. Test musical invariants and edge cases.
6. Integrate with the composition model.
7. Integrate with sound realisation and rendering where needed.
8. Expose controls and diagnostics in the interface.
9. Evaluate with reference compositions and listening.
10. Document limitations and update the relevant manual.

This reduces the risk of implementing interface behaviour before the underlying musical semantics are understood.

## 78. The feature acceptance standard

A feature is not complete because it exists in a menu or produces one successful result.

It should be considered complete only when:

- its musical purpose is documented;
- its contracts are implemented;
- valid and invalid inputs are handled;
- protected state remains intact;
- outputs are inspectable;
- undo or rollback works where required;
- deterministic behaviour is tested where promised;
- integration with dependent subsystems is verified;
- preview and render semantics are consistent;
- user-facing controls communicate their meaning;
- errors are actionable;
- reference projects demonstrate the intended behaviour;
- documentation is updated.

## 79. Definition of done template

```text
FEATURE: [name]

MUSICAL PURPOSE
- [What compositional problem does this solve?]
- [What musical result should become possible?]

CONTRACT
- [Inputs and outputs]
- [Hard constraints]
- [Soft preferences]
- [State changes]
- [Ownership boundaries]

IDENTITY AND MUTATION
- [What material may change?]
- [What must be preserved?]
- [How is lineage recorded?]

ENGINEERING
- [Schema and versioning]
- [Error handling]
- [Performance expectations]
- [Determinism expectations]
- [Undo / rollback]

VALIDATION
- [Unit tests]
- [Property tests]
- [Integration tests]
- [Regression project]
- [Listening evaluation]

USER EXPERIENCE
- [Control semantics]
- [Candidate / commit behaviour]
- [Diagnostics and explanation]

DOCUMENTATION
- [Updated guide]
- [Known limitations]
- [Migration notes if needed]
```

## 80. Change impact review

Before modifying a foundational subsystem, developers SHOULD ask:

- Which composition entities are affected?
- Which generators depend on this behaviour?
- Does this alter the meaning of saved project data?
- Does it affect deterministic replay?
- Does it change preview or render output?
- Does it invalidate existing presets or reference projects?
- Does it change the meaning of a user-facing control?
- Which musical identities or formal behaviours might regress?

The review is especially important for time representation, material identity, event scheduling, composition state, and rendering semantics.

---

# Part XV — Worked examples of constitutional behaviour

The examples below demonstrate how the principles guide real design decisions.

## 81. Example A — “Make this section more unpredictable”

### Incomplete interpretation

Set every randomisation parameter to a higher value.

### Constitutional interpretation

First determine:

- Which section and voices are in scope?
- Which elements create the current identity?
- Should unpredictability affect timing, accent, pitch, timbre, orchestration, repetition, or form?
- What must remain stable?
- Is the desired result gradual instability or sudden rupture?

### Proposed operation

- Preserve the main low-frequency pulse.
- Keep the phrase length and section boundary.
- Introduce bounded onset displacement in one upper-percussion voice.
- Allow one secondary pattern to rotate over a different cycle length.
- Reduce repeated accent predictability over successive phrases.
- Keep a recognisable recurrence at the end of the section.

### Evaluation

Check that the section is more unpredictable in the targeted dimensions, that its anchor remains recognisable, and that the result contributes to the next section rather than merely increasing local event disorder.

## 82. Example B — “Give the second section more energy”

### Incomplete interpretation

Increase loudness, tempo, distortion, note density, and track count.

### Constitutional interpretation

Ask what kind of energy is needed. The second section may need greater rhythmic insistence, sharper transients, a wider register, increased harmonic tension, or a foreground role change. It may not need greater loudness.

### Proposed operation

- Retain the tempo and main bass material.
- Increase the activity of the upper rhythmic layer.
- Add a response voice in the gaps of the principal motif.
- Shift the foreground from texture to a more identifiable melodic fragment.
- Keep the master level and low-frequency headroom controlled.

### Evaluation

Compare attention, rhythmic activity, spectral density, and perceived intensity separately. Confirm that the section feels more driven without making every dimension more crowded.

## 83. Example C — “Generate a new melody, but keep the track's identity”

### Incomplete interpretation

Generate random notes from the same scale.

### Constitutional interpretation

Identify the identity-bearing dimensions of the current material. If rhythm and contour are important, preserve or deliberately transform them. If the timbre is central, keep the sound family. If the phrase length is fixed, respect it.

### Candidate strategies

- retain rhythmic contour and change intervals;
- preserve interval relationships but alter the rhythm;
- use the motif's final fragment as the new opening;
- invert contour while retaining accent placement;
- derive a new line from the bass's implied pitch field;
- create a response that uses the motif's negative space.

### Evaluation

The composer should be able to hear why the new melody belongs to the same work, even if it is not a literal repetition.

## 84. Example D — “Regenerate the drums”

### Incomplete interpretation

Replace every percussion event with a newly randomised pattern.

### Constitutional interpretation

Determine whether the user means:

- new sound selection;
- new event positions;
- a new pattern with the same role;
- a different rhythmic identity;
- variation of one percussion voice;
- reorchestration of the existing rhythm.

The interface should disambiguate these operations or expose them as distinct commands.

### Required protection

The mutation should preserve frozen bass relationships, section duration, and any drum motifs that have been explicitly protected.

## 85. Example E — “The generated track is technically correct but boring”

### Incomplete interpretation

Increase complexity.

### Constitutional interpretation

Diagnose possible causes:

- no clear central proposition;
- no meaningful motif recurrence;
- all layers enter at once;
- every phrase has the same function;
- local changes do not affect global direction;
- the sound palette is static;
- the arrangement has no foreground shift;
- transitions do not alter expectation;
- the ending simply stops.

A useful correction may be subtraction, contrast, a new relationship, a changed role, or a stronger formal process rather than additional notes.

---

# Part XVI — Constitutional requirements checklist

Use this checklist during architecture reviews and major releases.

## 86. Artistic identity

- [ ] The software distinguishes generation from composition.
- [ ] The project can store an explicit artistic brief.
- [ ] Composition identity is represented or can be described through explicit commitments.
- [ ] The system supports more than one narrow arrangement template.
- [ ] Simple, sparse, repetitive, and process-based music remain valid outputs.

## 87. Musical hierarchy and relationships

- [ ] Musical entities have consistent definitions.
- [ ] Relationships between material are preserved where relevant.
- [ ] Local generators respect higher-level constraints.
- [ ] Pattern and phrase operations can be evaluated in context.
- [ ] The system supports material lineage.

## 88. Generation and mutation

- [ ] Candidate state is separate from committed state.
- [ ] Hard constraints and soft preferences are distinct.
- [ ] Mutations declare scope and preserve/change sets.
- [ ] Frozen material has precise semantics.
- [ ] Random decisions are bounded and traceable.
- [ ] Deterministic replay is supported where promised.

## 89. Perception and evaluation

- [ ] Technical validity is separate from musical quality.
- [ ] Evaluation covers multiple time scales.
- [ ] Density is not represented by event count alone.
- [ ] Diagnostics provide evidence and scope.
- [ ] Human audition and comparison are supported.
- [ ] Automated scores do not claim universal artistic authority.

## 90. Human agency

- [ ] The user can inspect and reject candidates.
- [ ] Local regeneration is supported where practical.
- [ ] Semantic controls have documented meanings.
- [ ] Automatic commits are visible and reversible.
- [ ] The interface reveals active constraints and frozen material.

## 91. Engineering and delivery

- [ ] The project model is authoritative and independent of UI state.
- [ ] Musical time semantics are centralised.
- [ ] Rendering does not mutate composition state.
- [ ] Preview differences are disclosed.
- [ ] Exports are validated.
- [ ] Project metadata and provenance are retained.
- [ ] Operations that alter accepted material are transactional.
- [ ] Regression compositions protect established behaviours.

A release should not claim constitutional compliance if a critical requirement is knowingly violated without a documented exception.

---

# Part XVII — Governance, exceptions, and evolution

## 92. The constitution must evolve without becoming arbitrary

A foundational document should be stable enough to guide architecture and flexible enough to respond to new musical practices and technical capabilities.

The constitution SHOULD be changed only when:

- a principle is ambiguous or contradictory;
- a new class of musical behaviour cannot be represented;
- an existing rule creates a demonstrable creative or engineering problem;
- research or practice provides a reason to revise an assumption;
- the project adopts a new class of interaction or rendering capability.

## 93. Exception procedure

An exception to a MUST-level requirement should document:

- the requirement being excepted;
- why the exception is necessary;
- the scope and duration of the exception;
- affected subsystems;
- risks and mitigations;
- how correctness will be tested;
- whether the exception should become a permanent amendment.

Exceptions MUST NOT be hidden in implementation details.

## 94. Amendment procedure

A proposed amendment should include:

1. the current principle or contract;
2. the problem with the current wording;
3. the proposed replacement;
4. musical consequences;
5. engineering consequences;
6. migration and compatibility implications;
7. affected documentation and tests.

The document owner or maintainers should record the amendment history. The constitution should not change silently because a feature implementation found a rule inconvenient.

## 95. What must remain invariant

Even as specific algorithms and interfaces change, the following commitments should remain stable:

- intention guides generation;
- composition is relational and hierarchical;
- material has identity and lineage;
- constraints have explicit semantics;
- mutations are scoped;
- candidates do not overwrite accepted material without authority;
- human agency remains possible;
- evaluation is multidimensional;
- technical validity is not confused with artistic value;
- project state is recoverable;
- rendering is reproducible to the degree promised;
- the system supports completion, not endless variation alone.

---

# Appendix A — Canonical subsystem contracts

These contracts are concise reference agreements. Detailed technical schemas belong in the dedicated ontology, architecture, evaluation, and rendering manuals.

## A1. Brief Interpreter

**Input:** user-authored intent, project settings, optional references, unresolved questions.

**Output:** structured brief, constraints, goals, inference annotations, ambiguity report.

**MUST:** preserve source intent; distinguish explicit from inferred values; report conflicts; avoid silently inventing hard constraints.

## A2. Composition Director

**Input:** brief, current composition state, section history, evaluation summaries, protected material.

**Output:** global plan, section goals, state transitions, next actions or candidate requests.

**MUST:** maintain long-range context; respect project commitments; avoid excessive state switching; record autonomous decisions.

## A3. Form and Phrase Planner

**Input:** global plan, material inventory, current formal state, timing constraints.

**Output:** phrase and section proposals, transition plans, formal diagnostics.

**MUST:** describe function rather than only duration; support irregular and nonstandard structures; preserve approved boundaries unless authorised.

## A4. Material Manager

**Input:** new material, transformations, user edits, provenance records.

**Output:** versioned material entities, identity metadata, lineage graph, dependency updates.

**MUST:** preserve parent relationships; maintain stable identifiers; support freezing and rollback.

## A5. Pattern and Motif Generators

**Input:** role, context, identity constraints, source material, variation policy, seed.

**Output:** candidates and generation metadata.

**MUST:** obey scope and constraints; preserve declared identity features; avoid committing automatically unless authorised.

## A6. Orchestrator

**Input:** voices, roles, section state, register and attention goals, sound-role requirements.

**Output:** orchestration candidates, interaction map, perceptual diagnostics.

**MUST:** evaluate combined behaviour; distinguish intended overlap from accidental competition; preserve source material unless authorised to revoice or transform it.

## A7. Sound Realiser

**Input:** abstract role, event data, sound vocabulary, instrument capabilities, processing constraints.

**Output:** instrument mappings, synthesis and effect graphs, automation mappings, render-ready configuration.

**MUST:** preserve musical event semantics; report unavailable resources; expose approximations; avoid silently substituting unrelated sound sources.

## A8. Evaluator

**Input:** project snapshot, brief, constraints, analysis configuration, optional human feedback.

**Output:** diagnostics, metrics, warnings, evidence, confidence or limitation notes.

**MUST:** distinguish objective checks from interpretive judgement; avoid overwriting material; report scope and method.

## A9. Mutation Engine

**Input:** target entity, mutation contract, constraints, seed, dependency graph.

**Output:** candidate patch, validation report, lineage record, rollback data.

**MUST:** change only authorised scope; preserve the required invariants; fail safely.

## A10. Renderer

**Input:** committed project snapshot, render configuration, assets and engine versions.

**Output:** audio files, stems, render report, checksums or manifests where supported.

**MUST:** not alter project state; report missing dependencies and failures; preserve timing and routing semantics; distinguish approximate and final renders.

## A11. Creative Interface

**Input:** user actions and current project state.

**Output:** visible state, commands, audition controls, edits, selection and commit requests.

**MUST:** distinguish candidates from accepted state; reveal relevant constraints and status; avoid hidden destructive operations.

---

# Appendix B — Decision and mutation record templates

## B1. Decision record

```yaml
decision_record:
  id: "decision-000184"
  subsystem: "phrase_planner"
  operation: "select_phrase_candidate"
  project_revision: 42
  generator_version: "phrase-planner/1.3.0"
  context:
    composition_id: "composition-A"
    section_id: "section-B"
    phrase_index: 3
  intent:
    - "increase instability without losing motif recognition"
  constraints_checked:
    - "phrase_duration_fixed"
    - "motif_contour_preserved"
  candidates:
    - id: "candidate-1"
      status: "rejected"
      reason: "too much identity loss"
    - id: "candidate-2"
      status: "selected"
      reason: "preserves contour and changes rhythmic grouping"
  selected_candidate: "candidate-2"
  randomness:
    seed: 184202
    deterministic: true
  commit:
    authorised_by: "user"
    reversible: true
    undo_reference: "revision-41"
```

## B2. Constraint record

```yaml
constraint:
  id: "constraint-voice-range-01"
  type: "hard"
  source: "user"
  scope:
    entity_type: "voice"
    entity_id: "bass-main"
  rule:
    property: "pitch_range"
    minimum: "A0"
    maximum: "D3"
  priority: 100
  conflict_policy: "report_and_stop"
  active: true
```

## B3. Candidate comparison record

```yaml
candidate_comparison:
  comparison_id: "compare-0031"
  target: "upper-motif"
  context: "section-2 / phrase-4"
  criteria:
    - "brief_alignment"
    - "identity_preservation"
    - "phrase_function"
    - "perceptual_clarity"
  candidates:
    - id: "A"
      diagnostics: ["clear identity", "low contrast"]
    - id: "B"
      diagnostics: ["strong contrast", "moderate identity loss"]
    - id: "C"
      diagnostics: ["high novelty", "weak relationship to source"]
  outcome:
    selected: "B"
    selected_by: "composer"
    note: "The increased contrast is appropriate at this formal point."
```

---

# Appendix C — Minimum reference-project suite

A mature implementation should maintain reference projects that exercise the constitution rather than only showcase its best outputs.

| Reference project | What it tests |
|---|---|
| Sparse pulse study | Restraint, repetition, omission, and negative space |
| Rotating-cycle study | Independent rhythmic layers and phase relationships |
| Fragment collage | Nonlinear form, material lineage, and transition logic |
| Motif-development study | Recognition, transformation, return, and variation budgets |
| Tonal-friction study | Pitch hierarchy, dissonance, and voice interaction |
| Noise/process study | Non-pitched material, long-form process, and perceptual attention |
| Hybrid sound-object study | Separation of musical identity from sound implementation |
| Multi-section composition | Long-range direction, contrast, and ending behaviour |
| Frozen-material study | Mutation contracts, local regeneration, and dependency protection |
| Candidate-selection study | Candidate management, comparison, commit, and rollback |
| Deterministic replay study | Seeds, versions, assets, and project reproducibility |
| Render-parity study | Preview/final semantics, stems, timing, and automation |
| Failure-recovery study | Invalid inputs, missing assets, failed rendering, and project safety |

Each reference project should include:

- the brief;
- source material;
- project file;
- expected structural properties;
- expected protected material;
- representative candidates;
- accepted state;
- MIDI or symbolic export where relevant;
- reference audio where relevant;
- evaluation notes;
- tests and known limitations.

---

# Appendix D — Developer review questions

Before accepting a major generative feature, ask:

### Musical questions

1. What musical problem does this feature solve?
2. What makes its output belong to the current composition?
3. Which musical relationships does it create or preserve?
4. Does it understand the phrase or section in which it operates?
5. Can it create meaningful absence as well as presence?
6. Can it produce a deliberately simple result?
7. Does it distinguish a variation from a replacement?
8. Can the composer hear why one candidate differs from another?

### Architectural questions

1. Which subsystem owns the decision?
2. What is the authoritative state?
3. Which contracts are involved?
4. What can change, and what must remain invariant?
5. Are dependencies and lineage preserved?
6. Is the operation transactional?
7. Can it be deterministic where required?
8. Can it be undone?

### Evaluation questions

1. What is the evidence that the feature works?
2. Which properties can be tested objectively?
3. Which properties need listening or human judgement?
4. What failure modes are expected?
5. Which existing reference projects could regress?
6. What does the system report when it cannot satisfy the request?

### Creative-interaction questions

1. Does the user understand what will change?
2. Can the user audition alternatives?
3. Can the user keep the current version?
4. Are automatic decisions visible?
5. Can a useful manual edit be made without fighting the generator?
6. Does the control express a meaningful musical intention?

---

# Appendix E — Glossary of constitutional terms

| Term | Definition |
|---|---|
| Artistic intent | The creative direction and desired listening experience of a work |
| Candidate | A generated possibility not yet committed to the authoritative project |
| Commit | An authorised transition that accepts a candidate into project state |
| Composition identity | The recognisable characteristics and commitments of a work |
| Constraint | A rule limiting or guiding possible decisions |
| Decision record | A record of context, alternatives, constraints, selection, and provenance |
| Deterministic replay | Reproducing a result from the same relevant state and dependencies |
| Evaluation | The process of testing technical, musical, perceptual, or artistic properties |
| Hard constraint | A requirement that must be satisfied for an operation to be valid |
| Intent alignment | The degree to which a result reflects the declared brief |
| Lineage | The recorded origin and transformation history of material |
| Material | A reusable musical idea or substance |
| Mutation | A scoped transformation of existing material |
| Mutation budget | A limit on how much an operation may change selected properties |
| Musical role | The function a voice or material performs in context |
| Ontology | The shared conceptual model of entities and relationships |
| Perceptual density | The experienced density of musical information, not reducible to event count |
| Provenance | Information describing the origin and processing history of an object or decision |
| Reconciliation | The explicit resolution of conflicting constraints or subsystem proposals |
| Reproducibility | The ability to reconstruct or meaningfully compare a prior result |
| Soft preference | A desirable quality that may be traded off |
| Transaction | An operation that either commits a validated change as a unit or leaves prior state intact |

---

# References and further reading

These sources inform the constitution's treatment of generative evaluation, human interaction, musical representation, and controllability. They do not prescribe one architecture or settle artistic questions.

1. **Lerch, Alexander; Arthur, Claire; Bryan-Kinns, Nick; Ford, Corey; Sun, Qianyi; Vinay, Ashvala.** “Survey on the Evaluation of Generative Models in Music.” *ACM Computing Surveys*, 2025/2026. DOI: [10.1145/3769106](https://doi.org/10.1145/3769106). A broad review of subjective and objective evaluation, output quality, usability, and methodological limitations.
2. **Agchar, Ismael; Baumann, Ilja; Braun, Franziska; Perez-Toro, Paula Andrea; Riedhammer, Korbinian; Trump, Sebastian; Ullrich, Martin.** “A Survey of Music Generation in the Context of Interaction.” arXiv:2402.15294, 2024. [https://arxiv.org/abs/2402.15294](https://arxiv.org/abs/2402.15294). Reviews music representation, generative models, interaction, and human-machine co-creation.
3. **Le, Dinh-Viet-Toan; Bigo, Louis; Herremans, Dorien; Keller, Mikaela.** “Natural Language Processing Methods for Symbolic Music Generation and Information Retrieval: A Survey.” *ACM Computing Surveys*, 2025. DOI: [10.1145/3714457](https://doi.org/10.1145/3714457). Useful for understanding symbolic music as structured representation and the limits of direct language-model analogies.
4. **Yang, Li-Chia; Lerch, Alexander.** “On the Evaluation of Generative Models in Music.” *Neural Computing and Applications*, 32, 4773–4784, 2020. DOI: [10.1007/s00521-018-3849-7](https://doi.org/10.1007/s00521-018-3849-7). Discusses the challenges of evaluating creative output and proposes musically informed objective measures.
5. **Fiebrink, Rebecca; Cook, Perry R.** “The Wekinator: A System for Real-Time, Interactive Machine Learning in Music.” Proceedings of the NIME community and related publications. The Wekinator project is a useful case study for interactive, user-shaped machine-learning instruments: [https://wekinator.org/](https://wekinator.org/).
6. **Roads, Curtis.** *The Computer Music Tutorial*. MIT Press, 1996. A foundational technical reference for computer music, synthesis, signal processing, and algorithmic practice.
7. **Zölzer, Udo (ed.).** *DAFX: Digital Audio Effects*, 2nd ed. Wiley, 2011. A technical foundation for sound processing and effect-system design.
8. **Smith, Julius O.** *Physical Audio Signal Processing*. Online book: [https://ccrma.stanford.edu/~jos/pasp/](https://ccrma.stanford.edu/~jos/pasp/). A detailed reference for physical modelling and audio signal processing.
9. **Farnell, Andy.** *Designing Sound*. MIT Press, 2010. A practical reference for procedural sound design and modelling.
10. **Cope, David.** *Computer Models of Musical Creativity*. MIT Press, 2005. A useful historical and conceptual reference for rule-based and algorithmic composition; its claims should be read critically rather than treated as a universal theory of creativity.

---

# Final declaration

An IDM Generative Instrument should be judged not by how many notes it can create, how many algorithms it contains, how complex its interface appears, or how closely its output resembles a narrow catalogue of genre references.

It should be judged by the quality of the musical possibilities it makes available, the relationships it can preserve and develop, the intelligibility of its controls, the honesty of its evaluation, the safety of its editing, and the usefulness of its collaboration with a composer.

Its central responsibility is to make musical exploration more powerful without making musical intention less important.

**The system must generate possibilities. It must protect identity. It must support judgement. It must preserve agency. And it must help a composition become a finished, editable, reproducible work.**

That is the constitution of the IDM Generative Instrument.
