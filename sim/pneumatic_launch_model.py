#!/usr/bin/env python3
"""
Pneumatic primary propulsion + 3-motor spin control model.

Per PROPULSION_ARCHITECTURE_REVIEW_V1.md:
- Compressed air = primary axial propulsion
- 3 motors (radial, tangent to tube) = spin / curve control module
- This file adds the pneumatic layer that the existing
  football_launch_model.py does not yet have.

This is engineering screening, not final CFD / FEA.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

# Ball
BALL_MASS_KG = 0.43
BALL_DIAMETER_M = 0.22
BALL_RADIUS_M = BALL_DIAMETER_M / 2
BALL_AREA_M2 = math.pi * BALL_RADIUS_M ** 2

# Tube
TUBE_ID_M = 0.226           # 226 mm
TUBE_LENGTH_M = 0.20        # 200 mm pressure section
BALL_FRONT_AREA_M2 = math.pi * BALL_RADIUS_M ** 2  # ball cross section in tube

# Pneumatic
GAMMA = 1.4                 # air adiabatic index
P_ATM_PA = 101325.0         # atmospheric pressure
VALVE_OPEN_MS = 30.0       # valve opening time
VALVE_CV = 0.85             # valve flow coefficient (screening)
LEAKAGE_COEFF = 0.05        # empirical leakage fraction
MECH_EFFICIENCY = 0.30      # fraction of gas work → ball KE (screening)

# Drag in tube (ball sliding along tube wall, not free flight)
TUBE_DRAG_COEFF = 1.1       # higher than free flight Cd due to wall friction

# Motor/spin (3-rotor radial-tangent, as spin module only)
WHEEL_RADIUS_M = 0.0315     # 6374 can radius ~31.5 mm
MU_ROLLING = 0.45           # rolling friction steel-rubber
PRESS_TIME_MS = 40.0        # duration motors can apply spin in tube


@dataclass
class PneumaticCase:
    name: str
    tank_pressure_bar_gauge: float   # gauge pressure
    tank_volume_l: float             # tank volume in litres
    tube_pressure_length_m: float    # length of pressurized tube section
    spin_mode: str                    # "STRAIGHT" / "TOPSPIN" / "LEFT_CURVE" / etc.
    spin_rpm_diff: int                # motor differential RPM for spin
    target_spin_rps: float = 0.0     # target ball spin rate (rps)
    launch_angle_deg: float = 8.0    # tube exit elevation
    notes: str = ""


@dataclass
class PneumaticResult:
    name: str
    avg_pressure_bar: float
    impulse_ns: float                 # pressure × time integral (Pa·s)
    launch_speed_mps: float
    spin_rate_rps: float
    range_m: float
    flight_time_s: float
    peak_height_m: float
    safety_margin: str
    notes: str


# ============================================================
# Pneumatic impulse model (simplified)
# ============================================================
def tank_air_mass_g(tank_pressure_bar_g: float, tank_volume_l: float) -> float:
    """
    Estimate air mass stored in tank at given pressure and volume.

    Uses ideal gas with atmospheric reference (101.325 kPa = 1.01325 bar absolute).
    Tank pressure gauge must be converted to absolute.
    """
    p_abs_bar = tank_pressure_bar_g + 1.01325
    # PV = nRT, m = n * M_air
    # At 20°C, air density at p_abs bar: rho = p_abs / (R_specific * T)
    R_specific = 287.05  # J/(kg·K) for dry air
    T = 293.15  # 20°C
    rho_kg_m3 = (p_abs_bar * 1e5) / (R_specific * T)
    volume_m3 = tank_volume_l / 1000.0
    return rho_kg_m3 * volume_m3 * 1000.0  # grams


def pneumatic_impulse(p_tank_bar_g: float, tube_length_m: float, ball_mass_kg: float,
                      tank_volume_l: float = 5.0) -> Tuple[float, float, float, float]:
    """
    Estimate gas work via isothermal expansion model.

    Tank at p0_abs with volume V0. Ball moves distance L down tube, expanding gas
    to V_new = V0 + A_ball * L. Work = p0 * V0 * ln(V_new / V0).

    Real launchers achieve ~20-50 m/s at 5-8 bar with tanks 5-50 L.
    MECH_EFFICIENCY scales this down to account for friction, leakage, gas
    heating losses, etc.

    Returns:
        avg_pressure_bar: average driving pressure during ball transit
        impulse_ns: F·t integral in Pa·s (rough estimate)
        v_exit_mps: estimated exit velocity
        work_j: total gas work in Joules
    """
    p_tank_pa = (p_tank_bar_g + 1.01325) * 1e5
    v0_m3 = tank_volume_l / 1000.0
    v_new_m3 = v0_m3 + BALL_FRONT_AREA_M2 * tube_length_m

    # Isothermal expansion work (ideal gas, isothermal)
    work_j_raw = p_tank_pa * v0_m3 * math.log(v_new_m3 / v0_m3) if v_new_m3 > v0_m3 else 0

    # Apply valve efficiency and mechanical efficiency
    work_j = work_j_raw * VALVE_CV * (1 - LEAKAGE_COEFF) * MECH_EFFICIENCY

    if work_j <= 0:
        return 0.0, 0.0, 0.0, 0.0

    v_exit = math.sqrt(2 * work_j / ball_mass_kg)
    # Average pressure estimate
    p_avg_pa = work_j / (BALL_FRONT_AREA_M2 * tube_length_m) if tube_length_m > 0 else 0
    t_transit = 2 * tube_length_m / v_exit if v_exit > 0.1 else 1.0
    impulse_ns = p_avg_pa * t_transit
    return p_avg_pa / 1e5, impulse_ns, v_exit, work_j


def apply_tube_drag(v_mps: float, tube_length_m: float) -> float:
    """
    Approximate tube-wall drag loss fraction over tube length.
    Returns speed at tube exit.
    """
    # Drag force ~ 0.5 * rho * Cd * A * v^2; integrate over distance
    # Simplification: assume average v ~ v_in * 0.7; loss fraction ~ k * L
    drag_loss_per_m = 0.04  # empirical screening
    loss = drag_loss_per_m * tube_length_m * 10
    return v_mps * (1 - min(loss, 0.4))


# ============================================================
# Spin from 3 motors (radial-tangent, very short impulse in tube)
# ============================================================
def motor_spin_rps(rpm_diff: int, ball_radius_m: float = BALL_RADIUS_M) -> float:
    """
    Differential RPM between two wheels (120° apart) creates ball spin.
    Simplified: spin rate rps ≈ surface speed difference / (2π · ball_radius)
    """
    surface_diff = (rpm_diff / 60.0) * (2 * math.pi * WHEEL_RADIUS_M)
    return surface_diff / (2 * math.pi * ball_radius_m)


# ============================================================
# Trajectory (post-tube free flight with drag + Magnus)
# ============================================================
def trajectory_pneumatic(v_exit: float, angle_deg: float, spin_rate_rps: float, spin_mode: str):
    """
    Free-flight trajectory after ball exits tube.
    """
    RHO = 1.225
    G = 9.81
    CD = 0.25

    a = math.radians(angle_deg)
    x = y = 0.0
    z = 0.35
    vx = v_exit * math.cos(a)
    vy = 0.0
    vz = v_exit * math.sin(a)
    dt = 0.002
    t = 0.0
    peak_z = z

    # Magnus coefficients (simplified)
    k_lat = 0.42
    k_vert = 0.30
    if spin_mode == "LEFT_CURVE":
        ay_s, az_s = k_lat * spin_rate_rps, 0.0
    if spin_mode == "RIGHT_CURVE":
        ay_s, az_s = -k_lat * spin_rate_rps, 0.0
    elif spin_mode == "TOPSPIN":
        ay_s, az_s = 0.0, -k_vert * spin_rate_rps
    elif spin_mode == "BACKSPIN":
        ay_s, az_s = 0.0, k_vert * spin_rate_rps
    else:
        ay_s, az_s = 0.0, 0.0

    while z >= 0 and x <= 80 and t <= 10.0:
        v = math.sqrt(vx * vx + vy * vy + vz * vz)
        drag = 0.5 * RHO * CD * BALL_AREA_M2 * v * v / BALL_MASS_KG
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


# ============================================================
# Main simulate
# ============================================================
def simulate_pneumatic(case: PneumaticCase) -> PneumaticResult:
    # Isothermal expansion work + efficiency
    p_avg_bar, impulse_ns, v_exit_calc, work_j = pneumatic_impulse(
        case.tank_pressure_bar_gauge,
        case.tube_pressure_length_m,
        BALL_MASS_KG,
        case.tank_volume_l,
    )
    if p_avg_bar <= 0:
        return PneumaticResult(
            case.name, 0, 0, 0, 0, 0, 0, 0,
            "INVALID: zero pressure", "no work done",
        )

    # Exit velocity (from isothermal model)
    v_exit = apply_tube_drag(v_exit_calc, case.tube_pressure_length_m)

    # Spin (motor module impulse while ball traverses tube)
    spin_rps = motor_spin_rps(case.spin_rpm_diff)

    # Free flight trajectory
    rng, lat, peak, tof = trajectory_pneumatic(
        v_exit, case.launch_angle_deg, spin_rps, case.spin_mode
    )

    # Safety margin heuristic: 8 bar = rated; test above 1.5x margin
    margin = case.tank_pressure_bar_gauge / 8.0
    if margin <= 0.6:
        safety = "OK: well below 8 bar rated"
    elif margin <= 1.0:
        safety = "CAUTION: at rated pressure; double-check dump valve"
    elif margin <= 1.5:
        safety = "OVER-RATED: above 8 bar; requires ASME vessel cert"
    else:
        safety = "DANGER: way above rating; STOP"

    return PneumaticResult(
        name=case.name,
        avg_pressure_bar=round(p_avg_bar, 2),
        impulse_ns=round(impulse_ns, 1),
        launch_speed_mps=round(v_exit, 2),
        spin_rate_rps=round(spin_rps, 2),
        range_m=round(rng, 1),
        flight_time_s=round(tof, 2),
        peak_height_m=round(peak, 2),
        safety_margin=safety,
        notes=case.notes,
    )


# ============================================================
# Cases
# ============================================================
def p0_pneumatic_cases() -> List[PneumaticCase]:
    return [
        # 5 bar / 5L tank — baseline
        PneumaticCase("pne_5bar_5L_straight", 5.0, 5.0, 0.20, "STRAIGHT", 0, 0, 8.0,
                       notes="Low-pressure baseline"),
        PneumaticCase("pne_5bar_5L_curve", 5.0, 5.0, 0.20, "LEFT_CURVE", 800, 0, 10.0,
                       notes="5 bar with curve spin"),
        # 8 bar / 5L tank — rated
        PneumaticCase("pne_8bar_5L_straight", 8.0, 5.0, 0.20, "STRAIGHT", 0, 0, 10.0,
                       notes="8 bar rated, straight"),
        PneumaticCase("pne_8bar_5L_topspin", 8.0, 5.0, 0.20, "TOPSPIN", 600, 0, 12.0,
                       notes="8 bar topspin for low arc"),
        # 8 bar / 20L tank + longer tube — for 50 m target
        PneumaticCase("pne_8bar_20L_50m", 8.0, 20.0, 0.40, "STRAIGHT", 0, 0, 15.0,
                       notes="Target 50m; 20L tank + 400mm tube"),
        # safety demos
        PneumaticCase("safety_12bar_warn", 12.0, 5.0, 0.20, "STRAIGHT", 0, 0, 10.0,
                       notes="Above 8 bar rated — should warn"),
    ]


def main() -> None:
    print("case,p_avg_bar,impulse_Ns,v_exit_mps,spin_rps,range_m,tof_s,peak_m,safety")
    for c in p0_pneumatic_cases():
        r = simulate_pneumatic(c)
        print(f"{r.name},{r.avg_pressure_bar},{r.impulse_ns},{r.launch_speed_mps},"
              f"{r.spin_rate_rps},{r.range_m},{r.flight_time_s},{r.peak_height_m},"
              f"{r.safety_margin}")


if __name__ == "__main__":
    main()