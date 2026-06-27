"""v9 渲染"""

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
TUBE_LEN = 200
N_MOTORS = 3
CRADLE_CENTER_R = TUBE_OR + 35
CRADLE_LEN = MOTOR_L + 8
CRADLE_OD = MOTOR_D + 14
WHEEL_RIM_OR = CRADLE_CENTER_R + 30
WHEEL_THICK = 6
WHEEL_N_SPOKES = 3
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'launch_tube': '#ff8c00',
    'motor_cradle': '#ff8c00',
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
        ax.view_init(elev=20, azim=45)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['launch_tube'], label='Launch Tube (with can holes)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_cradle'], label='Motor Cradle (external mount)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_can'], label='Motor Can (longer, passes through tube)'),
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

    # 管（带 can 孔）
    tube = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)
    for i in range(N_MOTORS):
        a = math.radians(i * 120)
        cx = (TUBE_OR + TUBE_IR) / 2 * math.cos(a)
        cy = (TUBE_OR + TUBE_IR) / 2 * math.sin(a)
        hole = C(TUBE_LEN + 2, (MOTOR_D + 4) / 2)
        hole = hole.translate([cx, cy, 0])
        tube = tube - hole
    parts['launch_tube'] = tube

    # 3 个 cradle（外挂）
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_CENTER_R * math.cos(angle_rad)
        cy = CRADLE_CENTER_R * math.sin(angle_rad)

        # hub
        hub_outer = C(CRADLE_LEN, CRADLE_OD / 2).rotate([0, math.pi / 2, 0])
        hub_inner = C(CRADLE_LEN + 0.4, MOTOR_D / 2 + 0.5).rotate([0, math.pi / 2, 0])
        hub = hub_outer - hub_inner
        hub = hub.rotate([0, 0, angle_deg])
        hub = hub.translate([cx, cy, 0])

        # 内圈连接环
        inner = C(WHEEL_THICK, TUBE_OR + 1) - C(WHEEL_THICK + 0.4, TUBE_OR - 4)
        inner = inner.translate([cx * 0.85, cy * 0.85, 0])

        # 3 条辐条
        spokes = Manifold()
        spoke_len = (WHEEL_RIM_OR - CRADLE_OD) / 2 - 5
        spoke_offset = (CRADLE_OD + WHEEL_RIM_OR) / 4
        for j in range(WHEEL_N_SPOKES):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((WHEEL_THICK, spoke_len, 14), center=True)
            spoke = spoke.rotate([sa, 0, 0])
            spoke = spoke.translate([cx, spoke_offset * math.cos(sa) * math.cos(angle_rad),
                                     spoke_offset * math.cos(sa) * math.sin(angle_rad)])
            spokes = spokes + spoke

        # 外圈
        rim = C(WHEEL_THICK, WHEEL_RIM_OR / 2).rotate([0, math.pi / 2, 0]) - \
              C(WHEEL_THICK + 0.4, (WHEEL_RIM_OR - 20) / 2).rotate([0, math.pi / 2, 0])
        rim = rim.rotate([0, 0, angle_deg])
        rim = rim.translate([cx, cy, 0])

        parts[f'motor_cradle_{i}'] = hub + inner + spokes + rim

    # 球
    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # 电机外壳（径向，长度足以穿过管壁）
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_CENTER_R * math.cos(angle_rad)
        cy = CRADLE_CENTER_R * math.sin(angle_rad)
        can_r = MOTOR_D / 2 + 1
        can = C(MOTOR_L + 30, can_r) - C(MOTOR_L + 30.4, MOTOR_D / 2 + 0.3)
        can = can.rotate([0, math.pi / 2, 0])
        can = can.rotate([0, 0, angle_deg])
        can = can.translate([cx, cy, 0])
        parts[f'motor_can_{i}'] = can

        stator_x = (CRADLE_CENTER_R + 10) * math.cos(angle_rad)
        stator_y = (CRADLE_CENTER_R + 10) * math.sin(angle_rad)
        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4).rotate([0, math.pi / 2, 0])
        stator = stator.rotate([0, 0, angle_deg])
        stator = stator.translate([stator_x, stator_y, 0])
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
    render(parts, 'iso', 'assembly_v9_iso.png',
           f'Football Launcher v9 — Modular (separate cradle from tube)\n3× 6374 radial | Ball 220mm')
    render(parts, 'top', 'assembly_v9_top.png',
           f'Football Launcher v9 — Top View (120° cradle layout)')


if __name__ == "__main__":
    main()