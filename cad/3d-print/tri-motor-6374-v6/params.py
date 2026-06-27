"""
Football Launcher — v6 修正电机轴向
关键修正：电机轴向必须垂直于管长（径向），否则只能让球原地打转

正确机制：
- 3 电机 120° 分布，电机轴沿径向
- 电机 can 沿径向旋转，3 个 can 夹持球
- 球被沿管轴方向（z）加速射出
- 电机差速产生旋转（弧线球/传中效果）
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

# 6374 电机 — 轴向沿径向（垂直于管）
MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管
TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 130                  # 管外径
TUBE_LEN = 200                 # ★ 管长要够长（球通过 + 加速距离）

# 电机位置（径向）
# 电机 can 接触球面 = 球面 + 电机 can 半径
# 电机 can 中心 = 球心 + (球半径 + can 突出) = BALL_R + 0
# 电机中心（轴线位置）= can 中心 + 电机 can 内偏 = BALL_R + (MOTOR_D/2 - 中心偏移)
# 简化：让电机中心在 TUBE_OR + 10 = 140mm 处
MOTOR_CENTER_R = TUBE_OR + 10  # 140mm 电机中心到管中心

# 电机座（径向支架）
CRADLE_LEN = TUBE_LEN          # 与管等长
CRADLE_THICK = 8               # 座厚（垂直于径向）
CRADLE_HEIGHT = MOTOR_D + 16   # 79mm 容纳电机高度

# 辐条轮（径向平面）
WHEEL_OR = MOTOR_CENTER_R + 40  # 180mm 轮外径
WHEEL_HUB_OD = MOTOR_D + 12    # 75mm
WHEEL_HUB_LEN = CRADLE_LEN     # 与管等长
WHEEL_RIM_W = 8
WHEEL_N_SPOKES = 3
WHEEL_SPOKE_W = 12
WHEEL_SPOKE_T = 8

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
# Part 1: Launch Tube（发射管 — 球通道）
# ============================================================
def make_launch_tube_v6():
    """发射管主通道"""
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 端部加固环
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    # 3 组辐条轮固定螺栓孔（每组 6 个 M5，沿管均布在径向位置）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        for j in range(4):
            ja = math.radians(j * 90 + 45)
            z_off = 20 + j * (TUBE_LEN - 40) / 3
            # 螺栓孔在管外壁，径向方向
            bx = (TUBE_OR + 1) * math.cos(angle + ja) if j < 4 else 0
            by = (TUBE_OR + 1) * math.sin(angle + ja) if j < 4 else 0
            # 简化：只在径向方向有螺栓
            bolt = C(8, 2.7, 16)
            bolt = bolt.translate([bx, by, z_off])
            body = body - bolt

    save(body, "launch_tube_v6.stl")


# ============================================================
# Part 2: Motor Cradle with Spoked Wheel（★ 径向辐条轮电机座）
# ============================================================
def make_motor_cradle_v6():
    """
    径向辐条轮电机座：
    - 3 条辐条（120° 间隔，在径向平面内）
    - 中心 hub 容纳电机（轴向沿径向）
    - 外圈
    - 电机轴孔垂直于管轴（径向）
    - 电机 can 端朝向管中心
    """
    parts = Manifold()

    # ===== 中心 hub（容纳 6374 电机）=====
    # 电机轴沿径向（X 方向），hub 是 X 方向延伸的圆柱
    # Cylinder 默认轴向 Z，需要旋转使其沿 X
    hub_outer = C(WHEEL_HUB_LEN, WHEEL_HUB_OD / 2)
    hub_outer = hub_outer.rotate([0, math.pi / 2, 0])  # 轴向从 z 改为 x
    hub_inner = C(WHEEL_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    hub_inner = hub_inner.rotate([0, math.pi / 2, 0])
    hub = hub_outer - hub_inner

    # 电机轴孔（沿径向 x 轴）
    shaft = C(WHEEL_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    shaft = shaft.rotate([0, math.pi / 2, 0])
    hub = hub - shaft

    # 电机固定端 M4 螺栓孔（端面，垂直于径向）
    for j in range(4):
        ja = math.radians(j * 90)
        # 螺栓位置在电机端面（X = -WHEEL_HUB_LEN/2 处）
        jx = -WHEEL_HUB_LEN / 2
        jy = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        jz = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        bolt = C(8, MOTOR_HOLE_D / 2 + 0.1, 16)
        bolt = bolt.translate([jx, jy, jz])
        hub = hub - bolt

    parts = parts + hub

    # ===== 3 条辐条（径向平面，120° 间隔）=====
    # 辐条在 YZ 平面内，从 hub 延伸到外圈
    # 3 条辐条，每条长 = (WHEEL_OR - WHEEL_HUB_OD) / 2 - WHEEL_RIM_W/2
    spoke_len = (WHEEL_OR - WHEEL_HUB_OD) / 2 - WHEEL_RIM_W / 2
    spoke_offset = (WHEEL_HUB_OD + WHEEL_OR) / 4

    for j in range(WHEEL_N_SPOKES):
        sa = math.radians(j * 120)
        # 辐条在 YZ 平面，宽度 WHEEL_SPOKE_W，厚度 WHEEL_SPOKE_T（X 方向）
        spoke = Manifold.cube((WHEEL_SPOKE_T, spoke_len, WHEEL_SPOKE_W), center=True)
        # 旋转到 YZ 平面内的角度
        # 先在 YZ 平面：长方形 (Y=spoke_len, Z=WHEEL_SPOKE_W)
        # 旋转围绕 X 轴
        spoke = spoke.rotate([0, 0, sa])
        # 平移到径向位置
        spoke = spoke.translate([0, spoke_offset * math.cos(sa), spoke_offset * math.sin(sa)])
        parts = parts + spoke

    # ===== 外圈（YZ 平面内的环）=====
    # 外圈是 YZ 平面内的环形
    # 通过旋转圆柱实现：圆柱轴沿 X，半径 WHEEL_OR/2，高度 = 圈厚度
    rim_outer = C(WHEEL_SPOKE_T, WHEEL_OR / 2)
    rim_outer = rim_outer.rotate([0, math.pi / 2, 0])
    rim_inner = C(WHEEL_SPOKE_T + 0.4, (WHEEL_OR - 2 * WHEEL_RIM_W) / 2)
    rim_inner = rim_inner.rotate([0, math.pi / 2, 0])
    rim = rim_outer - rim_inner

    # 外圈螺栓孔（6 个）
    for j in range(6):
        ra = math.radians(j * 60)
        bx = 0
        by = (WHEEL_OR - WHEEL_RIM_W / 2) * math.cos(ra)
        bz = (WHEEL_OR - WHEEL_RIM_W / 2) * math.sin(ra)
        bolt = C(WHEEL_SPOKE_T + 2, 2.7, 16)
        bolt = bolt.translate([bx, by, bz])
        rim = rim - bolt

    parts = parts + rim

    save(parts, "motor_cradle_v6.stl")


# ============================================================
# Part 3: Motor Can（径向电机外壳套）
# ============================================================
def make_motor_can_v6():
    """电机外壳套：套在电机外转子上，径向方向"""
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)
    # 旋转使轴沿 X（径向）
    can = can.rotate([0, math.pi / 2, 0])

    # 法兰（固定到 hub）
    flange = Manifold.cube((4, MOTOR_D + 20, MOTOR_D + 20), center=True)
    flange = flange.translate([can_h / 2 + 2, 0, 0])
    can = can + flange

    # 法兰螺栓孔
    for j in range(4):
        ja = math.radians(j * 90)
        hx = can_h / 2 + 2
        hy = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        hz = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        hole = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, hz])
        can = can - hole

    # V 槽（沿轴向分布在 3 个位置）
    for x_off in [-can_h / 2 + 8, 0, can_h / 2 - 8]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    # 端盖
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-can_h / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v6.stl")


# ============================================================
# Part 4: Side Plate（端板）
# ============================================================
def make_side_plate_v6():
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

    save(plate, "side_plate_v6.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v6: 电机轴向修正（垂直于管，径向）")
    print("=" * 50)
    print("关键修正：电机 can 沿径向旋转，从 3 个方向")
    print("夹持球，把球沿管轴方向（z）射出。")
    print("差速产生旋转 → 弧线球/传中效果。")
    print()

    make_launch_tube_v6()
    make_motor_cradle_v6()  # ★ 径向辐条轮
    make_motor_can_v6()
    make_side_plate_v6()

    print(f"\n✓ 4 个零件 → {OUTPUT_DIR}/")
    print(f"\n打印数量:")
    print(f"  launch_tube_v6:    1")
    print(f"  motor_cradle_v6:   3（径向辐条轮）")
    print(f"  motor_can_v6:      3")
    print(f"  side_plate_v6:     2")


if __name__ == "__main__":
    export_all()