"""v11 渲染"""

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
TUBE_LEN = 150
N_MOTORS = 3
CRADLE_R = TUBE_OR + 50
CRADLE_HUB_OD = MOTOR_D + 8
WHEEL_RIM_OR = CRADLE_R + 40
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
        ax.view_init(elev=15, azim=45)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)
    elif view == 'side':
        ax.view_init(elev=0, azim=90)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['spider_body'], label='Spider Body (integrated)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_can'], label='Motor Can (radial, contacts ball)'),
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

    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)

        # hub 沿 Z 轴
        hub = C(MOTOR_L + 8, CRADLE_HUB_OD / 2) - C(MOTOR_L + 8.4, MOTOR_D / 2 + 0.5)
        hub = hub.translate([cx, cy, (TUBE_LEN - MOTOR_L - 8) / 2])

        # 3 条辐条（在 XY 平面内）
        spokes = Manifold()
        spoke_len = (WHEEL_RIM_OR - CRADLE_HUB_OD) / 2 - 6
        spoke_offset = (CRADLE_HUB_OD + WHEEL_RIM_OR) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 18, 8), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     (TUBE_LEN - 8) / 2])
            spokes = spokes + spoke

        # 外圈
        rim = C(8, WHEEL_RIM_OR / 2) - C(9, (WHEEL_RIM_OR - 24) / 2)
        rim = rim.translate([cx, cy, (TUBE_LEN - 8) / 2])

        body = body + hub + spokes + rim

    parts['spider_body'] = body
    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # 电机 can（径向从 hub 朝球）
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        # can 从 cradle hub 朝管中心（球）
        can_inner_x = (CRADLE_R - 15) * math.cos(angle_rad)
        can_inner_y = (CRADLE_R - 15) * math.sin(angle_rad)
        # can 长 30mm，沿径向
        can_r = MOTOR_D / 2 + 1
        can = C(30, can_r) - C(30.4, MOTOR_D / 2 + 0.3)
        # can 轴向 X（径向）
        can = can.rotate([0, math.pi / 2, 0])
        # 旋转到对应角度
        can = can.rotate([0, 0, angle_deg])
        # 平移到 cradle hub 内端（朝向管中心）
        can = can.translate([can_inner_x, can_inner_y, (TUBE_LEN - 8) / 2])
        parts[f'motor_can_{i}'] = can

        stator_x = (CRADLE_R + 20) * math.cos(angle_rad)
        stator_y = (CRADLE_R + 20) * math.sin(angle_rad)
        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4)
        stator = stator.translate([stator_x, stator_y, (TUBE_LEN - MOTOR_L) / 2])
        parts[f'motor_stator_{i}'] = stator

    for z_sign in [-1, 1]:
        plate = C(6, TUBE_OR + 5) - C(8, BALL_R + 3)
        plate = plate.translate([0, 0, z_sign * (TUBE_LEN / 2 + 3)])
        parts[f'side_plate_{z_sign}'] = plate

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v11_iso.png',
           f'Football Launcher v11 — TRUE 180° spider (axial motor)\n3× 6374 parallel to tube | Ball 220mm')
    render(parts, 'top', 'assembly_v11_top.png',
           f'Football Launcher v11 — Top View (3 disc cradles @ 120°)')


if __name__ == "__main__":
    main()