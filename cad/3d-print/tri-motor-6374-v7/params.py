"""
Football Launcher — v7 优化贴近参考图
v6 方向已对（电机轴径向），v7 进一步优化细节：
- Cradle 更紧凑（盘状，不是长筒）
- Can 明显伸出 cradle 朝向球
- 辐条更明显
- 4 个 M4 电机固定螺栓孔可见
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

# 管
TUBE_IR = BALL_R + 3
TUBE_OR = 130
TUBE_LEN = 180

# 电机位置（径向）
# 电机 can 外缘接触球面
# 电机 can 中心距管中心 = BALL_R - 接触深度
# 简化：电机中心在 TUBE_OR + 5 = 135mm 处
# 这样电机 can 接触球面（can 内陷进管壁球通道）
MOTOR_CENTER_R = TUBE_OR + 5    # 135mm 电机中心到管中心

# Cradle（径向盘状电机座）
CRADLE_THICK = 12              # ★ 盘厚（薄盘状）
CRADLE_HUB_OD = MOTOR_D + 8    # 71mm
CRADLE_HUB_LEN = MOTOR_L + 8   # 82mm（盘厚 12 + 电机 74 - 4）
CRADLE_RIM_OR = MOTOR_CENTER_R + 50  # 185mm 轮外径
CRADLE_RIM_W = 10
CRADLE_N_SPOKES = 3            # 3 条辐条
CRADLE_SPOKE_W = 12
CRADLE_SPOKE_T = 12            # 与盘厚一致

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
# Part 1: Launch Tube（球通道）
# ============================================================
def make_launch_tube_v7():
    """球通道管（200mm 长）"""
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 端部加固环
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "launch_tube_v7.stl")


# ============================================================
# Part 2: Motor Cradle（径向盘状电机座 — 优化）
# ============================================================
def make_motor_cradle_v7():
    """
    径向盘状电机座（贴近参考图）：
    - 中心 hub：圆柱容纳 6374，电机轴径向
    - 3 条辐条：径向平面内，120° 间隔
    - 外圈：环形，4 个螺栓孔
    - 4 个 M4 电机端面螺栓孔（电机固定）
    """
    parts = Manifold()

    # ===== 中心 hub（径向圆柱，容纳电机）=====
    # 电机轴向 X（径向），hub 圆柱轴向 X
    hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2)
    hub_outer = hub_outer.rotate([0, math.pi / 2, 0])  # 轴向 z → x
    hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    hub_inner = hub_inner.rotate([0, math.pi / 2, 0])
    hub = hub_outer - hub_inner

    # 电机轴孔（径向）
    shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    shaft = shaft.rotate([0, math.pi / 2, 0])
    hub = hub - shaft

    # 4 个 M4 螺栓孔（端面，垂直于径向，Y-Z 平面）
    for j in range(4):
        ja = math.radians(j * 90)
        # 螺栓在电机外端（X = -CRADLE_HUB_LEN/2 处）
        bolt = C(8, MOTOR_HOLE_D / 2 + 0.1, 16)
        # 螺栓沿 Y 方向（径向平面内）
        bolt = bolt.rotate([math.pi / 2, 0, 0])  # 圆柱轴从 z 改 y
        bolt = bolt.rotate([0, 0, ja])
        bolt = bolt.translate([-CRADLE_HUB_LEN / 2, 0, 0])
        hub = hub - bolt

    parts = parts + hub

    # ===== 3 条辐条（径向平面，YZ 平面内，120° 间隔）=====
    spoke_len = (CRADLE_RIM_OR - CRADLE_HUB_OD) / 2 - CRADLE_RIM_W / 2
    spoke_offset = (CRADLE_HUB_OD + CRADLE_RIM_OR) / 4

    for j in range(CRADLE_N_SPOKES):
        sa = math.radians(j * 120)
        # 辐条在 YZ 平面：长度方向 Y，宽度方向 Z，厚度方向 X
        spoke = Manifold.cube((CRADLE_SPOKE_T, spoke_len, CRADLE_SPOKE_W), center=True)
        # 旋转到 YZ 平面内的角度（围绕 X 轴）
        spoke = spoke.rotate([sa, 0, 0])
        # 平移到径向位置（径向轴 X）
        # Y 位置 = spoke_offset * cos(sa), Z 位置 = spoke_offset * sin(sa)
        spoke = spoke.translate([0, spoke_offset * math.cos(sa), spoke_offset * math.sin(sa)])
        parts = parts + spoke

    # ===== 外圈（YZ 平面内环，垂直于径向轴 X）=====
    rim_outer = C(CRADLE_SPOKE_T, CRADLE_RIM_OR / 2)
    rim_outer = rim_outer.rotate([0, math.pi / 2, 0])  # 轴向改为 X
    rim_inner = C(CRADLE_SPOKE_T + 0.4, (CRADLE_RIM_OR - 2 * CRADLE_RIM_W) / 2)
    rim_inner = rim_inner.rotate([0, math.pi / 2, 0])
    rim = rim_outer - rim_inner

    # 6 个 M5 螺栓孔（外圈周向均布）
    for j in range(6):
        ra = math.radians(j * 60)
        by = (CRADLE_RIM_OR - CRADLE_RIM_W / 2) * math.cos(ra)
        bz = (CRADLE_RIM_OR - CRADLE_RIM_W / 2) * math.sin(ra)
        bolt = C(CRADLE_SPOKE_T + 2, 2.7, 16)
        bolt = bolt.translate([0, by, bz])
        rim = rim - bolt

    parts = parts + rim

    save(parts, "motor_cradle_v7.stl")


# ============================================================
# Part 3: Motor Can（径向电机外壳套 — 优化，伸出 cradle）
# ============================================================
def make_motor_can_v7():
    """
    径向电机外壳套：
    - 内陷进 cradle，朝向球伸出
    - 长度 > 电机长度（伸出部分）
    - V 槽
    """
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L + 10  # 比电机长 10mm（朝球伸出 10mm）

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)
    can = can.rotate([0, math.pi / 2, 0])  # 轴向 z → x

    # 法兰（端面，固定到 hub 外端）
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

    # V 槽（3 道）
    for x_off in [-can_h / 2 + 8, 0, can_h / 2 - 8]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.rotate([0, math.pi / 2, 0])
        groove = groove.translate([x_off, 0, 0])
        can = can - groove

    # 端盖（can 朝球端）
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.rotate([0, math.pi / 2, 0])
    cap = cap.translate([-can_h / 2 + 1, 0, 0])
    can = can + cap

    save(can, "motor_can_v7.stl")


# ============================================================
# Part 4: Side Plate（端板）
# ============================================================
def make_side_plate_v7():
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

    save(plate, "side_plate_v7.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v7: 优化贴近参考图")
    print("=" * 50)
    print("v6 方向已对（径向电机轴），v7 优化细节：")
    print("- 紧凑盘状 cradle")
    print("- Can 伸出 cradle 朝向球")
    print("- 更明显的辐条")
    print("- 可见螺栓孔")
    print()

    make_launch_tube_v7()
    make_motor_cradle_v7()
    make_motor_can_v7()
    make_side_plate_v7()

    print(f"\n✓ 4 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()