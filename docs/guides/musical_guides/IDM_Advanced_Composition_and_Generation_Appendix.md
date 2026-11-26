# IDM: Advanced Composition and Generative Systems

*A companion volume to **IDM: A Field Guide for Composers, Producers, and Programmers***

**Version:** 1.0  
**Prepared:** 23 November 2026  
**Purpose:** Extend the original field guide from a survey of techniques into a complete methodology for composing, orchestrating, generating, rendering, and evaluating complex electronic music.

---

## How this appendix relates to the original guide

The original field guide already introduces the history and identity of IDM; pulse, meter, subdivision, syncopation, polymeter, break editing, harmony, motifs, sound transformation, macro-form, Euclidean rhythms, probability, Markov chains, several algorithmic models, basic software architecture, Python pattern generation, audio-feature mapping, mixing, listening, and introductory exercises.

This appendix deliberately does **not** repeat those explanations. It develops the subjects that were only briefly mentioned or absent:

1. how listeners organise and predict complex sound;
2. how to compose phrases, interacting lines, and harmonic motion rather than only loops;
3. how to design time at several structural scales;
4. how to orchestrate electronic sound as a set of interacting musical roles;
5. how synthesis and DSP choices affect musical behaviour;
6. how to design generative systems that create coherent, editable compositions;
7. how to represent, schedule, test, save, and render musical events in software;
8. how to move from a generative sketch to a finished, critically evaluated work.

The central principle is:

> **A complete generative composition system must understand more than how to produce events. It must manage musical identity, expectation, development, hierarchy, constraint, and closure.**

The word *understand* here describes the capabilities represented in the system's rules and data, not consciousness or artistic intention.

# Part I — The listener is part of the composition

## 1. Perception, expectation, and musical information

A composition is not a neutral stream of notes. The listener groups sounds into objects, detects recurring relationships, forms expectations, notices deviations, and revises their interpretation as the piece unfolds. A producer can therefore shape a listener's experience by controlling not only what happens, but also what the listener has had enough time to learn.

The original guide discusses repetition as a reference frame. This section expands that idea into a practical model of perception.

### 1.1 Auditory grouping: why sounds become layers

A listener does not necessarily hear every simultaneous sound as a separate track. The auditory system groups or separates events according to cues such as:

- **Onset synchrony:** sounds beginning together are more likely to be heard as one event or a coordinated unit.
- **Common movement:** components that change together in pitch, amplitude, or position tend to be grouped.
- **Similar timbre:** related spectra and envelopes can make events sound as though they belong to one source.
- **Spatial position:** sounds occupying a similar perceived location may form a coherent stream.
- **Temporal proximity:** closely spaced events can be heard as a phrase, gesture, or continuous texture.
- **Continuity:** a sound that is briefly masked may still be perceived as continuing if its context supports that interpretation.

These principles have practical consequences for electronic orchestration. Two percussion layers can become one composite rhythm if their attacks repeatedly coincide. A single sound can split perceptually into attack and tail if the tail is delayed, filtered, or spatially detached. A rapidly moving sequence of tiny sounds may become a continuous texture rather than a collection of clicks.

**Production use:** When a mix feels crowded, do not immediately reach for EQ. First ask whether several layers are trying to occupy the same perceptual stream. Separate their onsets, envelopes, registers, spatial positions, or articulation. Conversely, synchronise and spectrally align sounds when you want them to fuse into one larger object.

### 1.2 Figure and ground

At any moment, some sounds function as the figure and others as the ground. The figure attracts attention; the ground establishes context.

A useful arrangement model has three roles:

- **Foreground:** the object the listener should follow now: a lead fragment, a peculiar drum gesture, a vocal sample, or a changing resonant sound.
- **Midground:** active supporting material that has its own motion but does not demand primary attention.
- **Background:** drone, room tone, noise, distant percussion, long tails, or a stable harmonic field.

These roles can change over time. A background texture may become the foreground when the beat disappears. A tiny click can become important after the mix has been reduced to near silence. A bass note can temporarily take over the role normally occupied by a melody.

A practical test is to listen once while following only the foreground, then again while following the background. If every layer competes for attention at once, the arrangement has no usable depth.

### 1.3 Masking is both a problem and a compositional resource

**Simultaneous masking** occurs when one sound makes another less perceptible because they overlap in frequency and time. **Temporal masking** occurs when a strong event affects the audibility of nearby events before or after it.

Masking is not solved only by cutting frequencies. It can be controlled compositionally:

- move one sound to a different register;
- shorten one envelope so the other can emerge;
- stagger attacks instead of stacking them;
- alternate which layer is active;
- use a contrasting noise or tonal profile;
- reduce the density of one stream during important events;
- allow masking deliberately when a fused, noisy object is desired.

**Rule:** Preserve the information that matters, not every sound independently. A deliberately obscured layer may be musically successful if its role is to create pressure, ambiguity, or a sense of depth.

### 1.4 Expectation, surprise, and learning

Listeners learn the local behaviour of a composition. After a repeated event, they begin to predict its return. A deviation can therefore feel meaningful even when the deviation itself is small.

A practical model separates three stages:

1. **Establishment:** present a pattern long enough for its identity to become legible.
2. **Prediction:** allow recurrence to create an expectation.
3. **Revision:** alter, delay, omit, interrupt, or transform the expected event.

The strongest surprise is often not the most statistically unlikely event. It is a deviation that is both recognisable as a deviation and understandable in context.

A useful design space is:

| Familiarity | Deviation | Likely effect |
| --- | --- | --- |
| Low | Low | Unclear or neutral; the listener has not learned enough to form a strong expectation |
| High | Low | Stable, hypnotic, predictable, potentially meditative |
| High | Moderate | Tension, groove variation, recognition, satisfying mutation |
| High | Extreme | Shock, rupture, humour, destabilisation, or deliberate discontinuity |
| Low | Extreme | May read as arbitrary unless timbre, gesture, or context provides another form of continuity |

This table is a compositional heuristic, not a universal psychological law.

### 1.5 Complexity, entropy, and attention are different quantities

Do not treat high event density, high statistical entropy, and high perceptual complexity as synonyms.

- A very dense pattern can be predictable if it repeats exactly.
- A sparse pattern can be unpredictable if each event has unusual timing or timbre.
- A simple pattern can be difficult to parse if its accents conflict with the listener's assumed pulse.
- A statistically random signal can be perceptually boring because it lacks grouping and development.

The important question is not “How much information is present?” but “What information can the listener organise, remember, and use to predict what happens next?”

### 1.6 A practical attention map

Before arranging a dense passage, write a short attention map:

| Time span | Foreground | Midground | Background | Intended listener action |
| --- | --- | --- | --- | --- |
| Opening | One isolated motif | Sparse ticks | Low drone | Recognise a sound identity |
| First groove | Kick/bass relationship | Broken percussion | Long room tail | Find the pulse |
| Mutation | New counter-rhythm | Original motif | Reduced ambience | Notice a changed rule |
| Suspension | Granular fragment | Almost absent | Residual tail | Re-evaluate the sound world |
| Return | Familiar motif, altered | Reassembled rhythm | New harmonic bed | Recognise continuity and change |

This simple document can prevent an arrangement from becoming a pile of equally prominent ideas.

# Part II — Composition beyond the loop

## 2. Phrase grammar and musical syntax

A loop is a useful local object. A composition needs relationships between objects. Phrase grammar provides a way to design those relationships without forcing every piece into conventional verse/chorus form.

### 2.1 A phrase is a perceptual unit, not necessarily four bars

A phrase is a span that the listener can recognise as a connected gesture. It can be one bar, three bars, seven bars, or an irregular duration. It may be defined by:

- a rhythmic pattern that reaches a point of rest;
- a melodic contour that arrives at a stable note;
- a sound gesture with a clear attack and decay;
- a gradual accumulation that reaches a threshold;
- a recurring texture that changes state;
- a silence or change of register that creates a boundary.

The bar is a coordinate system. Phrase length is a compositional decision.

### 2.2 Four useful phrase functions

These are flexible functions, not mandatory classical forms:

1. **Presentation:** introduce a recognisable object or system.
2. **Continuation:** extend its behaviour, often by repeating or slightly varying it.
3. **Departure:** move away from the established material through displacement, fragmentation, register change, harmonic change, or a new counter-layer.
4. **Arrival or suspension:** provide a point of rest, an unresolved hold, a reset, or a transition into another phrase.

A phrase can omit one function, combine two, or deliberately end without arrival.

### 2.3 Asymmetry as a way to create direction

A repeated 4 + 4 + 4 + 4 arrangement is easy to understand, but not always the most expressive. Try structures such as:

- 3 + 3 + 2 bars;
- 5 + 7 bars;
- 4 + 4 + 3 bars;
- a 16-bar rhythm with a 15-bar melodic cycle;
- a repeated phrase whose final event is removed every second time.

Asymmetry becomes meaningful when the listener can recognise some invariant: a motif, sound, pulse, phrase opening, or harmonic centre.

### 2.4 Develop a motif through controlled transformations

A motif is more useful when it can survive change. Treat it as a bundle of properties rather than a fixed MIDI clip.

| Transformation | Preserved | Changed | Typical use |
| --- | --- | --- | --- |
| Transposition | Interval contour and rhythm | Pitch level | Register or harmonic relocation |
| Inversion | Interval sizes | Up/down direction | A related but altered melodic identity |
| Retrograde | Note values and intervals | Temporal order | Reflection, reversal, or uncanny recognition |
| Augmentation | Relative pitch sequence | Duration values expanded | Slower, heavier, more spacious version |
| Diminution | Relative pitch sequence | Duration values reduced | Faster, more urgent version |
| Fragmentation | A subset of the original | Completeness | A motif dissolving into rhythmic cells |
| Reordering | Pitch or event vocabulary | Sequence | A controlled recombination |
| Reharmonisation | Melody or rhythm | Pitch context | Same identity, new emotional meaning |
| Reorchestration | Gesture and timing | Sound source and articulation | Same motif in a new perceptual role |
| Spectral transformation | Broad identity or envelope | Spectrum and texture | A motif becoming an evolving sound object |

Avoid applying every transformation to every motif. Choose one or two operations that support the track's larger argument.

### 2.5 Motif identity can be multidimensional

Represent a motif as:

`M = (pitch contour, interval profile, rhythm, duration, articulation, timbre, register, spatial character)`

A transformation can preserve some dimensions and alter others. For example:

- same rhythm + new pitch contour = rhythmic identity with melodic mutation;
- same contour + new timbre = melodic identity with orchestral change;
- same timbre + new rhythm = a familiar sound with a new behavioural role;
- same spectral shape + slower envelope = a percussion motif becoming a sustained texture.

A generative system can use this representation to create coherent variations instead of selecting unrelated notes.

## 3. Counterpoint and interacting musical lines

The original guide explains independent rhythmic systems, but it does not develop counterpoint as a compositional discipline. Counterpoint is useful in electronic music because separate layers can behave like independent voices even when they are made from percussion, noise, samples, or automation.

### 3.1 A line is more than a sequence of notes

A musical line has:

- a contour or trajectory;
- a rhythm and breathing pattern;
- a register;
- a degree of activity;
- an articulation and envelope;
- a relationship to other lines;
- moments of independence and moments of coordination.

A line can be pitched or unpitched. A sequence of filtered clicks can behave contrapuntally against a bass motif if each has an independent rhythmic and gestural identity.

### 3.2 Five relationships between layers

1. **Unison:** layers share the same events, perhaps with different timbres. Useful for weight and composite sound design.
2. **Doubling:** one layer reinforces another at a different register or articulation.
3. **Call and response:** one layer leaves space for another to answer.
4. **Independent counterpoint:** layers have distinct rhythms and contours but coexist within a shared phrase.
5. **Interlocking:** each layer supplies events omitted by the other, creating a composite pattern.

The relationship can change during a piece. Two independent lines might gradually synchronise, then separate again. That change itself can become a formal event.

### 3.3 Electronic counterpoint without traditional harmony

Try three layers:

- low layer: long notes or sparse bass attacks;
- mid layer: short pitched gestures with a distinct rhythm;
- high layer: unpitched ticks or granular fragments.

Give each layer a different cycle length, phrase boundary, and envelope family. Then choose a few moments where they align. Their occasional alignment becomes more meaningful because they are not always moving together.

### 3.4 Voice leading as continuity across changing harmony

Voice leading is the movement of individual pitch lines between harmonic states. Even in non-functional harmony, smooth or purposeful voice leading helps chords feel related.

For each chord change, inspect:

- common tones that can remain fixed;
- semitone or whole-tone movement that creates a smooth transition;
- contrary motion, where parts move in opposite directions;
- oblique motion, where one part holds while another changes;
- registral displacement, where a voice jumps to a new octave or range;
- voice crossing, where one line moves above another.

A chord sequence need not follow traditional functional harmony to benefit from coherent line movement. Conversely, deliberately rough voice leading can create rupture, mechanical instability, or emotional distance.

### 3.5 A practical voice-leading algorithm

For two chords represented as pitch lists, a simple heuristic is to find the assignment of notes that minimises total movement, optionally penalising voice crossings or large leaps. For small chord sizes, brute-force permutations are sufficient; for larger orchestration problems, use an assignment algorithm such as the Hungarian method.

A simple objective might be:

`cost = Σ |next_pitch[i] - current_pitch[assignment(i)]| + λ × crossing_penalty + μ × leap_penalty`

The cost function is a design choice. It is not an objective measure of musical beauty.

## 4. Pitch organisation beyond key and scale

The original guide introduces modal loops, pedal tones, pitch sets, and spectral harmony. This section adds a practical system for building a pitch language that can be used by a composer or algorithm.

### 4.1 Separate pitch vocabulary from pitch hierarchy

A **pitch collection** states which pitches are available. A **pitch hierarchy** states which pitches feel stable, prominent, tense, or transitional.

A piece may use a limited collection but still create hierarchy through duration, register, repetition, bass emphasis, phrase position, and timbre. A pitch does not become a tonic merely because it appears most often; its structural placement matters.

### 4.2 Four useful pitch systems

- **Centred tonal system:** one pitch or chord acts as a perceptual home, even when the harmony is unconventional.
- **Modal or collection-based system:** a restricted pitch collection supplies colour; hierarchy emerges from the bass, motifs, and recurring tones.
- **Intervallic system:** composition is driven by interval relationships (for example, minor seconds and tritones) rather than a named key.
- **Spectral or inharmonic system:** pitch material is derived from partials, resonances, or non-harmonic frequency relationships.

A track can move between systems. A clear bass centre can coexist with an ambiguous upper texture.

### 4.3 Harmonic rhythm

Harmonic rhythm is the rate at which the harmonic environment changes. It is separate from the drum pattern's event rate.

Try contrasting:

- rapid drums + very slow harmonic change;
- a static rhythm + frequent chord colour changes;
- a repeating bass + a slowly shifting spectral pad;
- a short repeated chord + a long phrase in the upper voice.

Changing the harmonic rhythm can create a large structural transformation without changing the percussion.

### 4.4 Detuning and beating

When two nearby frequencies sound together, their interference can create amplitude fluctuations called beating. The approximate beat rate is the absolute frequency difference:

`f_beat = |f_1 - f_2|`

A small difference can create slow warmth or instability; a larger difference may become a distinct roughness or pitch conflict. Detuning should be considered in relation to register: the same difference in hertz produces different musical intervals at different frequencies.

### 4.5 Microtonality as a controlled vocabulary

Microtonality need not mean unrestricted random pitch. Choose a tuning system or a small set of deviations from equal temperament. Define:

- the reference frequency;
- the size of the pitch divisions;
- the mapping from scale degree to frequency;
- whether the bass and percussion follow the same tuning logic;
- how MIDI or synthesis interfaces represent those pitches.

For equal temperament, the frequency of a pitch `n` semitones from a reference frequency `f_0` is:

`f(n) = f_0 × 2^(n/12)`

For a division into `N` equal parts per octave:

`f(k) = f_0 × 2^(k/N)`

This is enough to build a tuning table for a synthesizer or custom sequencer.

# Part III — Time and large-scale form

## 5. Nested time: from sample to whole composition

A composition operates on several timescales simultaneously. A robust arrangement makes these scales interact rather than allowing every event to mutate at once.

| Scale | Typical unit | Compositional role |
| --- | --- | --- |
| Sample | One waveform cycle to a few milliseconds | Timbre, phase, transient, distortion |
| Gesture | Milliseconds to a few seconds | Click, sweep, hit, granular burst |
| Beat | A fraction of a second to over a second | Pulse and groove |
| Bar or cycle | Several beats | Pattern identity |
| Phrase | Several bars or irregular spans | Musical statement and response |
| Section | Tens of seconds to minutes | Contrast and development |
| Whole work | Minutes or longer | Narrative, trajectory, closure |

A common mistake in generative music is to use the same randomisation process at every scale. That produces constant change but little form.

### 5.1 Separate local variation from structural change

- **Microvariation:** velocity, microtiming, filter movement, grain position, or sample selection.
- **Pattern variation:** a changed event sequence or rhythmic accent.
- **Phrase variation:** a changed phrase ending, motif fragment, or register.
- **Section mutation:** a new layer, pitch system, tempo, or orchestration.
- **Formal transition:** a change in the relationship between sections or in the work's overall direction.

Each scale should have its own allowed rate and budget. Microvariation can happen frequently. Formal transitions should be relatively rare and prepared.

### 5.2 Hypermetric organisation

Hypermeter is the perception of bars grouping into larger units. Even if a listener does not count bars, they may recognise a recurring larger pulse: every fourth bar has a stronger accent, every eighth bar introduces a fill, or each 16-bar cycle has a different phrase ending.

This provides a way to create large-scale structure while retaining the same local meter. For example:

- bars 1–3: establish;
- bar 4: small interruption;
- bars 5–7: repeat with one change;
- bar 8: phrase-ending gesture.

The same process can operate across 3, 5, 7, or irregular groups of bars.

### 5.3 Metric dissonance

Metric dissonance occurs when accents, grouping, or recurring cycles conflict with the listener's established metric interpretation. It can be created through:

- accenting weak subdivisions;
- shifting a loop by one or more steps;
- layering different groupings over the same pulse;
- repeating a phrase whose length does not fit the assumed bar;
- changing the perceived downbeat without changing the audio's tempo;
- sustaining a sound across an expected metric boundary.

The goal is not necessarily to make the beat impossible to follow. A useful technique is to keep one layer stable while another creates the conflict.

### 5.4 Swing is a relationship, not a preset

Swing is often described as a long-short subdivision, but actual groove can involve timing, velocity, duration, and accent together.

For a pair of subdivisions, a simple swing ratio is:

`r = duration(first subdivision) / duration(second subdivision)`

A ratio of 1:1 is straight. A ratio greater than 1 lengthens the first subdivision relative to the second. Real performances and programmed grooves are more complex than one ratio: swing can vary with tempo, phrase position, articulation, and instrument role.

**Practical experiment:** Keep the kick on a straight grid, apply a consistent timing ratio to a hat pattern, then change only the velocity accents. Listen for the difference between timing swing and accent swing.

### 5.5 Tempo as a structural parameter

Tempo can remain fixed while perceived speed changes through subdivision density, or tempo can change explicitly. Both are useful.

Methods include:

- gradual tempo acceleration or deceleration;
- abrupt tempo change at a section boundary;
- half-time or double-time reinterpretation;
- metric modulation, where a subdivision in the old tempo becomes the new beat;
- changing the density while leaving BPM constant;
- changing the pulse layer while keeping a background ostinato unchanged.

A tempo map should be composed as deliberately as a harmonic progression. Do not automate tempo simply because the software permits it.

## 6. Long-form architecture and pacing

A track is not necessarily a story with a beginning, conflict, and resolution. It does, however, need a reason for its duration. Long-form architecture concerns how the work spends time and distributes attention.

### 6.1 Four broad formal strategies

1. **Additive form:** the piece accumulates layers or parameters until a new state is reached.
2. **Subtractive form:** material is progressively removed, fragmented, or exposed.
3. **Transformational form:** a small set of materials changes identity over time.
4. **Episodic form:** contrasting scenes or systems are placed in sequence, connected by recurring motifs or transitions.

A composition can mix all four.

### 6.2 Energy is not loudness

Perceived energy can be influenced by:

- event density;
- transient sharpness;
- register and spectral brightness;
- rhythmic regularity or instability;
- low-frequency weight;
- harmonic tension;
- degree of foreground activity;
- spatial width and perceived distance;
- rate of change.

A quiet, high-density passage can feel intense. A loud sustained drone can feel static. Design an energy curve using several dimensions rather than relying only on the master fader.

### 6.3 Tension and release need not be tonal

Tension can be built with:

- increasing density;
- shortening the gaps between events;
- narrowing the available pitch range;
- increasing register or spectral brightness;
- reducing the listener's access to the anchor;
- holding a sound beyond its expected duration;
- repeating an incomplete phrase;
- increasing instability in timing or tuning;
- moving an important layer into the background.

Release can come from the opposite operations, but it can also come from a new stable pattern, a return of a familiar timbre, or the restoration of a spatial reference.

### 6.4 Design transitions as musical events

A transition is not merely a crossfade. It is a designed change in the listener's interpretation of the material.

| Transition type | Operation | Useful result |
| --- | --- | --- |
| Additive | Introduce a new layer before removing the old one | Continuity and expansion |
| Subtractive | Remove a defining layer | Exposure, suspension, reorientation |
| Rhythmic | Change cycle, accent, subdivision, or pulse | New movement without requiring new timbre |
| Harmonic | Alter bass centre, pitch collection, or chord colour | Emotional or tonal redirection |
| Timbral | Resynthesize, filter, distort, or re-orchestrate an existing motif | Identity preserved through sound change |
| Registral | Move material into another range | Change of weight or perspective |
| Spatial | Change distance, width, movement, or reverberant field | Change of environment |
| Temporal | Stretch, compress, pause, or accelerate | Reframing of time |
| Textural | Move from discrete events to continuous sound, or the reverse | Change of perceptual scale |
| Interruptive | Cut, glitch, silence, or abrupt scene switch | Shock, punctuation, deliberate fracture |

A strong transition often carries material from the previous section into the next. For example, the last snare transient may be stretched into the opening noise of the new section.

### 6.5 A transition design sheet

For every major transition, specify:

- what the listener expects before the transition;
- what stays continuous;
- what changes first;
- what changes last;
- whether the change is prepared or abrupt;
- whether the next section is a return, mutation, contrast, or consequence;
- which sound marks the new state.

This is especially useful for generative arrangements: a transition should be represented as a planned operation, not left to coincidental changes in random patterns.

### 6.6 Endings are a compositional problem

A generated piece can continue indefinitely. A finished composition cannot. The system therefore needs an exit strategy.

Possible endings:

- **Cadential:** a pitch, phrase, or rhythmic gesture feels settled.
- **Dissolving:** elements lose density and decay into a residual field.
- **Truncated:** the piece stops while expectation remains active.
- **Return:** opening material reappears with a changed meaning.
- **Transformation:** the main motif becomes a final texture, drone, or noise object.
- **Open ending:** the material stops without resolving its harmonic or formal question.

Choose an ending before the final minutes are generated. Otherwise the system may create an endless middle without a convincing destination.

# Part IV — Electronic orchestration and sound construction

## 7. Orchestration as role design

Orchestration is the practice of deciding which sounds perform which roles, how they interact, and how their identities change. It is not limited to acoustic instruments. A software instrument, a field recording, a resampled click, and a feedback process can all act as orchestral voices.

### 7.1 Build a role inventory before a track inventory

Start with functional roles:

- **Pulse anchor:** makes the temporal reference legible.
- **Low-frequency foundation:** provides weight, pitch centre, or low rhythmic motion.
- **Primary rhythmic voice:** carries the main groove or break.
- **Counter-rhythm:** creates independent motion or metric tension.
- **Motif voice:** provides recognisable melodic, rhythmic, or timbral identity.
- **Harmonic field:** creates pitch atmosphere and continuity.
- **Noise/texture voice:** provides friction, grain, or environmental depth.
- **Transition voice:** marks, prepares, or carries a section change.
- **Spatial bed:** creates the perceived environment.

A single sound can perform multiple roles, and one role can be distributed across several sounds.

### 7.2 Assign spectral and registral zones

A rough orchestral map can divide the frequency spectrum into functional territories:

| Region | Common role | Common risk |
| --- | --- | --- |
| Sub-bass | Physical weight, fundamental, slow movement | Excess duration, poor translation, phase interaction |
| Bass | Pitch identity, rhythmic propulsion | Masking with kick or low synth harmonics |
| Low-mid | Body, warmth, resonant movement | Accumulation and boxiness |
| Midrange | Pitch identity, motif, intelligibility | Congestion and competition for attention |
| High-mid | Attack, definition, articulation | Fatigue and brittle transients |
| High | Air, noise, ticks, spatial detail | Harshness, hiss, excessive activity |

These are descriptive zones, not hard EQ bands. The perceived role depends on source, pitch, envelope, playback system, and arrangement.

### 7.3 Register is a compositional parameter

Moving a motif up or down changes more than pitch. It can alter its perceived size, distance, urgency, and relationship to the bass. Register changes can therefore function as formal mutations.

Try keeping the exact rhythm and interval contour while moving the motif through three registers. Then keep the register fixed and change only the articulation. These two experiments isolate the effect of orchestration from the effect of musical content.

### 7.4 Articulation and envelope define behaviour

A sound source can assume different roles through its amplitude and spectral envelope:

- a short attack and short decay reads as a transient or punctuation;
- a slow attack can become a swell or pad;
- a resonant decay can create a pitched tail;
- a gated sustain can create mechanical insistence;
- a long release can connect separate events into a continuous texture;
- a sharp spectral transient over a soft amplitude envelope can create a bright but non-percussive sound.

Use articulation to differentiate layers even when they share a frequency range.

### 7.5 Build a coherent family of sounds

A palette often feels coherent when its elements share one or more characteristics:

- common source material;
- related envelopes;
- similar resonant frequencies;
- shared distortion or resampling history;
- a common spatial environment;
- related pitch or rhythmic language;
- one recurring modulation process.

Coherence does not mean all sounds should be similar. One contrasting sound can become more powerful when the rest of the palette shares a clear identity.

## 8. Synthesis methods as compositional instruments

The original guide names synthesis families but does not explain enough of their mechanisms to help a programmer or composer choose one deliberately.

### 8.1 Subtractive synthesis

Start with a harmonically rich source, such as a sawtooth, pulse, or noise, and remove or reshape spectral content with filters.

Musically useful controls:

- oscillator waveform and octave;
- filter cutoff and resonance;
- filter-envelope amount;
- amplitude envelope;
- oscillator detuning;
- saturation before or after filtering;
- modulation rate and depth.

Use subtractive synthesis when the sound needs a clear, controllable spectral contour. A filter sweep can become a melodic or formal gesture, not just an effect.

### 8.2 Additive synthesis

Construct a sound as a sum of partials:

`x(t) = Σ a_k(t) cos(2π f_k t + φ_k)`

Each partial can have its own amplitude envelope, frequency, and phase. Harmonic partials at integer multiples of a fundamental create a harmonic spectrum; inharmonic partials create bell-like, metallic, or unstable spectra.

Additive synthesis is useful for designing sounds whose overtone structure evolves independently of their perceived pitch. It also provides a direct route from spectral analysis to resynthesis.

### 8.3 Frequency modulation (FM)

A simple sinusoidal FM signal can be written:

`x(t) = sin(2π f_c t + β sin(2π f_m t))`

where:

- `f_c` is the carrier frequency;
- `f_m` is the modulator frequency;
- `β` is the modulation index.

Changing the modulator frequency and index changes the sideband structure. FM can move from smooth pitch modulation to bright, metallic, bell-like, or noisy spectra. In musical systems, the modulator can itself be enveloped or modulated.

Do not think of FM only as a timbre generator. A rhythmic modulator envelope can make one note evolve as a sequence of spectral events.

### 8.4 Wavetable synthesis

A wavetable is a stored waveform or set of waveforms. The oscillator can scan or interpolate across tables, changing spectral content over time.

Useful design choices:

- table topology and harmonic content;
- scan position and speed;
- interpolation method;
- phase behaviour;
- modulation source;
- whether the scan is cyclic, one-shot, stepped, or probabilistic.

Wavetable position can be tied to a phrase-level macro, a note envelope, or an audio-analysis feature. Avoid uncontrolled scanning if the sound must retain a stable pitch or identity.

### 8.5 Granular synthesis

Granular systems operate on small pieces of a source recording. Important parameters include:

- grain duration;
- grain start position;
- overlap and density;
- playback pitch;
- position jitter;
- amplitude window;
- spatial position;
- scan direction and source traversal.

The relationship between grain duration and density determines whether grains sound discrete, overlapping, or continuous. Very short grains can produce noise-like or pitched effects depending on source and repetition; longer grains preserve more of the source's identity.

### 8.6 Physical modelling and resonators

Physical modelling simulates aspects of vibrating objects or resonant systems. Even simplified models can imitate strings, plates, membranes, tubes, and coupled resonators.

A resonator can be treated as an instrument that is excited by another signal. This is particularly useful for IDM-like sound design because one event can excite a complex pitched response. A short click or noise burst can become a metallic or wooden tone without requiring a conventional oscillator melody.

### 8.7 Feedback and nonlinear systems

Feedback, saturation, clipping, waveshaping, and nonlinear filters can create spectra that depend strongly on input level and system state. They are powerful but require headroom and controlled gain.

A feedback system should have:

- defined gain limits;
- a predictable reset or decay behaviour;
- protection against runaway output;
- a clear monitoring path;
- stable parameter ranges;
- a way to freeze or print a useful state.

In a creative system, a runaway process may be musically interesting only if the software remains safe and the output level is controlled.

## 9. Digital audio: the DSP details a composer should know

A programmer building instruments or processing systems needs to understand the limits imposed by sampled audio. These are not merely engineering details; they directly affect sound.

### 9.1 Sample rate and Nyquist frequency

A digital audio signal represents a continuous signal through discrete samples. The sample rate `f_s` determines how often samples are taken. The Nyquist frequency is:

`f_N = f_s / 2`

Frequencies above Nyquist cannot be represented uniquely and may fold into lower frequencies as aliasing. Before downsampling, a signal needs appropriate low-pass filtering. Nonlinear processing can create new high-frequency partials, so distortion and waveshaping can introduce aliasing even when the input signal was band-limited.

**Production consequence:** Oversampling nonlinear stages can reduce aliasing. It costs CPU, so use it where the audible benefit is worthwhile. A deliberately aliased sound can be a valid aesthetic choice, but it should be controlled rather than accidental.

### 9.2 Bit depth and quantisation

Quantisation maps a continuous range of amplitude values to a finite set of representable levels. Reducing bit depth raises quantisation error and can make noise or distortion audible. Dither is used when reducing resolution to decorrelate quantisation error from the signal.

Do not confuse bit-depth reduction with sample-rate reduction. They produce different artefacts:

- bit-depth reduction changes amplitude resolution;
- sample-rate reduction changes temporal sampling and can introduce aliasing.

### 9.3 The FFT is not the sound

The discrete Fourier transform (DFT) describes a finite block of samples in terms of frequency components. The FFT is an efficient algorithm for computing the DFT. A spectrogram generally displays successive short-time spectra.

For an analysis window of `N` samples at sample rate `f_s`, the nominal bin spacing is:

`Δf = f_s / N`

A longer window improves frequency resolution but reduces temporal localisation. A shorter window locates transients more precisely but blurs nearby frequencies. This is a time-frequency trade-off, not a software defect.

Use:

- short windows for transient and rhythmic inspection;
- longer windows for stable pitch and spectral detail;
- multiple window sizes when analysing complex material;
- overlapping frames when smoother time evolution is needed.

Window choice matters because truncating a signal block can cause spectral leakage. A window function reduces edge discontinuities, but changes the shape and resolution of the spectrum.

### 9.4 Phase-vocoder and spectral processing artefacts

Spectral time-stretching often analyses frames, modifies their timing or phase relationships, and reconstructs the signal. Common artefacts include transient smearing, phasiness, loss of attack clarity, and unnatural modulation.

These are not always failures. They can become a sound source. But choose the method according to the material:

- percussive sources usually need transient preservation;
- sustained harmonic sources can tolerate longer analysis windows;
- noisy textures may accept phase incoherence;
- complex polyphonic sources may produce chorusing or blurred attacks when stretched.

### 9.5 Filters: magnitude is only half the story

A filter changes amplitude across frequency, but it may also change phase and transient shape. Different filter topologies can sound different even when their broad magnitude responses are similar.

Understand at least:

- low-pass, high-pass, band-pass, and notch responses;
- cutoff and resonance;
- slope and filter order;
- phase response and group delay;
- stability and coefficient updates;
- modulation smoothing;
- nonlinear or saturating filter behaviour.

A filter is not merely an EQ curve. A resonant filter can become a pitched voice; a changing group delay can alter transient relationships; a filter envelope can generate an independent rhythmic gesture.

### 9.6 Convolution and impulse responses

Convolution combines a source with an impulse response. In audio, an impulse response can represent a room, resonant body, cabinet, or designed filter. Convolution can create realistic spatial signatures or highly artificial transformations.

For a system to remain efficient, long convolution often uses partitioning and frequency-domain methods. For a composer, the key point is that an impulse response is a time- and frequency-dependent imprint, not just a generic reverb preset.

### 9.7 Dynamics processing

A compressor changes gain according to a detector and control law. Its behaviour depends on:

- threshold;
- ratio;
- attack and release;
- knee;
- detector type and sidechain filtering;
- makeup gain;
- peak versus RMS-like detection;
- stereo linking.

The sound of compression is often determined as much by envelope timing as by the ratio. Fast attack may reduce transients; slower attack can preserve the initial click while controlling the body. Release can create pumping or restore level between events.

A limiter is not a substitute for arrangement. A dense section may need less simultaneous material, not more gain reduction.

### 9.8 Stereo, phase, and spatial perception

Stereo is not simply “left versus right.” It uses level differences, time differences, spectral differences, reverberation, and sometimes head-related filtering to suggest position and space.

For every spatial effect, check:

- mono compatibility;
- phase cancellation;
- low-frequency stability;
- correlation between channels;
- whether motion distracts from the rhythmic anchor;
- whether spatial distance supports foreground/background roles.

Keep important low-frequency information stable unless the composition specifically uses moving or phase-based bass.

# Part V — Generative composition as a complete system

## 10. From pattern generator to composition engine

The original guide introduces generators, Markov states, and a high-level software architecture. This section makes the system hierarchical and composition-aware.

### 10.1 Five levels of a generative system

1. **Event generator:** creates notes, hits, grains, automation points, or other local events.
2. **Pattern generator:** organises events into a recurring unit or phrase.
3. **Phrase generator:** selects and transforms patterns over several cycles.
4. **Section director:** controls the relationship between phrases, energy, instrumentation, and formal states.
5. **Composition director:** manages the entire work, including opening, development, transitions, duration, and ending.

A common failure is to make one algorithm control every level. Keep the layers separate so local randomness cannot constantly rewrite the overall form.

### 10.2 Define invariants and mutation permissions

Every generative layer should have:

- an identity or role;
- a set of parameters it may change;
- parameters it must preserve;
- a permitted range;
- a mutation rate;
- a phrase boundary at which it may change;
- a condition under which it should stop changing.

Example:

| Layer | May change | Must preserve | Mutation interval |
| --- | --- | --- | --- |
| Kick anchor | Sample choice, velocity, occasional omission | Main pulse identity | Every 4–8 bars |
| High percussion | Density, timing, sample fragments | Broad phrase cycle | Every bar |
| Bass motif | Register, octave, note duration | Main pitch identity | Every 8 bars |
| Texture | Grain position, filter, stereo motion | Source family | Continuously, slowly |
| Section director | Layer presence, macro energy, phrase type | Overall trajectory | At section boundaries |

The exact intervals are project-specific. The important idea is that mutation permissions are explicit.

### 10.3 Use hierarchical probability

A useful architecture separates probabilities by scale:

- note-level probability chooses whether a small event occurs;
- bar-level probability chooses a fill or pattern variant;
- phrase-level probability chooses a transformation;
- section-level rules choose the next formal state.

Do not let a note-level random number decide a section-level change. Use separate random streams or seeds for each scale so changing the hi-hat probability does not also change the entire arrangement.

### 10.4 Deterministic randomness and seed management

A random seed is useful only if the system uses it consistently. Record:

- master seed;
- per-layer seed or substream identifier;
- generator version;
- parameter state;
- source asset identifiers and hashes where relevant;
- tempo map and timing resolution;
- algorithm configuration;
- manual edits and frozen decisions.

For example, a seed for `bass_phrase_03` should not change simply because a texture generator has added one extra random draw. Use independent random streams per subsystem.

### 10.5 Generate candidates, then select

A strong generative workflow is not always continuous live improvisation. It can generate multiple candidate phrases offline, measure their properties, let a composer audition them, and freeze the selected result.

Candidate evaluation can combine:

- hard constraints: no overlapping note-off errors, valid pitch range, bounded polyphony;
- musical constraints: motif similarity, target density, phrase length, register limits;
- novelty: distance from recent patterns;
- continuity: similarity to the previous phrase;
- contrast: difference from the previous section;
- human review: listening and editing.

A scoring function might be:

`score = w_c × continuity + w_n × novelty + w_g × groove_fit + w_f × formal_fit - w_v × violations`

The weights should be tuned to the musical goal. No numerical score can replace listening.

## 11. Generative methods not covered in the original guide

The original guide already covers Euclidean rhythms, Markov chains, cellular automata, L-systems, fractals, feedback, and stochastic processes. The following methods add different forms of control.

### 11.1 Rule grammars and rewriting systems

A grammar defines musical symbols and rules for expanding or transforming them. A symbol can represent a note, gesture, phrase, or section.

Example abstract grammar:

```text
TRACK  -> INTRO A B A2 EXIT
A      -> ANCHOR + MOTIF + ORNAMENT
B      -> ANCHOR' + COUNTERLINE + TEXTURE
A2     -> MOTIF_FRAGMENT + ANCHOR + MUTATION
INTRO  -> TEXTURE + MOTIF_HINT
EXIT   -> MOTIF_DECAY | HARD_CUT | SILENCE
```

A rewriting rule might change `ORNAMENT` into `ORNAMENT + FILL` after two repetitions. The grammar defines allowed structure; probabilities can choose among permitted alternatives.

This is especially useful when a piece needs recognisable formal logic but should not repeat one fixed arrangement every time.

### 11.2 Constraint-based generation

Constraint-based systems define what is allowed before searching for an outcome.

Possible constraints:

- exact phrase duration;
- maximum event density;
- permitted pitch collection;
- minimum rest between large transient events;
- maximum number of simultaneous voices;
- required motif occurrence at selected boundaries;
- register range per voice;
- no repeated sample more than a chosen number of times;
- transition must preserve at least one identity-bearing element.

A constraint solver can produce valid material, while a separate scoring function ranks candidates. This separation is useful: validity is not the same as quality.

### 11.3 Evolutionary and genetic methods

An evolutionary algorithm can create a population of candidate patterns, evaluate them, retain selected candidates, and mutate or recombine them.

A basic cycle:

1. generate a population;
2. evaluate each candidate against constraints and musical objectives;
3. select a subset;
4. mutate parameters or exchange fragments;
5. repeat until a stopping condition is reached;
6. audition and edit the best results.

Potential genomes include:

- event positions and velocities;
- motif transformations;
- sample IDs and playback parameters;
- automation curves;
- phrase structure;
- layer-presence masks.

Use human-in-the-loop selection. An algorithm can optimise a measurable feature while making the music less compelling. For example, it may maximise syncopation or spectral variety until the result becomes exhausting.

### 11.4 Search and optimisation

Search methods can be useful for selecting patterns that satisfy a compositional brief. Examples include:

- simulated annealing for exploring parameter combinations;
- beam search for expanding phrase candidates while retaining the strongest options;
- dynamic programming for finding a low-cost path through possible states;
- integer or mixed-integer optimisation for constrained event placement;
- Bayesian optimisation for expensive synthesis parameter searches.

These methods are tools for exploration, not artistic authorities. Use them when a search space is too large to inspect manually and the objective can be stated usefully.

### 11.5 Field-based and attractor systems

Instead of choosing each event independently, define a changing field that influences the probability of events across time, register, or space.

For example:

- a slow sine-like control curve raises the probability of high percussion over 16 bars;
- a spatial field attracts grains toward one region of a sample;
- an energy field reduces the number of simultaneous voices as density rises;
- an attractor-like trajectory moves the pitch centre through a bounded region.

The important feature is continuity: nearby states tend to produce related outcomes. This can create coherent evolution without explicit note-by-note programming.

### 11.6 Audio-conditioned generation

Audio analysis can influence new material, but the mapping should be designed around musical function.

Possible conditioning signals:

- onset times to trigger or avoid events;
- RMS envelope to control density or articulation;
- spectral centroid to control brightness;
- chroma to constrain pitch selection;
- spectral flux to identify activity changes;
- beat tracking to estimate a timing reference;
- source separation to isolate material for transformation.

Analysis outputs are estimates, not ground truth. Beat tracking can misidentify half-time or double-time. Chroma can be confused by inharmonic or noisy sounds. Onset detectors can respond to distortion and texture. Always provide smoothing, thresholding, confidence checks, and a manual override.

## 12. The composition director

A composition director is the subsystem responsible for long-range musical decisions. It should not write every note. It decides what kind of musical situation should exist, and delegates local material to specialised generators.

### 12.1 Inputs

- target duration or section plan;
- active scene and phrase index;
- current energy and density;
- recent history of motifs and section states;
- available layers and their current states;
- constraints on repetition and contrast;
- user controls, performance macros, or external signals.

### 12.2 Outputs

- next structural state;
- layer activation/deactivation requests;
- allowed pattern mutations;
- target ranges for density, brightness, instability, and space;
- motif transformation instructions;
- transition preparation;
- exit or ending trigger.

### 12.3 State should have memory

A director that sees only the current bar cannot judge whether a pattern has been repeated too often or whether a transformation has already occurred. Maintain a small history:

- last several phrase types;
- last time each motif appeared;
- most recent section transition;
- current and previous energy states;
- number of consecutive repetitions;
- unresolved formal goals.

This memory can be compact and explicit. It need not be a machine-learning model.

### 12.4 Use hysteresis to prevent state chatter

If a control signal hovers around a threshold, a system may alternate rapidly between states. Hysteresis uses different thresholds for entering and exiting a state.

For example:

- enter `high_energy` when energy rises above 0.72;
- leave `high_energy` only when energy falls below 0.58;
- require the condition to remain true for a minimum duration.

This avoids rapid switching and creates more stable behaviour.

### 12.5 A bounded director example

```python
from dataclasses import dataclass
from enum import Enum


class Scene(str, Enum):
    INTRO = "intro"
    FOUNDATION = "foundation"
    EXPANSION = "expansion"
    MUTATION = "mutation"
    SUSPENSION = "suspension"
    REASSEMBLY = "reassembly"
    EXIT = "exit"


@dataclass
class DirectorState:
    scene: Scene = Scene.INTRO
    phrase_index: int = 0
    energy: float = 0.25
    phrases_in_scene: int = 0
    motif_seen: bool = False
    exit_requested: bool = False


def choose_next_scene(s: DirectorState) -> Scene:
    """Deterministic example: structure is planned, not randomly guessed."""
    if s.exit_requested or s.phrase_index >= 24:
        return Scene.EXIT

    if s.scene == Scene.INTRO:
        return Scene.FOUNDATION
    if s.scene == Scene.FOUNDATION and s.phrases_in_scene >= 2:
        return Scene.EXPANSION
    if s.scene == Scene.EXPANSION and s.phrases_in_scene >= 3:
        return Scene.MUTATION
    if s.scene == Scene.MUTATION and s.phrases_in_scene >= 2:
        return Scene.SUSPENSION
    if s.scene == Scene.SUSPENSION:
        return Scene.REASSEMBLY
    if s.scene == Scene.REASSEMBLY and s.phrases_in_scene >= 3:
        return Scene.EXIT
    return s.scene


def scene_permissions(scene: Scene) -> dict:
    """Return what local generators may do in this scene."""
    permissions = {
        Scene.INTRO:       {"kick": False, "bass": False, "texture": True,  "density": 0.10},
        Scene.FOUNDATION:  {"kick": True,  "bass": True,  "texture": True,  "density": 0.35},
        Scene.EXPANSION:   {"kick": True,  "bass": True,  "texture": True,  "density": 0.58},
        Scene.MUTATION:    {"kick": True,  "bass": True,  "texture": True,  "density": 0.72},
        Scene.SUSPENSION:  {"kick": False, "bass": False, "texture": True,  "density": 0.12},
        Scene.REASSEMBLY:  {"kick": True,  "bass": True,  "texture": True,  "density": 0.48},
        Scene.EXIT:        {"kick": False, "bass": False, "texture": True,  "density": 0.03},
    }
    return permissions[scene]
```

This example intentionally avoids random transitions. First establish a coherent formal path; only then introduce controlled alternatives within that path.

# Part VI — Software design for composers and programmers

## 13. Represent the composition as a score, not as scattered callbacks

The original guide introduces events and separates composition time from audio time. The next step is to define a durable representation that can be edited, serialised, rendered, and reproduced.

### 13.1 Separate musical intent from playback implementation

A musical event should describe what is intended, not how a specific synthesizer happens to implement it.

A useful event schema:

```python
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any


@dataclass(frozen=True)
class MusicalEvent:
    event_id: str
    voice_id: str
    onset_beats: Fraction
    duration_beats: Fraction
    kind: str                 # note, hit, grain, trigger, control, marker
    pitch: float | None = None
    velocity: float = 0.8
    articulation: str = "default"
    parameters: dict[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()
    source_id: str | None = None
    seed: int | None = None
```

A score can also contain:

- tempo map;
- meter and cycle annotations;
- automation lanes;
- scene/section markers;
- asset references;
- generator provenance;
- manual edits;
- render settings.

### 13.2 Use rational musical time where possible

Floating-point seconds are convenient for playback, but repeated arithmetic can accumulate tiny errors. For symbolic music, represent positions as rational beat values:

- `1/4` beat;
- `3/8` beat;
- `5/12` beat;
- `7/16` beat.

A `Fraction` or integer tick grid makes relationships exact. Convert to seconds only at the scheduling or rendering boundary.

For MIDI export, choose a ticks-per-quarter-note (PPQ) resolution that can represent the intended subdivisions. A high PPQ is not a substitute for a well-defined time model; ensure rounding is explicit when converting to a file format.

### 13.3 Separate tempo, meter, and bar numbering

Do not assume that one bar always has four quarter notes. Meter determines the grouping convention; tempo defines the timing of a reference beat; cycle length may be independent of both.

Represent these as separate objects. This makes it possible to support polymeter, changing meter, tuplets, and non-bar-aligned patterns without special-case hacks.

### 13.4 Tempo maps

For constant tempo `B` beats per minute, a beat position `b` maps to seconds as:

`t = 60b / B`

For a piecewise-constant tempo map, integrate each tempo segment up to the target beat. For a continuous tempo ramp, integrate the reciprocal of BPM over beat position. Do not linearly interpolate seconds if the musical meaning requires a linear BPM curve; those are different trajectories.

Store tempo events in the score and centralise conversion. Never let every generator implement its own tempo arithmetic.

### 13.5 Automation is a first-class musical event

A complete score should support continuous control curves as well as discrete notes.

An automation lane needs:

- target parameter and stable identifier;
- unit or normalised range;
- time basis (beats, seconds, or sample positions);
- control points;
- interpolation mode (step, linear, cubic, exponential, custom);
- optional loop or cycle;
- smoothing policy;
- value constraints.

A filter sweep, grain-density curve, panning movement, feedback gain, or section macro is part of the composition. It should be stored, versioned, and editable like other score data.

### 13.6 An event log preserves provenance

A generated event should be traceable to:

- which generator created it;
- which seed or random stream was used;
- which parameters were active;
- which source material it used;
- whether it was manually edited or frozen;
- which score version contains it.

This makes debugging and artistic revision much easier. If a phrase is successful, the composer should be able to reproduce it or intentionally regenerate a related family of versions.

## 14. Scheduling and real-time reliability

A real-time audio system has deadlines. A generator can be artistically interesting but technically unusable if it misses scheduling deadlines or blocks the audio thread.

### 14.1 Distinguish the clocks

A practical system may involve:

- **musical clock:** beats, bars, subdivisions, tempo map;
- **wall clock:** elapsed real time;
- **audio sample clock:** exact sample positions;
- **control clock:** UI, sensor, OSC, or automation updates;
- **render clock:** offline progression through the score.

Do not assume these clocks advance identically.

### 14.2 Block-based and sample-accurate control

Many audio engines process blocks of samples. A block-based parameter update may only take effect at a block boundary. For slow macros this is acceptable; for transient placement, rhythmic gating, or MIDI timing, finer scheduling may be required.

If the host or engine supports sample-offset events inside a block, use them for sample-accurate timing. Otherwise, schedule events ahead of time and interpolate control changes where appropriate.

### 14.3 Audio-thread rules

The audio callback should do bounded work. Avoid:

- disk access;
- network access;
- memory allocation where avoidable;
- blocking locks;
- UI calls;
- unbounded loops;
- expensive parsing;
- unpredictable file loading;
- logging that may block.

Prepare resources on another thread and pass safe updates to the audio engine through bounded, thread-safe mechanisms. Use lock-free queues or carefully designed single-producer/single-consumer queues where they fit the design. Test under load rather than assuming the callback is safe.

### 14.4 MIDI and OSC interoperability

MIDI is useful for note and controller exchange. OSC is useful for structured control messages and networked communication. A robust application should define a protocol rather than sending arbitrary strings.

For each message, specify:

- address or message type;
- argument types and ranges;
- units;
- time basis;
- session or sequence identifier;
- version;
- behaviour when a message is late or missing;
- rate limits;
- reset and panic behaviour.

For networked control, consider latency, jitter, clock drift, and message bursts. Timestamped messages and look-ahead scheduling can reduce timing uncertainty when the receiving engine supports them.

MIDI 2.0 extends the MIDI 1.0 ecosystem with higher-resolution data and more expressive per-note control, while preserving an interoperability relationship with MIDI 1.0. Treat it as a capability to support when the target devices and software justify it, not as a requirement for every project.

### 14.5 State transitions should be atomic

When a scene changes, multiple parameters may need to update together. If the kick changes scene one block before the bass and texture, the listener may hear an unintended intermediate state.

Use a scene-change object or command that groups related changes and applies them at a defined boundary. For example:

```python
scene_change = {
    "apply_at_beat": "64",
    "scene_id": "suspension_02",
    "changes": {
        "kick.enabled": False,
        "bass.enabled": False,
        "texture.density": 0.18,
        "space.send": 0.72,
    },
}
```

The playback engine should validate the command and apply it as one coherent update.

## 15. Testing a generative music system

Software tests cannot determine whether a track is beautiful, but they can detect many failures that waste creative time.

### 15.1 Unit tests for musical logic

Test:

- pattern lengths and cycle boundaries;
- event ordering;
- note-on/note-off pairing;
- valid pitch and velocity ranges;
- density constraints;
- deterministic output for a fixed seed;
- tempo-map conversion;
- export/import round trips;
- transition permissions;
- generator behaviour at minimum and maximum parameter values.

### 15.2 Property-based tests

Instead of testing only one example, define invariants that must hold for many generated cases:

- no event has a negative duration;
- no event falls outside permitted pitch range;
- polyphony never exceeds a configured bound;
- a phrase generator always terminates;
- output is sorted or can be sorted deterministically;
- a fixed seed produces the same result under the same version;
- stopping the engine prevents new note-ons and releases active voices.

### 15.3 Audio regression tests

Render known seeds and compare outputs. Bit-identical output may not always be possible across different hardware, plugins, or floating-point implementations, but you can still compare:

- duration;
- peak and RMS range;
- channel count;
- onset positions within tolerance;
- spectral or loudness summaries;
- presence of silence or clipping;
- expected file metadata.

Keep listening tests in the loop. Regression tests protect technical behaviour, not artistic value.

### 15.4 Stress tests

Try the worst plausible case:

- maximum simultaneous voices;
- dense MIDI and automation bursts;
- multiple high-cost effects;
- large sample banks;
- fast scene transitions;
- long-duration rendering;
- missing assets;
- network interruption;
- CPU spikes and UI interaction during playback.

A reliable instrument should fail gracefully and provide a clear recovery path.

## 16. Generative system usability

The interface should expose musical decisions, not every internal variable.

Prefer controls such as:

- anchor stability;
- rhythmic density;
- syncopation amount;
- motif variation;
- harmonic tension;
- spectral brightness;
- spatial depth;
- mutation rate;
- section contrast;
- generative freedom.

Each macro may control several lower-level parameters, but the mapping should be documented and predictable.

Essential operations include:

- generate candidate;
- audition A/B;
- freeze event or layer;
- regenerate one layer without changing others;
- undo and redo;
- print to audio or MIDI;
- preserve seed and settings;
- bypass generation and play the frozen result;
- save/load a complete project state.

A useful interface should make the system's current state legible. Show the active scene, current phrase, generator status, seed, and any constraint that is preventing a requested change.

# Part VII — From generation to finished composition

## 17. The full composition pipeline

A complete method needs gates between creative phases. The aim is not to make art bureaucratic; it is to prevent a promising generator from replacing the actual work of composition.

### Stage 1 — Define the artistic question

Write one or two sentences describing the work's central tension, emotional temperature, and listening mode. Avoid relying only on genre tags or equipment descriptions.

### Stage 2 — Define the material vocabulary

Choose a restricted family of sounds, pitches, rhythmic cells, and transformations. Write down what belongs to the same world and what should feel foreign to it.

### Stage 3 — Establish an identity-bearing anchor

Create one sound, motif, pulse, or spatial feature that can remain recognisable through transformation. Test it in a sparse arrangement.

### Stage 4 — Compose a small set of related materials

Make at least three contrasting objects:

- a stable object;
- a responsive or answering object;
- an object that can destabilise the first two.

They need not be three tracks or three instruments. They are three compositional functions.

### Stage 5 — Choose the generative method

Use the simplest algorithm that expresses the intended behaviour. A fixed transformation may be better than a Markov chain. A rule grammar may be better than a neural generator. Use randomness only where uncertainty is part of the idea.

### Stage 6 — Generate candidate phrases

Generate several versions with independent seeds. Inspect their timing and event structure, then audition them. Do not automatically accept the first output.

### Stage 7 — Compose phrase relationships

Decide how the materials answer, overlap, interrupt, or transform one another. This is where loop material becomes composition.

### Stage 8 — Design the macro-form

Create a section map and an energy/attention trajectory. Specify what the listener should recognise, anticipate, and notice at each stage.

### Stage 9 — Design transitions and ending

Compose the transitions as explicit operations. Decide how the work ends before the final rendering stage.

### Stage 10 — Orchestrate and automate

Assign foreground, midground, and background roles. Shape registers, envelopes, space, and control curves. Avoid letting all parameters evolve at the same rate.

### Stage 11 — Print and edit

Freeze strong generated outcomes. Resample, slice, replace, rearrange, and manually edit. Treat the rendered material as a new compositional source.

### Stage 12 — Mix, reference, and translate

Balance the roles, check low end, dynamics, mono compatibility, and playback translation. Compare with references at matched perceived loudness where possible.

### Stage 13 — Critical revision

Listen without watching the DAW. Write down moments that feel unclear, overlong, emotionally unconvincing, or unnecessarily busy. Make changes only after identifying the musical problem.

### Stage 14 — Archive the composition

Save the score, seeds, source assets, generator versions, settings, automation, MIDI/OSC mapping, renders, and final export. A generative work should be reproducible enough to revisit later.

## 18. A listening-based evaluation framework

A generated phrase or finished track can be evaluated through several dimensions. Use these as prompts, not an objective ranking system.

| Dimension | Question | Warning sign |
| --- | --- | --- |
| Identity | Can I recognise what makes this piece itself? | Every section sounds unrelated |
| Continuity | Does each change connect to something established? | Mutations feel arbitrary |
| Contrast | Are different states meaningfully different? | The whole track has one intensity |
| Rhythmic legibility | Is there an anchor or intentional reason for its absence? | Complexity obscures all temporal reference |
| Motif development | Does material return with changed meaning? | Repetition is either static or unrecognisable |
| Orchestration | Can the listener distinguish foreground and background? | All layers compete in the same range and time |
| Pacing | Does each section last as long as its idea needs? | Long stretches contain no meaningful development |
| Surprise | Do deviations feel earned or purposeful? | Random changes substitute for form |
| Emotional coherence | Does the sonic behaviour support the intended mood? | Technical novelty has no expressive direction |
| Technical integrity | Are timing, clipping, voice limits, and exports reliable? | Interesting ideas are undermined by preventable faults |

### 18.1 The subtraction test

Mute 20–30% of the layers, one group at a time. Ask whether the piece becomes:

- clearer;
- more focused;
- more emotionally direct;
- less fatiguing;
- easier to follow.

If so, the removed material may be unnecessary or may need a different role. If the track loses its identity, restore the essential layer and remove something else.

### 18.2 The invariance test

Choose the supposed identity of the piece: a bass motif, rhythm, sound family, tuning, or spatial image. Remove or transform other elements. Does the identity survive?

If not, the piece may have no strong organising material yet. That is not necessarily wrong, but it should be a deliberate compositional choice.

### 18.3 The context test

Audition the same generated phrase:

1. alone;
2. after the section that precedes it;
3. before the section that follows it;
4. at a lower density;
5. at a different register;
6. with one important layer removed.

A phrase that sounds compelling alone may be unsuitable in the arrangement. Composition is contextual.

# Part VIII — Practical compositional blueprints

## 19. Four complete starting architectures

These are not style recipes. They are project blueprints that combine musical and computational decisions.

### Blueprint A — Stable machine, unstable surface

**Artistic premise:** a stable pulse continues while increasingly intricate systems emerge around it.

**Materials:** one kick, one bass note or short motif, two percussion families, one high-frequency texture.

**Composition:**

- Establish a two- or four-bar anchor.
- Add a counter-pattern whose cycle is not an integer number of bars.
- Keep the anchor unchanged through the first major section.
- Mutate only the ornament layer for several phrases.
- Remove the kick and let the counter-pattern briefly become the pulse reference.
- Restore the anchor with one altered timbral property.

**Generation:** deterministic anchor, independent seeded random ornament stream, phrase-level cycle rotation, section-level density director.

**Critical question:** does the stable layer remain perceptually useful, or has the surface become so dense that the anchor is functionally hidden?

### Blueprint B — One motif, many identities

**Artistic premise:** a small melodic or timbral object changes identity through orchestration.

**Materials:** a three-to-seven-event motif, three synthesis methods, one harmonic field, one percussion source.

**Composition:**

- Present the motif dry and close.
- Repeat it with changed register and envelope.
- Reharmonise or retune it while preserving rhythm.
- Fragment it into short transient events.
- Reconstruct it as a sustained or granular sound.
- Return the original version at the end, but change its spatial context.

**Generation:** motif transformation matrix, pitch-set constraints, parameter lanes, candidate audition and freeze.

**Critical question:** which features preserve the motif's identity, and which changes make it feel like a new object?

### Blueprint C — A probabilistic environment with a fixed formal path

**Artistic premise:** the local sound world is unpredictable, but the work's large-scale structure is deliberate.

**Materials:** a small sample bank, several event classes, a fixed scene sequence, a controlled pitch vocabulary.

**Composition:**

- Define a formal path before generating events.
- Use local probability for ornaments and sample selection.
- Restrict each scene to a different allowed density and register.
- Introduce one rare event type only after the listener has learned the ordinary vocabulary.
- Prepare an explicit exit state.

**Generation:** independent random streams, grammar-based section director, hard constraints, candidate scoring and freeze.

**Critical question:** does the listener hear a coherent world rather than a sequence of unrelated random events?

### Blueprint D — Audio-reactive composition

**Artistic premise:** the audio signal influences a composition, but the system remains musically stable.

**Materials:** an input signal or analysis file, beat/onset estimate, energy and spectral features, precomposed motifs, bounded macros.

**Composition:**

- Analyse input with several window sizes.
- Smooth and normalise features.
- Map them to a small set of musical macros.
- Keep the macro mappings stable for an entire phrase.
- Let the section director make decisions only at phrase boundaries.
- Provide manual overrides and a fallback when analysis confidence is low.

**Generation:** feature extraction, smoothing, hysteresis, phrase scheduler, scene director.

**Critical question:** does the input influence the work in a perceptible and meaningful way, or does it simply cause the parameters to wiggle?

## 20. A 32-bar composition study

This study is designed to exercise the connective skills missing from a purely loop-based approach.

| Bars | Formal task | Musical task | Generator behaviour |
| --- | --- | --- | --- |
| 1–4 | Presentation | Establish pulse, motif, and sound identity | Deterministic material only |
| 5–8 | Continuation | Add a contrasting rhythmic voice | Ornament variation, anchor fixed |
| 9–12 | Departure | Introduce counterpoint and a different cycle length | Phrase-level transformation |
| 13–16 | First arrival | Align two previously independent layers | Freeze the best candidate alignment |
| 17–20 | Mutation | Alter harmony, register, or spectral identity | One major mutation, not all parameters |
| 21–24 | Suspension | Remove the most obvious pulse layer | Sparse texture generator, slow automation |
| 25–28 | Reassembly | Restore a recognisable motif in a changed role | Reorchestrate and recombine frozen material |
| 29–32 | Exit | Resolve, dissolve, or interrupt the form | Ending state with no new random structural branch |

Treat bar counts as a scaffold. If the musical phrase requires an irregular length, change the plan rather than forcing it into a neat grid.

# Part IX — Exercises for composers and programmers

## 21. Twelve advanced exercises

### Exercise 1 — Figure and ground

Create four layers. Give each a different register, envelope, and role. Make one layer foreground for eight bars, then transfer foreground status to another layer without changing the master volume.

### Exercise 2 — Masking by arrangement

Build two overlapping midrange parts. First solve the conflict with EQ. Then solve it using only timing, envelope, register, and note omission. Compare which version preserves the more interesting sound.

### Exercise 3 — Motif transformation matrix

Write a short motif and create six versions: transposed, inverted, fragmented, augmented, reharmonised, and reorchestrated. Arrange them so the listener can identify the original material.

### Exercise 4 — Counterpoint without chords

Create two independent unpitched percussion lines. Give them distinct phrase lengths and accents. Create only three moments where they align. Make those alignments important to the form.

### Exercise 5 — Voice-leading without functional harmony

Choose three chords from a pitch collection. Connect them using the smallest useful voice movements. Then create a second version that deliberately uses wide leaps and crossing voices. Compare the emotional and spatial effect.

### Exercise 6 — Hypermetric expectation

Create an eight-bar pattern with a phrase accent every fourth bar. After the listener has learned it, move the accent to the third bar while keeping the underlying pulse unchanged.

### Exercise 7 — Energy without loudness

Create a 60-second build using event density, spectral brightness, articulation, and register. Do not increase the master volume. Then create a release without muting every track.

### Exercise 8 — Transition as transformation

Make a transition where the final sound of section A becomes the first sound of section B. Use resampling or synthesis to preserve an audible relationship between the two sections.

### Exercise 9 — Synthesis as orchestration

Create one rhythmic motif using subtractive, FM, granular, and resonator-based synthesis. Arrange the versions as if they were four different instruments playing one part.

### Exercise 10 — DSP window comparison

Analyse the same audio with a short and a long STFT window. Identify which details become clearer and which become blurred. Do not infer that one spectrogram is more correct; each answers a different temporal/frequency question.

### Exercise 11 — Hierarchical generator

Build a generator with separate note-, bar-, phrase-, and section-level processes. Give each an independent seed. Prove that changing the note-level seed does not alter the section sequence.

### Exercise 12 — Freeze and finish

Generate 20 candidate phrases. Select two, edit them manually, and arrange them into a complete 90-second piece with an ending. Do not regenerate the selected phrases after the arrangement stage begins.

# Part X — Reference implementation patterns

## 22. A small musical-time conversion model

The example below uses piecewise-constant tempo segments. It keeps symbolic event positions in beats and converts to seconds only when needed. A production system should extend this to its chosen tempo-ramp model and file format.

```python
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class TempoPoint:
    beat: Fraction
    bpm: float


class TempoMap:
    def __init__(self, points: list[TempoPoint]):
        if not points:
            raise ValueError("At least one tempo point is required")
        self.points = sorted(points, key=lambda p: p.beat)
        if self.points[0].beat != 0:
            raise ValueError("This simple model expects a tempo point at beat 0")
        if any(p.bpm <= 0 for p in self.points):
            raise ValueError("BPM must be positive")

    def beat_to_seconds(self, target: Fraction) -> float:
        if target < 0:
            raise ValueError("Beat position cannot be negative")

        elapsed = 0.0
        for i, point in enumerate(self.points):
            next_beat = (
                self.points[i + 1].beat
                if i + 1 < len(self.points)
                else target
            )
            segment_end = min(target, next_beat)
            if segment_end > point.beat:
                duration_beats = float(segment_end - point.beat)
                elapsed += duration_beats * 60.0 / point.bpm
            if target <= next_beat:
                break
        return elapsed


if __name__ == "__main__":
    tempo = TempoMap([
        TempoPoint(Fraction(0), 120.0),
        TempoPoint(Fraction(32), 96.0),
        TempoPoint(Fraction(48), 128.0),
    ])
    for beat in (Fraction(0), Fraction(16), Fraction(32), Fraction(48), Fraction(64)):
        print(beat, tempo.beat_to_seconds(beat))
```

This model changes tempo only at explicit beat positions. For a continuously ramping BPM curve `B(b)`, elapsed seconds are found by integrating `60 / B(b)` over beat position. Keep that distinction explicit in a full implementation.

## 23. A simple phrase-candidate generator with independent seeds

```python
from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class CandidateEvent:
    step: int
    velocity: float
    sample_id: str


def generate_ornaments(
    *,
    steps: int,
    seed: int,
    density: float,
    samples: tuple[str, ...],
) -> list[CandidateEvent]:
    if steps <= 0:
        raise ValueError("steps must be positive")
    if not 0.0 <= density <= 1.0:
        raise ValueError("density must be between 0 and 1")
    if not samples:
        raise ValueError("At least one sample is required")

    rng = Random(seed)
    events: list[CandidateEvent] = []
    for step in range(steps):
        if rng.random() < density:
            events.append(CandidateEvent(
                step=step,
                velocity=rng.uniform(0.15, 0.55),
                sample_id=rng.choice(samples),
            ))
    return events


def generate_track(seed_map: dict[str, int]) -> dict[str, list[CandidateEvent]]:
    # Each subsystem has its own seed. A change in one layer won't perturb another.
    return {
        "metal": generate_ornaments(
            steps=64,
            seed=seed_map["metal"],
            density=0.18,
            samples=("tick_a", "tick_b", "click_c"),
        ),
        "noise": generate_ornaments(
            steps=64,
            seed=seed_map["noise"],
            density=0.07,
            samples=("noise_a", "noise_b"),
        ),
    }


if __name__ == "__main__":
    arrangement = generate_track({"metal": 17, "noise": 91})
    for layer, events in arrangement.items():
        print(layer, len(events), events[:5])
```

This is intentionally simple. A complete system should also include motif constraints, phrase boundaries, velocity shaping, note durations, event provenance, and candidate evaluation.

# Part XI — Further references and study paths

The original guide already lists historical IDM sources, TidalCycles, Max/Gen, librosa, Euclidean rhythm research, Xenakis, Roads, and introductory granular synthesis. The following references expand the subjects added here.

## 24. Music cognition and expectation

1. Marcus T. Pearce and Geraint A. Wiggins, **“Auditory Expectation: The Information Dynamics of Music Perception and Cognition,”** *Topics in Cognitive Science* (2012). A research overview of expectation and probabilistic models of musical perception. [PubMed record](https://pubmed.ncbi.nlm.nih.gov/22847872/) · [DOI](https://doi.org/10.1111/j.1756-8765.2012.01214.x)
2. Albert S. Bregman, *Auditory Scene Analysis: The Perceptual Organization of Sound*. Foundational work on how listeners group and separate sound streams.
3. David Huron, *Sweet Anticipation: Music and the Psychology of Expectation*. Useful for understanding expectation, surprise, and emotional response.
4. *The Psychology of Music*, edited by Diana Deutsch. A broad reference covering pitch, rhythm, grouping, tonality, and music perception.

## 25. Composition, form, and pitch organisation

1. Fred Lerdahl and Ray Jackendoff, *A Generative Theory of Tonal Music*. A formal account of grouping, meter, and inferred musical structure. [MIT Press](https://mitpress.mit.edu/9780262620499/a-generative-theory-of-tonal-music/)
2. Dmitri Tymoczko, *A Geometry of Music*. A useful bridge between voice leading, harmony, pitch-class space, and mathematical thinking.
3. Dmitri Tymoczko, *Tonality: An Owner's Manual* (2023). A more recent systematic discussion of voice leading, harmony, modulation, melody, and musical grammar. [Oxford Academic](https://academic.oup.com/book/57582)
4. Arnold Schoenberg, *Fundamentals of Musical Composition*. A practical study of motive, phrase, contrast, and formal development. Use it as a compositional resource, not a stylistic prescription for electronic music.

## 26. DSP and synthesis

1. Julius O. Smith III, *Spectral Audio Signal Processing*. Detailed online resource for spectra, windows, STFT, time-frequency analysis, resynthesis, and filter banks. [Online book](https://www.dsprelated.com/freebooks/sasp)
2. Udo Zölzer (ed.), *DAFX: Digital Audio Effects*. Broad treatment of filters, delays, modulation, nonlinear processing, spatial effects, time-frequency effects, and source-filter processing. [Book contents](https://www.dafx.de/DAFX_Book_Page/index.html)
3. Curtis Roads, *The Computer Music Tutorial*. Broad reference for computer music, synthesis, and signal processing.
4. Curtis Roads, *Microsound*. Detailed exploration of granular composition and microsound.
5. Miller Puckette, *The Theory and Technique of Electronic Music*. A practical and conceptual reference for synthesis and DSP. [Online text](https://msp.ucsd.edu/techniques/latest/book-html/)

## 27. Software, timing, and interoperability

 1. [MIDI Association — MIDI 1.0 and MIDI 2.0 specifications](https://midi.org/specs). Official specification resources. MIDI 2.0 extends the MIDI 1.0 system with higher-resolution data and richer per-note expression while maintaining an interoperability path. [MIDI 2.0 overview](https://midi.org/midi-2-0)
 2. [SuperCollider — Server timing and scheduling](https://doc.sccode.org/Guides/ServerTiming.html). Explains logical and physical time, server bundles, timestamps, and latency.
 3. [JUCE — AudioProcessor reference](https://docs.juce.com/develop/classjuce_1_1AudioProcessor.html). Useful for plugin lifecycle and audio-callback considerations.
 4. [Faust documentation](https://faustdoc.grame.fr/manual/introduction/). Describes a functional DSP language and its use in synthesizers, effects, and cross-platform audio applications. [Architecture and sample-accurate control](https://faustdoc.grame.fr/manual/architectures/)
 5. [Ableton Live Manual — Automation](https://www.ableton.com/en/manual/automation/). A practical reference for timeline automation, breakpoint envelopes, and tempo automation. [Clip envelopes](https://www.ableton.com/en/live-manual/12/clip-envelopes/)
 6. [Sonic Visualiser reference](https://www.sonicvisualiser.org/doc/reference/5.2.1/en/). A useful tool for inspecting spectrograms, time rulers, and layers of audio analysis.

---

# Final synthesis: what makes the system compositional?

A pattern generator creates events. A phrase generator creates related events. A section director creates contrast. A composition director manages the work's trajectory. An audio engine makes the result audible. A composer decides what deserves to remain.

The full system therefore needs six interacting capabilities:

1. **Material:** an identifiable vocabulary of sounds, pitches, gestures, and sources.
2. **Grammar:** rules for how the material may relate, repeat, answer, and transform.
3. **Perception:** awareness of what the listener is likely to recognise, expect, and notice.
4. **Form:** a hierarchy of events, patterns, phrases, sections, and endings.
5. **Execution:** reliable scheduling, synthesis, DSP, state management, and reproducibility.
6. **Judgement:** audition, selection, editing, subtraction, and contextual evaluation.

No single algorithm supplies all six. A powerful instrument is usually a collection of small, understandable processes with clearly defined responsibilities.

**The practical target is not maximum generative autonomy. It is maximum useful musical agency: the ability to create, inspect, transform, freeze, arrange, and finish material without losing the identity of the composition.**
