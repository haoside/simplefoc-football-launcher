"""v18 渲染 — 切向电机轴"""

import numpy as np
from manifold3d import Manifold
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math
import os

BALL_D = 220
BALL_R = BALL_D / 2
MOTOR_D = 63
MOTOR_CAN_R = MOTOR_D / 2
MOTOR_L = 74
MOTOR_BASE_D = 40
TUBE_IR = BALL_R + 3
TUBE_LEN = 160
CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R
TUBE_OR = TUBE_IR + 8
SHELL_OR = MOTOR_CENTER_R + MOTOR_CAN_R + 12
SUPPORT_THICK = 10
SUPPORT_GAP = MOTOR_L + 2 * SUPPORT_THICK
N_MOTORS = 3
SEGMENTS = 96

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'shell':  '#ff8c00',
    'motor':  '#888888',
    'ball':   '#00cc00',
    'arrow':  '#cc0000',
}


def C(h, r):
    return Manifold.cylinder(h, r, r, SEGMENTS)


def tangent_cylinder(h, r, angle_deg):
    cyl = C(h, r)
    cyl = cyl.rotate([90, 0, 0])
    cyl = cyl.rotate([0, 0, angle_deg])
    return cyl


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
        base_name = name.rsplit('_', 1)[0] if name.startswith('motor_') else name
        color = COLORS.get(base_name, '#888888')
        alpha = 0.35 if name == 'ball' else 0.9
        mc = Poly3DCollection(triangles, alpha=alpha, facecolor=color,
                              edgecolor='#222222', linewidth=0.08)
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
        ax.view_init(elev=22, azim=45)
    elif view == 'top':
        ax.view_init(elev=88, azim=0)
    elif view == 'side':
        ax.view_init(elev=10, azim=0)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm) — 发射方向')
    ax.set_title(title, fontsize=13, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['shell'], label='Monocoque shell + tangent supports'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor'], label='Motor can = roller (TANGENT axis)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['ball'], alpha=0.5, label='Ball 220mm'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=10)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {filename} — {os.path.getsize(out)//1024}KB")


def build():
    parts = {}

    # 壳体（简化重建）
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)
    outer = C(TUBE_LEN, SHELL_OR) - C(TUBE_LEN + 0.4, SHELL_OR - 6)
    body = body + outer

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = MOTOR_CENTER_R * math.cos(angle_rad)
        cy = MOTOR_CENTER_R * math.sin(angle_rad)
        cz = TUBE_LEN / 2
        tx = -math.sin(angle_rad)
        ty = math.cos(angle_rad)

        # 两块支撑板
        for sign in [-1, 1]:
            plate = Manifold.cube((SHELL_OR - TUBE_OR + 5, SUPPORT_THICK, MOTOR_D + 20), center=True)
            plate = plate.rotate([0, 0, angle_deg])
            plate = plate.translate([
                (TUBE_OR + SHELL_OR) / 2 * math.cos(angle_rad) + sign * tx * (SUPPORT_GAP / 2),
                (TUBE_OR + SHELL_OR) / 2 * math.sin(angle_rad) + sign * ty * (SUPPORT_GAP / 2),
                cz
            ])
            body = body + plate

        # 管壁开槽
        slot = Manifold.cube((MOTOR_D + 6, MOTOR_L + 4, MOTOR_D + 2), center=True)
        slot = slot.rotate([0, 0, angle_deg])
        slot = slot.translate([(TUBE_IR + MOTOR_CENTER_R) / 2 * math.cos(angle_rad),
                               (TUBE_IR + MOTOR_CENTER_R) / 2 * math.sin(angle_rad),
                               cz])
        body = body - slot

    body = body - C(TUBE_LEN + 0.4, TUBE_IR)
    parts['shell'] = body

    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # 3 个电机 can（切向轴）
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = MOTOR_CENTER_R * math.cos(angle_rad)
        cy = MOTOR_CENTER_R * math.sin(angle_rad)
        cz = TUBE_LEN / 2
        can = tangent_cylinder(MOTOR_L, MOTOR_CAN_R, angle_deg)
        can = can.translate([cx, cy, cz])
        parts[f'motor_{i}'] = can

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v18_iso.png',
           f'Football Launcher v18 — TANGENT motor axis (correct)\nCan rolls → +Z contact velocity → ball launches')
    render(parts, 'top', 'assembly_v18_top.png',
           f'Football Launcher v18 — Top View (3 motors TANGENT @ 120°)')
    render(parts, 'side', 'assembly_v18_side.png',
           f'Football Launcher v18 — Side View (tangent rollers drive ball +Z)')


if __name__ == "__main__":
    main()