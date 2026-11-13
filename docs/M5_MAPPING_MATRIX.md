# M5 — Unified Performance Mapping Matrix

The same normalized source/mapping semantics are used by every performance target family. Separate source-specific code must not be added in the renderer or individual generator widgets.

## Inputs

Transport beat/downbeat/phrase pulses, beat/bar phase and scene intensity; audio RMS/peak/low/mid/high/onset/beat confidence; Sonic Pi energy/cutoff; named Modulator Bank sources.

## Target namespaces

| Namespace | Parameters |
| --- | --- |
| `layer.*` | opacity, rotation, scale, position_x, position_y |
| `generator.*` | animation_speed, animation_amount, density, rotation, text_animation_speed, text_animation_amount, font_size, letter_spacing, waveform_amplitude, waveform_frequency, particle_speed, particle_size, particle_spread, particle_trail |
| `overlay.*` | playback_speed, frame_hold |
| `automation.*` | loop/switch probability, cut/segment bounds, layout/effect/generator interval |
| `master.*` | effect parameters exposed by the global Modulation Matrix |
| `macro.*` | named normalized macro controls |

Local layer targets are saved with composition layers. Global effect and automation targets remain in the Modulation Matrix. MIDI addresses stable target IDs. A target is only implemented when it has a registered range, getter/setter, compatibility filter, UI surface and persistence; verification must be documented separately from static CI checks.

## Precedence

1. A locked layer suspends local modulation and automation writes.
2. A manual edit temporarily owns that target.
3. A valid per-layer modifier claims its exact layer target before a selected-layer global route.
4. Global routes own master and automation targets.
5. Releasing a source, disabling/removing a mapping, stopping a set or changing project restores the pre-modulation baseline.
