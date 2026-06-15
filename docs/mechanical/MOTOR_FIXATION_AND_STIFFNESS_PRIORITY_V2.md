# Motor Fixation And Stiffness Priority v2

## Why this note exists

The current mainline is no longer blocked mainly by concept layout. The owner has explicitly raised `63-series motor fixation guarantee` and `stable load-bearing structure` as immediate priorities.

## Updated geometry premise

For the current mainline:

- motor axis lines are centerlines
- the 3 motor centerlines form an `equilateral triangle` in one plane
- the 3 outer rotor working surfaces are tangent to the football
- the head must keep adjustability for football diameter / preload variation

## Mechanical priority statement

For the current launcher-head branch, the structure must first guarantee:

1. stable fixation of each 63-series motor
2. controlled load path from motor bottom-face mount into the outer head structure
3. minimal drift under preload and ball-contact load
4. maintainability / adjustability without destroying stiffness

## What this means in practice

### A. Motor fixation

- avoid relying on a thin local plate only
- prefer bottom mount + short load path + braced support
- keep bolt group close to the motor support base
- ensure the bottom-face mount reads as a real support node, not only a geometric placeholder

### B. Stiffness

- shorten unsupported spans
- avoid soft cantilever interpretations around the ring
- use the stronger ring web sectors as the preferred support handoff regions
- keep side support / triangular bracket direction aligned with those stronger sectors
- preserve symmetry as much as possible because the centerline geometry is equilateral

### C. Adjustability

Adjustability is still required, but it must be introduced without turning the head into a weak flexible cage.

Preferred directions for future iterations:

- slot adjustment close to the support base, not far out on a flexible tip
- shim / spacer / indexed hole steps where possible
- avoid long weak floating adjustment arms
- prioritize equal and repeatable adjustment behavior on the 3 motor stations

## Mainline model adjustment suggestions

1. increase the realism of bottom-face support nodes before adding more cosmetic frame detail
2. keep the three support paths geometrically symmetric around the equilateral centerline layout
3. review whether the current ring-ear -> stub -> link -> frame support chain is short enough in each station
4. introduce adjustment features near the motor support bases rather than near the outer ring edge

## Next CAD focus

The next CAD pass should prioritize motor-fixation and stiffness details before chasing more visual completeness.
