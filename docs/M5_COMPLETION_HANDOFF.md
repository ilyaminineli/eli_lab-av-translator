# M5 Completion & Live Validation Handoff

**Repository:** `ilyaminineli/eli_lab-av-translator`  
**Baseline reviewed:** `main` at `358dc597c76e9ee11344f5c13c8361667a07fafe` (12 November 2026)  
**M5 feature PR:** [#19 — Separate text editing from asynchronous generator rasterization](https://github.com/ilyaminineli/eli_lab-av-translator/pull/19), merged as `ecc6f86bb896e9c8ff1cd23d083683fdfdef8e14`  
**Quality:** [Workflow #116 passed](https://github.com/ilyaminineli/eli_lab-av-translator/actions/runs/43132442896) on the reviewed `main` head (compile + Ruff only).  
**Connection topology:** Sonic Pi and AV Translator on the same computer.

## Status

**M5 implementation scope is merged to `main`. Code-level CI is green. M5 live-performance acceptance remains open pending target-machine rehearsal. M6 planning/implementation may proceed in parallel.**

The final M5 code review covered the application-owned generator raster service, CPU rasterizer, preview/projector render integration, generator editor controls, Performance Mode/AUTO PERFORMANCE integration, project lifecycle and the PyInstaller local build route. PR #19 is merged; `main` subsequently received the formatting-only commit `358dc597`.

The Quality workflow on that current commit passed Python compilation and Ruff. The repository does not contain the former pytest/unit-test suite. A green Quality run does not execute the GUI, create a real OpenGL context, run Sonic Pi, exercise a Windows audio device or measure projector performance.

## M5 implementation inventory

- One application-owned background generator raster worker shared by preview/projector renderers.
- One active raster job globally and at most one pending snapshot per layer; newer pending work replaces older queued work.
- Monotonic per-layer revisions and static-settings fingerprints; obsolete worker results are discarded before caching/emission and checked again by renderers before texture upload.
- CPU-only raster workers; preview and projector upload their own accepted pixel snapshots while their individual OpenGL contexts are current.
- Separate static typography rasterization and GPU-shader text animation paths.
- Text edit buffer separated from committed layer settings, debounced commit and explicit Apply Immediately.
- Live Preview, commit-on-pause, Draft/Balanced/High/Maximum preview quality, optional 1600×900 final raster, maximum 1–20 Hz text raster rate, Freeze current texture, last-valid-texture fallback and EDITING/RASTERIZING/READY/FAILED/FROZEN status.
- Cached raster replay for a renderer that missed an earlier completion, including preview re-enable/unfreeze.
- Raster invalidation on layer deletion, project reset/load and application shutdown.
- Performance Mode, Modulator Bank, generated per-layer performance modifiers and phrase-aware AUTO PERFORMANCE remain part of the merged M5 foundation.

## Same-computer OSC configuration

Use loopback. No LAN address is required.

| Setting | Value |
| --- | --- |
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

At 92 BPM, a 4/4 bar is about 2.61 seconds. The continuous musical clock/macros—not the diagnostic sender—should maintain LIVE status during the performance.

## Recovery and ownership checks

After the uninterrupted run:

- [ ] Stop and restart SONATA. Confirm the new session ID is accepted and LIVE resumes.
- [ ] Confirm delayed packets from the superseded session are rejected.
- [ ] Press STOP PERFORMANCE MODE while SONATA is playing. Confirm Sonic Pi audio continues.
- [ ] Re-arm Performance Mode, restart SONATA and confirm a fresh session becomes LIVE.
- [ ] Confirm user-authored routes/modifiers and services that were already running are preserved.

## Generator raster / four-deck acceptance

On the target Windows machine, keep all of the following active together:

- [ ] Four video decks playing representative H.264 footage.
- [ ] Multiple text and non-text generator layers.
- [ ] Per-layer effects and master effects.
- [ ] Audio reactivity and/or live SONATA macros.
- [ ] Projector output open on the external display.
- [ ] Continuous rapid typing/pasting of long Japanese and English multiline text.

Record input responsiveness, text raster duration/start rate, preview and projector upload timing, FPS and dropped frames. Verify the latest committed text revision eventually appears on every output and that old revisions never replace it. Exercise Live Preview off/on, Freeze/unfreeze, Apply Immediately at full resolution, a forced raster failure/fallback, layer deletion, project reset/load and output-window close/reopen while raster work is active.

**This stress acceptance has not yet been performed or measured in the repository review.**

## Diagnostic sender is not the rehearsal

`python scripts/osc_test_sender.py --host 127.0.0.1 --port 57121` is a finite protocol/receiver diagnostic. It sends a short sequence and exits. A later STALE state is expected after it stops; that is not a failure of the live SONATA sender.

## Remaining validation and deferred work

| Gate | State on 12 November 2026 |
| --- | --- |
| M4 versioned OSC receiver, validation, session/replay protection and diagnostics | Implemented |
| M5 Performance Mode orchestration and AUTO PERFORMANCE integration | Implemented; live rehearsal pending |
| Modulator Bank and generated per-layer performance modifiers | Implemented; live response rehearsal pending |
| Async generator raster service and text raster controls | Merged; static Quality check passed |
| Full 384-bar SONATA rehearsal | **Not yet validated** |
| Stop/restart and stale-session recovery rehearsal | **Not yet validated** |
| Windows physical input/system-loopback reconnect and sustained capture | **Pending target-machine validation** |
| Four-deck continuous-text stress with effects/audio/projector active | **Pending target-machine validation** |
| Projector hot-plug, frame-pacing and long-duration rehearsal | **Pending target-machine validation** |
| Local PyInstaller executable build and packaged self-check on the build computer | **Not certified by the Quality workflow; run locally** |
| Windows Onefile Build GitHub Actions fallback | Manual-dispatch only |
| Master-output recording and audio/video muxing | **Not implemented; deferred separate delivery item** |

## M5 exit decision and M6 handoff

M5 **implementation** is complete and merged. M5 **live-performance acceptance** is not yet signed off; the checklist above remains an open validation record. The recording/audio-muxing feature is not implemented and is explicitly treated as a separate deferred deliverable, rather than being presented as complete or used to block M6 development.

M6 can begin from the merged M5 baseline while the target-machine validation is completed. Carry the outstanding M5 checks into the performance release checklist and record actual results before claiming hardware readiness.

See [M6 Advanced VJ Environment](M6_ADVANCED_VJ_ENVIRONMENT.md) for the next milestone's initial live-mixer scope.
