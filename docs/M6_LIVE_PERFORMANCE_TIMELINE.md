# M6 — Live Performance Timeline

This is subsection C of the separate **M6 — Advanced Performance Controls** workstream. It is distinct from M6-C Advanced Visual Transformations in the broader Advanced VJ Environment roadmap.

**Implementation status:** Merged to `main` in [PR #31](https://github.com/ilyaminineli/eli_lab-av-translator/pull/31), merge commit `c9b9f884`. The Performance Macro System is merged in [PR #30](https://github.com/ilyaminineli/eli_lab-av-translator/pull/30) and is used by the timeline's modulation events. Target-Windows musical rehearsal and projector acceptance remain open.

## Purpose

The Live Performance Timeline is a saved, musical event plan that runs alongside the existing internal or Sonic Pi transport. It adds deliberate structure to a show without replacing AUTO PERFORMANCE or the current generative variation system.

Events are positioned by **bar and beat**, not by video frame or wall-clock timestamp. A show can contain section and phrase markers as well as actions that recall scenes, control decks, change effects, regenerate text, change palettes, drive Performance Macros and cue transitions.

The timeline is an application control-plane service. Clock/network workers only deliver validated events; event actions run through the application tick on the UI thread. They reuse existing deck, scene, EffectSettings, generator, palette and macro APIs.

## Musical position and playback

Each event has:
- A 1-based bar number.
- A 1-based beat number (1–16, checked against the active meter at playback).
- An event type, display label, JSON payload and enabled flag.

The timeline is limited to 512 events and bar positions up to 1,000,000. Events at the same bar/beat execute in their authored insertion order. Events are one-shot during a pass. Rewinding/restarting the transport makes later events eligible again; disarming stops event dispatch without deleting the plan.

### Internal transport

The existing InternalTransport emits bar and beat events. The timeline consumes those positions on the normal application/UI tick. Arming while stopped prepares playback from bar 1. Arming during a running internal show starts from the current position and waits for the next musical position, so it does not unexpectedly replay the current cue.

### Sonic Pi transport

The existing `/eli_lab/v1/clock/bar` message reports a bar index, BPM and beats per bar. The current SONATA integration sends a bar clock rather than one OSC message for each beat. Between bar messages, AV Translator interpolates the beat position from the last received bar timestamp and the reported BPM using the monotonic application clock.

This is musical-clock interpolation, not an exact hardware/MIDI clock or frame-sync guarantee. Event dispatch is bounded by the application tick cadence. A fresh bar packet is expected at least once per bar; timeline interpolation is suspended when the most recent bar packet is older than approximately 1.5 bars. If a timeline is armed before the first external bar packet, the first packet establishes the current song position. Earlier events are treated as elapsed rather than fired as a burst.

Projects persist the event definitions, not the armed state or playback cursor. Opening a project or performance set never starts a timeline automatically.

## Event types

| Event | Behaviour |
| --- | --- |
| `scene_marker` | Descriptive section marker such as INTRO, PEAK or BREAKDOWN. Publishes a marker event and updates the timeline status; it does not recall a VJ scene. |
| `phrase_marker` | Descriptive phrase marker at an authored bar/beat position. |
| `scene_recall` | Recalls an existing VJ Scene Bank scene, with an optional numeric morph duration. |
| `clip_trigger` | Operates one of the four video decks, or loads a media-library asset into the selected deck and applies the requested action. |
| `effect_change` | Applies an existing master effect preset and optional whitelisted EffectSettings overrides. |
| `text_regenerate` | Generates new Text Art content using the selected layer's saved language, theme, count and dictionary settings. Can address a specific Text Art layer, or defaults to the first unlocked Text Art layer. |
| `palette_change` | Applies a named palette to unlocked generator layers. |
| `modulation` | Sets one normalized Performance Macro (0–1) for a specified number of bars. The macro's assigned continuous source can resume after the manual hold. |
| `transition_cue` | Recalls an existing VJ Scene with a configured numeric morph duration. Discrete media/text/generator changes retain the scene bank's current cut policy. |

### Payload examples

The timeline editor shows a type-specific hint and a JSON payload editor. These are representative event payloads:

Scene recall:
```json
{"scene_id": "intro-scene", "morph_seconds": 0.0}
```

Load a media-library asset into deck A and start it:
```json
{"deck_id": "deck_a", "action": "play", "asset_id": "media-asset-id"}
```

Change feedback controls:
```json
{
  "preset_name": "Digital Damage",
  "settings": {
    "feedback_enabled": true,
    "feedback_amount": 0.68,
    "feedback_decay": 0.94
  }
}
```

Regenerate one Text Art layer:
```json
{"layer_id": "text-layer-id", "seed": 20261113}
```

Change palette:
```json
{"palette": "Fuji · 藤"}
```

Drive CHAOS for four bars:
```json
{"macro_id": "chaos", "value": 0.82, "duration_bars": 4}
```

The clip action can be `load`, `play`, `pause`, `hold`, `release`, `restart`, `stop` or `seek`. Supplying an `asset_id` first loads that asset into the selected deck. The current VideoDeck.load implementation autostarts its decoder; use the subsequent deck action to pause/hold/stop as required.

Effect changes accept only known EffectSettings fields and validated enum values. They do not permit arbitrary application attributes or renderer objects.

## Generative variation alongside the timeline

The timeline is intentionally additive. AUTO PERFORMANCE and the Modulator Bank can continue to produce generative variation while the timeline places structural cues around it. For example, a timeline can mark a new section, recall a known composition, change a palette, trigger text regeneration and push a Performance Macro to a new intensity; AUTO PERFORMANCE can continue making its own interval/bar/phrase-aware decisions inside that section.

A marker by itself does not change automation style or lock a section's appearance. Use scene recall, effect, palette, text or macro events when the show needs an explicit state change. Manual deck locks and layer locks remain respected for the corresponding actions.

## Authoring surface

The **LIVE PERFORMANCE TIMELINE** dock provides:
- A sorted bar/beat event list with event type and label.
- Enable/disable checkboxes.
- Bar, beat, event type, label and JSON payload editing.
- Add, update and remove actions.
- ARM / DISARM and REWIND.
- An insertable eight-marker example structure matching bars 1, 17, 33, 49, 65, 81, 97 and 113.

The editor intentionally exposes payload JSON for the first increment instead of adding a large number of type-specific forms. It validates the complete event before saving it and shows type-specific payload guidance.

## Persistence and safety

- Definitions are stored under `app_state.performance_settings.performance_timeline` in the existing project payload.
- Performance sets include the timeline automatically because they reuse the project snapshot.
- Event count, bar/beat, payload size/depth, identifiers, numeric ranges, effect fields, macro IDs, deck IDs and palette names are validated.
- Missing scenes, media assets, decks or Text Art layers produce a skipped-event result rather than terminating timeline playback.
- The cursor and armed state are runtime-only and are not restored from a saved project.
- Timeline actions use existing APIs; they do not directly allocate GL resources or issue renderer commands.

## Current boundaries

- The first increment is bar/beat based. SMPTE timecode, arbitrary millisecond positions, frame-accurate external clock and per-frame authoring are not implemented.
- Sonic Pi beat positions are interpolated between bar packets using the last received BPM. The current protocol does not send every beat as a packet.
- Scene recall reuses the existing scene morph/cut behaviour. Dual-scene crossfades, midpoint switching and fade-through-black are not implemented here.
- Phrase markers are user-authored labels at bar/beat positions; the timeline does not infer musical phrases from audio.
- The timeline can coexist with AUTO PERFORMANCE, but does not yet provide section-scoped automation profiles, nested timelines, conditional branches or generative probability rules per event.
- Target-Windows live musical rehearsal, full SONATA timing, deck/media stress and projector acceptance remain manual validation work. A successful compile/Ruff workflow does not replace those checks.

## Acceptance checklist

- [ ] A timeline can be authored, saved, reopened and edited without resuming playback.
- [ ] Internal transport triggers bar/beat events once and in stable authored order.
- [ ] Sonic Pi bar packets establish a timeline position and beat interpolation advances between bars.
- [ ] Arming mid-show does not replay earlier cues; transport restart/rewind enables a new pass.
- [ ] Disabled events do not execute.
- [ ] All nine event types validate payloads and execute through the application thread.
- [ ] Missing scene/media/layer references are reported and do not stop subsequent events.
- [ ] AUTO PERFORMANCE and macro sources continue operating alongside the timeline.
- [ ] A representative 113-bar show is rehearsed on the target Windows machine with scene, deck, effect, text, palette and modulation events.
- [ ] Timing, late-packet behaviour, manual lock handling, UI responsiveness and projector output are recorded during acceptance.
