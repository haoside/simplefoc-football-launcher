# Frame Support Mode Decision v2

## Decision status

The current mainline remains:

- `frame_support_mode = "triangular_bracket"`

`radial_plate` remains comparison-only.

## Why the decision still holds after integration

After integrating the frame-side support choice directly into the mainline model, the triangular bracket option still reads better because:

1. it continues the load path from the stronger ring web sectors more naturally
2. it better matches the current triangular launcher-head interpretation
3. it avoids making the outer support look like a flat plate simply appended to a radial concept
4. it remains more coherent when the head-to-frame gap is expressed explicitly

## Files

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v10.scad`
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v4.scad`

## Guidance

Unless a specific comparison check requires otherwise, screenshots, reviews, and future iterations should treat the triangular bracket mode as the default frame-side support interpretation.
