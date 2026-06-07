# Outer Rotor Parametric Model v1

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v3.scad`

## Purpose

Provide a tunable OpenSCAD concept model for the frozen single-ball launcher direction:

- 3 short 63-series outer-rotor motors
- bottom-face mounted only
- central launch ring / barrel
- 3 barrel wall cutouts for direct outer-shell ball contact
- no separate friction wheel
- no star-shaped center-converging axis expression

## Main parameters

| Parameter | Meaning | Default |
|---|---|---:|
| `ball_d` | football diameter | `220` |
| `motor_body_d` | outer rotor body diameter | `63` |
| `motor_body_len` | motor length (6354 placeholder) | `53.5` |
| `motor_shaft_d` | shaft diameter | `10` |
| `rubber_t` | friction sleeve thickness | `2.0` |
| `preload` | conceptual radial preload | `4` |
| `ring_clearance` | ring ID oversize vs football | `16` |
| `ring_wall` | ring wall thickness | `10` |
| `ring_h` | ring height | `56` |
| `cutout_w` | single cutout radial width | `52` |
| `cutout_extra` | tangential allowance beyond motor diameter | `12` |
| `head_z` | head center height | `620` |

## What to tune first

1. `motor_body_len`
   - compare 6354 / 6360 / 6374 packaging effect
2. `ring_clearance`
   - controls how tightly the ball sits inside the ring
3. `cutout_w` and `cutout_extra`
   - controls how much of the motor shell enters the ring wall zone
4. `ring_wall`
   - tradeoff between stiffness and cutout size

## Current interpretation guardrail

This file is still a concept placeholder. It should be interpreted as:

- motors installed around the ring
- shell surfaces pass through the cutouts
- triangular relationship around the ring

It should **not** be interpreted as a final proof that the motor axes geometrically converge to one center point, and it should **not** be used as fabrication CAD.
