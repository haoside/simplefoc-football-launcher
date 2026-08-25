"""
Football Launcher — v24: 一体化径向直驱笼体 + 电机固定细节

参考特写确认的固定方式:
  - 座为杯状: 外端面封闭, 中央过轴孔 (轴朝外穿出)
  - 外端面上 N 颗螺丝围绕轴孔分布, 轴向拧入电机定子安装法兰 → 定子被夹紧
  - 转子壳(银)朝孔侧悬伸, 凸入发射孔压球
  - 座与孔环一体成型 (v23 拓扑保留)

用法: python3 gen_v24.py
"""
import math
import os
import struct

import numpy as np
from manifold3d import Manifold, OpType

# ---- 球 / 孔 ----
BALL_R = 110.0
BORE_R = 100.0
PRELOAD = 6.0

# ---- 6374 ----
MOTOR_D = 63.0
MOTOR_L = 74.0
ROLL_R = 39.5                  # 壳+PU
R_C = BORE_R - PRELOAD + ROLL_R   # 133.5
SHAFT_D = 8.0

# ---- 电机定子固定 (外端面) ----
FIX_N = 4                      # 6374 定子法兰 4×M3 (实物核对后可改 3)
FIX_PCD = 30.0                 # 法兰螺丝分布直径 (待卡尺核对)
FIX_SCREW = 3.2                # M3 过孔
ENDWALL_T = 7.0                # 外端面厚
SHAFT_HOLE = SHAFT_D + 0.7     # 过轴间隙孔

# ---- 座 ----
SEAT_IR = MOTOR_D / 2 + 0.5    # 32.0 内腔贴定子/转子
SEAT_WALL = 8.0
SEAT_ARC = 160.0
SEAT_LEN = MOTOR_L + ENDWALL_T # 81 杯全长 (含外端面)

# ---- 孔环 ----
RING_LEN = 56.0
RING_WALL = 9.0

# ---- 肋 ----
RIB_T = 14.0
RIB_W = 18.0

SEG = 96
N = 3
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stls")
os.makedirs(OUT, exist_ok=True)


def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEG)


def rot_x(m, d): return m.rotate([d, 0, 0])
def rot_y(m, d): return m.rotate([0, d, 0])
def rot_z(m, d): return m.rotate([0, 0, d])


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


def seat_cup():
    """杯状电机座 (局部: 电机轴沿 +X, 朝外=+X).
    外端面封闭: 过轴孔 + N×固定螺丝孔.
    内侧开口朝 -X (孔侧), 转子壳由此凸入孔."""
    # 弧形筒身
    outer = C(SEAT_LEN, SEAT_IR + SEAT_WALL)
    inner = C(SEAT_LEN + 4, SEAT_IR)
    ring = outer - inner
    w1 = Manifold.cube([300, 300, SEAT_LEN + 8], True).translate([-150, 0, 0])
    w2 = rot_z(Manifold.cube([300, 300, SEAT_LEN + 8], True).translate([0, -150, 0]),
               -(180 - SEAT_ARC) / 2)
    w3 = rot_z(Manifold.cube([300, 300, SEAT_LEN + 8], True).translate([0, 150, 0]),
               (180 - SEAT_ARC) / 2)
    cup = ring - w1 - w2 - w3
    cup = rot_y(cup, 90)                       # 弧轴沿 X

    # 外端面: 实心圆板 (与弧筒外径同径), 位于 +X 端
    wall = C(ENDWALL_T, SEAT_IR + SEAT_WALL)
    wall = wall.translate([SEAT_LEN / 2 - ENDWALL_T / 2, 0, 0])
    cup = cup + wall

    # 过轴孔 (中央, 轴朝外穿出)
    cup = cup - C(ENDWALL_T + 4, SHAFT_HOLE / 2).translate([SEAT_LEN / 2, 0, 0])

    # N×定子固定螺丝孔: 围绕轴孔, 轴向贯穿外端面 (拧入电机定子法兰)
    for k in range(FIX_N):
        a = 2 * math.pi * k / FIX_N + math.pi / FIX_N
        cup = cup - C(ENDWALL_T + 4, FIX_SCREW / 2).translate(
            [SEAT_LEN / 2, FIX_PCD / 2 * math.cos(a), FIX_PCD / 2 * math.sin(a)])

    # 定子法兰沉台: 端面内侧留 2mm 深定位台阶 (φ=FIX_PCD+8)
    recess = C(2.2, (FIX_PCD + 10) / 2).translate([SEAT_LEN / 2 - ENDWALL_T - 0.1, 0, 0])
    cup = cup - recess

    return cup


def spider_body():
    body = Manifold()

    # 中央发射孔环
    ring = C(RING_LEN, BORE_R + RING_WALL) - C(RING_LEN + 4, BORE_R)
    body = body + ring

    for i in range(N):
        ang = 90 + i * 120
        # 杯座: 壳心在 R_C, 轴朝外
        seat = seat_cup().translate([R_C, 0, 0])
        body = body + rot_z(seat, ang)

        # 座↔环 一体肋
        rib_len = R_C - SEAT_IR - (BORE_R + RING_WALL) + 12
        rib = Manifold.cube([rib_len, RIB_W, RIB_T], False)
        rib = rib.translate([BORE_R + RING_WALL - 6, -RIB_W / 2, -RIB_T / 2])
        body = body + rot_z(rib, ang)

        # 孔壁窗口 (壳面凸入孔内)
        win = C(RING_LEN - 16, SEAT_IR - 3)
        win = rot_y(win, 90).translate([BORE_R + RING_WALL + 20, 0, 0])
        win = rot_z(win, ang)
        cutter = C(RING_LEN + 2, BORE_R + RING_WALL + 1) - C(RING_LEN + 2, BORE_R - 1)
        body = body - Manifold.batch_boolean([win, cutter], OpType.Intersect)

    return body


if __name__ == "__main__":
    print("generating v24 cage with motor-fix details ...")
    save(spider_body(), "spider_body_v24.stl")
    print("done ->", OUT)
