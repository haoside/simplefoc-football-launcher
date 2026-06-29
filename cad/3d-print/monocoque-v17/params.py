"""
Football Launcher — v17 推倒重做（按 owner 全部要求）

设计要点：
1. 一体化壳体（monocoque）
2. 电机轴平行于管（Z），can 外转子中间段当滚轮
3. 电机两端（静止定子/出线侧）固定到加强筋
4. 加强筋与电机轴成 90°（垂直端支撑）= "90度关系"
5. 出线侧从加强筋引出
6. 气压主线（电机 = 控旋 / 控球）
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
MOTOR_L = 74                    # can 长度
MOTOR_SHAFT_D = 8               # 轴径
MOTOR_BASE_D = 40               # 定子基座直径（出线侧）
MOTOR_BASE_L = 10               # 定子基座长度
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管（球通道）
TUBE_IR = BALL_R + 3            # 113mm
TUBE_LEN = MOTOR_L + 2 * 20     # 114mm（电机长 + 两端加强筋空间）

# 电机位置（can 接触球，1mm 压紧）
CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R  # 140.5mm

# 一体化壳体
TUBE_OR = MOTOR_CENTER_R - MOTOR_CAN_R - 3  # 管外壁（can 内侧）
if TUBE_OR < TUBE_IR + 6:
    TUBE_OR = TUBE_IR + 8
SHELL_OR = MOTOR_CENTER_R + MOTOR_CAN_R + 10  # 壳体外径
SHELL_WALL = 6

# 加强筋（端部，90° 于电机轴）
RIB_THICK = 18                  # 加强筋厚度
RIB_OR = SHELL_OR               # 加强筋外径
MOTOR_MOUNT_BORE = MOTOR_BASE_D + 1  # 电机基座安装孔

# 管壁开槽（can 露出接触球）
SLOT_W = MOTOR_D + 4

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
# Part 1: Monocoque Shell（一体化壳体 + 两端加强筋）
# ============================================================
def make_monocoque_v17():
    """
    一体化壳体：
    - 中心管段（球通道）
    - 外环壳
    - 两端加强筋（90° 于电机轴，捕获电机两端）
    - 管壁开槽（can 接触球）
    - 出线口（加强筋上开槽）
    """
    # 中心管
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 外环壳（仅在 can 区域外侧，连接两端加强筋）
    outer = C(TUBE_LEN, SHELL_OR) - C(TUBE_LEN + 0.4, SHELL_OR - SHELL_WALL)
    body = body + outer

    # ===== 两端加强筋（90° 端盘）=====
    for z_pos, end_name in [(RIB_THICK / 2, 'bottom'), (TUBE_LEN - RIB_THICK / 2, 'top')]:
        rib = C(RIB_THICK, RIB_OR) - C(RIB_THICK + 0.4, TUBE_IR)
        rib = rib.translate([0, 0, z_pos])

        # 在加强筋上为每个电机开安装座（电机两端定子座固定于此）
        for i in range(N_MOTORS):
            angle = math.radians(i * 120)
            cx = MOTOR_CENTER_R * math.cos(angle)
            cy = MOTOR_CENTER_R * math.sin(angle)

            # 电机定子座安装孔（沉孔）
            mount = C(RIB_THICK + 2, MOTOR_BASE_D / 2 + 0.5)
            mount = mount.translate([cx, cy, z_pos])
            rib = rib - mount

            # 电机轴孔/定子固定螺栓（4×M4）
            for j in range(4):
                ja = math.radians(j * 90)
                bx = cx + (MOTOR_HOLE_PCD / 2) * math.cos(ja)
                by = cy + (MOTOR_HOLE_PCD / 2) * math.sin(ja)
                bolt = C(RIB_THICK + 2, MOTOR_HOLE_D / 2 + 0.1, 16)
                bolt = bolt.translate([bx, by, z_pos])
                rib = rib - bolt

            # 出线口（仅底部加强筋，朝外开槽引线）
            if end_name == 'bottom':
                wire_slot = Manifold.cube((SHELL_OR - MOTOR_CENTER_R + 20, 12, RIB_THICK + 2), center=True)
                wire_slot = wire_slot.rotate([0, 0, i * 120])
                wire_slot = wire_slot.translate([(MOTOR_CENTER_R + SHELL_OR) / 2 * math.cos(angle),
                                                 (MOTOR_CENTER_R + SHELL_OR) / 2 * math.sin(angle),
                                                 z_pos])
                rib = rib - wire_slot

        body = body + rib

    # ===== can 区域：开放空间（电机 can 在两加强筋之间转动）=====
    # can 接触球的开槽（管壁）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        slot = Manifold.cube((MOTOR_CAN_R * 2 + 12, SLOT_W, MOTOR_L - 4), center=True)
        slot = slot.rotate([0, 0, i * 120])
        slot = slot.translate([(TUBE_IR + MOTOR_CENTER_R) / 2 * math.cos(angle),
                               (TUBE_IR + MOTOR_CENTER_R) / 2 * math.sin(angle),
                               TUBE_LEN / 2])
        body = body - slot

    # ===== 连接筋（外环 → 管，仅在加强筋之间的中段，避开 can）=====
    for i in range(N_MOTORS):
        a_mid = math.radians(i * 120 + 60)  # 在两电机之间
        web = Manifold.cube((SHELL_OR - TUBE_OR, 10, TUBE_LEN), center=True)
        web = web.rotate([0, 0, math.degrees(a_mid)])
        web = web.translate([(TUBE_OR + SHELL_OR) / 2 * math.cos(a_mid),
                             (TUBE_OR + SHELL_OR) / 2 * math.sin(a_mid), 0])
        body = body + web

    # 重新挖球通道
    body = body - C(TUBE_LEN + 0.4, TUBE_IR)

    save(body, "monocoque_v17.stl")


# ============================================================
# Part 2: Side Plate（端板 — 接气压端/出球端）
# ============================================================
def make_side_plate_v17():
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

    save(plate, "side_plate_v17.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v17: 推倒重做 — 两端加强筋支撑 + can 滚轮")
    print("=" * 50)
    print("- 一体化壳体（monocoque）")
    print("- 电机轴平行管（Z），两端固定到加强筋")
    print("- 加强筋 90° 于电机轴（垂直端支撑）")
    print("- can 外转子中间段当滚轮，接触球")
    print("- 出线侧从底部加强筋引出")
    print(f"- 电机中心 R = {MOTOR_CENTER_R:.1f}mm")
    print(f"- 管: IR {TUBE_IR} / OR {TUBE_OR:.0f} / L {TUBE_LEN:.0f}")
    print(f"- 壳体外径 = {SHELL_OR:.0f}mm")
    print(f"- 加强筋厚 = {RIB_THICK}mm")
    print()

    make_monocoque_v17()
    make_side_plate_v17()

    print(f"\n✓ 2 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()