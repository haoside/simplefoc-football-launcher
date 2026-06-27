"""
v5 一体化 + 辐条轮渲染
"""

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
TUBE_OR = 130
TUBE_LEN = 90
WHEEL_OR = 165
WHEEL_HUB_OD = MOTOR_D + 14
WHEEL_HUB_LEN = MOTOR_L + 10
MOTOR_SHAFT_D = 8
WHEEL_N_SPOKES = 3
N_MOTORS = 3
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'spider_body': '#ff8c00',
    'motor_can':   '#c0c0c0',
    'side_plate':  '#1f77b4',
    'ball':        '#00cc00',
    'motor_stator':'#444444',
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
                    name.startswith('motor_stator_') else name
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
        ax.view_init(elev=25, azim=45)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)
    elif view == 'side':
        ax.view_init(elev=0, azim=90)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['spider_body'], label='Spider Body (integrated + spoked wheel)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_can'], label='Motor Can'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_stator'], label='Motor Stator'),
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

    # 简化版主体（用于渲染）
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    wheel_center_r = (WHEEL_HUB_OD + TUBE_OR) / 2 + 5

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = wheel_center_r * math.cos(angle_rad)
        cy = wheel_center_r * math.sin(angle_rad)

        # 简化辐条轮
        # hub
        hub = C(WHEEL_HUB_LEN, WHEEL_HUB_OD / 2) - C(WHEEL_HUB_LEN + 0.4, MOTOR_D / 2 + 2)
        hub = hub.translate([cx, cy, 0])

        # 3 条辐条
        spokes = Manifold()
        spoke_len = (WHEEL_OR - WHEEL_HUB_OD) / 2 - 5
        spoke_off = (WHEEL_HUB_OD + WHEEL_OR) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 14, 8), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_off * math.cos(sa), cy + spoke_off * math.sin(sa), 0])
            spokes = spokes + spoke

        # 外圈
        rim = C(8, WHEEL_OR / 2) - C(9, (WHEEL_OR - 20) / 2)
        rim = rim.translate([cx, cy, 0])

        wheel = hub + spokes + rim

        # 连接肋
        rib = Manifold.cube((TUBE_OR, 20, 8), center=True)
        rib = rib.rotate([0, 0, angle_deg])
        rib = rib.translate([(TUBE_OR + wheel_center_r - WHEEL_HUB_OD / 2) / 2 * math.cos(angle_rad) * 1.5,
                            (TUBE_OR + wheel_center_r - WHEEL_HUB_OD / 2) / 2 * math.sin(angle_rad) * 1.5, 0])

        body = body + wheel + rib

    parts['spider_body'] = body

    # 球
    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # 电机
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = wheel_center_r * math.cos(angle_rad)
        cy = wheel_center_r * math.sin(angle_rad)

        can_r = MOTOR_D / 2 + 1
        can = C(MOTOR_L, can_r) - C(MOTOR_L + 0.4, MOTOR_D / 2 + 0.3)
        can = can.translate([cx, cy, 0])
        parts[f'motor_can_{i}'] = can

        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4)
        stator = stator.translate([cx * 1.15, cy * 1.15, 0])
        parts[f'motor_stator_{i}'] = stator

    # 端板
    for z_sign in [-1, 1]:
        plate = C(6, TUBE_OR + 5) - C(8, BALL_R + 3)
        plate = plate.translate([0, 0, z_sign * (TUBE_LEN / 2 + 3)])
        parts[f'side_plate_{z_sign}'] = plate

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v5_iso.png',
           f'Football Launcher v5 — INTEGRATED with SPOKED WHEEL\n3× 6374 @ 120° | Ball 220mm')
    render(parts, 'top', 'assembly_v5_top.png',
           f'Football Launcher v5 — Top View (Spoked Wheel Pattern)\n3× motors @ 120°')
    render(parts, 'side', 'assembly_v5_side.png',
           f'Football Launcher v5 — Side View')


if __name__ == "__main__":
    main()