# Outer Rotor 6354 Recommended Starting Params v1

## Scope

Recommended starting values for the current frozen concept branch:

- short `6354`-class 63-series outer-rotor motors
- bottom-face mounted
- central ring / barrel
- 3 cutouts for direct shell contact
- no separate friction wheel

## Recommended starting values

| Parameter | Start value |
|---|---:|
| football diameter | `220mm` |
| motor body diameter | `63mm` |
| motor body length | `53.5mm` |
| shell friction sleeve thickness | `2.0mm` |
| preload | `4mm` |
| ring ID clearance vs football | `16mm` |
| ring wall | `10mm` |
| ring height | `56mm` |
| cutout width | `52mm` |
| cutout tangential extra | `12mm` |
| residual web thickness | `14mm` |

## Why these are only starting values

These values are intended to begin the next CAD / prototype loop, not to freeze fabrication.

They are biased toward:

- making the shell contact windows visible enough
- keeping some remaining web material in the ring
- leaving room for bottom-face support packaging

## Immediate tuning order

1. `cutout width`
2. `residual web thickness`
3. `ring wall`
4. `preload`

The first loop should tune the ring before tuning the full vehicle frame.
