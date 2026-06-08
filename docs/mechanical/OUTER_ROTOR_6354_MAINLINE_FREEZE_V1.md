# Outer Rotor 6354 Mainline Freeze v1

## Current mainline choice

The current preferred mechanical mainline for the single-ball launcher concept is:

- `6354`-class short 63-series outer-rotor motor
- `bottom-face mounting only`
- `central launch ring / barrel`
- `3 shell-contact cutouts`
- `ring web sectors used for support ears`
- `non-star interpretation of the motor arrangement`

## Why 6354 is the mainline

Compared against `6360` and `6374`, the current concept favors `6354` because it gives:

1. the shortest tail intrusion below the ring
2. the easiest bottom-face support packaging
3. the lowest penalty when adding ring ears and outer connection parts
4. the easiest path to keep the launcher head compact

## Mainline model files

### Primary parametric concept
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v3.scad`

### Latest explicit parametric revision source
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v9.scad`

### Ring-focused review model
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_ring_focus_v2.scad`

### Motor placeholder
- `cad/vendor-placeholders/63xx-motor-v2/63xx_outer_rotor_bottom_mount_placeholder_v2.scad`

## Not frozen yet

The following are still open for iteration:

- exact cutout edge geometry
- exact ear / stub / link dimensions
- exact frame connection layout
- final selected vendor motor drawing
- final preload and ring wall thickness

## Guidance

Until a new decision supersedes this one, treat `6354` as the mainline branch and treat `6360 / 6374` as comparison branches only.
