# Side Support Plate Integration v1

## Files

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v9.scad`
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v3.scad`

## Purpose

Integrate the previously isolated side support plate direction directly back into the main launcher-head concept.

## New in this step

1. side support plates now exist inside the main integrated concept model
2. a nominal `head_to_frame_gap` is introduced
3. the head can now be read as:
   - ring
   - ears
   - stubs
   - link plates
   - outer mount plates
   - side support plates

## New parameters

| Parameter | Meaning | Default |
|---|---|---:|
| `use_side_support_plates` | enable side support plates | `true` |
| `head_to_frame_gap` | nominal spacing from outer mount plate to side support plate | `26` |
| `side_plate_w` | side support plate width | `120` |
| `side_plate_h` | side support plate height | `180` |
| `side_plate_t` | side support plate thickness | `8` |
| `side_plate_hole_dx` | side support hole pitch surrogate | `34` |
| `side_plate_hole_dz` | side support hole pitch surrogate | `40` |
| `side_plate_hole_d` | side support hole diameter | `6.6` |
| `side_plate_leg` | side plate leg projection | `70` |

## Why this matters

This is the first revision where head-to-frame spacing becomes an explicit parameter instead of a purely visual implication.

## Next review focus

1. whether `26mm` is a sensible first-pass head-to-frame gap
2. whether side support plate orientation should remain radial in the next revision
3. whether outer mount plates should merge directly into the side support plates in a later cleanup pass
