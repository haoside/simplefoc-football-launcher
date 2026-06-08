# Ring Connection Ears v1

## File

- `cad/assembly/p0-single-ball-launcher-v2/p0_single_ball_launcher_ring_focus_v2.scad`

## Purpose

Continue the launcher ring concept from pure cutout review toward a mountable subassembly by adding simple support ears around the outer ring.

## What was added

- 3 outer-ring support ears
- one ear located in each web sector between adjacent cutouts
- simple hole placeholder in each ear for frame / bracket connection review

## Current placeholder values

| Item | Value |
|---|---:|
| ear width | `34mm` |
| ear length | `36mm` |
| ear thickness | `12mm` |
| ear hole diameter | `6.6mm` |

## Placement rule

Ears are placed in the three stronger sectors that remain between cutouts, not in the cutout sectors themselves.

This matches the current structural intuition:

- cutout sectors are already weakened by shell-contact windows
- web sectors are the better place to transfer load into the outer support structure

## Next review focus

1. whether ear size is enough for actual bracket connection
2. whether web sector thickness remains sufficient after adding ears
3. whether ear direction should stay radial or switch to tangential tabs in the next revision
