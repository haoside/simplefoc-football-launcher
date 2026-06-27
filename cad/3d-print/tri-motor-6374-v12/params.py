"""
Football Launcher — v12 参考图等比例放大版
- 缩放因子 2.25-2.5×
- 保留参考图比例
- 适配 6374 + 220mm 球
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 缩放参数（基于参考图比例放大到 6374 + 220mm）
# ============================================================
SCALE = 2.5  # 缩放因子

# 球
BALL_D = 220
BALL_R = BALL_D / 2

# 6374 电机（参考 2212 放大）
MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管
TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 140                  # 管外径
TUBE_LEN = 200

# Cradle 比例（参考图保持）
# 参考图：轮外径 ≈ 2.5×电机 OD，hub ≈ 1.15×电机 OD
WHEEL_RATIO = 2.5
CRADLE_HUB_OD = MOTOR_D * 1.15    # 72.5mm
WHEEL_RIM_OR = MOTOR_D * WHEEL_RATIO  # 157.5mm（基于电机）

# Cradle 中心位置（管外）
# 参考图：cradle 中心距管中心 ≈ 1.8×电机 OD
CRADLE_OFFSET_RATIO = 1.8
CRADLE_R = MOTOR_D * CRADLE_OFFSET_RATIO + TUBE_OR / 2  # 电机轴到管中心距离
# 113 + 28*1.8 = 113 + 50 = 163mm，cradle 中心在 163mm 处
# 调整：从管中心到 cradle 中心
CRADLE_CENTER_R = TUBE_OR / 2 + MOTOR_D * 1.5  # = 70 + 94.5 = 164.5mm

# 盘厚（参考图：cradle 盘厚 ≈ 0.25×电机 OD）
CRADLE_THICK = MOTOR_D * 0.25  # 15.75mm

# 辐条
WHEEL_RIM_W = 12
WHEEL_N_SPOKES = 3
WHEEL_SPOKE_W = 18
WHEEL_SPOKE_T = CRADLE_THICK

# Hub 长度（沿 Z 轴，容纳电机 + 法兰空间）
CRADLE_HUB_LEN = MOTOR_L + 10  # 84mm

# Can（径向）
CAN_LEN = MOTOR_D * 0.5  # 30mm（参考图：can 短而粗）
CAN_R_OUT = MOTOR_D / 2 + 1
CAN_R_IN = MOTOR_D / 2 + 0.3

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
# Part 1: Integrated Spider Body（参考图等比例放大）
# ============================================================
def make_spider_body_v12():
    """
    参考图等比例放大版一体化结构：
    - 中心管段
    - 3 个盘状 cradle（垂直于 Z 轴）
    - 比例保持参考图视觉特征
    """
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_CENTER_R * math.cos(angle_rad)
        cy = CRADLE_CENTER_R * math.sin(angle_rad)

        # ===== Hub（沿 Z 轴）=====
        hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2)
        hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
        hub = hub_outer - hub_inner

        # 电机轴孔
        shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
        hub = hub - shaft

        # 4 个 M4 电机螺栓孔（端面，XY 平面）
        for j in range(4):
            ja = math.radians(j * 90)
            bolt_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            bolt_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            bolt = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([bolt_x, bolt_y, CRADLE_HUB_LEN / 2 - 3])
            hub = hub - bolt

        # 平移 hub
        hub = hub.translate([cx, cy, (TUBE_LEN - CRADLE_HUB_LEN) / 2])
        body = body + hub

        # ===== 3 条辐条（XY 平面内）=====
        spoke_len = (WHEEL_RIM_OR - CRADLE_HUB_OD) / 2 - WHEEL_RIM_W / 2
        spoke_offset = (CRADLE_HUB_OD + WHEEL_RIM_OR) / 4

        for j in range(WHEEL_N_SPOKES):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, WHEEL_SPOKE_W, WHEEL_SPOKE_T), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     (TUBE_LEN - CRADLE_THICK) / 2])
            body = body + spoke

        # ===== 外圈（XY 平面内的环）=====
        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - \
              C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2)
        rim = rim.translate([cx, cy, (TUBE_LEN - CRADLE_THICK) / 2])

        # 4 个 M5 螺栓孔（外圈，参考图显示 4 颗）
        for j in range(4):
            ra = math.radians(j * 90 + 45)
            bx = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
            by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
            # 在 XY 平面，bolt 沿 Z 方向
            bolt = C(CRADLE_THICK + 2, 2.7, 16)
            # bolt 中心在 XY 平面内的 (bx, by)，需要平移到 (cx + bx, cy + by)
            # 但 rim 已经在 (cx, cy) 位置，所以 bolt 只需要在 rim 的局部坐标内
            bolt = bolt.translate([cx + bx - cx, cy + by - cy, 0])
            # 上面那行不对，直接平移：
            bolt = bolt.translate([bx - bx, by - by, 0])  # noop
            # 实际上 bolt 应该是相对于 rim 中心的位置
            # 修正：直接用 rim 中心偏移
            bolt = Manifold.cylinder(CRADLE_THICK + 2, 2.7, 2.7, 16)
            bolt = bolt.translate([cx + bx, cy + by, (TUBE_LEN - CRADLE_THICK) / 2])
            rim = rim - bolt

        body = body + rim

    # ===== 两端加固环 =====
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "spider_body_v12.stl")


# ============================================================
# Part 2: Motor Can（径向，参考图比例）
# ============================================================
def make_motor_can_v12():
    can = C(CAN_LEN, CAN_R_OUT) - C(CAN_LEN + 0.4, CAN_R_IN)
    can = can.rotate([0, math.pi / 2, 0])  # 轴向 X（径向）

    # 球端十字凹槽（参考图特征）
    cross_w = 2.5
    cross_depth = 1.5
    cross_len = CAN_R_OUT - 2
    cross1 = Manifold.cube((cross_depth * 2, cross_len, cross_w), center=True)
    cross1 = cross1.translate([-CAN_LEN / 2 + cross_depth, 0, 0])
    can = can - cross1
    cross2 = Manifold.cube((cross_depth * 2, cross_w, cross_len), center=True)
    cross2 = cross2.translate([-CAN_LEN / 2 + cross_depth, 0, 0])
    can = can - cross2

    # V 槽
    for x_off in [-CAN_LEN / 2 + 5, CAN_LEN / 2 - 5]:
        groove = C(3, CAN_R_OUT + 0.5) - C(3.4, CAN_R_OUT - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    # 端盖
    cap = C(2, CAN_R_OUT - 5) - C(3, CAN_R_IN, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-CAN_LEN / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v12.stl")


# ============================================================
# Part 3: Side Plate
# ============================================================
def make_side_plate_v12():
    plate_r = TUBE_OR + 5
    h = 6

    plate = C(h, plate_r)
    plate = plate - C(h + 2, BALL_R + 3)

    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 4) * math.cos(a)
        by = (plate_r - 4) * math.sin(a)
        hole = C(h + 2, 2.7, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    for i in range(3):
        a = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 10) * math.cos(a)
        py = (plate_r / 2 + 10) * math.sin(a)
        light = C(h + 2, 12, 32)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate_v12.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v12: 参考图等比例放大（缩放 2.5×）")
    print("=" * 50)
    print(f"电机 OD: {MOTOR_D}mm = 2.5× 参考图 25mm")
    print(f"球:     {BALL_D}mm = 2.93× 参考图 75mm")
    print(f"轮外径: {WHEEL_RIM_OR:.1f}mm (电机×{WHEEL_RATIO})")
    print(f"Hub OD: {CRADLE_HUB_OD:.1f}mm (电机×1.15)")
    print(f"Cradle R: {CRADLE_CENTER_R:.1f}mm (管外 {MOTOR_D*1.5:.0f}mm)")
    print()

    make_spider_body_v12()
    make_motor_can_v12()
    make_side_plate_v12()

    print(f"\n✓ 3 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()