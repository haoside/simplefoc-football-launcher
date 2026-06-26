"""
Football Launcher — 3-Motor 120° Independent Design
从零设计，6374 电机 × 3，标准 5 号足球

设计原则：
- FDM 可打印（无支撑 / 少支撑）
- 标准螺栓连接（M4/M5）
- 0.2-0.3mm FDM 公差
- 壁厚 ≥ 3mm
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 全局参数
# ============================================================

# 足球
BALL_D = 220                 # mm，标准 5 号足球
BALL_R = BALL_D / 2          # 110mm

# 发射滚轮
ROLLER_D = 70                # mm，滚轮外径
ROLLER_R = ROLLER_D / 2      # 35mm
ROLLER_W = 25                # mm，滚轮宽度（接触面宽度）
ROLLER_BORE = 8              # mm，电机轴孔
ROLLER_HUB_D = 16            # mm，轮毂直径

# 6374 电机
MOTOR_D = 63                 # mm，电机外径
MOTOR_L = 74                 # mm，电机长度
MOTOR_SHAFT_D = 8            # mm，轴径
MOTOR_BOLT_D = 4             # mm，安装螺丝 M4
MOTOR_BOLT_SPACING = 31      # mm，安装孔中心距

# 滚轮接触几何
# 滚轮外缘到球心距离 = BALL_R + ROLLER_R = 110 + 35 = 145mm
ROLLER_CENTER_R = BALL_R + ROLLER_R   # 145mm

# 结构
WALL = 4                     # mm，壁厚
FRAME_LEN = 120              # mm，框架长度（球道方向）
TUBE_OR = ROLLER_CENTER_R + 15  # mm，框架外半径 160mm
TUBE_IR = BALL_R + 3         # mm，框架内半径 113mm（球通过间隙）
ARM_LEN = 50                 # mm，电机臂长度
ARM_W = 20                   # mm，臂宽
ARM_H = 8                    # mm，臂厚
BOLT_D = 5                   # mm，M5 连接螺栓

SEGMENTS = 64
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


# ============================================================
# CSG 工具
# ============================================================
def C(h, r_bot, r_top=None):
    """圆柱"""
    if r_top is None:
        r_top = r_bot
    return Manifold.cylinder(h, r_bot, r_top, SEGMENTS)

def R(h, r_out, r_in):
    """管（空心圆柱）"""
    return C(h, r_out) - C(h + 0.4, r_in)

def B(w, d, h):
    """长方体"""
    return Manifold.cube((w, d, h), center=True)

def save(body, name):
    """导出 STL"""
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
# Part 1: Launch Tube（发射管 — 两半对开）
# ============================================================
def make_launch_tube():
    """
    发射管主框架：
    - 两半对开，法兰螺栓合体
    - 内径 213mm（球通过 + 间隙）
    - 外径 230mm
    - 3 组电机臂安装座 120° 均布
    - 两端法兰面
    """
    # 管体
    tube = R(FRAME_LEN, TUBE_OR, TUBE_IR)

    # 两端法兰环（增加端面刚性 + 对齐）
    for z in [0, FRAME_LEN]:
        flange = C(3, TUBE_OR + 8) - C(4, TUBE_IR)
        flange = flange.translate([0, 0, z - 1.5])
        tube = tube + flange

    # 3 组电机臂安装座（120° 均布）
    for i in range(3):
        angle = math.radians(i * 120)
        cx = TUBE_OR * math.cos(angle)
        cy = TUBE_OR * math.sin(angle)

        # 安装座凸台（方形，从管壁向外延伸）
        boss = B(ARM_W + 10, WALL * 3, FRAME_LEN - 20)
        boss = boss.rotate([0, 0, angle])
        boss = boss.translate([cx, cy, FRAME_LEN / 2])
        tube = tube + boss

        # M5 螺栓孔（臂固定用，每侧 2 个）
        for z_off in [15, FRAME_LEN - 15]:
            for y_off in [-6, 6]:
                # 计算螺栓位置（在安装座面上）
                nx = math.cos(angle + math.pi / 2)
                ny = math.sin(angle + math.pi / 2)
                px = cx + y_off * nx
                py = cy + y_off * ny
                hole = C(WALL * 4, BOLT_D / 2 + 0.15)
                hole = hole.translate([px, py, z_off])
                tube = tube - hole

    # 合体螺栓孔（法兰面上，每端 8 个）
    for z in [8, FRAME_LEN - 8]:
        for i in range(8):
            a = math.radians(i * 45)
            bx = (TUBE_OR + 4) * math.cos(a)
            by = (TUBE_OR + 4) * math.sin(a)
            hole = C(12, BOLT_D / 2 + 0.15)
            hole = hole.translate([bx, by, z])
            tube = tube - hole

    save(tube, "launch_tube.stl")


# ============================================================
# Part 2: Motor Mount（电机安装座）
# ============================================================
def make_motor_mount():
    """
    电机安装座：
    - 半圆卡箍包裹 6374 电机
    - 法兰面带 M4 孔固定电机
    - 侧面 M5 孔连接臂
    """
    clamp_r = MOTOR_D / 2 + WALL  # 卡箍内径
    clamp_or = clamp_r + WALL     # 卡箍外径
    clamp_h = MOTOR_L + 10        # 卡箍高度（比电机长 10mm）

    # 卡箍主体（管状，包裹电机）
    clamp = R(clamp_h, clamp_or, clamp_r)

    # 一半切掉（对开设计，方便装电机）
    cut = B(clamp_or * 3, clamp_or * 2, clamp_h + 2)
    cut = cut.translate([0, -clamp_or, 0])
    clamp = clamp - cut

    # 法兰面（电机固定端）
    flange = B(MOTOR_D + 20, clamp_or * 2, WALL)
    flange = flange.translate([0, 0, -WALL / 2])
    clamp = clamp + flange

    # M4 电机安装孔（4 个，90° 分布在法兰面上）
    bolt_r = MOTOR_BOLT_SPACING / 2
    for i in range(4):
        a = math.radians(i * 90)
        hx = bolt_r * math.cos(a)
        hy = bolt_r * math.sin(a)
        hole = C(WALL + 2, MOTOR_BOLT_D / 2 + 0.1)
        hole = hole.translate([hx, hy, -WALL / 2])
        clamp = clamp - hole

    # 中心轴孔（电机轴穿过）
    shaft = C(clamp_or * 2, MOTOR_SHAFT_D / 2 + 0.3)
    shaft = shaft.rotate([math.pi / 2, 0, 0])
    shaft = shaft.translate([0, 0, clamp_h / 2])
    clamp = clamp - shaft

    # M5 侧面连接孔（连接臂用，2 个对称）
    for y_off in [-clamp_or + 2, clamp_or - 2]:
        hole = C(clamp_or * 2, BOLT_D / 2 + 0.15)
        hole = hole.rotate([math.pi / 2, 0, 0])
        hole = hole.translate([0, y_off, clamp_h / 2])
        clamp = clamp - hole

    # 紧固螺栓孔（卡箍合口处，M5 穿通）
    for z_off in [15, clamp_h - 15]:
        hole = C(clamp_or + 4, BOLT_D / 2 + 0.15)
        hole = hole.rotate([math.pi / 2, 0, 0])
        hole = hole.translate([0, 0, z_off])
        clamp = clamp - hole

    save(clamp, "motor_mount.stl")


# ============================================================
# Part 3: Motor Arm（电机臂）
# ============================================================
def make_motor_arm():
    """
    结构臂：连接发射管安装座 ↔ 电机安装座
    - 两端各 2 个 M5 螺栓孔
    - 中间减重凹槽
    - 端部倒角
    """
    arm = B(ARM_LEN, ARM_W, ARM_H)

    # 两端安装孔（M5，每端 2 个）
    for x_off in [-ARM_LEN / 2 + 10, ARM_LEN / 2 - 10]:
        for y_off in [-ARM_W / 4, ARM_W / 4]:
            hole = C(ARM_H + 2, BOLT_D / 2 + 0.15)
            hole = hole.translate([x_off, y_off, 0])
            arm = arm - hole

    # 减重凹槽（双面，保留中间腹板）
    recess = B(ARM_LEN - 20, ARM_W - 8, ARM_H / 2 - 0.5)
    recess = recess.translate([0, 0, ARM_H / 4 + 0.25])
    arm = arm - recess

    # 端部倒角（4 角各切 3mm）
    for x in [-ARM_LEN / 2, ARM_LEN / 2]:
        for y in [-ARM_W / 2, ARM_W / 2]:
            chamfer = C(ARM_H + 2, 3)
            chamfer = chamfer.translate([x, y, 0])
            arm = arm - chamfer

    save(arm, "motor_arm.stl")


# ============================================================
# Part 4: Launch Roller（发射滚轮）
# ============================================================
def make_launch_roller():
    """
    发射滚轮：
    - 外径 70mm，带鼓形弧面（crowned profile）增加抓球
    - V 槽
    - 键槽 + 顶丝孔
    - 减重孔
    """
    r_out = ROLLER_R          # 35mm
    r_in = ROLLER_BORE / 2    # 4mm
    r_hub = ROLLER_HUB_D / 2  # 8mm

    # 主体（鼓形：中间微凸，用锥台模拟）
    body = C(ROLLER_W, r_out, r_out - 1)  # 微锥，中间高 1mm
    top = C(ROLLER_W, r_out - 1, r_out).translate([0, 0, 0])
    # 简化为直筒，加 V 槽实现抓球
    body = C(ROLLER_W, r_out)

    # 中心轴孔
    body = body - C(ROLLER_W + 2, r_in)

    # 轮毂加强（轴孔周围加厚区）
    hub = C(ROLLER_W - 4, r_hub) - C(ROLLER_W - 2, r_in)
    body = body + hub

    # V 槽（中间环形凹槽，深度 3mm）
    groove = C(ROLLER_W - 8, r_out + 0.3) - C(ROLLER_W - 6, r_out - 3)
    groove = groove.translate([0, 0, 4])
    body = body - groove

    # 键槽
    keyway = B(3, 1.5, ROLLER_W + 2)
    keyway = keyway.translate([0, r_in + 0.75, 0])
    body = body - keyway

    # 顶丝孔（侧面径向）
    screw = C(r_out + 2, 1.6)
    screw = screw.rotate([math.pi / 2, 0, 0])
    body = body - screw

    # 减重孔（轮辐间，4 个）
    for i in range(4):
        a = math.radians(i * 90 + 45)
        hx = (r_hub + 4) * math.cos(a)
        hy = (r_hub + 4) * math.sin(a)
        light = C(ROLLER_W - 8, 4)
        light = light.translate([hx, hy, 4])
        body = body - light

    save(body, "launch_roller.stl")


# ============================================================
# Part 5: Side Plate（侧板）
# ============================================================
def make_side_plate():
    """
    侧板：框架端面结构加强
    - 环形板，中心球通过孔
    - 3 组电机臂通过缺口
    - 法兰螺栓孔
    """
    plate_r = TUBE_OR + 8     # 比管外径大 8mm
    h = 5                      # 板厚

    # 主体
    plate = C(h, plate_r)

    # 中心球通过孔
    plate = plate - C(h + 2, TUBE_IR)

    # 3 组电机臂通过缺口（120° 均布）
    for i in range(3):
        angle = math.radians(i * 120)
        # 缺口位置在臂安装座处
        cx = TUBE_OR * math.cos(angle)
        cy = TUBE_OR * math.sin(angle)
        notch = B(ARM_W + 8, WALL * 4 + 4, h + 2)
        notch = notch.rotate([0, 0, angle])
        notch = notch.translate([cx, cy, 0])
        plate = plate - notch

    # 法兰螺栓孔（8 个，45° 间隔）
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 5) * math.cos(a)
        by = (plate_r - 5) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 减重孔（3 个大孔，120° 均布，臂之间）
    for i in range(3):
        angle = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 5) * math.cos(angle)
        py = (plate_r / 2 + 5) * math.sin(angle)
        light = C(h + 2, 15)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate.stl")


# ============================================================
# Part 6: Tube Flange Ring（管法兰连接环）
# ============================================================
def make_flange_ring():
    """
    法兰环：两个半管的合体连接件
    - 环形，卡在管外
    - M5 螺栓连接两半
    - 定位销孔
    """
    h = 10                     # 环高
    ring_or = TUBE_OR + 10     # 外径
    ring_ir = TUBE_OR - 1      # 内径（卡在管外壁）

    ring = C(h, ring_or) - C(h + 0.4, ring_ir)

    # M5 螺栓孔（每半 4 个，共 8 个）
    for i in range(8):
        a = math.radians(i * 45)
        bx = (TUBE_OR + 5) * math.cos(a)
        by = (TUBE_OR + 5) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15)
        hole = hole.translate([bx, by, 0])
        ring = ring - hole

    # 定位销孔（2 个，对称）
    for a_deg in [0, 180]:
        a = math.radians(a_deg)
        px = (TUBE_OR + 5) * math.cos(a)
        py = (TUBE_OR + 5) * math.sin(a)
        pin = C(h + 2, 2.1)
        pin = pin.translate([px, py, 0])
        ring = ring - pin

    save(ring, "flange_ring.stl")


# ============================================================
# 导出全部
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("Football Launcher — 3-Motor 120° Independent Design")
    print("=" * 50)
    print(f"Ball:    {BALL_D}mm")
    print(f"Channel: {TUBE_IR*2}mm ID / {TUBE_OR*2}mm OD")
    print(f"Roller:  {ROLLER_D}mm × {ROLLER_W}mm")
    print(f"Motor:   {MOTOR_D}mm × {MOTOR_L}mm (6374)")
    print(f"Arms:    {ARM_LEN}mm × {ARM_W}mm × {ARM_H}mm")
    print(f"Layout:  3× motors @ 120°")
    print(f"Roller center: {ROLLER_CENTER_R}mm from axis")
    print()

    make_launch_tube()
    make_motor_mount()
    make_motor_arm()
    make_launch_roller()
    make_side_plate()
    make_flange_ring()

    print(f"\n✓ 6 个零件 → {OUTPUT_DIR}/")
    print(f"\n每种打印数量:")
    print(f"  launch_tube:    2（对开）")
    print(f"  motor_mount:    3（每电机 1 个）")
    print(f"  motor_arm:      3（每电机 1 根）")
    print(f"  launch_roller:  3（每电机 1 个）")
    print(f"  side_plate:     2（两端各 1）")
    print(f"  flange_ring:    2（两端各 1）")


if __name__ == "__main__":
    export_all()
