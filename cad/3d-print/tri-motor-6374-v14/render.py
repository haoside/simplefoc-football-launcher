"""v14 渲染：修正版 — 径向电机 + 平面飞轮盘"""

import numpy as np
from manifold3d import Manifold
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math
import os

BALL_D = 220
BALL_R = BALL_D / 2
MOTOR_D = 63
MOTOR_L = 74
TUBE_IR = BALL_R + 3
TUBE_OR = 140
TUBE_LEN = 200
N_MOTORS = 3
CRADLE_R = TUBE_OR / 2 + 55
FLYWHEEL_D = 50
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'spider_body': '#ff8c00',
    'motor_stator':'#444444',
    'side_plate':  '#1f77b4',
    'ball':        '#00cc00',
    'flywheel':    '#888888',
}


def C(h, r):
    return Manifold.cylinder(h, r, r, SEGMENTS)


def manifold_to_mesh(body):
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    return v, f


def render(parts, view, filename, title):
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    for name, body in parts.items():
        v, f = manifold_to_mesh(body)
        triangles = v[f]
        base_name = name.rsplit('_', 1)[0] if name.startswith('motor_can_') or \
                    name.startswith('motor_stator_') or name.startswith('flywheel_') else name
        color = COLORS.get(base_name, '#888888')
        alpha = 0.4 if name == 'ball' else 0.9
        mc = Poly3DCollection(triangles, alpha=alpha, facecolor=color,
                              edgecolor='#222222', linewidth=0.05)
        ax.add_collection3d(mc)

    all_v = []
    for body in parts.values():
        v, _ = manifold_to_mesh(body)
        all_v.append(v)
    all_v = np.vstack(all_v)

    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2 * 1.05
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2

    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    if view == 'iso':
        ax.view_init(elev=20, azim=45)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)
    elif view == 'side':
        ax.view_init(elev=0, azim=90)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['spider_body'], label='Spider Body'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_stator'], label='Motor'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['flywheel'], label='Flywheel Disc'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['side_plate'], label='Side Plate'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['ball'], alpha=0.5, label='Ball (220mm)'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=10)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {filename} — {os.path.getsize(out)//1024}KB")


def build():
    parts = {}

    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)

        # hub
        hub = C(MOTOR_L + 10, (MOTOR_D + 8) / 2) - C(MOTOR_L + 10.4, MOTOR_D / 2 + 0.5)
        hub = hub.translate([cx, cy, (TUBE_LEN - MOTOR_L - 10) / 2])

        # 3 条辐条
        spokes = Manifold()
        spoke_len = (160 - (MOTOR_D + 8)) / 2 - 5
        spoke_offset = ((MOTOR_D + 8) + 160) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 16, 10), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     (TUBE_LEN - 10) / 2])
            spokes = spokes + spoke

        # 外圈
        rim = C(10, 160 / 2) - C(11, (160 - 20) / 2)
        rim = rim.translate([cx, cy, (TUBE_LEN - 10) / 2])

        body = body + hub + spokes + rim

        # 飞轮盘（关键修正）
        # 盘面在径向 X 方向（垂直于管轴 Z）
        # 盘中心在 (cx + R + FLYWHEEL_D/2, cy, TUBE_LEN/2)
        flywheel_cx = cx * (CRADLE_R + FLYWHEEL_D / 2 + 5) / CRADLE_R
        flywheel_cy = cy * (CRADLE_R + FLYWHEEL_D / 2 + 5) / CRADLE_R
        flywheel = C(8, FLYWHEEL_D / 2)
        # 轴向 X
        flywheel = flywheel.rotate([0, math.pi / 2, 0])
        flywheel = flywheel.translate([flywheel_cx, flywheel_cy, (TUBE_LEN) / 2])
        body = body + flywheel

    parts['spider_body'] = body
    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        stator_cx = (CRADLE_R + 5) * math.cos(angle_rad)
        stator_cy = (CRADLE_R + 5) * math.sin(angle_rad)
        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4)
        stator = stator.rotate([0, math.pi / 2, 0])
        stator = stator.rotate([0, 0, angle_deg])
        stator = stator.translate([stator_cx, stator_cy, (TUBE_LEN - MOTOR_L) / 2])
        parts[f'motor_stator_{i}'] = stator

    for z_sign in [-1, 1]:
        plate = C(6, TUBE_OR + 5) - C(8, BALL_R + 3)
        plate = plate.translate([0, 0, z_sign * (TUBE_LEN / 2 + 3)])
        parts[f'side_plate_{z_sign}'] = plate

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v14_iso.png',
           f'Football Launcher v14 — Radial motor + Flywheel disc\n(launches ball along tube axis)')
    render(parts, 'side', 'assembly_v14_side.png',
           f'Football Launcher v14 — Side view showing flywheel alignment')


if __name__ == "__main__":
    main()