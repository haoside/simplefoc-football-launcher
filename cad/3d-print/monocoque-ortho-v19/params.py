"""
Football Launcher — v19 电机轴互相正交（X / Y / Z 各一个）

按 owner 最新澄清：
- "空间相错 90 度" = 3 个电机轴互相 90°（mutually perpendicular）
- "平行但不相交" = 3 根轴在不同位置（120° 错开），不交于一点
- 3 个电机在管周围 120° 分布
- 电机轴向：X（径向）、Y（切向）、Z（轴向）各一个

力学效果：
- Motor 1 (X 轴): 接触点正对轴心，速度为 0（不打滑不推球）
- Motor 2 (Y 轴): 接触点偏离轴心，can 转动给 +Z 速度（推球射出！）
- Motor 3 (Z 轴): can 转动给球侧向速度（自旋/弧线）
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# 参数
BALL_D = 220
BALL_R = BALL_D / 2

MOTOR_D = 63
MOTOR_CAN_R = MOTOR_D / 2
MOTOR_L = 74
MOTOR_BASE_D = 40
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

TUBE_IR = BALL_R + 3
TUBE_LEN = 160

CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R  # 140.5mm

TUBE_OR = TUBE_IR + 8
SHELL_OR = MOTOR_CENTER_R + MOTOR_CAN_R + 12

# 每个电机轴方向（3 互相正交）
MOTOR_AXES = [
    np.array([1.0, 0.0, 0.0]),  # Motor 1: X 方向（径向 0°）
    np.array([0.0, 1.0, 0.0]),  # Motor 2: Y 方向（切向）
    np.array([0.0, 0.0, 1.0]),  # Motor 3: Z 方向（轴向）
]

N_MOTORS = 3
SEGMENTS = 96
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEGMENTS)


def oriented_cylinder(h, r, axis):
    """生成轴向为指定方向（在 XY/Z 单位向量）的圆柱，中心在原点"""
    cyl = C(h, r)
    # 计算从默认 Z 轴到目标轴的旋转
    z_axis = np.array([0.0, 0.0, 1.0])
    target = np.array(axis, dtype=float)
    target = target / np.linalg.norm(target)
    if np.allclose(target, z_axis):
        return cyl
    if np.allclose(target, -z_axis):
        return cyl.rotate([180, 0, 0])
    # 计算旋转轴和角度
    rot_axis = np.cross(z_axis, target)
    rot_axis = rot_axis / np.linalg.norm(rot_axis)
    # Manifold3D 的 rotate 用轴角（axis * angle）作为 3 元素向量
    angle = math.acos(np.clip(np.dot(z_axis, target), -1, 1))
    axis_angle = (rot_axis * angle).tolist()
    return cyl.rotate(axis_angle)


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
# Part 1: 一体化壳体 + 3 电机正交支撑
# ============================================================
def make_monocoque_v19():
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)
    outer = C(TUBE_LEN, SHELL_OR) - C(TUBE_LEN + 0.4, SHELL_OR - 6)
    body = body + outer

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        cx = MOTOR_CENTER_R * math.cos(angle_rad)
        cy = MOTOR_CENTER_R * math.sin(angle_rad)
        cz = TUBE_LEN / 2
        axis = MOTOR_AXES[i]

        # 两块支撑板（在 can 两端，垂直于电机轴 = "90度关系"）
        for sign in [-1, 1]:
            # 支撑板中心偏移
            plate_center = np.array([cx, cy, cz]) + sign * axis * (MOTOR_L / 2 + 5)

            # 支撑板：垂直于电机轴，尺寸足够大
            plate_size_perp = [SHELL_OR - TUBE_OR + 5, MOTOR_D + 20, 8]
            plate = Manifold.cube(plate_size_perp, center=True)
            # 默认轴向是 X（最长边），需要旋转到沿 axis
            # axis 是单位向量，决定板的法向
            z_axis = np.array([0.0, 0.0, 1.0])
            target = axis / np.linalg.norm(axis)
            if not np.allclose(target, z_axis):
                rot_axis = np.cross(z_axis, target)
                if np.linalg.norm(rot_axis) > 1e-6:
                    rot_axis = rot_axis / np.linalg.norm(rot_axis)
                    angle = math.acos(np.clip(np.dot(z_axis, target), -1, 1))
                    plate = plate.rotate((rot_axis * angle).tolist())

            plate = plate.translate(plate_center.tolist())
            body = body + plate

            # 电机定子座安装孔
            mount_hole = C(10, MOTOR_BASE_D / 2 + 0.5)
            # 沿轴向拉伸
            mount_hole = oriented_cylinder(12, MOTOR_BASE_D / 2 + 0.5, axis)
            mount_hole = mount_hole.translate(plate_center.tolist())
            body = body - mount_hole

        # 管壁开槽（让 can 接触球）
        # 槽方向：根据电机轴方向调整
        slot = Manifold.cube((MOTOR_D + 6, MOTOR_L + 4, MOTOR_D + 2), center=True)
        # 简化：所有槽都按径向方向（方便 can 露出）
        slot = slot.rotate([0, 0, angle_deg])
        slot = slot.translate([(TUBE_IR + MOTOR_CENTER_R) / 2 * math.cos(angle_rad),
                               (TUBE_IR + MOTOR_CENTER_R) / 2 * math.sin(angle_rad),
                               cz])
        body = body - slot

    body = body - C(TUBE_LEN + 0.4, TUBE_IR)

    for z in [6, TUBE_LEN - 6]:
        ring = C(4, SHELL_OR) - C(5, SHELL_OR - 3)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "monocoque_v19.stl")


# ============================================================
# Part 2: 端板
# ============================================================
def make_side_plate_v19():
    plate_r = SHELL_OR
    h = 6
    plate = C(h, plate_r)
    plate = plate - C(h + 2, BALL_R + 3)
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 6) * math.cos(a)
        by = (plate_r - 6) * math.sin(a)
        hole = C(h + 2, 2.7, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole
    save(plate, "side_plate_v19.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v19: 3 电机轴互相正交（X / Y / Z）")
    print("=" * 50)
    print("- Motor 1: X 方向（径向 0° 位置）")
    print("- Motor 2: Y 方向（切向）")
    print("- Motor 3: Z 方向（轴向）")
    print("- 3 根轴在空间相错 120°，互相 90°，不相交")
    print()

    make_monocoque_v19()
    make_side_plate_v19()

    print(f"\n✓ 2 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()