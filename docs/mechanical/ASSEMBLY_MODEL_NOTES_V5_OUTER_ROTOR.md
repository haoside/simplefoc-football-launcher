# P0 Assembly Model Notes v5 — Outer Rotor Direct Contact Concept

## Change summary

This revision tracks the currently frozen launcher-head concept:

- uses `3 x short 63-series outer-rotor BLDC motors` with `6354` placeholder length
- motors are `bottom-face mounted only`
- motors are arranged `around a central launch ring / barrel`
- the rotating outer cylindrical shell surfaces pass through `3 barrel wall cutouts` and directly contact the football
- the concept must be read as a `triangular motor-axis relationship around the ring`, not as a star-shaped set of axes converging to one point

## CAD placeholder

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_assembly_v2.scad`

## Intent

Use this concept model to review:

1. ring + 3 cutout geometry around the ball
2. clearance benefit of shorter `6354`-class motors versus `6374`
3. bottom-face motor support arrangement
4. launcher-head proportion on the existing base envelope

## Model assumptions

- football diameter: `220mm`
- motor body diameter: `63mm`
- placeholder motor length: `53.5mm` (`6354` class)
- shaft diameter: `10mm`
- thin rubber sleeve on outer shell: `2mm`
- preload target: `4mm`

## Frozen mechanical wording

> Three short 63-series outer-rotor motors are installed around the central launch ring. The motor outer cylindrical shells pass through three barrel wall cutouts and directly contact the football. Motors are bottom-face mounted. The motor-axis relationship is triangular around the ring and must not be interpreted as a star-shaped axis convergence.

## Still not fabrication-ready

The following still need confirmation before fabrication freeze:

1. exact selected 6354 vendor drawing and bottom-face mounting interface
2. allowable radial load on the chosen motor bearings
3. real outer-shell friction sleeve material / retention method / balance process
4. exact barrel cutout edge geometry and remaining ring stiffness
5. final support bracket stiffness / serviceability review

## Boundary reminder

- this is still a single-ball manual-loading P0 concept
- no hopper / no feed tube / no gate
- no separate friction wheel in this concept branch
