# CAD Gap Closure v1

## Why

The previous render was constrained by existing OpenSCAD files. To move closer to a real object, this update adds missing placeholder CAD modules for layout and clearance review.

## Added CAD placeholders

| File | Purpose |
|---|---|
| `cad/vendor-placeholders/6374-motor-v1/6374_motor_placeholder_v1.scad` | 6374 motor envelope and 8mm shaft placeholder |
| `cad/3d-print/friction-wheel-v1/friction_wheel_v1.scad` | 110/130mm friction wheel placeholder |
| `cad/frame/mobile-base-v1/mobile_base_frame_v1.scad` | 1000×800mm mobile base with rear pneumatic / front caster wheel placeholders |
| `cad/assembly/p0-single-ball-launcher-v1/p0_single_ball_launcher_assembly_v1.scad` | P0 full layout assembly placeholder |

## What this enables

- Check whether the 3-wheel 120° layout fits around a size-5 ball.
- Check guide tube vs. ball clearance.
- Reserve space for 110/130mm wheel swap.
- Review mobile base proportions.
- Create more realistic renderings after OpenSCAD/export tooling is available.

## Still needs real vendor data

1. Exact 6374 motor mounting drawing.
2. Real friction wheel CAD / hardness / tread profile.
3. Actual high-current driver board dimensions.
4. PC guard unfolded pattern.
5. Mobile base fabrication details.

## Product boundary reminder

- Single-ball manual loading only for P0.
- No hopper / no feed tube / no gate.
- Auto pickup reserved for later phase only.
