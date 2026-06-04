# Radial Wheel Adjustment Mechanism v1

## Purpose

The launcher must support:

1. `110mm` wheel for P0-A safe bring-up.
2. `130mm` wheel for P0-B field tuning.
3. Ball preload adjustment between `5–15mm`.
4. Re-centering after wheel wear or rubber replacement.

## Mechanism concept

Use one radial slide per wheel module:

- fixed base plate
- sliding motor plate
- two long radial slots
- four locking bolts
- preload scale marks

## CAD files

- Mechanism standalone model:
  - `cad/mechanisms/radial-wheel-adjust-v1/radial_wheel_adjust_v1.scad`
- Assembly visual integration:
  - `cad/assembly/p0-single-ball-launcher-v1/p0_single_ball_launcher_assembly_v1.scad`

## Initial dimensions

| Item | Value |
|---|---:|
| base plate | 220×80×8mm |
| slider plate | 170×52×8mm |
| slot length | 70mm |
| slot width | 10mm |
| locking bolt | M6 class |
| effective radial travel | target ±20mm minimum |

## Usage procedure

1. Loosen four locking bolts.
2. Move wheel module radially inward/outward.
3. Set preload by scale mark.
4. Tighten bolts.
5. Run no-ball spin check.
6. Run low-speed ball contact check.

## Product constraints

- Adjustment must be accessible without removing the full PC guard.
- Locking bolts must not face the ball/output path.
- Both 110mm and 130mm wheels must fit within the same guard envelope.
- After any adjustment, e-stop and no-ball spin-up must be revalidated.
