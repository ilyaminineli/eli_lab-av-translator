# M6 — Live Performance and Workspace Integration

## Status

Implemented on `m6/auto-performance-live-particles-4x3-queer-pools`. This follow-up connects the merged C1/D1-D2/E1 capabilities to the existing AUTO PERFORMANCE and modulation systems. Python/ruff and target-Windows GPU validation must be recorded independently; static checks do not establish shader or projector acceptance.

## A. AUTO PERFORMANCE coverage

The existing per-layer modifier engine and global Modulation Matrix remain the routing foundations. New parameters are registered with bounded target ranges rather than added as special-case animation code.

### Per-layer targets

- Particle System 2.0: continuous emission rate, particle radius, lifetime, speed, spread, turbulence, force strength, trail persistence and source-reformation strength.
- Text Art shader motion: speed, amount and reveal-step/column density. These are compositor uniforms; layout and glyph rasterization remain outside the render loop.
- Per-layer FX: mix, monochrome, invert, threshold, posterize, hue, saturation, contrast, brightness, scanlines and chromatic aberration.
- Existing layer transform, opacity, generator and animated-overlay targets remain available.

The global Modulation Matrix also includes bounded numeric targets for C1 master transforms, displacement and feedback: transform mix, kaleidoscope controls, mosaic tile count, pixel-sort amount/threshold, edge extraction, dithering, displacement amount/scale and feedback amount/decay/zoom/rotation/translation/colour shift/distortion/motion warp/datamosh/delay. The new defaults use beat, onset, phrase, energy, cutoff and audio-band sources.

Discrete choices remain operator decisions. AUTO PERFORMANCE does not select a transform mode, choose a displacement source, toggle temporal feedback, freeze history or issue a feedback reset. Numeric routes take effect when the corresponding effect is enabled by the operator.

## B. Particle System 2.0 as a live instrument

### Continuous emission

Particle System 2.0 now exposes a bounded emission rate from 0 to 3000 particles per second, defaulting to 600. A deterministic gate in the fixed-step GPU simulation distributes births over time rather than starting the complete population as a one-shot burst.

The requested rate is divided by the number of independent populations. Emission uses dead/available particle slots, so the existing per-system and per-output limits remain authoritative; no unbounded CPU or GPU allocation is introduced.

### Event routing

AUTO PERFORMANCE can shape live emission and motion with:

- Energy and beat pulses → emission rate.
- Onsets → speed and force accents.
- Low-frequency energy → force strength.
- Cutoff → turbulence.
- Phrase energy → trails and source reformation.
- Beat/downbeat → particle radius.

The editor reflects live modifier values, but pauses its slider synchronisation while a control has focus or is actively dragged. Changes are applied to simulation uniforms without recreating particle state.

### State continuity

The compositor keeps a particle-system instance resident for up to six seconds after its layer becomes temporarily inactive. This is intended for short cuts, brief deck/layer changes and automation transitions. Removing the layer, a render failure, output-context teardown or expiry still releases the GPU resources.

Resource limits remain four active systems and 16384 particles total per output, with at most 8192 particles per system. Preview and projector own independent simulation state in their respective GL contexts.

## C. Wide and 4:3 workspace layout

The main Qt workspace now distinguishes compact layouts by window width and aspect ratio. Its default dock layout uses narrower side columns and a shorter deck region on compact/4:3 windows, and it relaxes dock minimum sizes so the central composition editor remains usable.

The initial window geometry and minimum size are bounded by the available primary-screen area. User-saved dock arrangements are preserved; responsive rebalancing is applied to the built-in default layout and after the operator restores that default.

This changes the editor workspace, not the saved composition dimensions. The compositor's existing `canvas_fit_scale` keeps the project canvas at its configured aspect ratio and letterboxes it into an output whose aspect differs. It does not stretch content or silently rewrite a 16:9 project to 4:3. A separate per-project canvas-aspect selector remains future work.

## D. Queer text pool and dictionary hygiene

Text Art adds a selectable **Queer / クィア** theme in English, Japanese and bilingual modes. Its curated vocabulary includes the word **QUEER**, gender-expression and identity language, pronoun terms, chosen names, chosen family and short self-definition phrases.

English words read from repository dictionary files pass through an additional normalization and denylist check before they enter the random pool. The explicitly curated pool is separate and retains **QUEER**. This filter is a defensive safeguard, not a guarantee of exhaustive moderation: local dictionary files remain editable and should continue to be reviewed by the project maintainer.

## E. Acceptance checklist

### Static / integration checks

- [ ] Python 3.12 compileall passes.
- [ ] Ruff passes.
- [ ] AUTO PERFORMANCE default installation preserves existing custom routes and modifiers.
- [ ] All new modulation target IDs have a matching getter/setter and bounded target specification.
- [ ] Numeric master targets are included in the MIDI learn value snapshot.
- [ ] Continuous emission rate normalizes to 0–3000 and is divided across 1–4 populations.
- [ ] Queer theme survives project settings normalization in all language modes.
- [ ] Existing dictionary files cannot reintroduce known offensive English headwords through random text sampling.

### Manual Windows / GPU checks

- [ ] Test emission at zero, low and high rates over several particle lifetimes.
- [ ] Check that rate remains consistent when population count changes.
- [ ] Confirm beat/onset/energy routes alter emission and motion without resetting the system.
- [ ] Hide/show or cut a particle layer within six seconds and confirm simulation continuity; remove it and confirm cleanup.
- [ ] Enable each master transform / feedback mode and verify its AUTO PERFORMANCE values are visible and musically stable.
- [ ] Verify per-layer FX automation when layer FX are enabled; confirm disabled FX remain bypassed.
- [ ] Confirm text motion and reveal-step targets update without repeated CPU raster jobs.
- [ ] Run text scrolling and mechanical scrolling through multiple loop boundaries; no wrapped edge glyphs or out-of-bounds smearing should appear.
- [ ] Test default workspace and restored custom layouts at 16:9 and 4:3 resolutions.
- [ ] Verify the project canvas is letterboxed, not stretched, when output aspect differs.
- [ ] Check Queer, English, Japanese and bilingual dictionary sampling against maintained repository dictionary files.
- [ ] Run four-deck playback plus Particle System 2.0 and feedback at the target projector resolution; record FPS, GPU memory and dropped frames.

Static CI is necessary but does not replace these target-Windows, OpenGL and projector checks.
