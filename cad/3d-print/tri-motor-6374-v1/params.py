"""
Football Launcher — 3-Motor 120° Monocoque Design
参考图中橙色一体式壳体方案，放大适配 6374 + 标准5号足球

核心：三电机外转子直接接触球面，一体式打印壳体
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
BALL_R = BALL_D / 2                 # 110mm

# 6374 外转子电机（外壳旋转，直接接触球面）
MOTOR_OD = 63                        # 电机外壳外径 = 滚轮直径
MOTOR_OR = MOTOR_OD / 2              # 31.5mm
MOTOR_LEN = 74                       # 电机长度
MOTOR_SHAFT_D = 8
MOTOR_BOLT_D = 4
MOTOR_BOLT_SPACING = 31              # mm，安装孔间距
MOTOR_BOLT_PATTERN = 4               # 4孔 90°

# 滚轮接触几何
# 电机外壳直接接触球面 → 电机中心到球心距离 = BALL_R + MOTOR_OR
MOTOR_CENTER_R = BALL_R + MOTOR_OR   # 141.5mm

# 发射管
TUBE_OR = MOTOR_CENTER_R + MOTOR_LEN / 2 + 5  # 183mm（留间隙）
TUBE_IR = BALL_R + 3                        # 113mm（球通过）
TUBE_LEN = 120                              # 发射管长度

# 一体壳体
SHELL_WALL = 4                      # mm，壳体壁厚
SHELL_GAP = 0.3                     # mm，FDM 装配间隙

# M5 连接螺栓
BOLT_D = 5
BOLT_HEAD_D = 9

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
# Part 1: Monocoque Shell（一体式三电机壳体）
# ============================================================
def make_monocoque_shell():
    """
    一体式壳体（参考图中橙色件）：
    - 中心管夹箍
    - 3 个电机圆弧卡座 120° 均布
    - 桥接筋连接各卡座
    - 线槽出口
    - 对开设计（两半合体）
    """
    # ---- 中心管夹箍 ----
    clamp_or = TUBE_OR + 10
    clamp_ir = TUBE_IR
    clamp_h = TUBE_LEN

    # 主体管
    shell = R(clamp_h, clamp_or, clamp_ir)

    # ---- 3 个电机卡座 ----
    for i in range(3):
        angle_deg = i * 120
        rad = math.radians(angle_deg)

        # 电机卡座圆弧槽（半圆形，包裹电机外壳）
        cradle_r = MOTOR_OR + SHELL_GAP       # 卡槽内径
        cradle_wall = SHELL_WALL
        cradle_depth = MOTOR_LEN + 5          # 卡槽深度（比电机长）

        # 卡座凸台（从管壁向外延伸）
        boss_ext = cradle_depth + cradle_wall  # 向外延伸量
        boss_w = MOTOR_OD + cradle_wall * 2    # 卡座宽度

        # 圆弧卡座：圆柱减去内部电机空间
        boss_outer = C(boss_ext, MOTOR_OR + cradle_wall)
        boss_inner = C(boss_ext + 0.4, cradle_r)
        cradle = boss_outer - boss_inner

        # 定位到管壁外侧
        cradle = cradle.rotate([math.pi / 2, 0, 0])  # 轴沿 Y
        cradle = cradle.rotate([0, 0, rad])           # 绕 Z 旋转到 120° 位
        cradle = cradle.translate([
            (TUBE_OR + 2) * math.cos(rad),
            (TUBE_OR + 2) * math.sin(rad),
            clamp_h / 2
        ])
        shell = shell + cradle

        # ---- 电机固定螺丝孔（4 个，M4，从侧面拧入） ----
        bolt_r = MOTOR_BOLT_SPACING / 2
        for bi in range(MOTOR_BOLT_PATTERN):
            bolt_angle = math.radians(bi * 90)
            # 螺丝方向：从卡座外侧径向拧入
            bx = (TUBE_OR + cradle_depth + cradle_wall + 2) * math.cos(rad)
            by = (TUBE_OR + cradle_depth + cradle_wall + 2) * math.sin(rad)
            # 螺丝孔位置（在卡座面上）
            screw_hole = C(cradle_wall + 4, MOTOR_BOLT_D / 2 + 0.1)
            # 旋转到正确的角度位置
            screw_hole = screw_hole.rotate([0, 0, bolt_angle])
            screw_hole = screw_hole.translate([
                bolt_r * math.cos(rad + bolt_angle),
                bolt_r * math.sin(rad + bolt_angle),
                clamp_h / 2
            ])
            shell = shell - screw_hole

        # ---- 桥接筋（连接卡座到管体） ----
        # 两个三角形加强筋，卡座两侧
        for side in [-1, 1]:
            bridge_angle = rad + side * math.radians(30)
            bridge_len = TUBE_OR + 5
            bridge = B(8, bridge_len, clamp_h - 40)
            bridge = bridge.rotate([0, 0, bridge_angle])
            bridge = bridge.translate([
                (TUBE_OR / 2) * math.cos(bridge_angle),
                (TUBE_OR / 2) * math.sin(bridge_angle),
                clamp_h / 2
            ])
            shell = shell + bridge

        # ---- 线槽出口（卡座底部，走线用） ----
        wire_slot = B(MOTOR_OD, 10, 15)
        wire_slot = wire_slot.rotate([0, 0, rad])
        wire_slot = wire_slot.translate([
            (TUBE_OR + cradle_depth / 2) * math.cos(rad),
            (TUBE_OR + cradle_depth / 2) * math.sin(rad),
            10  # 靠近底部
        ])
        shell = shell - wire_slot

    # ---- 合体法兰面（对开螺栓孔） ----
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
        flange = C(3, clamp_or + 8) - C(4, clamp_ir)
        flange = flange.translate([0, 0, z - 1.5])
        shell = shell + flange

    save(shell, "monocoque_shell.stl")


# ============================================================
# Part 2: Motor Clamp Cap（电机卡座盖板）
# ============================================================
def make_motor_clamp_cap():
    """
    电机卡座盖板：扣在电机上方，锁紧电机
    - 弧形，匹配电机外壳曲率
    - 2 个 M4 螺丝孔固定到壳体
    """
    cap_r = MOTOR_OR + SHELL_GAP + SHELL_WALL  # 盖板内径
    cap_or = cap_r + 3                          # 外径
    cap_w = MOTOR_OD + 10                       # 宽度
    cap_h = 10                                  # 厚度

    # 盖板主体（弧形，120° 扇区）
    cap = C(cap_h, cap_or) - C(cap_h + 0.4, cap_r)

    # 切成 120° 扇区
    cut1 = B(cap_or * 3, cap_or * 2, cap_h + 2)
    cut1 = cut1.rotate([0, 0, 30])
    cut1 = cut1.translate([0, -cap_or, 0])
    cap = cap - cut1

    cut2 = B(cap_or * 3, cap_or * 2, cap_h + 2)
    cut2 = cut2.rotate([0, 0, -30])
    cut2 = cut2.translate([0, cap_or, 0])
    cap = cap - cut2

    # M4 安装孔（2 个，对称）
    for y_off in [-cap_w / 2 + 5, cap_w / 2 - 5]:
        hole = C(cap_h + 2, MOTOR_BOLT_D / 2 + 0.1)
        hole = hole.translate([0, y_off, 0])
        cap = cap - hole

    save(cap, "motor_clamp_cap.stl")


# ============================================================
# Part 3: Side Plate（侧板）
# ============================================================
def make_side_plate():
    """
    侧板：端面结构加强
    - 环形板 + 球通道孔
    - 3 组电机通过缺口
    - 螺栓孔
    """
    plate_r = TUBE_OR + 10
    h = 5

    plate = C(h, plate_r)
    plate = plate - C(h + 2, TUBE_IR)  # 球通道

    # 3 组电机卡座缺口
    for i in range(3):
        angle = math.radians(i * 120)
        cx = MOTOR_CENTER_R * math.cos(angle)
        cy = MOTOR_CENTER_R * math.sin(angle)
        notch = B(MOTOR_OD + 12, MOTOR_OD + 12, h + 2)
        notch = notch.rotate([0, 0, angle])
        notch = notch.translate([cx, cy, 0])
        plate = plate - notch

    # 螺栓孔（8 个）
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 5) * math.cos(a)
        by = (plate_r - 5) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 减重孔（3 个，臂之间）
    for i in range(3):
        angle = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 5) * math.cos(angle)
        py = (plate_r / 2 + 5) * math.sin(angle)
        light = C(h + 2, 12)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate.stl")


# ============================================================
# Part 4: Flange Ring（法兰连接环）
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

    # 定位销
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
    print("Football Launcher — 3-Motor 120° Monocoque")
    print("=" * 50)
    print(f"Ball:      {BALL_D}mm")
    print(f"Tube:      {TUBE_IR*2}mm ID / {TUBE_OR*2}mm OD")
    print(f"Motor:     6374 × 3 @ 120° (外转子直触球面)")
    print(f"Motor R:   {MOTOR_CENTER_R}mm from axis")
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
