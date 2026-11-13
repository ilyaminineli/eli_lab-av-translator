# M2 — Generative Visuals, Typography and Overlays

## Purpose

M2 turns the video mixer into a mixed-media VJ instrument. Generators, still/animated media and ordinary video footage share one composition-layer model. All layers can be ordered, positioned, scaled, rotated, hidden, locked, blended, saved and rendered by preview and projector outputs.

## Generator layers

### Geometry

Transparent procedural patterns rasterized once when settings change:

- Rings, grids, radial constructions, crosshatch and nested polygons
- Spirals, offset-circle moiré and hexagonal grids

Controls include density, line width, primary/accent colours and the common layer transform/opacity/blend controls.

### Text Art

The Text Art layer has two layouts:

- **Single block:** editable multiline text, system typeface, weight, font size, tracking, line spacing, horizontal/vertical alignment, primary/accent colour, outline and shadow.
- **Typographic collage:** each line is treated as a word/phrase fragment. A seeded arrangement varies scale, font weight, rotation, placement and accent colour to form dense editorial/experimental typography compositions.

Text animation is applied in the GPU compositor after the static text texture has been cached. Available behaviours:

| Motion | Behaviour |
| --- | --- |
| Type-on | Horizontal reveal sweep |
| Word / column reveal | Reveal in successive horizontal cells |
| Line wave | Displace text sampling by a wave |
| Glyph jitter | Time-varying local sample jitter |
| Crawl | Vertical texture travel |
| Signal glitch | Sparse horizontal line displacement |
| None | No text-specific motion |

Changing text or typography raster settings updates the cached texture after a short UI debounce. Changing only the animation mode, speed or amount does not invalidate the raster cache. The explicit Apply button remains available.

### Bilingual random text pool

The editor includes reproducible-ready text pools in English, Japanese or bilingual mode. Themes:

- Memory / 記憶
- Body / 身体
- Signal / 信号
- Ritual / 儀式
- Identity / 自己
- Random mix

Generated text is inserted into the editable text field and stored in the project. Regeneration is manual or scheduled by Auto Performance; it never occurs per frame. The repository's local English wordlists and Japanese reading/kanji lists can enrich the curated phrase sets, with the curated pools retained as a fallback. The dictionary checkbox lets the user opt out. Language, theme, fragment count and dictionary preference are saved with generator settings. The collage arrangement uses a saved seed so a saved project retains the same composition until the user requests another random text set.

### Waveform

Procedural signal-like visuals that need no audio device:

- Parallel sine traces
- Lissajous curves
- Orbit patterns
- Radial traces
- Rose curves

Density, amplitude, frequency, line width and two-colour treatment are adjustable. Audio-band modulation remains part of M3.

### Particle Field

A first procedural GPU particle layer is implemented directly in the composition shader. It supports density, size, speed, spread, primary/accent colour and trails, with four motion modes:

- Drift
- Rise
- Fall
- Orbit

The particle field is generated per pixel in the shader. It does not upload a CPU-generated full-canvas bitmap each frame. This is the first M2 particle treatment, not yet a general-purpose physics simulation: emitters from arbitrary geometry/video, particle collisions, acceleration fields, lifetime curves and instanced particle sprites remain future extensions.

## Still and animated-media overlays

Use **+ IMAGE / VIDEO OVERLAY** in the Generators dock or **File → Add Image / Video Overlay**.

An overlay becomes a normal composition layer with a saved source path, media kind, transform, opacity, blend mode, visibility, lock and per-layer effects.

- Still PNG and other Qt-supported still-image formats retain their alpha channel.
- Qt-supported animated image formats are advanced by the image reader using each frame's delay. They loop continuously by default for performance use.
- Video overlays use their own VideoDeck decoder and frame queue.
- Preview and projector outputs receive the same CPU-side frame snapshots; each renderer uploads those revisions into its own GL context.

Animated-image format support depends on the Qt image-format plugins installed with the runtime. If a format cannot be decoded, the overlay import reports the error instead of adding a broken layer. Video support follows the app's PyAV/FFmpeg decoder support.

## Independent per-layer effects

The **LAYERS** dock now includes a selected-layer FX section. Each layer stores its own effect dictionary and can have these treatments independently of the master output grade:

- Monochrome
- Inversion
- Threshold / Xerox
- Posterization
- Hue shift
- Contrast, saturation and brightness
- Scanlines
- RGB separation
- FX enable/bypass and mix

Starting layer presets are Clean, Monochrome, Xerox, Negative, Duotone, Ghost and Tape. These per-layer treatments are applied during GPU composition before the layer blends into the accumulated frame. The master post-process remains available after all layers have been composed.

## Master effects

The master GPU post-process can be bypassed without changing saved parameters. An effect-mix slider blends the treated image with the untouched composition for A/B comparison.

Master controls include exposure, brightness, contrast, saturation, gamma, temperature, tint, hue rotation, vignette, film grain, scanlines, RGB separation, signal glitch, pixelation, posterization, inversion, halftone and solarization.

Available looks: Clean, 16mm Film, VHS / Tape, CRT, Bleach Bypass, Dream Haze, Digital Damage, Halftone Print, Photocopy, Infrared, Cold Steel and Solarized.

## Project and rendering architecture

- core.composition.Layer stores generator settings, per-layer effect settings and overlay source metadata.
- generators.catalog validates generator values and clamps visual/resource ranges.
- generators.rasterizer.GeneratorRasterizer creates transparent RGBA content and caches it by a content fingerprint.
- Text motion-only settings are excluded from the raster fingerprint.
- media.image_overlay.ImageOverlayPlayer decodes still/animated images to stride-safe RGBA frames.
- Video overlays use their own decoder and bounded frame queue.
- core.render_engine.RenderEngine uploads new source/generator revisions per GL context.
- rendering.compositor.Compositor applies transforms, per-layer FX and blends; it generates particle fields and text motion in the shader.
- The master effect pass runs after the full layer stack.

Layer settings and media references are stored in .eliav projects. Older projects load with neutral defaults for the added layer fields.

## Auto Performance integration\n\nAuto Performance can now vary generators, regenerate text pools and mix independent per-layer FX. Generator changes are scheduled separately from footage cuts, layout changes and master looks. Text generation draws from the curated English/Japanese pools plus optional local dictionary files; all results are saved as ordinary generator settings and therefore survive project save/load. Locked layers are excluded from automation.\n\n## Remaining M2 work

- General particle simulation with emitter shapes, lifetime/velocity curves and force fields.
- More compact and densely packed typographic layout solvers, text paths, variable fonts and vertical CJK composition.
- Rich text runs with multiple styles and arbitrary mixed language runs.
- [x] Overlay timing metadata, animated-image playback speed/frame hold and alpha/luma track mattes; scene-sync metadata is persisted for timeline integration.
- [x] Per-layer effect stage ordering, reorder controls, chain save/import and project preset import/export.
- User-defined generator presets and scene banks.
- Auto Performance can periodically vary geometry, waveform, particle and text generator settings, regenerate bilingual dictionary-backed text, and vary enabled per-layer FX presets. Each generator/FX variation has a separate interval; locked layers are never changed. The UI exposes generator/text and layer-FX variation toggles.

Audio reactivity remains M3; Sonic Pi control remains M4.

## M2 effect-chain and overlay close-out

Per-layer FX are stored as ordered stages (maximum eight), rendered top-to-bottom in the shared compositor. Current GPU stages are monochrome, negative, threshold, posterize, scanlines and hue shift. Stage order is project data, so preview and projector consume the same saved chain. The layer panel supports stage add/remove/reorder and saving a chain JSON file. Project preset collections can be imported into composition metadata and exported as JSON. Auto Performance skips a layer's FX for 30 seconds after a manual edit, in addition to respecting the layer lock.

Overlay layers persist source in/out values, speed, frame-hold count, scene-sync intent and a matte source/mode. Animated image overlays use speed and hold settings at decode time. Alpha and luma mattes sample a referenced source texture in the compositor. Video source trimming and scene-clock scheduling remain dependent on the performance timeline introduced in M3; the saved fields provide the compatibility contract.
