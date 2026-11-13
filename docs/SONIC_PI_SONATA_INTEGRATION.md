# SONATA Expanded — Sonic Pi / AV Translator Integration Notes

## Source inspected

Repository: [`ilyaminineli/sonicpi_eli_lab`](https://github.com/ilyaminineli/sonicpi_eli_lab)  
Patch: [`04_LIVE/SEULPIRLEAMBACY/SONATA_expanded.rb`](https://github.com/ilyaminineli/sonicpi_eli_lab/blob/main/04_LIVE/SEULPIRLEAMBACY/SONATA_expanded.rb)

The M4 sender is installed in the live patch at the musical control points only. It does not instrument the 93 synth/drum loops.

## Musical clock and form

- Tempo: **92 BPM**.
- Meter: **4 beats per bar**.
- Form: **384 bars**, approximately **16 minutes 42 seconds** at 92 BPM.
- Structure: **16 scene changes**, including the final `end` scene.
- The bar clock increments `sp_b_count`, cues `sp_b`, then sleeps for four beats.
- Scene changes update `sp_sc` and `sp_int`, then cue `sp_sc_change`.
- The synchronized macro loop updates `sx_m_e` (energy), `sx_m_c` (filter cutoff) and `sx_macro_phr` (phrase index).
- The local `F:` sample root remains Sonic Pi's responsibility; AV Translator does not index those samples.

## Stable scene IDs and intensities

| Scene ID | Duration | Intensity |
| --- | ---: | ---: |
| `in` | 16 bars | 0.12 |
| `exp` | 24 bars | 0.28 |
| `tm_a` | 24 bars | 0.45 |
| `trns` | 16 bars | 0.34 |
| `dev` | 32 bars | 0.62 |
| `fr` | 32 bars | 0.84 |
| `ssp` | 24 bars | 0.24 |
| `rtrns` | 16 bars | 0.46 |
| `rc` | 16 bars | 0.70 |
| `rc_w` | 40 bars | 1.00 |
| `peak` | 56 bars | 1.00 |
| `intd` | 24 bars | 0.30 |
| `s_s` | 28 bars | 1.00 |
| `rls` | 24 bars | 0.42 |
| `c` | 12 bars | 0.14 |
| `end` | final marker | 0.00 |

`sp_b_count` increments before `sp_b` is cued, so OSC `bar_index` is **1-based**.

## Patch sender configuration

At the top of `SONATA_expanded.rb`, the helper exposes three values:

- `$sp_av_enabled = true` — set to `false` for an audio-only rehearsal.
- `$sp_av_host = "127.0.0.1"` — explicit AV Translator bind address.
- `$sp_av_port = 57121` — match the UDP port shown in the AUDIO / CONTROL dock.

A unique session identifier is generated at patch start from a wall-clock timestamp with a microsecond component; it does not depend on the patch's seeded musical random generator, so rapid restarts receive distinct IDs. A shared sequence counter increments for each outgoing message inside a short mutex-protected sender section, so concurrent musical loops cannot reuse or reorder sequence numbers. The helper uses Sonic Pi's `osc_send(host, port, path, *args)` API and does not depend on Sonic Pi's incoming OSC port. If AV Translator is closed, local UDP sends are harmless; the patch's audio structure and cues continue to run.

## One-button autonomous connection

1. Prepare the composition and choose the local audio source in AUDIO / CONTROL. For actual analysis of the sound playing from Sonic Pi, select the system-loopback device. Choose Sonic Pi macros only to run without local audio capture.
2. Verify the OSC bind address and port. Same-computer use defaults to 127.0.0.1:57121. COPY SONATA SETTINGS copies the address and port lines for the patch.
3. Press PERFORMANCE MODE in the main toolbar. The application starts the OSC receiver automatically, starts the selected local audio capture if requested, installs missing default modulation curves and AUTO PERFORMANCE assignments, and arms phrase-aware automation.
4. Run SONATA_expanded.rb in Sonic Pi. The first transport/start or clock/bar packet switches the mode from ARMED to LIVE and starts AUTO PERFORMANCE. Scene changes and phrase cues then drive visual variations.
5. Watch AUDIO / CONTROL for receiver freshness, audio source state, modulation outputs and AUTO PERFORMANCE status. Stop SONATA to stop automation; press STOP PERFORMANCE MODE to release resources owned by the mode and restore generated mapping baselines.

The mode may also reuse an OSC receiver that was started manually. It will not close a receiver or audio stream that was already running before Performance Mode took ownership. Sonic Pi is an OSC control source, not an audio-device entry: normalized energy/cutoff and transport continue to work without local audio capture, while system loopback adds real audio-band/onset analysis.

For a remote Sonic Pi computer, bind to the AV Translator computer's reachable LAN IPv4 address and set $sp_av_host to the same address. Do not use 127.0.0.1 for a remote sender; loopback only reaches the machine on which the receiver runs.

## Version 1 wire protocol

Namespace: `/eli_lab/v1`. Every event begins with a string session ID and positive integer sequence number. Sequence numbers increase across all event types for one patch run. Restart the patch to generate a new session ID.

| Address | Arguments after session ID + sequence | Event |
| --- | --- | --- |
| `/transport/start` | BPM (float), beats/bar (int) | `transport.start` |
| `/transport/stop` | none | `transport.stop` |
| `/transport/tempo` | BPM (float) | `transport.tempo` |
| `/clock/bar` | 1-based bar (int), BPM (float), beats/bar (int) | `clock.bar` |
| `/scene/select` | scene ID (string), intensity (float 0..1), bar (int; `0` only for the initial pre-clock scene marker, otherwise 1-based) | `scene.select` |
| `/scene/intensity` | intensity (float 0..1) | `scene.intensity` |
| `/macro/set` | name (`energy`, `cutoff`, `chaos`, `density`, `depth`, `decay`, `pressure` or `fragment`), value (float 0..1) | `macro.set` |
| `/cue/trigger` | cue name (identifier) | `cue.trigger` |
| `/source/heartbeat` | none | `source.heartbeat` |

The initial `in` scene is announced before the first clock tick and therefore carries `bar_index=0` as a pre-clock marker; the first `/clock/bar` is bar 1. Every subsequent scene event is emitted after the preceding scene's bar-counted form block and carries the current 1-based bar index. The cutoff normalization is `clamp((sx_m_c - 48.0) / 70.0, 0.0, 1.0)`. Energy is already normalized in the patch. Macro messages are sent once per bar; a phrase cue is sent on four-bar boundaries. The M6 Performance Macro receiver also accepts the six built-in names `chaos`, `density`, `depth`, `decay`, `pressure` and `fragment` on this same route. Each updates its normalized 0–1 macro value and can drive multiple master/per-layer targets. The existing SONATA patch continues to use `energy` and `cutoff`; no change to its 93 loops or its existing sender is required. Bar messages are emitted once per bar, and a separate heartbeat is sent every four bars. The application treats SONATA as clock authority, disables its internal test clock on `transport/start` or, as a packet-loss fallback, the first accepted `clock/bar`, and derives the M3 `transport.phase` modulation source from the most recent bar clock. Macro values feed the existing M3 modulation matrix and the generated M5 routes/modulators, including smoothing, hold, lock, manual-override and intensity-ceiling behaviour.

### M5 Modulator Bank connection

M5 consumes the same M4 signals without changing the OSC protocol or the SONATA patch:

- `macro.energy` and `macro.cutoff` are available as direct layer-modifier sources and as inputs to reusable **Control Follower** modulators.
- Both macros can trigger ADSR envelopes using a configurable normalized threshold.
- Control Followers can be assigned to waveform amplitude/frequency, geometry, text, particles and other compatible layer targets. A follower can drive multiple assignments; no additional OSC message is needed per visual object.
- Follower attack/release smoothing interpolates the once-per-bar SONATA macro updates at the application tick rate.
- A macro source is considered stale after a bounded window (at least five seconds or two current bars, whichever is longer). Stale values are omitted, so follower assignments release to their baselines instead of holding the last received cutoff/energy value.

The 93 SONATA audio loops remain untouched. OSC still carries only the transport, scene, macro and cue intent described above.

For example, an additional live patch can set CHAOS to 0.75 with `/eli_lab/v1/macro/set` followed by its normal session ID, next sequence number, the string `chaos` and a float value `0.75`. The same route accepts the other five built-in macro names. Values outside 0–1 and unregistered names are rejected; OSC macro values remain live for at least five seconds or two bars, whichever is longer.

## Receiver safety and application threading

- Default bind is loopback; binding to another interface is an explicit user choice.
- Only known versioned addresses, exact argument counts, strict OSC types, registered macro names and safe numeric ranges are accepted.
- Session IDs are retained in a bounded 64-session replay history and cannot be reused within that window. Packets from a superseded session and duplicate/out-of-order sequences are rejected.
- Input is rate-limited (60 messages/second by default) and the M3 event queue remains bounded.
- The receiver runs on one dedicated daemon worker. It only creates validated `ControlEvent` objects and submits them to the queue.
- The main application tick drains a bounded number of events, updates performance-control state and applies modulation. Qt widgets, composition state and OpenGL resources are never touched by the OSC worker.
- The AUDIO / CONTROL dock shows listening/live/stale status, last address, active session, accepted/rejected/dropped counts and last packet age.

A lost packet does not block the clock: the next bar or macro packet is handled independently. Malformed datagrams are discarded and counted; the receiver remains available. A stale sender is recovered by restarting SONATA with a fresh session ID. If STOP PERFORMANCE MODE was pressed, arm Performance Mode again before restarting the patch; the mode starts or reuses the receiver automatically.

## Test without Sonic Pi

With AV Translator running and OSC started on loopback port 57121:

    python scripts/osc_test_sender.py --host 127.0.0.1 --port 57121

The script sends start, bar, scene, energy/cutoff, heartbeat, phrase and end events. It is a manual diagnostic sender. The repository's former unit-test suite was removed at the user's request; current CI performs compilation and Ruff checks only.

## Live rehearsal checklist

1. Start AV Translator and press PERFORMANCE MODE. Confirm the receiver is listening on `127.0.0.1:57121` and the mode is ARMED.
2. In Sonic Pi, leave `$sp_av_enabled = true`, verify host and port, then run SONATA. Confirm the mode moves to LIVE.
3. Confirm BPM 92, bar positions 1 through 384, all 16 scene IDs, energy/cutoff movement, four-bar phrase cues and final stop.
4. Stop/restart the patch and confirm the new session is accepted while delayed packets from the prior session are rejected.
5. Press STOP PERFORMANCE MODE and confirm SONATA audio continues. Re-arm Performance Mode, restart SONATA and confirm a fresh OSC session becomes LIVE.

**Validation boundary:** the OSC protocol and sender insertion are implemented. The complete 384-bar performance has not been executed inside Sonic Pi by the current quality workflow; timing and machine-specific rehearsal remain a manual sign-off.
