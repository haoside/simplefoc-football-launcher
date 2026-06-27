"""
Football Launcher — v10 一体化结构（180° 电机关系）
- 一体打印：管 + 3 cradle + 桥接筋（单件）
- 电机轴径向（垂直于管）
- 电机本体在管外，can 穿过管壁接触球
- 180° 关系：电机本体一端 + can 另一端反向（can 在管内）
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
TUBE_OR = 140                  # 加厚一点容纳 can
TUBE_LEN = 120                 # 较短，球加速靠旋转而非管长

# 电机位置
# 电机 can 接触球面，can 中心距球心 = BALL_R
# can 半径 ≈ MOTOR_D/2 = 31.5mm
# 电机 can 中心到管中心 = BALL_R - (can_r - contact_offset)
# 简化：让电机 can 内端接触球面 → can 中心到管中心 = BALL_R = 110mm
# 但电机 can 中心 = 电机中心，所以电机中心 = 110mm 处（在管内）
# 不合理。改为：电机中心在管壁外侧一点
MOTOR_CENTER_R = TUBE_OR + 5    # 145mm 电机中心到管中心

# Cradle
CRADLE_LEN = MOTOR_L + 12       # 86mm 长
CRADLE_HUB_OD = MOTOR_D + 12    # 75mm 外径
CRADLE_HUB_LEN = CRADLE_LEN     # 同长
CRADLE_THICK = 10               # 厚

# 辐条轮
WHEEL_RIM_OR = MOTOR_CENTER_R + 45  # 190mm 轮外径
WHEEL_RIM_W = 12
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
# Part 1: Integrated Spider Body（一体化主结构）
# ============================================================
def make_spider_body_v10():
    """
    一体化蜘蛛结构（180° 电机关系）：
    - 中心管段（球通道）
    - 3 个 cradle 120° 分布
    - 每个 cradle：电机 hub + 3 辐条 + 外圈
    - 电机 can 端嵌入管壁（180° 反向）
    - 桥接筋（cradle 之间）
    """
    # 中心管段
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 3 个电机位（含 cradle）
    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = MOTOR_CENTER_R * math.cos(angle_rad)
        cy = MOTOR_CENTER_R * math.sin(angle_rad)

        # ===== Cradle hub（容纳电机，径向轴）=====
        hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2).rotate([0, math.pi / 2, 0])
        hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5).rotate([0, math.pi / 2, 0])
        hub = hub_outer - hub_inner

        # 电机轴孔
        shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16).rotate([0, math.pi / 2, 0])
        hub = hub - shaft

        # 4 个 M4 电机螺栓孔
        for j in range(4):
            ja = math.radians(j * 90)
            bolt = C(8, MOTOR_HOLE_D / 2 + 0.1, 16).rotate([math.pi / 2, 0, 0]).rotate([0, 0, ja])
            bolt = bolt.translate([CRADLE_HUB_LEN / 2, 0, 0])
            hub = hub - bolt

        # 平移 hub 到电机中心
        hub = hub.rotate([0, 0, angle_deg])
        hub = hub.translate([cx, cy, 0])
        body = body + hub

        # ===== 3 条辐条（径向平面 YZ 内）=====
        spoke_len = (WHEEL_RIM_OR - CRADLE_HUB_OD) / 2 - WHEEL_RIM_W / 2
        spoke_offset = (CRADLE_HUB_OD + WHEEL_RIM_OR) / 4

        for j in range(WHEEL_N_SPOKES):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((WHEEL_SPOKE_T, spoke_len, WHEEL_SPOKE_W), center=True)
            spoke = spoke.rotate([sa, 0, 0])
            spoke = spoke.translate([0, spoke_offset * math.cos(sa), spoke_offset * math.sin(sa)])
            # 旋转到对应角度并平移
            spoke = spoke.rotate([0, 0, angle_deg])
            spoke = spoke.translate([cx, cy, 0])
            body = body + spoke

        # ===== 外圈（环）=====
        rim = C(WHEEL_SPOKE_T, WHEEL_RIM_OR / 2).rotate([0, math.pi / 2, 0]) - \
              C(WHEEL_SPOKE_T + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2).rotate([0, math.pi / 2, 0])

        # 6 个 M5 螺栓孔
        for j in range(6):
            ra = math.radians(j * 60)
            by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
            bz = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
            bolt = C(WHEEL_SPOKE_T + 2, 2.7, 16)
            bolt = bolt.translate([0, by, bz])
            rim = rim - bolt

        rim = rim.rotate([0, 0, angle_deg])
        rim = rim.translate([cx, cy, 0])
        body = body + rim

    # ===== 桥接筋（cradle 之间连接）=====
    for i in range(N_MOTORS):
        a_mid = math.radians(i * 120 + 60)
        # 在管外壁添加局部凸起筋
        rib = C(TUBE_LEN, TUBE_OR + 3) - C(TUBE_LEN + 0.4, TUBE_OR + 1)
        # 切割成弧段
        cut1 = Manifold.cube((TUBE_OR * 3, TUBE_OR * 2, TUBE_LEN), center=True)
        cut1 = cut1.rotate([0, 0, math.degrees(a_mid) + 35])
        cut1 = cut1.translate([0, TUBE_OR * 1.5, 0])
        cut2 = Manifold.cube((TUBE_OR * 3, TUBE_OR * 2, TUBE_LEN), center=True)
        cut2 = cut2.rotate([0, 0, math.degrees(a_mid) - 35])
        cut2 = cut2.translate([0, TUBE_OR * 1.5, 0])
        rib = rib - cut1 - cut2
        body = body + rib

    # ===== 两端加固环 =====
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "spider_body_v10.stl")


# ============================================================
# Part 2: Motor Can（径向电机外壳，180° 反向）
# ============================================================
def make_motor_can_v10():
    """电机外壳：180° 反向，can 一端朝向球，另一端固定到 hub"""
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L + 10  # 比电机长 10mm（穿入管内 5mm + 外露 5mm）

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)
    can = can.rotate([0, math.pi / 2, 0])

    # 外端法兰（固定到 hub 外端）
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

    # 内端（朝球）十字凹槽
    cross_w = 2.5
    cross_depth = 1.5
    cross_len = can_r_out - 2
    cross1 = Manifold.cube((cross_depth * 2, cross_len, cross_w), center=True)
    cross1 = cross1.translate([-can_h / 2 + cross_depth, 0, 0])
    can = can - cross1
    cross2 = Manifold.cube((cross_depth * 2, cross_w, cross_len), center=True)
    cross2 = cross2.translate([-can_h / 2 + cross_depth, 0, 0])
    can = can - cross2

    # V 槽（3 道沿轴向）
    for x_off in [-can_h / 2 + 12, 0, can_h / 2 - 12]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    # 内端盖
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-can_h / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v10.stl")


# ============================================================
# Part 3: Side Plate（端板）
# ============================================================
def make_side_plate_v10():
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

    save(plate, "side_plate_v10.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v10: 一体化结构（180° 电机关系）")
    print("=" * 50)
    print("- 一件：管 + 3 cradle + 桥接筋")
    print("- 电机轴径向，can 穿过管壁接触球")
    print("- 180° 关系：电机本体外 / can 内")
    print()

    make_spider_body_v10()
    make_motor_can_v10()
    make_side_plate_v10()

    print(f"\n✓ 3 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()