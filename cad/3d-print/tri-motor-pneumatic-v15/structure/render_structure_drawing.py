"""电机与发射圆管结构图 — 工程制图风格"""

import numpy as np
from manifold3d import Manifold
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, FancyArrow
import math
import os

# 参数（与 v15 一致）
BALL_D = 220
BALL_R = BALL_D / 2
MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31
TUBE_IR = BALL_R + 3
TUBE_OR = 140
TUBE_LEN = 400
CRADLE_R = TUBE_OR / 2 + 55
CRADLE_THICK = 10
HUB_OD = MOTOR_D + 8
HUB_LEN = MOTOR_L + 10
WHEEL_RIM_OR = 160
WHEEL_RIM_W = 10
WHEEL_N_SPOKES = 3
WHEEL_SPOKE_W = 16
FLYWHEEL_D = 50
FLYWHEEL_T = 8
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def C(h, r):
    return Manifold.cylinder(h, r, r, SEGMENTS)


def manifold_to_mesh(body):
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    return v, f


def render_single_part(part, filename, title, view='iso', color='#ff8c00'):
    """渲染单个零件"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    v, f = manifold_to_mesh(part)
    triangles = v[f]
    mc = Poly3DCollection(triangles, alpha=0.9, facecolor=color,
                          edgecolor='#222222', linewidth=0.1)
    ax.add_collection3d(mc)

    all_v = v
    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2 * 1.1
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2

    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    if view == 'iso':
        ax.view_init(elev=25, azim=45)
    elif view == 'front':
        ax.view_init(elev=0, azim=0)
    elif view == 'top':
        ax.view_init(elev=90, azim=0)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {filename}")


def build_motor_cradle():
    """构建电机 cradle（v15 版本）"""
    parts = Manifold()

    # Hub 沿 Z 轴
    hub_outer = C(HUB_LEN, HUB_OD / 2)
    hub_inner = C(HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    hub = hub_outer - hub_inner

    # 电机轴孔
    shaft = Manifold.cylinder(HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    hub = hub - shaft

    # 4 个 M4 电机螺栓孔
    for j in range(4):
        ja = math.radians(j * 90)
        bolt_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        bolt_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        bolt = Manifold.cylinder(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        bolt = bolt.translate([bolt_x, bolt_y, HUB_LEN / 2 - 3])
        hub = hub - bolt

    parts = parts + hub

    # 3 条辐条
    spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - WHEEL_RIM_W / 2
    spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4
    for j in range(WHEEL_N_SPOKES):
        sa = math.radians(j * 120)
        spoke = Manifold.cube((spoke_len, WHEEL_SPOKE_W, CRADLE_THICK), center=True)
        spoke = spoke.rotate([0, 0, sa])
        spoke = spoke.translate([spoke_offset * math.cos(sa),
                                 spoke_offset * math.sin(sa), 0])
        parts = parts + spoke

    # 外圈
    rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - \
          C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2)

    for j in range(4):
        ra = math.radians(j * 90 + 45)
        bx = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
        by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
        bolt = Manifold.cylinder(CRADLE_THICK + 2, 2.7, 16)
        bolt = bolt.translate([bx, by, 0])
        rim = rim - bolt

    parts = parts + rim

    # 飞轮盘（径向 +X）
    flywheel = C(FLYWHEEL_T, FLYWHEEL_D / 2)
    flywheel = flywheel.rotate([0, math.pi / 2, 0])
    flywheel = flywheel.translate([FLYWHEEL_D / 2 + 5, 0, 0])
    parts = parts + flywheel

    return parts


def build_tube_with_cradle_assembly():
    """构建管 + cradle 装配"""
    parts = {}

    # Tube
    parts['tube'] = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 3 个 cradle（径向）
    for i in range(3):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)

        cradle_hub = C(HUB_LEN, HUB_OD / 2) - C(HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
        cradle_hub = cradle_hub.translate([cx, cy, TUBE_LEN / 2])

        spokes = Manifold()
        spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - 5
        spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 16, 10), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     TUBE_LEN / 2])
            spokes = spokes + spoke

        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - \
              C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2)
        rim = rim.translate([cx, cy, TUBE_LEN / 2])

        # 飞轮
        fw_x = (cx / CRADLE_R) * (CRADLE_R + FLYWHEEL_D / 2 + 5)
        fw_y = (cy / CRADLE_R) * (CRADLE_R + FLYWHEEL_D / 2 + 5)
        flywheel = C(FLYWHEEL_T, FLYWHEEL_D / 2)
        flywheel = flywheel.rotate([0, math.pi / 2, 0])
        flywheel = flywheel.translate([fw_x, fw_y, TUBE_LEN / 2])

        # 电机（灰色）
        stator = C(MOTOR_L + 5, MOTOR_D / 2 - 4)
        stator = stator.rotate([0, math.pi / 2, 0])
        stator = stator.translate([cx + 5 * math.cos(angle_rad),
                                   cy + 5 * math.sin(angle_rad),
                                   TUBE_LEN / 2])

        parts[f'cradle_{i}'] = cradle_hub + spokes + rim
        parts[f'flywheel_{i}'] = flywheel
        parts[f'motor_{i}'] = stator

    parts['ball'] = Manifold.sphere(BALL_R, SEGMENTS)

    return parts


def render_motor_assembly_view(parts, view, filename, title):
    """电机 + tube 装配图（彩色编码）"""
    fig = plt.figure(figsize=(18, 12))
    ax = fig.add_subplot(111, projection='3d')

    COLORS = {
        'tube': '#ff8c00',          # 橙色 - 管
        'cradle': '#ff6600',        # 深橙 - cradle 主体
        'motor': '#444444',         # 深灰 - 电机
        'flywheel': '#888888',      # 浅灰 - 飞轮
        'ball': '#00cc00',          # 绿色 - 球
    }

    for name, body in parts.items():
        v, f = manifold_to_mesh(body)
        triangles = v[f]
        base_name = name.rsplit('_', 1)[0] if '_' in name else name
        color = COLORS.get(base_name, '#888888')
        alpha = 0.4 if name == 'ball' else 0.9
        mc = Poly3DCollection(triangles, alpha=alpha, facecolor=color,
                              edgecolor='#222222', linewidth=0.1)
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
    elif view == 'side':
        ax.view_init(elev=15, azim=0)
    elif view == 'cutaway':
        ax.view_init(elev=15, azim=0)

    ax.set_xlabel('X (mm)')
    ax.set_ylabel('Y (mm)')
    ax.set_zlabel('Z (mm)')
    ax.set_title(title, fontsize=14, fontweight='bold')

    legend_items = [
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['tube'], label='Launch Tube (Ø140, L400)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['cradle'], label='Motor Cradle (3x at 120°)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['motor'], label='6374 Motor (radial axis)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['flywheel'], label='Flywheel Disc (ball contact)'),
        plt.Rectangle((0, 0), 1, 1, fc=COLORS['ball'], alpha=0.5, label='Ball 220mm'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=10)
    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {filename}")


def render_technical_drawing():
    """工程制图：剖面 + 标注 + 尺寸"""
    fig = plt.figure(figsize=(20, 12))

    # ============ 上排：剖面图 ============
    # 1. 管径向剖面（看 cradle + 球 + 飞轮装配关系）
    ax1 = plt.subplot(2, 3, 1)
    ax1.set_title('A. 管径向剖面（X-Y 平面）\nCradle + 球 + 飞轮关系', fontsize=11, fontweight='bold')
    ax1.set_aspect('equal')

    # 管轮廓
    circle_tube = Circle((0, 0), TUBE_OR / 2, fill=False, edgecolor='#ff8c00', linewidth=2)
    circle_inner = Circle((0, 0), TUBE_IR / 2, fill=False, edgecolor='#ff8c00', linewidth=1, linestyle='--')
    ax1.add_patch(circle_tube)
    ax1.add_patch(circle_inner)

    # 球
    ball_circle = Circle((0, 0), BALL_R / 2, fill=True, facecolor='#00cc00', alpha=0.3, edgecolor='#00aa00', linewidth=2)
    ax1.add_patch(ball_circle)

    # 3 个 cradle
    for i in range(3):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)
        cradle_circle = Circle((cx, cy), WHEEL_RIM_OR / 2, fill=False, edgecolor='#ff6600', linewidth=1.5)
        hub_circle = Circle((cx, cy), HUB_OD / 2, fill=False, edgecolor='#ff6600', linewidth=2)
        ax1.add_patch(cradle_circle)
        ax1.add_patch(hub_circle)

        # 飞轮
        fw_x = (cx / CRADLE_R) * (CRADLE_R + FLYWHEEL_D / 2 + 5)
        fw_y = (cy / CRADLE_R) * (CRADLE_R + FLYWHEEL_D / 2 + 5)
        fw_circle = Circle((fw_x, fw_y), FLYWHEEL_D / 2, fill=True, facecolor='#888888', alpha=0.5, edgecolor='#444444')
        ax1.add_patch(fw_circle)

        # 标注
        ax1.annotate(f'Cradle {i+1}', (cx, cy), textcoords="offset points", xytext=(0, 10),
                     ha='center', fontsize=9, color='#ff4400')

    # 标注尺寸
    ax1.annotate('', xy=(WHEEL_RIM_OR / 2 + 10, 0), xytext=(TUBE_OR / 2 + 5, 0),
                arrowprops=dict(arrowstyle='<->', color='black'))
    ax1.text((WHEEL_RIM_OR / 2 + TUBE_OR / 2) / 2, 15, f'Ø{WHEEL_RIM_OR}', ha='center', fontsize=9)

    ax1.set_xlim(-110, 110)
    ax1.set_ylim(-110, 110)
    ax1.set_xlabel('X (mm)')
    ax1.set_ylabel('Y (mm)')
    ax1.grid(True, alpha=0.3)

    # 2. 管轴向剖面（看压力端 + 装球口 + 出球端）
    ax2 = plt.subplot(2, 3, 2)
    ax2.set_title('B. 管轴向剖面（X-Z 平面）\n压力端 → 装球口 → 出球端', fontsize=11, fontweight='bold')
    ax2.set_aspect('equal')

    # 管
    rect_outer = Rectangle((0, -TUBE_OR / 2), TUBE_LEN, TUBE_OR, fill=False, edgecolor='#ff8c00', linewidth=2)
    rect_inner = Rectangle((0, -TUBE_IR / 2), TUBE_LEN, TUBE_IR, fill=False, edgecolor='#ff8c00', linewidth=1, linestyle='--')
    ax2.add_patch(rect_outer)
    ax2.add_patch(rect_inner)

    # 压力端（左）
    rect_pressure = Rectangle((-30, -TUBE_OR / 2 - 8), 30, TUBE_OR + 16, fill=True, facecolor='#cc4400', alpha=0.6)
    ax2.add_patch(rect_pressure)

    # 出球端（右）
    rect_output = Rectangle((TUBE_LEN, -TUBE_OR / 2 - 20), 5, TUBE_OR + 40, fill=True, facecolor='#1f77b4', alpha=0.6)
    ax2.add_patch(rect_output)

    # 球（在管内）
    ball_rect = Rectangle((TUBE_LEN * 0.45, -BALL_R / 2), BALL_D, BALL_R, fill=True, facecolor='#00cc00', alpha=0.5, edgecolor='#00aa00', linewidth=1.5)
    ax2.add_patch(ball_rect)

    # 装球口位置
    load_port = Rectangle((TUBE_LEN * 0.2, TUBE_OR / 2), BALL_D, 8, fill=True, facecolor='#888888', alpha=0.7)
    ax2.add_patch(load_port)

    # 标注
    ax2.annotate('压力端\n(进气口)', xy=(-30, TUBE_OR / 2 + 30), ha='center', fontsize=9, color='#cc4400',
                 arrowprops=dict(arrowstyle='->', color='#cc4400'))
    ax2.annotate('装球口', xy=(TUBE_LEN * 0.2, TUBE_OR / 2 + 20), ha='center', fontsize=9, color='#444444',
                 arrowprops=dict(arrowstyle='->', color='#444444'))
    ax2.annotate('球 (220mm)', xy=(TUBE_LEN * 0.45 + BALL_D / 2, BALL_R / 2 + 30),
                 ha='center', fontsize=9, color='#00aa00',
                 arrowprops=dict(arrowstyle='->', color='#00aa00'))
    ax2.annotate('出球端', xy=(TUBE_LEN + 5, TUBE_OR / 2 + 30), ha='center', fontsize=9, color='#1f77b4',
                 arrowprops=dict(arrowstyle='->', color='#1f77b4'))

    # 尺寸
    ax2.annotate('', xy=(TUBE_LEN, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='<->', color='black'))
    ax2.text(TUBE_LEN / 2, 20, f'L = {TUBE_LEN} mm', ha='center', fontsize=10, weight='bold')

    ax2.set_xlim(-50, TUBE_LEN + 30)
    ax2.set_ylim(-110, 110)
    ax2.set_xlabel('Z (mm) — 沿发射方向')
    ax2.set_ylabel('X (mm)')
    ax2.grid(True, alpha=0.3)

    # 3. 单个 cradle 俯视图（XY 平面）
    ax3 = plt.subplot(2, 3, 3)
    ax3.set_title('C. Cradle 俯视图（XY 平面）\n辐条 + 外圈 + Hub', fontsize=11, fontweight='bold')
    ax3.set_aspect('equal')

    # 外圈
    rim_outer = Circle((0, 0), WHEEL_RIM_OR / 2, fill=False, edgecolor='#ff6600', linewidth=2)
    rim_inner = Circle((0, 0), (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2, fill=False, edgecolor='#ff6600', linewidth=1, linestyle='--')
    ax3.add_patch(rim_outer)
    ax3.add_patch(rim_inner)

    # Hub
    hub_circ = Circle((0, 0), HUB_OD / 2, fill=False, edgecolor='#ff6600', linewidth=2)
    ax3.add_patch(hub_circ)
    motor_circ = Circle((0, 0), MOTOR_D / 2, fill=True, facecolor='#444444', alpha=0.6, edgecolor='#222222')
    shaft_circ = Circle((0, 0), MOTOR_SHAFT_D / 2, fill=True, facecolor='#000000')
    ax3.add_patch(motor_circ)
    ax3.add_patch(shaft_circ)

    # 4 颗 M4 电机螺栓
    for j in range(4):
        ja = math.radians(j * 90)
        bx = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        by = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        bolt = Circle((bx, by), MOTOR_HOLE_D / 2, fill=False, edgecolor='#0066cc', linewidth=1.5)
        ax3.add_patch(bolt)

    # 3 条辐条
    spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - WHEEL_RIM_W / 2
    spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4
    for j in range(3):
        sa = math.radians(j * 120)
        # 辐条矩形
        sx, sy = spoke_offset * math.cos(sa), spoke_offset * math.sin(sa)
        ax3.add_patch(Rectangle((sx - spoke_len / 2, sy - WHEEL_SPOKE_W / 2),
                                 spoke_len, WHEEL_SPOKE_W,
                                 facecolor='#ff6600', alpha=0.5, edgecolor='#ff4400', linewidth=1.5,
                                 angle=math.degrees(sa)))

    # 4 颗 M5 外圈螺栓
    for j in range(4):
        ra = math.radians(j * 90 + 45)
        bx = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
        by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
        bolt = Circle((bx, by), 2.7, fill=False, edgecolor='#cc6600', linewidth=1.5)
        ax3.add_patch(bolt)

    # 标注
    ax3.annotate('3 辐条 (120°)', xy=(-spoke_offset * 0.7, spoke_offset * 0.7),
                 fontsize=9, color='#ff4400', ha='center',
                 arrowprops=dict(arrowstyle='->', color='#ff4400'))
    ax3.annotate('Hub (Ø71)', xy=(0, -HUB_OD / 2 - 8), fontsize=9, color='#ff4400', ha='center')
    ax3.annotate('4×M5 外圈', xy=(WHEEL_RIM_OR / 2 - 30, WHEEL_RIM_OR / 2 - 5),
                 fontsize=9, color='#cc6600')
    ax3.annotate('4×M4 电机', xy=(MOTOR_HOLE_PCD / 2 + 5, 0), fontsize=9, color='#0066cc')

    # 尺寸
    ax3.annotate('', xy=(WHEEL_RIM_OR / 2, 0), xytext=(0, 0),
                arrowprops=dict(arrowstyle='<->', color='black', lw=0.5))
    ax3.text(WHEEL_RIM_OR / 4, -5, f'Ø{WHEEL_RIM_OR}', ha='center', fontsize=9)

    ax3.set_xlim(-WHEEL_RIM_OR / 2 - 15, WHEEL_RIM_OR / 2 + 15)
    ax3.set_ylim(-WHEEL_RIM_OR / 2 - 15, WHEEL_RIM_OR / 2 + 15)
    ax3.set_xlabel('X (mm)')
    ax3.set_ylabel('Y (mm)')
    ax3.grid(True, alpha=0.3)

    # ============ 下排：3D 视图 ============

    # 4. 整体等轴测
    ax4 = plt.subplot(2, 3, 4, projection='3d')
    ax4.set_title('D. 整体等轴测\nTube + 3 Cradles (3D)', fontsize=11, fontweight='bold')

    # 渲染管
    tube_mesh = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)
    v, f = manifold_to_mesh(tube_mesh)
    mc = Poly3DCollection(v[f], alpha=0.7, facecolor='#ff8c00', edgecolor='#222222', linewidth=0.1)
    ax4.add_collection3d(mc)

    # 渲染 3 个 cradle
    for i in range(3):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)

        cradle_hub = C(HUB_LEN, HUB_OD / 2) - C(HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
        cradle_hub = cradle_hub.translate([cx, cy, TUBE_LEN / 2])

        spokes = Manifold()
        spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - 5
        spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 16, 10), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     TUBE_LEN / 2])
            spokes = spokes + spoke

        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 20) / 2)
        rim = rim.translate([cx, cy, TUBE_LEN / 2])

        cradle_body = cradle_hub + spokes + rim
        v, f = manifold_to_mesh(cradle_body)
        mc = Poly3DCollection(v[f], alpha=0.9, facecolor='#ff6600', edgecolor='#222222', linewidth=0.1)
        ax4.add_collection3d(mc)

    # 球
    v, f = manifold_to_mesh(Manifold.sphere(BALL_R, SEGMENTS))
    mc = Poly3DCollection(v[f], alpha=0.5, facecolor='#00cc00', edgecolor='#00aa00', linewidth=0.5)
    ax4.add_collection3d(mc)

    all_v = []
    v, f = manifold_to_mesh(tube_mesh)
    all_v.append(v)
    for i in range(3):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)
        cradle_hub = C(HUB_LEN, HUB_OD / 2) - C(HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
        cradle_hub = cradle_hub.translate([cx, cy, TUBE_LEN / 2])
        spokes = Manifold()
        spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - 5
        spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, 16, 10), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     TUBE_LEN / 2])
            spokes = spokes + spoke
        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 20) / 2)
        rim = rim.translate([cx, cy, TUBE_LEN / 2])
        cradle_body = cradle_hub + spokes + rim
        v, _ = manifold_to_mesh(cradle_body)
        all_v.append(v)
    v, _ = manifold_to_mesh(Manifold.sphere(BALL_R, SEGMENTS))
    all_v.append(v)
    all_v = np.vstack(all_v)

    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2 * 1.1
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2
    ax4.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax4.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax4.set_zlim(mid[2] - max_range, mid[2] + max_range)
    ax4.view_init(elev=20, azim=45)

    # 5. Cradle 立体图
    ax5 = plt.subplot(2, 3, 5, projection='3d')
    ax5.set_title('E. Cradle 立体图\n(3D)', fontsize=11, fontweight='bold')

    cradle = build_motor_cradle()
    v, f = manifold_to_mesh(cradle)
    mc = Poly3DCollection(v[f], alpha=0.9, facecolor='#ff6600', edgecolor='#222222', linewidth=0.2)
    ax5.add_collection3d(mc)

    # 电机（灰色）
    motor = C(MOTOR_L + 5, MOTOR_D / 2 - 4)
    v, f = manifold_to_mesh(motor)
    mc = Poly3DCollection(v[f], alpha=0.85, facecolor='#444444', edgecolor='#222222', linewidth=0.2)
    ax5.add_collection3d(mc)

    all_v = []
    v, _ = manifold_to_mesh(cradle)
    all_v.append(v)
    v, _ = manifold_to_mesh(motor)
    all_v.append(v)
    all_v = np.vstack(all_v)
    max_range = np.max(all_v.max(axis=0) - all_v.min(axis=0)) / 2 * 1.1
    mid = (all_v.max(axis=0) + all_v.min(axis=0)) / 2
    ax5.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax5.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax5.set_zlim(mid[2] - max_range, mid[2] + max_range)
    ax5.view_init(elev=20, azim=45)

    # 6. 关键尺寸表
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    ax6.set_title('F. 关键尺寸与装配关系', fontsize=11, fontweight='bold')

    table_data = [
        ['参数', '值', '单位'],
        ['球直径', '220', 'mm'],
        ['球质量', '430', 'g'],
        ['管内径', f'{TUBE_IR}', 'mm'],
        ['管外径', f'{TUBE_OR}', 'mm'],
        ['管长', f'{TUBE_LEN}', 'mm'],
        ['Cradle 中心距', f'{CRADLE_R:.0f}', 'mm'],
        ['Cradle 外径', f'{WHEEL_RIM_OR}', 'mm'],
        ['Cradle 厚度', f'{CRADLE_THICK}', 'mm'],
        ['Hub 外径', f'{HUB_OD}', 'mm'],
        ['Hub 长度', f'{HUB_LEN}', 'mm'],
        ['飞轮盘直径', f'{FLYWHEEL_D}', 'mm'],
        ['电机螺栓', '4×M4', '—'],
        ['外圈螺栓', '4×M5', '—'],
        ['电机轴向', '径向 (X)', '—'],
        ['Cradle 数量', '3', '@120°'],
    ]

    table = ax6.table(cellText=table_data, cellLoc='left', loc='center',
                       colWidths=[0.4, 0.3, 0.15])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.5)

    # 高亮标题行
    for i in range(3):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')

    # 高亮关键参数
    for i in [1, 5, 7, 12, 13, 15]:
        for j in range(3):
            table[(i, j)].set_facecolor('#FFE699')

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "structure_drawing_v15.png")
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ structure_drawing_v15.png — {os.path.getsize(out)//1024}KB")


def main():
    print("=" * 50)
    print("电机 + 发射圆管结构图")
    print("=" * 50)

    # 1. Cradle 单独视图
    print("\n[1/4] Cradle 单独视图...")
    cradle = build_motor_cradle()
    render_single_part(cradle, "cradle_only_v15.png",
                       "Motor Cradle (v15) — 控旋模块\n3 spokes + hub + flywheel",
                       view='iso', color='#ff6600')
    render_single_part(cradle, "cradle_top_v15.png",
                       "Motor Cradle — Top View",
                       view='top', color='#ff6600')

    # 2. Tube 单独视图
    print("\n[2/4] Tube 单独视图...")
    tube = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)
    render_single_part(tube, "tube_only_v15.png",
                       "Launch Tube (v15) — 主发射管\nØ140 × L400mm",
                       view='iso', color='#ff8c00')

    # 3. 装配视图
    print("\n[3/4] 装配视图...")
    assembly = build_tube_with_cradle_assembly()
    render_motor_assembly_view(assembly, 'iso', "assembly_motor_v15_iso.png",
                                "Motor + Tube 装配（v15）\n3×6374 radial cradles + ball")
    render_motor_assembly_view(assembly, 'side', "assembly_motor_v15_side.png",
                                "Motor + Tube 装配 — Side View")

    # 4. 工程制图（多视图）
    print("\n[4/4] 工程制图...")
    render_technical_drawing()

    print("\n✓ 所有图 → " + OUTPUT_DIR + "/")


if __name__ == "__main__":
    main()