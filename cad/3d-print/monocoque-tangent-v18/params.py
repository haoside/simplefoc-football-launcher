"""
Football Launcher — v18 切向电机轴（正确几何）

关键修正：
- 电机轴 = 切向（垂直于径向，也垂直于管轴 Z）
- "恰恰有 90 度关系" + "旋转与径向相切" + "电机轴不平行于管"
- can 绕切向轴旋转 → 接触点速度在 +Z → 球沿管射出
- 3 电机 120° 同向 → 摩擦驱动发射；差速 → 弧线球
- 电机两端定子（出线侧）固定到加强筋（90° 于电机轴）
- 一体化壳体
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

# 6374 外转子电机（can 当滚轮）
MOTOR_D = 63
MOTOR_CAN_R = MOTOR_D / 2       # 31.5mm 滚轮半径
MOTOR_L = 74                    # can 长度（沿切向轴）
MOTOR_SHAFT_D = 8
MOTOR_BASE_D = 40               # 定子基座（出线侧）
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管（球通道）
TUBE_IR = BALL_R + 3            # 113mm
TUBE_LEN = 160                  # 管长

# 电机位置（can 接触球，1mm 压紧）
CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R  # 140.5mm

# 一体化壳体
TUBE_OR = TUBE_IR + 8           # 管外径 121mm
SHELL_OR = MOTOR_CENTER_R + MOTOR_CAN_R + 12  # 184mm

# 电机支撑板（在 can 切向两端，垂直于切向轴 = 90°关系）
SUPPORT_THICK = 10              # 支撑板厚
SUPPORT_GAP = MOTOR_L + 2 * SUPPORT_THICK  # 两支撑板间距

# 管壁开槽（can 接触球）
SLOT_LEN = MOTOR_L + 4          # 沿切向方向的槽长
SLOT_DEPTH_W = MOTOR_D + 6      # 径向方向的槽宽

N_MOTORS = 3
SEGMENTS = 96
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


# ============================================================
# 工具
# ============================================================
def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEGMENTS)


def tangent_cylinder(h, r, angle_deg):
    """生成轴向沿切向（angle 处切线方向）的圆柱，中心在原点"""
    cyl = C(h, r)
    cyl = cyl.rotate([90, 0, 0])          # Z 轴 → Y 轴
    cyl = cyl.rotate([0, 0, angle_deg])   # Y → 切向 (angle 处)
    return cyl


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
# Part 1: Monocoque Shell（一体化壳体 + 切向电机支撑）
# ============================================================
def make_monocoque_v18():
    """
    一体化壳体：
    - 中心管段（球通道）
    - 3 组切向电机支撑（每组 2 块支撑板夹住电机两端）
    - 管壁开槽（can 切向接触球）
    - 出线侧固定位
    """
    # 中心管
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 外环壳
    outer = C(TUBE_LEN, SHELL_OR) - C(TUBE_LEN + 0.4, SHELL_OR - 6)
    body = body + outer

    for i in range(N_MOTORS):
        angle_deg = i * 120
        angle_rad = math.radians(angle_deg)
        # 电机中心（在管周围 120°）
        cx = MOTOR_CENTER_R * math.cos(angle_rad)
        cy = MOTOR_CENTER_R * math.sin(angle_rad)
        cz = TUBE_LEN / 2

        # 切向单位向量
        tx = -math.sin(angle_rad)
        ty = math.cos(angle_rad)

        # ===== 两块电机支撑板（在 can 切向两端，垂直于切向轴）=====
        for sign in [-1, 1]:
            # 支撑板中心：电机中心 ± 切向方向 SUPPORT_GAP/2
            sx = cx + sign * tx * (SUPPORT_GAP / 2)
            sy = cy + sign * ty * (SUPPORT_GAP / 2)

            # 支撑板：径向延伸的板（连接管壁到外壳）
            # 板平面垂直于切向轴（在径向-Z 平面内）
            plate = Manifold.cube((SHELL_OR - TUBE_OR + 5, SUPPORT_THICK, MOTOR_D + 20), center=True)
            # 板长边沿径向，厚度沿切向，高度沿 Z
            plate = plate.rotate([0, 0, angle_deg])  # 径向对齐
            plate = plate.translate([
                (TUBE_OR + SHELL_OR) / 2 * math.cos(angle_rad) + sign * tx * (SUPPORT_GAP / 2),
                (TUBE_OR + SHELL_OR) / 2 * math.sin(angle_rad) + sign * ty * (SUPPORT_GAP / 2),
                cz
            ])

            # 电机定子座安装孔（在板上，电机轴位置）
            mount_hole = tangent_cylinder(SUPPORT_THICK + 2, MOTOR_BASE_D / 2 + 0.5, angle_deg)
            mount_hole = mount_hole.translate([sx, sy, cz])
            plate = plate - mount_hole

            body = body + plate

        # ===== 管壁开槽（can 切向露出接触球）=====
        # 槽沿切向方向，让 can 圆柱面接触球
        slot = Manifold.cube((SLOT_DEPTH_W, SLOT_LEN, MOTOR_D + 2), center=True)
        # 旋转：长边沿切向
        slot = slot.rotate([0, 0, angle_deg])
        slot = slot.translate([(TUBE_IR + MOTOR_CENTER_R) / 2 * math.cos(angle_rad),
                               (TUBE_IR + MOTOR_CENTER_R) / 2 * math.sin(angle_rad),
                               cz])
        body = body - slot

    # 重新挖球通道
    body = body - C(TUBE_LEN + 0.4, TUBE_IR)

    # 两端加固环
    for z in [6, TUBE_LEN - 6]:
        ring = C(4, SHELL_OR) - C(5, SHELL_OR - 3)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "monocoque_v18.stl")


# ============================================================
# Part 2: Side Plate
# ============================================================
def make_side_plate_v18():
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
    save(plate, "side_plate_v18.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v18: 切向电机轴（正确几何）")
    print("=" * 50)
    print("- 电机轴 = 切向（垂直径向 + 垂直管轴）")
    print("- can 绕切向轴转 → 接触点速度 +Z → 球射出")
    print("- 3 电机 120° 同向 → 摩擦驱动；差速 → 弧线")
    print("- 电机两端支撑板（90° 于切向轴）")
    print(f"- 电机中心 R = {MOTOR_CENTER_R:.1f}mm")
    print(f"- 管: IR {TUBE_IR} / OR {TUBE_OR} / L {TUBE_LEN}")
    print(f"- 壳体外径 = {SHELL_OR:.0f}mm")
    print()

    make_monocoque_v18()
    make_side_plate_v18()

    print(f"\n✓ 2 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()