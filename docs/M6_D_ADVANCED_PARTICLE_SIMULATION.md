# M6-D — Advanced Particle Simulation

## Status

**D1 + D2 software implementation is on `m6/d1-particle-system-2`, stacked on the C1 branch.** Static quality CI for the initial D1 foundation passed. The path/source-emitter extension awaits a fresh CI run and target-GPU visual validation. The original `particles` procedural field remains unchanged.

## Objective

Preserve the existing `particles` procedural field and introduce a separate `particle_system_2` generator with a GPU-resident particle simulation. Particle System 2.0 is a physics system, not a replacement or rename of the inexpensive legacy generator.

## D1 — General-purpose GPU foundation

### Delivered capability

| Capability | D1 state |
|---|---|
| Point emitter | Implemented |
| Circle emitter | Implemented |
| Rectangle emitter | Implemented |
| Path / polyline emitter | D2 implemented (up to 64 normalized points) |
| Video luminance emitter | D2 implemented |
| Image alpha / luminance silhouette emitter | D2 implemented |
| Contour / edge emitter | D2 implemented |
| Video/image source reformation | D2 implemented |
| Deterministic seed and respawn sequence | Implemented |
| Multiple independent populations | Implemented (1–4 per system) |
| Particle lifetime / respawn | Implemented |
| Initial velocity and random spread | Implemented |
| Acceleration and drag | Implemented |
| Turbulence field | Implemented |
| Attraction / repulsion / orbit force field | Implemented |
| GPU particle trails | Implemented |
| Size over lifetime | Constant, grow, shrink, pulse |
| Per-population individual parameter overrides | D3 |

### Physics and deterministic behaviour

Particles are represented by three GPU state records per particle:

- Position and velocity.
- Age, lifetime, respawn cycle and per-particle size variation.
- Source target position, target-active flag and last source-resampling phase.

A fixed 60 Hz simulation step integrates acceleration, drag, turbulence and the selected radial force field. Render stalls are bounded to four simulation substeps per render; excess elapsed time is capped rather than creating an unbounded catch-up loop.

The spawn sequence uses the configured system seed together with stable particle index, population seed and respawn cycle. Changing the seed, total count or population count rebuilds the initial GPU state. Ordinary continuous control changes update shader uniforms without moving per-particle state through the CPU.

Each system may contain one to four populations. D1 populations share emitter and physics settings but have separate state textures and seeds, stable small emitter offsets, and distinct speed/size/colour variation. This provides layered motion without duplicating all controls in the first UI.

### Resource ceilings

- Maximum 8192 particles per system layer.
- Maximum four active Particle System 2.0 layers per output renderer.
- Maximum 16384 particles total per output renderer.
- Budget is allocated deterministically in composition layer order. If earlier layers consume the budget, later systems are capped or omitted; they do not silently create more GPU state.
- Simulation uses three fixed-size RGBA32F ping-pong texture pairs for state, metadata and source targets.
- Trail accumulation uses two RGBA8 render targets at half output resolution to constrain memory and fill rate.
- Existing video/image source textures are sampled directly by the renderer-local GPU simulation; the particle system does not upload a duplicate source image.
- The editable path is uploaded as a compact RG32F texture only when its points change.
- CPU memory is used only to initialize bounded state buffers and upload the small path definition; per-frame integration, source sampling, respawning, force evaluation and trail accumulation stay on the GPU.

At 8192 particles, position/velocity, metadata and source-target ping-pong state consumes approximately 768 KiB per system, excluding driver overhead. Trail memory is the larger cost: two half-resolution RGBA8 targets use about 4 MiB per 1080p output layer or 15.8 MiB per 4K output layer. Preview and projector each own these resources independently.

### Integration

Particle System 2.0 is a normal composition layer and uses the existing layer transform, opacity, blend mode and layer-effect path. Its settings are stored in `Layer.generator_settings`, so project and VJ Scene persistence use the existing composition serialization. The renderer owns GPU objects; they are never serialized.

The legacy `particles` field continues to use its existing fragment-shader path and its old density/speed/size/spread/trail/mode controls. It is not migrated to Particle System 2.0 automatically.

## D1 + D2 acceptance checks

### Static/software checks

- Python compilation and Ruff pass.
- Legacy `particles` settings and rendering remain unchanged.
- `particle_system_2` settings normalize and clamp count, population count, emitter, physics, force and visual ranges.
- New layers save/reopen through existing composition serialization.
- The CPU generator raster service is not asked to rasterize Particle System 2.0.
- The compositor caps active systems and total particles and releases resources when layers are removed.

### Manual GPU checks

- Point, circle and rectangle emitter shapes are correct.
- Same seed/settings reproduce the same spawn sequence over repeated runs.
- Different populations have independent stable streams and readable colour/size separation.
- Lifetime/respawn, initial direction/spread, acceleration, drag and each force mode behave as expected.
- Turbulence has stable motion at different frame rates and after brief render stalls.
- Size curves and trail persistence produce smooth results without unbounded accumulation.
- Resize, hide/show, remove/re-add and context recreation do not leak GPU objects or leave stale trails.
- Four-deck video playback plus 16384 particles remains responsive at the intended projector resolution.

## D2 — Path, image and video emitters

**Implemented in the current development branch; GPU/visual acceptance remains open.**

- Point, circle and rectangle emitters remain available.
- A path/polyline emitter samples an editable list of up to 64 normalized points from a compact GPU path texture. Emission can follow a selected cardinal direction or the local path tangent.
- Video-luminance emission samples an existing video/overlay layer's GPU texture and preferentially spawns in bright regions.
- Image-silhouette emission supports alpha or luminance maps, allowing transparent PNG overlays as well as opaque grayscale imagery.
- Contour emission measures four-neighbour luminance gradients in the source texture and uses edge strength for candidate selection.
- Source sampling is deterministic per particle/respawn seed. Each spawn checks a bounded 1–16 candidates and applies a configurable threshold.
- Source controls include the chosen video/image layer, map mode, threshold, probe count and resample interval (0.1–10 seconds).
- Sampled source coordinates are mapped through the source layer's position, scale and rotation so emitted particles line up with the footage in the composition.
- Reformation stores each particle's sampled source coordinate as a GPU target. With reform enabled, a spring force pulls particles back toward the source silhouette; targets refresh from the current source frame at the chosen interval, so moving footage can change the shape being reconstructed.
- Missing source textures safely disable source sampling for that simulation step. When no candidate satisfies the threshold, that respawn is suppressed and retried rather than generating a false bright-region particle.

The path points are saved in the layer's generator settings. Source textures remain the renderer's existing layer textures. Particle positions, source targets and trails remain GPU-only and are not written to projects.

### Additional D2 manual checks

- Path, point, circle and rectangle emitters display the expected shape and tangent mode.
- Video brightness thresholding, image alpha/luma silhouette and contour sampling respond to the selected layer texture.
- Reform strength and resample interval pull a dispersed cloud toward the current source mask.
- Source removal or missing frames degrade safely without GPU or application failure.
- Preview and projector use independent but repeatable source-emission and reformation state.

## D3 — Advanced emitter and population authoring

- Per-population emitter, count, colour, lifetime, speed, size and force overrides.
- Per-population curves and modulation/MIDI/OSC targets.
- Additional vector fields, collision/mask forces and more advanced target-shape reformation.
- Optional render-scale, trail-resolution and simulation-quality controls with clear GPU-budget feedback.

## Scope boundary

D1/D2 does not claim per-population independent authoring, dense video motion tracking, codec-level datamoshing or advanced collision/vector-field solvers. Those remain D3 work rather than being approximated as full features.
