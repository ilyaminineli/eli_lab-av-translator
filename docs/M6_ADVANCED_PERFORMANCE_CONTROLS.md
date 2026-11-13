# M6 — Advanced Performance Controls

**Status:** Initial Performance Macro System implementation is on `m6/performance-macros`. It is not merged to `main` yet. The normal Windows Quality workflow checks Python compilation and Ruff; keyboard, MIDI, OSC, audio-device and live GPU behaviour still require target-machine validation.

## A. Performance Macro System

The Performance Macro layer sits above the existing normalized modulation architecture. It does not introduce a second effect or target engine: each macro publishes a normalized source value that can feed the existing global Modulation Matrix and per-layer performance modifier engine.

### Built-in macros

Every macro has a normalized value in the inclusive range 0–1.

| Macro | Intended control domain |
| --- | --- |
| **CHAOS** | Glitch, rotation, chromatic displacement and feedback motion |
| **DENSITY** | Mosaic/tile density, kaleidoscope slices, text reveal steps and particle emission |
| **DEPTH** | Transform mix, zoom, feedback amount, trails and layer positioning |
| **DECAY** | Feedback persistence, layer-FX mix, particle lifetime and trails |
| **PRESSURE** | Contrast, edge/threshold treatment, distortion and particle forces |
| **FRAGMENT** | Pixelation, pixel sorting, displacement scale, glyph motion and particle spread |

The initial value for each built-in macro is 0.0. Default master and per-layer mappings are installed without replacing operator-authored routes or assignments. The per-layer engine applies mappings only to compatible, unlocked layers. Target settings that require CPU rasterization are deliberately excluded from the default live density mapping; text reveal and particle controls use existing shader/simulation targets.

### Input sources and manual control

A macro can use one continuous input source at a time, or remain in manual mode. The source selector offers available audio-analysis features, normalized transport/rhythm signals, Sonic Pi's `macro.energy` and `macro.cutoff`, and outputs from the Modulator Bank. Modulator Bank outputs are evaluated before macro inputs, so a follower/LFO can feed a macro and that macro can then fan out to multiple targets.

A manual change temporarily takes priority over an assigned continuous source, then the continuous source resumes. The current defaults use 35 ms attack and 260 ms release smoothing. The six macro definitions, source assignments, values, smoothing settings and keyboard shortcuts are saved in project and scene state.

### Keyboard

Each macro has an editable keyboard shortcut. The default shortcuts are:

| Macro | Default shortcut |
| --- | --- |
| CHAOS | `Ctrl+Alt+1` |
| DENSITY | `Ctrl+Alt+2` |
| DEPTH | `Ctrl+Alt+3` |
| DECAY | `Ctrl+Alt+4` |
| PRESSURE | `Ctrl+Alt+5` |
| FRAGMENT | `Ctrl+Alt+6` |

A shortcut toggles its macro between 0.0 and 1.0. It is an endpoint toggle, not a key-pressure or hold-to-modulate control. Shortcuts are application-wide while the main window is active.

### MIDI CC and notes

The existing MIDI Learn workflow includes all six Performance Macro targets. A learned CC or note message can therefore control one macro, which in turn fans out to its configured master and per-layer destinations. MIDI note velocity is normalized to 0–1; note-off is delivered as zero. Existing mapping range, curve and pickup behaviour remains in the MIDI mapping engine.

### OSC and Sonic Pi

The versioned OSC protocol retains the existing `/eli_lab/v1/macro/set` route. After the normal session ID and sequence number, the message carries a macro name and a normalized value:

```text
/eli_lab/v1/macro/set <session_id> <sequence> chaos 0.75
/eli_lab/v1/macro/set <session_id> <sequence> density 0.40
/eli_lab/v1/macro/set <session_id> <sequence> depth 0.60
/eli_lab/v1/macro/set <session_id> <sequence> decay 0.85
/eli_lab/v1/macro/set <session_id> <sequence> pressure 0.50
/eli_lab/v1/macro/set <session_id> <sequence> fragment 0.70
```

The accepted names are `energy`, `cutoff`, `chaos`, `density`, `depth`, `decay`, `pressure` and `fragment`. Existing `energy` and `cutoff` messages continue to feed the M4/M5 control state; the six new names additionally update their corresponding Performance Macro value. OSC macro values are held for at least five seconds or two bars, whichever is longer, matching the existing bar-based freshness policy.

### Persistence and lifecycle

- `.eliav` project files persist macro definitions and input/shortcut settings.
- Performance Scene snapshots capture and restore macro configuration and values alongside the Modulator Bank and modulation routes.
- Performance Sets reuse project serialization, so the same macro setup travels with the set.
- Loading a project or scene sanitizes references to missing Modulator Bank sources.
- Removing a Modulator Bank source clears macros that refer to it.
- The macro engine runs on the application tick. MIDI/OSC callbacks only submit normalized events through the existing bounded event path; they do not mutate Qt widgets, composition state or OpenGL resources.

### Current boundaries

- The first increment provides six built-in macros; it does not provide user-created macro definitions or arbitrary macro graphs.
- Each macro accepts one continuous source at a time. Multi-target fan-out is supported through the existing modulation and layer-modifier engines.
- Keyboard shortcuts toggle between endpoints; they do not provide analog keyboard pressure or key-down/key-up envelopes.
- The current panel exposes source selection and direct value control. Fine-grained input range, input curve, inversion and attack/release editing are not exposed as separate panel controls in this increment.
- Master/layer routing is a set of safe defaults, not a claim that every parameter of every generator is available on every layer.
- Quality CI cannot verify Qt shortcut conflicts, physical MIDI hardware, Sonic Pi rehearsal, shader compilation on the target GPU or projector performance.

## Verification checklist

- [ ] Python compilation and Ruff pass on the PR head.
- [ ] Open a project, change macro source/shortcut/value, save, restart, and confirm the values/configuration restore.
- [ ] Recall a VJ scene and confirm its macro configuration and value state restore.
- [ ] Move one MIDI CC through its range and verify a selected macro and its multiple targets respond; verify MIDI note-on/note-off behaviour.
- [ ] Send all six OSC macro names with valid session/sequence data and verify normalized updates; send out-of-range values and unknown names and verify rejection.
- [ ] Test one audio band, one Sonic Pi macro and one Modulator Bank follower as macro inputs.
- [ ] Verify keyboard toggles do not collide with the application's normal commands.
- [ ] Confirm the default macro controls do not cause per-frame CPU generator rasterization.
- [ ] Run a sustained live test with master feedback, text, legacy particles and Particle System 2.0 on the target Windows GPU.
