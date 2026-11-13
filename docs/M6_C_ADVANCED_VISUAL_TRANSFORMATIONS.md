# M6-C — Advanced Visual Transformations

## Objective

Add image-space geometry and temporal processing that turns the compositor into a more expressive VJ instrument. Effects must remain on the GPU, operate after the current layer stack, and keep each output window's OpenGL resources private to its own context.

C is intentionally staged. The first implementation concentrates on the two highest-value foundations identified in the milestone brief: persistent feedback and displacement maps. The initial slice also adds a compact set of geometry and tonal transforms that fit the existing GLSL post pass.

## C1 — GPU geometry and feedback foundation

### Geometry and image transforms

| Control | C1 implementation | Behaviour |
| --- | --- | --- |
| Kaleidoscope | Implemented | Radial wedge folding with slice count, rotation and zoom. |
| Polar coordinates | Implemented | Remaps the rectangular image into angular/radial coordinates. |
| Mosaic / tile | Implemented | Quantizes image sampling to a configurable tile grid. |
| Directional pixel sort | Approximation | Luminance-gated horizontal scan displacement, not a full row/region sorting algorithm. |
| Displacement map | Implemented | Samples another layer's existing source texture as an RG or luma displacement field. |
| Posterize + dithering | Implemented | Extends the existing tonal reduction with an ordered 4×4-style threshold pattern. |
| Edge extraction | Implemented | Four-neighbour luminance-gradient edge pass for graphic/line-based looks. |
| Datamosh-style blocks | Feedback approximation | Time-quantized block displacement of the retained feedback image. |
| Optical-flow distortion | Feedback approximation | Temporal luma-difference and image-gradient-driven warp; not a dense optical-flow solver. |

Geometry transforms can be composed with the existing master colour effects. Displacement maps are selected by layer source ID; selecting OFF or a missing source safely disables the map rather than sampling an unrelated texture.

### Feedback engine

The feedback engine sits after the master post-processing pass:

1. Compose layers into the compositor's existing ping-pong targets.
2. Apply master filters and geometry transforms into a renderer-local post target.
3. Sample the delayed feedback history and combine it with the current post image.
4. Write the new result to the next history texture when not frozen.
5. Present the result to that output window's framebuffer.

The history is a bounded five-texture ring per output context. The selected delay supports the previous frame through three additional frames of delay. This avoids an unbounded temporal queue and all CPU readback/copy paths. Preview and projector outputs have independent history because they do not share GL objects or contexts.

### Feedback controls

| Parameter | Meaning |
| --- | --- |
| Enable | Enables temporal feedback. |
| Amount | Mixes retained imagery with the current composited frame. |
| Decay | Multiplies retained colour on each feedback pass. |
| Zoom / rotation / X-Y offset | Transforms the historical image before it is fed back. |
| Colour shift | Adds an RGB split to the retained image. |
| Distortion | Adds a procedural spatial warp to the history sample. |
| Motion-driven warp | Uses temporal luminance difference and local history gradients to deform the history sample. |
| Datamosh blocks | Applies time-quantized block displacement to retained imagery. |
| Blend mode | Normal, add, screen, multiply or difference. |
| Temporal delay | Selects up to three frames behind the latest completed history frame. |
| Freeze | Stops advancing the stored history while continuing to display the current input combined with the frozen history. |
| Reset | Advances a reset generation; every output context clears its own history on its next render. |

Reset and resize clear the entire ring. Frozen history is not overwritten. Feedback settings are persisted through the existing `EffectSettings` project and VJ Scene serialization; GPU textures, current history index and retained frames are runtime-only.

## Performance and safety constraints

- No CPU image copies or texture readbacks in the feedback loop.
- Feedback buffers are owned and released by the corresponding `Compositor` and GL context.
- The five-texture history ring is allocated lazily on first feedback use; when allocated, it is resized with that output and released with its GL context.
- Raw RGBA8 history storage is approximately 39.6 MiB per 1920×1080 output or 158.2 MiB per 3840×2160 output, before driver overhead. Preview and projector each allocate their own ring only when feedback is enabled.
- History length is fixed and resize-aware; no unbounded frame retention.
- The displacement source is an existing compositor texture. It is never uploaded a second time for use as a map.
- The feedback pass is bypassed when disabled or when amount is zero.
- Freeze does not stop decoders or layer composition; it freezes only the retained feedback memory.
- Reset uses a monotonic generation so both preview and projector clear independently even though the UI action is shared.
- GPU memory cost is proportional to output dimensions and the fixed history length. Validate at the target output sizes before considering larger history.

## Acceptance checks

### Static/software checks

- Python compilation and Ruff pass on the branch.
- Legacy projects load with defaults for all newly introduced transform/feedback fields.
- New fields survive project and VJ Scene round-trip because they are part of the existing `EffectSettings` serialization.
- The preview and projector each allocate, resize and release independent feedback textures.
- Shader samplers use explicit texture units and do not sample from the framebuffer currently being written.
- Missing displacement source and disabled feedback both degrade to the ordinary post pass.

### Manual GPU/visual checks

- Kaleidoscope slice count, rotation and zoom stay centred and stable at 16:9 and non-16:9 output sizes.
- Polar remapping, mosaic, pixel-sort approximation, displacement-map RG/luma modes, edge extraction and ordered dithering produce expected image changes.
- Feedback starts with a clean seed frame, retains trails with decay, and changes predictably with amount/zoom/rotation/translation/colour shift/blend.
- A 0–3 frame temporal delay selects the correct older history slot after the ring fills.
- Freeze holds history while live content continues; unfreeze resumes updates; reset clears immediately on both preview and projector render ticks.
- Resize and context recreation do not preserve stale feedback textures or produce black frames after release.
- Run both outputs simultaneously at the intended projector resolution; monitor GPU memory, render time and dropped frames.

## C2 — Higher-quality image analysis and sorting

- A true directional pixel-sort pass that gathers and orders selected row/column segments by luminance or a chosen channel.
- Better edge extraction (Sobel/Canny-style thresholds), line extraction, contour emphasis and graphic line compositions.
- Dither pattern options and colour-channel/bit-depth control.
- Region masks and sort thresholds with independent X/Y direction, scan length and temporal gating.

## C3 — Motion and temporal composition

- Dense or pyramidal optical-flow estimation, with explicit GPU cost and fallback quality tiers.
- Vector-field displacement, motion trails and directional smears derived from actual frame motion.
- Dedicated datamosh transition modes with keyframeable block size, motion-vector retention and source switching.
- Optional temporal delay beyond the small C1 history ring only after memory/latency profiling.

## C4 — Scene, MIDI/OSC and automation integration

The new settings are included in the existing EffectSettings model, so scenes capture and recall them with other master effects. The live-performance integration now exposes numeric master transform, displacement and feedback parameters as bounded Modulation Matrix / AUTO PERFORMANCE / MIDI targets. Transform-specific values become visible when the corresponding transform mode is selected; feedback parameters take effect when feedback is enabled. Reset and freeze remain explicit operator actions rather than automatic modulation targets.

## Scope boundary

C1 does not claim full optical flow, exact GPU pixel sorting, a dedicated vector-field editor, or an unlimited feedback delay buffer. Those are deliberate later work rather than approximations hidden behind full-effect names.
