# Render Source Map v1

## Source repository

https://github.com/haoside/simplefoc-football-launcher

## CAD / OpenSCAD files used

| Render part | Source file | Source dimensions |
|---|---|---|
| Short guide tube | `cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad` | L=200mm, ID=232mm, wall=4mm, flange Ø270mm, flare entry Ø255mm |
| Motor mount plate | `cad/sheet-metal/motor-mount-plate-v1/motor_mount_plate_v1.scad` | 180×140×8mm, center hole Ø24mm, slot 120×20mm |
| E-stop panel | `cad/sheet-metal/estop-panel-v1/estop_panel_v1.scad` | 100×80×3mm, button hole Ø22.5mm |
| Battery clamp | `cad/sheet-metal/battery-clamp-v1/battery_clamp_v1.scad` | 260×35×4mm |
| Guard bracket | `cad/sheet-metal/guard-bracket-v1/guard_bracket_v1.scad` | 220×40×4mm |
| Control bay plate | `cad/sheet-metal/control-bay-plate-v1/control_bay_plate_v1.scad` | Used as control bay reference |
| Power bay plate | `cad/sheet-metal/power-bay-plate-v1/power_bay_plate_v1.scad` | Used as power bay reference |

## Rendered output files

| File | Purpose |
|---|---|
| `docs/renders/P0_CAD_BASED_RENDER_V1.svg` | Build-oriented assembled concept render |
| `docs/renders/P0_CAD_EXPLODED_VIEW_V1.svg` | Exploded layout showing major CAD-derived modules |

## Assumptions still not backed by exact CAD

These are visually represented but still need real CAD/part models:

1. 6374 motor body model.
2. 110/130mm friction wheel model and tread profile.
3. Mobile base frame / wheel brackets.
4. Rear pneumatic wheel and front caster models.
5. Full transparent PC guard cover unfolded pattern.
6. Wiring harness and connector placement.

## Product rule

Any render must keep the frozen P0 boundary:

- single-ball manual loading only
- no hopper
- no feed tube
- no gate
- no continuous feeding
- auto pickup only as future reserved interface
