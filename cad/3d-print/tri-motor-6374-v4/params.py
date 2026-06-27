"""
Football Launcher — v4 一体化蜘蛛结构
基于参考图：中心管段 + 3 条弯曲辐臂 + 电机座，一件成型

设计特点：
- 单件 3D 打印件，集成管+臂+电机座
- 弯曲有机辐臂（参考图风格）
- 电机座开口容纳 6374
- 3 个电机位大圆孔（让 can 穿过）
- 减重凹槽
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 参数
# ============================================================
BALL_D = 220
BALL_R = BALL_D / 2

# 6374 电机
MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 一体化主体
TUBE_IR = BALL_R + 3           # 113mm 球通过内径
TUBE_OR = 145                  # 主体外径
TUBE_LEN = 100                 # 主体长度

# 电机位置
MOTOR_HOLE_DIA = MOTOR_D + 2   # 65mm 大圆孔
MOTOR_CENTER_R = (TUBE_OR + TUBE_IR) / 2  # 电机中心位于管壁
ARM_OUTER_R = MOTOR_CENTER_R + 30  # 臂末端外缘半径
ARM_LEN = ARM_OUTER_R - MOTOR_CENTER_R  # 臂长 30mm

# 电机座（臂末端）
CRADLE_OD = MOTOR_D + 16       # 79mm 座外径
CRADLE_LEN = MOTOR_L + 15      # 89mm 座深度

# 辐臂
ARM_W = 18                     # 臂宽
ARM_T = 8                      # 臂厚
ARM_NECK = 12                  # 臂与主体连接处的颈宽
ARM_CURVE = 1.2                # 弯曲度系数

# 桥筋（臂之间连接）
RIB_W = 6
RIB_T = 5

BOLT_D = 5
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


def make_curve_arm(angle_deg, start_r, end_r, width, thickness, length, n_steps=20):
    """
    生成弯曲辐臂：从主体外壁到电机座
    沿径向延伸，宽度逐渐变化
    """
    angle_rad = math.radians(angle_deg)

    # 起点和终点（在主体坐标系中）
    sx = start_r * math.cos(angle_rad)
    sy = start_r * math.sin(angle_rad)
    ex = end_r * math.cos(angle_rad)
    ey = end_r * math.sin(angle_rad)

    # 中间点（曲线偏移）
    mid_r = (start_r + end_r) / 2
    # 切向偏移量
    tangent_off = ARM_CURVE * length * 0.3
    mid_a = angle_rad + math.atan2(tangent_off, length)
    mx = mid_r * math.cos(mid_a)
    my = mid_r * math.sin(mid_a)

    # 用一系列小方块沿曲线铺设
    arms = Manifold()
    for i in range(n_steps + 1):
        t = i / n_steps
        # 二次贝塞尔曲线
        one_minus_t = 1 - t
        x = one_minus_t * one_minus_t * sx + 2 * one_minus_t * t * mx + t * t * ex
        y = one_minus_t * one_minus_t * sy + 2 * one_minus_t * t * my + t * t * ey

        # 切线方向（相邻点的方向）
        if i < n_steps:
            t2 = (i + 1) / n_steps
            omt2 = 1 - t2
            x2 = omt2 * omt2 * sx + 2 * omt2 * t2 * mx + t2 * t2 * ex
            y2 = omt2 * omt2 * sy + 2 * omt2 * t2 * my + t2 * t2 * ey
            dx, dy = x2 - x, y2 - y
        else:
            if i > 0:
                t0 = (i - 1) / n_steps
                omt0 = 1 - t0
                x0 = omt0 * omt0 * sx + 2 * omt0 * t0 * mx + t0 * t0 * ex
                y0 = omt0 * omt0 * sy + 2 * omt0 * t0 * my + t0 * t0 * ey
                dx, dy = x - x0, y - y0
            else:
                dx, dy = ex - sx, ey - sy

        seg_len = math.sqrt(dx * dx + dy * dy)
        seg_angle = math.atan2(dy, dx)

        # 当前宽度（中间窄，两端宽）
        current_w = width * (0.7 + 0.3 * math.sin(t * math.pi))

        # 创建小段方块
        seg = Manifold.cube((seg_len * 1.1, current_w, thickness), center=True)
        # 旋转使长度方向沿 (dx, dy)
        seg = seg.rotate([0, 0, seg_angle])
        # 平移到 (x, y)
        seg = seg.translate([x, y, 0])
        arms = arms + seg

    return arms


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
# Part 1: One-Piece Spider Body（一体化蜘蛛主体）
# ============================================================
def make_spider_body():
    """
    一体化"蜘蛛"主体：
    - 中心管段（球通道）
    - 3 条弯曲辐臂（120° 均布）
    - 3 个电机座（臂末端，容纳 6374）
    - 3 个大圆孔（让电机外壳穿过）
    - 减重凹槽
    """
    # ===== 中心管段 =====
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # ===== 3 条弯曲辐臂 + 电机座 =====
    for i in range(N_MOTORS):
        angle_deg = i * 120

        # 电机座（臂末端的圆柱，容纳电机）
        # 中心位置：MOTOR_CENTER_R 半径处
        crad_r = MOTOR_CENTER_R
        crad_cy = CRADLE_OD / 2
        cradle_outer = C(TUBE_LEN, crad_cy, crad_cy)
        cradle_inner = C(TUBE_LEN + 0.4, MOTOR_D / 2 + 0.5, MOTOR_D / 2 + 0.5)

        # 旋转电机座使其朝向径向
        # 但电机座的轴向应该平行于管长（z 轴），不需要径向旋转
        # 电机座就在径向位置
        angle_rad = math.radians(angle_deg)
        cx = crad_r * math.cos(angle_rad)
        cy = crad_r * math.sin(angle_rad)
        cradle_outer = cradle_outer.translate([cx, cy, 0])
        cradle_inner = cradle_inner.translate([cx, cy, 0])
        cradle = cradle_outer - cradle_inner

        # 电机轴孔
        shaft_hole = C(TUBE_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
        shaft_hole = shaft_hole.translate([cx, cy, 0])
        cradle = cradle - shaft_hole

        # 电机固定端 M4 螺栓孔（4 个）
        for j in range(4):
            ja = math.radians(j * 90)
            jx = cx + (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            jy = cy + (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            bolt = C(TUBE_LEN + 2, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([jx, jy, 0])
            cradle = cradle - bolt

        body = body + cradle

        # 弯曲辐臂（从主体外壁到电机座）
        # 起点：TUBE_OR 半径处（主体外壁）
        # 终点：crad_r - crad_cy 处（电机座近端）
        start_r = TUBE_OR
        end_r = crad_r - crad_cy
        arm = make_curve_arm(angle_deg, start_r, end_r, ARM_W, ARM_T, length=ARM_LEN)
        body = body + arm

        # 电机座端到主体的填充（径向连接板，确保结构连续）
        fillet = Manifold.cube((CRADLE_OD, 12, TUBE_LEN), center=True)
        # 旋转到径向
        fillet = fillet.rotate([0, 0, angle_deg])
        fillet = fillet.translate([crad_r, 0, 0])
        body = body + fillet

    # ===== 桥接筋（臂之间）=====
    # 沿管外壁，在两个臂之间添加肋
    for i in range(N_MOTORS):
        a1 = math.radians(i * 120)
        a2 = math.radians(((i + 1) % N_MOTORS) * 120)
        a_mid = (a1 + a2) / 2
        # 在主体外壁添加局部凸起
        rib = Manifold.cylinder(TUBE_LEN, TUBE_OR + 2, TUBE_OR + 2, 16) - \
              Manifold.cylinder(TUBE_LEN + 0.4, TUBE_OR + 1, TUBE_OR + 1, 16)
        # 用切割角度形成局部筋
        angle_span = 0.4  # 弧度
        for sign in [-1, 1]:
            # 在 a_mid 附近创建窄条
            # 简化：用矩形切割后旋转
            cut = Manifold.cube((TUBE_OR * 3, TUBE_OR * 2, TUBE_LEN), center=True)
            cut = cut.rotate([0, 0, math.degrees(a_mid) + math.degrees(angle_span * sign) + 90])
            cut = cut.translate([0, TUBE_OR * 1.5, 0])
            rib = rib - cut

        body = body + rib

    # ===== 减重凹槽（在臂上）=====
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        mid_r = (TUBE_OR + MOTOR_CENTER_R) / 2
        # 凹槽尺寸
        recess = Manifold.cube((ARM_W - 6, 12, TUBE_LEN - 20), center=True)
        # 旋转到径向
        recess = recess.rotate([0, 0, angle_deg])
        recess = recess.translate([mid_r, 0, 0])
        body = body - recess

    # ===== 两端加固环 =====
    for z in [6, TUBE_LEN - 6]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "spider_body_v4.stl")


# ============================================================
# Part 2: Motor Can（电机外壳套）
# ============================================================
def make_motor_can():
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)

    # 法兰
    flange = Manifold.cube((MOTOR_D + 20, MOTOR_D + 20, 4), center=True)
    flange = flange.translate([0, 0, can_h / 2 + 2])
    can = can + flange

    # 法兰螺栓孔
    for i in range(4):
        a = math.radians(i * 90)
        hx = (MOTOR_HOLE_PCD / 2) * math.cos(a)
        hy = (MOTOR_HOLE_PCD / 2) * math.sin(a)
        hole = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, can_h / 2 + 2])
        can = can - hole

    # V 槽
    for z_off in [-can_h / 2 + 8, 0, can_h / 2 - 8]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.translate([0, 0, z_off])
        can = can - groove

    # 端盖
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.translate([0, 0, -can_h / 2 + 1])
    can = can + cap

    save(can, "motor_can_v4.stl")


# ============================================================
# Part 3: Side Plate（端板）
# ============================================================
def make_side_plate():
    plate_r = TUBE_OR + 5
    h = 6

    plate = C(h, plate_r)
    plate = plate - C(h + 2, BALL_R + 3)

    # 螺栓孔
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 4) * math.cos(a)
        by = (plate_r - 4) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 减重孔
    for i in range(3):
        a = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 10) * math.cos(a)
        py = (plate_r / 2 + 10) * math.sin(a)
        light = C(h + 2, 12, 32)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate_v4.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v4: 一体化蜘蛛结构（参考图黄色件）")
    print("=" * 50)

    make_spider_body()
    make_motor_can()
    make_side_plate()

    print(f"\n✓ 3 个零件 → {OUTPUT_DIR}/")
    print(f"\n打印数量:")
    print(f"  spider_body_v4:   1（一件集成：管 + 臂 + 电机座）")
    print(f"  motor_can_v4:     3（电机外壳）")
    print(f"  side_plate_v4:    2（端板）")


if __name__ == "__main__":
    export_all()