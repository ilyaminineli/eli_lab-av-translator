# M5 Completion & Live Validation Handoff

**Repository:** `ilyaminineli/eli_lab-av-translator`  
**Baseline reviewed:** `main` at `8b518e4e8d07f8c6a87db499ae2fdf0c7f921957` (6 November 2026)  
**Connection topology:** Sonic Pi and AV Translator on the same computer

## Status

**M5 software implementation is merged to main. M5 milestone exit is still open.**

The uploaded Repomix snapshot was reconciled against GitHub. The M5 implementation and documentation files checked—including the OSC receiver, performance-control services, modulation and modifier systems, Modulator Bank, performance UI, text pools, SONATA integration guide, M5 documentation, README and roadmap—match the GitHub `main` blobs at the baseline commit. No unpushed M5 source changes were identified.

This is a documentation handoff, not a claim that the live rehearsal has passed. The full 384-bar SONATA run has not been executed as part of repository CI.

## Same-computer OSC configuration

Use loopback. No LAN address is required.

| Setting | Value |
|---|---|
| AV Translator OSC bind address | `127.0.0.1` |
| AV Translator OSC UDP port | `57121` |
| SONATA `$sp_av_enabled` | `true` |
| SONATA `$sp_av_host` | `"127.0.0.1"` |
| SONATA `$sp_av_port` | `57121` |

Sonic Pi's own incoming OSC port (commonly `4560`) is not the destination for these messages. SONATA sends outbound OSC to AV Translator on port `57121`.

## Live start sequence

1. Launch AV Translator.
2. Open **AUDIO / CONTROL** and confirm the OSC receiver is configured for `127.0.0.1:57121`.
3. Choose **System loopback** if the show needs FFT/audio-band/onset analysis of Sonic Pi's actual output. Choose the macros-only option if SONATA's normalized energy/cutoff controls are sufficient.
4. Press **PERFORMANCE MODE**. Confirm the mode is **ARMED** and the receiver is listening.
5. In Sonic Pi, confirm the three SONATA settings above and run `SONATA_expanded.rb`.
6. Confirm the first accepted transport/start or clock/bar packet changes the mode to **LIVE** and starts AUTO PERFORMANCE.

## Full SONATA rehearsal

SONATA is 92 BPM, 4/4 and 384 bars: approximately **16 minutes 42 seconds**.

During the uninterrupted run, verify:

- [ ] Receiver remains **LIVE**; packet age does not repeatedly cross the stale threshold.
- [ ] BPM reads 92 and bar position advances from 1 through 384.
- [ ] All 16 scene IDs arrive in the documented order, including the final `end` marker.
- [ ] Energy and normalized cutoff values change and feed the modulation system.
- [ ] Four-bar phrase cues trigger phrase-aware AUTO PERFORMANCE.
- [ ] Modulator Bank followers/envelopes/LFOs and compatible per-layer modifiers respond.
- [ ] The visual output remains responsive; no sustained render stalls or unexpected automation freeze.
- [ ] SONATA reaches its final stop event cleanly.

The SONATA sender emits the bar clock and energy/cutoff macros once per bar, with a separate heartbeat every four bars. At 92 BPM, a bar is about 2.61 seconds. The continuous musical clock/macros—not the diagnostic sender—are what should maintain LIVE status during the performance.

## Recovery and ownership checks

After the uninterrupted run:

- [ ] Stop and restart SONATA. Confirm the new session ID is accepted and LIVE resumes.
- [ ] Confirm delayed packets from the superseded session are rejected.
- [ ] Press **STOP PERFORMANCE MODE** while SONATA is playing. Confirm Sonic Pi audio continues.
- [ ] Re-arm Performance Mode, restart SONATA and confirm a fresh session becomes LIVE.
- [ ] Confirm user-authored routes/modifiers and services that were already running are preserved.

## Diagnostic sender is not the rehearsal

`python scripts/osc_test_sender.py --host 127.0.0.1 --port 57121` is a finite protocol/receiver diagnostic. It sends a short sequence and exits. A later STALE state is expected after it stops; that is not a failure of the live SONATA sender.

## Remaining M5 exit gates

| Gate | Current state |
|---|---|
| M4 versioned OSC receiver, validation, session/replay protection and diagnostics | Implemented |
| M5 Performance Mode orchestration and AUTO PERFORMANCE integration | Implemented |
| Modulator Bank and generated per-layer performance modifiers | Implemented |
| SONATA same-computer destination documented | `127.0.0.1:57121` |
| Complete 384-bar SONATA rehearsal | **Not yet validated** |
| Stop/restart and stale-session recovery rehearsal | **Not yet validated** |
| Windows system-loopback reconnect and sustained-session checks | **Pending target-machine validation** |
| Master-output recording and audio/video muxing | **Not implemented** |
| Lenovo / projector output acceptance and frame-pacing validation | **Pending** |
| Windows one-file native build and target-machine acceptance | **Pending** |

The current CI workflow performs Python compilation and Ruff checks. The repository's former pytest suite was removed at the user's request, so a green CI run does not certify runtime, OSC rehearsal, audio-device reconnect or GPU/projector behaviour.

## M5 exit decision

Do not mark M5 fully complete until the recording/audio-muxing scope is either implemented or explicitly descoped by the project owner, and the agreed live/target-machine validation gates have been run and recorded.

Once these gates are resolved, define M6 as a separate milestone with its own scope and acceptance criteria. The current roadmap does not yet define M6 in detail.
