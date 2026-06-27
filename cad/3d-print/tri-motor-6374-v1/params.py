"""
Football Launcher — 3-Motor 120° Monocoque v2
关键修正：管壁开孔让电机穿过接触球面

参考图特征：
- 白色管体上有圆孔，电机轴/外壳穿过管壁进入内部
- 橙色一体壳体包裹管体 + 电机卡座
- 桥接筋连接卡座
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
BALL_R = BALL_D / 2              # 110mm

# 6374 外转子电机
MOTOR_OD = 63
MOTOR_OR = MOTOR_OD / 2          # 31.5mm
MOTOR_LEN = 74
MOTOR_SHAFT_D = 8
MOTOR_BOLT_D = 4
MOTOR_BOLT_SPACING = 31

# 接触几何
MOTOR_CENTER_R = BALL_R + MOTOR_OR  # 141.5mm

# 发射管
TUBE_OR = MOTOR_CENTER_R + MOTOR_LEN / 2 + 5  # ~183mm
TUBE_IR = BALL_R + 3                          # 113mm
TUBE_LEN = 120

# 管壁开孔
# 电机外壳穿过管壁 → 开孔直径 = MOTOR_OD + 间隙
PORT_D = MOTOR_OD + 6           # 69mm（每侧 3mm 间隙）
PORT_R = PORT_D / 2             # 34.5mm

# 壳体
SHELL_WALL = 4
SHELL_GAP = 0.3

BOLT_D = 5
SEGMENTS = 64
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


# ============================================================
# CSG 工具
# ============================================================
def C(h, r_bot, r_top=None):
    if r_top is None: r_top = r_bot
    return Manifold.cylinder(h, r_bot, r_top, SEGMENTS)

def R(h, r_out, r_in):
    return C(h, r_out) - C(h + 0.4, r_in)

def B(w, d, h):
    return Manifold.cube((w, d, h), center=True)

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
# Part 1: Monocoque Shell（一体式壳体 — 含管壁开孔）
# ============================================================
def make_monocoque_shell():
    """
    一体式壳体：
    - 中心管体（带 3 个电机穿过孔）
    - 3 个电机卡座凸台 120° 均布
    - 桥接筋
    - 对开法兰
    """
    clamp_or = TUBE_OR + 10
    clamp_h = TUBE_LEN

    # ---- 主管体 ----
    shell = R(clamp_h, TUBE_OR, TUBE_IR)

    # ---- 管壁开孔（3 个，120°，电机穿过） ----
    for i in range(3):
        angle_deg = i * 120
        rad = math.radians(angle_deg)

        # 开孔中心在管壁上
        port_cx = TUBE_OR * math.cos(rad)
        port_cy = TUBE_OR * math.sin(rad)

        # 圆柱开孔（径向穿过管壁）
        # 圆柱轴线沿径向（从管外到管内）
        port = C(TUBE_OR * 2, PORT_R)
        # 旋转使轴线沿径向
        port = port.rotate([math.pi / 2, 0, 0])
        port = port.rotate([0, 0, rad])
        port = port.translate([port_cx, port_cy, clamp_h / 2])
        shell = shell - port

        # ---- 电机卡座凸台（开孔周围加厚） ----
        boss_r = PORT_R + SHELL_WALL + 3
        boss_len = MOTOR_LEN + 5
        boss = C(boss_len, boss_r) - C(boss_len + 0.4, PORT_R - 1)
        boss = boss.rotate([math.pi / 2, 0, 0])
        boss = boss.rotate([0, 0, rad])
        boss = boss.translate([
            (TUBE_OR + boss_len / 2 - 2) * math.cos(rad),
            (TUBE_OR + boss_len / 2 - 2) * math.sin(rad),
            clamp_h / 2
        ])
        shell = shell + boss

        # ---- 桥接筋（卡座两侧到管体） ----
        for side in [-1, 1]:
            bridge_angle = rad + side * math.radians(35)
            bridge = B(6, TUBE_OR * 0.6, clamp_h - 40)
            bridge = bridge.rotate([0, 0, bridge_angle])
            bridge = bridge.translate([
                (TUBE_OR * 0.4) * math.cos(bridge_angle),
                (TUBE_OR * 0.4) * math.sin(bridge_angle),
                clamp_h / 2
            ])
            shell = shell + bridge

        # ---- 线槽出口（卡座底部） ----
        wire = B(MOTOR_OD, 8, 12)
        wire = wire.rotate([0, 0, rad])
        wire = wire.translate([
            (TUBE_OR + MOTOR_LEN / 2) * math.cos(rad),
            (TUBE_OR + MOTOR_LEN / 2) * math.sin(rad),
            8
        ])
        shell = shell - wire

        # ---- M4 电机固定螺丝孔（卡座侧面） ----
        bolt_r = MOTOR_BOLT_SPACING / 2
        for bi in range(4):
            bolt_angle = math.radians(bi * 90)
            screw = C(SHELL_WALL + 6, MOTOR_BOLT_D / 2 + 0.1)
            screw = screw.rotate([0, 0, bolt_angle])
            screw = screw.translate([
                (TUBE_OR + MOTOR_LEN + 2) * math.cos(rad) + bolt_r * math.cos(rad + bolt_angle),
                (TUBE_OR + MOTOR_LEN + 2) * math.sin(rad) + bolt_r * math.sin(rad + bolt_angle),
                clamp_h / 2
            ])
            shell = shell - screw

    # ---- 合体法兰孔 ----
    for z in [10, clamp_h - 10]:
        for i in range(8):
            a = math.radians(i * 45)
            bx = (clamp_or + 4) * math.cos(a)
            by = (clamp_or + 4) * math.sin(a)
            hole = C(12, BOLT_D / 2 + 0.15)
            hole = hole.translate([bx, by, z])
            shell = shell - hole

    # ---- 两端法兰环 ----
    for z in [0, clamp_h]:
        flange = C(3, clamp_or + 8) - C(4, TUBE_IR)
        flange = flange.translate([0, 0, z - 1.5])
        shell = shell + flange

    save(shell, "monocoque_shell.stl")


# ============================================================
# Part 2: Motor Clamp Cap（电机卡座盖板）
# ============================================================
def make_motor_clamp_cap():
    """
    电机盖板：扣在电机上方，弧形匹配电机外壳
    - 2 个 M4 螺丝孔
    """
    cap_r = MOTOR_OR + SHELL_GAP + SHELL_WALL
    cap_or = cap_r + 3
    cap_h = 10

    # 弧形盖板（120° 扇区）
    cap = C(cap_h, cap_or) - C(cap_h + 0.4, cap_r)

    # 切扇区
    cut = B(cap_or * 3, cap_or * 2, cap_h + 2)
    cut = cut.rotate([0, 0, 30])
    cut = cut.translate([0, -cap_or, 0])
    cap = cap - cut
    cut2 = B(cap_or * 3, cap_or * 2, cap_h + 2)
    cut2 = cut2.rotate([0, 0, -30])
    cut2 = cut2.translate([0, cap_or, 0])
    cap = cap - cut2

    # M4 孔
    for y_off in [-8, 8]:
        hole = C(cap_h + 2, MOTOR_BOLT_D / 2 + 0.1)
        hole = hole.translate([0, y_off, 0])
        cap = cap - hole

    save(cap, "motor_clamp_cap.stl")


# ============================================================
# Part 3: Side Plate（侧板）
# ============================================================
def make_side_plate():
    plate_r = TUBE_OR + 10
    h = 5

    plate = C(h, plate_r) - C(h + 2, TUBE_IR)

    # 3 组电机穿过缺口
    for i in range(3):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)
        notch = B(PORT_D + 8, PORT_D + 8, h + 2)
        notch = notch.rotate([0, 0, angle])
        notch = notch.translate([cx, cy, 0])
        plate = plate - notch

    # 螺栓孔
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 5) * math.cos(a)
        by = (plate_r - 5) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 减重孔
    for i in range(3):
        angle = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 5) * math.cos(angle)
        py = (plate_r / 2 + 5) * math.sin(angle)
        light = C(h + 2, 12)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate.stl")


# ============================================================
# Part 4: Flange Ring（法兰环）
# ============================================================
def make_flange_ring():
    h = 10
    ring_or = TUBE_OR + 10
    ring_ir = TUBE_OR - 1

    ring = C(h, ring_or) - C(h + 0.4, ring_ir)

    for i in range(8):
        a = math.radians(i * 45)
        bx = (TUBE_OR + 5) * math.cos(a)
        by = (TUBE_OR + 5) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15)
        hole = hole.translate([bx, by, 0])
        ring = ring - hole

    for a_deg in [0, 180]:
        a = math.radians(a_deg)
        px = (TUBE_OR + 5) * math.cos(a)
        py = (TUBE_OR + 5) * math.sin(a)
        pin = C(h + 2, 2.1)
        pin = pin.translate([px, py, 0])
        ring = ring - pin

    save(ring, "flange_ring.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("Football Launcher — Monocoque v2 (with tube ports)")
    print("=" * 50)
    print(f"Ball:       {BALL_D}mm")
    print(f"Tube:       {TUBE_IR*2}mm ID / {TUBE_OR*2}mm OD")
    print(f"Port:       {PORT_D}mm (motor passes through)")
    print(f"Motor:      6374 × 3 @ 120°")
    print(f"Motor R:    {MOTOR_CENTER_R}mm from axis")
    print()

    make_monocoque_shell()
    make_motor_clamp_cap()
    make_side_plate()
    make_flange_ring()

    print(f"\n✓ 4 个零件 → {OUTPUT_DIR}/")
    print(f"\n打印数量:")
    print(f"  monocoque_shell:    2（对开）")
    print(f"  motor_clamp_cap:    6（每电机 2 片）")
    print(f"  side_plate:         2（两端）")
    print(f"  flange_ring:        2（两端）")


if __name__ == "__main__":
    export_all()
