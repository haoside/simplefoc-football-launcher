# Outer Rotor Parametric Model v3

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_outer_rotor_parametric_v5.scad`

## New in v3

This refinement continues from v4 and focuses on the next two review items:

1. **switchable motor length preset** for `6354 / 6360 / 6374`
2. **more realistic bottom-face support geometry**
3. **softer barrel cutout edge shape** instead of pure rectangular windows

## Added / changed parameters

| Parameter | Meaning | Default |
|---|---|---:|
| `motor_series` | motor length preset | `"6354"` |
| `brace_len` | bottom-mount brace length | `34` |
| `brace_t` | brace thickness | `8` |

## Preset behavior

`motor_series` maps to:

- `6354` → `53.5mm`
- `6360` → `60mm`
- `6374` → `74mm`

This allows quick packaging comparison without rewriting the whole model.

## Review focus

When opening v5, check these items first:

1. compare tail clearance for `6354 / 6360 / 6374`
2. judge whether the bottom-face supports still fit cleanly under the ring envelope
3. inspect whether softer cutout edges make the barrel concept more manufacturable
4. keep validating the frozen concept: ring-centered, three cutouts, shell-through-window contact, non-star interpretation
