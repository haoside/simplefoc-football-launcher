"""
Football Launcher — v14 修正：电机径向 + 平面飞轮盘
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

MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管
TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 140
TUBE_LEN = 200

# Cradle 位置（参考图视觉）
CRADLE_R = TUBE_OR / 2 + 55   # 125mm cradle 中心到管中心

# 飞轮盘（关键修正！）
FLYWHEEL_D = 50              # 飞轮直径（比电机小，更轻）
FLYWHEEL_T = 8               # 飞轮厚度
FLYWHEEL_HUB_D = 20          # 飞轮 hub 内径
FLYWHEEL_GROOVE = 2          # V 槽深

# Hub 容纳电机
HUB_OD = MOTOR_D + 8         # 71mm
HUB_LEN = MOTOR_L + 10       # 84mm

# 辐条轮
WHEEL_RIM_OR = 160           # 外径
WHEEL_RIM_W = 10
CRADLE_THICK = 10
WHEEL_N_SPOKES = 3
WHEEL_SPOKE_W = 16
WHEEL_SPOKE_T = CRADLE_THICK

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
# Part 1: Integrated Spider Body（修正版）
# ============================================================
def make_spider_body_v14():
    """
    修正版：电机径向（轴垂直于管）
    - 中心管段
    - 3 个 cradle：hub（沿径向）+ 飞轮盘（垂直于径向）
    - 飞轮盘面朝球
    """
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = CRADLE_R * math.cos(angle_rad)
        cy = CRADLE_R * math.sin(angle_rad)
        # Cradle 中心位置

        # ===== Cradle 主体（盘状，垂直于 Z 轴）=====
        # 中心 hub（沿 Z 轴，容纳电机）
        hub_outer = C(HUB_LEN, HUB_OD / 2)
        hub_inner = C(HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
        hub = hub_outer - hub_inner

        # 电机轴孔
        shaft = C(HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
        hub = hub - shaft

        # 4×M4 电机螺栓孔（端面）
        for j in range(4):
            ja = math.radians(j * 90)
            bolt_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            bolt_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            bolt = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([bolt_x, bolt_y, HUB_LEN / 2 - 3])
            hub = hub - bolt

        hub = hub.translate([cx, cy, (TUBE_LEN - HUB_LEN) / 2])
        body = body + hub

        # ===== 3 条辐条（XY 平面内）=====
        spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - WHEEL_RIM_W / 2
        spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4

        for j in range(WHEEL_N_SPOKES):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((spoke_len, WHEEL_SPOKE_W, WHEEL_SPOKE_T), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([cx + spoke_offset * math.cos(sa),
                                     cy + spoke_offset * math.sin(sa),
                                     (TUBE_LEN - CRADLE_THICK) / 2])
            body = body + spoke

        # ===== 外圈 =====
        rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - \
              C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2)
        rim = rim.translate([cx, cy, (TUBE_LEN - CRADLE_THICK) / 2])

        # 4 颗 M5 外圈螺栓
        for j in range(4):
            ra = math.radians(j * 90 + 45)
            bx = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
            by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
            bolt = Manifold.cylinder(CRADLE_THICK + 2, 2.7, 2.7, 16)
            bolt = bolt.translate([cx + bx, cy + by, (TUBE_LEN - CRADLE_THICK) / 2])
            rim = rim - bolt

        body = body + rim

        # ===== 飞轮盘（关键修正）=====
        # 飞轮盘：盘面垂直于电机轴（径向 X）
        # 盘在 motor +X 端外侧（远离管中心）
        # 盘轴向 X，盘面在 YZ 平面

        flywheel_center = (cx + FLYWHEEL_D / 2 + 5, cy, (TUBE_LEN) / 2)
        flywheel = C(FLYWHEEL_T, FLYWHEEL_D / 2)
        # 旋转使轴向 X（径向）
        flywheel = flywheel.rotate([0, math.pi / 2, 0])
        flywheel = flywheel.translate(flywheel_center)
        body = body + flywheel

        # 飞轮盘螺栓孔（4 颗 M4，对应电机轴端面）
        for j in range(4):
            ja = math.radians(j * 90)
            bh_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
            bh_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
            bh = Manifold.cylinder(FLYWHEEL_T + 2, MOTOR_HOLE_D / 2 + 0.1, 16)
            bh = bh.rotate([0, math.pi / 2, 0])
            bh = bh.translate([flywheel_center[0], flywheel_center[1] + bh_y, flywheel_center[2] + bh_x])
            body = body - bh

        # 飞轮盘 V 槽（增加抓球摩擦）
        # V 槽在盘面（YZ 平面）上的圆环
        for z_off in [-2, 0, 2]:
            groove_outer = Manifold.cylinder(FLYWHEEL_T + 0.5, FLYWHEEL_D / 2, FLYWHEEL_D / 2, 48)
            groove_outer = groove_outer.rotate([0, math.pi / 2, 0])
            groove_inner = Manifold.cylinder(FLYWHEEL_T + 1, FLYWHEEL_D / 2 - FLYWHEEL_GROOVE, FLYWHEEL_D / 2 - FLYWHEEL_GROOVE, 48)
            groove_inner = groove_inner.rotate([0, math.pi / 2, 0])
            groove = groove_outer - groove_inner
            groove = groove.translate([flywheel_center[0], flywheel_center[1], flywheel_center[2] + z_off])
            body = body - groove

    # ===== 两端加固环 =====
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "spider_body_v14.stl")


# ============================================================
# Part 2: Side Plate
# ============================================================
def make_side_plate_v14():
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

    save(plate, "side_plate_v14.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v14: 修正版 — 电机径向 + 平面飞轮盘")
    print("=" * 50)
    print("关键修正：")
    print("- 电机轴沿径向（垂直于管）")
    print("- 飞轮盘面（不是圆柱 can）")
    print("- 盘旋转产生 Z 方向速度分量")
    print("- 球沿管轴方向射出")
    print()

    make_spider_body_v14()
    make_side_plate_v14()

    print(f"\n✓ 2 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()