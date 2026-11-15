# Windows stability and performance acceptance

This checklist complements the automated regression suite. Automated tests exercise deterministic application logic and Qt widget behavior; they do not replace an interactive Windows/OpenGL/projector soak test.

## Automated coverage

Run the focused stress tests:

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_unified_visual_director.py tests/test_performance_runtime_regressions.py tests/test_ui_performance_stability.py tests/test_session_recovery_and_localization.py
~~~

Run the complete suite:

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
~~~

The focused tests cover:

- Sonic Pi scene-select section mapping and a 1,200-event scene/phrase burst.
- The bounded control-event queue under a 10,000-event burst, including drop accounting and ordered draining.
- 1,001 macro slider value changes without an extra modulation pass per mouse move; modulation is evaluated by the regular performance runtime tick.
- Shared wrapping/growth rules for inspector forms, including AUTO PERF.
- Compact inspector tab labels, Japanese translations and deck/modifier header typography.

## Build and self-check

Create a clean repository-local environment and run the supported build:

~~~powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe .\scripts\build_pyinstaller.py
~~~

The build script installs the build profile, runs pip check, verifies runtime imports, compiles the source, creates the one-file executable and runs the packaged self-check. It writes resolved package versions and the executable SHA-256 to build\pyinstaller-build-report.txt.

The packaged self-check does not initialize an OpenGL context, exercise the projector, enumerate audio devices or run the four video decks.

## Manual operator soak test

Use the actual performance computer, its normal GPU driver and the target display/projector. Start from a saved copy of a known-good project/performance set.

1. **Cold launch and recovery.** Start the executable, confirm the final 絵 icon/title, restore a session with four decks and several generator/effect layers, then close and reopen twice. Confirm playback and live automation remain stopped after session recovery until explicitly started.
2. **Inspector navigation.** Open LAYERS, FX, AUTO, PREVIEW, AUDIO, MOD and TIME repeatedly. Confirm compact labels are readable, full names appear on hover, scrollbars work, and no form label overlaps or clips at the normal and narrower window sizes.
3. **Macro scrubbing.** With a representative composition loaded, drag each of the six macro sliders slowly and rapidly while watching preview FPS and process CPU. Confirm the numeric value responds immediately and there is no sustained frame-rate collapse. Repeat with a source-driven macro and a keyboard shortcut.
4. **Sonic Pi event stream.** Start SONATA and leave transport/bar/scene cues running for at least 10 minutes. Check the application log for rejected control events, tracebacks or repeated warnings. Confirm scene.select no longer reports a _scene_section argument-count error.
5. **Deck and generator stress.** Play four representative H.264 clips. Add geometry, particle, Text Art and overlay layers. Scrub macros and switch inspector tabs while playback continues. Record preview FPS, dropped frames, decode/convert/upload time, CPU and memory at the beginning and end.
6. **Lifecycle cycling.** Stop and restart Performance Mode, stop/restart SONATA, switch workspaces, restore the default layout and reopen the projector. Repeat these transitions several times; confirm no stale status or duplicate transport remains.
7. **Extended soak.** Leave a representative show running for 30 minutes. Compare memory and frame pacing at the start and end, inspect the log, and save the final session.

## Acceptance notes

- Compare results on the same clips, composition, display resolution and GPU driver; otherwise frame-rate comparisons are not meaningful.
- A brief render dip during a source switch or generator raster rebuild is not by itself a crash. Look for sustained degradation, unbounded memory growth, frozen UI, stale GL errors or repeated control-event rejection.
- Keep the application log at %LOCALAPPDATA%\eli_lab\AVTranslator\logs\av-translator.log.
- Record the exact executable SHA-256 from the build report with any issue reproduction.
- Do not treat a green CI run or a successful packaged self-check as a sign-off for GPU, audio loopback, Sonic Pi or projector stability.