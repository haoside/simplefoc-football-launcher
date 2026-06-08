# Outer Rotor Parametric Model v2

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v4.scad`

## New in v2

This refinement continues from the v3 parametric model and adds visual aids for the next mechanical review loop:

1. **contact band visualization** on the outer rotor shell
2. **contact zone visualization** around the football inside the launcher head
3. **residual barrel webs** between the three cutouts to make remaining ring stiffness easier to judge

## Why this matters

The current risk is no longer only overall packaging. The next practical questions are:

- whether the barrel keeps enough material after opening 3 shell-contact windows
- whether the visible shell contact band sits in the correct height zone against the ball
- whether the short 63xx motor package still leaves enough structure around the ring

## Parameters added in v2

| Parameter | Meaning | Default |
|---|---|---:|
| `contact_band_h` | visible shell contact band height | `22` |
| `residual_web_t` | remaining material web between cutouts | `14` |

## Review focus

When opening this file, check these items first:

1. shell contact band vs. ball position
2. ring cutout width vs. remaining material web
3. bottom-face support intrusion vs. ring envelope
4. whether the launcher head still reads as ring-first, motor-through-cutout-second
