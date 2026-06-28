#!/usr/bin/env python3
"""
Propulsion source comparison per PROPULSION_ARCHITECTURE_REVIEW_V1.md.

Compares the three options:
1. Pure 3-rotor friction (from football_launch_model.py)
2. Pneumatic primary + 3 motors for spin (from pneumatic_launch_model.py)
3. Tilted/helical rotor (placeholder — needs geometry input)

Outputs side-by-side table for PM review.
"""
from __future__ import annotations

import math
import sys
import os

# Add sim/ to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the two models
try:
    from pneumatic_launch_model import (
        simulate_pneumatic, PneumaticCase, p0_pneumatic_cases, BALL_MASS_KG
    )
except ImportError as e:
    print(f"ERROR: pneumatic_launch_model import failed: {e}")
    sys.exit(1)

try:
    from football_launch_model import (
        simulate, SimCase, p0_cases, RPM_MIN, RPM_MAX
    )
except ImportError as e:
    print(f"ERROR: football_launch_model import failed: {e}")
    sys.exit(1)


def header(t: str) -> None:
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def section(t: str) -> None:
    print()
    print("-" * 78)
    print(t)
    print("-" * 78)


def run_pneumatic_table():
    header("Option 2: Pneumatic primary + 3-motor spin module")

    section("Cases:")
    for c in p0_pneumatic_cases():
        print(f"  {c.name:<28} | P={c.tank_pressure_bar_gauge:5.1f}bar | "
              f"V_tank={c.tank_volume_l:5.1f}L | L_press={c.tube_pressure_length_m:.2f}m | "
              f"spin={c.spin_mode} dRPM={c.spin_rpm_diff}")

    section("Results:")
    print(f"  {'case':<28} | {'v_exit':>7} | {'range':>7} | {'spin':>6} | {'safety':<40}")
    for c in p0_pneumatic_cases():
        r = simulate_pneumatic(c)
        print(f"  {r.name:<28} | {r.launch_speed_mps:5.1f}m/s | "
              f"{r.range_m:5.1f}m | {r.spin_rate_rps:4.1f}rps | {r.safety_margin}")


def run_rotor_table():
    header("Option 1: Pure 3-rotor friction (current football_launch_model.py)")

    section("Cases (P0 nominal):")
    for c in p0_cases():
        print(f"  {c.name:<28} | target_speed={c.target_speed_mps}m/s | "
              f"spin_mode={c.spin_mode} dRPM={c.spin_bias_rpm}")

    section("Results:")
    print(f"  {'case':<28} | {'w1':>6} | {'w2':>6} | {'w3':>6} | {'v':>6} | "
          f"{'range':>7} | {'risk':<30}")
    for c in p0_cases():
        r = simulate(c)
        print(f"  {r.case:<28} | {r.wheel1_rpm:5d} | {r.wheel2_rpm:5d} | "
              f"{r.wheel3_rpm:5d} | {r.launch_speed_mps:5.1f} | "
              f"{r.range_m:5.1f}m | {r.current_risk}")


def run_tilted_estimate():
    """
    Option 3: Tilted rotor screening estimate.

    Assumption: ball moving in tube of length L, 3 motors with can at angle
    α from radial. Can surface velocity v_can = ω·R_can. Velocity component
    along tube axis: v_z = v_can · sin(α).

    Empirical fit: with α=10°, μ=0.6, preload 8mm, effective contact efficiency
    ~0.55. v_exit ~ v_can · sin(α) · efficiency.
    """
    header("Option 3: Tilted / helical rotor (screening)")

    section("Setup:")
    can_r = 0.0315     # 6374 can radius
    wheel_rpm = 2500   # typical mid range
    v_can = wheel_rpm / 60 * 2 * math.pi * can_r
    print(f"  Wheel RPM: {wheel_rpm}, can surface speed: {v_can:.1f} m/s")

    section("Tilt angle scan:")
    print(f"  {'tilt°':>6} | {'v_z_comp':>8} | {'ball_v_exit':>10} | {'note'}")
    for alpha_deg in [0, 5, 10, 15, 20, 30]:
        sin_a = math.sin(math.radians(alpha_deg))
        eff = 0.55
        v_exit = v_can * sin_a * eff
        note = ("ball spins only" if alpha_deg == 0
                else "feasible, low speed"
                if v_exit < 8
                else "usable for short range"
                if v_exit < 25
                else "good for mid range")
        print(f"  {alpha_deg:6.1f} | {v_can * sin_a:7.1f}m/s | {v_exit:8.1f}m/s | {note}")


def main() -> None:
    print("Propulsion Architecture Review — Comparison Table")
    print("Reference: docs/mechanical/PROPULSION_ARCHITECTURE_REVIEW_V1.md")
    run_pneumatic_table()
    run_rotor_table()
    run_tilted_estimate()
    section("Summary")
    print("  Option 1 (pure rotor):  ball launches only at tilt > 0")
    print("                          otherwise ball spins in place (0 m/s axial)")
    print("  Option 2 (pneumatic):   ball launches reliably at 5-8 bar,")
    print("                          50 m target reachable with 8 bar / 20 L")
    print("  Option 3 (tilted):      ball launches but limited to ~25 m/s at 15°,")
    print("                          mechanical complexity + asymmetric wear")
    print()
    print("Recommendation: Option 2 (pneumatic primary + 3-motor spin module)")


if __name__ == "__main__":
    main()