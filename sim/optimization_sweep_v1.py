#!/usr/bin/env python3
"""P0 optimization sweep for football launcher geometry / RPM envelope.

Compares wheel diameter and RPM cap options using the same simplified launch model.
This file is intended for product/engineering tradeoff only; field calibration required.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

MODEL_PATH = pathlib.Path(__file__).with_name('football_launch_model.py')
spec = importlib.util.spec_from_file_location('model', MODEL_PATH)
model = importlib.util.module_from_spec(spec)
sys.modules['model'] = model
spec.loader.exec_module(model)  # type: ignore

TARGETS = [
    ('straight_training', 15.0, 10, 'STRAIGHT', 0),
    ('light_curve_assist', 16.0, 12, 'LEFT_CURVE', 300),
    ('standard_curve_assist', 18.0, 14, 'LEFT_CURVE', 550),
]

WHEEL_DIAMETERS = [0.11, 0.13, 0.15]
RPM_CAPS = [3000, 4000, 5000]
FRICTION = 0.65
PRELOAD_MM = 10
RAMP_S = 5


def run_case(name, speed, angle, spin_mode, bias, diameter, rpm_cap):
    # Mutate module constants for screening sweep.
    model.WHEEL_DIAMETER_M = diameter
    model.WHEEL_RADIUS_M = diameter / 2
    model.RPM_MAX = rpm_cap
    case = model.SimCase(
        f'{name}_{int(diameter*1000)}mm_{rpm_cap}rpm',
        speed,
        angle,
        spin_mode,
        bias,
        FRICTION,
        PRELOAD_MM,
        RAMP_S,
    )
    return model.simulate(case)


def main():
    print('preset,wheel_diameter_mm,rpm_cap,w1,w2,w3,launch_mps,range_m,lateral_m,current_risk,clamped')
    for preset in TARGETS:
        for d in WHEEL_DIAMETERS:
            for cap in RPM_CAPS:
                r = run_case(*preset, d, cap)
                clamped = any(w >= cap for w in (r.wheel1_rpm, r.wheel2_rpm, r.wheel3_rpm))
                print(f'{preset[0]},{int(d*1000)},{cap},{r.wheel1_rpm},{r.wheel2_rpm},{r.wheel3_rpm},{r.launch_speed_mps},{r.range_m},{r.lateral_offset_m},{r.current_risk},{clamped}')


if __name__ == '__main__':
    main()
