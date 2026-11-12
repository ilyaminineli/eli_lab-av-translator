# M6-D — Advanced Particle Simulation

## Objective

Preserve the existing `particles` procedural field and introduce a separate `particle_system_2` generator with a GPU-resident particle simulation. Particle System 2.0 is a physics system, not a replacement or rename of the inexpensive legacy generator.

## D1 — General-purpose GPU foundation

### Delivered capability

| Capability | D1 state |
|---|---|
| Point emitter | Implemented |
| Circle emitter | Implemented |
| Rectangle emitter | Implemented |
| Path emitter | D2/D3 |
| Video luminance emitter | D2 |
| Image silhouette emitter | D2 |
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

Particles are represented by two GPU state records per particle:

- Position and velocity.
- Age, lifetime, respawn cycle and per-particle size variation.

A fixed 60 Hz simulation step integrates acceleration, drag, turbulence and the selected radial force field. Render stalls are bounded to four simulation substeps per render; excess elapsed time is capped rather than creating an unbounded catch-up loop.

The spawn sequence uses the configured system seed together with stable particle index, population seed and respawn cycle. Changing the seed, total count or population count rebuilds the initial GPU state. Ordinary continuous control changes update shader uniforms without moving per-particle state through the CPU.

Each system may contain one to four populations. D1 populations share emitter and physics settings but have separate state textures and seeds, stable small emitter offsets, and distinct speed/size/colour variation. This provides layered motion without duplicating all controls in the first UI.

### Resource ceilings

- Maximum 8192 particles per system layer.
- Maximum four active Particle System 2.0 layers per output renderer.
- Maximum 16384 particles total per output renderer.
- Budget is allocated deterministically in composition layer order. If earlier layers consume the budget, later systems are capped or omitted; they do not silently create more GPU state.
- Simulation uses fixed-size RGBA32F state/metadata texture pairs.
- Trail accumulation uses two RGBA8 render targets at half output resolution to constrain memory and fill rate.
- CPU memory is used only to initialize bounded zeroed state buffers; per-frame integration, spawning, force evaluation and trail accumulation stay on the GPU.

At 8192 particles, position/velocity and metadata ping-pong state consumes approximately 512 KiB per system, excluding driver overhead. Trail memory is the larger cost: two half-resolution RGBA8 targets use about 4 MiB per 1080p output layer or 15.8 MiB per 4K output layer. Preview and projector each own these resources independently.

### Integration

Particle System 2.0 is a normal composition layer and uses the existing layer transform, opacity, blend mode and layer-effect path. Its settings are stored in `Layer.generator_settings`, so project and VJ Scene persistence use the existing composition serialization. The renderer owns GPU objects; they are never serialized.

The legacy `particles` field continues to use its existing fragment-shader path and its old density/speed/size/spread/trail/mode controls. It is not migrated to Particle System 2.0 automatically.

## D1 acceptance checks

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

## D2 — Image- and video-derived emitters

- Video luminance sampling from an existing video/overlay layer texture.
- Brightness-region emission with adjustable threshold, density and sampling cadence.
- Image alpha/luma silhouette emission.
- Contour/edge emission using GPU gradient sampling, with contour-strength controls.
- Particle reformation: use the same sampled source coordinates as target positions so particles can return to the source silhouette.
- Safe handling when the source layer is missing, hidden or temporarily has no uploaded frame.

## D3 — Advanced emitter and population authoring

- Path/polyline emitters and editable path assets.
- Per-population emitter, count, colour, lifetime, speed, size and force overrides.
- Per-population curves and modulation/MIDI/OSC targets.
- Additional vector fields, collision/mask forces and target-shape reformation.
- Optional render-scale, trail-resolution and simulation-quality controls with clear GPU-budget feedback.

## Scope boundary

D1 does not claim path, video-luminance, image-silhouette or contour emitters. It establishes the deterministic GPU physics and trail foundation those emitter modes can use in D2 without introducing CPU particle simulation.
