#!/usr/bin/env python3
"""
P0 numerical simulation for the 3-BLDC / 120-degree football launcher.

Purpose:
- Convert target launch speed + spin mode into wheel RPMs.
- Estimate launch speed/spin from wheel RPMs, friction, and preload.
- Estimate range/lateral offset with drag + simplified Magnus effect.
- Flag rough current risk from ramp duration.

This is an engineering screening model, not final CFD / FEA.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, Tuple

G = 9.81
RHO = 1.225
CD = 0.25
BALL_MASS_KG = 0.43
BALL_DIAMETER_M = 0.22
BALL_RADIUS_M = BALL_DIAMETER_M / 2
BALL_AREA_M2 = math.pi * BALL_RADIUS_M**2
WHEEL_DIAMETER_M = 0.11
WHEEL_RADIUS_M = WHEEL_DIAMETER_M / 2
RPM_MIN = 500
RPM_MAX = 3000

# wheel physical coordinates frozen by PM:
# wheel1 @ 12:00, wheel2 @ 4:00, wheel3 @ 8:00
SPIN_MODES = ("STRAIGHT", "TOPSPIN", "BACKSPIN", "LEFT_CURVE", "RIGHT_CURVE")


@dataclass
class SimCase:
    name: str
    target_speed_mps: float
    launch_angle_deg: float
    spin_mode: str
    spin_bias_rpm: int
    friction_coeff: float
    preload_mm: int
    ramp_s: int


@dataclass
class SimResult:
    case: str
    wheel1_rpm: int
    wheel2_rpm: int
    wheel3_rpm: int
    launch_speed_mps: float
    spin_rate_rps: float
    range_m: float
    lateral_offset_m: float
    peak_height_m: float
    flight_time_s: float
    current_risk: str
    notes: str


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def wheel_surface_speed_to_rpm(speed_mps: float) -> float:
    return speed_mps / (2 * math.pi * WHEEL_RADIUS_M) * 60


def rpm_to_surface_speed(rpm: float) -> float:
    return rpm / 60 * (2 * math.pi * WHEEL_RADIUS_M)


def rpm_mixer_120deg(target_speed_mps: float, spin_mode: str, spin_bias_rpm: int) -> Tuple[int, int, int]:
    base = wheel_surface_speed_to_rpm(target_speed_mps)
    d = spin_bias_rpm
    if spin_mode == "STRAIGHT":
        w = (base, base, base)
    elif spin_mode == "TOPSPIN":
        w = (base + d, base - d / 2, base - d / 2)
    elif spin_mode == "BACKSPIN":
        w = (base - d, base + d / 2, base + d / 2)
    elif spin_mode == "LEFT_CURVE":
        w = (base, base + d, base - d)
    elif spin_mode == "RIGHT_CURVE":
        w = (base, base - d, base + d)
    else:
        raise ValueError(f"unknown spin_mode: {spin_mode}")
    return tuple(int(round(clamp(x, RPM_MIN, RPM_MAX))) for x in w)  # type: ignore


def contact_efficiency(mu: float, preload_mm: int) -> float:
    # Empirical screening estimate:
    # - more preload improves coupling but too much increases deformation loss.
    # - 10mm is treated as the nominal P0 starting point.
    preload_gain = 0.82 + 0.018 * min(preload_mm, 12)
    overload_loss = max(preload_mm - 12, 0) * 0.015
    mu_gain = 0.72 + 0.32 * clamp((mu - 0.45) / (0.85 - 0.45), 0, 1)
    return clamp(preload_gain * mu_gain - overload_loss, 0.55, 0.94)


def estimate_launch(wheel_rpms: Tuple[int, int, int], mu: float, preload_mm: int) -> Tuple[float, float]:
    surface_speeds = [rpm_to_surface_speed(r) for r in wheel_rpms]
    avg_speed = sum(surface_speeds) / 3
    eff = contact_efficiency(mu, preload_mm)
    launch_speed = avg_speed * eff

    # RPM spread approximates spin strength. Convert differential surface speed to rough spin rps.
    spread_speed = max(surface_speeds) - min(surface_speeds)
    spin_rate_rps = (spread_speed / (2 * math.pi * BALL_RADIUS_M)) * eff
    return launch_speed, spin_rate_rps


def spin_accel(spin_mode: str, spin_rate_rps: float) -> Tuple[float, float]:
    # Simplified Magnus-like acceleration. Needs field calibration.
    k_lat = 0.42
    k_vert = 0.30
    if spin_mode == "LEFT_CURVE":
        return k_lat * spin_rate_rps, 0.0
    if spin_mode == "RIGHT_CURVE":
        return -k_lat * spin_rate_rps, 0.0
    if spin_mode == "TOPSPIN":
        return 0.0, -k_vert * spin_rate_rps
    if spin_mode == "BACKSPIN":
        return 0.0, k_vert * spin_rate_rps
    return 0.0, 0.0


def trajectory(speed: float, angle_deg: float, spin_mode: str, spin_rate_rps: float) -> Tuple[float, float, float, float]:
    angle = math.radians(angle_deg)
    x = y = 0.0
    z = 0.35
    vx = speed * math.cos(angle)
    vy = 0.0
    vz = speed * math.sin(angle)
    dt = 0.002
    t = 0.0
    peak_z = z
    ay_spin, az_spin = spin_accel(spin_mode, spin_rate_rps)

    while z >= 0 and x <= 60 and t <= 8.0:
        v = math.sqrt(vx * vx + vy * vy + vz * vz)
        drag_acc = 0.5 * RHO * CD * BALL_AREA_M2 * v * v / BALL_MASS_KG
        if v > 1e-6:
            ax_d = -drag_acc * vx / v
            ay_d = -drag_acc * vy / v
            az_d = -drag_acc * vz / v
        else:
            ax_d = ay_d = az_d = 0.0
        vx += ax_d * dt
        vy += (ay_d + ay_spin) * dt
        vz += (az_d + az_spin - G) * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        peak_z = max(peak_z, z)
        t += dt
    return x, y, peak_z, t


def current_risk(wheel_rpms: Tuple[int, int, int], ramp_s: int) -> str:
    max_rpm = max(wheel_rpms)
    if ramp_s < 4:
        return "HIGH: ramp too aggressive"
    if max_rpm >= 2800 and ramp_s <= 4:
        return "HIGH: high RPM with short ramp"
    if max_rpm >= 2500 and ramp_s <= 5:
        return "MEDIUM: watch BMS / branch current"
    return "LOW"


def simulate(case: SimCase) -> SimResult:
    rpms = rpm_mixer_120deg(case.target_speed_mps, case.spin_mode, case.spin_bias_rpm)
    launch_speed, spin_rate = estimate_launch(rpms, case.friction_coeff, case.preload_mm)
    rng, lat, peak, tof = trajectory(launch_speed, case.launch_angle_deg, case.spin_mode, spin_rate)
    return SimResult(
        case=case.name,
        wheel1_rpm=rpms[0],
        wheel2_rpm=rpms[1],
        wheel3_rpm=rpms[2],
        launch_speed_mps=round(launch_speed, 2),
        spin_rate_rps=round(spin_rate, 2),
        range_m=round(rng, 1),
        lateral_offset_m=round(lat, 2),
        peak_height_m=round(peak, 2),
        flight_time_s=round(tof, 2),
        current_risk=current_risk(rpms, case.ramp_s),
        notes="screening estimate; calibrate mu/contact/Magnus with field test",
    )


def p0_cases() -> Iterable[SimCase]:
    # Nominal mid-friction / 10mm preload / 5s ramp set.
    return [
        SimCase("straight_pass", 15.0, 10, "STRAIGHT", 0, 0.65, 10, 5),
        SimCase("light_curve_assist", 15.0, 12, "LEFT_CURVE", 250, 0.65, 10, 5),
        SimCase("standard_curve_assist", 16.5, 14, "LEFT_CURVE", 450, 0.65, 10, 5),
    ]


def main() -> None:
    print("case,wheel1,wheel2,wheel3,launch_mps,spin_rps,range_m,lateral_m,peak_m,time_s,current_risk")
    for c in p0_cases():
        r = simulate(c)
        print(f"{r.case},{r.wheel1_rpm},{r.wheel2_rpm},{r.wheel3_rpm},{r.launch_speed_mps},{r.spin_rate_rps},{r.range_m},{r.lateral_offset_m},{r.peak_height_m},{r.flight_time_s},{r.current_risk}")


if __name__ == "__main__":
    main()
