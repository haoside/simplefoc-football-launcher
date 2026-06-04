# P0 Simulation: 3-BLDC Football Launcher

## Goal

Validate the first-order mapping:

```text
wheel1/2/3 RPM -> launch speed / spin / curve / landing point
```

This is a lightweight numerical model for parameter screening. It is not CFD, FEA, or final system validation.

## Frozen geometry

- 3 friction wheels in 120° distribution
- wheel1 @ 12:00
- wheel2 @ 4:00
- wheel3 @ 8:00
- standard size-5 football: 0.22 m diameter, 0.43 kg
- nominal wheel diameter: 0.11 m

## Run

```bash
python3 sim/football_launch_model.py
```

## Outputs

- recommended wheel RPMs for:
  - straight pass
  - light curve assist pass
  - standard curve assist pass
- estimated launch speed
- estimated spin rate
- estimated range and lateral offset
- rough current risk flag based on RPM/ramp

## Calibration needed on real machine

1. Actual wheel surface speed vs. measured ball exit speed.
2. Effective friction coefficient for wheel rubber + football surface.
3. Best preload window between 5–15 mm.
4. Actual curve strength vs. `spinBiasRpm`.
5. Current peak during 4/5/6 s spin-up ramps.

## P0 acceptance use

Use the model to choose first safe RPM presets before field tests. Then update the model constants from measured data.
