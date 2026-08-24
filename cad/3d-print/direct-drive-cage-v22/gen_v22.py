"""
Football Launcher — v22: 径向电机直驱笼体 (参考结构最终修正版)

参考特写确认的几何:
  - 中央球孔轴线 = 发射管轴 (Z)
  - 三电机轴线 = 径向 (XY 平面内, 120° 均布), 与管轴成 90°
  - 转子壳(φ63+PU套=φ79) 圆周正切于球孔缘, 壳面凸入孔内 PRELOAD
  - 旋转切向速度沿 Z → 球沿管轴射出 (旋转向外=壳外表面为工作面)
  - 电机从笼体外侧轴向插入弧形座, 定子端盖朝外

零件:
  spider_body_v22.stl    主笼体 (中心孔环 + 三径向电机弧座 + 连接梁)
  motor_snap_ring_v22.stl 电机卡环 ×3 (插入后锁住电机外端)
"""
import math
import os
import struct

import numpy as np
from manifold3d import Manifold

# ---- 球 / 转子 ----
BALL_R = 110.0
BORE_R = 100.0                     # 中央球道孔 (φ200, 球挤过预紧)
ROLL_R = 39.5                      # φ63壳 + PU 8mm → φ79
PRELOAD = 6.0                      # 壳面凸入孔缘深度 (孔缘半径 100, 切点在 94)
MOTOR_D = 63.0
MOTOR_L = 74.0

# 电机轴线径向: 转子壳心到笼体中心距离
# 壳面最近点距离 = R_c - ROLL_R = BORE_R - PRELOAD
R_C = BORE_R - PRELOAD + ROLL_R    # 133.5

# ---- 弧形电机座 (抱住转子壳, 轴向长=壳长) ----
SEAT_IR = MOTOR_D / 2 + 0.5        # 32.0 内弧 (贴壳)
SEAT_WALL = 7.0
SEAT_ARC_DEG = 150.0               # 包角, 开口朝孔(装球侧) → 实际开口朝外装电机
SEAT_LEN = MOTOR_L + 6.0           # 80

# ---- 中心孔环 ----
RING_WALL = 8.0                    # 孔缘壁厚
RING_LEN = 60.0                    # 孔环轴向长度 (导球段)

# ---- 连接梁 ----
STRUT_W = 20.0
STRUT_T = 12.0

# ---- 卡环 ----
RING_T = 6.0
RING_SCREW = 3.2

SEG = 96
N_MOTORS = 3
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stls")
os.makedirs(OUT, exist_ok=True)


def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEG)


def rot_x(m, d): return m.rotate([d, 0, 0])
def rot_y(m, d): return m.rotate([0, d, 0])
def rot_z(m, d): return m.rotate([0, 0, d])


def polar_xy(m, r, ang_deg, z=0.0):
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


def motor_seat():
    """径向电机弧座 (局部系: 电机轴沿 +X, 壳心在原点).
    弧筒轴沿 X; 开口扇区朝 -X (朝孔侧, 让壳面凸入孔内并走线)."""
    outer = C(SEAT_LEN, SEAT_IR + SEAT_WALL)          # 轴沿 Z, 之后转
    inner = C(SEAT_LEN + 2, SEAT_IR)
    ring = outer - inner
    # 开口: 切除朝 -X 的 360-150=210° 扇区 → 保留朝 +X 的 150° 包角
    wedge = Manifold.cube([300, 300, SEAT_LEN + 4], True)
    wedge = wedge.translate([-150, 0, 0])             # -X 半平面
    # 半平面只切一半? 需要 210° 开口: 再加两个斜半平面
    wedge2 = Manifold.cube([300, 300, SEAT_LEN + 4], True)
    wedge2 = wedge2.translate([0, -150, 0])           # -Y 半平面
    wedge2 = rot_z(wedge2, -(180 - SEAT_ARC_DEG) / 2 + 0)
    wedge3 = rot_z(Manifold.cube([300, 300, SEAT_LEN + 4], True).translate([0, 150, 0]),
                   (180 - SEAT_ARC_DEG) / 2)
    ring = ring - wedge - wedge2 - wedge3
    # 转为轴沿 X
    ring = rot_y(ring, 90)
    return ring


def spider_body():
    body = Manifold()

    # --- 中央孔环 (发射管段, 轴 Z) ---
    ring = C(RING_LEN, BORE_R + RING_WALL) - C(RING_LEN + 4, BORE_R)
    body = body + ring.translate([0, 0, -RING_LEN / 2])

    # --- 三个径向电机座 (120°: 12点/4点/8点) ---
    for i in range(N_MOTORS):
        ang = 90 + i * 120
        seat = motor_seat()                            # 轴沿 +X, 壳心在原点
        # 平移壳心到 R_C, 再旋转到方位角
        seat = seat.translate([R_C, 0, 0])
        seat = rot_z(seat, ang - 0)
        body = body + seat

        # 座-孔环连接梁 (径向, 在座上方/下方各一条 → 实际一条厚梁)
        strut = Manifold.cube([R_C - BORE_R - RING_WALL + 14, STRUT_W, STRUT_T], False)
        strut = strut.translate([BORE_R + RING_WALL - 7, -STRUT_W / 2, -STRUT_T / 2])
        strut = rot_z(strut, ang)
        body = body + strut

        # 座端面卡环螺丝沉孔 (外端面 3×M3, 锁 motor_snap_ring)
        for k in range(3):
            a = math.radians(k * 120 + 60)
            hole = C(14, RING_SCREW / 2)
            hole = hole.translate([R_C + SEAT_IR + SEAT_WALL - 2,
                                   (SEAT_IR - 6) * math.cos(a),
                                   (SEAT_IR - 6) * math.sin(a)])
            hole = rot_y(hole, 90)
            hole = rot_z(hole, ang)
            body = body - hole

    # --- 孔环外翻边 (上下端, 复现参考图的台阶口) ---
    fl = C(6, BORE_R + RING_WALL + 8) - C(8, BORE_R)
    body = body + fl.translate([0, 0, -RING_LEN / 2 - 3])
    body = body + fl.translate([0, 0, RING_LEN / 2 - 3])

    return body


def motor_snap_ring():
    """电机外端卡环 (局部: 轴沿 X 后由装配旋转; 生成时轴沿 Z).
    环形, 中心孔让轴穿过, 3×M3 对准座端面沉孔."""
    ring = C(RING_T, SEAT_IR + SEAT_WALL) - C(RING_T + 4, 12.0)   # 中心过轴孔 φ24
    for k in range(3):
        a = math.radians(k * 120 + 60)
        ring = ring - C(RING_T + 4, RING_SCREW / 2).translate(
            [(SEAT_IR - 6) * math.cos(a), (SEAT_IR - 6) * math.sin(a), -2])
    return ring


if __name__ == "__main__":
    print("generating v22 radial-motor direct-drive cage ...")
    save(spider_body(), "spider_body_v22.stl")
    save(motor_snap_ring(), "motor_snap_ring_v22.stl")
    print("done ->", OUT)
