# Side Support Plate Concept v1

## Files

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_mainline_v2.scad`
- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_side_support_plate_concept_v1.scad`

## Purpose

Move the launcher-head concept one step closer to a mountable frame relationship by defining an explicit side support plate direction beyond the outer mount plates.

## Current interpretation

The current mainline should now be read as:

- ring web sector
- support ear
- frame stub
- link plate
- outer mount plate
- side support plate direction

## Why this helps

This revision starts separating two concerns:

1. the launcher head subassembly itself
2. the larger outer side structure it will eventually bolt into

## Next review focus

1. whether the side support plate should be radial or triangular in the next revision
2. whether the outer mount plate should merge into the side plate or stay a separate interface plate
3. whether head-to-frame spacing should be explicitly parameterized next
