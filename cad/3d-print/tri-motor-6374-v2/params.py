"""
Football Launcher — 3-Motor 120° Outer-Rotor Design
电机外壳穿过管壁接触球面

设计概念：
- 6374 电机外转子（外壳/can）穿过管壁大圆孔进入内部
- 管壁上是加厚凸台，提供结构支撑
- 凸台间用桥接筋保持刚性
- 电机外壳本身就是发射面（无需独立滚轮）
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 参数
# ============================================================

BALL_D = 220                # mm
BALL_R = BALL_D / 2

# 6374 电机 — 外转子发射
MOTOR_D = 63                # mm 外径
MOTOR_L = 74                # mm 长度
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4            # M4
MOTOR_HOLE_PCD = 31         # 安装孔中心距

# 电机外转子（外壳/spinning can）接触球面
# 外壳半径需要超过球面半径以保证接触
# 球面外缘 = BALL_R + 接触深度
# 外壳中心距管中心距离 = BALL_R + (外壳突出到球内)
# 让外壳能伸到球内接触球面
MOTOR_INSERT_DEPTH = 5      # mm，外壳伸入球内接触深度
MOTOR_CENTER_R = BALL_R + 10  # mm，电机中心到管中心距离 = 120mm
# 即电机外壳外缘在 120 + 31.5 = 151.5mm 处
# 球面在 110mm 处，所以外壳深入球内 (151.5 - 110) = 41.5mm
# 调整：让外壳伸入到刚接触球面附近

# 调整方案：
# 让电机外壳外缘恰好接触球面：
# MOTOR_CENTER_R = BALL_R + MOTOR_D/2 = 110 + 31.5 = 141.5mm
# 这样外壳外缘在 141.5 + 31.5 = 173mm，但球面在 110mm，外壳伸入 (173-110)=63mm 太深
# 正确做法：让外壳中心距离球心 = BALL_R
# 即外壳外缘正好到达球面，此时外壳前半部分在球内
# MOTOR_CENTER_R = BALL_R - sqrt((MOTOR_D/2)^2 - 接触深度^2)
# 接触深度 5mm: MOTOR_CENTER_R = 110 - sqrt(31.5^2 - 5^2) = 110 - 31.1 = 78.9mm

# 实际方案：
# 让电机外壳外缘到球心距离 = BALL_R - 0.5mm（轻微压入）
# MOTOR_CENTER_R + MOTOR_D/2 = BALL_R - 0.5
# MOTOR_CENTER_R = BALL_R - 0.5 - MOTOR_D/2 = 110 - 0.5 - 31.5 = 78mm
# 但这样电机完全在管内，不合理

# 更合理：电机外壳是发射面（不是球面接触，是外壳本身穿过管壁）
# 管壁有孔，电机外壳从外面穿过孔进入管内，外壳外缘接触球面

# 几何重新设计：
# - 管中心是球通道
# - 球在管中心，BALL_R = 110mm
# - 管内径需要 > 球径：TUBE_IR = 113mm（球通过间隙）
# - 电机外壳外缘到球心 = BALL_R（接触球面）
# - 电机外壳外缘 = MOTOR_CENTER_R + MOTOR_D/2
# - 设接触点高度 = 球心位置（球直径方向）：
# - MOTOR_CENTER_R + 31.5 = 110
# - MOTOR_CENTER_R = 78.5mm

# 但这样电机壳完全在管内，需要管内径至少 78.5 + 31.5 = 110mm，球都放不下
# 矛盾了

# 重新理解：参考图显示的方案
# 图中是管+电机座在管外侧，电机轴穿过管壁接触球
# 不是外壳接触球，而是轴上的滚轮接触球

# 但 owner 说"电机轴/外壳穿过管壁进入内部接触球面"
# 这意味着电机深入管内，外壳/轴作为发射面

# 第三种方案：管壁薄，电机几乎嵌入管内
# TUBE_IR = 113mm（球通过）
# TUBE_OR = 130mm（管壁薄）
# MOTOR_CENTER_R = TUBE_OR - WALL = 126mm（电机中心在管壁外侧一点）
# 电机外壳外缘 = 126 + 31.5 = 157.5mm（深入管内）
# 接触球面 = BALL_R = 110mm
# 接触深度 = 157.5 - 110 = 47.5mm（外壳在球内的部分）

# 这种方案电机大部分嵌入管壁中

# 更合理的方案：电机外壳卡入管壁的凹陷处，外壳外缘接触球
# TUBE_OR 设大一些（如 150mm），外壳伸出管外
# 球面与外壳外缘相切

# 设定：
TUBE_IR = BALL_R + 3        # 113mm 球通过间隙
TUBE_OR = 140               # mm 管外壁
WALL = (TUBE_OR - TUBE_IR)  # 27mm 管壁厚
BOSS_EXTRA = 20             # mm 凸台向外延伸
BOSS_OR = TUBE_OR + BOSS_EXTRA  # 160mm
MOTOR_HOLE_DIA = MOTOR_D + 2  # mm 管壁穿孔直径（让电机外壳穿过）

# 电机中心位置（在管壁中，凸台外侧）
# 电机外壳外缘要接触球面 = BALL_R
# 电机中心 = BALL_R + MOTOR_D/2（外壳外缘到球面）
# 这要求 MOTOR_CENTER_R = 110 + 31.5 = 141.5mm
# 即电机中心在管中心外 141.5mm 处
# 凸台 OR = 160mm，电机中心可在管壁外侧（凸台内）
MOTOR_CENTER_R = BALL_R + MOTOR_D / 2 + 5  # 146.5mm 电机中心到管中心距离
# 外壳外缘 = 146.5 + 31.5 = 178mm，远超球面
# 但管内空间只有 110-(-110) = 220mm，外壳伸入部分需要单独考虑

# 重要观察：电机外壳不需要全部接触球面，只需要外壳在球面方向的外缘部分
# 接触球面的点在外壳表面最靠近球心的位置
# 外壳中心到球心 = 141.5mm
# 外壳半径 = 31.5mm
# 外壳最近点到球心 = 141.5 - 31.5 = 110mm = BALL_R ✓ 接触

# 所以电机外壳外缘接触球面
# 电机中心在 141.5mm 处，需要管壁+凸台整体能支撑

# 框架参数
FRAME_LEN = 100             # mm 框架长度
BOSS_H = FRAME_LEN          # 凸台高度与框架等长
RIB_W = 8                   # mm 桥接筋宽度
RIB_H = FRAME_LEN

BOLT_D = 5                  # mm M5 螺栓
N_MOTORS = 3

SEGMENTS = 64
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


# ============================================================
# 工具
# ============================================================
def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEGMENTS)

def save(body, name):
    path = os.path.join(OUTPUT_DIR, name)
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    with open(path, 'wb') as fh:
        fh.write(b'\0' * 80)
        fh.write(struct.pack('<I', len(f)))
        for tri in f:
            p0, p1, p2 = v[tri[0]], v[tri[1]], v[tri[2]]
            n = np.cross(p1 - p0, p2 - p0)
            nl = np.linalg.norm(n)
            n = n / nl if nl > 0 else [0, 0, 1]
            fh.write(struct.pack('<3f', *n))
            fh.write(struct.pack('<3f', *p0))
            fh.write(struct.pack('<3f', *p1))
            fh.write(struct.pack('<3f', *p2))
            fh.write(struct.pack('<H', 0))
    print(f"  ✓ {name} — {len(f)} faces, {os.path.getsize(path)//1024}KB")


# ============================================================
# Part 1: Launch Tube（发射管 — 整圆 + 大圆孔 + 加厚凸台 + 桥接筋）
# ============================================================
def make_launch_tube():
    """
    发射管主框架：
    - 整圆管（不分对开），内径 113mm
    - 管壁 27mm，外径 140mm
    - 3 个大圆孔（直径 65mm，让电机外壳穿过）
    - 每个孔周围加厚凸台，向外延伸 20mm
    - 凸台间用桥接筋连接（保持刚性）
    - 桥接筋跨越凸台之间的间隙
    """
    # 主管
    tube = Manifold.cylinder(FRAME_LEN, TUBE_OR, TUBE_OR, SEGMENTS) - \
           Manifold.cylinder(FRAME_LEN + 0.4, TUBE_IR, TUBE_IR, SEGMENTS)

    # 3 个电机位大圆孔（管壁上）
    # 孔中心在管壁上：距离管中心 = TUBE_OR - WALL/2
    hole_center_r = (TUBE_OR + TUBE_IR) / 2  # 主管中心位置
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = hole_center_r * math.cos(angle)
        cy = hole_center_r * math.sin(angle)

        # 大圆孔（让电机外壳穿过）
        hole = Manifold.cylinder(FRAME_LEN + 2, MOTOR_HOLE_DIA / 2, MOTOR_HOLE_DIA / 2, SEGMENTS)
        hole = hole.translate([cx, cy, 0])
        tube = tube - hole

    # 3 个加厚凸台（孔周围向外延伸）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)

        # 凸台（圆柱形，向管外延伸）
        boss = Manifold.cylinder(BOSS_H, BOSS_EXTRA / 2, BOSS_EXTRA / 2, SEGMENTS)
        boss = boss.translate([cx, cy, 0])
        tube = tube + boss

        # 凸台中心孔（让电机外壳穿过，贯通）
        boss_hole = Manifold.cylinder(BOSS_H + 2, MOTOR_D / 2 + 0.5, MOTOR_D / 2 + 0.5, SEGMENTS)
        boss_hole = boss_hole.translate([cx, cy, 0])
        tube = tube - boss_hole

        # M4 电机安装孔（4 个，凸台端面）
        for j in range(4):
            ja = math.radians(j * 90)
            jx = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            jy = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            bolt = Manifold.cylinder(BOSS_H + 2, MOTOR_HOLE_D / 2 + 0.1, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([cx + jx, cy + jy, 0])
            tube = tube - bolt

    # 桥接筋（3 条，连接相邻两个凸台外缘）
    # 筋从管外壁到凸台外侧，跨越 27mm 的间隙
    for i in range(N_MOTORS):
        angle1 = math.radians(i * 120)
        angle2 = math.radians(((i + 1) % N_MOTORS) * 120)
        a_mid = (angle1 + angle2) / 2
        a_diff = abs(angle2 - angle1)

        # 筋位置（两凸台之间）
        rib_start_r = TUBE_OR
        rib_end_r = BOSS_OR
        rib_arc_radius = (rib_start_r + rib_end_r) / 2

        # 筋截面（梯形，跨越管壁到凸台）
        rib = Manifold.cylinder(RIB_H, RIB_W / 2, RIB_W / 2, 16)
        # 沿径向延伸
        rib = rib.translate([rib_arc_radius, 0, 0])

        # 旋转到中间角度
        rib = rib.rotate([0, 0, math.radians(math.degrees(a_mid))])
        tube = tube + rib

    # 加固环（管外壁 3 条凸环）
    for z in [15, FRAME_LEN - 15, FRAME_LEN / 2]:
        ring = Manifold.cylinder(5, TUBE_OR + 3, TUBE_OR + 3, SEGMENTS) - \
               Manifold.cylinder(6, TUBE_OR - 1, TUBE_OR - 1, SEGMENTS)
        ring = ring.translate([0, 0, z - 2.5])
        tube = tube + ring

    save(tube, "launch_tube.stl")


# ============================================================
# Part 2: Motor Can Cap（电机外壳端盖 — 接触球面的发射面）
# ============================================================
def make_motor_can():
    """
    电机外壳（外转子 can）：
    - 套在电机外壳外侧
    - 外表面带 V 槽或橡胶圈接触球
    - 法兰端固定到凸台
    """
    # 主体（薄壁管，套在电机外面）
    can_r_out = MOTOR_D / 2 + 1     # 32.5mm 外径
    can_r_in = MOTOR_D / 2 + 0.3    # 32.3mm 内径（紧配合）
    can_h = MOTOR_L                  # 74mm 长

    can = Manifold.cylinder(can_h, can_r_out, can_r_out, SEGMENTS) - \
          Manifold.cylinder(can_h + 0.4, can_r_in, can_r_in, SEGMENTS)

    # 法兰（固定到凸台）
    flange = Manifold.cube((MOTOR_D + 20, MOTOR_D + 20, 4), center=True)
    flange = flange.translate([0, 0, can_h / 2 + 2])
    can = can + flange

    # 法兰 M4 孔
    for i in range(4):
        a = math.radians(i * 90)
        hx = (MOTOR_HOLE_PCD / 2) * math.cos(a)
        hy = (MOTOR_HOLE_PCD / 2) * math.sin(a)
        hole = Manifold.cylinder(6, MOTOR_HOLE_D / 2 + 0.1, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, can_h / 2 + 2])
        can = can - hole

    # V 槽（外表面，3 圈增加抓球力）
    for z_off in [-can_h / 2 + 8, 0, can_h / 2 - 8]:
        groove_outer = Manifold.cylinder(3, can_r_out + 0.5, can_r_out + 0.5, SEGMENTS)
        groove_inner = Manifold.cylinder(3.4, can_r_out - 2, can_r_out - 2, SEGMENTS)
        groove = groove_outer - groove_inner
        groove = groove.translate([0, 0, z_off])
        can = can - groove

    # 顶部减重孔（封口）
    cap = Manifold.cylinder(2, can_r_out - 5, can_r_out - 5, SEGMENTS) - \
          Manifold.cylinder(3, can_r_in, can_r_in, SEGMENTS)
    cap = cap.translate([0, 0, -can_h / 2 + 1])
    can = can + cap

    save(can, "motor_can.stl")


# ============================================================
# Part 3: Side Plate（侧板 — 框架端面结构）
# ============================================================
def make_side_plate():
    """
    侧板：发射管两端的结构加强板
    - 圆环，与管外径匹配
    - 3 个电机位大孔
    - 螺栓孔
    """
    plate_r = TUBE_OR + 5
    h = 6

    plate = Manifold.cylinder(h, plate_r, plate_r, SEGMENTS)

    # 中心球通过孔
    plate = plate - Manifold.cylinder(h + 2, BALL_R + 3, BALL_R + 3, SEGMENTS)

    # 3 个电机轴通过孔（如果需要穿过端面）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)
        hole = Manifold.cylinder(h + 2, MOTOR_D / 2 + 2, MOTOR_D / 2 + 2, SEGMENTS)
        hole = hole.translate([cx, cy, 0])
        plate = plate - hole

    # 螺栓孔（12 个均布）
    for i in range(12):
        a = math.radians(i * 30)
        bx = (plate_r - 5) * math.cos(a)
        by = (plate_r - 5) * math.sin(a)
        hole = Manifold.cylinder(h + 2, BOLT_D / 2 + 0.15, BOLT_D / 2 + 0.15, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 减重孔
    for i in range(3):
        angle = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 10) * math.cos(angle)
        py = (plate_r / 2 + 10) * math.sin(angle)
        light = Manifold.cylinder(h + 2, 12, 12, 32)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate.stl")


# ============================================================
# Part 4: Motor Stator Mount（电机定子固定座 — 卡在管内）
# ============================================================
def make_stator_mount():
    """
    电机定子固定座：
    - 从管内卡住电机定子
    - 固定电机不旋转的部分
    - 让外转子（can）自由旋转
    """
    # 主体（圆形薄板，中间孔容纳定子）
    stator_d = 35    # 6374 定子典型尺寸
    stator_d_inner = 30
    h = 8

    body = Manifold.cylinder(h, stator_d, stator_d, SEGMENTS) - \
           Manifold.cylinder(h + 0.4, stator_d_inner, stator_d_inner, SEGMENTS)

    # 法兰（卡在管壁上）
    flange = Manifold.cube((stator_d + 20, stator_d + 20, 3), center=True)
    flange = flange.translate([0, 0, -h / 2 - 1.5])
    body = body + flange

    # 法兰 M4 孔（4 个）
    for i in range(4):
        a = math.radians(i * 90)
        hx = 12 * math.cos(a)
        hy = 12 * math.sin(a)
        hole = Manifold.cylinder(4, MOTOR_HOLE_D / 2 + 0.1, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, -h / 2 - 1.5])
        body = body - hole

    save(body, "stator_mount.stl")


# ============================================================
# Part 5: Bridge Rib（独立桥接筋 — 可选备用）
# ============================================================
def make_bridge_rib():
    """
    独立桥接筋：
    - 跨越两个凸台之间的间隙
    - 一体式长筋，从管壁到凸台
    """
    rib_l = TUBE_OR + BOSS_EXTRA + 20  # 总长度
    rib_w = RIB_W
    rib_h = RIB_H

    body = Manifold.cube((rib_l, rib_w, rib_h), center=True)

    # 两端各 2 个 M5 螺栓孔
    for x_off in [-rib_l / 2 + 10, rib_l / 2 - 10]:
        for y_off in [-rib_w / 4, rib_w / 4]:
            hole = Manifold.cylinder(rib_h + 2, BOLT_D / 2 + 0.15, BOLT_D / 2 + 0.15, 16)
            hole = hole.translate([x_off, y_off, 0])
            body = body - hole

    save(body, "bridge_rib.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("3-Motor 120° Outer-Rotor (电机外壳穿过管壁)")
    print("=" * 50)
    print(f"球: {BALL_D}mm | 管内径: {TUBE_IR*2}mm")
    print(f"管壁厚: {WALL}mm | 电机中心: {MOTOR_CENTER_R}mm")
    print()

    make_launch_tube()
    make_motor_can()
    make_side_plate()
    make_stator_mount()
    make_bridge_rib()

    print(f"\n✓ 5 个零件 → {OUTPUT_DIR}/")
    print(f"\n打印数量:")
    print(f"  launch_tube:   1")
    print(f"  motor_can:     3 (电机外壳发射面)")
    print(f"  side_plate:    2 (两端)")
    print(f"  stator_mount:  3 (电机定子固定)")
    print(f"  bridge_rib:    3 (可选，额外加固)")


if __name__ == "__main__":
    export_all()