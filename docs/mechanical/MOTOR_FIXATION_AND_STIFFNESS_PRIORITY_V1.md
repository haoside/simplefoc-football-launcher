# Motor Fixation And Stiffness Priority v1

## Why this note exists

The current mainline is no longer blocked mainly by concept layout. The owner has explicitly raised `63-series motor fixation guarantee` and `stable load-bearing structure` as immediate priorities.

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

### B. Stiffness

- shorten unsupported spans
- avoid soft cantilever interpretations around the ring
- use the stronger ring web sectors as the preferred support handoff regions
- keep side support / triangular bracket direction aligned with those stronger sectors

### C. Adjustability

Adjustability is still required, but it must be introduced without turning the head into a weak flexible cage.

Preferred directions for future iterations:

- slot adjustment close to the support base, not far out on a flexible tip
- shim / spacer / indexed hole steps where possible
- avoid long weak floating adjustment arms

## Next CAD focus

The next CAD pass should prioritize motor-fixation and stiffness details before chasing more visual completeness.
