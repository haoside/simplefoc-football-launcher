"""
Football Launcher — 整体组装图渲染
manifold3d 构建装配体，matplotlib 3D 渲染
"""

import numpy as np
from manifold3d import Manifold
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import math
import os

# ============================================================
# 参数（与 design_v2.py 一致）
# ============================================================
BALL_D = 220
BALL_R = BALL_D / 2

MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 140
WALL = TUBE_OR - TUBE_IR       # 27mm
BOSS_EXTRA = 20
BOSS_OR = TUBE_OR + BOSS_EXTRA # 160mm
MOTOR_HOLE_DIA = MOTOR_D + 2

FRAME_LEN = 100
MOTOR_CENTER_R = BALL_R + MOTOR_D / 2 + 5   # 146.5mm

# 辐条轮参数
CRADLE_OD = MOTOR_CENTER_R + 15
CRADLE_THICK = 8
CRADLE_RIM_W = 8
CRADLE_HUB_OD = MOTOR_D + 8
CRADLE_HUB_LEN = MOTOR_L + 10
CRADLE_N_SPOKES = 4
CRADLE_SPOKE_W = 6
CRADLE_SPOKE_T = 6

BOLT_D = 5
N_MOTORS = 3
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")

# 零件颜色
COLORS = {
    'launch_tube':  '#ff7f0e',      # 橙色（参考图同色）
    'motor_cradle': '#ff7f0e',      # 橙色（参考图同色）
    'motor_can':    '#2ca02c',       # 绿色
    'side_plate':   '#1f77b4',       # 蓝色
    'stator_holder':'#d62728',       # 红色
    'bridge_rib':   '#9467bd',       # 紫色
    'ball':         '#ffffff',       # 白色（球）
    'motor_stator': '#7f7f7f',       # 灰色（电机本体）
}


# ============================================================
# 装配体构建 — 在同一个坐标系中组合所有零件
# ============================================================
def build_assembly():
    """
    装配体：所有零件按正确位置组合
    返回 dict of {part_name: manifold}
    """
    parts = {}

    # ===== Launch Tube（简化版 — 只有孔） =====
    tube = Manifold.cylinder(FRAME_LEN, TUBE_OR, TUBE_OR, SEGMENTS) - \
           Manifold.cylinder(FRAME_LEN + 0.4, TUBE_IR, TUBE_IR, SEGMENTS)

    # 3 个电机位大圆孔
    hole_center_r = (TUBE_OR + TUBE_IR) / 2
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = hole_center_r * math.cos(angle)
        cy = hole_center_r * math.sin(angle)
        hole = Manifold.cylinder(FRAME_LEN + 2, MOTOR_HOLE_DIA / 2, MOTOR_HOLE_DIA / 2, SEGMENTS)
        hole = hole.translate([cx, cy, 0])
        tube = tube - hole

    # 螺栓孔（每组 4 个 M4）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        pcd = TUBE_OR + 5
        for j in range(4):
            ja = math.radians(j * 90 + 45)
            jx = pcd * math.cos(angle + ja)
            jy = pcd * math.sin(angle + ja)
            bolt = Manifold.cylinder(8, MOTOR_HOLE_D / 2 + 0.1, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([jx, jy, 0])
            tube = tube - bolt

    parts['launch_tube'] = tube

    # ===== Motor Cradle（电机辐条座）× 3 =====
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)

        # 中心轮毂（容纳电机，轴向平行于管长即 z 轴）
        hub = Manifold.cylinder(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2, CRADLE_HUB_OD / 2, SEGMENTS) - \
              Manifold.cylinder(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5, MOTOR_D / 2 + 0.5, SEGMENTS)

        # 电机轴孔
        hub = hub - Manifold.cylinder(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, MOTOR_SHAFT_D / 2 + 0.5, 16)

        # 电机端面螺栓孔
        for j in range(4):
            ja = math.radians(j * 90)
            jx = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            jy = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            hub = hub - Manifold.cylinder(CRADLE_HUB_LEN + 2, MOTOR_HOLE_D / 2 + 0.1, MOTOR_HOLE_D / 2 + 0.1, 16).translate([jx, jy, 0])

        # 外缘环
        rim = Manifold.cylinder(CRADLE_THICK, CRADLE_OD / 2, CRADLE_OD / 2, SEGMENTS) - \
              Manifold.cylinder(CRADLE_THICK + 0.4, CRADLE_OD / 2 - CRADLE_RIM_W, CRADLE_OD / 2 - CRADLE_RIM_W, SEGMENTS)

        # 外缘螺栓孔
        for j in range(4):
            ja = math.radians(j * 90 + 45)
            bx = (CRADLE_OD - CRADLE_RIM_W / 2) * math.cos(ja)
            by = (CRADLE_OD - CRADLE_RIM_W / 2) * math.sin(ja)
            rim = rim - Manifold.cylinder(CRADLE_THICK + 2, BOLT_D / 2 + 0.15, BOLT_D / 2 + 0.15, 16).translate([bx, by, 0])

        # 4 条辐条
        spokes = Manifold()
        spoke_len = (CRADLE_OD - CRADLE_HUB_OD) / 2 - CRADLE_RIM_W / 2
        spoke_offset = (CRADLE_HUB_OD + CRADLE_OD) / 4
        for j in range(CRADLE_N_SPOKES):
            ja = math.radians(j * 90)
            spoke = Manifold.cube((spoke_len, CRADLE_SPOKE_W, CRADLE_SPOKE_T), center=True)
            spoke = spoke.translate([spoke_offset, 0, 0])
            spoke = spoke.rotate([0, 0, ja])
            spokes = spokes + spoke

        cradle = hub + spokes + rim
        cradle = cradle.translate([cx, cy, 0])
        parts[f'motor_cradle_{i}'] = cradle

    # ===== Motor Can（电机外壳）× 3 =====
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)

        # 电机外壳（穿过管壁，外壳外缘接触球面）
        # 外壳轴向沿径向（指向管中心）
        can_r_out = MOTOR_D / 2 + 1
        can_r_in = MOTOR_D / 2 + 0.3
        can_h = 80  # 长度（含伸入管内的部分）

        # 外壳朝向：轴线沿径向（从管壁指向管中心）
        # 创建时默认轴线是 z 方向
        # 需要旋转到径向
        # 旋转顺序：先绕 y 轴转到 xz 平面，再绕 z 轴转到对应角度

        can = Manifold.cylinder(can_h, can_r_out, can_r_out, SEGMENTS) - \
              Manifold.cylinder(can_h + 0.4, can_r_in, can_r_in, SEGMENTS)

        # 旋转使轴线沿径向
        # 默认轴向 z，先绕 y 转 90° 使轴向 x（指向 +x）
        can = can.rotate([0, math.pi / 2, 0])

        # 再绕 z 转到对应角度
        can = can.rotate([0, 0, angle])

        # 平移到凸台位置
        # 旋转后，can 的轴线沿 (cos(angle), sin(angle), 0) 方向
        # 中心位置应该在管壁外侧一点，让外壳穿过孔
        # 沿径向从管壁延伸到管内
        # can 中心位置：MOTOR_CENTER_R 处，但加上旋转偏移
        # 简化：can 在凸台中心位置，部分在管内，部分在管外
        # can 中心在 MOTOR_CENTER_R + BOSS_EXTRA/2 处（凸台中心），即 (MOTOR_CENTER_R + 10) = 156.5
        # can 长 80，旋转后一半在管内 (40)，一半在管外 (40)
        can_center_r = MOTOR_CENTER_R  # 凸台中心就是 can 中心
        cx_pos = can_center_r * math.cos(angle)
        cy_pos = can_center_r * math.sin(angle)
        can = can.translate([cx_pos, cy_pos, 0])

        parts[f'motor_can_{i}'] = can

    # ===== Side Plate（侧板）× 2 =====
    for z_sign in [0, 1]:
        plate_r = TUBE_OR + 5
        h = 6

        plate = Manifold.cylinder(h, plate_r, plate_r, SEGMENTS)
        plate = plate - Manifold.cylinder(h + 2, BALL_R + 3, BALL_R + 3, SEGMENTS)

        # 3 个电机孔
        for i in range(N_MOTORS):
            angle = math.radians(i * 120)
            cx = MOTOR_CENTER_R * math.cos(angle)
            cy = MOTOR_CENTER_R * math.sin(angle)
            hole = Manifold.cylinder(h + 2, MOTOR_D / 2 + 2, MOTOR_D / 2 + 2, SEGMENTS)
            hole = hole.translate([cx, cy, 0])
            plate = plate - hole

        # 螺栓孔
        for i in range(12):
            a = math.radians(i * 30)
            bx = (plate_r - 5) * math.cos(a)
            by = (plate_r - 5) * math.sin(a)
            hole = Manifold.cylinder(h + 2, 2.7, 2.7, 16)
            hole = hole.translate([bx, by, 0])
            plate = plate - hole

        z_pos = -FRAME_LEN / 2 - h / 2 if z_sign == 0 else FRAME_LEN / 2 + h / 2
        plate = plate.translate([0, 0, z_pos])
        parts[f'side_plate_{z_sign}'] = plate

    # ===== Ball（球）— 用于图示参考 =====
    ball = Manifold.sphere(BALL_R, SEGMENTS)
    parts['ball'] = ball

    # ===== Motor Stator（电机定子简化模型）= × 3
    # 用于图示电机位置
    stator_r = MOTOR_D / 2 - 3  # 定子比 can 小
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = (MOTOR_CENTER_R + BOSS_EXTRA / 2 + 10) * math.cos(angle)
        cy = (MOTOR_CENTER_R + BOSS_EXTRA / 2 + 10) * math.sin(angle)

        stator = Manifold.cylinder(MOTOR_L + 5, stator_r, stator_r, 32)
        stator = stator.rotate([0, math.pi / 2, 0])
        stator = stator.rotate([0, 0, angle])
        stator = stator.translate([cx, cy, 0])

        parts[f'motor_stator_{i}'] = stator

    return parts


# ============================================================
# 渲染装配图
# ============================================================
def manifold_to_mesh(body):
    """manifold → mesh 数据"""
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    return v, f


def render_assembly(parts, view='iso', filename='assembly.png'):
    """
    渲染装配图
    view: 'iso' (默认), 'front', 'top', 'side'
    """
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    for name, body in parts.items():
        v, f = manifold_to_mesh(body)

        # 三角面顶点
        triangles = v[f]

        # 选择颜色
        base_name = name.rsplit('_', 1)[0] if name.startswith('motor_can_') or \
                    name.startswith('side_plate_') or name.startswith('motor_stator_') else name
        color = COLORS.get(base_name, '#888888')
        alpha = 0.3 if name == 'ball' else 0.85

        mesh_collection = Poly3DCollection(
            triangles,
            alpha=alpha,
            facecolor=color,
            edgecolor='#333333',
            linewidth=0.1
        )
        ax.add_collection3d(mesh_collection)

    # 视图范围
    all_v = []
    for body in parts.values():
        v, _ = manifold_to_mesh(body)
        all_v.append(v)
    all_v = np.vstack(all_v)

    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2

    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    # 视图角度
    if view == 'iso':
        ax.view_init(elev=25, azim=45)
    elif view == 'front':
        ax.view_init(elev=0, azim=0)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)
    elif view == 'side':
        ax.view_init(elev=0, azim=90)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(f'Football Launcher Assembly — {view.upper()} View\n'
                 f'3× 6374 @ 120° | Ball 220mm | Tube Ø{2*TUBE_OR}mm',
                 fontsize=14, fontweight='bold')

    # 创建图例
    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['launch_tube'], label='Launch Tube'),
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


# ============================================================
# 导出爆炸图
# ============================================================
def render_exploded(parts, filename='exploded.png'):
    """
    爆炸图：各零件沿轴向分离显示
    """
    # 创建偏移后的零件
    exploded = {}
    exploded['ball'] = parts['ball']

    # 侧板往后推
    exploded['side_plate_0'] = parts['side_plate_0'].translate([0, 0, -30])
    exploded['side_plate_1'] = parts['side_plate_1'].translate([0, 0, 30])

    # 管居中
    exploded['launch_tube'] = parts['launch_tube']

    # 电机分散：每个角度不同距离
    for i, name in enumerate([n for n in parts if n.startswith('motor_can_')]):
        angle = math.radians(i * 120)
        offset = MOTOR_CENTER_R + 30
        dx = offset * math.cos(angle) - MOTOR_CENTER_R * math.cos(angle)
        dy = offset * math.sin(angle) - MOTOR_CENTER_R * math.sin(angle)
        exploded[name] = parts[name].translate([dx, dy, 0])

    for i, name in enumerate([n for n in parts if n.startswith('motor_stator_')]):
        angle = math.radians(i * 120)
        offset = MOTOR_CENTER_R + BOSS_EXTRA / 2 + 30
        orig_x = (MOTOR_CENTER_R + BOSS_EXTRA / 2 + 10) * math.cos(angle)
        orig_y = (MOTOR_CENTER_R + BOSS_EXTRA / 2 + 10) * math.sin(angle)
        new_x = offset * math.cos(angle)
        new_y = offset * math.sin(angle)
        exploded[name] = parts[name].translate([new_x - orig_x, new_y - orig_y, 0])

    # 自定义标题
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    for name, body in exploded.items():
        v, f = manifold_to_mesh(body)
        triangles = v[f]

        base_name = name.rsplit('_', 1)[0] if name.startswith('motor_can_') or \
                    name.startswith('side_plate_') or name.startswith('motor_stator_') else name
        color = COLORS.get(base_name, '#888888')
        alpha = 0.3 if name == 'ball' else 0.85

        mesh_collection = Poly3DCollection(
            triangles, alpha=alpha, facecolor=color,
            edgecolor='#333333', linewidth=0.1
        )
        ax.add_collection3d(mesh_collection)

    all_v = []
    for body in exploded.values():
        v, _ = manifold_to_mesh(body)
        all_v.append(v)
    all_v = np.vstack(all_v)

    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2 * 1.1
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2

    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    ax.view_init(elev=25, azim=45)
    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(f'Football Launcher Assembly — EXPLODED View\n'
                 f'3× 6374 @ 120° | Ball 220mm | Tube Ø{2*TUBE_OR}mm',
                 fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['launch_tube'], label='Launch Tube'),
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


# ============================================================
# 主程序
# ============================================================
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Building assembly...")
    parts = build_assembly()
    print(f"  Parts: {len(parts)}")
    print()

    print("Rendering views...")
    render_assembly(parts, view='iso', filename='assembly_iso.png')
    render_assembly(parts, view='front', filename='assembly_front.png')
    render_assembly(parts, view='top', filename='assembly_top.png')
    render_exploded(parts, filename='exploded.png')

    print(f"\n✓ 4 张组装图 → {OUTPUT_DIR}/")
    print("  - assembly_iso.png     (等轴测)")
    print("  - assembly_front.png   (正视图)")
    print("  - assembly_top.png     (俯视图)")
    print("  - exploded.png         (爆炸图)")


if __name__ == "__main__":
    main()