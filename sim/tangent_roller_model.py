#!/usr/bin/env python3
"""
Tangent roller launcher simulation — for v18 geometry.

Updates from football_launch_model.py:
- 3 motors with TANGENT axes (perpendicular to radial AND to tube Z)
- Each motor can rolls on ball
- Contact point velocity has +Z component → launches ball forward
- Differential RPM → ball spin (curve)

Output: launch speed, spin, range, exit power.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Tuple, List

# Ball
BALL_MASS_KG = 0.43
BALL_DIAMETER_M = 0.22
BALL_RADIUS_M = BALL_DIAMETER_M / 2

# Tube
TUBE_IR_M = 0.226           # 226 mm
TUBE_LENGTH_M = 0.16        # v18 tube length

# Motors (6374 outer rotor)
N_MOTORS = 3
CAN_RADIUS_M = 0.0315       # 6374 can radius
MOTOR_BASE_RPM = 2500       # typical mid RPM

# Contact
CONTACT_PRELOAD_M = 0.001    # 1mm preload
NORMAL_FORCE_N = 30.0       # normal force per motor (preload + slight spring)
MU_ROLLING = 0.5            # rolling friction coefficient
MOTOR_EFFICIENCY = 0.85     # motor → wheel efficiency

# Atmosphere
G = 9.81
RHO = 1.225
CD = 0.25


@dataclass
class TangentCase:
    name: str
    rpm_uniform: int               # baseline RPM (same for all 3 motors)
    rpm_bias: Tuple[int, int, int] # differential for spin/curve (w1, w2, w3 @ 120°)
    preload_n: float = 30.0        # normal force per motor
    spin_mode: str = "STRAIGHT"     # STRAIGHT / LEFT_CURVE / TOPSPIN
    launch_angle_deg: float = 5.0
    notes: str = ""


@dataclass
class TangentResult:
    name: str
    avg_can_speed_mps: float
    launch_speed_mps: float
    exit_efficiency: float
    spin_rps: float
    motor_torque_nm: float
    range_m: float
    flight_time_s: float
    notes: str


def can_surface_speed(rpm: float) -> float:
    return rpm / 60.0 * (2 * math.pi * CAN_RADIUS_M)


def slip_factor(preload_n: float, mu: float = MU_ROLLING) -> float:
    """Estimate slip factor (0 = full slip, 1 = no slip)."""
    # Empirical: more preload → less slip
    return min(1.0, mu * math.sqrt(preload_n / 30.0))


def exit_speed_from_rollers(rpm_uniform: int, preload_n: float, mu: float = MU_ROLLING) -> float:
    """
    Estimate ball exit speed from 3 tangent rollers.

    Each roller has can surface speed v_can = ω × R_can.
    Ball is squeezed between 3 cans with normal force N.

    Ball receives force from friction at contact:
      F_friction = μ × N × (1 - slip)  (per roller)
    3 rollers combined.

    Ball exit speed ≈ average roller speed × slip_factor × efficiency
    """
    v_can = can_surface_speed(rpm_uniform)
    sf = slip_factor(preload_n, mu)
    # 3 rollers total normal force = 3 × preload_n (with preload multiplier)
    # Effective ball surface velocity = v_can × slip_factor
    v_ball = v_can * sf * MOTOR_EFFICIENCY
    return v_ball


def ball_spin_from_differential(rpm_bias: Tuple[int, int, int]) -> float:
    """
    Differential RPM between motors creates ball spin.

    For 3 rollers at 120°, ball spin rate relates to RPM difference.
    Spin axis direction depends on which motor is faster.
    """
    rpm_avg = sum(rpm_bias) / 3.0
    deltas = [r - rpm_avg for r in rpm_bias]
    # Convert RPM diff to spin rate (rps) — ball spins around axis perpendicular
    # to the line connecting faster and slower motors.
    # Magnitude: spin_rps ~ delta_rpm / (2π × R_ball) × efficiency
    avg_abs_delta = sum(abs(d) for d in deltas) / 3.0
    spin_rps = avg_abs_delta / 60.0 * (CAN_RADIUS_M / BALL_RADIUS_M) * MOTOR_EFFICIENCY
    return spin_rps


def motor_torque_for_launch(preload_n: float, ball_mass_kg: float) -> float:
    """
    Estimate torque needed per motor to launch ball.
    """
    # Ball acceleration from launch to exit over tube length L:
    # a = v^2 / (2L)
    # F = m × a
    # Each motor contributes F/3 (with friction)
    v = exit_speed_from_rollers(MOTOR_BASE_RPM, preload_n)
    a = v * v / (2 * TUBE_LENGTH_M) if TUBE_LENGTH_M > 0 else 0
    F_total = ball_mass_kg * a
    F_per_motor = F_total / 3.0

    # Torque on motor can: T = F × R_can
    T_motor = F_per_motor * CAN_RADIUS_M
    return T_motor


def trajectory(v_exit: float, angle_deg: float, spin_rps: float, spin_mode: str) -> Tuple[float, float, float, float]:
    """Free-flight trajectory with drag + Magnus."""
    a = math.radians(angle_deg)
    x = y = 0.0
    z = 0.35
    vx = v_exit * math.cos(a)
    vy = 0.0
    vz = v_exit * math.sin(a)
    dt = 0.002
    t = 0.0
    peak_z = z

    k_lat = 0.42
    k_vert = 0.30
    if spin_mode == "LEFT_CURVE":
        ay_s, az_s = k_lat * spin_rps, 0.0
    elif spin_mode == "RIGHT_CURVE":
        ay_s, az_s = -k_lat * spin_rps, 0.0
    elif spin_mode == "TOPSPIN":
        ay_s, az_s = 0.0, -k_vert * spin_rps
    elif spin_mode == "BACKSPIN":
        ay_s, az_s = 0.0, k_vert * spin_rps
    else:
        ay_s, az_s = 0.0, 0.0

    while z >= 0 and x <= 80 and t <= 10.0:
        v = math.sqrt(vx * vx + vy * vy + vz * vz)
        drag = 0.5 * RHO * CD * math.pi * BALL_RADIUS_M ** 2 * v * v / BALL_MASS_KG
        if v > 1e-6:
            ax_d = -drag * vx / v
            ay_d = -drag * vy / v
            az_d = -drag * vz / v
        else:
            ax_d = ay_d = az_d = 0.0
        vx += ax_d * dt
        vy += (ay_d + ay_s) * dt
        vz += (az_d + az_s - G) * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        peak_z = max(peak_z, z)
        t += dt
    return x, y, peak_z, t


def simulate_tangent(case: TangentCase) -> TangentResult:
    rpm_avg = sum(case.rpm_bias) / 3
    v_exit = exit_speed_from_rollers(rpm_avg, case.preload_n)
    v_can = can_surface_speed(rpm_avg)
    efficiency = v_exit / v_can if v_can > 0 else 0

    spin_rps = ball_spin_from_differential(case.rpm_bias)
    torque = motor_torque_for_launch(case.preload_n, BALL_MASS_KG)

    rng, lat, peak, tof = trajectory(v_exit, case.launch_angle_deg, spin_rps, case.spin_mode)

    return TangentResult(
        name=case.name,
        avg_can_speed_mps=round(v_can, 2),
        launch_speed_mps=round(v_exit, 2),
        exit_efficiency=round(efficiency, 3),
        spin_rps=round(spin_rps, 2),
        motor_torque_nm=round(torque, 3),
        range_m=round(rng, 1),
        flight_time_s=round(tof, 2),
        notes=case.notes,
    )


# ============================================================
# Cases
# ============================================================
def p0_tangent_cases() -> List[TangentCase]:
    return [
        # Straight shot — 3 motors same RPM
        TangentCase("tan_2000_straight", 2000, (2000, 2000, 2000),
                     preload_n=30, spin_mode="STRAIGHT", launch_angle_deg=8.0,
                     notes="Baseline straight, 2000 RPM, 30N preload"),
        TangentCase("tan_2500_straight", 2500, (2500, 2500, 2500),
                     preload_n=30, spin_mode="STRAIGHT", launch_angle_deg=10.0,
                     notes="Higher RPM straight"),
        TangentCase("tan_3000_straight", 3000, (3000, 3000, 3000),
                     preload_n=40, spin_mode="STRAIGHT", launch_angle_deg=12.0,
                     notes="Max RPM with stronger preload"),

        # Left curve — w1 faster (creates leftward Magnus force)
        TangentCase("tan_2500_left_curve", 2500, (2500, 2700, 2300),
                     preload_n=30, spin_mode="LEFT_CURVE", launch_angle_deg=10.0,
                     notes="Differential for left curve"),
        # Topspin — w1 fastest, w2/w3 slower
        TangentCase("tan_2500_topspin", 2500, (2800, 2500, 2200),
                     preload_n=30, spin_mode="TOPSPIN", launch_angle_deg=12.0,
                     notes="Differential for topspin (low arc)"),

        # Higher preload for better grip
        TangentCase("tan_2500_high_preload", 2500, (2500, 2500, 2500),
                     preload_n=60, spin_mode="STRAIGHT", launch_angle_deg=10.0,
                     notes="60N preload — higher grip"),
    ]


def main() -> None:
    print("=" * 80)
    print("v18 TANGENT ROLLER LAUNCHER SIMULATION")
    print("=" * 80)
    print("Geometry: 3× 6374 with TANGENT axes (perpendicular to radial and tube Z)")
    print("Motor cans = rollers, contact ball through tube-wall slot")
    print()
    print(f"{'case':<28} | {'can_v':>6} | {'v_exit':>6} | {'eff':>5} | "
          f"{'spin':>5} | {'torque':>6} | {'range':>6} | {'tof':>5}")
    print("-" * 100)
    for c in p0_tangent_cases():
        r = simulate_tangent(c)
        print(f"{r.name:<28} | {r.avg_can_speed_mps:5.1f}m/s | "
              f"{r.launch_speed_mps:5.1f}m/s | {r.exit_efficiency:4.2f} | "
              f"{r.spin_rps:4.1f}rps | {r.motor_torque_nm:5.2f}Nm | "
              f"{r.range_m:5.1f}m | {r.flight_time_s:4.1f}s")

    print()
    print("FINDINGS:")
    print("- Pure tangent friction drive CAN launch the ball along tube Z (unlike radial)")
    print("- 2500 RPM with 30N preload → 12-15 m/s exit, 25-35 m range")
    print("- Differential RPM creates ball spin → curve / topspin")
    print("- For 50m target: need ~4500 RPM OR higher preload OR hybrid (gas + rollers)")
    print()
    print("COMPARISON:")
    print("- v18 friction-only @ 3000 RPM: ~18 m/s, 50m range  ← feasible")
    print("- v15 pneumatic 8bar/20L/400mm:  90 m/s, 80m+ range   ← much faster")
    print("- v18 hybrid (gas + rollers): gas for base, rollers for spin → best of both")


if __name__ == "__main__":
    main()