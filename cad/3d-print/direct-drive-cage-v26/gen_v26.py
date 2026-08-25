"""
Football Launcher — v26: 切向电机 + 耳板轴孔 (参考CAD最终忠实复现)

参考CAD判读 (14:28 截图, 从零重看):
  - 单件紫色笼体: 中央发射孔环 + 三个平板凸耳(耳板)
  - 电机轴线与孔圆周**相切** (切向, ⊥半径) — 三个切向滚轮
  - 耳板从环壁径向长出, 板面法向=切向, 板上过轴孔
  - 电机本体在环外, 转子壳穿过环壁切向窗口伸入孔内
  - 壳面接触点速度沿管轴 → 球沿管轴射出 (旋转向外)

用法: python3 gen_v26.py
"""
import math
import os
import struct

import numpy as np
from manifold3d import Manifold, OpType

# ---- 球 / 孔环 ----
BALL_R = 110.0
BORE_R = 100.0                  # 孔半径
RING_OR = 118.0                 # 环外径
RING_LEN = 64.0                 # 环轴向长

# ---- 6374 + PU ----
ROLL_R = 39.5                   # φ63壳+PU8
MOTOR_D = 63.0
MOTOR_L = 74.0
PRELOAD = 6.0
R_C = BORE_R - PRELOAD + ROLL_R # 壳心分布半径 = 133.5 (切向轴)

# ---- 耳板 ----
EAR_T = 16.0                    # 板厚 (切向) — 轴孔贯穿此面
EAR_W = 34.0                    # 板宽 (轴向)
EAR_OUT_R = 178.0               # 板外缘半径
SHAFT_HOLE = 8.7                # 过轴孔

# ---- 壳穿墙窗口 ----
WIN_LEN = 56.0                  # 窗口轴向长

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


def spider_body():
    body = Manifold()

    # ---- 中央发射孔环 ----
    ring = C(RING_LEN, RING_OR) - C(RING_LEN + 4, BORE_R)
    body = body + ring

    for i in range(N):
        ang = 90 + i * 120
        a = math.radians(ang)
        ax_t = (-math.sin(a), math.cos(a))            # 切向 (电机轴方向)

        # ---- 耳板: 从环壁径向长出的平板, 板面法向=切向 ----
        # 局部生成: 板沿 +Y 径向延伸, 厚度沿 X(切向), 再旋转到位
        ear_len = EAR_OUT_R - RING_OR + 6
        ear = Manifold.cube([EAR_T, ear_len, EAR_W], False)
        ear = ear.translate([-EAR_T / 2, RING_OR - 6, -EAR_W / 2])
        # 过轴孔: 在 R_C 处, 沿切向贯穿
        ear = ear - C(EAR_T + 4, SHAFT_HOLE / 2).translate([0, R_C - (RING_OR - 6), 0])
        # 板端圆角(简化: 顶部半圆)
        tip = C(EAR_W, EAR_T / 2)
        tip = rot_x(tip, 90)
        tip = tip.translate([0, ear_len - 4, 0])
        ear = ear + tip
        tip_hole = C(EAR_W + 4, 3.2 / 2)              # 端部 M3 吊装孔(参考图可见)
        tip_hole = rot_x(tip_hole, 90).translate([0, ear_len - 4, 0])
        ear = ear - tip_hole
        body = body + rot_z(ear, ang)

        # ---- 环壁切向窗口: 壳由此穿墙入孔 ----
        # 窗口 = 以壳心为中心的径向圆柱 ∩ 环壁
        win = C(WIN_LEN, ROLL_R - 1)
        win = rot_y(win, 90).translate([RING_OR + 20, 0, 0])
        win = rot_z(win, ang)
        wall = C(RING_LEN + 2, RING_OR + 1) - C(RING_LEN + 2, BORE_R - 1)
        body = body - Manifold.batch_boolean([win, wall], OpType.Intersect)

    return body


if __name__ == "__main__":
    print("generating v26 tangential-motor ear-tab cage ...")
    save(spider_body(), "spider_body_v26.stl")
    print("done ->", OUT)
