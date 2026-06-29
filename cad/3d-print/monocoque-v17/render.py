"""v17 渲染 — 两端加强筋 + can 滚轮"""

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
TUBE_LEN = MOTOR_L + 2 * 20
CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R
TUBE_OR = max(MOTOR_CENTER_R - MOTOR_CAN_R - 3, TUBE_IR + 8)
SHELL_OR = MOTOR_CENTER_R + MOTOR_CAN_R + 10
RIB_THICK = 18
N_MOTORS = 3
SEGMENTS = 96

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'shell':  '#ff8c00',
    'motor':  '#888888',
    'base':   '#333333',
    'ball':   '#00cc00',
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
        base_name = name.rsplit('_', 1)[0] if name.startswith(('motor_', 'base_')) else name
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
        ax.view_init(elev=8, azim=0)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['shell'], label='Monocoque shell + end ribs'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor'], label='Motor can = roller (mid section)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['base'], label='Stator base (wire-exit, fixed to ribs)'),
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

    # 两端加强筋
    for z_pos in [RIB_THICK / 2, TUBE_LEN - RIB_THICK / 2]:
        rib = C(RIB_THICK, SHELL_OR) - C(RIB_THICK + 0.4, TUBE_IR)
        rib = rib.translate([0, 0, z_pos])
        for i in range(N_MOTORS):
            angle = math.radians(i * 120)
            cx = MOTOR_CENTER_R * math.cos(angle)
            cy = MOTOR_CENTER_R * math.sin(angle)
            mount = C(RIB_THICK + 2, MOTOR_BASE_D / 2 + 0.5)
            mount = mount.translate([cx, cy, z_pos])
            rib = rib - mount
        body = body + rib

    # 管壁开槽
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        slot = Manifold.cube((MOTOR_CAN_R * 2 + 12, MOTOR_D + 4, MOTOR_L - 4), center=True)
        slot = slot.rotate([0, 0, i * 120])
        slot = slot.translate([(TUBE_IR + MOTOR_CENTER_R) / 2 * math.cos(angle),
                               (TUBE_IR + MOTOR_CENTER_R) / 2 * math.sin(angle),
                               TUBE_LEN / 2])
        body = body - slot

    # 中段连接筋（避开电机）
    for i in range(N_MOTORS):
        a_mid = math.radians(i * 120 + 60)
        web = Manifold.cube((SHELL_OR - TUBE_OR, 10, TUBE_LEN), center=True)
        web = web.rotate([0, 0, math.degrees(a_mid)])
        web = web.translate([(TUBE_OR + SHELL_OR) / 2 * math.cos(a_mid),
                             (TUBE_OR + SHELL_OR) / 2 * math.sin(a_mid), 0])
        body = body + web

    body = body - C(TUBE_LEN + 0.4, TUBE_IR)
    parts['shell'] = body

    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # 3 个电机：can（中段滚轮）+ 两端定子座
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)

        # can（中段，滚轮）
        can = C(MOTOR_L, MOTOR_CAN_R)
        can = can.translate([cx, cy, TUBE_LEN / 2])
        parts[f'motor_{i}'] = can

        # 两端定子座（出线侧，固定到加强筋）
        for z_pos in [RIB_THICK / 2, TUBE_LEN - RIB_THICK / 2]:
            base = C(RIB_THICK, MOTOR_BASE_D / 2)
            base = base.translate([cx, cy, z_pos])
            parts[f'base_{i}_{int(z_pos)}'] = base

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v17_iso.png',
           f'Football Launcher v17 — Both-end rib support\nMotor can=roller (mid), stator base fixed to end ribs (90°)')
    render(parts, 'top', 'assembly_v17_top.png',
           f'Football Launcher v17 — Top View (3 motors @ 120°, can contacts ball)')
    render(parts, 'side', 'assembly_v17_side.png',
           f'Football Launcher v17 — Side View (motor axis || tube, both ends on ribs)')


if __name__ == "__main__":
    main()