# Generative Intelligence, Algorithms & Decision-Making

## A Computational Composition Manual for the IDM Generative Instrument

**Volume 7 of the IDM Generative Instrument documentation library**  
**Document type:** Algorithmic, compositional, and decision-system architecture  
**Audience:** Music-software developers, algorithmic composers, computational musicians, researchers, and technical artists  
**Status:** Reference specification and implementation guide  
**Scope:** Generative reasoning, candidate creation, planning, constraint management, selection, adaptation, evaluation, and reproducibility

---

## Abstract

A generative music system becomes a compositional instrument only when it can do more than produce plausible events. It must interpret an artistic intention, construct a plan at an appropriate level of abstraction, generate material that belongs to that plan, understand relationships between musical objects, compare alternatives, preserve accepted decisions, and revise its work without destroying the identity of the composition.

This manual specifies the intelligence and decision-making layer of the IDM Generative Instrument. It explains how to organise algorithmic methods, how to assign different methods to different musical problems, how to coordinate local generators with long-range planning, how to represent uncertainty, how to generate and evaluate candidates, and how to keep human agency and reproducibility intact.

The manual is deliberately algorithm-neutral. It does not claim that one model family—rules, probability, search, evolutionary computation, neural networks, or language models—can solve every compositional problem. Instead, it defines a hybrid architecture in which each method is selected for a specific responsibility and must operate through shared musical concepts, constraints, and contracts.

The central operational principle is:

> **Generate possibilities, reason about their consequences, evaluate them in context, and commit only what the composition can support.**

The system must not confuse statistical plausibility with musical purpose, novelty with originality, complexity with interest, or a numerical score with artistic judgement.

---

# How to use this manual

This is the seventh volume in the IDM Generative Instrument library. It is a developer-facing companion to the governing constitution and the musical ontology.

The documents have distinct responsibilities:

| Document | Primary question |
|---|---|
| **Philosophy, Principles & Design Constitution** | What should the instrument believe and protect? |
| **Musical Ontology, Representation & Composition Data Architecture** | What musical objects exist, and how are they represented? |
| **Generative Intelligence, Algorithms & Decision-Making** | How does the instrument reason, generate, compare, and decide? |
| Perceptual orchestration and evaluation manuals | How can musical and perceptual consequences be assessed? |
| Composition and sound-design manuals | What musical and sonic materials can the instrument work with? |

This manual references canonical entities from the ontology—such as `CompositionBrief`, `Composition`, `Section`, `Phrase`, `Motif`, `Pattern`, `Voice`, `Candidate`, `Transformation`, `DecisionRecord`, and `MutationContract`—without redefining their complete storage schemas. The ontology remains authoritative for identity, relationships, time representation, persistence, and serialization.

## Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** describe implementation requirements.

- **MUST / MUST NOT** indicate requirements that protect musical integrity, project integrity, or reproducibility.
- **SHOULD / SHOULD NOT** indicate strong defaults that may be overridden with a documented reason.
- **MAY** indicates an optional capability.

An algorithm may be replaced without changing the architecture, provided its replacement honours the same inputs, outputs, invariants, and decision contracts.

## What this manual does not prescribe

It does not prescribe a fixed IDM sound, a preferred tempo, one canonical formal structure, one universal definition of beauty, or a single algorithmic technique. It does not require machine learning. It does not require the system to compose autonomously. It does not replace the composer, the domain manuals, or the ontology.

It specifies how computational methods are selected, coordinated, constrained, evaluated, and made accountable to a composition.

---

# Part I — What generative intelligence means

## 1. Generation, composition, and decision-making are different operations

A software system can generate events without composing. It can compose locally coherent phrases without producing a coherent track. It can produce a structurally coherent track that does not fulfil the artistic brief. It can satisfy the brief but be difficult to edit or reproduce.

For this reason, the system distinguishes at least six operations:

1. **Interpretation** — converting an artistic request into a structured set of intentions, constraints, priorities, and unresolved questions.
2. **Planning** — deciding what kinds of musical events and transformations should occur, at what structural levels, and in what relationships.
3. **Generation** — proposing possible musical material or actions.
4. **Evaluation** — checking validity and estimating the consequences and suitability of proposals.
5. **Selection and commitment** — choosing a candidate, preserving the choice, and integrating it into the project.
6. **Revision** — changing an accepted or proposed part of the work while respecting its mutation contract and dependencies.

These operations may be implemented by one process or many services, but their responsibilities MUST remain conceptually separate.

### 1.1 Generator

A generator produces candidates from inputs and a defined method. It may be deterministic, stochastic, rule-based, learned, evolutionary, or hybrid.

A generator does not automatically have authority to commit its output.

### 1.2 Planner

A planner selects goals, subgoals, dependencies, temporal placement, and acceptable future states. It reasons at a higher level than a local pattern generator.

### 1.3 Evaluator

An evaluator produces evidence about a candidate. It may report validity, constraint violations, musical relationships, perceptual estimates, technical defects, and uncertainty.

An evaluator does not own the artistic decision unless the system has explicitly delegated a narrow decision to it.

### 1.4 Selector

A selector compares candidates against priorities, constraints, and preferences. It may return one candidate, a ranked set, a Pareto set, or a request for human judgement.

### 1.5 Composer-facing instrument

The complete system is an instrument when the user can inspect, alter, accept, reject, freeze, compare, and extend its output without losing project integrity.

## 2. A practical definition of compositional intelligence

For this project, **compositional intelligence** is the capacity of a system to make context-sensitive decisions about musical material and its relationships over time, while preserving an explicit artistic intention and the integrity of the composition.

This definition does not claim consciousness, human-like understanding, or autonomous aesthetic authority. It defines observable capabilities.

A system demonstrates compositional intelligence when it can:

- infer a workable interpretation of a brief;
- identify which decisions belong to global, sectional, phrase, material, or event levels;
- generate several meaningfully different candidates;
- preserve an idea's identity across permitted transformations;
- detect conflicts between local and global goals;
- coordinate related voices and layers;
- reason about repetition, contrast, development, and return;
- explain the evidence behind a recommendation;
- admit uncertainty or failure;
- preserve accepted user decisions;
- reproduce or deliberately revise a prior result.

A system does not demonstrate compositional intelligence merely because it creates a large number of events, uses a complex model, generates audio that resembles a reference corpus, or has many exposed parameters.

## 3. The intelligence architecture: control plane and musical data plane

Separate the **control plane** from the **musical data plane**.

### 3.1 Control plane

The control plane governs intent and decisions. It contains:

- brief interpretation;
- project priorities;
- global and local plans;
- constraint policies;
- generation requests;
- candidate lifecycle;
- evaluation profiles;
- selection policies;
- user approvals;
- decision history.

### 3.2 Musical data plane

The musical data plane contains the actual composition entities and their relationships:

- sections and phrases;
- material, motifs, and patterns;
- voices and roles;
- events and automation;
- sound assignments and realisations;
- transformations and lineage.

The control plane may request a change to the data plane, but it MUST do so through typed commands or transactions. A generator MUST NOT quietly edit the project store as a side effect of producing a candidate.

### 3.3 Why this separation matters

Without this separation, generation logic tends to become entangled with project mutation, UI state, audio playback, and rendering. The result is difficult to test and dangerous to revise. A candidate preview can accidentally become accepted material; a UI slider can mutate an unrelated voice; a render callback can silently alter timing.

The control plane should describe *what is requested and why*. The data plane should represent *what the composition currently contains*.

## 4. The core decision loop

Every substantial generative operation SHOULD follow the same explicit cycle:

```text
INTERPRET REQUEST
        |
        v
RESOLVE SCOPE AND AUTHORITY
        |
        v
BUILD GENERATION CONTEXT
        |
        v
GENERATE CANDIDATES
        |
        v
VALIDATE STRUCTURAL AND HARD CONSTRAINTS
        |
        v
EVALUATE MUSICAL CONSEQUENCES
        |
        v
SELECT / RANK / REQUEST HUMAN CHOICE
        |
        v
COMMIT AS A TRANSACTION OR REJECT
        |
        v
RECORD DECISION, PROVENANCE, AND SEED
```

A failed stage MUST return a meaningful result. It must not silently skip to commitment.

### 4.1 Candidate lifecycle

A candidate passes through explicit states, for example:

`created → validated → evaluated → presented → accepted → committed`

Alternative terminal or intermediate states may include:

`rejected`, `superseded`, `invalid`, `needs_review`, `archived`.

The exact state names should follow the ontology registry. The important rule is that **candidate**, **accepted material**, and **committed composition data** are not synonyms.

---

# Part II — The decision hierarchy

## 5. Musical decisions occur at different scales

A generator should not choose an event in isolation when the choice depends on a higher-level purpose. The system therefore uses nested decision levels.

| Level | Primary question | Typical output |
|---|---|---|
| Artistic intent | What experience or identity is being pursued? | Brief interpretation and priorities |
| Global composition | What is the overall trajectory? | Macro-plan and structural states |
| Section | What is this region's role? | Section plan and local constraints |
| Phrase | What should this phrase do? | Phrase function and developmental action |
| Material | Which musical idea is used? | Motif, pattern, bass, or harmonic material |
| Voice / role | How does a part relate to other parts? | Voice plan and interaction constraints |
| Event | What happens at this exact time? | Notes, triggers, automation, or sound events |
| Realisation | How is the event made audible? | Instrument, synthesis, effects, and rendering data |

### 5.1 Top-down and bottom-up reasoning

The architecture needs both directions.

**Top-down reasoning** passes intention and constraints from higher levels to lower levels. A section intended to withdraw should not receive an uncontrolled density increase from a local generator.

**Bottom-up reasoning** passes evidence from lower levels to higher levels. A planner may discover that a proposed motif cannot be realised within the available range, that too many layers compete for the same register, or that a section's material has insufficient variation.

The planner should be able to revise its plan when lower-level evidence reveals a real conflict. Hierarchy is not a one-way command chain; it is a system of owned decisions and controlled feedback.

## 6. Decision ownership and conflict resolution

Every important decision MUST have an owner or an explicit shared-decision policy.

Examples:

- The composition director owns the global section trajectory.
- The phrase planner owns phrase-level function within a section.
- A motif generator owns candidate motif construction.
- The orchestrator owns voice-role assignment and interaction.
- The user owns accepted creative decisions unless they explicitly delegate them.
- The renderer owns sample-level execution, not compositional rewriting.

### 6.1 Conflict precedence

When two instructions conflict, resolve them in this order:

1. Project integrity and explicit user protection (frozen material, locked regions, accepted constraints).
2. Hard constraints and safety/technical validity.
3. Explicit artistic intent and high-level composition decisions.
4. Section and phrase contracts.
5. Material identity and dependency rules.
6. Local generator preferences.
7. Stochastic variation and cosmetic preferences.

A lower-level generator MUST NOT override a higher-level rule just because its local score is higher.

### 6.2 Hard constraints, soft constraints, preferences, and objectives

Keep these categories distinct.

- **Hard constraint:** must be satisfied for a candidate to be valid.
- **Soft constraint:** desirable but violable at a cost.
- **Preference:** a contextual bias that influences selection but does not define correctness.
- **Objective:** a dimension the system attempts to improve or balance.
- **Exclusion:** an explicit prohibition.
- **Invariant:** a property that must remain unchanged during a defined operation.
- **Budget:** a bounded quantity, such as a maximum number of altered events or a permitted range of structural change.

Do not place all of these into an untyped numeric weight vector. Each has different semantics and should have a distinct representation.

## 7. Plans are hypotheses, not immutable scripts

A plan is a structured hypothesis about how the composition may develop. It should be specific enough to guide generators but flexible enough to respond to useful discoveries.

A plan SHOULD specify:

- goals and constraints;
- section or phrase roles;
- material anchors and expected relationships;
- intended transformations;
- density, attention, or energy trajectories where useful;
- transition conditions;
- protected material;
- uncertainty or unresolved decisions;
- completion conditions.

A plan MUST distinguish fixed commitments from exploratory intentions. The system should not turn every descriptive word in a brief into an inflexible rule.

---

# Part III — Algorithm families and their proper responsibilities

## 8. Algorithm selection begins with the musical problem

The system should never ask, “Which algorithm should generate this track?” as though one algorithm were responsible for everything.

It should ask:

- What is the musical decision?
- At what timescale does it operate?
- What information does it require?
- What constraints must it honour?
- How much variation is appropriate?
- What kind of output is required?
- How will the result be evaluated?
- What must be preserved if it is regenerated?

The answer may combine several methods.

## 9. Deterministic rule systems and transformation operators

Rule-based methods encode explicit transformations and constraints.

### Suitable uses

- transposition, inversion, retrograde, rotation, augmentation, diminution;
- register and range enforcement;
- rhythmic displacement;
- event filtering and selection;
- motif-preserving variation;
- instrument-role restrictions;
- deterministic section transitions;
- validation and repair of known structural defects.

### Strengths

- explainable;
- reproducible;
- fast;
- easy to test;
- naturally compatible with mutation contracts;
- reliable for exact invariants.

### Limitations

- can produce predictable material;
- rule conflicts can become difficult to manage;
- an overgrown rule set can encode accidental assumptions;
- a rule that is appropriate locally may be inappropriate globally.

Rules should be modular, named, scoped, versioned, and evaluated in context. Avoid a single global “music rules” module.

## 10. Probabilistic and stochastic methods

Stochastic methods sample from probability distributions or transition processes.

### Suitable uses

- controlled event variation;
- accent and articulation alternatives;
- bounded timing deviations;
- candidate selection among valid options;
- local rhythmic or pitch exploration;
- texture density and activity variation;
- probabilistic transitions between explicitly defined states.

### Important distinction: randomness versus uncertainty

Randomness is a computational mechanism. Uncertainty is a property of the system's knowledge or prediction. They are related but not identical.

A stochastic generator can be fully reproducible. A deterministic model can still be uncertain about whether its recommendation is musically appropriate.

### Distribution choice matters

Do not use uniform random selection by default. Uniform sampling may give equal probability to outcomes that have very different musical consequences.

Possible distributions include:

- categorical distributions for discrete choices;
- weighted categorical distributions for contextual preferences;
- Bernoulli distributions for event presence/absence;
- binomial distributions for bounded counts;
- Gaussian distributions for bounded continuous deviations, with truncation or transformation where necessary;
- beta distributions for proportions and probabilities;
- Poisson-like processes for event counts when assumptions are justified;
- empirical distributions learned from a project or approved material set.

The distribution, its parameters, and the musical meaning of the sampled variable should be explicit.

## 11. Markov models and state-transition systems

Markov models are useful when the next state depends on a limited representation of current context.

### Suitable uses

- local transitions between rhythmic states;
- articulation or texture states;
- controlled event sequences;
- probabilistic phrase continuations when the state captures relevant context;
- transitions in a composition director.

### Limitations

A low-order Markov model may capture local regularities but fail to preserve long-range intent, motif identity, and section-level structure. This is not a reason to reject Markov methods; it is a reason to place them at the correct level and enrich their state.

Use higher-level conditioning, hierarchical state, explicit memory, or a planner when longer dependencies matter. Do not expect a local transition table to invent an entire composition's form.

### State design

A state should contain only the information required for the decision. It may include:

- current structural role;
- recent motif or pattern identity;
- current activity or density band;
- harmonic or pitch context;
- recent transition history;
- allowed next states;
- a cooldown or recurrence constraint.

State explosion is a real design risk. Factor the state into independent dimensions where possible.

## 12. Grammars, rewriting systems, and hierarchical expansion

A grammar describes how higher-level structures can expand into lower-level structures.

A simplified compositional grammar might express:

```text
Composition  -> Opening Development Contrast Return Ending
Development  -> Establishment Expansion Transformation
Phrase       -> Statement Response Extension
Pattern      -> Core Motif Variation
Variation    -> Displacement | Fragmentation | Ornamentation
```

This is a conceptual grammar, not a universal form template.

### Suitable uses

- formal planning;
- phrase-role expansion;
- motif-family construction;
- controlled structural alternatives;
- ensuring that a composition contains required functional stages;
- generating related but non-identical sections.

### Design guidance

- Separate syntactic validity from musical quality.
- Allow optional productions and alternative expansions.
- Attach constraints to productions where necessary.
- Track lineage from parent structure to expanded child.
- Avoid grammar rules that force one style or one track length.
- Use stochastic production selection only after hard constraints are known.

## 13. Constraint programming, SAT, SMT, and constraint optimisation

Constraint methods search for values that satisfy a defined set of requirements.

### Suitable uses

- voice-range and overlap constraints;
- rhythmic alignment or disalignment requirements;
- bounded polyphony;
- instrument and register allocation;
- simultaneous event compatibility;
- phrase length and transition restrictions;
- multi-part arrangements with interdependent conditions;
- selecting a set of material objects under limited resources.

### Constraint hierarchy

Separate:

1. **Feasibility constraints:** define whether a solution is allowed.
2. **Preference constraints:** define desirable properties.
3. **Optimisation objectives:** define what should be improved.

Do not encode aesthetic preferences as hard constraints unless the project specifically requires them.

### Incremental solving

For interactive use, prefer incremental solving when the solver and problem formulation support it. If the user changes one region, the system should not unnecessarily solve unrelated parts of the composition from scratch. Constraint-programming approaches to music have a substantial research history; Anders and Miranda's survey (2011) is a useful entry point, while Herremans and Chew's MorpheuS work demonstrates the use of recurring-pattern and tension constraints in structured generation.

### Failure behaviour

A solver must be able to report:

- feasible solution found;
- no feasible solution found;
- search limit reached;
- incomplete or approximate result;
- conflicting or unsatisfiable constraints, when the solver can provide such evidence.

The system must not silently weaken hard constraints to produce an answer. It may propose a conflict-resolution plan, but changing priorities requires explicit authority.

## 14. Search and optimisation

Search methods explore a space of candidate solutions.

### Useful methods

- exhaustive search for small spaces;
- beam search for bounded candidate exploration;
- best-first search for prioritised expansion;
- hill climbing for local improvement;
- simulated annealing for controlled escape from local optima;
- branch-and-bound for constrained optimisation;
- dynamic programming when subproblems overlap and optimal substructure applies;
- Monte Carlo tree search where sequential decisions and rollouts are meaningful.

### Search design questions

Every search component must specify:

- state representation;
- successor-generation method;
- feasibility checks;
- evaluation or heuristic function;
- stopping condition;
- maximum expansion or time budget;
- diversity policy;
- accepted-result policy.

A heuristic is not a truth oracle. Search can efficiently optimise a bad objective. Therefore, heuristic design and musical evaluation require independent review.

## 15. Evolutionary algorithms and population-based exploration

Evolutionary methods maintain a population of candidates and iteratively apply selection, variation, and replacement.

### Suitable uses

- exploring combinations of motifs or patterns;
- evolving orchestration configurations;
- searching sound-design parameter combinations;
- finding alternative structural plans;
- discovering candidates under several competing objectives.

### Representation comes first

A poor chromosome representation produces poor search behaviour. The representation must preserve meaningful musical units. For example, a chromosome made from arbitrary event indices may destroy phrase identity during crossover.

Potential representations include:

- transformation sequences applied to a seed motif;
- structured phrase plans;
- role assignments;
- motif-family graphs;
- parameterised sound-object definitions;
- bounded sets of section-level decisions.

### Variation operators

Use musical operators rather than arbitrary bit flips:

- substitute one phrase with a related candidate;
- alter a permitted rhythm cell;
- change a voice relationship;
- swap a material assignment;
- mutate one transformation parameter;
- change one section-level strategy;
- vary a bounded sound-object parameter group.

### Risks

- premature convergence;
- loss of diversity;
- metric exploitation;
- excessive compute;
- invalid offspring;
- weak relationship between fitness and musical value.

Track diversity and ancestry. Keep multiple promising lineages where possible. Do not let one proxy score determine the fate of every candidate.

## 16. Agent-based and multi-agent systems

Agents can model specialised decision-makers or musical roles.

Possible agents:

- form planner;
- rhythmic planner;
- motif developer;
- bass and harmonic planner;
- orchestration planner;
- perceptual evaluator;
- constraint checker;
- sound-design proposer.

### Agents must have contracts

Each agent must define:

- its owned decision scope;
- required context;
- permitted outputs;
- constraints it must respect;
- dependencies;
- conflict-resolution policy;
- computational budget;
- whether it may propose, select, or commit.

Agents should not freely mutate shared project state. They should return proposals through the same candidate and transaction mechanism as other generators.

### Avoid fictional intelligence

Multiple agents do not automatically produce better reasoning. An agent architecture can increase latency, coordination cost, and contradictory proposals. Use agents only when specialised responsibilities and their interactions justify the complexity.

## 17. Cellular automata, fields, attractors, and dynamical systems

These methods can produce evolving behaviour from local rules or continuous state.

### Suitable uses

- evolving textures;
- rhythmic cells with neighbourhood dependencies;
- spatial or spectral activity fields;
- slowly changing probability maps;
- controlled instability;
- material evolution over a section;
- visual/audio-linked processes where the musical mapping is explicit.

### Design concerns

- define boundary conditions;
- define update rate and musical time scale;
- constrain state ranges;
- prevent uncontrolled drift;
- establish reset and return conditions;
- record initial state and parameters;
- map system states to musical actions through an interpretable adapter.

An attractive chaotic process is not necessarily a useful composition engine. The musical mapping matters more than the mathematical novelty of the underlying process.

## 18. Learned models: neural networks, transformers, diffusion, and language models

Learned models can propose, continue, transform, classify, embed, or render musical material. They can be useful components, but they should not become an excuse to abandon explicit musical structure and project integrity.

### Possible responsibilities

- generating candidate motifs or phrases;
- predicting continuations from a context;
- proposing transformations;
- estimating similarity or style characteristics;
- producing embeddings for retrieval and clustering;
- mapping text or descriptive controls to candidate parameters;
- suggesting formal plans;
- generating or transforming audio.

### Model-family considerations

| Model family | Potential strength | Important limitation or risk |
|---|---|---|
| RNN / LSTM | Sequential context and compact continuation models | Long-range structure and error accumulation can be difficult |
| Transformer | Flexible context modelling and conditioning | Long sequences, representation choices, and weakly grounded high-level plans remain challenges |
| VAE | Continuous latent spaces and interpolation | Latent dimensions may not correspond to useful musical controls |
| GAN | Generative sampling and distribution learning | Training stability and coverage can be difficult |
| Diffusion | Iterative generation and conditional refinement | Sampling cost and structural controllability must be considered |
| LLM | Natural-language interpretation and high-level planning | Symbolic precision, temporal alignment, and execution fidelity need external validation |
| Audio models | Timbre, audio continuation, and sound-level transformation | May not expose editable symbolic structure or preserve project-level provenance |

This table is a selection aid, not a ranking. Different implementations have different capabilities. The 2026 survey by Duan, Yu, and Briot discusses recent model families and identifies continuing challenges around musicality, consistency, controllability, representation, and evaluation.

### Required boundary

A learned model should output a typed candidate or proposal. The host system must validate it against the ontology, project constraints, and mutation contract before it can become accepted composition data.

### Training and data provenance

Any learned component must record, as appropriate:

- model identifier and version;
- source or licence information for training and fine-tuning data where available;
- conditioning inputs;
- decoding parameters;
- random seed or sampling state;
- external model endpoint/version if applicable;
- known limitations;
- whether output may be regenerated exactly.

Do not imply exact reproducibility when the model provider or runtime does not guarantee it.

## 19. Retrieval and case-based generation

Retrieval can find prior material with useful properties and adapt it to a new context.

### Suitable uses

- finding a motif with a desired contour or rhythmic profile;
- retrieving sound-object candidates;
- reusing a successful transition strategy;
- finding related material from the same composition;
- retrieving reference projects for testing;
- proposing variations from an approved material library.

### Retrieval is not composition by itself

A nearest-neighbour result may be similar but contextually unsuitable. Retrieval must be followed by adaptation, validation, and evaluation.

Store provenance and source relationships. Make clear whether retrieved material is copied, transformed, or merely used as a reference.

## 20. Hybrid methods are the default architectural assumption

A strong system may combine several methods in one decision chain.

Example:

1. A hierarchical planner defines a phrase function.
2. A grammar proposes phrase structures.
3. A motif generator creates related candidates.
4. A stochastic operator supplies bounded rhythmic alternatives.
5. A constraint solver rejects invalid pitch or timing relationships.
6. A perceptual evaluator estimates density and role competition.
7. A selector returns a small diverse candidate set.
8. The composer chooses one candidate.
9. The mutation engine records the operation and its provenance.

The architecture should make these combinations explicit. “Hybrid” must not mean that unrelated algorithms are connected without shared contracts. Classical surveys of algorithmic composition and computational creativity provide useful taxonomies of rule-based, statistical, evolutionary, and other approaches; more recent reviews extend that landscape to symbolic, audio, multimodal, neural, and interactive systems. See Papadopoulos and Wiggins (1999), Herremans, Chuan, and Chew (2017), Carnovalini and Rodà (2021), and Duan, Yu, and Briot (2026) in the references.

---

# Part IV — Hierarchical generation and planning

## 21. Plan before generating at scale

Large generation tasks should begin with a plan or a defined exploratory strategy. The plan may be incomplete, but it should specify enough context for lower-level generators to know what they are trying to achieve.

A full planning stack may include:

1. brief interpretation;
2. global trajectory proposal;
3. section-role assignment;
4. phrase-function planning;
5. material selection and development;
6. voice and role coordination;
7. event generation;
8. sound realisation.

Not every project requires all stages to be fully automated. The user may specify some stages and delegate others.

## 22. Global composition planning

The global planner works with the composition's identity, duration constraints, formal intention, material vocabulary, and accepted anchors.

It SHOULD describe:

- the broad sequence of structural states;
- what material should be introduced, developed, withheld, transformed, or returned;
- which sections share material;
- expected areas of contrast;
- where the composition should reduce, intensify, pause, or redirect attention;
- where the ending becomes possible;
- which elements remain unresolved intentionally.

Avoid making the plan a rigid bar-by-bar script unless that is the explicit artistic brief.

## 23. Section planning

A section plan should define a functional role and its boundaries.

Possible role labels include establishment, expansion, fragmentation, contrast, withdrawal, accumulation, destabilisation, return, transition, and ending. These are descriptive tools, not mandatory genre stages.

Each section plan may contain:

- expected active roles;
- material anchors;
- new material allowance;
- permitted transformations;
- rhythmic and harmonic context;
- activity/density tendencies;
- perceptual focus;
- dependencies on prior sections;
- transition-in and transition-out requirements;
- completion condition.

## 24. Phrase planning

Phrase planning defines a local musical action within a section.

Possible phrase intents:

- state an idea;
- answer or contradict an idea;
- extend an unfinished idea;
- fragment a motif;
- shift emphasis;
- delay or avoid resolution;
- prepare a new event;
- reduce material;
- create a temporary interruption;
- recall earlier material.

Phrase intents SHOULD be linked to actual material and relationships. A label without a corresponding musical consequence is not enough.

## 25. Dependency-aware planning

Plans should expose dependencies.

For example:

- a return phrase depends on an earlier motif;
- a transformation depends on a source material object;
- a bass response depends on a rhythmic anchor;
- a transition may depend on a sound object introduced earlier;
- a section may require a previous event to be withheld or removed.

The planner must know whether a dependency is mandatory, optional, or merely preferred. If a source object is deleted or frozen, the system should detect affected dependents before proceeding.

## 26. Replanning and plan repair

Replanning is permitted when evidence shows that the original plan cannot be fulfilled or no longer makes sense.

Triggers may include:

- no feasible candidate exists;
- an accepted edit changes a dependency;
- the user changes the brief;
- a material candidate is accepted that suggests a new direction;
- perceptual evaluation reveals serious competition;
- a section exceeds its activity or duration budget;
- the chosen sound realisation changes the perceptual effect materially.

Replanning MUST distinguish between:

- revising an uncommitted proposal;
- revising a flexible plan component;
- changing an accepted structural decision;
- changing frozen material.

The last two require explicit authority and an impact report.

---

# Part V — Candidate generation and selection

## 27. Why candidate-based generation matters

A generator should normally produce a set of alternatives rather than treating its first output as the answer.

Candidates provide:

- comparison;
- variation;
- recovery from weak proposals;
- human choice;
- evidence about the search space;
- a way to separate proposal generation from commitment.

The number of candidates should be appropriate to the task. More candidates are not always better; they increase evaluation cost and can overwhelm the composer.

## 28. Candidate validity before candidate quality

Use a staged evaluation pipeline.

### Gate 1 — Schema validity

Does the candidate conform to the ontology and data contracts?

### Gate 2 — Referential validity

Do all referenced objects exist? Are identities and dependencies valid?

### Gate 3 — Temporal validity

Are event times, durations, tempo references, and metric positions valid?

### Gate 4 — Hard constraints

Does the candidate obey protected ranges, locked material, exclusions, and required conditions?

### Gate 5 — Mutation-contract compliance

Did the operation change only the permitted region and dimensions?

### Gate 6 — Musical evaluation

Does the candidate have relevant compositional properties and relationships?

### Gate 7 — Perceptual and realisation evaluation

Does it remain intelligible and useful when orchestrated or rendered?

Candidates that fail hard gates should not be silently repaired unless repair is an explicit operation with its own record.

## 29. Candidate diversity

A candidate set should contain meaningfully distinct possibilities, not trivial variations of one solution.

Diversity can be measured across relevant dimensions:

- rhythmic profile;
- motif contour or interval structure;
- phrase shape;
- voice relationship;
- section strategy;
- orchestration;
- density trajectory;
- transformation type;
- timbral or realisation strategy.

Do not maximize difference indiscriminately. A candidate can be different but irrelevant. Diversity must be measured inside the current task's intent and constraints.

## 30. Multi-objective evaluation

Musical quality is not a single scalar property. Candidate comparison may consider:

- brief alignment;
- identity preservation;
- local coherence;
- relationship to existing material;
- development potential;
- rhythmic interest;
- melodic/harmonic suitability;
- perceptual clarity;
- structural usefulness;
- novelty;
- technical validity;
- ease of editing;
- user preference.

### 30.1 Avoid universal weighted sums

A simple weighted score can be useful for a narrowly scoped decision, but a universal weighted sum is dangerous. It can obscure trade-offs, overvalue easy-to-measure features, and make arbitrary weights appear objective.

Prefer a combination of:

- hard feasibility gates;
- lexicographic priority for non-negotiable objectives;
- Pareto comparison for genuinely competing dimensions;
- pairwise user preferences;
- task-specific weighted scores when their semantics are documented;
- qualitative review for dimensions that resist reliable automation.

### 30.2 Pareto dominance

Candidate A dominates candidate B when A is no worse on every objective under consideration and strictly better on at least one. Non-dominated candidates form a Pareto set.

A Pareto set is useful because it preserves alternatives with different strengths rather than pretending there is one universally best result.

### 30.3 Normalisation

Before comparing numeric metrics, document their range, direction, context, and calibration. A 0.8 value on one metric is not automatically comparable to 0.8 on another.

### 30.4 Candidate explanations

Expose the evidence behind a candidate's position:

- which constraints it satisfies;
- which objectives it performs well on;
- what trade-offs it introduces;
- what material it preserves;
- what relationships it changes;
- what remains uncertain.

## 31. Selection policies

Possible selection policies include:

- choose the highest-ranked feasible candidate;
- return a diverse shortlist;
- choose among a Pareto set through user preference;
- choose randomly from a qualified set using a recorded seed;
- request clarification when goals conflict;
- ask the user to choose when the evaluator cannot distinguish alternatives reliably.

A system should know when not to decide.

## 32. Candidate comparison as a first-class operation

Comparison should be contextual and local.

A useful comparison might state:

- Candidate A preserves the original rhythm and changes articulation.
- Candidate B displaces two accents and increases local instability.
- Candidate C replaces the motif with a related fragment and creates a stronger contrast.

A poor comparison merely prints a list of parameter differences without explaining their musical consequences.

---

# Part VI — Controlled randomness and uncertainty

## 33. Randomness must be scoped and named

A single global random-number generator is not sufficient for a complex composition system. Adding one random call to the percussion generator should not unexpectedly change every later melody, automation curve, and sound-design result.

Use independent deterministic random streams for meaningful scopes, such as:

- composition planning;
- section generation;
- motif generation;
- rhythm generation;
- orchestration;
- sound realisation;
- mutation experiments.

### 33.1 Stable seed derivation

Derive child seeds from stable identifiers and operation context rather than call order alone.

Conceptual formula:

```text
child_seed = HASH(
    project_seed,
    composition_id,
    subsystem_id,
    target_entity_id,
    operation_id,
    generation_revision
)
```

The hash function, encoding, and version must be documented. Avoid process-randomised language hashes when cross-run reproducibility is required.

### 33.2 Seed isolation

A generator should not consume another subsystem's random stream. Candidate ordering should not shift because an unrelated subsystem performed extra draws.

### 33.3 Reproducibility record

A seed alone is not a complete provenance record. Store:

- root and derived seed identifiers;
- algorithm and implementation version;
- configuration and constraints;
- input entity revisions;
- relevant model/plugin version;
- candidate generation request;
- selection policy;
- environment information when needed;
- whether deterministic equivalence is guaranteed or best-effort.

## 34. Hierarchical probability

Probability should be applied at the level where the decision belongs.

For example:

- global plan selects a broad developmental strategy;
- section planner chooses one of several compatible section actions;
- phrase planner selects a transformation class;
- event generator samples details within the selected transformation.

This is preferable to a single flat random process in which every note and section is sampled independently.

## 35. Entropy is not a universal creativity control

Entropy describes uncertainty in a probability distribution under a chosen representation. It does not directly measure originality, interest, complexity, or artistic value.

A system may expose a control such as “increase unpredictability,” but it should map that control to specific dimensions and scopes:

- event selection uncertainty;
- accent variation;
- phrase transformation variety;
- section strategy alternatives;
- sound-parameter exploration.

The user should be able to understand which aspects are affected.

## 36. Bounded variation and mutation budgets

A variation budget limits how much a generator may change at once.

Possible budgets:

- maximum altered events;
- permitted timing deviation;
- maximum pitch displacement;
- maximum number of new materials;
- allowed register shift;
- allowed structural edits;
- allowed number of changed voices;
- permitted timbral deviation.

Budgets should be relative to the source material where possible. A four-note motif and a 400-event pattern should not be governed by the same absolute event-change threshold.

## 37. Uncertainty and confidence

The system should distinguish:

- **aleatoric uncertainty:** variability inherent in the chosen stochastic process;
- **epistemic uncertainty:** uncertainty due to limited information, model limitations, or ambiguous context;
- **constraint uncertainty:** ambiguity in how a human brief should be formalised;
- **evaluation uncertainty:** uncertainty in the quality estimate itself.

The UI and decision records should not collapse these into one generic confidence percentage.

If the system cannot determine what “more organic” means in the current project, it should present an interpretation or ask for clarification rather than silently altering multiple unrelated parameters.

---

# Part VII — Material development and relational generation

## 38. Generate relationships, not isolated layers

A common failure of generative music software is to generate a drum pattern, a bass line, a melody, and a texture independently, then place them together. Each layer may be locally plausible while the combined result lacks interaction.

Generation should therefore be relationship-aware.

Examples:

- bass responds to selected percussion accents;
- melodic rhythm complements or deliberately conflicts with a rhythmic anchor;
- a texture derives its envelope rhythm from a motif;
- a secondary voice answers a phrase rather than duplicating it;
- a later section transforms a source pattern;
- an automation gesture reinforces or contradicts a musical event intentionally.

## 39. Material-first, role-first, and context-first generation

Three useful strategies can coexist.

### Material-first

Start with an identity-bearing idea, then derive related parts and transformations.

Best when the composition depends on a distinctive motif or sound object.

### Role-first

Define musical roles and their interactions, then generate material to fulfil them.

Best when the track needs a clear arrangement or perceptual architecture.

### Context-first

Analyse the existing composition and generate a part that responds to its current state.

Best for continuation, local regeneration, and filling a specific compositional gap.

The brief and current project state should determine which strategy is appropriate.

## 40. Cross-voice coordination

For simultaneous voices, generate and evaluate shared constraints before finalising each line.

Potential shared context:

- harmonic or pitch field;
- rhythmic anchors;
- register allocation;
- phrase boundaries;
- motif relationships;
- call-and-response schedule;
- activity budget;
- perceptual foreground assignment.

Independent generators may still contribute, but their outputs must be reconciled before commitment.

## 41. Motif-family generation

A motif family is a set of related materials connected by explicit lineage or transformation relationships.

A motif-family generator should be able to:

1. accept a source motif or seed idea;
2. identify dimensions that define its identity;
3. identify dimensions permitted to change;
4. propose transformation operators;
5. generate candidates;
6. evaluate identity retention and useful difference;
7. preserve the source and record lineage.

Identity may include contour, interval profile, rhythm, accent pattern, register, articulation, phrase function, or timbral identity. The relevant dimensions depend on the source material.

## 42. Development without arbitrary replacement

A development operation should state how the new material relates to its predecessor.

Possible relationships:

- repetition;
- ornamentation;
- fragmentation;
- extension;
- compression;
- rhythmic displacement;
- inversion or retrograde;
- register transfer;
- reorchestration;
- timbral transformation;
- call-and-response;
- counterpoint;
- harmonic reinterpretation;
- deliberate rupture.

A rupture can be valid, but it should be an intentional compositional action rather than an accidental consequence of unrelated generators.

---

# Part VIII — Mutation and revision intelligence

## 43. Mutation is a typed operation

A mutation must declare:

- target entity or region;
- source revision;
- operation type;
- dimensions allowed to change;
- dimensions to preserve;
- affected dependencies;
- mutation budget;
- constraint policy;
- seed context;
- validation and evaluation requirements;
- rollback strategy.

The ontology's `MutationContract` is authoritative for the full data model. This manual specifies its behavioural semantics.

## 44. Mutation classes

### Event-level mutation

Change one or a few events while preserving their container and identity relationship.

### Pattern-level mutation

Change a rhythmic or pitch pattern under a defined preservation rule.

### Motif-level mutation

Create a related motif variant, preserving selected identity features.

### Phrase-level mutation

Change phrase behaviour, length, function, or internal development.

### Voice-level mutation

Change the behaviour of one voice and check its interactions with other voices.

### Section-level mutation

Change a section's material, roles, activity, or internal progression.

### Structural mutation

Change section order, boundaries, duration, or global relationships. This has the highest dependency impact and should require explicit authorisation.

## 45. Local regeneration

Local regeneration is a core capability.

The system must define a scope and a protection boundary.

For a request to regenerate one drum phrase:

1. identify the target phrase and its source revision;
2. identify related bass or motif dependencies;
3. determine which dependencies are constraints and which are optional references;
4. freeze unrelated accepted material;
5. generate candidates only for the intended scope;
6. evaluate cross-layer consequences;
7. present a diff and impact report;
8. commit through a transaction after selection.

Do not regenerate unrelated content simply because the internal generator currently works at whole-track scope.

## 46. Mutation impact analysis

Before changing an object, compute or estimate its dependents.

The report should distinguish:

- direct dependents;
- indirect dependents;
- frozen dependents;
- accepted material that may be affected;
- optional relationships that may be re-evaluated;
- rendering or cache objects that may become stale.

A mutation engine should not automatically propagate changes through the entire dependency graph. Propagation must follow explicit rules and authority.

## 47. Transactional commit and rollback

A selected candidate should be committed atomically.

A transaction should:

- check the source revision is still current;
- revalidate constraints;
- apply the approved delta;
- update provenance and lineage;
- invalidate only dependent caches;
- create an undo record;
- publish a change event after successful commit.

If any step fails, the project must remain in its prior valid state.

---

# Part IX — Adaptive composition directors and stateful systems

## 48. Why a composition director is necessary

Local generators do not automatically create long-term direction. A composition director maintains the higher-level state and chooses which kind of musical action is appropriate next.

It may oversee:

- formal progression;
- energy and activity tendencies;
- attention focus;
- material introduction and recurrence;
- contrast and withdrawal;
- return and closure;
- unresolved compositional needs.

The director should not directly write every event. It should issue plans and constraints to specialised components.

## 49. State representation

A director's state may include:

- current section and phrase;
- current structural role;
- active material identities;
- recent material history;
- unresolved goals;
- current activity and attention estimates;
- repetition and recurrence counts;
- transition readiness;
- constraints and protected regions;
- uncertainty and pending decisions.

The state should be serializable and reproducible. Hidden mutable state that cannot be inspected or restored is prohibited for core compositional decisions.

## 50. Hysteresis and transition stability

A director should not switch states every time a noisy metric crosses a threshold. Use hysteresis, minimum dwell times, or explicit transition conditions.

Example:

- enter a high-activity state only when the activity estimate exceeds a higher threshold;
- remain there until it falls below a lower threshold;
- require a minimum number of phrases before another structural transition;
- allow explicit override when a user command or formal plan requires immediate change.

The purpose is stability, not rigid repetition.

## 51. Goals, affordances, and transition conditions

The director should reason in terms of available musical actions.

For example:

- If a motif has been established and the section is stable, a transformation may be available.
- If the main material has been withheld, an introduction may be available.
- If density is already high, an additional foreground layer may be blocked or require another layer to withdraw.
- If the composition has reached its planned ending region, new long-term material may be discouraged.

These are conditional affordances, not universal musical rules.

## 52. Completion and termination

Generative systems often continue because they have no defined condition for finishing.

Every composition task should define completion conditions, such as:

- required structural stages have been resolved;
- ending strategy has been selected and realised;
- unresolved dependencies are handled;
- duration is within the permitted range;
- all accepted material is valid;
- export or render prerequisites are satisfied;
- the user has accepted the final state.

The system should be able to stop and report that a task is complete, incomplete, or blocked.

---

# Part X — Evaluation, reward design, and metric integrity

## 53. Evaluation is a separate discipline

The generator and evaluator should not be assumed to share the same blind spots. If a candidate generator is optimised against one narrow metric, it may learn to exploit that metric rather than improve the music.

Evaluation must be plural, contextual, and evidence-based.

## 54. Evaluation dimensions

A project-level evaluation profile may include. Recent evaluation surveys emphasise that system output, user interaction, objective metrics, and human judgement are distinct but related evaluation targets (Lerch et al., 2025). Human-preference benchmarking has also shown why metric alignment with listener judgement must be tested rather than assumed (Solak et al., 2025).

A project-level evaluation profile may include:

1. intent alignment;
2. identity preservation;
3. local coherence;
4. cross-voice relationship quality;
5. motif development;
6. rhythmic and temporal behaviour;
7. harmonic or pitch-field behaviour;
8. formal direction;
9. perceptual organisation;
10. novelty and diversity;
11. technical validity;
12. editability and user usefulness.

Not every decision requires every metric. Select only relevant dimensions for the task.

## 55. Multi-resolution evaluation

Evaluate at the level of the operation.

| Level | Questions |
|---|---|
| Event | Is the event valid and correctly timed? |
| Pattern | Does it have an intended rhythmic/pitch behaviour? |
| Motif | Does it preserve or deliberately alter identity? |
| Phrase | Does it fulfil a phrase function? |
| Voice | Does it interact with other voices appropriately? |
| Section | Does it fulfil its structural role? |
| Composition | Does it develop an identifiable trajectory? |
| Render | Does the realised audio preserve the intended result? |

A local score should not be treated as evidence of global quality.

## 56. Objective metrics: useful but limited

Possible metrics include:

- event density;
- onset distribution;
- inter-onset interval statistics;
- rhythmic similarity;
- pitch-class distribution;
- interval distribution;
- motif recurrence;
- self-similarity matrices;
- section-level feature trajectories;
- register occupancy;
- spectral overlap estimates;
- dynamic range and clipping checks;
- structural and referential validity.

Metrics are measurements of chosen representations, not direct readings of artistic quality. Document what each metric can and cannot support.

## 57. Human evaluation

Human listening remains necessary for dimensions that are difficult to operationalise reliably.

Useful methods include:

- pairwise comparison;
- rank ordering;
- structured listening forms;
- blind A/B tests;
- preference feedback;
- qualitative annotations;
- composer review of editability and creative usefulness.

Ask specific questions. “Which version is better?” is often too broad. Better questions include:

- Which version preserves the identity of the original idea more convincingly?
- Which version creates a clearer relationship between bass and percussion?
- Which transition feels more prepared?
- Which candidate gives the next section more potential?

## 58. Reward hacking and Goodhart's law

When a measure becomes a target, a system may optimise the measure rather than the property it was intended to represent.

Examples:

- maximising novelty by generating incoherent events;
- maximising rhythmic variation by destroying groove identity;
- maximising spectral activity by filling every frequency region;
- maximising formal contrast by making sections unrelated;
- maximising motif recurrence by repeating the motif excessively.

Mitigations:

- use multiple evaluation methods;
- test adversarial examples;
- inspect candidate distributions;
- maintain human review;
- use hard constraints for true invariants;
- avoid using one metric as an all-purpose reward;
- periodically review whether the objective still represents the intended musical property.

## 59. Calibration and uncertainty of evaluators

An evaluator should report confidence or uncertainty only when it has a defined interpretation and calibration method.

It may instead provide qualitative reliability labels:

- directly measured;
- rule-validated;
- estimated by a model;
- inferred from proxy features;
- subjective / requires listening;
- unknown.

Do not present a model estimate as an objective fact.

---

# Part XI — Human-in-the-loop decision-making

## 60. The human is an active decision-maker

The system should support several collaboration modes:

- **Manual:** the user makes decisions; software assists with tools and diagnostics.
- **Advisory:** software proposes alternatives; the user selects.
- **Delegated local generation:** software makes bounded changes within an approved scope.
- **Autonomous draft:** software builds a complete draft under a brief, then presents it for review.
- **Exploratory co-creation:** the user and system alternate decisions and transformations.

The mode and authority should be visible.

## 61. Explicit decision states

Use distinct states for material:

- generated;
- selected as candidate;
- accepted by user;
- committed to project;
- frozen;
- rejected;
- archived;
- superseded.

Do not infer that auditioning a candidate means accepting it.

## 62. Semantic controls

A musical control such as “make this more fragmented” must map to a defined set of possible operations.

The system should:

1. interpret the requested quality;
2. identify relevant musical dimensions;
3. show or record the interpretation;
4. choose permitted transformations;
5. generate alternatives;
6. explain what changed;
7. preserve unrelated properties.

Semantic controls should be local by default. A request on one phrase should not globally alter the composition unless the user explicitly asks for that scope.

## 63. Preference learning

The system may learn project-specific preferences from explicit user feedback, but it must avoid silently turning one choice into a permanent rule.

Separate:

- project preference;
- composition preference;
- session preference;
- global application preference.

Provide inspection, editing, and reset mechanisms. Prefer explicit feedback labels over opaque inference from user behaviour.

## 64. Asking for clarification versus making a proposal

Clarify when ambiguity would materially change the output or risk violating accepted material.

Make a proposal when several interpretations are safe and useful.

Example:

Request: “Make the second half stranger.”

Possible interpretations:

- increase rhythmic displacement;
- fragment established motifs;
- destabilise tonal reference;
- use unexpected orchestration;
- alter formal recurrence.

A good system may offer three clearly differentiated candidate strategies rather than silently applying all five.

## 65. Explainability

Explainability should state:

- the request interpreted;
- the scope affected;
- the operation selected;
- the properties preserved;
- the properties changed;
- the evaluation evidence;
- the remaining uncertainty.

It should not claim to explain artistic meaning completely or manufacture an elaborate rationale after an arbitrary result.

---

# Part XII — Operational architecture and subsystem contracts

## 66. Core components

A reference architecture may include the following components. These are logical responsibilities; a small application may combine them, while a large application may split them into services.

### 66.1 Brief Interpreter

**Input:** `CompositionBrief`, project context, user clarifications.  
**Output:** structured goals, hard constraints, soft constraints, preferences, unresolved questions, and interpretation notes.

It MUST preserve the original brief and distinguish explicit instructions from inferred interpretations.

### 66.2 Composition Director

**Input:** brief interpretation, current composition state, accepted material, evaluation summaries.  
**Output:** global plan, structural state, available actions, and replanning requests.

It MUST NOT directly edit individual events.

### 66.3 Hierarchical Planner

**Input:** global plan and structural context.  
**Output:** section and phrase plans, dependencies, completion conditions.

It MUST keep plans versioned and identify which decisions are flexible.

### 66.4 Material Manager

**Input:** material entities, lineage graph, identity profiles, approved libraries.  
**Output:** material candidates, retrieval results, identity comparison, dependency reports.

It MUST preserve provenance and stable identity.

### 66.5 Generator Registry

**Input:** typed generation request and capability requirements.  
**Output:** compatible generator selection and configuration.

It MUST select generators by task fit, not by a universal hierarchy of sophistication.

### 66.6 Candidate Generator

**Input:** task context, constraints, seed context, algorithm configuration.  
**Output:** candidate set with provenance and declared variation.

It MUST not commit output.

### 66.7 Constraint and Validator Service

**Input:** candidate and applicable contracts.  
**Output:** validation report with explicit failures and warnings.

It MUST distinguish invalid data from an aesthetically weak result.

### 66.8 Musical Evaluator

**Input:** valid candidate, task-specific evaluation profile.  
**Output:** objective features, estimates, qualitative flags, uncertainty, and evidence.

It MUST not imply that its score is final artistic authority.

### 66.9 Candidate Selector

**Input:** candidate set, evaluation evidence, selection policy, user preferences.  
**Output:** ranked set, Pareto set, chosen candidate, or request for human selection.

It MUST preserve alternative candidates when requested.

### 66.10 Mutation Engine

**Input:** target, mutation contract, candidate operation.  
**Output:** proposed delta, dependency impact report, validation result.

It MUST respect frozen and protected material.

### 66.11 Commit Manager

**Input:** accepted candidate or approved delta.  
**Output:** committed transaction, undo record, updated graph, change event.

It MUST apply atomic changes and reject stale revisions.

### 66.12 Decision Ledger

**Input:** decisions, generation requests, selection outcomes, user approvals.  
**Output:** append-only or versioned history with provenance.

It MUST be queryable and exportable. It should not become a dumping ground for opaque debug text.

## 67. Generation request contract

A generation request SHOULD contain at least:

```json
{
  "request_id": "request-uuid",
  "task_type": "phrase_candidate_generation",
  "target": {
    "entity_id": "phrase-identifier",
    "expected_revision": 12
  },
  "context": {
    "composition_id": "composition-identifier",
    "section_id": "section-identifier",
    "related_material_ids": ["motif-a", "pattern-b"]
  },
  "intent": {
    "goal": "create a related but more fragmented phrase",
    "scope": "target_phrase"
  },
  "constraints": {
    "hard": ["preserve_pitch_field", "preserve_tempo_map"],
    "soft": ["retain_accent_identity"],
    "exclusions": ["do_not_modify_frozen_material"]
  },
  "variation_budget": {
    "max_changed_events": 8,
    "allow_length_change": false
  },
  "generation": {
    "candidate_count": 6,
    "algorithm_profile": "motif_fragmentation_v2",
    "seed_context": "derived-from-project-and-operation"
  },
  "selection": {
    "policy": "diverse_shortlist_for_user"
  }
}
```

This is an illustrative request envelope, not a replacement for the ontology's canonical schema. Exact field names should be aligned with the project's schema registry.

## 68. Candidate result contract

A candidate result should include:

- candidate identity;
- target and source revisions;
- generated entity references or proposed delta;
- generator identifier and version;
- algorithm configuration;
- seed provenance;
- mutation contract used;
- validation report;
- evaluation evidence;
- lineage links;
- limitations and uncertainty;
- lifecycle state.

The result should be sufficient to inspect, compare, reproduce where supported, and commit transactionally.

## 69. Decision record

A decision record should explain the operation without pretending that every creative choice has a fully formal justification.

Recommended fields:

- decision identifier;
- timestamp or logical project revision;
- responsible subsystem or user;
- task and target;
- relevant context revision;
- candidate set;
- selection policy;
- accepted candidate or user choice;
- rejected alternatives and reasons, if available;
- constraints applied;
- evaluation evidence;
- seed and algorithm provenance;
- resulting project revision.

The ontology's decision record schema remains authoritative.

---

# Part XIII — Failure modes and recovery

## 70. Common failure modes

| Failure | Symptom | Required response |
|---|---|---|
| Local plausibility, global incoherence | Each phrase works alone but track lacks direction | Revisit global and section planning |
| Over-constrained search | No candidates satisfy every rule | Report conflict; propose explicit relaxation options |
| Under-constrained generation | Candidates are unrelated or invalid | Add context, constraints, or a stronger representation |
| Randomness drift | Small code changes alter unrelated outputs | Isolate random streams and derive seeds by stable scope |
| Candidate collapse | All candidates are nearly identical | Add diversity-aware sampling or alternative methods |
| Novelty inflation | Results are surprising but unusable | Rebalance intent alignment and relationship constraints |
| Metric exploitation | High score but poor listening result | Inspect objective proxy and add independent evaluation |
| Mode collapse | Generator repeats a narrow family of solutions | Expand candidate strategy and monitor diversity |
| State chatter | Director rapidly switches behaviour | Add hysteresis, dwell time, and state memory |
| Destructive regeneration | Accepted unrelated material changes | Enforce mutation scope and transaction checks |
| Silent repair | System changes a candidate without disclosure | Make repair an explicit recorded operation |
| Plan rigidity | System cannot use useful emergent material | Mark flexible plan components and permit controlled replanning |
| Endless generation | System never declares completion | Define termination and completion conditions |
| False confidence | Evaluator presents a proxy as fact | Expose metric type, calibration, and uncertainty |
| Agent conflict | Subsystems issue contradictory proposals | Use ownership, shared context, and conflict resolution |

## 71. No-solution behaviour

When no feasible candidate can be found, return a structured failure report:

1. what was requested;
2. what scope was searched;
3. which hard constraints blocked candidates;
4. whether the search budget was exhausted;
5. which constraints might be relaxed;
6. what material or plan changes could create feasibility;
7. whether human clarification is required.

Do not silently remove a constraint, substitute unrelated material, or claim success with an invalid candidate.

## 72. Partial success

Some tasks can be partially completed. For example, the system may find a valid rhythmic candidate but fail to find a satisfactory cross-voice arrangement.

Report partial results explicitly, with clear boundaries between completed and unresolved stages.

## 73. Recovery and rollback

Every committed operation must be reversible where project semantics allow. If a failed task changes no committed material, it should leave no hidden side effects other than an optional diagnostic record.

---

# Part XIV — Performance, scheduling, and computational budgets

## 74. Budget-aware intelligence

A generative system should be capable of scaling its reasoning effort to the task.

Define budgets for:

- candidate count;
- search depth;
- search nodes or iterations;
- model calls;
- solver time;
- evaluation passes;
- preview rendering;
- memory use;
- wall-clock latency.

The budget policy should reflect user interaction. A fast local variation should not invoke an expensive global search unless requested.

## 75. Progressive generation

For interactive workflows, consider progressive output:

1. return a quick valid candidate;
2. continue exploring better or more diverse candidates;
3. update the candidate set without changing accepted material;
4. allow the user to stop exploration at any time.

Progressive generation must preserve candidate identity and avoid invalidating a candidate that the user has already accepted. New candidates can be added; committed material must not be replaced automatically.

## 76. Caching and invalidation

Cache only outputs whose inputs and dependencies are known.

Cache keys should include relevant revisions, algorithm versions, configuration, and seed context. When an input changes, invalidate only affected results.

A cache hit must not bypass required validation if the contract or relevant state has changed.

## 77. Parallel generation

Independent candidate branches may be generated in parallel if they do not mutate shared state and their random streams are isolated.

Parallel completion order must not alter deterministic selection semantics. Sort or identify candidates using stable identifiers rather than arrival order.

---

# Part XV — Worked decision examples

## 78. Example A: “Make this phrase more unpredictable”

### Weak interpretation

Randomise onset times, pitches, velocities, and instruments.

### Better interpretation

Identify which aspect of predictability the user wants to change. Possible scopes include event-level accents, rhythmic displacement, motif fragmentation, note selection, or phrase continuation.

### Procedure

1. Resolve the target phrase and its revision.
2. Inspect established identity features.
3. Offer or choose a specific unpredictability dimension.
4. Define a bounded mutation contract.
5. Generate several candidates with independent seeds.
6. Validate frozen and hard-constrained properties.
7. Compare identity retention and variation.
8. Present candidates with concise explanations.

### Example candidates

- Candidate A: keep the event order, vary accent placement.
- Candidate B: preserve the motif contour, displace selected onsets.
- Candidate C: fragment the motif and leave larger gaps.

These are meaningfully different interpretations of the same request.

## 79. Example B: generate a new phrase related to an existing motif

### Input

- source motif;
- target phrase role;
- allowed transformations;
- pitch and timing context;
- identity dimensions to preserve;
- mutation budget.

### Strategy

1. Create a transformation set.
2. Generate candidates by applying one primary transformation at a time.
3. Generate a smaller number of compound transformations.
4. Validate musical and structural constraints.
5. Compare candidates against the source and current composition.
6. Return candidates with lineage.

### Important rule

Do not evaluate similarity only as event-by-event equality. A motif may preserve identity through contour, rhythm, accent, or phrase function even when exact pitches differ.

## 80. Example C: “Make the second half more intense”

### Weak interpretation

Increase volume, note density, distortion, and tempo.

### Better interpretation

Treat intensity as multidimensional. Ask which dimensions may change or propose a controlled combination:

- greater event activity;
- faster surface rhythm;
- increased register span;
- denser timbral interaction;
- reduced rests;
- stronger contrast between foreground and background;
- harmonic or textural instability;
- more frequent material transformations.

The planner must ensure that increasing one dimension does not accidentally destroy another important characteristic.

## 81. Example D: local regeneration with protected material

### Request

Regenerate percussion in one phrase while preserving bass and melody.

### Required process

1. Resolve the target phrase and protected voices.
2. Inspect relationships between percussion, bass, and melody.
3. Decide whether the protected voices impose constraints or merely provide context.
4. Generate percussion candidates.
5. Evaluate how each candidate interacts with the protected voices.
6. Produce a delta limited to the percussion target.
7. Show an impact report.
8. Commit only after acceptance.

The system must not modify the bass or melody to improve a percussion candidate.

## 82. Example E: no candidate satisfies all constraints

### Situation

The user requests a phrase of fixed duration, fixed pitch content, fixed accents, a new rhythmic pattern, and no changes to the source motif. The requested changes may be mutually incompatible.

### Correct behaviour

- report that no valid candidate was found;
- identify the conflicting requirements;
- offer specific possible relaxations;
- preserve the original phrase;
- wait for an authorised change or provide a partial result if possible.

The generator must not silently reinterpret the request.

## 83. Example F: a candidate has a high score but sounds weak

### Situation

A candidate scores well on novelty, event density, and rhythmic variation but sounds incoherent in context.

### Correct response

- inspect whether the metrics are appropriate;
- listen in context;
- compare it with the source and other candidates;
- identify whether it breaks material identity or perceptual organisation;
- mark the evaluation as insufficient rather than forcing acceptance;
- update the evaluator or its task profile if the failure is systematic.

The candidate should not be accepted solely because a numeric score is high.

---

# Part XVI — Reference algorithms and implementation patterns

## 84. Pareto filtering

A basic Pareto filter can help preserve candidates that are not dominated across selected objectives. The following example assumes that all objectives have already been normalised so that higher values are better.

```python
from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class CandidateScore:
    candidate_id: str
    values: Mapping[str, float]


def dominates(a: CandidateScore, b: CandidateScore) -> bool:
    """Return True when a is no worse on every objective and better on one."""
    if a.values.keys() != b.values.keys():
        raise ValueError("Candidates must use the same objective dimensions")

    no_worse = all(a.values[key] >= b.values[key] for key in a.values)
    strictly_better = any(a.values[key] > b.values[key] for key in a.values)
    return no_worse and strictly_better


def pareto_front(candidates: list[CandidateScore]) -> list[CandidateScore]:
    """Return all non-dominated candidates, preserving input order."""
    return [
        candidate
        for candidate in candidates
        if not any(
            other.candidate_id != candidate.candidate_id
            and dominates(other, candidate)
            for other in candidates
        )
    ]
```

This code does not choose the artistically best candidate. It only identifies non-dominated candidates under the supplied metrics. It also assumes the metrics are meaningful, normalised, and comparable for the current task.

## 85. Stable independent seed derivation

A seed should be derived from stable operation context, not from the order in which random numbers happen to be requested.

```python
import hashlib
import json


def derive_seed(*parts: object) -> int:
    """Derive a stable 64-bit seed from canonical JSON-compatible values."""
    payload = json.dumps(
        parts,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


project_seed = 20261126
phrase_seed = derive_seed(
    project_seed,
    "motif-generator-v2",
    "composition-001",
    "phrase-018",
    "mutation-003",
)
```

For production, avoid relying on `default=str` for arbitrary objects. Prefer explicit canonical serialisation of a documented set of primitive types. The example illustrates the principle, not a complete cross-language seed standard.

## 86. Bounded candidate-generation loop

```python
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class CandidateResult:
    candidate: Any
    valid: bool
    report: dict[str, Any]


def generate_candidate_set(
    request: Any,
    generate_one: Callable[[Any, int], Any],
    validate: Callable[[Any, Any], CandidateResult],
    seed_for_index: Callable[[Any, int], int],
    candidate_count: int,
) -> list[CandidateResult]:
    if candidate_count < 1:
        raise ValueError("candidate_count must be positive")

    results: list[CandidateResult] = []
    for index in range(candidate_count):
        seed = seed_for_index(request, index)
        proposal = generate_one(request, seed)
        result = validate(proposal, request)
        results.append(result)

    return results
```

The caller should keep invalid results for diagnostics when appropriate, but only valid candidates should proceed to selection. In an interactive application, generation should also support cancellation and a computational budget.

## 87. A task-specific algorithm profile

A generator registry may store capability descriptions rather than a hard-coded global preference order.

Example profile:

```yaml
profile_id: motif_variation.exploratory.v1
problem_class: motif_transformation
input_requirements:
  - source_motif
  - identity_profile
  - mutation_contract
supports:
  deterministic: true
  candidate_sets: true
  lineage: true
  local_scope: true
methods:
  - rule_transformations
  - bounded_stochastic_sampling
selection_requirements:
  - hard_constraint_validation
  - identity_retention_estimate
  - candidate_diversity
limitations:
  - does_not_select_final_artistically_preferred_candidate
```

The profile describes capability and responsibility, not a universal ranking of methods.

## 88. Simple state-transition decision

```python
from dataclasses import dataclass


@dataclass
class DirectorState:
    current: str
    dwell_count: int = 0


def next_state(
    state: DirectorState,
    activity: float,
    enter_threshold: float,
    exit_threshold: float,
    min_dwell: int,
) -> DirectorState:
    """Illustrative hysteresis for a two-state director."""
    if state.current == "steady":
        if activity >= enter_threshold:
            return DirectorState("intensified", dwell_count=0)
        return DirectorState("steady", state.dwell_count + 1)

    if state.current == "intensified":
        if state.dwell_count < min_dwell:
            return DirectorState("intensified", state.dwell_count + 1)
        if activity <= exit_threshold:
            return DirectorState("steady", dwell_count=0)
        return DirectorState("intensified", state.dwell_count + 1)

    raise ValueError(f"Unknown director state: {state.current}")
```

A production director will require more than two states, explicit musical transition conditions, and a distinction between a measured activity estimate and a desired compositional trajectory. The example illustrates hysteresis and minimum dwell behaviour only.

---

# Part XVII — Testing and acceptance criteria

## 89. Test the intelligence layer independently

Testing should not require a complete audio render for every algorithmic change. Use layered tests.

### Unit tests

- distribution behaviour;
- transformation operators;
- candidate sorting;
- constraint evaluation;
- stable seed derivation;
- state transitions;
- Pareto dominance;
- mutation-budget enforcement.

### Property-based tests

- frozen material remains unchanged;
- deterministic mode reproduces the same candidate under a fixed environment and version;
- independent random streams do not affect each other;
- candidates never commit automatically;
- invalid candidates cannot be selected as valid;
- all generated events remain within permitted time and pitch domains;
- mutation deltas remain inside the declared scope;
- candidate lineage points to valid source entities.

### Integration tests

- planner output is consumable by generators;
- generator output conforms to ontology schemas;
- validation reports reach the selector;
- selector output can be committed through the transaction manager;
- user rejection does not modify accepted project state;
- a new project revision invalidates stale candidate commits.

### Listening tests

- compare the generated candidates in musical context;
- evaluate whether transformations preserve intended identity;
- check whether section-level behaviour fulfils its plan;
- test for metric exploitation;
- assess whether semantic controls produce understandable consequences.

## 90. Golden compositions and benchmark sets

Maintain reference projects representing different musical problems, not only different genre labels.

Examples:

- a composition centred on one motif family;
- a track with independent polymetric layers;
- a form driven by subtractive development;
- a composition with gradual timbral transformation;
- a fragmented, discontinuous structure;
- a sparse composition where silence is structurally important;
- a high-density composition with clear figure-ground organisation;
- a composition with strict frozen regions and local regeneration;
- a project requiring deterministic reconstruction;
- a project with conflicting constraints for failure-path testing.

Each benchmark should define what is being tested, not prescribe one correct artistic output.

## 91. Evaluation protocol

A benchmark report should specify:

- software and algorithm versions;
- brief and constraints;
- seed policy;
- candidate-generation budget;
- objective metrics and definitions;
- human evaluation protocol;
- known confounders;
- failure cases;
- reproducibility status.

Do not compare algorithms using different candidate budgets or different input constraints without making those differences explicit.

## 92. Definition of done for a new generative feature

A new generator or decision feature is not complete merely because it produces output.

It is complete when:

- its musical problem and scope are documented;
- it consumes canonical ontology objects;
- it declares its decision owner and permissions;
- its hard constraints and mutation rules are explicit;
- it produces typed candidates;
- it does not commit without authority;
- it records algorithm and seed provenance;
- it has deterministic tests where applicable;
- it has failure and no-solution behaviour;
- it can be evaluated in context;
- it preserves protected material;
- its UI controls have clear musical semantics;
- the developer documentation and examples are updated.

---

# Part XVIII — Implementation roadmap

## 93. Stage 0 — Decision vocabulary and contracts

Establish canonical types for generation requests, candidate results, algorithm profiles, evaluation reports, mutation permissions, decision records, and selection policies.

**Exit criteria:** all major subsystems can describe what they request and return without shared informal dictionaries.

## 94. Stage 1 — Deterministic generation core

Implement deterministic transformation operators, independent seed streams, candidate lifecycle, and hard validation.

**Exit criteria:** the system can generate, validate, compare, and reproduce a small candidate set without mutating the project.

## 95. Stage 2 — Constraint and relationship-aware generation

Add shared context, dependency inspection, constraint validation, and cross-voice relationships.

**Exit criteria:** a generator can produce material that responds to existing composition entities and reports why candidates fail.

## 96. Stage 3 — Hierarchical planning

Implement brief interpretation, global planning, section/phrase plans, completion conditions, and controlled replanning.

**Exit criteria:** a composition task can be decomposed into explicit plans consumed by lower-level generators.

## 97. Stage 4 — Candidate selection and multi-objective evaluation

Implement evaluation profiles, candidate diversity, Pareto filtering, ranking policies, and human selection.

**Exit criteria:** the system can present a useful shortlist and explain trade-offs without pretending that one metric decides artistic quality.

## 98. Stage 5 — Mutation and transactional revision

Implement mutation contracts, scope protection, dependency impact reports, atomic commit, undo, and local regeneration.

**Exit criteria:** a user can regenerate one region without changing unrelated accepted material.

## 99. Stage 6 — Stateful composition director

Implement explicit structural states, transition conditions, memory, hysteresis, and termination logic.

**Exit criteria:** the system can manage a bounded long-form generation task and finish or report why it cannot finish.

## 100. Stage 7 — Hybrid and learned methods

Integrate retrieval, learned model proposals, evolutionary search, agent collaboration, or other methods only where they solve a documented problem.

**Exit criteria:** each method obeys the same contracts, validation, provenance, and candidate lifecycle as native generators.

## 101. Stage 8 — Evaluation laboratory

Build benchmark compositions, human listening protocols, regression reports, and metric calibration procedures.

**Exit criteria:** changes to generation behaviour can be compared across musical, technical, and interaction dimensions.

---

# Appendix A — Algorithm selection matrix

| Musical task | Strong candidate methods | Important safeguards |
|---|---|---|
| Exact transformation of a motif | Rule-based operators | Explicit identity dimensions and mutation contract |
| Local event variation | Stochastic sampling, rules | Bounded distributions and seed isolation |
| Phrase expansion | Grammar, search, learned continuation | Phrase function and source lineage |
| Multi-voice coordination | Constraint programming, joint search | Cross-voice validation and perceptual review |
| Long-form structure | Hierarchical planning, grammar, state machines, learned proposals | Completion criteria and material memory |
| Alternative orchestration | Candidate search, evolutionary methods, rules | Role constraints and perceptual evaluation |
| Texture evolution | Dynamical systems, stochastic processes | Bounded state, reset behaviour, musical mapping |
| Retrieval of related material | Embeddings, feature search, case-based reasoning | Provenance and contextual adaptation |
| Natural-language control | Intent interpreter, LLM or classifier | Typed interpretation, clarification, explicit scope |
| Audio transformation | Signal-processing and learned audio models | Render validation and source provenance |
| Candidate selection | Pareto analysis, pairwise preference, task-specific rankers | No universal single score |
| Local regeneration | Context-aware generation and transactional mutation | Scope locks and dependent-object analysis |

No row mandates one algorithm. The table identifies methods worth evaluating for each class of problem.

---

# Appendix B — Algorithm specification template

Every substantial algorithm should be documented with this template.

```yaml
algorithm_id: example.motif_variation.v1
name: Example Motif Variation
problem_class: motif_transformation
purpose: >-
  Generate related motif candidates while preserving the selected
  identity dimensions.

inputs:
  required:
    - source_motif
    - identity_profile
    - mutation_contract
    - musical_context
  optional:
    - reference_material
    - user_preferences

outputs:
  - candidate_set
  - provenance_record
  - validation_context

method:
  family: hybrid
  components:
    - deterministic_transformations
    - bounded_stochastic_sampling

constraints:
  hard:
    - preserve_frozen_dimensions
    - obey_mutation_scope
  soft:
    - maintain_recognisable_identity
    - avoid_duplicate_candidates

randomness:
  deterministic_supported: true
  stream_scope: target_entity_and_operation

selection:
  owned_by: candidate_selector
  algorithm_may_commit: false

evaluation:
  required:
    - schema_validity
    - mutation_compliance
    - identity_retention
    - candidate_diversity

failure_modes:
  - no_feasible_candidate
  - insufficient_variation
  - excessive_identity_loss

limitations:
  - identity_is_context_dependent

version: 1.0.0
```

---

# Appendix C — Candidate comparison record template

| Field | Description |
|---|---|
| Task | What was requested? |
| Scope | Which entity or region was eligible to change? |
| Context | Which composition state and dependencies were used? |
| Candidate | Stable candidate identity |
| Preserved | Properties guaranteed unchanged |
| Changed | Properties intentionally transformed |
| Constraints | Hard and soft requirements applied |
| Evidence | Validation and evaluation results |
| Trade-offs | Benefits and costs of the candidate |
| Uncertainty | What could not be assessed reliably? |
| Provenance | Algorithm, version, seed, and source material |
| Status | Proposed, selected, rejected, or committed |

---

# Appendix D — Developer review checklist

## D1. Task definition

- Is the musical problem explicit?
- Is the target level clear?
- Is the decision owner defined?
- Are inputs and outputs typed?
- Is the expected timescale clear?

## D2. Algorithm choice

- Does the method fit the problem?
- Is a simpler method sufficient?
- Does it require training data or external services?
- Does it have known failure modes?
- Can it produce diverse candidates?
- Can it operate within the required budget?

## D3. Constraints and identity

- Are hard constraints distinct from preferences?
- Is the mutation scope explicit?
- Are protected and frozen objects honoured?
- Is lineage preserved?
- Are dependencies inspected?

## D4. Randomness and reproducibility

- Are random streams isolated?
- Is seed derivation stable?
- Is algorithm version recorded?
- Are nondeterministic dependencies declared?
- Can a prior decision be inspected and, where supported, reproduced?

## D5. Evaluation and selection

- Are validation and musical evaluation separate?
- Are metrics appropriate to the task?
- Is diversity considered?
- Are trade-offs visible?
- Can the system request human judgement?
- Are no-solution and uncertainty states handled?

## D6. Project integrity

- Are candidates separate from committed material?
- Is commit transactional?
- Can the operation be undone?
- Are unrelated regions protected?
- Are stale revisions rejected?

## D7. User experience

- Does the control have a clear musical meaning?
- Can the user inspect the affected scope?
- Are alternatives understandable?
- Can the user accept, reject, freeze, or revise?
- Does the system explain its actions without overstating certainty?

---

# Appendix E — Glossary

**Algorithm profile:** A versioned description of an algorithm's purpose, capabilities, inputs, outputs, constraints, and limitations.

**Candidate:** A proposed musical object or change that has not necessarily been accepted or committed.

**Candidate set:** A collection of alternatives generated for one task under comparable context and constraints.

**Commit:** The authorised transactional integration of a candidate or change into the composition.

**Composition director:** A high-level stateful component that manages long-range goals and requests lower-level actions.

**Constraint:** A condition that restricts possible outputs; its hard/soft status must be explicit.

**Decision owner:** The component or person authorised to make a particular class of decision.

**Evaluation profile:** A task-specific selection of measurements, rules, and human review questions.

**Generation request:** A typed specification of what material or decision is being requested, with scope, context, constraints, and budget.

**Hierarchical generation:** Generation in which higher-level plans constrain and coordinate lower-level decisions.

**Mutation budget:** A bound on the amount or type of change allowed in an operation.

**Mutation contract:** A formal declaration of what an operation may alter and what it must preserve.

**Pareto set:** The set of candidates not dominated by another candidate across the selected objectives.

**Provenance:** The record of where material or a decision came from and how it was produced or transformed.

**Replanning:** Revising a plan in response to new constraints, accepted edits, or evidence that the prior plan is infeasible or unsuitable.

**Seed isolation:** The use of independent random streams so one subsystem's random draws do not unexpectedly affect another.

**Selection policy:** The declared method by which candidates are ranked, filtered, or presented for human choice.

**Uncertainty:** A representation of what the system does not know reliably, distinct from random variation.

---

# References and further reading

The following works provide foundations and current research context. They are references for study, not claims that any particular paper supplies a complete architecture for this instrument.

## Algorithmic composition and computational creativity

1. Papadopoulos, G., & Wiggins, G. (1999). **AI Methods for Algorithmic Composition: A Survey, a Critical View and Future Prospects.** Proceedings of the AISB'99 Symposium on Musical Creativity, pp. 110–117. [Research record and access links](https://researchportal.vub.be/en/publications/ai-methods-for-algorithmic-composition-a-survey-a-critical-view-a/).
2. Carnovalini, F., & Rodà, A. (2021). **Computational Creativity and Music Generation Systems: An Introduction to the State of the Art.** *Frontiers in Artificial Intelligence*, 3, 14. [https://doi.org/10.3389/frai.2020.00014](https://doi.org/10.3389/frai.2020.00014).
3. Agres, K., Forth, J., & Wiggins, G. A. (2016). **Evaluation of Musical Creativity and Musical Metacreation Systems.** *Computers in Entertainment*, 14(3). [https://doi.org/10.1145/2967506](https://doi.org/10.1145/2967506).
4. Xenakis, I. (1992 edition). **Formalized Music: Thought and Mathematics in Composition.** Pendragon Press. [Publisher information](https://www.pendragonpress.com/).
5. Cope, D. (2001). **Virtual Music: Computer Synthesis of Musical Style.** MIT Press. [MIT Press](https://mitpress.mit.edu/).

## Current music-generation research and evaluation

6. Duan, W., Yu, Y., & Briot, J.-P. (2026). **Recent Advances in Music Generation: Methods, Evaluation, and Challenges.** *Artificial Intelligence Review*, 59, 195. [https://doi.org/10.1007/s10462-026-11582-x](https://doi.org/10.1007/s10462-026-11582-x). This review surveys symbolic, audio, and multimodal generation, including statistical and neural approaches, evaluation, controllability, consistency, and long-term structure.
7. Lerch, A., Arthur, C., Bryan-Kinns, N., Ford, C., Sun, Q., & Vinay, A. (2025). **Survey on the Evaluation of Generative Models in Music.** *ACM Computing Surveys*. [https://doi.org/10.1145/3769106](https://doi.org/10.1145/3769106). Covers subjective and objective methods from musicological, engineering, and HCI perspectives.
8. Solak, A., Grötschla, F., Lanzendörfer, L. A., & Wattenhofer, R. (2025). **Benchmarking Music Generation Models and Metrics via Human Preference Studies.** ICASSP 2025. [https://doi.org/10.1109/ICASSP49660.2025.10887745](https://doi.org/10.1109/ICASSP49660.2025.10887745).
9. Kader, F. B., & Karmaker, S. (2025). **A Survey on Evaluation Metrics for Music Generation.** [arXiv:2509.00051](https://arxiv.org/abs/2509.00051).

## Constraint-based and computational methods

10. Anders, T., & Miranda, E. R. (2011). **Constraint Programming Systems for Modeling Music Theories and Composition.** *ACM Computing Surveys*. [https://doi.org/10.1145/1978802.1978809](https://doi.org/10.1145/1978802.1978809).
11. Herremans, D., Chuan, C.-H., & Chew, E. (2017). **A Functional Taxonomy of Music Generation Systems.** *ACM Computing Surveys*, 50(5). [Author publication record](https://dorienherremans.com/biblio?f%5Bauthor%5D=17&o=asc&s=year).
12. Herremans, D., & Chew, E. (2017). **MorpheuS: Generating Structured Music with Constrained Patterns and Tension.** *IEEE Transactions on Affective Computing*. [Author publication record](https://dorienherremans.com/biblio?f%5Bauthor%5D=12&f%5Btg%5D=M&o=desc&s=year).
13. Russell, S., & Norvig, P. **Artificial Intelligence: A Modern Approach.** Pearson. A broad reference for search, planning, constraint satisfaction, and agent architectures.
14. Mitchell, M. (1998). **An Introduction to Genetic Algorithms.** MIT Press. [MIT Press](https://mitpress.mit.edu/).
15. Holland, J. H. (1992). **Adaptation in Natural and Artificial Systems.** MIT Press edition. [MIT Press](https://mitpress.mit.edu/).
16. Sutton, R. S., & Barto, A. G. (2018). **Reinforcement Learning: An Introduction** (2nd ed.). [Open text](http://incompleteideas.net/book/the-book-2nd.html).

## Music cognition, structure, and perception

17. Lerdahl, F., & Jackendoff, R. (1983). **A Generative Theory of Tonal Music.** MIT Press. [MIT Press](https://mitpress.mit.edu/).
18. Temperley, D. (2007). **Music and Probability.** MIT Press. [MIT Press](https://mitpress.mit.edu/).
19. Huron, D. (2006). **Sweet Anticipation: Music and the Psychology of Expectation.** MIT Press. [MIT Press](https://mitpress.mit.edu/).

## Implementation note

Research literature changes quickly. Before selecting a specific model, solver, or evaluation metric for production use, review its latest documentation, licence, computational requirements, and limitations. The architectural contracts in this manual are intended to remain independent of those implementation choices.

---

# Final declaration

The purpose of generative intelligence is not to remove uncertainty from composition. It is to make uncertainty useful, bounded where necessary, and creatively available where appropriate.

The instrument should be capable of making proposals that a composer did not anticipate. It should also be capable of explaining the scope and consequences of those proposals, preserving successful material, recognising when its own methods have failed, and allowing the human author to decide what becomes part of the work.

No algorithm is inherently compositional. No probability distribution is inherently creative. No neural model is automatically intelligent in the musical sense. No evaluation metric can fully replace listening. Their value comes from the musical problems they solve, the relationships they preserve, and the decisions they enable.

The governing cycle is therefore:

**Interpret → Plan → Generate → Validate → Evaluate → Compare → Select → Commit → Learn from the result.**

The system becomes a compositional instrument when this cycle is coherent, inspectable, reproducible where promised, and always accountable to the identity of the composition.
