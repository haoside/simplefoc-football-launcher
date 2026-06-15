# Outer Rotor 6354 Mainline Freeze v2

## Current mainline choice

The current preferred mechanical mainline for the single-ball launcher concept is:

- `6354`-class short 63-series outer-rotor motor
- `63-series motor fixation/stiffness` is now a first-priority structural topic
- motor axis lines are treated as `centerlines`
- the three motor centerlines form an `equilateral triangle` in one plane
- the three outer-rotor shell working surfaces are tangent to the football
- the launcher head must include `adjustability` to accommodate football diameter variation / environment-related tolerance drift
- `bottom-face mounting only`
- current frame-side support default remains `triangular_bracket`

## Control intent

Mechanical design must support the control goal:

- use `FOC` to vary launch speed
- use wheel-speed / rotor-speed differential to influence final curve / spin behavior

## Mainline model files

### Primary parametric concept
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v4.scad`

### Latest explicit parametric revision source
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v10.scad`

### Ring-focused review model
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_ring_focus_v2.scad`

### Motor placeholder
- `cad/vendor-placeholders/63xx-motor-v2/63xx_outer_rotor_bottom_mount_placeholder_v2.scad`

## Immediate mechanical priority

The next mechanical iteration should prioritize:

1. `63-series motor fixation guarantee`
2. support-path stiffness from motor bottom mount to head frame
3. tangent contact geometry consistency across 3 motors
4. adjustability for ball diameter / preload variation

## Guidance

Until superseded, treat this `v2` freeze note as the latest mechanical direction for the outer-rotor branch.
