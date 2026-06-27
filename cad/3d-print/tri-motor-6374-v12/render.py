"""v12 渲染：参考图等比例放大"""

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
CRADLE_CENTER_R = TUBE_OR / 2 + MOTOR_D * 1.5
CRADLE_HUB_OD = MOTOR_D * 1.15
WHEEL_RIM_OR = MOTOR_D * 2.5
CRADLE_THICK = MOTOR_D * 0.25
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

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['spider_body'], label='Spider Body (scaled 2.5×)'),
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

    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_CENTER_R * math.cos(angle_rad)
        cy = CRADLE_CENTER_R * math.sin(angle_rad)

        # hub 沿 Z
        hub = C(MOTOR_L + 10, CRADLE_HUB_OD / 2) - C(MOTOR_L + 10.4, MOTOR_D / 2 + 0.5)
        hub = hub.translate([cx, cy, (TUBE_LEN - MOTOR_L - 10) / 2])

        # 3 条辐条
        spokes = Manifold()
        spoke_len = (WHEEL_RIM_OR - CRADLE_HUB_OD) / 2 - 6
        spoke_offset = (CRADLE_HUB_OD + WHEEL_RIM_OR) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 18, CRADLE_THICK), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     (TUBE_LEN - CRADLE_THICK) / 2])
            spokes = spokes + spoke

        # 外圈
        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 24) / 2)
        rim = rim.translate([cx, cy, (TUBE_LEN - CRADLE_THICK) / 2])

        body = body + hub + spokes + rim

    parts['spider_body'] = body
    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # Can
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = (CRADLE_CENTER_R - 15) * math.cos(angle_rad)
        cy = (CRADLE_CENTER_R - 15) * math.sin(angle_rad)
        can_r = MOTOR_D / 2 + 1
        can = C(MOTOR_D * 0.5, can_r) - C(MOTOR_D * 0.5 + 0.4, MOTOR_D / 2 + 0.3)
        can = can.rotate([0, math.pi / 2, 0])
        can = can.rotate([0, 0, angle_deg])
        can = can.translate([cx, cy, (TUBE_LEN - MOTOR_L) / 2])
        parts[f'motor_can_{i}'] = can

        stator_x = (CRADLE_CENTER_R + 25) * math.cos(angle_rad)
        stator_y = (CRADLE_CENTER_R + 25) * math.sin(angle_rad)
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
    render(parts, 'iso', 'assembly_v12_iso.png',
           f'Football Launcher v12 — Scaled 2.5× from reference\n3× 6374 | Ball 220mm | Wheel OD 158mm')
    render(parts, 'top', 'assembly_v12_top.png',
           f'Football Launcher v12 — Top View (3 cradles @ 120°)')


if __name__ == "__main__":
    main()