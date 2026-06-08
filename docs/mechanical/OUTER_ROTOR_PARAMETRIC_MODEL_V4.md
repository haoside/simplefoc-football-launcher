# Outer Rotor Parametric Model v4

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v6.scad`

## New in v4

This refinement turns the ring ears from isolated head-only ideas into a direct part of the full launcher-head concept model.

### Added

1. `use_ring_ears` switch
2. integrated support ears in the full parametric assembly
3. simple outer frame-connection stubs extending from the ears

## Why this matters

The model is now not only showing:

- motors
- ring
- cutouts
- contact zone

It also begins to show:

- how the ring could hand off load into the surrounding support structure

## Added / changed parameters

| Parameter | Meaning | Default |
|---|---|---:|
| `use_ring_ears` | enable ring ears | `true` |
| `ear_w` | ear width | `34` |
| `ear_l` | ear length | `36` |
| `ear_t` | ear thickness | `12` |
| `ear_hole_d` | ear hole diameter | `6.6` |
| `frame_stub_l` | outer support stub length | `70` |
| `frame_stub_w` | outer support stub width | `22` |
| `frame_stub_t` | outer support stub thickness | `10` |

## Review focus

When opening v6, check these items first:

1. whether the ear sectors still coincide with the stronger residual web sectors
2. whether the stub direction is reasonable for later frame connection
3. whether the ring remains visually and structurally understandable after ears and stubs are added
4. whether 6354 still remains the most comfortable motor length in this integrated version
