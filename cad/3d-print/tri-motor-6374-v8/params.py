"""
Football Launcher — v8 单层薄盘 cradle，can 接触球面
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

TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 130
TUBE_LEN = 180

# 关键几何：电机 can 接触球面
# can 半径 = MOTOR_D/2 + 1 = 32.5mm
# can 外缘接触球面：can 中心到管中心 = BALL_R - can_r + 接触深度
# 让 can 接触球面（轻微压入 1mm）：can 中心 = BALL_R - can_r + 1 = 110 - 32.5 + 1 = 78.5mm
# 但这要求电机完全嵌入管内
# 更合理：让 can 部分嵌入管壁，can 中心 = TUBE_OR - 5 = 125mm
# 这样 can 内端在 125 - 32.5 = 92.5mm，嵌入球通道 92.5 < BALL_R = 110，接触球面
CAN_CENTER_R = TUBE_OR - 5    # 125mm can 中心到管中心（嵌入管壁）
MOTOR_CENTER_R = CAN_CENTER_R  # 电机中心 == can 中心

# Cradle 单层薄盘
CRADLE_THICK = 8              # ★ 单层薄盘（更接近参考图）
CRADLE_HUB_OD = MOTOR_D + 6   # 69mm hub 外径（贴近电机）
CRADLE_HUB_LEN = MOTOR_L + 4  # 78mm hub 深度（刚好容纳电机）
CRADLE_RIM_OR = MOTOR_CENTER_R + 55  # 180mm 轮外径
CRADLE_RIM_W = 10
CRADLE_N_SPOKES = 3
CRADLE_SPOKE_W = 14
CRADLE_SPOKE_T = 8

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
# Part 1: Launch Tube
# ============================================================
def make_launch_tube_v8():
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "launch_tube_v8.stl")


# ============================================================
# Part 2: Motor Cradle（单层薄盘，贴近参考图）
# ============================================================
def make_motor_cradle_v8():
    """
    单层薄盘 cradle（参考图风格）：
    - 中心 hub 容纳电机（轴向径向）
    - 3 条辐条 + 外圈
    - 单层 8mm 厚（参考图特征）
    """
    parts = Manifold()

    # ===== 中心 hub =====
    hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2).rotate([0, math.pi / 2, 0])
    hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5).rotate([0, math.pi / 2, 0])
    hub = hub_outer - hub_inner

    # 轴孔
    shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16).rotate([0, math.pi / 2, 0])
    hub = hub - shaft

    # 4 个 M4 电机螺栓孔（端面 Y-Z 平面）
    for j in range(4):
        ja = math.radians(j * 90)
        bolt = C(8, MOTOR_HOLE_D / 2 + 0.1, 16).rotate([math.pi / 2, 0, 0]).rotate([0, 0, ja])
        bolt = bolt.translate([-CRADLE_HUB_LEN / 2, 0, 0])
        hub = hub - bolt

    parts = parts + hub

    # ===== 3 条辐条（径向平面 YZ 内）=====
    spoke_len = (CRADLE_RIM_OR - CRADLE_HUB_OD) / 2 - CRADLE_RIM_W / 2
    spoke_offset = (CRADLE_HUB_OD + CRADLE_RIM_OR) / 4

    for j in range(CRADLE_N_SPOKES):
        sa = math.radians(j * 120)
        spoke = Manifold.cube((CRADLE_SPOKE_T, spoke_len, CRADLE_SPOKE_W), center=True)
        spoke = spoke.rotate([sa, 0, 0])
        spoke = spoke.translate([0, spoke_offset * math.cos(sa), spoke_offset * math.sin(sa)])
        parts = parts + spoke

    # ===== 外圈 =====
    rim_outer = C(CRADLE_SPOKE_T, CRADLE_RIM_OR / 2).rotate([0, math.pi / 2, 0])
    rim_inner = C(CRADLE_SPOKE_T + 0.4, (CRADLE_RIM_OR - 2 * CRADLE_RIM_W) / 2).rotate([0, math.pi / 2, 0])
    rim = rim_outer - rim_inner

    # 6 个 M5 螺栓孔
    for j in range(6):
        ra = math.radians(j * 60)
        by = (CRADLE_RIM_OR - CRADLE_RIM_W / 2) * math.cos(ra)
        bz = (CRADLE_RIM_OR - CRADLE_RIM_W / 2) * math.sin(ra)
        bolt = C(CRADLE_SPOKE_T + 2, 2.7, 16)
        bolt = bolt.translate([0, by, bz])
        rim = rim - bolt

    parts = parts + rim

    save(parts, "motor_cradle_v8.stl")


# ============================================================
# Part 3: Motor Can（嵌入管壁，端面十字凹槽）
# ============================================================
def make_motor_can_v8():
    """
    电机外壳套：
    - 嵌入管壁（中心在 125mm 处）
    - 端面有十字形凹槽（参考图特征）
    - V 槽
    """
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L + 8  # 略长于电机

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)
    can = can.rotate([0, math.pi / 2, 0])

    # 法兰（固定到 hub 外端）
    flange = Manifold.cube((4, MOTOR_D + 20, MOTOR_D + 20), center=True)
    flange = flange.translate([can_h / 2 + 2, 0, 0])
    can = can + flange

    # 法兰 M4 螺栓孔
    for j in range(4):
        ja = math.radians(j * 90)
        hy = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        hz = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        hole = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([can_h / 2 + 2, hy, hz])
        can = can - hole

    # ★ 端面十字形凹槽（参考图特征 — can 朝球端）
    # 在 X = -can_h/2 端面开十字槽
    cross_w = 2.5
    cross_depth = 1.5
    cross_len = can_r_out - 2

    # 横槽
    cross1 = Manifold.cube((cross_depth * 2, cross_len, cross_w), center=True)
    cross1 = cross1.translate([-can_h / 2 + cross_depth, 0, 0])
    can = can - cross1

    # 纵槽
    cross2 = Manifold.cube((cross_depth * 2, cross_w, cross_len), center=True)
    cross2 = cross2.translate([-can_h / 2 + cross_depth, 0, 0])
    can = can - cross2

    # V 槽（3 道沿轴向）
    for x_off in [-can_h / 2 + 12, 0, can_h / 2 - 12]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    # 端盖（朝球端）
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-can_h / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v8.stl")


# ============================================================
# Part 4: Side Plate
# ============================================================
def make_side_plate_v8():
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

    save(plate, "side_plate_v8.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v8: 单层薄盘 cradle + can 接触球面 + 十字凹槽")
    print("=" * 50)
    print("优化点：")
    print("- 单层 8mm 薄盘（v7 是 12mm）")
    print("- can 嵌入管壁（中心 125mm）")
    print("- can 端面十字凹槽（参考图特征）")
    print()

    make_launch_tube_v8()
    make_motor_cradle_v8()
    make_motor_can_v8()
    make_side_plate_v8()

    print(f"\n✓ 4 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()