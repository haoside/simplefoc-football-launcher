"""
Football Launcher 3D Printed Parts — 3 Motor 120° Layout
manifold3d 布尔运算，可直接打印 STL
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 参数
# ============================================================
BALL_DIA = 220
CHANNEL_ID = BALL_DIA + 5
MOTOR_DIA = 63
MOTOR_SHAFT = 8
MOTOR_PCD = 30
MOTOR_HOLE = 4
WALL = 4
FRAME_W = 80
ROLLER_DIA = 60
ROLLER_W = 20
ROLLER_BORE = 8
ROLLER_GROOVE = 3
ARM_LEN = 120
ARM_W = 25
ARM_H = 8
BOLT_DIA = 5
N_MOTORS = 3
SEGMENTS = 64

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


# ============================================================
# 工具
# ============================================================
def cyl(h, r_bot, r_top=None, n=SEGMENTS):
    """圆柱体，中心在底面"""
    if r_top is None:
        r_top = r_bot
    return Manifold.cylinder(h, r_bot, r_top, n)

def ring(h, r_out, r_in, n=SEGMENTS):
    """空心圆柱"""
    return cyl(h, r_out, n=n) - cyl(h + 0.2, r_in, n=n)

def box(w, d, h):
    """长方体，中心"""
    return Manifold.cube((w, d, h), center=True)

def save_stl(body, filename):
    """保存 STL"""
    path = os.path.join(OUTPUT_DIR, filename)
    m = body.to_mesh()
    verts = np.array(m.vert_properties)[:, :3]
    tris = np.array(m.tri_verts)

    with open(path, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', len(tris)))
        for tri in tris:
            v0, v1, v2 = verts[tri[0]], verts[tri[1]], verts[tri[2]]
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            norm = np.linalg.norm(normal)
            if norm > 0:
                normal = normal / norm
            f.write(struct.pack('<3f', *normal))
            f.write(struct.pack('<3f', *v0))
            f.write(struct.pack('<3f', *v1))
            f.write(struct.pack('<3f', *v2))
            f.write(struct.pack('<H', 0))

    print(f"  ✓ {filename} — {len(tris)} faces, {os.path.getsize(path)//1024}KB")


# ============================================================
# Part 1: Motor Mount（电机安装座）
# ============================================================
def make_motor_mount():
    outer_r = MOTOR_DIA / 2 + WALL * 2
    inner_r = MOTOR_DIA / 2 - 0.3
    h = 25
    flange_size = MOTOR_DIA + 30

    # 主体圆柱
    body = cyl(h, outer_r)

    # 中心轴孔
    body = body - cyl(h + 2, MOTOR_SHAFT / 2 + 0.5)

    # 法兰板
    flange = box(flange_size, flange_size + 20, WALL)
    flange = flange.translate([0, 0, h / 2 + WALL / 2])
    body = body + flange

    # M4 电机安装孔（4 个 90°）
    for i in range(4):
        angle = math.radians(i * 90)
        hx = (MOTOR_PCD / 2) * math.cos(angle)
        hy = (MOTOR_PCD / 2) * math.sin(angle)
        hole = cyl(WALL + 4, MOTOR_HOLE / 2 + 0.2)
        hole = hole.translate([hx, hy, h / 2])
        body = body - hole

    # M5 管夹紧固孔
    clamp = cyl(outer_r * 2 + 4, BOLT_DIA / 2 + 0.2)
    clamp = clamp.rotate([math.pi / 2, 0, 0])
    clamp = clamp.translate([0, 0, h / 2])
    body = body - clamp

    save_stl(body, "motor_mount.stl")


# ============================================================
# Part 2: Frame Main（主框架）
# ============================================================
def make_frame():
    id_r = CHANNEL_ID / 2
    od_r = id_r + WALL
    hub_h = 30
    hub_w = MOTOR_DIA + 20
    hub_d = WALL * 3

    # 主管
    body = ring(FRAME_W, od_r, id_r)

    # 3 个安装凸台
    for i in range(N_MOTORS):
        angle_deg = i * 120
        rad = math.radians(angle_deg)
        cx = (od_r + hub_h / 2) * math.cos(rad)
        cy = (od_r + hub_h / 2) * math.sin(rad)

        hub = box(hub_w, hub_d, hub_h)
        hub = hub.translate([cx, cy, FRAME_W / 2])
        hub = hub.rotate([0, 0, rad])
        body = body + hub

        # M5 连接孔
        for yi in [-8, 8]:
            nx = math.cos(rad + math.pi / 2)
            ny = math.sin(rad + math.pi / 2)
            px = cx + yi * nx
            py = cy + yi * ny
            hole = cyl(hub_d + 4, BOLT_DIA / 2 + 0.2)
            hole = hole.translate([px, py, FRAME_W / 2])
            body = body - hole

    # 加固环
    ring_body = cyl(3, od_r + 3) - cyl(4, od_r - 1)
    ring_body = ring_body.translate([0, 0, FRAME_W / 2 - 1.5])
    body = body + ring_body

    save_stl(body, "frame_main.stl")


# ============================================================
# Part 3: Roller Wheel（滚轮）
# ============================================================
def make_roller_wheel():
    r_out = ROLLER_DIA / 2
    r_in = ROLLER_BORE / 2
    r_groove = r_out - ROLLER_GROOVE

    # 主体
    body = cyl(ROLLER_W, r_out) - cyl(ROLLER_W + 2, r_in)

    # V 槽
    groove = cyl(ROLLER_W - 6, r_out + 0.5) - cyl(ROLLER_W - 4, r_groove)
    groove = groove.translate([0, 0, 3])
    body = body - groove

    # 键槽
    keyway = box(3, 2, ROLLER_W + 2)
    keyway = keyway.translate([0, r_in - 1, 0])
    body = body - keyway

    # 顶丝孔
    screw = cyl(r_out + 2, 1.6)
    screw = screw.rotate([math.pi / 2, 0, 0])
    body = body - screw

    # 减重孔（4 个）
    for i in range(4):
        angle = math.radians(i * 90)
        hx = (r_out / 2 + 2) * math.cos(angle)
        hy = (r_out / 2 + 2) * math.sin(angle)
        light = cyl(ROLLER_W - 8, 4)
        light = light.translate([hx, hy, 4])
        body = body - light

    save_stl(body, "roller_wheel.stl")


# ============================================================
# Part 4: Structural Arm（结构臂）
# ============================================================
def make_structural_arm():
    arm = box(ARM_LEN, ARM_W, ARM_H)

    # 两端安装孔（M5）
    for x_off in [-ARM_LEN / 2 + 12, ARM_LEN / 2 - 12]:
        for y_off in [-ARM_W / 4, ARM_W / 4]:
            hole = cyl(ARM_H + 4, BOLT_DIA / 2 + 0.2)
            hole = hole.translate([x_off, y_off, 0])
            arm = arm - hole

    # 减重凹槽
    recess = box(ARM_LEN - 30, ARM_W - 10, ARM_H - 2)
    arm = arm - recess

    # 端部倒角
    for x_off in [-ARM_LEN / 2, ARM_LEN / 2]:
        for y_off in [-ARM_W / 2, ARM_W / 2]:
            chamfer = cyl(ARM_H + 2, ARM_H / 3)
            chamfer = chamfer.translate([x_off, y_off, 0])
            arm = arm - chamfer

    save_stl(arm, "structural_arm.stl")


# ============================================================
# Part 5: Connector Flange（连接法兰）
# ============================================================
def make_connector_flange():
    id_r = CHANNEL_ID / 2
    od_r = id_r + WALL
    flange_r = od_r + 12
    h = 8

    body = cyl(h, flange_r) - cyl(h + 2, id_r)

    # M5 螺栓孔（8 个）
    bolt_r = od_r + 6
    for i in range(8):
        angle = math.radians(i * 45)
        bx = bolt_r * math.cos(angle)
        by = bolt_r * math.sin(angle)
        hole = cyl(h + 4, BOLT_DIA / 2 + 0.2)
        hole = hole.translate([bx, by, 0])
        body = body - hole

    # 定位销孔
    for angle_deg in [60, 300]:
        rad = math.radians(angle_deg)
        px = (od_r + 3) * math.cos(rad)
        py = (od_r + 3) * math.sin(rad)
        pin = cyl(h + 2, 2.1)
        pin = pin.translate([px, py, 0])
        body = body - pin

    save_stl(body, "connector_flange.stl")


# ============================================================
# Part 6: Motor Side Plate（电机侧盖板）
# ============================================================
def make_motor_side_plate():
    r = CHANNEL_ID / 2 + WALL + 15
    h = 5

    body = cyl(h, r)

    # 中心球通道孔
    body = body - cyl(h + 2, CHANNEL_ID / 2 - 5)

    # 3 个电机位通过孔
    motor_r = CHANNEL_ID / 2 + WALL - 5
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        mx = motor_r * math.cos(angle)
        my = motor_r * math.sin(angle)
        hole = cyl(h + 2, MOTOR_DIA / 2 + 3)
        hole = hole.translate([mx, my, 0])
        body = body - hole

    # 安装螺栓孔（3 组 × 2）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120 + 60)
        for d in [-8, 8]:
            px = (r - 8) * math.cos(angle) + d * math.cos(angle + math.pi / 2)
            py = (r - 8) * math.sin(angle) + d * math.sin(angle + math.pi / 2)
            hole = cyl(h + 2, 2.2)
            hole = hole.translate([px, py, 0])
            body = body - hole

    # 减重孔
    for i in range(3):
        angle = math.radians(i * 120 + 30)
        px = r * 0.55 * math.cos(angle)
        py = r * 0.55 * math.sin(angle)
        light = cyl(h + 2, 12)
        light = light.translate([px, py, 0])
        body = body - light

    save_stl(body, "motor_side_plate.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Football Launcher — 3 Motor 120° (manifold3d CSG)")
    print(f"通道: {CHANNEL_ID}mm | 电机: {MOTOR_DIA}mm × 3\n")

    make_motor_mount()
    make_frame()
    make_roller_wheel()
    make_structural_arm()
    make_connector_flange()
    make_motor_side_plate()

    print(f"\n✓ 6 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()
