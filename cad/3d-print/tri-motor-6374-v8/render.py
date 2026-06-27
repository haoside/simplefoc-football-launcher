"""
v8 渲染
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
TUBE_LEN = 180
MOTOR_CENTER_R = TUBE_OR - 5  # 125mm
CRADLE_RIM_OR = MOTOR_CENTER_R + 55
CRADLE_HUB_OD = MOTOR_D + 6
CRADLE_HUB_LEN = MOTOR_L + 4
CRADLE_THICK = 8
CRADLE_N_SPOKES = 3
N_MOTORS = 3
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
    elif view == 'side':
        ax.view_init(elev=0, azim=90)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['launch_tube'], label='Launch Tube'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_cradle'], label='Motor Cradle (single-disc)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor_can'], label='Motor Can (with cross groove)'),
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
    parts['launch_tube'] = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = MOTOR_CENTER_R * math.cos(angle_rad)
        cy = MOTOR_CENTER_R * math.sin(angle_rad)

        # hub 径向
        hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2).rotate([0, math.pi / 2, 0])
        hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5).rotate([0, math.pi / 2, 0])
        hub = hub_outer - hub_inner
        hub = hub.rotate([0, 0, angle_deg])
        hub = hub.translate([cx, cy, 0])

        # 3 条辐条
        spokes = Manifold()
        spoke_len = (CRADLE_RIM_OR - CRADLE_HUB_OD) / 2 - 5
        spoke_offset = (CRADLE_HUB_OD + CRADLE_RIM_OR) / 4
        for j in range(CRADLE_N_SPOKES):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((CRADLE_THICK, spoke_len, 14), center=True)
            spoke = spoke.rotate([sa, 0, 0])
            spoke = spoke.translate([cx, spoke_offset * math.cos(sa) * math.cos(angle_rad),
                                     spoke_offset * math.cos(sa) * math.sin(angle_rad)])
            spokes = spokes + spoke

        # 外圈
        rim = C(CRADLE_THICK, CRADLE_RIM_OR / 2).rotate([0, math.pi / 2, 0]) - \
              C(CRADLE_THICK + 0.4, (CRADLE_RIM_OR - 20) / 2).rotate([0, math.pi / 2, 0])
        rim = rim.rotate([0, 0, angle_deg])
        rim = rim.translate([cx, cy, 0])

        parts[f'motor_cradle_{i}'] = hub + spokes + rim

    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        # can 嵌入管壁
        cx = (MOTOR_CENTER_R + 10) * math.cos(angle_rad)
        cy = (MOTOR_CENTER_R + 10) * math.sin(angle_rad)
        can_r = MOTOR_D / 2 + 1
        can = C(MOTOR_L + 8, can_r) - C(MOTOR_L + 8.4, MOTOR_D / 2 + 0.3)
        can = can.rotate([0, math.pi / 2, 0])
        can = can.rotate([0, 0, angle_deg])
        can = can.translate([cx, cy, 0])
        parts[f'motor_can_{i}'] = can

        stator_x = (MOTOR_CENTER_R + 25) * math.cos(angle_rad)
        stator_y = (MOTOR_CENTER_R + 25) * math.sin(angle_rad)
        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4).rotate([0, math.pi / 2, 0])
        stator = stator.rotate([0, 0, angle_deg])
        stator = stator.translate([stator_x, stator_y, 0])
        parts[f'motor_stator_{i}'] = stator

    for z_sign in [-1, 1]:
        plate = C(6, TUBE_OR + 5) - C(8, BALL_R + 3)
        plate = plate.translate([0, 0, z_sign * (TUBE_LEN / 2 + 3)])
        parts[f'side_plate_{z_sign}'] = plate

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v8_iso.png',
           f'Football Launcher v8 — Single-disc cradle, can contacts ball\n3× 6374 radial | Ball 220mm')
    render(parts, 'top', 'assembly_v8_top.png',
           f'Football Launcher v8 — Top View (cross-groove cans visible)')


if __name__ == "__main__":
    main()