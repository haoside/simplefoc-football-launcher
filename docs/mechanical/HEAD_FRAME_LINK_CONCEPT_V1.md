# Head Frame Link Concept v1

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v7.scad`

## Purpose

Extend the launcher-head load path one step further beyond ring ears and short stubs by adding simple link plates aimed toward the outer head carrier region.

## Concept chain

Current concept load path is now expressed as:

- ring web sector
- support ear
- outer stub
- link plate
- outer head carrier direction

## Why this matters

Before this revision, the model already suggested where the ring could connect outward. This revision makes the transition more explicit and easier to discuss in terms of actual assembly strategy.

## Current placeholder values

| Item | Value |
|---|---:|
| link plate width | `26mm` |
| link plate thickness | `8mm` |
| link plate hole diameter | `6.6mm` |

## Important limitation

This is still not a finalized bracket design. It is only a structural-reading concept that helps answer:

1. does the current head want radial load paths out of the strong web sectors?
2. is the ring-ear location still sensible after adding the next connection element?
3. does 6354 still remain the easiest motor length after outer connection parts are visible?
