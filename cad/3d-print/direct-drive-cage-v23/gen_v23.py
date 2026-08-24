"""
Football Launcher — v23: 一体化径向直驱笼体 (结构拓扑复现)

参考结构本质 (特写判读):
  - 单件打印: 中央发射孔环 + 三瓣电机凸耳座, 一体成型
  - 电机轴线径向 (⊥ 管轴), 120° 均布
  - 电机壳伸入中央孔, 壳面即孔内壁一部分 (球在孔内被三壳面夹持加速)
  - 参考电机扁平; 本设计用 6374 → 座/环相应加厚

仅结构拓扑, 不含卡环/螺丝等安装细节 (后续再加)。

用法: python3 gen_v23.py
"""
import math
import os
import struct

import numpy as np
from manifold3d import Manifold

# ---- 球 / 孔 ----
BALL_R = 110.0
BORE_R = 100.0                 # 中央发射孔 (球挤过, 三壳面凸入夹持)

# ---- 6374 + PU ----
ROLL_R = 39.5                  # φ63壳+8mm PU
MOTOR_D = 63.0
MOTOR_L = 74.0                 # 比参考扁平电机长 → 座加厚
PRELOAD = 6.0                  # 壳面凸入孔缘深度
R_C = BORE_R - PRELOAD + ROLL_R  # 壳心分布半径 = 133.5

# ---- 中央环 (一体化: 环壁直接长出电机座) ----
RING_LEN = 56.0                # 环轴向长 (6374 较长 → 环比参考加厚)
RING_WALL = 9.0                # 孔缘壁

# ---- 电机座 (与环一体) ----
SEAT_IR = MOTOR_D / 2 + 0.5    # 32.0 内弧贴壳
SEAT_WALL = 8.0
SEAT_ARC = 160.0               # 抱壳包角, 开口朝孔侧(壳面由此凸入)
SEAT_LEN = RING_LEN + 8.0      # 座比环略长, 包住壳全段

# ---- 连接肋 (座与环之间, 同体材料) ----
RIB_T = 14.0                   # 肋厚(轴向)
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


def seat_solid():
    """电机座实体 (局部: 电机轴沿 +X, 壳心在原点).
    弧筒 160° 包角, 开口朝 -X (孔侧)."""
    outer = C(SEAT_LEN, SEAT_IR + SEAT_WALL)
    inner = C(SEAT_LEN + 4, SEAT_IR)
    ring = outer - inner
    # 开口: 切除 -X 侧 200° 扇区
    w1 = Manifold.cube([300, 300, SEAT_LEN + 8], True).translate([-150, 0, 0])
    w2 = rot_z(Manifold.cube([300, 300, SEAT_LEN + 8], True).translate([0, -150, 0]),
               -(180 - SEAT_ARC) / 2)
    w3 = rot_z(Manifold.cube([300, 300, SEAT_LEN + 8], True).translate([0, 150, 0]),
               (180 - SEAT_ARC) / 2)
    ring = ring - w1 - w2 - w3
    return rot_y(ring, 90)         # 弧轴转沿 X


def spider_body():
    body = Manifold()

    # --- 中央发射孔环 ---
    ring = C(RING_LEN, BORE_R + RING_WALL) - C(RING_LEN + 4, BORE_R)
    body = body + ring

    # --- 三瓣电机座: 与环同体材料, 壳心位于 R_C ---
    for i in range(N):
        ang = 90 + i * 120
        seat = seat_solid().translate([R_C, 0, 0])
        seat = rot_z(seat, ang)
        body = body + seat

        # 座↔环 一体连接肋 (径向, 与环壁熔合)
        rib_len = R_C - SEAT_IR - (BORE_R + RING_WALL) + 12
        rib = Manifold.cube([rib_len, RIB_W, RIB_T], False)
        rib = rib.translate([BORE_R + RING_WALL - 6, -RIB_W / 2, -RIB_T / 2])
        body = body + rot_z(rib, ang)

    # --- 座内弧与环壁之间的过渡: 让壳面真正凸入孔内 ---
    # 在孔壁开三个窗口 (壳面由此进入孔内)
    for i in range(N):
        ang = 90 + i * 120
        # 窗口 = 座内弧在孔壁上的投影, 略缩小
        win = C(RING_LEN - 16, SEAT_IR - 3)
        win = rot_y(win, 90).translate([BORE_R + RING_WALL + 20, 0, 0])
        win = rot_z(win, ang)
        # 只切孔壁那一侧材料: 用与环壁等厚的切割环
        cutter = (C(RING_LEN + 2, BORE_R + RING_WALL + 1) - C(RING_LEN + 2, BORE_R - 1))
        from manifold3d import OpType
        win_cut = Manifold.batch_boolean([win, cutter], OpType.Intersect)
        body = body - win_cut

    return body


if __name__ == "__main__":
    print("generating v23 monolithic radial direct-drive cage ...")
    save(spider_body(), "spider_body_v23.stl")
    print("done ->", OUT)
