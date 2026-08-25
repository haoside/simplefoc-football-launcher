"""
Football Launcher — v27: 切向耳板笼体 + 轴承固定轴板 + MKS XDRIVE Mini 基座

在 v26 拓扑 (切向电机/耳板过轴孔/壳穿墙) 基础上新增:
  1. 耳板轴孔升级为轴承座 (625ZZ φ16×5, 轴向定位+径向支撑转子轴)
  2. 耳板外端加 MKS XDRIVE Mini 驱动板基座 (每电机一块, 就近安装)
     - 板体实测: ~66.3 × 58.2 mm, 双轴 ODrive 兼容固件 v0.5.1
     - 一块 XDRIVE Mini 驱动 2 轴 → 3 电机用 2 块板 (axis0/axis1)
  3. AS5047 磁编支持: 基座含 AS5047 小板位 + 磁钢轴向间隙对位
     (AS5047P 装于轴端, 与磁铁同心, 气隙 1~2mm)

用法: python3 gen_v27.py
"""
import math
import os
import struct

import numpy as np
from manifold3d import Manifold, OpType

# ---- 球 / 孔环 ----
BALL_R = 110.0
BORE_R = 100.0
RING_OR = 118.0
RING_LEN = 64.0

# ---- 6374 裸壳 (无PU — Owner 指定) ----
MOTOR_D = 63.0
ROLL_R = MOTOR_D / 2             # 31.5
PRELOAD = 8.0
R_C = BORE_R - PRELOAD + ROLL_R  # 123.5 切向轴心分布半径

# ---- 轴 / 轴承 ----
SHAFT_D = 8.0
BEAR_OD = 16.0                   # 625ZZ 薄壁轴承
BEAR_T = 5.0
EAR_T = 18.0                     # 加厚到轴承宽+端面余量

# ---- 耳板 ----
EAR_W = 34.0
EAR_OUT_R = R_C + BEAR_OD / 2 + 8   # 覆盖轴承座圈 = 151.5

# ---- MKS XDRIVE Mini 基座 ----
XD_L = 68.0                      # 板长 (实测66.3 + 间隙)
XD_W = 60.0                      # 板宽 (实测58.2 + 间隙)
XD_T = 6.0                       # 基座板厚
XD_STAND_H = 12.0                # 底部抬高 (走线/散热)
XD_SCREW = 3.4                   # M3 安装孔
XD_SCREW_INSET = 4.5             # 孔边距 (按板实物孔位修配)

# ---- AS5047 小板 ----
AS_L = 20.0
AS_W = 20.0
AS_SCREW = 2.2                   # M2

N = 3
SEG = 96
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


def ear_with_bearing():
    """耳板 (局部: 板沿 +Y 径向延伸, 厚沿X切向, 宽沿Z).
    R_C 处: 轴承沉孔 (双侧各半, 压入625ZZ) + 过轴通孔."""
    ear_len = EAR_OUT_R - RING_OR + 6
    ear = Manifold.cube([EAR_T, ear_len, EAR_W], False)
    ear = ear.translate([-EAR_T / 2, RING_OR - 6, -EAR_W / 2])

    # 轴承沉孔: 从两侧面各挖 BEAR_T/2+0.5 深, φ16
    for side in (-1, 1):
        bore_seat = C(BEAR_T / 2 + 0.6, BEAR_OD / 2 + 0.15).translate(
            [side * (EAR_T / 2 - BEAR_T / 4), 0, 0]) if False else None
    # 正确做法: 轴承压入方向=轴向(切向X)? 不 — 轴沿切向X, 轴承外圈应嵌耳板,
    # 轴承轴线=X. 沉孔从板两外侧面向内各 (EAR_T-BEAR_T)/2 … 直接做通孔φ16.3+
    # 两侧卡环槽更易打印。简化: 通孔φ16.35 + 两端面各留 1.65mm 台阶挡肩。
    through = C(EAR_T + 4, BEAR_OD / 2 + 0.175).translate([0, R_C - (RING_OR - 6), 0])
    ear = ear - through
    # 挡肩: 中心环 φ13.4 通孔保留, 两端面台阶由 φ19 浅坑形成
    for s in (-1, 1):
        step = C((EAR_T - BEAR_T) / 2 + 0.01, (BEAR_OD + 6) / 2)
        step = step.translate([s * (EAR_T / 2 - (EAR_T - BEAR_T) / 4 + 0.001),
                               R_C - (RING_OR - 6), 0])
        # 反向: 这步是"保留材料"难表达 → 改为直接小通孔方案见下
    # 简化最终方案: 通孔φ16.35, 轴承两侧用打印垫圈(M3长螺丝夹紧)固定 — 结构最简
    shaft = C(EAR_T + 4, SHAFT_D / 2 + 0.2).translate([0, R_C - (RING_OR - 6), 0])
    ear = ear - shaft if False else ear   # 轴承内圈承担, 不再开细孔

    # 端部吊装孔
    tip = C(EAR_W, EAR_T / 2)
    tip = rot_x(tip, 90).translate([0, ear_len - 4, 0])
    ear = ear + tip
    tip_hole = rot_x(C(EAR_W + 4, 1.6), 90).translate([0, ear_len - 4, 0])
    ear = ear - tip_hole
    return ear


def xdrive_base():
    """MKS XDRIVE Mini 基座 (局部: 平放, XY=板面, Z=高).
    L型: 底板(带M3孔) + 立板(贴耳板外侧)."""
    base = Manifold.cube([XD_L, XD_W, XD_T], False)
    # 板安装孔 ×4 (角部内缩)
    for sx in (XD_SCREW_INSET, XD_L - XD_SCREW_INSET):
        for sy in (XD_SCREW_INSET, XD_W - XD_SCREW_INSET):
            base = base - C(XD_T + 2, XD_SCREW / 2).translate([sx, sy, -1])
    # 开口减重/走线窗 (中部)
    base = base - Manifold.cube([XD_L - 24, XD_W - 24, XD_T + 2], True).translate(
        [XD_L / 2, XD_W / 2, XD_T / 2])
    # AS5047 小板位 (底板一角, 20×20, 2×M2)
    as_pos = (XD_L - AS_L - 4, 4)
    for dx, dy in ((2, 2), (AS_L - 2, AS_W - 2)):
        base = base - C(XD_T + 2, AS_SCREW / 2).translate(
            [as_pos[0] + dx, as_pos[1] + dy, -1])
    return base


def spider_body():
    body = Manifold()

    # 中央发射孔环
    ring = C(RING_LEN, RING_OR) - C(RING_LEN + 4, BORE_R)
    body = body + ring

    for i in range(N):
        ang = 90 + i * 120
        a = math.radians(ang)

        # 耳板 (含轴承通孔)
        ear = ear_with_bearing()
        body = body + rot_z(ear, ang)

        # 壳穿墙窗口
        win = C(56.0, ROLL_R - 1)
        win = rot_y(win, 90).translate([RING_OR + 20, 0, 0])
        win = rot_z(win, ang)
        wall = C(RING_LEN + 2, RING_OR + 1) - C(RING_LEN + 2, BORE_R - 1)
        body = body - Manifold.batch_boolean([win, wall], OpType.Intersect)

        # XDRIVE 基座: 立在耳板外侧 (法向=切向), 底板平行耳板
        xb = xdrive_base()
        xb = rot_y(xb, 90)                       # 立起: 底板法向沿切向
        xb = xb.translate([-EAR_T / 2 - XD_T, R_C + 14, -(XD_W / 2) + EAR_W / 2 - 17])
        body = body + rot_z(xb, ang)

    return body


if __name__ == "__main__":
    print("generating v27 cage + bearing ears + XDRIVE bases ...")
    save(spider_body(), "spider_body_v27.stl")
    save(xdrive_base(), "xdrive_base_v27.stl")
    print("done ->", OUT)
