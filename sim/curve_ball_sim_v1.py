import math
from dataclasses import dataclass

G = 9.81
BALL_MASS = 0.43
BALL_DIAMETER = 0.22
BALL_RADIUS = BALL_DIAMETER / 2
BALL_AREA = math.pi * BALL_RADIUS * BALL_RADIUS
RHO0 = 1.225  # kg/m3 at 15C dry-ish sea level
CD = 0.25

@dataclass
class Env:
    name: str
    temp_c: float
    rh: float
    wind_speed: float
    wind_dir: str  # none/tail/head/left/right

@dataclass
class Preset:
    name: str
    speed: float
    angle_deg: float
    spin_mode: str
    spin_strength: float  # 0..1 rough

ENVS = [
    Env('E0', 20, 0.50, 0.0, 'none'),
    Env('E1', 16, 0.60, 2.0, 'none'),
    Env('E1_leftwind', 16, 0.60, 2.0, 'left'),
    Env('E1_rightwind', 16, 0.60, 2.0, 'right'),
    Env('E2', 6, 0.45, 4.0, 'none'),
    Env('E2_leftwind', 6, 0.45, 4.0, 'left'),
]

PRESETS = [
    Preset('straight_pass', 15.0, 10.0, 'straight', 0.0),
    Preset('light_left_curve', 15.0, 12.0, 'left_curve', 0.35),
    Preset('standard_left_curve', 16.5, 14.0, 'left_curve', 0.65),
    Preset('standard_right_curve', 16.5, 14.0, 'right_curve', 0.65),
]


def air_density(temp_c: float, rh: float) -> float:
    # simple engineering approximation: warmer / more humid => slightly lower density
    temp_k = temp_c + 273.15
    rho = RHO0 * (288.15 / temp_k) * (1.0 - 0.08 * rh)
    return rho


def wind_vector(speed: float, direction: str):
    # x: forward, y: left positive, z: up
    if direction == 'none':
        return (0.0, 0.0, 0.0)
    if direction == 'tail':
        return (speed, 0.0, 0.0)
    if direction == 'head':
        return (-speed, 0.0, 0.0)
    if direction == 'left':
        return (0.0, speed, 0.0)
    if direction == 'right':
        return (0.0, -speed, 0.0)
    return (0.0, 0.0, 0.0)


def spin_accel(preset: Preset):
    # rough engineering approximation, not CFD
    lateral = 0.0
    vertical = 0.0
    if preset.spin_mode == 'left_curve':
        lateral = 2.1 * preset.spin_strength
    elif preset.spin_mode == 'right_curve':
        lateral = -2.1 * preset.spin_strength
    elif preset.spin_mode == 'topspin':
        vertical = -1.5 * preset.spin_strength
    elif preset.spin_mode == 'backspin':
        vertical = 1.5 * preset.spin_strength
    return lateral, vertical


def simulate(env: Env, preset: Preset):
    rho = air_density(env.temp_c, env.rh)
    wx, wy, wz = wind_vector(env.wind_speed, env.wind_dir)
    lateral_spin, vertical_spin = spin_accel(preset)

    speed = preset.speed
    angle = math.radians(preset.angle_deg)
    x = y = 0.0
    z = 0.35  # launch height rough
    vx = speed * math.cos(angle)
    vy = 0.0
    vz = speed * math.sin(angle)
    dt = 0.002
    max_y = 0.0
    max_z = z
    t = 0.0

    while z >= 0 and x <= 40 and t <= 5.0:
        rvx = vx - wx
        rvy = vy - wy
        rvz = vz - wz
        rv = math.sqrt(rvx*rvx + rvy*rvy + rvz*rvz)
        drag = 0.5 * rho * CD * BALL_AREA * rv * rv / BALL_MASS
        if rv > 1e-6:
            ax_drag = -drag * rvx / rv
            ay_drag = -drag * rvy / rv
            az_drag = -drag * rvz / rv
        else:
            ax_drag = ay_drag = az_drag = 0.0

        ax = ax_drag
        ay = ay_drag + lateral_spin
        az = az_drag - G + vertical_spin

        vx += ax * dt
        vy += ay * dt
        vz += az * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        max_y = max(max_y, abs(y))
        max_z = max(max_z, z)
        t += dt

    impact_speed = math.sqrt(max(vx*vx + vy*vy + vz*vz, 0))
    return {
        'env': env.name,
        'preset': preset.name,
        'range_m': round(x, 1),
        'max_lateral_m': round(abs(y), 2),
        'impact_lateral_m': round(y, 2),
        'peak_height_m': round(max_z, 2),
        'flight_time_s': round(t, 2),
        'impact_speed_mps': round(impact_speed, 1),
    }


def main():
    for env in ENVS:
        for preset in PRESETS:
            print(simulate(env, preset))

if __name__ == '__main__':
    main()
