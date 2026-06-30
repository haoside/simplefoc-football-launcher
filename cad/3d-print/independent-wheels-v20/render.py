"""v20 渲染 — 独立 cradle 轮辋"""

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
TUBE_IR = BALL_R + 3
TUBE_OR = TUBE_IR + 6
TUBE_LEN = 200
CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R
CRADLE_RIM_OR = MOTOR_CENTER_R + 20
CRADLE_RIM_IR = MOTOR_CENTER_R - 25
CRADLE_RIM_THICK = 14
CRADLE_HUB_OD = MOTOR_D + 8
CRADLE_HUB_LEN = MOTOR_L + 6
CRADLE_BOLT_PCD = (CRADLE_RIM_OR + CRADLE_RIM_IR) / 2
N_MOTORS = 3
SEGMENTS = 96

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'cradle': '#ff8c00',
    'motor':  '#888888',
    'tube':   '#ff8c00',
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
        ax.view_init(elev=20, azim=45)
    elif view == 'top':
        ax.view_init(elev=88, azim=0)
    elif view == 'cradle':
        # 专门看一个 cradle 轮
        ax.view_init(elev=20, azim=30)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=13, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['cradle'], label='Cradle wheel (rim + 3 spokes + hub)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor'], label='Motor 6374'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['tube'], label='Tube + side plates'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['ball'], alpha=0.5, label='Ball 220mm'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=10)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {filename} — {os.path.getsize(out)//1024}KB")


def build_cradle_wheel(angle_deg, z_center):
    """构造单个 cradle 轮"""
    a = math.radians(angle_deg)
    cx = MOTOR_CENTER_R * math.cos(a)
    cy = MOTOR_CENTER_R * math.sin(a)

    parts = Manifold()

    # 外圈轮辋
    rim = C(CRADLE_RIM_THICK, CRADLE_RIM_OR / 2) - C(CRADLE_RIM_THICK + 0.4, CRADLE_RIM_IR / 2)
    # 4 颗螺栓孔
    for j in range(4):
        ra = math.radians(j * 90 + 45)
        bx = CRADLE_BOLT_PCD / 2 * math.cos(ra)
        by = CRADLE_BOLT_PCD / 2 * math.sin(ra)
        bolt = Manifold.cylinder(CRADLE_RIM_THICK + 2, 2.7, 16)
        bolt = bolt.translate([bx, by, 0])
        rim = rim - bolt
    parts = parts + rim

    # 中心 hub
    hub = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2) - C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    parts = parts + hub

    # 过渡盘
    trans = C(CRADLE_RIM_THICK, (CRADLE_HUB_OD + 8) / 2) - C(CRADLE_RIM_THICK + 0.4, CRADLE_HUB_OD / 2)
    parts = parts + trans

    # 3 条辐条
    spoke_len = (CRADLE_RIM_OR - CRADLE_HUB_OD) / 2 - 8
    spoke_offset = (CRADLE_HUB_OD + CRADLE_RIM_OR) / 4
    for j in range(3):
        sa = math.radians(j * 120)
        spoke = Manifold.cube((spoke_len, 18, 10), center=True)
        spoke = spoke.rotate([0, 0, sa])
        spoke = spoke.translate([spoke_offset * math.cos(sa),
                                 spoke_offset * math.sin(sa), 0])
        parts = parts + spoke

    # 平移到 cradle 中心位置
    parts = parts.translate([cx, cy, z_center])
    return parts


def build():
    parts = {}
    parts['tube'] = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        cradle = build_cradle_wheel(i * 120, TUBE_LEN / 2)
        parts[f'cradle_{i}'] = cradle

        # 电机（径向 X 轴）
        a = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(a)
        cy = MOTOR_CENTER_R * math.sin(a)
        stator = C(MOTOR_L, MOTOR_D / 2 - 4)
        stator = stator.rotate([0, math.pi / 2, 0])
        stator = stator.translate([cx, cy, TUBE_LEN / 2])
        parts[f'motor_{i}'] = stator

    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    for z_sign in [-1, 1]:
        plate = C(6, TUBE_OR + 5) - C(8, BALL_R + 3)
        plate = plate.translate([0, 0, z_sign * (TUBE_LEN / 2 + 3)])
        parts[f'plate_{z_sign}'] = plate

    return parts


def build_single_cradle_only():
    """单独展示一个 cradle 轮（对比参考图）"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    cradle = build_cradle_wheel(0, 0)

    # 电机（径向）
    stator = C(MOTOR_L, MOTOR_D / 2 - 4)
    stator = stator.rotate([0, math.pi / 2, 0])
    stator = stator.translate([0, 0, 0])

    for body, color, name in [(cradle, '#ff8c00', 'Cradle wheel'),
                                (stator, '#888888', 'Motor')]:
        v, f = manifold_to_mesh(body)
        triangles = v[f]
        mc = Poly3DCollection(triangles, alpha=0.9, facecolor=color,
                              edgecolor='#222222', linewidth=0.1)
        ax.add_collection3d(mc)

    all_v = []
    for body in [cradle, stator]:
        v, _ = manifold_to_mesh(body)
        all_v.append(v)
    all_v = np.vstack(all_v)
    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2 * 1.1
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    ax.view_init(elev=25, azim=35)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title('v20 Single Cradle Wheel (matches reference: rim + 3 spokes + hub)',
                  fontsize=13, fontweight='bold')

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "cradle_wheel_v20_single.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ cradle_wheel_v20_single.png — {os.path.getsize(out)//1024}KB")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v20_iso.png',
           f'Football Launcher v20 — 3 INDEPENDENT cradle wheels (matches reference)\nNo continuous outer shell (corrected from v19)')
    render(parts, 'top', 'assembly_v20_top.png',
           f'Football Launcher v20 — Top View (3 wheels @ 120° on tube)')
    build_single_cradle_only()


if __name__ == "__main__":
    main()