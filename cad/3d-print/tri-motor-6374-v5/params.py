"""
Football Launcher — v5 一体化 + 辐条轮特征
参考图关键特征：橙色件是明显辐条轮（外圈+辐条+中心 hub）
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

# 中心管段
TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 130                  # 管外径
TUBE_LEN = 90                  # 管长

# 辐条轮（电机座）
WHEEL_OR = 165                 # 轮外径
WHEEL_THICK = 8                # 轮厚
WHEEL_RIM_W = 10               # 外圈宽度
WHEEL_HUB_OD = MOTOR_D + 14    # 中心 hub 77mm
WHEEL_HUB_LEN = MOTOR_L + 10   # hub 深度 84mm
WHEEL_N_SPOKES = 3             # ★ 3 条辐条（120° 间隔）
WHEEL_SPOKE_W = 14             # 辐条宽
WHEEL_SPOKE_T = 8              # 辐条厚

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


def make_spoked_wheel(cx, cy, cz=0):
    """
    生成单个辐条轮（参考图橙色件的核心特征）：
    - 外圈（环状）
    - 3 条辐条（120° 间隔）
    - 中心 hub（容纳 6374 电机）
    """
    parts = Manifold()

    # ===== 中心 hub（容纳电机，轴向沿 z）=====
    hub_outer = C(WHEEL_HUB_LEN, WHEEL_HUB_OD / 2)
    hub_inner = C(WHEEL_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    hub = hub_outer - hub_inner

    # 电机轴孔
    shaft = C(WHEEL_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    hub = hub - shaft

    # 电机端面 M4 螺栓孔（4 个，固定电机）
    for j in range(4):
        ja = math.radians(j * 90)
        jx = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        jy = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        bolt = C(WHEEL_HUB_LEN + 2, MOTOR_HOLE_D / 2 + 0.1, 16)
        bolt = bolt.translate([jx, jy, 0])
        hub = hub - bolt

    parts = parts + hub

    # ===== 3 条径向辐条（120° 间隔）=====
    spoke_len = (WHEEL_OR - WHEEL_HUB_OD) / 2 - WHEEL_RIM_W / 2
    spoke_offset = (WHEEL_HUB_OD + WHEEL_OR) / 4

    spokes = Manifold()
    for j in range(WHEEL_N_SPOKES):
        sa = math.radians(j * 120)
        # 辐条主体（长方体）
        spoke = Manifold.cube((spoke_len, WHEEL_SPOKE_W, WHEEL_SPOKE_T), center=True)
        # 旋转到对应角度
        spoke = spoke.rotate([0, 0, sa])
        # 移动到径向位置
        spoke = spoke.translate([spoke_offset * math.cos(sa), spoke_offset * math.sin(sa), 0])
        spokes = spokes + spoke

    parts = parts + spokes

    # ===== 外圈（环形）=====
    rim_outer = C(WHEEL_THICK, WHEEL_OR / 2)
    rim_inner = C(WHEEL_THICK + 0.4, (WHEEL_OR - 2 * WHEEL_RIM_W) / 2)
    rim = rim_outer - rim_inner

    # 外圈螺栓孔（6 个均布）
    for j in range(6):
        ra = math.radians(j * 60)
        bx = (WHEEL_OR - WHEEL_RIM_W / 2) * math.cos(ra)
        by = (WHEEL_OR - WHEEL_RIM_W / 2) * math.sin(ra)
        bolt = C(WHEEL_THICK + 2, 2.7, 16)
        bolt = bolt.translate([bx, by, 0])
        rim = rim - bolt

    parts = parts + rim

    # 平移到指定位置
    parts = parts.translate([cx, cy, cz])

    return parts


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
# Part 1: Integrated Spider Body（一体化 + 辐条轮）
# ============================================================
def make_spider_body_v5():
    """
    一体化蜘蛛结构：
    - 中心管段
    - 3 个辐条轮（120° 均布，参考图橙色件核心特征）
    - 管段与轮之间的连接肋
    """
    # 中心管段
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 3 个辐条轮（每个独立完整：hub + 3 辐条 + 外圈）
    wheel_center_r = (WHEEL_HUB_OD + TUBE_OR) / 2 + 5  # 轮中心位置

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = wheel_center_r * math.cos(angle_rad)
        cy = wheel_center_r * math.sin(angle_rad)

        wheel = make_spoked_wheel(cx, cy, 0)
        body = body + wheel

        # 管段到轮 hub 的连接肋（梯形过渡）
        rib_w = WHEEL_SPOKE_W + 6
        rib_t = WHEEL_SPOKE_T
        rib = Manifold.cube((TUBE_OR - TUBE_IR, rib_w, rib_t), center=True)
        # 旋转到径向
        rib = rib.rotate([0, 0, angle_deg])
        # 平移：从管内壁延伸到 hub 内壁
        # 起点：TUBE_OR 处（管外壁）
        # 终点：wheel_center - WHEEL_HUB_OD/2 处（hub 近端）
        mid_r = (TUBE_OR + wheel_center_r - WHEEL_HUB_OD / 2) / 2
        rib = rib.translate([mid_r, 0, 0])
        body = body + rib

    # 加强环（管段两端）
    for z in [6, TUBE_LEN - 6]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    # 桥接筋（轮之间，沿管外壁）
    for i in range(N_MOTORS):
        a_mid = math.radians(i * 120 + 60)
        # 在管外壁加局部凸起
        rib = C(TUBE_LEN, TUBE_OR + 3) - C(TUBE_LEN + 0.4, TUBE_OR + 1)
        # 切割成局部弧段
        cut1 = Manifold.cube((TUBE_OR * 3, TUBE_OR * 2, TUBE_LEN), center=True)
        cut1 = cut1.rotate([0, 0, math.degrees(a_mid) + 35])
        cut1 = cut1.translate([0, TUBE_OR * 1.5, 0])
        cut2 = Manifold.cube((TUBE_OR * 3, TUBE_OR * 2, TUBE_LEN), center=True)
        cut2 = cut2.rotate([0, 0, math.degrees(a_mid) - 35])
        cut2 = cut2.translate([0, TUBE_OR * 1.5, 0])
        rib = rib - cut1 - cut2
        body = body + rib

    save(body, "spider_body_v5.stl")


# ============================================================
# Part 2: Motor Can（电机外壳套）
# ============================================================
def make_motor_can_v5():
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)

    flange = Manifold.cube((MOTOR_D + 20, MOTOR_D + 20, 4), center=True)
    flange = flange.translate([0, 0, can_h / 2 + 2])
    can = can + flange

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

    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.translate([0, 0, -can_h / 2 + 1])
    can = can + cap

    save(can, "motor_can_v5.stl")


# ============================================================
# Part 3: Side Plate（端板）
# ============================================================
def make_side_plate_v5():
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

    save(plate, "side_plate_v5.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v5: 一体化 + 辐条轮特征")
    print("=" * 50)

    make_spider_body_v5()
    make_motor_can_v5()
    make_side_plate_v5()

    print(f"\n✓ 3 个零件 → {OUTPUT_DIR}/")
    print(f"\n打印数量:")
    print(f"  spider_body_v5:   1（一体化 + 辐条轮特征）")
    print(f"  motor_can_v5:     3")
    print(f"  side_plate_v5:    2")


if __name__ == "__main__":
    export_all()