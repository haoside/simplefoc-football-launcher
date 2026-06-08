# Outer Rotor Parametric Model v5

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v7.scad`

## New in v5

This refinement continues from v6 and extends the launcher-head concept outward another step:

1. adds simple **link plates** between the ring-side support direction and the outer head carrier region
2. makes the load path easier to read from ring ear -> stub -> outer connection direction
3. keeps the geometry intentionally simple while moving closer to a believable subassembly

## Added / changed parameters

| Parameter | Meaning | Default |
|---|---|---:|
| `link_plate_w` | link plate width | `26` |
| `link_plate_t` | link plate thickness | `8` |
| `link_hole_d` | link plate hole diameter | `6.6` |

## Review focus

When opening v7, check these items first:

1. whether the ear -> stub -> link direction still aligns with the stronger web sectors
2. whether the outer link plates conceptually point toward a sensible head carrier connection region
3. whether 6354 still remains the most comfortable baseline after the extra outer connection parts are visible
4. whether the launcher head can now be read as a load path instead of only a visual arrangement
