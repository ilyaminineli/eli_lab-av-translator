# M6-E — Typography as an Independent Visual Instrument

**Implementation branch:** `m6/e1-typographic-instrument`  
**Current slice:** E1 — rich runs, vertical layout, text paths and GPU texture-space motion  
**Status:** E1 is merged to `main`. Rich runs, vertical layouts, text paths and texture-space shader modes are implemented. Target-Windows visual and GPU validation remains open.

## Goal

Treat Text Art as an authored visual instrument rather than a single string rendered with one font. Typography should support multiple voices within a layer, Japanese vertical composition, spatial paths and time-based motion while retaining the renderer's strict separation between content/layout work and frame-rate animation.

E1 extends the existing text pipeline. It does not replace the asynchronous raster service and does not create GPU resources from the worker thread.

## E1 — Rich composition and animated texture

### Rich text runs

A text layer accepts an optional `text_runs` array. Each run can override:

- Text content.
- Typeface family, pixel size and weight.
- Fill colour and letter spacing.
- Outline colour and width.
- Shadow enablement.

The editor exposes this as a bounded JSON array (maximum 64 runs and 8192 combined characters after normalization). When no runs are supplied, the existing single-style text editor and legacy layout are retained. Each run is shaped/rasterized as part of one immutable CPU snapshot; the resulting image is uploaded independently by each render context.

Example:

```json
[
  {"text":"記憶は", "font_family":"Noto Sans JP", "font_size":180, "font_weight":900, "color":"#F2EEE6"},
  {"text":"まだここにある", "font_size":92, "font_weight":500, "color":"#C35C75", "letter_spacing":3}
]
```

### Japanese and multilingual layout

The advanced layout path supports:

- Horizontal mixed-script flow, including run changes inside the same composition.
- Vertical right-to-left columns (`vertical_rl`).
- Vertical left-to-right columns (`vertical_lr`).
- Practical upright handling for CJK glyph clusters and rotated ASCII alphanumeric clusters.
- Newline-driven column breaks.

This is a practical vertical compositor, not yet complete CJK typography. Full OpenType vertical alternates (`vert` / `vrt2`), script-specific punctuation positioning, ruby annotations, kinsoku line breaking and a comprehensive grapheme/shaping engine remain open.

### Text on paths

Supported path modes:

- `circle`: closed circular path with wrapping.
- `arc`: open arc.
- `custom`: polyline authored as normalized canvas coordinates (x/y from 0 to 1), up to 64 points.

Glyph clusters are placed along a cached path-length sample and rotated to follow the local tangent. Path generation and placement happen in the background raster job; the path is not rebuilt every render frame.

### GPU-side animation

Existing modes remain available: type-on, word/column reveal, line wave, jitter, crawl and signal glitch.

E1 adds:

- Reverse typewriter reveal.
- Dissolve.
- Flicker.
- Character-cell displacement.
- Vertical reveal.
- Scattered glyph-cell movement.
- Segmented collision-style movement.
- Mechanical scrolling.

These modes use existing compositor uniforms and the text texture. Motion-only edits do not invalidate the static text raster or enqueue a CPU raster job. The modes are deterministic functions of texture coordinates and the renderer's animation clock. Text scrolling and mechanical scrolling shift the source through the layer viewport without wrapping the opposite texture edge into view; displaced samples outside the valid texture region are alpha-clipped rather than clamped into stretched edge glyphs.

**Important implementation boundary:** The new E1 animation modes are texture-space/grid treatments. They do not yet provide one GPU instance per glyph. "Character displacement", "scattered glyphs" and "word collisions" are therefore visual approximations, not independent glyph-body simulation. Likewise, reverse typewriter and vertical reveal are wipes over the text texture, not per-character event schedules.

## Pipeline and performance contract

1. UI edits update an editing buffer and committed, normalized layer settings.
2. Text content, rich-run shaping, vertical layout and path placement are captured in an immutable settings snapshot.
3. The shared `GeneratorRasterService` coalesces obsolete requests and performs CPU rasterization on its single worker. It does not create or mutate OpenGL resources.
4. A completed raster is accepted only when its revision and fingerprint are still current.
5. Each output renderer uploads the accepted pixels while its own GL context is current.
6. The compositor evaluates text animation uniforms every frame. It does not invoke the rasterizer for animation-only changes.

The existing raster-rate limit, preview quality, freeze and last-valid-texture recovery remain in effect. Preview and projector textures remain context-local.

## Not implemented in E1

These features require a different representation or an additional workflow; they must not be inferred from the E1 texture modes:

- GPU glyph atlas plus per-glyph instance data.
- Independent per-character position, rotation, scale, alpha and velocity.
- Per-word and per-character start/end timing tracks.
- True glyph-level typewriter, dissolve and entrance/exit scheduling.
- Deterministic character/kanji substitution using a preloaded glyph set.
- Real word-to-word collision/physics.
- Text-fragment emission into Particle System 2.0.
- A dedicated text-only feedback send/return. E1 text is part of the ordinary composition and can enter the existing master feedback path.
- Named, saved typographic composition presets.

## E2 — Glyph-level animation engine

Recommended next slice:

- Build a bounded per-output glyph atlas with stable glyph keys and a texture/SSBO-compatible instance representation appropriate for the project's OpenGL 3.3 target.
- Keep shaping, glyph discovery, atlas packing and text-to-instance generation off the frame loop; update instance data only when content or layout changes.
- Animate glyph transform, alpha, colour and timing in the vertex/fragment shader using a shared clock.
- Add independent character and word schedules, entrance/exit curves, vertical writing reveal, scatter/reform and real deterministic glyph replacement.
- Define explicit fallback for missing glyphs and atlas-capacity overflow.
- Set hard limits for glyph count, atlas dimensions and per-output memory; expose diagnostics and predictable degradation.

E2 should retain a baked-text fallback for text with unsupported shaping/features, and must not create a Python/Qt object per glyph per frame.

## E3 — Presets and typographic signal routing

- Save/load named typographic compositions including runs, writing mode, path and animation configuration.
- Add an explicit text feedback send/return or feedback source selection, with bounded history and per-output ownership.
- Allow text fragments or selected glyph events to drive Particle System 2.0 and modulation targets without coupling their lifecycle to the text editor.

## Acceptance checklist

### Static layout

- [ ] Rich run arrays save, reopen and preserve styles, including Japanese/English mixed runs.
- [ ] Plain-text layers without runs remain backward-compatible and visually unchanged.
- [ ] Empty plain-text field with non-empty rich runs still renders.
- [ ] Vertical RL/LR layout handles kana, kanji, punctuation, Latin words and line breaks without clipping or invalid font state.
- [ ] Circle/arc/custom paths handle short and long text, including wrap/clipping behaviour.
- [ ] Editing rich-run JSON with invalid syntax reports a recoverable UI error and retains the last valid texture.

### Animation and integration

- [ ] Every text animation mode can be selected, changed live and saved in a project.
- [ ] Animation-only changes do not start a raster job; content/layout changes produce one coalesced background job.
- [ ] Preview and projector receive identical settings while keeping separate GL texture resources.
- [ ] Text participates in existing layer effects, transforms, blend modes and master feedback as expected.
- [ ] Rapid edits do not allow stale raster completions to replace a newer text revision.

### Target-machine validation

- [ ] Shader compilation on the target Windows GPU.
- [ ] Fullscreen projector, resize, preview/projector independence and sustained animation.
- [ ] Rich Japanese/English, vertical writing and custom paths at High/Maximum raster quality.
- [ ] 4-deck composition with multiple text layers, other generators, layer FX and master feedback.
- [ ] AUTO PERFORMANCE / Modulation Matrix changes text motion speed, amount and reveal-step density without requesting a CPU raster every frame.
- [ ] Record FPS, render time, upload time, raster duration and dropped frames.

Static compilation/lint CI does not satisfy the target-GPU checklist. Until that rehearsal is performed, E1 should be treated as implementation-ready for review rather than hardware-validated.
