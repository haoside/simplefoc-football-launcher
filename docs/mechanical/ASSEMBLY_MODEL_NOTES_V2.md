# P0 Assembly Model Notes v2

## Change summary

The assembly model was revised to be closer to a real machine:

- Coordinate convention clarified: X left/right, Y front/back, Z vertical.
- Three wheels now sit around the ball in a **vertical X/Z plane**:
  - wheel1 above ball
  - wheel2 lower right
  - wheel3 lower left
- Short guide tube axis is horizontal and feeds into the ball centerline.
- Mobile base includes taller frame, rear push handle, low battery box, and control/e-stop bay.
- PC guard is represented as a transparent head envelope.

## Why this matters

The earlier placeholder assembly was useful for proving that OpenSCAD export works, but the wheel orientation was closer to a layout sketch. This version is better for visual review and first mechanical clearance discussions.

## Still placeholder

- 6374 motor body is still approximate.
- Friction wheel tread and rubber hardness are not modeled.
- PC guard is an envelope, not a manufacturable flat pattern.
- Mobile chassis is a frame envelope, not final fabrication drawing.

## P0 boundary

Still frozen:

- single-ball manual load
- no hopper
- no feed tube
- no gate
- no continuous feeding
