# 63xx Outer Rotor Motor Mount Interface v1

## Purpose

Record the currently preferred placeholder mount interface for the launcher concept after the shift from long `6374` packaging toward shorter `6354`-class packaging.

## Current preferred interpretation

- use a short `63xx` outer-rotor motor, currently modeled as `6354`
- install by `bottom-face mounting` only in the launcher concept
- do not use top-face hanging as the main concept mount

## Placeholder dimensions from current reference drawing

| Item | Value |
|---|---:|
| body diameter | `63mm` |
| body length | `53.5mm` |
| shaft diameter | `10mm` |
| shaft length | `29.5mm` |
| top mounting hole set | `44 / 30 mm` |
| bottom mounting hole set | `22 mm` |
| mounting hole size | `M4` |

## CAD placeholder file

- `cad/vendor-placeholders/63xx-motor-v2/63xx_outer_rotor_bottom_mount_placeholder_v2.scad`

## Design implication for launcher head

1. head bracket logic should assume `bottom-face mounted motor support`
2. barrel / ring cutouts should be sized around a `63mm` body plus sleeve tolerance
3. short motor packaging improves clearance around the ring versus 6374
4. top-face hole sets may still be kept in documentation, but should not be treated as the primary concept mount in this branch

## Warning

`63xx` is a family size, not a universal mounting standard. Before fabrication, the selected vendor drawing must replace this placeholder assumption.
