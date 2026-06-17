# Outer Rotor Model Index v1

## Mainline file

Use this file first when reviewing the current preferred launcher-head concept:

- `cad/assembly/p0-single-ball-launcher-v3/outrunner_launch_tube_v1.scad`
- `cad/assembly/p0-single-ball-launcher-v3/outrunner_launch_tube_v1_1.scad`

`outrunner_launch_tube_v1.scad` remains the first baseline. `outrunner_launch_tube_v1_1.scad` is the current 6354 refinement with parameterized end-face slots, 2–3mm preload expression, shield tabs, and rib updates.

## Current design note

- `docs/mechanical/OUTRUNNER_LAUNCH_TUBE_V1.md`
- `docs/mechanical/OUTRUNNER_LAUNCH_TUBE_V1_1.md`
- `docs/renders/OUTRUNNER_LAUNCH_TUBE_THREE_VIEW_V1.svg`
- `docs/renders/OUTRUNNER_LAUNCH_TUBE_THREE_VIEW_V1_1.svg`


## Supporting files

### Ring-focused review
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_ring_focus_v2.scad`

### Motor placeholder
- `cad/vendor-placeholders/63xx-motor-v2/63xx_outer_rotor_bottom_mount_placeholder_v2.scad`

### Previous mainline / comparison
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v3.scad`

## Historical / comparison parametric files

These remain useful for review history and comparison, but they are not the first file to open now:

- `..._parametric_v3.scad`
- `..._parametric_v4.scad`
- `..._parametric_v5.scad`
- `..._parametric_v6.scad`
- `..._parametric_v7.scad`
- `..._parametric_v8.scad`

## Guidance

For current discussion, screenshots, and further iteration, prefer the `mainline` file unless a comparison turn explicitly needs one of the older parametric revisions.
