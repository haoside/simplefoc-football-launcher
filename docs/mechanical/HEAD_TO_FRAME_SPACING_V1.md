# Head To Frame Spacing v1

## Files

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v9.scad`
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v3.scad`

## Purpose

Turn the head-to-frame relationship from an implied spacing into an explicit model parameter.

## Current parameter

| Parameter | Meaning | Default |
|---|---|---:|
| `head_to_frame_gap` | nominal spacing from outer mount plate to side support plate | `26mm` |

## Why this matters

This spacing becomes the first real handle for discussing:

- wiring / connector room
- bolt stand-off room
- tool access
- ring-to-side-plate interference risk

## Immediate interpretation

`26mm` is a first-pass packaging gap, not a validated fabrication dimension.

It is meant to be large enough to make the head-to-frame relationship legible in CAD while still looking compact.

## Next review focus

1. whether `26mm` is too tight or too loose for actual bolt / spacer / tool access
2. whether the side support plates should stay radial with this gap
3. whether the outer mount plates should merge into the side support plates after one more iteration
