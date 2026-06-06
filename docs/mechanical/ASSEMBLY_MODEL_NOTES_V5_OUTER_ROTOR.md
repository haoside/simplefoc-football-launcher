# P0 Assembly Model Notes v5 — Outer Rotor Direct Contact Concept

## Change summary

This revision adds a new concept assembly placeholder for the updated launcher head direction:

- replaces the previous `3 parallel friction wheel` visual assumption
- uses `3 x 6374 outer-rotor motor cans` as the direct ball-contact bodies
- motor axes are no longer parallel; each axis tilts inward toward the ball center
- keeps `120°` circumferential distribution around the football
- keeps the guide ring recessed so it does not become the primary contact surface

## Added CAD placeholder

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_assembly_v2.scad`

## Intent

Use this concept model to review:

1. whether the cylindrical outer shell surfaces can achieve real 3-point contact with a size-5 ball
2. motor tilt / support-arm clearance around the launcher head
3. guide-ring retreat vs. ball entry path
4. overall head proportion on the existing mobile-base envelope

## Model assumptions

- football diameter: `220mm`
- 6374 outer-rotor can diameter: `63mm` placeholder
- thin rubber sleeve on motor outer shell: `2mm`
- preload target: `4mm`
- motor-axis inward tilt: `28°` placeholder

## Not yet fabrication-ready

The following still need confirmation before fabrication freeze:

1. exact 6374 vendor drawing and mounting face
2. allowable radial load on the chosen motor bearings
3. real outer-shell friction sleeve material / retention method / balance process
4. final motor tilt angle from actual shooting-direction testing
5. stator bracket stiffness and serviceability review

## Boundary reminder

- this is still a single-ball manual-loading P0 concept
- no hopper / no feed tube / no gate
- no separate friction wheel in this concept branch
