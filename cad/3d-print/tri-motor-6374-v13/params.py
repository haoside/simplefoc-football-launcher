"""
Football Launcher — v13 视觉模仿参考图
不考虑电机轴向角度，只模仿参考图的视觉结构
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 缩放因子（参考图 → 足球发射）
# ============================================================
SCALE = 2.5

# 球
BALL_D = 220
BALL_R = BALL_D / 2

# 6374 电机
MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 参考图视觉比例 → 足球发射
# Cradle 是盘状（垂直于参考管轴），3 条辐条，4 颗 M5 外圈螺栓
# 等比例放大：每个尺寸 × 2.5

# 管
TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 140
TUBE_LEN = 180

# Cradle 盘（参考图比例放大）
# 参考图：轮外径约 60mm（球径 75mm）→ 放大 2.5-3×
# 球径 220mm，轮外径 ≈ 球径 × 0.85 = 187mm
WHEEL_RIM_OR = 187
WHEEL_RIM_W = 12
CRADLE_HUB_OD = MOTOR_D + 8   # 71mm
CRADLE_HUB_LEN = MOTOR_L + 8  # 82mm（容纳电机 + 法兰空间）
CRADLE_THICK = 14              # 盘厚（参考图视觉估算）
CRADLE_N_SPOKES = 3             # 参考图明显 3 条辐条
WHEEL_SPOKE_W = 18

# Cradle 中心位置（参考图：cradle 在管上方/侧方）
CRADLE_R = TUBE_OR / 2 + 55   # 125mm 半径

# Can
CAN_LEN = MOTOR_D * 0.5       # 30mm
CAN_R_OUT = MOTOR_D / 2 + 1   # 32.5mm
CAN_R_IN = MOTOR_D / 2 + 0.3  # 32.3mm

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
# Part 1: Integrated Spider Body（模仿参考图）
# ============================================================
def make_spider_body_v13():
    """
    视觉模仿参考图：
    - 中心管段（球通道）
    - 3 个盘状 cradle，3 条辐条，外圈 4 颗 M5
    - 集成单件
    """
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)

        # ===== Cradle 主体（盘状，垂直于 Z 轴）=====
        # 中心 hub（沿 Z 轴，容纳电机）
        hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2)
        hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
        hub = hub_outer - hub_inner

        # 电机轴孔
        shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
        hub = hub - shaft

        # 4×M4 电机螺栓孔（端面）
        for j in range(4):
            ja = math.radians(j * 90)
            bolt_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            bolt_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            bolt = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([bolt_x, bolt_y, CRADLE_HUB_LEN / 2 - 3])
            hub = hub - bolt

        # 平移 hub 到 cradle 中心
        hub = hub.translate([cx, cy, (TUBE_LEN - CRADLE_HUB_LEN) / 2])
        body = body + hub

        # ===== 3 条辐条（XY 平面内）=====
        spoke_len = (WHEEL_RIM_OR - CRADLE_HUB_OD) / 2 - WHEEL_RIM_W / 2
        spoke_offset = (CRADLE_HUB_OD + WHEEL_RIM_OR) / 4

        for j in range(CRADLE_N_SPOKES):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, WHEEL_SPOKE_W, CRADLE_THICK), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     (TUBE_LEN - CRADLE_THICK) / 2])
            body = body + spoke

        # ===== 外圈（XY 平面内的环）=====
        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - \
              C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2)
        rim = rim.translate([cx, cy, (TUBE_LEN - CRADLE_THICK) / 2])

        # 4 颗 M5 外圈螺栓（参考图可见 4 颗螺栓）
        for j in range(4):
            ra = math.radians(j * 90 + 45)
            bx = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
            by = (WHEEL_RIM_W / 2 - WHEEL_RIM_W) * math.cos(ra)  # 错误
        # 修复：从外圈中心取螺栓位置
        # rim 中心在 (cx, cy)，外圈半径 WHEEL_RIM_OR - WHEEL_RIM_W/2
        rim_bolt_r = WHEEL_RIM_OR - WHEEL_RIM_W / 2
        for j in range(4):
            ra = math.radians(j * 90 + 45)
            # 螺栓位置在 rim 局部坐标 (rim_bolt_r*cos, rim_bolt_r*sin)
            # 需要平移到 (cx, cy) + 局部坐标
            bx = rim_bolt_r * math.cos(ra)
            by = rim_bolt_r * math.sin(ra)
            bolt = Manifold.cylinder(CRADLE_THICK + 2, 2.7, 2.7, 16)
            # 平移到全局位置 (cx + bx, cy + by, mid_z)
            bolt = bolt.translate([cx + bx, cy + by, (TUBE_LEN - CRADLE_THICK) / 2])
            rim = rim - bolt

        body = body + rim

        # ===== Cradle 与管之间的连接筋（参考图未见，先不要）=====

    # ===== 两端加固环 =====
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "spider_body_v13.stl")


# ============================================================
# Part 2: Motor Can
# ============================================================
def make_motor_can_v13():
    can = C(CAN_LEN, CAN_R_OUT) - C(CAN_LEN + 0.4, CAN_R_IN)
    can = can.rotate([0, math.pi / 2, 0])

    # 球端十字凹槽
    cross_w = 2.5
    cross_depth = 1.5
    cross_len = CAN_R_OUT - 2
    cross1 = Manifold.cube((cross_depth * 2, cross_len, cross_w), center=True)
    cross1 = cross1.translate([-CAN_LEN / 2 + cross_depth, 0, 0])
    can = can - cross1
    cross2 = Manifold.cube((cross_depth * 2, cross_w, cross_len), center=True)
    cross2 = cross2.translate([-CAN_LEN / 2 + cross_depth, 0, 0])
    can = can - cross2

    for x_off in [-CAN_LEN / 2 + 5, CAN_LEN / 2 - 5]:
        groove = C(3, CAN_R_OUT + 0.5) - C(3.4, CAN_R_OUT - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    cap = C(2, CAN_R_OUT - 5) - C(3, CAN_R_IN, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-CAN_LEN / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v13.stl")


# ============================================================
# Part 3: Side Plate
# ============================================================
def make_side_plate_v13():
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

    save(plate, "side_plate_v13.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v13: 纯视觉模仿参考图（不考虑轴向角度）")
    print("=" * 50)
    print("参考图视觉特征 → 足球发射规格：")
    print(f"- 球 220mm（参考图 ~75mm）")
    print(f"- 电机 6374（参考图 2212/6T）")
    print(f"- 盘外径 187mm（≈ 球径 0.85×）")
    print(f"- 盘厚 14mm")
    print(f"- 3 辐条 + 4 颗 M5 外圈螺栓")
    print()

    make_spider_body_v13()
    make_motor_can_v13()
    make_side_plate_v13()

    print(f"\n✓ 3 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()