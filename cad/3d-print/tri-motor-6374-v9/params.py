"""
Football Launcher — v9 完全分离设计
- 独立管（带 3 个 can 通过孔）
- 独立 cradle（外挂管外，M5 螺栓固定）
- Can 通过管壁孔接触球
- 球导轨
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
TUBE_OR = 130
TUBE_LEN = 200

# 3 电机 120° 分布
N_MOTORS = 3
MOTOR_HOLE_DIA = MOTOR_D + 4   # 67mm 管壁孔（让 can 穿过）

# 电机位置（径向外挂）
# Cradle 中心在管外，距离管壁 MOTOR_HOLE_DIA/2 + MOTOR_HOLE_DIA/2
# 简化：cradle 中心在 TUBE_OR + 35 = 165mm 处
CRADLE_CENTER_R = TUBE_OR + 35  # 165mm cradle 中心到管中心
CRADLE_LEN = MOTOR_L + 8         # 82mm cradle 长度（容纳电机 + 法兰）
CRADLE_OD = MOTOR_D + 14         # 77mm cradle 外径
CRADLE_WALL = 5                  # 壁厚

# 辐条轮
WHEEL_RIM_OR = CRADLE_CENTER_R + 30  # 195mm
WHEEL_RIM_W = 10
WHEEL_THICK = 6                  # 薄盘
WHEEL_N_SPOKES = 3
WHEEL_SPOKE_W = 14

# 球导轨（管内 4 条凸筋，让球保持中心）
GUIDE_RIB_W = 6
GUIDE_RIB_H = 4
GUIDE_N_RIBS = 4

BOLT_D = 5
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
# Part 1: Launch Tube（管 + can 孔 + 球导轨）
# ============================================================
def make_launch_tube_v9():
    """管壁带 3 个 can 孔 + 球导轨"""
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 3 个 can 通过孔（管壁上）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = (TUBE_OR + TUBE_IR) / 2 * math.cos(angle)
        cy = (TUBE_OR + TUBE_IR) / 2 * math.sin(angle)
        hole = C(TUBE_LEN + 2, MOTOR_HOLE_DIA / 2)
        hole = hole.translate([cx, cy, 0])
        body = body - hole

    # 球导轨（管内 4 条凸筋，轴向贯通）
    for i in range(GUIDE_N_RIBS):
        angle = math.radians(i * 90 + 45)  # 4 条，间隔 90°
        # 凸筋位置：在管内壁，靠近电机位置但不在电机孔上
        # 用圆柱切出凸筋
        rib_r = TUBE_IR + GUIDE_RIB_H / 2
        rib = C(TUBE_LEN, rib_r)
        # 切割凸筋宽度
        cut_w = GUIDE_RIB_W
        cut = Manifold.cube((TUBE_OR * 2, cut_w * 2, TUBE_LEN + 2), center=True)
        cut = cut.rotate([0, 0, math.degrees(angle)])
        cut = cut.translate([0, 0, 0])
        rib = rib - cut
        # 只保留中心部分
        # 用更大的盒子限制
        # 简化：直接凸筋
        rib_keep = Manifold.cube((TUBE_OR * 2, cut_w, TUBE_LEN), center=True)
        rib_keep = rib_keep.rotate([0, 0, math.degrees(angle)])
        # 计算凸筋中心位置
        cx = (TUBE_IR + GUIDE_RIB_H / 2) * math.cos(angle + math.pi / 2)
        cy = (TUBE_IR + GUIDE_RIB_H / 2) * math.sin(angle + math.pi / 2)
        rib_keep = rib_keep.translate([cx, cy, 0])
        body = body + rib_keep

    # 加固环（两端）
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "launch_tube_v9.stl")


# ============================================================
# Part 2: Motor Cradle（外挂辐条轮 — 独立件）
# ============================================================
def make_motor_cradle_v9():
    """
    外挂 cradle：
    - 中心 hub 容纳电机（径向轴）
    - 3 条辐条 + 外圈
    - 外圈 M5 螺栓固定到管
    - 中心 hub 法兰端 4×M4 固定电机
    """
    parts = Manifold()

    # 中心 hub（径向圆柱）
    hub_outer = C(CRADLE_LEN, CRADLE_OD / 2).rotate([0, math.pi / 2, 0])
    hub_inner = C(CRADLE_LEN + 0.4, MOTOR_D / 2 + 0.5).rotate([0, math.pi / 2, 0])
    hub = hub_outer - hub_inner

    # 电机轴孔
    shaft = C(CRADLE_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16).rotate([0, math.pi / 2, 0])
    hub = hub - shaft

    # 4 个 M4 螺栓孔（端面）
    for j in range(4):
        ja = math.radians(j * 90)
        bolt = C(8, MOTOR_HOLE_D / 2 + 0.1, 16).rotate([math.pi / 2, 0, 0]).rotate([0, 0, ja])
        bolt = bolt.translate([CRADLE_LEN / 2, 0, 0])
        hub = hub - bolt

    parts = parts + hub

    # 内圈端面（朝向管一侧）— 切平
    # 在 X = 0 处切平（让 cradle 紧贴管壁）
    cut_plate = Manifold.cube((CRADLE_OD, CRADLE_OD * 2, CRADLE_OD * 2), center=True)
    cut_plate = cut_plate.translate([-(CRADLE_LEN / 2 + CRADLE_WALL), 0, 0])
    # 只保留 X > 0 部分
    parts = parts - cut_plate

    # 内圈连接环（紧贴管壁的环形）
    inner_ring = C(WHEEL_THICK, TUBE_OR + 1) - C(WHEEL_THICK + 0.4, TUBE_OR - 4)
    parts = parts + inner_ring

    # 3 条辐条（径向平面 YZ 内）
    spoke_len = (WHEEL_RIM_OR - CRADLE_OD) / 2 - WHEEL_RIM_W / 2
    spoke_offset = (CRADLE_OD + WHEEL_RIM_OR) / 4
    for j in range(WHEEL_N_SPOKES):
        sa = math.radians(j * 120)
        spoke = Manifold.cube((WHEEL_THICK, spoke_len, WHEEL_SPOKE_W), center=True)
        spoke = spoke.rotate([sa, 0, 0])
        spoke = spoke.translate([0, spoke_offset * math.cos(sa), spoke_offset * math.sin(sa)])
        parts = parts + spoke

    # 外圈
    rim = C(WHEEL_THICK, WHEEL_RIM_OR / 2).rotate([0, math.pi / 2, 0]) - \
          C(WHEEL_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2).rotate([0, math.pi / 2, 0])
    for j in range(6):
        ra = math.radians(j * 60)
        by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
        bz = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
        bolt = C(WHEEL_THICK + 2, 2.7, 16)
        bolt = bolt.translate([0, by, bz])
        rim = rim - bolt

    parts = parts + rim

    save(parts, "motor_cradle_v9.stl")


# ============================================================
# Part 3: Motor Can（径向电机外壳 — 通过管壁孔）
# ============================================================
def make_motor_can_v9():
    """电机外壳，长度足够穿过管壁接触球面"""
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    # 长度 = 电机长度 + 穿过管壁厚度 + 接触球面凸出量
    # 管壁厚 27mm + 接触凸出 5mm + 电机长度 74mm + 外露 5mm
    can_h = MOTOR_L + 30  # 104mm

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)
    can = can.rotate([0, math.pi / 2, 0])

    # 法兰（外端固定到 cradle）
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

    # 端面十字凹槽
    cross_w = 2.5
    cross_depth = 1.5
    cross_len = can_r_out - 2
    cross1 = Manifold.cube((cross_depth * 2, cross_len, cross_w), center=True)
    cross1 = cross1.translate([-can_h / 2 + cross_depth, 0, 0])
    can = can - cross1
    cross2 = Manifold.cube((cross_depth * 2, cross_w, cross_len), center=True)
    cross2 = cross2.translate([-can_h / 2 + cross_depth, 0, 0])
    can = can - cross2

    # V 槽（3 道）
    for x_off in [-can_h / 2 + 12, 0, can_h / 2 - 12]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    # 端盖
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-can_h / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v9.stl")


# ============================================================
# Part 4: Side Plate
# ============================================================
def make_side_plate_v9():
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

    save(plate, "side_plate_v9.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v9: 完全分离设计 — 管 + 外挂 cradle + can 穿管壁")
    print("=" * 50)
    print("优化点：")
    print("- 管和 cradle 独立件")
    print("- cradle 外挂在管外（M5 螺栓固定）")
    print("- can 长度增加（穿过管壁 + 接触球面）")
    print("- 管内 4 条球导轨")
    print()

    make_launch_tube_v9()
    make_motor_cradle_v9()
    make_motor_can_v9()
    make_side_plate_v9()

    print(f"\n✓ 4 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()