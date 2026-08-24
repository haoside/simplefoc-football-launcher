"""
Football Launcher — v21: 平板蜘蛛笼体 (严格复现参考结构)

参考: YouTube WQlTYPqzlNI — 平板笼体, 三电机轴线平行于中心孔,
电机壳内切于中心孔边缘, 球从孔中挤过由三个转子壳摩擦加速。

几何核心:
  三个转子圆 (φ79, 含PU套) 圆心分布在 R 上, 120° 均布
  转子内包络半径 = R - 39.5 = 球道孔半径
  球 φ220 挤过孔 φ200 → 每触点预紧 10mm

零件:
  spider_plate_v21.stl   主平板笼体 ×1
  motor_retainer_v21.stl 电机压环 ×3 (螺丝锁板固定电机)
"""
import math
import os
import struct

import numpy as np
from manifold3d import Manifold

# ---- 球/转子 ----
BALL_R = 110.0
PRELOAD = 10.0                    # 单触点压紧 (直径方向 220 vs 200)
ROLL_R = 39.5                     # φ63壳 + 8mm PU = φ79
BORE_R = BALL_R - PRELOAD         # 100 中心孔半径
MOTOR_C_R = BORE_R + ROLL_R       # 139.5 电机圆心分布半径

# ---- 6374 电机 ----
MOTOR_D = 63.0
MOTOR_L = 74.0

# ---- 平板 ----
PLATE_T = 26.0                    # 板厚 (电机轴向嵌入 ~1/3, 兼顾刚度和外观)
SEAT_ARC = 200.0                  # 电机座孔包角 (轴向插入, C形开口朝外)
SEAT_CLEAR = 0.5                  # 插入间隙 (φ63.5 + PU 套后按实物修配)
SEAT_R = MOTOR_D / 2 + SEAT_CLEAR # 32.0
RETAIN_T = 6.0                    # 压环厚
RETAIN_SCREW = 3.2                # M3
RETAIN_N = 3

# ---- 外轮廓 ----
LOBE_R = SEAT_R + 14.0            # 电机凸台外圆
TAB_R = 5.0                       # 角部安装孔位置半径偏移
TAB_HOLE = 5.5                    # M5
N_MOTORS = 3
SEG = 96
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stls")
os.makedirs(OUT, exist_ok=True)


def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEG)


def polar(m, r, ang_deg, z=0.0):
    a = math.radians(ang_deg)
    return m.translate([r * math.cos(a), r * math.sin(a), z])


def save(body, name):
    mesh = body.to_mesh()
    v = np.asarray(mesh.vert_properties, dtype=np.float32)[:, :3]
    t = np.asarray(mesh.tri_verts, dtype=np.int32)
    with open(os.path.join(OUT, name), "wb") as f:
        _stl(f, v, t)
    print(f"  {name}: {len(t)} tris")


def _stl(fh, verts, tris):
    fh.write(b"\x00" * 80)
    fh.write(struct.pack("<I", len(tris)))
    for tri in tris:
        p0, p1, p2 = verts[tri[0]], verts[tri[1]], verts[tri[2]]
        n = np.cross(p1 - p0, p2 - p0)
        ln = np.linalg.norm(n)
        n = n / ln if ln > 1e-12 else np.array([0.0, 0.0, 1.0])
        fh.write(struct.pack("<3f", *n))
        for p in (p0, p1, p2):
            fh.write(struct.pack("<3f", *p))
        fh.write(struct.pack("<H", 0))


def lobe_plate_outline(thickness):
    """圆角三叶外轮廓: 三叶凸台圆 + 中央圆的凸包近似 (并集平滑)"""
    plate = C(thickness, BORE_R + 26)                    # 中央盘
    for i in range(N_MOTORS):
        plate = plate + polar(C(thickness, LOBE_R), MOTOR_C_R, 90 + i * 120)
    # 叶间连接臂
    for i in range(N_MOTORS):
        arm = Manifold.cube([MOTOR_C_R + LOBE_R * 0.3, 30, thickness], False)
        arm = arm.translate([0, -15, 0])
        plate = plate + polar(arm, 0, 90 + 60 + i * 120)
    return plate


def spider_plate():
    plate = lobe_plate_outline(PLATE_T)

    # 中央球道孔
    plate = plate - C(PLATE_T + 4, BORE_R)

    # 三个电机座: 轴向通孔 C形 (开口朝外, 200° 包角)
    for i in range(N_MOTORS):
        ang = 90 + i * 120
        seat = C(PLATE_T + 4, SEAT_R)
        # 开口楔 (朝外 160° 扇区切除)
        wedge = Manifold.cube([200, 200, PLATE_T + 8], True)
        wedge = wedge.translate([100, 0, 0])             # +Y 半平面 → 旋转对准开口
        wedge = wedge.rotate([0, 0, -(90 - SEAT_ARC / 2)])
        seat = seat - wedge
        plate = plate - polar(seat, MOTOR_C_R, ang, -2)

        # 压环螺丝沉孔 (座两侧, 沿切向)
        for s in (-1, 1):
            hole_ang = ang + s * (SEAT_ARC / 2 - 18)
            hp = C(PLATE_T + 6, RETAIN_SCREW / 2)
            a = math.radians(hole_ang)
            plate = plate - hp.translate([
                (MOTOR_C_R + SEAT_R + 4) * math.cos(a) - SEAT_R * 0.0,
                (MOTOR_C_R + SEAT_R + 4) * math.sin(a),
                -2,
            ])

    # 角部 M5 安装孔 (三叶外缘, 复现参考图可见孔)
    for i in range(N_MOTORS):
        ang = 90 + i * 120 + 60          # 叶之间
        plate = plate - polar(C(PLATE_T + 4, TAB_HOLE / 2),
                              MOTOR_C_R + LOBE_R - 6, ang)
    return plate


def motor_retainer():
    """压环: 环形, 3×M3 沉孔, 盖住电机端面锁入板面"""
    ring = C(RETAIN_T, SEAT_R + 8) - C(RETAIN_T + 4, SEAT_R - 2)
    for i in range(RETAIN_N):
        a = math.radians(i * 360 / RETAIN_N + 60)
        ring = ring - C(RETAIN_T + 4, RETAIN_SCREW / 2).translate(
            [(SEAT_R + 4) * math.cos(a), (SEAT_R + 4) * math.sin(a), -2])
    return ring


if __name__ == "__main__":
    print("generating v21 flat-spider plate (faithful to reference) ...")
    save(spider_plate(), "spider_plate_v21.stl")
    save(motor_retainer(), "motor_retainer_v21.stl")
    print("done ->", OUT)
