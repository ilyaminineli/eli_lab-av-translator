# Perceptual Orchestration, Attention & Musical Scene Architecture

## A Developer's Manual for Listener-Centred Musical Organisation in the IDM Generative Instrument

**Documentation family:** IDM Generative Instrument  
**Volume:** Perceptual architecture  
**Status:** Reference manual / proposed implementation specification  
**Version:** 1.0  
**Audience:** Music software architects, algorithmic-composition researchers, DSP engineers, composers, producers, interaction designers, and evaluators of generative music systems

---

## Abstract

A composition can be structurally coherent, rhythmically sophisticated, harmonically plausible, and technically well rendered while still failing as a perceptual experience. Its parts may compete for attention, fuse when they should remain distinct, separate when they should form one object, obscure important gestures, or maintain the same foreground/background relationship for so long that the listener stops noticing the composition's development.

This manual defines a listener-centred architecture for **perceptual orchestration**: the organisation of sound objects, streams, layers, and events so that their relationships are understandable, deliberately ambiguous, richly blended, sharply contrasted, or otherwise perceptually consequential.

It treats a musical scene as more than a mixer snapshot. A scene is a time-dependent perceptual hypothesis about what the listener may hear as objects, streams, figures, backgrounds, groups, spaces, and changing attentional targets. The software cannot know exactly what every listener will perceive. It can, however, represent perceptual intentions, estimate relevant acoustic conditions, detect likely conflicts, generate alternatives, and expose uncertain predictions for human judgement.

The manual develops:

- a vocabulary for auditory objects, streams, groups, figures, backgrounds, and scene states;
- the main acoustic and cognitive cues that support fusion, segregation, continuity, and attention;
- a multidimensional model of salience, density, masking, contrast, and perceptual load;
- attention trajectories across events, phrases, sections, and whole compositions;
- orchestration strategies for clarity, fusion, ambiguity, foreground exchange, and controlled overload;
- computational feature models and the limits of proxy metrics;
- data structures, APIs, algorithms, decision procedures, and subsystem contracts;
- listening tests, diagnostic reports, regression cases, and acceptance criteria.

The central principle is simple:

> **A generative instrument must orchestrate not only which sounds exist, but also the relationships through which a listener may organise, notice, ignore, connect, separate, remember, and reinterpret those sounds.**

This is not a claim that software can reproduce human hearing in full. It is a practical architecture for making perceptual consequences explicit parts of compositional reasoning.

---

# How to Use This Manual

## 1. Scope

This volume focuses on the perceptual organisation of simultaneous and successive musical material. It is concerned with the questions:

- Which elements should be heard as one sound object?
- Which should be perceived as independent sources or streams?
- Which should attract attention, and when?
- Which should remain background, support, or latent material?
- How much activity can coexist before relationships become difficult to follow?
- How can the scene change focus without losing continuity?
- How should the system represent uncertainty about listener perception?
- How can perceptual objectives influence composition, orchestration, sound realisation, and evaluation?

It does **not** attempt to replace the Composition Atlas, Sound Design Manual, Musical Ontology, Generative Intelligence manual, or Constitution. It specifies the perceptual layer that connects them.

## 2. Relationship to the other volumes

| Existing volume | Responsibility | Contribution to this manual |
|---|---|---|
| IDM Field Guide | Broad musical, historical, mathematical, and production foundation | Context for experimental electronic listening and production |
| Advanced Composition & Generation Appendix | Extended composition and generative methods | Concepts for development, form, perception, and algorithmic design |
| Composition Atlas | Patterns, phrases, motifs, and track structures | Musical material and formal events whose perception is orchestrated |
| Sound Design Manual | Synthesis, effects, timbre, and hybrid sound structures | Acoustic properties used as grouping, contrast, and salience cues |
| Philosophy & Design Constitution | Governing values, hierarchy, mutation, agency, and invariants | Authority for intent, preservation, and human control |
| Musical Ontology & Data Architecture | Canonical entities, graph relationships, time, provenance, and schemas | Canonical representation for perceptual objects and plans |
| Generative Intelligence | Planning, candidate generation, selection, uncertainty, and decision-making | Algorithms that propose, test, and revise perceptual arrangements |

This volume introduces new perceptual entities and interfaces, but they must reference the canonical identifiers and relationships defined by the ontology manual. They must not create a parallel note, motif, phrase, instrument, or section model.

## 3. Normative language

The words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** express implementation requirements.

- **MUST / MUST NOT:** required for architectural or data integrity.
- **SHOULD / SHOULD NOT:** strong recommendation; deviations require a documented reason.
- **MAY:** optional capability.
- **Perceptual estimate:** a computational approximation, not a fact about every listener.
- **Observed result:** a result obtained from an explicitly described listening test or measurement.
- **Artistic intention:** what the composer wants the scene to do, regardless of whether a heuristic predicts it.

## 4. The non-negotiable epistemic rule

The software MUST distinguish:

1. **Acoustic description** — measurable properties of the audio or planned signals.
2. **Perceptual hypothesis** — a prediction about how a listener may organise or attend to those signals.
3. **Compositional intention** — what the composer wants the listener to experience.
4. **Human evaluation** — what particular listeners report or demonstrate under stated listening conditions.

These categories are related but not interchangeable. A spectral-centroid value is not brightness as experienced by every listener. A masking-risk estimate is not proof that a part is inaudible. A high salience score is not proof that an element will capture attention. Every perceptual metric MUST declare which category it belongs to and what it can legitimately support.

---

# Part I — The Perceptual Philosophy

## 1. A mix is not a scene

A mix is a technical combination of signals. A musical scene is a listener's organised interpretation of a changing acoustic field.

A project may contain 24 tracks. A listener may hear:

- one fused metallic instrument assembled from several layers;
- a foreground percussion stream;
- a bass line and kick as one coupled rhythmic object;
- a diffuse noise bed;
- a distant periodic click pattern;
- one transient that briefly captures attention;
- several sounds whose sources remain intentionally ambiguous.

Track count is therefore not a reliable measure of perceived object count, musical density, or attentional complexity.

The perceptual architecture must be able to reason about **many technical sources becoming one perceptual object**, and **one technical source becoming multiple perceived streams**.

## 2. Perceptual orchestration as a compositional discipline

Traditional orchestration often asks which instrument plays which line, in which register, with which dynamic and articulation. Perceptual orchestration extends this question:

- What should the listener group together?
- What should the listener separate?
- What should be noticed first?
- What should be discoverable only after repeated listening?
- Which relationships should be obvious, and which should remain unstable?
- How should the listener's focus move through the work?

In experimental electronic music, these decisions are particularly important because the composer can construct sources whose timbres, envelopes, spatial behaviours, and temporal patterns have no fixed acoustic identity. A sound may behave as percussion in one passage, a melodic stream in another, and an atmospheric component later.

## 3. Three simultaneous perspectives

The system SHOULD maintain three complementary views.

### 3.1 Composer's scene

The intended organisation: declared roles, intended foreground, desired blending, attention trajectory, narrative function, and deliberate ambiguity.

### 3.2 Signal scene

The technically measurable signal relationships: timing, spectrum, loudness, modulation, spatialisation, transient structure, dynamics, and routing.

### 3.3 Listener scene hypothesis

An estimate of likely grouping, segregation, prominence, masking, continuity, and attention. It should represent confidence and uncertainty rather than asserting a single universal percept.

A scene is well designed when these views are meaningfully aligned—or when their divergence is deliberate.

## 4. Clarity is not the universal objective

The instrument MUST NOT interpret perceptual clarity as the requirement that every sound be separately identifiable.

A composition may intentionally seek:

- fusion: several components heard as one composite object;
- segregation: multiple clearly independent streams;
- ambiguity: unstable interpretation between one object and several;
- occlusion: an element partially hidden by another;
- emergence: a background feature becoming foreground;
- disappearance: a previously important element losing perceptual priority;
- saturation: the listener encountering a dense, partly unresolved field;
- perceptual reclassification: a familiar sound being heard in a new role.

Clarity, ambiguity, and overload are compositional modes. None is automatically superior.

## 5. The listener is not a fixed reference microphone

Perception varies with hearing ability, listening level, playback system, room, attention, familiarity, fatigue, cultural learning, and listening task. A robust system SHOULD model a range of plausible listening contexts and SHOULD avoid claims such as “this element will definitely be heard”.

A useful target is not perfect prediction. It is **transparent, controllable management of perceptual risk and intention**.

---

# Part II — Canonical Perceptual Concepts

## 6. Sound object

A **sound object** is a perceptual unit that may be heard as one event or source, whether it is generated by one technical source or several.

Examples:

- one FM metallic hit;
- a kick layered from a sine body, noise click, and sampled transient;
- a granular cloud perceived as one moving texture;
- a resonant tail perceived as part of a struck object;
- several synchronized sounds fused into a composite instrument.

A sound object is not synonymous with an ontology `Instrument`, `Track`, or `Event`. It references those entities but has its own identity as a perceptual hypothesis.

## 7. Auditory stream

An **auditory stream** is a sequence of events perceived as belonging together over time. A stream may correspond to a melody, a repeated click sequence, an evolving noise layer, a bass line, or a timbrally coherent series of fragments.

A stream is a temporal perceptual grouping. It may cross phrase, section, track, or instrument boundaries.

## 8. Perceptual group

A **perceptual group** is a set of objects, events, or streams treated as a related unit. Grouping may be strong, weak, temporary, nested, or ambiguous.

Examples:

- kick and bass grouped by rhythmic synchrony;
- several partials grouped as one inharmonic metallic object;
- a family of glitches grouped by shared timbre;
- a foreground motif and its delayed response grouped as a call-and-response unit.

## 9. Figure and ground

- **Figure:** the element or group that currently occupies perceptual foreground.
- **Ground:** the supporting or contextual field against which the figure is heard.

Figure and ground are relational, not permanent instrument labels. A pad can become a figure. A lead can become background. A texture may be both ground and the source of a newly emerging figure.

## 10. Foreground, middle ground, background, and latent layer

A useful working classification is:

| Scene plane | Typical behaviour | Not a fixed rule |
|---|---|---|
| Foreground | High attention priority, distinct gestures, strong identity | May be quiet, sparse, or spatially distant |
| Middle ground | Supports, answers, contextualises, or connects foreground material | Can temporarily become foreground |
| Background | Establishes environment, continuity, harmonic or spectral context | Can contain important long-range information |
| Latent layer | Low-level or intermittent detail that may become noticeable under changed context | Should not automatically be treated as useless or inaudible |

A plane is an intended function. It is not equivalent to a fader position.

## 11. Salience and attention

**Salience** is the degree to which an element differs from its context along one or more dimensions. **Attention** is the selection or allocation of processing toward some part of the scene. Salience can attract attention, but attention also depends on expectation, task, memory, learned structure, and deliberate listening.

The system MUST NOT collapse salience, loudness, and attention into one number.

## 12. Scene state and attention trajectory

A **scene state** is a time-bounded description of the intended and predicted perceptual organisation.

An **attention trajectory** describes how the composition intends to guide, redirect, distribute, or release attention over time.

The trajectory may be:

- focused: one strong figure;
- distributed: several co-equal figures;
- alternating: attention passes between objects;
- layered: figure changes while background remains stable;
- diffuse: no single stable foreground;
- emergent: an object gradually becomes prominent;
- interrupted: attention is captured by a sudden event;
- withdrawn: focal material is removed or weakened.

---

# Part III — Auditory Grouping and Scene Formation

## 13. Why grouping matters

The auditory system does not simply register a list of independent frequencies or tracks. It organises acoustic information into events and streams. Research on auditory scene analysis identifies cues such as harmonicity, onset synchrony, parallel frequency or intensity change, and spatial position as factors in grouping and segregation. Music perception also involves learned schemas and listener-specific differences [1][2].

For a generative instrument, these findings imply that the same collection of notes and samples can be orchestrated to sound fused, separate, or ambiguously related by changing their acoustic and temporal relationships.

## 14. Concurrent grouping: components heard together

Concurrent grouping concerns which simultaneous spectral and temporal components are heard as one event or object.

### 14.1 Harmonicity

Components with frequency relationships consistent with a common fundamental tend to fuse more readily than unrelated components. This is a powerful sound-object construction cue.

**Compositional uses:**

- build a composite tone from several oscillators;
- fuse a transient click with a pitched resonant body;
- create a stable instrument identity from partials distributed across synthesis layers;
- intentionally fracture a sound by detuning or introducing inharmonic components.

**Software implication:** represent `harmonicity_relation` as a graded cue, not a binary truth. Inharmonic objects can still fuse through common onset, shared modulation, envelope similarity, or learned context.

### 14.2 Common onset and onset synchrony

Components beginning near one another in time can be grouped as one event. Synchronised attacks can make separately rendered layers behave as a composite hit.

**Compositional uses:**

- align a noise click, tonal body, and resonant tail to create a single drum object;
- synchronise several spectral bands to create an impact;
- offset one layer slightly to expose internal articulation or create a double-hit impression;
- use a common onset followed by divergent decay to create a source that seems to split open.

The architecture SHOULD represent onset alignment as a measured relation with a tolerance and confidence, not a universal fixed threshold.

### 14.3 Common fate and co-modulation

Components changing together in frequency, amplitude, or another dimension can be heard as belonging together. Shared modulation may bind an otherwise complex sound; independent modulation may separate its components.

**Compositional uses:**

- route several layers through one slow amplitude envelope to fuse them;
- give only one band an independent tremolo to make it emerge;
- move the spectral centroid of several components together;
- gradually diverge modulation rates to transform one object into several streams.

### 14.4 Spatial coherence

Components with similar apparent spatial origins or movement can be grouped. Contrasting spatial positions can support segregation.

This does not mean that panning alone reliably separates sources. Spectral overlap, room acoustics, headphones, loudspeakers, and playback conditions alter the effect.

### 14.5 Shared envelope and timbral coherence

Similar attacks, decays, spectral envelopes, and articulation can encourage grouping. Similarity is multidimensional: two sounds can share pitch but differ in envelope; share envelope but differ in timbre; or share a common modulation pattern while occupying different registers.

### 14.6 Concurrent grouping as a design matrix

| Desired result | Useful cues | Potential counter-cues |
|---|---|---|
| One composite sound | Common onset, harmonic or coherent spectrum, shared envelope/modulation | Large onset offset, independent motion, contrasting spatial placement |
| Two distinct simultaneous sounds | Different attacks, register, timbre, modulation, or spatial image | Strong synchrony and similar spectra may fuse them |
| One object with internal complexity | Common event envelope plus differentiated internal components | Excessive independence can split the object |
| Ambiguous fusion | Competing grouping cues | Do not force every cue toward the same interpretation |

## 15. Sequential grouping: events heard as a stream

Sequential grouping determines which events over time are perceived as belonging together.

### 15.1 Pitch and frequency proximity

Events in a similar register or with a plausible pitch trajectory may form one stream. Large leaps, alternating registers, or rapid switching can encourage stream segregation, depending on tempo and other cues.

### 15.2 Timbre similarity

Repeated events with similar timbral characteristics tend to be heard as one stream. A pattern can therefore remain recognisable even when its notes change, as long as its timbral identity stays coherent.

### 15.3 Rhythmic continuity

Regular timing, recurring accent patterns, and predictable inter-onset relationships can support stream continuity. Deliberate interruptions can either break a stream or be heard as omissions within a continuing pattern.

### 15.4 Spatial continuity

A sequence that maintains a stable apparent location may be heard as one stream. Spatial jumps can divide or reframe it.

### 15.5 Good continuation and closure

Listeners may maintain a sense of continuity through brief interruptions or masking. This offers compositional possibilities: a motif can disappear behind another event and remain perceptually implied, or a repeated sound can create the sense of an interrupted but continuous process.

The software SHOULD distinguish an actual absence of material from a perceived gap inside a continuing stream.

## 16. Segmental grouping and phrase-scale perception

At larger time scales, listeners organise events into gestures, phrases, sections, and returns. Segment boundaries may be supported by changes in texture, register, density, timbre, dynamics, rhythm, or spatial scene.

A new section does not require every property to change. A single well-chosen change can be enough to reorient the listener, while preserving other dimensions maintains continuity.

## 17. Grouping cues can conflict

The system SHOULD model grouping as evidence that can support competing interpretations.

Example:

- two parts begin together (supports fusion);
- their registers differ greatly (may support separation);
- their modulation is shared (supports fusion);
- their spatial positions diverge (supports separation);
- they repeat in a common rhythmic pattern (supports grouping).

The result may be one composite object, two related streams, or unstable ambiguity. The architecture SHOULD allow all three as intentional outcomes.

## 18. Grouping graph

Represent perceptual relations as edges between canonical ontology entities.

Suggested relation types:

- `fuses_with`
- `segregates_from`
- `shares_onset_with`
- `shares_modulation_with`
- `shares_pitch_trajectory_with`
- `shares_rhythmic_identity_with`
- `spatially_coherent_with`
- `contrasts_with`
- `continues_after`
- `masks_partially`
- `emerges_from`
- `reinterprets_as`

Each edge SHOULD include:

- cue type;
- strength estimate;
- confidence;
- time interval;
- source of evidence (measured, planned, inferred, user-authored);
- intended interpretation if explicitly specified;
- model version.

A grouping edge is not a permanent property of two tracks. It may change across the composition.

---

# Part IV — Figure, Ground, and Role Dynamics

## 19. Musical role versus perceptual role

The ontology distinguishes a musical `Role` from a perceived scene position.

A musical role answers: *What function does this material serve in the composition?*  
A perceptual role answers: *How should this material be heard at this moment?*

Examples:

| Musical role | Possible perceptual role |
|---|---|
| Bass foundation | Foreground, middle ground, or fused support with kick |
| Rhythmic ornament | Foreground punctuation or latent detail |
| Harmonic bed | Background, diffuse field, or emerging figure |
| Motif carrier | Foreground stream or distributed ensemble figure |
| Transition texture | Background continuity or dominant interruption |
| Noise layer | Ground, masking veil, or primary figure |

The same musical role can change perceptual function without changing its fundamental identity.

## 20. Foreground is not equivalent to loudness

Foreground prominence may be produced by:

- level contrast;
- transient sharpness;
- spectral contrast;
- pitch/register separation;
- rhythmic isolation;
- spatial position;
- timbral novelty;
- phrase position;
- expectation and repetition;
- sudden absence of competing material.

A very quiet click in a sparse passage can become the main figure. A loud broadband wash may remain background if it is continuous and non-differentiated.

The system MUST NOT use track gain as the only control of perceptual hierarchy.

## 21. Foreground/background strategies

### 21.1 Stable figure over changing ground

The foreground motif remains recognisable while the background changes timbre, harmony, spatial motion, or density. The listener gains identity continuity and changing context.

### 21.2 Changing figure over stable ground

A stable pulse, drone, or texture supports successive foreground events. This gives the listener a reference frame for comparing transformations.

### 21.3 Figure-ground reversal

A background element gradually gains contrast, activity, or isolation until it takes over the foreground. The former figure may recede, fragment, or stop.

### 21.4 Distributed foreground

Several parts share prominence. This can create polyphonic, ensemble, or collage-like listening. The system SHOULD assess whether the parts have distinguishable identities and compatible attention demands.

### 21.5 Diffuse foreground

The scene itself is the figure: a sound mass, noise field, dense granular cloud, or unstable texture. No individual source needs to dominate.

### 21.6 Latent-to-salient emergence

A subtle element can become noticeable through repetition, isolation, gradual increase, spectral exposure, or contextual change. A good emergence often begins before the listener recognises its importance.

## 22. Perceptual handoff

A **perceptual handoff** is a planned transfer of focal attention from one object or stream to another.

Possible mechanisms:

1. **Overlap:** the new figure enters before the old one exits.
2. **Call and answer:** a new stream responds to the old one.
3. **Spectral transfer:** energy or activity moves from one region to another.
4. **Rhythmic inheritance:** the new figure preserves a timing feature of the old.
5. **Timbre inheritance:** the new figure retains a recognisable timbral component.
6. **Spatial migration:** apparent location changes while identity remains.
7. **Silence-mediated handoff:** the old figure disappears, exposing a prepared new figure.
8. **Metamorphosis:** both figures are perceived as successive states of one object.

A handoff plan SHOULD specify whether continuity, contrast, or surprise is the primary intention.

## 23. Attention trajectories

Attention should be planned at multiple scales.

| Scale | Typical question |
|---|---|
| Event | Which transient or gesture should be noticed? |
| Beat / local cycle | Which part defines the immediate rhythmic focus? |
| Phrase | What carries the phrase's identity? |
| Section | What is the dominant perceptual proposition? |
| Whole composition | How does attention evolve and return? |

A useful trajectory is not necessarily a smooth curve. IDM and related experimental forms may use sudden cuts, interruptions, long plateaus, abrupt reclassifications, or several competing focal paths.

---

# Part V — Salience, Attention, and Perceptual Priority

## 24. Salience is multidimensional

A system may estimate salience using several dimensions, but it MUST retain the components rather than storing only a single aggregate score.

### 24.1 Acoustic salience candidates

- relative loudness / local level contrast;
- transient strength and onset novelty;
- spectral contrast;
- spectral centroid or brightness proxy;
- pitch or register isolation;
- rhythmic novelty;
- modulation contrast;
- timbral novelty;
- spatial contrast or movement;
- duration and continuity;
- local sparsity around the event.

### 24.2 Contextual salience candidates

- deviation from established patterns;
- return of a remembered motif;
- fulfillment or violation of a formal expectation;
- phrase position;
- role declared in the composition brief;
- current attention target;
- prior exposure and familiarity;
- relation to a recently interrupted stream.

### 24.3 Task and listener dependence

A listener asked to follow the bass may attend differently from a listener asked to identify high-frequency events. A listener familiar with a motif may notice its transformation earlier than a first-time listener. This means an attention model needs a **listening task or profile** when making task-specific predictions.

## 25. Bottom-up and top-down attention

**Bottom-up attention** is driven by signal properties and contrast: sudden onset, change, unusual spectrum, loudness difference, motion, or novelty.

**Top-down attention** is directed by goals, expectations, memory, familiarity, and learned schemas.

A generative instrument SHOULD support both.

Examples:

- a sudden transient may capture attention bottom-up;
- a recurring motif may attract attention top-down;
- a quiet sound may become salient because the composition has prepared the listener to expect it;
- a loud event may be ignored if it is repetitive and predictable.

Research on auditory attention models discusses interactions between sound-object formation, selective attention, and foreground/background organisation [3]. The practical lesson is to avoid a purely amplitude-driven salience model.

## 26. Attention priority versus salience estimate

A composition may intend a sound to be important even if its acoustic salience is low. Conversely, a sound may be accidentally salient because of an uncontrolled transient.

Store separate fields:

- `intended_attention_priority`;
- `estimated_bottom_up_salience`;
- `estimated_top_down_relevance`;
- `predicted_attention_competition`;
- `human_attention_observation` when available.

The generator can then detect conflicts between intention and acoustic realisation.

## 27. Attention budget as a planning metaphor

Attention is not a literal fixed resource that software can measure as a scalar. Nevertheless, an **attention budget** is a useful compositional planning metaphor: too many simultaneous high-priority events may make the intended hierarchy difficult to perceive.

Use it as a constraint or heuristic, not a biological law.

A simple planning rule might be:

- one dominant focus;
- one or two supporting active figures;
- several lower-priority background streams;
- occasional controlled violations.

This is a starting point, not a genre rule. A deliberately crowded passage may be the intended outcome.

## 28. Salience competition

When several events have high salience at the same moment, the system should ask:

- Is this a deliberate polyfocal moment?
- Are the events meant to form one composite event?
- Is one event intended to interrupt the others?
- Are the events sufficiently distinct to be followed separately?
- Does their simultaneity create useful ambiguity?
- Is one event redundant or accidentally dominant?

The answer belongs to the composition brief and local scene plan, not to a universal salience threshold.

---

# Part VI — Density, Masking, and Perceptual Load

## 29. Density is not one quantity

The architecture MUST distinguish at least the following:

| Density dimension | Meaning |
|---|---|
| Event density | Number or rate of discrete events |
| Rhythmic density | Subdivision and activity of rhythmic information |
| Spectral density | Occupancy and overlap across frequency regions |
| Harmonic density | Number and complexity of simultaneous pitch relationships |
| Timbral density | Variety or complexity of timbral components |
| Modulation density | Number and speed of changing parameters |
| Spatial density | Number and distribution of apparent spatial sources |
| Attention density | Number of elements intentionally competing for focus |
| Perceptual density | A human judgement about how crowded or complex the scene feels |

A dense event pattern can be spectrally sparse. A slow drone can be spectrally and modulatorily dense. A composition can have many tracks but a simple perceptual scene.

## 30. Frequency masking and spectral competition

Frequency masking occurs when energy in one region reduces the audibility of nearby frequency components. The effect depends on frequency, level, spectral shape, duration, and listening conditions. Critical-band and auditory-filter models are useful engineering approximations, not exact universal boundaries.

For compositional software:

- use perceptually motivated frequency scales where appropriate (for example ERB or Bark-like representations);
- inspect energy and tonal structure by time window;
- distinguish broadband noise from narrowband tonal content;
- consider level differences and temporal overlap;
- retain source attribution where possible;
- do not infer inaudibility from spectral overlap alone.

### 30.1 Masking risk categories

A practical diagnostic can classify:

- `low`: little apparent conflict under the selected model;
- `moderate`: overlap may reduce clarity under some conditions;
- `high`: strong overlap and limited contrast likely compromise the intended distinction;
- `unknown`: insufficient signal or model support.

These labels indicate review priority, not objective audibility.

### 30.2 Masking can be desirable

Masking is not merely a defect. It can support:

- veiled motifs;
- hidden counter-rhythms;
- partial disappearance;
- fused composite timbres;
- unstable auditory grouping;
- dense sound masses;
- deliberate obscurity.

A masking diagnostic should therefore compare predicted risk against the intended perceptual relationship.

## 31. Temporal masking and transient competition

A strong event can reduce the perception of weaker events immediately before or after it. Transient interactions also affect the clarity of rapid patterns.

For IDM-oriented generation, examine:

- closely spaced kick, snare, and glitch attacks;
- transient clusters across similar spectral bands;
- rapid alternations where one event may obscure another;
- event tails overlapping subsequent attacks;
- transient layers that combine into one attack versus transient layers that should remain separate.

The system SHOULD evaluate local event windows and not only long-term averages.

## 32. Loudness, perceived prominence, and gain structure

RMS, peak level, true peak, and loudness estimates answer different engineering questions. Programme loudness algorithms such as ITU-R BS.1770 provide standardised measurements of programme loudness and true-peak level; they do not describe the complete perceptual salience of a sound object [4]. EBU R 128 provides a broadcast programme-normalisation recommendation, not a universal artistic loudness target for IDM tracks [5].

The generative system SHOULD keep:

- sample peak;
- true peak;
- RMS or energy measures;
- integrated loudness where relevant;
- short-term and momentary loudness where useful;
- local contrast relative to neighbouring events;
- intended scene prominence.

Do not use a broadcast target as a default master target for every music project. Delivery requirements should be selected by platform, medium, and user intent.

## 33. Perceptual load and cognitive complexity

Perceptual load is broader than signal density. It may be influenced by:

- number of independent streams;
- stream similarity and segregation difficulty;
- rate of change;
- novelty and surprise;
- expectation violations;
- memory demands;
- ambiguity of object identity;
- competing rhythmic organisations;
- listening task.

The software MAY calculate a heuristic load estimate, but MUST label it as a project-specific model. It MUST NOT present one universal “listener capacity” as fact.

## 34. Contrast as a way to manage density

Density can be made more manageable without simply reducing the number of events.

Useful contrast dimensions include:

- attack versus sustain;
- periodic versus irregular;
- pitched versus noisy;
- stable versus mobile;
- narrowband versus broadband;
- dry versus reverberant;
- centered versus spatially diffuse;
- repetitive versus episodic;
- continuous versus punctuated;
- foreground versus background.

A dense scene with differentiated roles may remain intelligible. A sparse scene with highly similar overlapping elements may remain confusing.

## 35. Dynamic density planning

A section-level density plan SHOULD describe several dimensions independently.

Example:

| Section | Event | Spectral | Modulation | Attention | Intended experience |
|---|---:|---:|---:|---:|---|
| A | Low | Medium | Low | Focused | Open, exposed |
| B | Medium | Medium | Medium | Focused | Pulse emerges |
| C | High | High | High | Distributed | Controlled overload |
| D | Low | Medium | Medium | Re-focused | A single residue becomes audible |

The profile is descriptive. Values should be normalised within a project or model version, not treated as objective cross-song units.

---

# Part VII — Spatial Scene and Apparent Distance

## 36. Spatialisation is a perceptual relationship, not decoration

Spatial position can support stream segregation, identity, motion, depth, and scene hierarchy. It can also create instability or ambiguity.

A spatial plan should distinguish:

- channel placement;
- apparent source direction;
- width;
- depth;
- distance impression;
- reverberant environment;
- motion trajectory;
- source directivity or spatial character;
- mono compatibility.

## 37. Binaural and loudspeaker cues

Spatial perception can draw on interaural time differences, interaural level differences, spectral cues shaped by the head and outer ears, reverberation, and motion. Their effectiveness depends on playback configuration and listener differences [6].

The system SHOULD distinguish spatial rendering modes:

- stereo balance/panning;
- stereo width processing;
- mid-side design;
- binaural/HRTF rendering;
- multichannel speaker rendering;
- object-based or scene-based spatial audio;
- mono-compatible spatial cues.

These methods are not interchangeable. A stereo pan law is not a full spatial-audio model.

## 38. Apparent distance

A distant impression may be suggested by a combination of:

- lower direct-to-reverberant ratio;
- reduced high-frequency detail;
- lower transient sharpness;
- lower direct level relative to scene context;
- diffuse reflections;
- reduced apparent localisation precision.

These are tendencies, not a recipe that works identically in every mix. Sound design decisions are covered in the Sound Design Manual; this volume specifies their perceptual orchestration role.

## 39. Spatial scene contracts

A spatial plan SHOULD include:

- intended coordinate system and reference frame;
- rendering target (stereo, headphones, multichannel, etc.);
- movement envelope;
- depth intention;
- mono compatibility requirement;
- fallback behaviour when a renderer is unavailable;
- whether spatial cues contribute to object identity or only scene ambience.

## 40. Spatial robustness

A spatial distinction may disappear when summed to mono, played through a single speaker, or reproduced by a different headphone response. Important musical identity SHOULD NOT rely exclusively on fragile spatial cues unless the target format explicitly supports them.

Test:

- mono fold-down;
- left/right channel isolation;
- headphone playback;
- loudspeaker playback;
- narrow stereo playback;
- low-quality or bandwidth-limited reproduction when relevant.

---

# Part VIII — Perceptual Time, Expectation, and Memory

## 41. Local surprise and long-term expectation

Musical expectation is shaped by short-term acoustic context and learned structural knowledge. Computational and cognitive accounts of auditory expectation describe information dynamics and probabilistic prediction in music [7]. More recent work also reports distinguishable contributions of sensory and cognitive expectations to musical expectancy [8].

A generative system can use these ideas without claiming to model the listener's complete cognitive state.

## 42. Expectation as a scene resource

The composition can establish expectations about:

- which stream continues;
- when a recurring event should occur;
- which voice occupies the foreground;
- what follows a particular gesture;
- the return of a timbral object;
- the duration of a texture;
- the spatial position of a source;
- the relationship between a motif and its response.

A violation becomes meaningful when there is an established expectation to violate.

## 43. Repetition builds perceptual identity

Repetition can improve recognition and stream continuity. The system SHOULD represent both exact repetition and family resemblance.

A motif might return with:

- identical rhythm but changed timbre;
- identical timbre but changed register;
- the same onset pattern but different pitch content;
- preserved contour with altered timing;
- preserved spatial identity with changed role;
- only one surviving fragment.

The listener may recognise a transformed object even when its acoustic signal changes substantially. The system should preserve the lineage and intended recognisability level.

## 44. Attention memory

A composition can remember its own scene history. The system SHOULD track:

- recently foregrounded objects;
- objects that have remained background for a long time;
- motifs that disappeared but may return;
- attention targets repeated too frequently;
- scene configurations already used;
- transitions that have been prepared but not resolved;
- recurring spatial or timbral signatures.

This memory supports long-range contrast and prevents the generator from applying the same foreground strategy in every section.

## 45. Perceptual pacing

Pacing is not merely the rate of events. It is the rate at which the listener is asked to update their perceptual model.

A track may change very little at the event level while making a major perceptual shift by gradually separating a fused object into streams. Conversely, many notes may change while the listener hears one stable repeated object.

The generator SHOULD distinguish:

- event change rate;
- material change rate;
- grouping change rate;
- attention change rate;
- scene-state change rate.

---

# Part IX — Scene Architectures and Orchestration Strategies

## 46. A catalogue of perceptual scene types

These are reusable planning models, not prescriptive track forms.

### 46.1 Single focal object

One clearly identifiable sound object dominates. Other elements support or punctuate it.

Useful for: exposed motifs, minimal passages, isolated rhythmic figures.

### 46.2 Stable foreground with diffuse background

A focused stream sits against a continuous field. The background can change slowly without displacing the figure.

Useful for: ambient IDM, repetitive sections, slow timbral evolution.

### 46.3 Multiple independent streams

Several streams remain perceptually distinct through differences in register, timbre, articulation, rhythm, or space.

Useful for: polymetric compositions, counterpoint, interlocking rhythmic systems.

### 46.4 Fused composite instrument

Several sources are designed to form one perceived object.

Useful for: hybrid percussion, spectral instruments, complex synthetic impacts.

### 46.5 Sound mass

Many sources merge into a continuous or evolving perceptual whole.

Useful for: granular clouds, noise orchestration, dense spectral fields.

### 46.6 Call-and-response scene

Attention alternates between distinguishable figures.

Useful for: rhythmic conversations, stereo exchanges, fragmented melodies.

### 46.7 Foreground relay

Several voices inherit a motif or gesture, passing its focal role between them.

Useful for: timbral orchestration, multi-instrument motif development, long-form continuity.

### 46.8 Emergent scene

A previously background or latent element gradually becomes a focal object.

Useful for: long builds, texture-to-rhythm transitions, hidden pulse emergence.

### 46.9 Interrupted scene

A strong event interrupts an established stream or texture.

Useful for: glitch cuts, structural breaks, sudden formal reorientation.

### 46.10 Ambiguous scene

Grouping cues conflict so that the listener may alternate between interpretations.

Useful for: perceptual illusions, unstable sound objects, uncertain source identity.

### 46.11 Layered chronology

A current sound contains fragments or residues of previous scenes, making memory audible.

Useful for: resampling, delayed echoes, transformed motif returns, spectral traces.

### 46.12 Controlled overload

Several high-activity streams coexist intentionally, creating a temporary loss of single-focus hierarchy.

Useful for: climaxes, maximalist passages, dense IDM collages.

## 47. Scene transitions

A transition should be evaluated for what happens to grouping and attention, not only for which parts enter or exit.

| Transition | Perceptual operation |
|---|---|
| Layer addition | New stream joins the scene |
| Layer removal | Existing hierarchy is exposed or reduced |
| Fusion | Several objects become one composite object |
| Fission | One object separates into multiple streams |
| Foreground handoff | Attention moves to another figure |
| Spatial migration | Apparent position changes |
| Spectral migration | Activity moves across frequency regions |
| Rhythmic reclassification | A texture becomes a pulse or vice versa |
| Masking veil | A figure becomes partially obscured |
| Reveal | A previously hidden relation becomes perceptible |
| Scene reset | Most grouping and attention assumptions are replaced |
| Residual continuation | A fragment of the previous scene persists into the new one |

The transition planner SHOULD declare which properties are preserved, transformed, or discarded.

## 48. Attention trajectories by section function

Examples of attention design:

- **Introduction:** establish a scene grammar; allow the listener to identify a source or process.
- **First development:** introduce a second stream or reveal internal complexity.
- **Main statement:** identify the dominant material or relation.
- **Variation:** change one or more grouping cues while preserving identity.
- **Breakdown:** withdraw a figure, leaving a trace or ground.
- **Climax:** concentrate, distribute, or deliberately overload attention.
- **Outro:** allow the scene to dissolve, narrow, or reclassify its remaining objects.

The system MUST NOT assume that every composition needs all these functions or that attention must always intensify toward a climax.

---

# Part X — Perceptual Feature Analysis and Computational Proxies

## 49. Analysis pipeline

A practical analysis pipeline can use the following stages:

1. Decode audio or render candidate stems.
2. Align all signals to a shared timeline.
3. Compute frame-based and event-based features.
4. Estimate source/voice activity where possible.
5. Build spectral, temporal, and spatial descriptors.
6. Relate descriptors to known musical entities.
7. Estimate grouping and conflict hypotheses.
8. Compare estimates to intended scene plans.
9. Produce diagnostics and alternative suggestions.
10. Store model versions and analysis provenance.

Analysis should be performed at multiple window sizes. A single FFT window cannot simultaneously represent precise transients and fine low-frequency resolution.

## 50. Useful feature families

| Feature family | Possible descriptors | Possible use | Important limitation |
|---|---|---|---|
| Level | Peak, RMS, loudness estimate, local contrast | Prominence and dynamic balance | Not equivalent to attention |
| Onset | Onset strength, transient density, attack time | Event grouping, transient competition | Different detectors disagree |
| Spectrum | Centroid, bandwidth, flatness, roll-off | Timbre and spectral contrast | Strongly dependent on window and content |
| Tonality | Harmonicity, pitch confidence, inharmonicity | Fusion and pitch-stream hypotheses | Percussive sounds may have no stable pitch |
| Change | Spectral flux, waveform difference, feature novelty | Change detection and emergence | High change is not necessarily salient |
| Modulation | Amplitude/frequency modulation rate and depth | Common fate, texture, roughness proxies | Modulation metrics are model-specific |
| Rhythm | Inter-onset intervals, periodicity, accent profile | Stream continuity and rhythmic independence | Polyrhythms complicate a single pulse estimate |
| Space | Pan, interaural cues, width, direct/reverb estimate | Spatial grouping and movement | Depends on playback format and renderer |
| Masking | Auditory-band energy relations, temporal overlap | Risk screening | Not a guarantee of audibility |
| Memory | Repetition, recurrence, motif similarity | Top-down relevance proxy | Requires reliable material lineage |

## 51. Time-frequency representations

The system SHOULD select analysis representations based on the question.

- STFT: general time-frequency analysis with a chosen window/hop trade-off.
- Constant-Q transform: useful where logarithmic frequency resolution helps pitch-related structure.
- ERB/Bark-like auditory bands: useful for perceptually motivated band grouping and masking proxies.
- Waveform/envelope analysis: useful for transients and amplitude behaviour.
- Onset/event analysis: useful for temporal grouping and local density.
- Spatial analysis: useful where multichannel or binaural signals are available.

No representation is universally optimal. Every analysis result SHOULD include sample rate, channel layout, window size, hop size, scaling, normalisation, and algorithm version.

## 52. Specific loudness and loudness models

Psychoacoustic loudness models can estimate perceived loudness more meaningfully than raw amplitude measures in some contexts. Specific loudness distributions can also reveal how energy is distributed across auditory bands. However, the model's assumptions, calibration, and applicable signal classes must be documented. Use standards such as ITU-R BS.1770 for programme loudness tasks, not as a replacement for a full object-attention model [4].

## 53. Roughness, sharpness, fluctuation, and sensory descriptors

Descriptors such as roughness, sharpness, fluctuation strength, tonality, and loudness may help distinguish timbral or modulation conditions. Their definitions and implementations vary by model and standard. They should be versioned, calibrated where required, and interpreted as descriptors rather than universal aesthetic values [9][10].

## 54. Feature normalisation

Feature values should be normalised using a documented reference:

- within one sound object;
- within one stem;
- within one scene;
- across one composition;
- against a calibrated reference set.

The software MUST NOT silently compare values normalised under different scopes. Store the normalisation method and reference range with every derived score.

## 55. Feature-to-meaning boundary

A feature extractor can report high spectral flux. It cannot conclude, by itself, that the music has become more exciting. It can report high band overlap. It cannot prove that two sounds are perceptually fused. It can report a sharp onset. It cannot establish that the listener will attend to it.

Semantic interpretation requires context, a model, or human evaluation. The architecture MUST preserve that boundary.

---

# Part XI — Perceptual Planning and Algorithms

## 56. Perceptual planning as a constrained search problem

A scene plan is a set of intended relationships over time. Candidate orchestration can be evaluated against:

- identity preservation;
- attention trajectory;
- desired grouping;
- intended stream separation;
- masking risk;
- density profile;
- contrast profile;
- spatial intention;
- transition continuity;
- artistic brief constraints.

The planner SHOULD produce several valid candidates when the space of solutions is ambiguous.

## 57. A multi-layer perceptual planner

Suggested responsibilities:

1. **Scene intention planner:** chooses the scene type and attention trajectory.
2. **Role assignment planner:** maps musical roles to perceptual functions.
3. **Grouping planner:** proposes object and stream relationships.
4. **Salience planner:** manages intended focal priority and competition.
5. **Density planner:** manages independent density dimensions.
6. **Masking analyst:** identifies possible acoustic conflicts.
7. **Spatial planner:** manages apparent location and depth.
8. **Transition planner:** plans scene-state changes.
9. **Evaluator:** compares candidates against declared intent.
10. **Repair planner:** proposes minimal changes for detected conflicts.

These services may be implemented as modules in one process. Their separation is about responsibility, not mandatory microservice deployment.

## 58. Rule-based scene constraints

Examples:

- a foreground motif must remain distinguishable from its supporting pattern;
- a fused percussion object must retain a common attack envelope;
- a call-and-response exchange must leave enough temporal space for each response to register;
- a background layer should not continuously override the intended focal transient;
- a mono-critical motif must retain identity in mono;
- an ambiguity section must preserve at least two plausible grouping interpretations;
- a deliberately dense section must still satisfy technical render limits.

Each constraint should declare owner, scope, severity, and whether it can be overridden by the composer.

## 59. Heuristic salience model

A project MAY implement a heuristic composite score, but it MUST expose its components.

For event or object `i` in time window `t`:

```text
S_i(t) = w_level * L_i(t)
       + w_onset * O_i(t)
       + w_spectral * C_i(t)
       + w_pitch * P_i(t)
       + w_rhythm * R_i(t)
       + w_timbre * T_i(t)
       + w_space * X_i(t)
       + w_context * K_i(t)
```

Where:

- `L` = local level contrast;
- `O` = onset/transient novelty;
- `C` = spectral contrast;
- `P` = pitch or register isolation;
- `R` = rhythmic novelty or isolation;
- `T` = timbral distinctiveness;
- `X` = spatial contrast;
- `K` = contextual relevance (motif return, formal role, or brief alignment).

This is a design heuristic, not a validated universal model of human attention. Weights MUST be calibrated per application, stored with the model version, and tested against listening evidence.

## 60. Masking-risk heuristic

A practical risk score may combine:

- auditory-band overlap;
- relative level;
- temporal overlap;
- transient proximity;
- similar pitch/register;
- intended grouping relationship;
- importance of the masked event.

A high-risk pair is not necessarily wrong. The evaluator should ask whether the overlap matches the declared scene intention.

## 61. Attention allocation as multi-objective planning

The planner SHOULD avoid treating all dimensions as one weighted sum. It may compare candidates by Pareto dominance or rule-based priorities.

Candidate A may offer:
- stronger foreground clarity;
- lower timbral novelty;
- higher continuity.

Candidate B may offer:
- greater ambiguity;
- stronger contrast;
- more masking risk.

Neither is universally better. The composition brief and the current section intention determine the relevant trade-off.

## 62. Minimal repair

When the system detects an unintended conflict, it SHOULD propose the smallest change that resolves it while preserving accepted identity.

Possible repairs:

- change only one layer's onset;
- reduce one transient's duration;
- alter one register;
- adjust modulation independence;
- redistribute spatial position;
- alter one automation lane;
- simplify one voice in the conflicting window;
- move the competing event;
- create a short gap;
- change the role of one source.

Do not automatically lower every competing track or remove the most active material. Repair must be intent-aware.

## 63. Perceptual candidate comparison

Each candidate report SHOULD include:

- intended scene type;
- expected figure/ground organisation;
- grouping hypotheses;
- attention trajectory;
- density profile;
- masking-risk pairs;
- spatial plan;
- confidence and uncertainty;
- changes from the parent candidate;
- constraints passed or violated;
- suggested listening focus.

---

# Part XII — Canonical Data Model and Interfaces

## 64. Data-model design rules

Perceptual entities MUST reference ontology entities using canonical IDs. They MUST NOT duplicate source events, motifs, tracks, or instruments as detached copies.

Every perceptual estimate SHOULD include:

- unique identifier;
- entity or time-range references;
- model/version provenance;
- confidence;
- evidence source;
- analysis context;
- created/updated revision;
- intended-versus-inferred status.

## 65. SoundObjectProfile

A `SoundObjectProfile` describes how a canonical source or group may be perceived.

```json
{
  "id": "percept:sound-object:metal-hit-01",
  "schema_version": "1.0.0",
  "ontology_refs": ["instrument:metal-layer-a", "instrument:fm-body-b"],
  "identity_ref": "material:metallic-hit-family",
  "perceptual_identity": {
    "intended_unit": "composite_object",
    "grouping_strength_target": 0.82,
    "separability_target": 0.18,
    "ambiguity_target": 0.0
  },
  "acoustic_cues": {
    "common_onset": true,
    "harmonicity_relation": "mixed_inharmonic",
    "shared_envelope": true,
    "shared_modulation": false,
    "spatial_coherence": true
  },
  "role_refs": ["role:percussive-accent"],
  "confidence": 0.9,
  "evidence_kind": "composer_intent"
}
```

The numeric targets are project-specific parameters, not perceptual probabilities.

## 66. AuditoryStream

```json
{
  "id": "percept:stream:upper-clicks",
  "schema_version": "1.0.0",
  "event_refs": ["event:click-001", "event:click-002", "event:click-003"],
  "voice_refs": ["voice:upper-percussion"],
  "time_range_qn": {"start": "32", "end": "48"},
  "continuity_intent": "stable_with_local_omissions",
  "identity_cues": ["timbre_similarity", "rhythmic_periodicity", "register_proximity"],
  "attention_role": "background_detail",
  "model_hypothesis": {
    "stream_coherence": 0.73,
    "confidence": 0.62,
    "model_id": "stream-model-v1"
  }
}
```

A stream may reference events from multiple voices or tracks if the composer intends them to form one perceptual sequence.

## 67. PerceptualGroupingEdge

```json
{
  "id": "percept:edge:group-002",
  "from_ref": "percept:sound-object:metal-hit-01",
  "to_ref": "percept:sound-object:noise-tail-03",
  "relation": "fuses_with",
  "time_range_qn": {"start": "12", "end": "12.5"},
  "cue_evidence": {
    "onset_synchrony": 0.88,
    "envelope_similarity": 0.74,
    "spectral_relatedness": 0.42,
    "spatial_coherence": 0.91
  },
  "strength": 0.79,
  "confidence": 0.71,
  "intent_status": "desired",
  "provenance": {
    "kind": "planner_estimate",
    "model_version": "grouping-estimator-1.2"
  }
}
```

## 68. AttentionPlan

```json
{
  "id": "percept:attention-plan:section-b",
  "section_ref": "section:B",
  "time_range_qn": {"start": "64", "end": "96"},
  "trajectory": "emergent_then_focused",
  "keyframes": [
    {
      "at_qn": "64",
      "target_refs": ["percept:stream:noise-bed"],
      "mode": "diffuse",
      "priority": "medium"
    },
    {
      "at_qn": "76",
      "target_refs": ["percept:stream:upper-clicks"],
      "mode": "emergent",
      "priority": "high"
    },
    {
      "at_qn": "88",
      "target_refs": ["percept:stream:upper-clicks", "percept:stream:bass"],
      "mode": "distributed",
      "priority": "high"
    }
  ],
  "allowed_competition": "moderate",
  "human_override": true
}
```

## 69. MaskingRiskReport

```json
{
  "id": "percept:masking-report:section-b-001",
  "analysis_range_qn": {"start": "64", "end": "96"},
  "pairs": [
    {
      "source_a_ref": "voice:metal-percussion",
      "source_b_ref": "voice:upper-motif",
      "risk": "moderate",
      "risk_score": 0.58,
      "reason_codes": ["spectral_overlap", "transient_proximity"],
      "intent_status": "review",
      "confidence": 0.63
    }
  ],
  "analysis_context": {
    "sample_rate_hz": 48000,
    "channel_layout": "stereo",
    "analysis_model": "masking-proxy-1.0"
  }
}
```

## 70. PerceptualSceneState

```json
{
  "id": "percept:scene-state:section-b-climax",
  "section_ref": "section:B",
  "time_range_qn": {"start": "80", "end": "96"},
  "scene_type": "controlled_overload",
  "figure_refs": ["percept:stream:bass", "percept:stream:upper-clicks"],
  "ground_refs": ["percept:sound-object:noise-bed"],
  "grouping_graph_ref": "percept:grouping-graph:B",
  "attention_plan_ref": "percept:attention-plan:section-b",
  "density_profile_ref": "percept:density-profile:B",
  "spatial_scene_ref": "percept:spatial-scene:B",
  "transition_in_ref": "percept:transition:B-in",
  "transition_out_ref": "percept:transition:B-out"
}
```

## 71. Perceptual entities are time-bounded

A source may be fused with one layer in the opening and segregated from it in the climax. A sound may be background at first, foreground later, and part of a diffuse mass at the end.

Therefore, perceptual relationships MUST support time ranges, keyframes, interpolation policies, and partial overlap. A single static label on a track is insufficient.

## 72. Interface boundaries

Suggested subsystem APIs:

- `build_scene_hypotheses(project_revision, analysis_context)`
- `estimate_grouping(entity_refs, time_range, cue_model)`
- `plan_attention(scene_intent, candidate_material, constraints)`
- `analyse_density(audio_or_events, scope, profile)`
- `analyse_masking(source_refs, time_range, render_context)`
- `plan_spatial_scene(scene_intent, renderer_capabilities)`
- `evaluate_perceptual_candidate(candidate_ref, perceptual_brief)`
- `suggest_minimal_repairs(report_ref, mutation_contracts)`
- `compare_scene_candidates(candidate_refs, evaluation_profile)`

All interfaces MUST be side-effect free until an explicit commit operation. They MUST return provenance, warnings, confidence, and unresolved questions.

---

# Part XIII — System Workflow and Decision Ownership

## 73. Perceptual orchestration lifecycle

1. Read the `CompositionBrief` and current composition graph.
2. Identify the musical roles and materials active in the target range.
3. Read the intended scene state and attention trajectory.
4. Build one or more perceptual grouping hypotheses.
5. Generate candidate role and scene arrangements.
6. Render previews or analyse available audio.
7. Estimate salience competition, density, masking, and spatial robustness.
8. Validate musical and perceptual constraints.
9. Compare alternatives against the artistic intention.
10. Present explanations and uncertainty to the composer.
11. Commit the selected scene plan transactionally.
12. Preserve the decision history and analysis provenance.

## 74. Decision ownership

| Decision | Primary owner | Other contributors |
|---|---|---|
| Intended foreground | Composition/section planner or composer | Attention planner |
| Intended fusion or separation | Perceptual scene planner | Sound design and event generators |
| Acoustic grouping estimate | Analysis layer | DSP and source models |
| Masking-risk estimate | Perceptual analysis | Audio engine and mixer |
| Scene density target | Composition director | Perceptual planner |
| Spatial intention | Composer / scene planner | Renderer capabilities |
| Repair candidate | Repair planner | Mutation system and material generators |
| Acceptance | Composer or explicit selection policy | Evaluator |

The analysis layer may report that a declared intention is at risk. It MUST NOT silently rewrite the composition or override a frozen decision.

## 75. Candidate and commitment separation

Every perceptual alternative must be a candidate until explicitly accepted. A candidate may include changes to role assignments, grouping relations, attention keyframes, spatial positions, event timing, or sound realisation. The system must preserve the parent version and all unaffected entities.

## 76. Mutation contracts for perceptual repair

A repair request MUST specify:

- target entity or scene range;
- intended perceptual result;
- allowed dimensions of change;
- protected identities and relationships;
- hard constraints;
- soft preferences;
- acceptable trade-offs;
- whether changes may affect neighbouring sections;
- whether audio regeneration is required;
- rollback strategy.

Example:

```json
{
  "id": "mutation:foreground-clarity-repair-01",
  "target_refs": ["voice:upper-motif", "voice:metal-percussion"],
  "intent": "restore_motif_legibility_without_simplifying_its_rhythm",
  "allowed_changes": ["transient_timing", "spectral_balance", "automation", "spatial_position"],
  "protected": ["motif:upper-motif-A", "pattern:metal-accent-pattern"],
  "forbidden_changes": ["pitch_content", "motif_identity", "section_form"],
  "scope": {"start_qn": "80", "end_qn": "88"},
  "preserve_unrelated_material": true,
  "require_candidate_review": true
}
```

---

# Part XIV — Evaluation and Listening Validation

## 77. Why perceptual validation must include listeners

A computational model can identify likely conflicts, but it cannot establish every listener's experience. The architecture must combine signal analysis, explicit intent, and human listening tests.

The 2026 synthetic review of auditory scene analysis in music surveys acoustic grouping, schema-based factors, blend, segregation, salience, complexity, and listener differences, emphasising that scene perception is shaped by interacting stimulus and listener factors [1]. Computational models of auditory scene analysis are also often partial: different models capture different grouping or prediction mechanisms rather than providing one complete universal account [11].

The implication for software design is to treat perceptual output as a hypothesis and maintain a human validation path.

## 78. Evaluation dimensions

| Dimension | Evaluation question |
|---|---|
| Intended grouping | Are components heard as fused or separate as intended? |
| Stream continuity | Can a listener follow the intended sequence? |
| Foreground fidelity | Does the intended figure become perceptually important? |
| Background stability | Does the ground support rather than accidentally dominate? |
| Attention transition | Is the focus change recognisable and musically effective? |
| Masking | Are important events obscured unintentionally? |
| Density | Does the scene feel as crowded or open as intended? |
| Spatial robustness | Does the intended distinction survive target playback formats? |
| Identity | Are recurring objects or motifs recognisable at the intended level? |
| Ambiguity | Is ambiguity productive and controlled, rather than an accidental failure? |

## 79. Listening-test designs

### 79.1 Focused A/B test

Compare two versions that differ in one perceptual variable. Ask a specific question: Which version makes the motif easier to follow? Which version creates stronger fusion? Which version makes the foreground handoff more apparent?

### 79.2 Blind preference test

Use when preference is relevant, but do not treat preference as equivalent to clarity, grouping, or artistic success.

### 79.3 Identification test

Ask listeners to identify a recurring stream, motif, source, or focal event. This helps assess identity and continuity.

### 79.4 Attention instruction test

Give listeners a listening task (follow the bass, notice the high-register stream, count a repeated event) and compare whether the intended scene supports that task.

### 79.5 Free-description test

Ask listeners what they hear as the main figure, what seems connected, and what changed. This can reveal unexpected scene interpretations.

### 79.6 Repeated-listening test

Compare first-listen and later-listen reports. A latent layer may be intentionally difficult to notice at first but become meaningful through familiarity.

## 80. Testing protocol requirements

Every recorded listening result SHOULD specify:

- participant count and relevant listener characteristics where ethically and practically available;
- playback equipment and environment;
- playback level and calibration procedure if measured;
- excerpt duration and context;
- listening task and exact prompt;
- randomisation/blinding method;
- response format;
- analysis method;
- uncertainty and limitations.

Do not generalise a small informal listening session to all listeners.

## 81. Regression corpus

Maintain a corpus of perceptual reference projects:

1. fused composite transient;
2. clearly segregated multi-stream rhythm;
3. shared-modulation sound object;
4. independent modulation split;
5. foreground handoff;
6. figure-ground reversal;
7. controlled masking;
8. unintended masking repair;
9. mono-robust spatial arrangement;
10. deliberate ambiguity;
11. controlled overload;
12. latent-to-salient emergence;
13. recurring motif across timbral changes;
14. interrupted stream with perceived continuity;
15. diffuse sound mass.

Each reference should include project files, audio renders, intended scene description, expected diagnostics, listening notes, and known failure cases.

## 82. Automated versus human acceptance

Automated tests can verify schema integrity, references, time ranges, routing, reproducibility, metric computation, and constraint handling. They cannot alone establish artistic success or universal perceptual outcomes.

Use separate acceptance statuses:

- `technically_valid`;
- `perceptually_reviewed`;
- `intent_aligned_by_review`;
- `composer_accepted`;
- `export_ready`.

---

# Part XV — Practical Worked Examples

## 83. Example A: A kick and bass that should become one rhythmic object

### Intention

The kick and bass should be perceived as a unified low-frequency gesture rather than two unrelated sources.

### Plan

- align important attacks;
- preserve a complementary spectral envelope;
- avoid unnecessary modulation divergence during the shared attack;
- allow the bass tail to create the pitch identity after the kick transient;
- use a shared accent map;
- permit later separation as a formal development.

### Evaluation

- Are the attacks heard as one coupled gesture?
- Does the bass pitch remain intelligible?
- Does the kick mask the bass's important pitch information?
- Does the relationship remain clear on smaller playback systems?

### Possible development

Gradually offset the bass attack or give its upper harmonics independent motion. The coupled object may split into two streams while retaining rhythmic kinship.

## 84. Example B: A percussion layer that should remain independently followable

### Intention

A high-register irregular click stream should remain distinct from the main breakbeat.

### Plan

- give the click stream a stable timbral family;
- preserve a recognisable rhythmic identity;
- choose a register and transient shape that contrasts with the breakbeat;
- avoid always aligning its strongest events with the main drum transients;
- keep its spatial position sufficiently consistent;
- allow deliberate interruptions without destroying its stream identity.

### Evaluation

Ask listeners to follow or count the click stream while the breakbeat plays. Compare the full mix with a version where the click stream is isolated or slightly reduced in density.

## 85. Example C: A fused granular object that slowly splits into independent layers

### Intention

The opening should sound like one evolving cloud. Later, the same material should be heard as separate rhythmic, pitched, and noise components.

### Stages

1. Share onset envelopes and broad modulation.
2. Use related spectral movement to bind the cloud.
3. Gradually separate modulation rates.
4. Introduce independent event timing.
5. Give the emerging streams different registers or spatial trajectories.
6. Preserve a recognisable residue of the original cloud as a memory cue.

### Core technique

Change grouping cues gradually. Do not simply add three unrelated instruments and call the result a transformation.

## 86. Example D: A foreground handoff from texture to motif

### Intention

A background texture should gradually reveal a repeating melodic fragment and become the foreground.

### Stages

1. Establish the texture as the dominant scene.
2. Embed a low-contrast fragment within the texture.
3. Repeat the fragment with stable timing or contour.
4. Increase one or two differentiating cues (register, onset contrast, timbral separation).
5. Reduce competing texture activity around the fragment.
6. Allow the fragment to become an independently followable stream.
7. Retain the original texture as a quieter ground or remove it.

### Evaluation

Can listeners recognise that the motif emerged from the texture rather than entering as a completely unrelated part?

## 87. Example E: Intentional controlled overload

### Intention

Create a section where several streams compete. The goal is not clarity but a composed sense of excess, with enough internal identity for later re-listening.

### Plan

- declare the section's scene type as `controlled_overload`;
- identify the active streams and their origins;
- define which rhythmic or timbral signatures should remain recoverable;
- allow high attention competition;
- set technical limits for peak, true peak, and rendering load;
- plan a later reduction or re-focus.

### Evaluation

Ask not “Can every part be heard clearly?” but:

- Does the overload feel intentional?
- Does it have internal character?
- Are any important details recoverable on repeated listening?
- Does the transition out of overload create a meaningful perceptual change?

## 88. Example F: A motif returns but is heard differently

### Intention

A motif introduced as a foreground lead should return as part of a diffuse background texture.

### Plan

- preserve selected identity features (for example rhythm and interval contour);
- alter timbral integration and spectral context;
- reduce transient contrast;
- distribute or blur its partials;
- align it with background modulation;
- maintain motif lineage in the data model.

This example demonstrates that musical identity and perceptual role can change independently.

---

# Part XVI — Failure Modes and Anti-Patterns

## 89. Treating track count as perceived source count

**Failure:** Every track is assigned a unique foreground identity.  
**Consequence:** The model misunderstands fused objects and cross-track streams.  
**Correction:** Build a time-dependent perceptual grouping graph.

## 90. Treating loudness as attention

**Failure:** The loudest track is automatically the foreground.  
**Consequence:** Quiet but distinctive gestures and learned expectations are ignored.  
**Correction:** Separate level, salience, intended priority, and attention hypothesis.

## 91. Treating clarity as correctness

**Failure:** The evaluator always separates overlapping parts.  
**Consequence:** Sound masses, ambiguity, and hybrid objects are destroyed.  
**Correction:** Evaluate against intended grouping, not universal separation.

## 92. One-dimensional density

**Failure:** Density is calculated only as MIDI note count or events per bar.  
**Consequence:** Spectral, modulation, spatial, and attentional crowding are missed.  
**Correction:** Maintain independent density dimensions.

## 93. Static foreground/background labels

**Failure:** Each instrument receives a permanent role such as `lead` or `pad`.  
**Consequence:** Scene transitions and role exchange cannot be represented.  
**Correction:** Use time-bounded perceptual functions and attention keyframes.

## 94. Overconfident psychoacoustic claims

**Failure:** A heuristic claims a source is inaudible, fused, or attention-grabbing.  
**Consequence:** Developers mistake a proxy metric for listener evidence.  
**Correction:** Return risk, confidence, model version, and listening-test status.

## 95. Spatialisation as a substitute for orchestration

**Failure:** Every conflict is solved by panning sources apart.  
**Consequence:** The mix becomes spatially scattered and fragile in mono or non-target playback.  
**Correction:** Use timing, timbre, register, dynamics, articulation, and role relationships too.

## 96. Constant novelty

**Failure:** Every event is designed to capture attention.  
**Consequence:** Nothing remains a stable reference; local surprise loses meaning.  
**Correction:** Reserve contrast and novelty. Use stable ground to make change perceptible.

## 97. Ignoring the intended listening mode

**Failure:** The scene is evaluated only in one playback context.  
**Consequence:** Important distinctions collapse on headphones, speakers, mono, or bandwidth-limited systems.  
**Correction:** Declare target contexts and test robustly.

## 98. Automatic repair that destroys identity

**Failure:** The system removes or simplifies material to reduce every diagnostic score.  
**Consequence:** A perceptual issue is “fixed” by erasing composition.  
**Correction:** Apply mutation contracts, minimal repair, candidate comparison, and human approval.

---

# Part XVII — Implementation Roadmap

## 99. Stage 0 — Data contracts and terminology

Deliverables:

- perceptual entity definitions;
- grouping relation catalogue;
- scene-state and attention-plan schemas;
- evidence and confidence semantics;
- links to canonical ontology objects;
- versioned model metadata.

Acceptance:

- schemas validate;
- no duplicate musical entities are created;
- all perceptual relations support time ranges;
- composer intent and inferred estimates remain distinguishable.

## 100. Stage 1 — Manual scene authoring

Deliverables:

- assign intended figures and grounds;
- define grouping/fusion intent;
- author attention keyframes;
- define density profiles;
- specify spatial intentions;
- compare scene states.

Acceptance:

- changes are editable and serialisable;
- frozen materials are preserved;
- scene plans can be rendered or inspected;
- user-authored intent survives regeneration.

## 101. Stage 2 — Basic signal diagnostics

Deliverables:

- event density;
- band-energy summaries;
- transient-overlap reports;
- local loudness/contrast reports;
- spectral feature extraction;
- channel and mono diagnostics.

Acceptance:

- analysis metadata is complete;
- results are deterministic for fixed inputs and settings;
- no diagnostic is labelled as a direct measurement of attention;
- unit and reference tests cover signal edge cases.

## 102. Stage 3 — Grouping and masking hypotheses

Deliverables:

- onset synchrony estimates;
- harmonicity or spectral-relatedness estimates;
- shared modulation estimates;
- stream continuity hypotheses;
- masking-risk reports;
- confidence and uncertainty output.

Acceptance:

- reference cases cover fusion and segregation;
- model outputs are compared with controlled listening tests;
- false confidence is reported and tracked;
- ambiguity is representable.

## 103. Stage 4 — Attention planning

Deliverables:

- intended attention trajectories;
- salience component maps;
- competition diagnostics;
- foreground handoff planning;
- minimal repair suggestions.

Acceptance:

- user priority is not overwritten by a heuristic;
- candidate changes preserve declared constraints;
- all repair suggestions include a reason and affected entities;
- the composer can accept, reject, or edit every candidate.

## 104. Stage 5 — Perceptual evaluation and corpus

Deliverables:

- reference compositions;
- listener-test protocols;
- regression suite;
- model comparison reports;
- perceptual review state in project metadata.

Acceptance:

- automated and human evaluation are separate;
- listening conditions are recorded;
- metrics are traceable to versions and configurations;
- known failure cases remain in the test suite.

## 105. Stage 6 — Adaptive orchestration

Deliverables:

- context-sensitive scene transitions;
- attention memory;
- perceptual replanning;
- adaptive role exchange;
- long-range scene diversity.

Acceptance:

- replanning respects accepted material and mutation contracts;
- perceptual state does not drift without provenance;
- deterministic regeneration is supported;
- the system can explain its decision chain.

---

# Part XVIII — Developer Acceptance Checklist

Before a perceptual orchestration feature is merged, ask:

### Ontology and representation

- [ ] Does it reference canonical musical entities rather than copying them?
- [ ] Are scene relations time-bounded?
- [ ] Are intended relationships separate from inferred estimates?
- [ ] Are confidence, provenance, and model versions stored?
- [ ] Can ambiguous grouping be represented?

### Perceptual reasoning

- [ ] Does it distinguish salience from attention?
- [ ] Does it distinguish loudness from prominence?
- [ ] Does it account for concurrent and sequential grouping?
- [ ] Does it preserve multiple density dimensions?
- [ ] Does it allow intentional masking and overload?
- [ ] Does it avoid claiming universal listener outcomes?

### Composition and generation

- [ ] Does it follow the composition brief?
- [ ] Does it preserve material identity?
- [ ] Are candidate generation and commitment separate?
- [ ] Are mutations constrained and reversible?
- [ ] Can the human composer override the result?

### Analysis and evaluation

- [ ] Are signal-analysis parameters stored?
- [ ] Are features interpreted only within their valid scope?
- [ ] Are estimates tested against reference examples?
- [ ] Are human listening results separate from model output?
- [ ] Are confidence and uncertainty visible?

### Production and robustness

- [ ] Does the feature work with the supported channel layouts?
- [ ] Is mono compatibility tested when relevant?
- [ ] Does it avoid relying on one playback system?
- [ ] Are audio and project states reproducible?
- [ ] Does it avoid introducing uncontrolled gain or clipping?

### User experience

- [ ] Can the composer inspect why a conflict was detected?
- [ ] Can the composer audition alternatives?
- [ ] Are controls expressed in musical/perceptual language?
- [ ] Can changes be accepted, rejected, frozen, and restored?
- [ ] Does the interface avoid presenting heuristics as facts?

---

# Appendix A — Glossary

| Term | Definition |
|---|---|
| Auditory scene | The organised perceptual interpretation of a complex sound field |
| Auditory stream | A sequence of events perceived as belonging together over time |
| Sound object | A perceptual unit that may be formed from one or multiple technical sources |
| Perceptual group | A set of objects or streams heard as related |
| Figure | The currently prominent perceptual element or group |
| Ground | The supporting perceptual field |
| Salience | Degree of distinctiveness relative to context |
| Attention | Selective allocation of listening or cognitive processing |
| Fusion | Components perceived as one object or event |
| Segregation | Components perceived as distinct objects or streams |
| Common onset | Similar onset timing that supports grouping |
| Harmonicity | Frequency relationships that support a common pitched object |
| Common fate | Shared change or modulation that supports grouping |
| Co-modulation | Related amplitude or frequency changes across components |
| Masking | Reduced audibility of one signal due to another signal |
| Spectral density | Occupancy and overlap across frequency regions |
| Attention trajectory | Intended change in focal attention over time |
| Perceptual handoff | Transfer of focal attention from one figure to another |
| Scene state | Time-bounded description of perceptual organisation |
| Scene transition | Change from one perceptual organisation to another |
| Ambiguity | A state with multiple plausible perceptual interpretations |
| Controlled overload | Intentional high competition or density with defined artistic purpose |
| Latent layer | A low-priority or partly hidden element that may emerge later |
| Perceptual proxy | A measurable feature used to estimate a perceptual quality indirectly |
| Confidence | The system's stated confidence in an estimate, not a guarantee of correctness |
| Listening context | Playback and task conditions under which a scene is evaluated |

---

# Appendix B — Suggested Reason Codes

Use stable machine-readable reason codes in diagnostics.

| Code | Meaning |
|---|---|
| `GROUP_COMMON_ONSET` | Common onset supports fusion |
| `GROUP_HARMONICITY` | Harmonic relation supports fusion |
| `GROUP_SHARED_MODULATION` | Common modulation supports fusion |
| `GROUP_TIMBRE_SIMILARITY` | Timbre similarity supports stream integration |
| `GROUP_SPATIAL_COHERENCE` | Similar spatial position supports grouping |
| `SEPARATE_REGISTER_CONTRAST` | Register contrast supports segregation |
| `SEPARATE_TIMBRE_CONTRAST` | Timbre contrast supports segregation |
| `SEPARATE_ONSET_OFFSET` | Onset difference may promote separation |
| `SEPARATE_SPATIAL_DIVERGENCE` | Spatial divergence supports separation |
| `MASK_SPECTRAL_OVERLAP` | Spectral regions overlap |
| `MASK_TEMPORAL_OVERLAP` | Events overlap in time |
| `MASK_TRANSIENT_COMPETITION` | Close transients may compete |
| `ATTN_COMPETING_FIGURES` | Several high-priority figures coexist |
| `ATTN_UNINTENDED_DOMINANCE` | A source appears more prominent than intended |
| `ATTN_HANDOFF_UNCLEAR` | Planned focal transfer may not be perceptible |
| `DENSITY_EVENT_HIGH` | Event density exceeds the configured profile |
| `DENSITY_SPECTRAL_HIGH` | Spectral occupancy exceeds the configured profile |
| `SPACE_MONO_COLLAPSE` | Important distinction weakens in mono |
| `SPACE_RENDER_UNAVAILABLE` | Requested spatial renderer is unavailable |
| `MODEL_LOW_CONFIDENCE` | Estimate is weak or uncertain |
| `INTENT_METRIC_CONFLICT` | Metric suggests risk, but the declared intention may permit it |
| `HUMAN_REVIEW_REQUIRED` | A perceptual judgement cannot be resolved automatically |

---

# Appendix C — Reference Listening Exercises

These exercises are designed for developers and composers to connect measurable signal properties with actual listening.

1. **Fusion by onset:** use the same two sounds with several onset offsets. Record when they are heard as one event or two.
2. **Fusion by modulation:** keep two layers spectrally distinct but share one modulation source; then give them independent modulation.
3. **Fusion by harmonic relation:** compare harmonic and inharmonic partial arrangements with the same amplitude envelope.
4. **Stream segregation by register:** alternate events across registers and gradually alter their timing.
5. **Stream segregation by timbre:** keep pitch and rhythm stable while changing timbral identity.
6. **Figure-ground reversal:** keep the same materials but exchange their contrast and activity over time.
7. **Quiet foreground:** create a sparse scene where a low-level event becomes the focal object.
8. **Transient competition:** place multiple attacks at progressively smaller intervals and compare perceived separation.
9. **Masking by noise:** place a motif under a broadband texture and gradually alter its spectral overlap.
10. **Spatial grouping:** compare a common spatial image with divergent positions, then test mono.
11. **Latent motif:** embed a fragment in a texture and reveal it gradually.
12. **Controlled overload:** create a dense scene, then ask listeners what remains identifiable after one and five listens.
13. **Attention memory:** repeat an object after a long absence and compare its recognition with a new object.
14. **Perceptual handoff:** transfer a rhythmic identity across three instruments using one preserved feature at each transition.
15. **Ambiguous object:** create two components whose onset, spectrum, modulation, and spatial cues partially conflict.

Record the audio, analysis context, listening questions, responses, and interpretations. The exercise is valuable precisely because results can differ between listeners.

---

# Appendix D — Further Reading and Technical References

The following references ground the perceptual concepts and provide starting points for deeper study. They do not prescribe one definitive implementation.

1. **Siedenburg, K., Hake, R., Jacobsen, S., & Bürgel, M. (2026).** “Auditory scene analysis in music: A synthetic review.” *Attention, Perception, & Psychophysics*, 88, 171. DOI: [10.3758/s13414-026-03310-y](https://doi.org/10.3758/s13414-026-03310-y). A recent synthesis of musical scene analysis, grouping, blending, segregation, salience, complexity, and individual differences. [Open access](https://pmc.ncbi.nlm.nih.gov/articles/PMC13429554/).

2. **McAdams, S. (2024).** “Processes of auditory organization during music listening.” In *Perception and Cognition of Music: The Sorbonne Lectures*. Oxford University Press. DOI: [10.1093/oso/9780198939177.003.0002](https://doi.org/10.1093/oso/9780198939177.003.0002). A contemporary account of concurrent and sequential grouping in music.

3. **Shinn-Cunningham, B. G. (2017).** “Modelling auditory attention.” *Philosophical Transactions of the Royal Society B*. [Open access](https://pmc.ncbi.nlm.nih.gov/articles/PMC5206269/). Reviews computational approaches to auditory attention and its interaction with scene organisation.

4. **ITU-R Recommendation BS.1770-5 (2023).** *Algorithms to measure audio programme loudness and true-peak audio level*. [ITU recommendation](https://www.itu.int/rec/R-REC-BS.1770/en). Technical reference for programme loudness and true-peak measurements; not a complete model of musical attention.

5. **European Broadcasting Union (2023).** *EBU R 128: Loudness normalisation and permitted maximum level of audio signals*, version 5.0. [EBU publication](https://tech.ebu.ch/publications/r128). Broadcast loudness recommendation; use only when the delivery context calls for it.

6. **Blauert, J. (1997).** *Spatial Hearing: The Psychophysics of Human Sound Localization*. Revised edition. MIT Press. Foundational reference on spatial hearing, localisation, and auditory spatial cues. See also: **“Auditory localization: a comprehensive practical review” (2024)**, *Frontiers in Psychology*. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/39049946/).

7. **Pearce, M. T., & Wiggins, G. A. (2012).** “Auditory expectation: the information dynamics of music perception and cognition.” *Topics in Cognitive Science*, 4(4), 625–652. DOI: [10.1111/j.1756-8765.2012.01214.x](https://doi.org/10.1111/j.1756-8765.2012.01214.x). Computational and cognitive perspectives on musical expectation.

8. **Cognitive and sensory expectations independently shape musical expectancy and pleasure (2023).** [PubMed record](https://pubmed.ncbi.nlm.nih.gov/38104601/). Research on distinct contributions of sensory and cognitive expectation.

9. **Fastl, H., & Zwicker, E. (2007).** *Psychoacoustics: Facts and Models*. 3rd edition. Springer. A broad reference for loudness, masking, roughness, sharpness, and auditory perception.

10. **DIN 45692:2009-08.** *Measurement technique for the simulation of the auditory sensation of sharpness*. Standard reference for sharpness calculation; use the applicable licensed standard and implementation details.

11. **Computational Models of Auditory Scene Analysis: A Review (2016).** [Open access](https://pmc.ncbi.nlm.nih.gov/articles/PMC5108797/). Reviews grouping, stream formation, competing interpretations, prediction, and evaluation of computational models.

12. **Bregman, A. S. (1990).** *Auditory Scene Analysis: The Perceptual Organization of Sound*. MIT Press. Foundational work on auditory grouping and stream segregation.

13. **Deutsch, D. (Ed.). (2013).** *The Psychology of Music*. 3rd edition. Academic Press. Broad reference for music perception and cognition.

14. **Noble, J. (2019).** “Auditory Scene Analysis.” *Timbre and Orchestration Resource*. [Article](https://timbreandorchestration.org/writings/timbre-lingo/2019/2/12/auditory-scene-analysis). Accessible introduction to grouping cues in orchestration.

---

# Appendix E — Summary of Constitutional Requirements

The Perceptual Orchestration subsystem MUST adhere to these governing requirements:

1. It MUST distinguish the signal, the intended scene, and the estimated listener scene.
2. It MUST represent sound objects and streams independently from technical tracks and instruments.
3. It MUST support time-varying grouping, figure/ground roles, and attention trajectories.
4. It MUST distinguish salience from attention and both from loudness.
5. It MUST represent multiple density dimensions.
6. It MUST allow fusion, segregation, ambiguity, masking, emergence, and controlled overload as valid artistic intentions.
7. It MUST preserve uncertainty and avoid claims of universal perceptual prediction.
8. It MUST reference canonical ontology entities and preserve material provenance.
9. It MUST generate repair suggestions as candidates and respect mutation contracts.
10. It MUST maintain human composer authority over artistic acceptance.
11. It SHOULD validate important perceptual claims through listening tests.
12. It SHOULD test relevant playback contexts, including mono and spatial rendering fallbacks.
13. It SHOULD provide interpretable diagnostics and identify the evidence behind each estimate.
14. It MUST keep technical audio validity separate from perceptual and artistic evaluation.
15. It MUST be reproducible: analysis methods, model versions, normalisation, and decision provenance must be recorded.

## Final Principle

**The listener does not hear a project file. The listener hears a scene.**

A generative instrument must therefore compose not only events, notes, instruments, and effects, but also the perceptual relationships that turn those materials into a musical experience.

Its task is not to force every listener to hear the same thing. Its task is to make perceptual intention representable, testable, revisable, and creatively useful.
