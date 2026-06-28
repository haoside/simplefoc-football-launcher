"""v15 渲染 — 气压主线架构"""

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
TUBE_LEN = 400
PRESS_END_LEN = 30
PRESS_END_OR = TUBE_OR + 15
N_MOTORS = 3
CRADLE_R = TUBE_OR / 2 + 55
FLYWHEEL_D = 50
HUB_OD = MOTOR_D + 8
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

COLORS = {
    'tube':         '#ff8c00',
    'pressure_end': '#cc4400',  # 红褐色 — 压力端
    'cradle':       '#ff8c00',
    'output_end':   '#1f77b4',
    'motor':        '#444444',
    'flywheel':     '#888888',
    'ball':         '#00cc00',
    'gas_inlet':    '#ffff00',  # 黄色 — 进气口占位
}


def C(h, r):
    return Manifold.cylinder(h, r, r, SEGMENTS)


def manifold_to_mesh(body):
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    return v, f


def render(parts, view, filename, title):
    fig = plt.figure(figsize=(18, 12))
    ax = fig.add_subplot(111, projection='3d')

    for name, body in parts.items():
        v, f = manifold_to_mesh(body)
        triangles = v[f]
        base_name = name.rsplit('_', 1)[0] if name.startswith('motor_') or \
                    name.startswith('flywheel_') else name
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
    elif view == 'side':
        ax.view_init(elev=15, azim=0)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['tube'], label='Launch Tube (400mm, gas channel)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['pressure_end'], label='Pressure End Cap (gas inlet)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['cradle'], label='Motor Cradle (spin module)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor'], label='Motor 6374'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['flywheel'], label='Flywheel Disc (ball contact)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['output_end'], label='Output End Plate + safety net'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['gas_inlet'], label='Gas Inlet (placeholder)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['ball'], alpha=0.5, label='Ball (220mm)'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=9)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {filename} — {os.path.getsize(out)//1024}KB")


def build():
    parts = {}

    # 主发射管（z = 0 到 z = TUBE_LEN）
    parts['tube'] = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 压力端（z = -PRESS_END_LEN 到 z = 0）
    pressure_end = C(PRESS_END_LEN, PRESS_END_OR)
    pressure_end = pressure_end - C(PRESS_END_LEN + 2, 12.5)  # 进气口
    pressure_end = pressure_end.translate([0, 0, -PRESS_END_LEN / 2])
    parts['pressure_end'] = pressure_end

    # 出球端（z = TUBE_LEN）
    out_plate = C(5, TUBE_OR + 20) - C(7, BALL_R + 3)
    out_plate = out_plate.translate([0, 0, TUBE_LEN + 2.5])
    parts['output_end'] = out_plate

    # 3 个电机 cradle + 飞轮
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)

        # Cradle 主体（盘状，XY 平面）
        cradle_hub = C(MOTOR_L + 10, HUB_OD / 2) - C(MOTOR_L + 10.4, MOTOR_D / 2 + 0.5)
        cradle_hub = cradle_hub.translate([cx, cy, TUBE_LEN / 2])

        # 3 条辐条
        spokes = Manifold()
        spoke_len = (160 - HUB_OD) / 2 - 5
        spoke_offset = (HUB_OD + 160) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 16, 10), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     TUBE_LEN / 2])
            spokes = spokes + spoke

        # 外圈
        rim = C(10, 160 / 2) - C(11, (160 - 20) / 2)
        rim = rim.translate([cx, cy, TUBE_LEN / 2])

        # 飞轮盘（径向）
        flywheel = C(8, FLYWHEEL_D / 2)
        flywheel = flywheel.rotate([0, math.pi / 2, 0])  # 轴向 X
        # 计算飞轮位置（cradle 外侧 X+方向）
        fw_x = (cx / CRADLE_R) * (CRADLE_R + FLYWHEEL_D / 2 + 5)
        fw_y = (cy / CRADLE_R) * (CRADLE_R + FLYWHEEL_D / 2 + 5)
        flywheel = flywheel.translate([fw_x, fw_y, TUBE_LEN / 2])

        parts[f'cradle_{i}'] = cradle_hub + spokes + rim

        # 电机（简化）
        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4)
        stator = stator.rotate([0, math.pi / 2, 0])
        stator = stator.translate([cx + 5 * math.cos(angle_rad),
                                   cy + 5 * math.sin(angle_rad),
                                   TUBE_LEN / 2])
        parts[f'motor_{i}'] = stator

        parts[f'flywheel_{i}'] = flywheel

    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    # 进气口占位（黄色环）
    gas_inlet = C(40, 25) - C(41, 20)
    gas_inlet = gas_inlet.translate([0, 0, -PRESS_END_LEN - 15])
    parts['gas_inlet'] = gas_inlet

    return parts


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    parts = build()
    render(parts, 'iso', 'assembly_v15_iso.png',
           f'Football Launcher v15 — PNEUMATIC mainline\nCompressed air + 3-motor spin module')
    render(parts, 'side', 'assembly_v15_side.png',
           f'Football Launcher v15 — Side view (gas inlet on left, ball exit on right)')


if __name__ == "__main__":
    main()