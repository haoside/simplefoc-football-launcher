"""
Football Launcher — v20: V2 直驱笼体 (参考视频结构移植)
电机外转子壳(φ63)+PU套(→φ79) 直接作为摩擦面, 无独立摩擦轮。

零件:
  spider_body_v20.stl   主笼体 (中心球道 + 三瓣120°摇篮 + 安装耳)
  cradle_clamp_v20.stl  摇篮压盖 ×3 (束带/螺柱预紧)
  side_plate_v20.stl    端板 ×2 (轴承/俯仰安装)

用法:
  python3 gen_v20.py            # 输出 STL 到 ./stls
"""
import math
import os

import numpy as np
from manifold3d import Manifold

# ============================================================
# 参数 (与 sim/odrive_launch_sim_v1.py V2 同源)
# ============================================================
BALL_D = 220
BALL_R = BALL_D / 2                      # 110

# 6374 外转子电机 (标准尺寸)
MOTOR_D = 63.0                           # 转子壳直径
MOTOR_L = 74.0                           # 壳长
MOTOR_SHAFT_D = 8.0
MOTOR_FIX_HOLE_D = 3.4                   # M3
MOTOR_FIX_PCD = 25.0                     # 端盖螺丝 PCD (典型 25mm, 打印后按实物修配)
MOTOR_FIX_N = 4

# PU 套 → 滚动面
ROLL_D = 79.0                            # φ63 壳 + 8mm PU = 滚动直径
ROLL_L = 48.0                            # PU 套有效宽度

# 笼体 / 球道
BORE_IR = BALL_R + 2.0                   # 球道内半径 112
WALL = 6.0                               # 球道壁厚
CAGE_W = WALL * 2 + BORE_IR * 2          # 笼体外径向包络
SEGMENTS = 96

# 摇篮: 弧面包住滚动面, 内弧半径 = ROLL_D/2 + 0.4 打印间隙
CRADLE_CLEAR = 0.4
CRADLE_IR = ROLL_D / 2 + CRADLE_CLEAR    # 39.9
CRADLE_ARC_DEG = 105                     # 包角 (>90° 自对中, 开口供压入)
CRADLE_THICK = 7.0                       # 弧壁厚
CRADLE_STRUT_W = 22.0                    # 连接梁宽
N_MOTORS = 3

# 预紧压盖
CLAMP_T = 8.0                            # 压盖厚度
CLAMP_SCREW_D = 6.5                      # M6 束带柱孔
CLAMP_LEN = 34.0
CLAMP_W = 16.0

# 端板
PLATE_D = 150.0
PLATE_T = 6.0
PLATE_BORE_D = 30.0                      # 俯仰轴孔
PLATE_SCREW_D = 5.5                      # M5 连接笼体

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stls")
os.makedirs(OUT_DIR, exist_ok=True)


# ============================================================
# manifold 工具
# ============================================================
def C(h, r1, r2=None):
    if r2 is None:
        r2 = r1
    return Manifold.cylinder(h, r1, r2, SEGMENTS)


def rot_x(m, deg):
    return m.rotate([deg, 0, 0])


def rot_z(m, deg):
    return m.rotate([0, 0, deg])


def at_polar(m, radius, angle_deg):
    """把 XY 平面原点物体平移到极坐标 (radius, angle)"""
    a = math.radians(angle_deg)
    return m.translate([radius * math.cos(a), radius * math.sin(a), 0])


def save(body, name):
    mesh = body.to_mesh()
    verts = np.asarray(mesh.vert_properties, dtype=np.float32)[:, :3]
    tris = np.asarray(mesh.tri_verts, dtype=np.int32)
    path = os.path.join(OUT_DIR, name)
    with open(path, "wb") as f:
        _write_stl(f, verts, tris)
    print(f"  {name}: {len(tris)} tris")


def _write_stl(fh, verts, tris):
    import struct
    fh.write(b"\x00" * 80)
    fh.write(struct.pack("<I", len(tris)))
    for t in tris:
        p0, p1, p2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(p1 - p0, p2 - p0)
        ln = np.linalg.norm(n)
        n = n / ln if ln > 1e-12 else np.array([0.0, 0.0, 1.0])
        fh.write(struct.pack("<3f", *n))
        for p in (p0, p1, p2):
            fh.write(struct.pack("<3f", *p))
        fh.write(struct.pack("<H", 0))


# ============================================================
# 单个摇篮模块 (局部系: 摇篮弧心在原点, 弧轴沿 Z)
# ============================================================
def cradle_ring():
    """>105° 包角弧形座, 开口朝 +Y (球道方向)"""
    outer = C(MOTOR_L + 4, CRADLE_IR + CRADLE_THICK)
    inner = C(MOTOR_L + 4 + 2, CRADLE_IR)
    ring = outer - inner
    # 切掉开口扇区, 留 >105° 包角
    open_wedge = Manifold.cube([200, 200, 200], True).translate([0, 100 + CRADLE_IR * 0.35, 0])
    ring = ring - open_wedge
    # 底部实心加强筋
    rib = Manifold.cube([CRADLE_THICK * 2, 14, MOTOR_L + 4], True).translate(
        [-(CRADLE_IR + CRADLE_THICK / 2), -(CRADLE_IR + 4), 0])
    ring = ring + rib
    return ring


def clamp_plate():
    """压盖: 盖住开口, 中间 M6 孔穿预紧螺柱"""
    plate = Manifold.cube([CLAMP_LEN, CLAMP_W, CLAMP_T], True)
    plate = plate - C(CLAMP_T + 2, CLAMP_SCREW_D / 2).translate([CLAMP_LEN / 2 - 9, 0, 0])
    # 两端 M3 沉头孔锁进摇篮侧壁
    for sx in (-CLAMP_LEN / 2 + 5, CLAMP_LEN / 2 - 5):
        plate = plate - C(CLAMP_T + 2, 1.8).translate([sx, 0, 0])
    return plate


# ============================================================
# 主笼体: 中心球道 + 三瓣摇篮连接梁
# ============================================================
def spider_body():
    body = Manifold()

    # --- 中心球道短筒 ---
    tube = C(120, BORE_IR + WALL) - C(140, BORE_IR)
    body = body + tube

    # --- 三瓣摇篮 (120°, 12点/4点/8点) ---
    for i in range(N_MOTORS):
        ang = 90 + i * 120
        # 摇篮弧心位置: 球道壁外侧, 使滚动面与球道内切
        cradle_center_R = BORE_IR + ROLL_D / 2 - 2.0     # 滚动面侵入球道 2mm ≈ 预紧基准
        ring = rot_x(cradle_ring(), 90)                  # 弧轴转向径向
        ring = at_polar(ring.translate([0, 0, 0]), 0, 0)  # keep
        # 把弧环从竖直转为径向朝外: 先绕 X 转90°使轴向=X, 再极坐标摆放
        ring = rot_z(ring, ang - 90)
        ring = ring.translate([
            cradle_center_R * math.cos(math.radians(ang)),
            cradle_center_R * math.sin(math.radians(ang)),
            0,
        ])
        body = body + ring

        # 连接梁: 球道外壁 -> 摇篮底
        strut = Manifold.cube([cradle_center_R, CRADLE_STRUT_W, MOTOR_L + 4], False).translate(
            [0, -CRADLE_STRUT_W / 2, -(MOTOR_L + 4) / 2])
        strut = rot_z(strut, ang)
        body = body + strut

    # --- 球道口翻边 (上下各 8mm) ---
    flange = C(8, PLATE_D / 2) - C(10, BORE_IR)
    body = body + flange.translate([0, 0, -8])
    body = body + flange.translate([0, 0, 112])

    # --- 端板螺丝柱 (×6 @PCD135) ---
    for i in range(6):
        boss = C(120, 7.0)
        body = body + at_polar(boss, 135.0 / 2 + 3.5, i * 60).translate([0, 0, 0])

    return body


def side_plate():
    plate = C(PLATE_T, PLATE_D / 2) - C(PLATE_T + 2, BORE_IR - 10)
    plate = plate + C(PLATE_T + 4, 16).translate([0, 0, 0])       # 轴毂
    plate = plate - C(PLATE_T + 8, PLATE_BORE_D / 2)              # 俯仰轴孔
    for i in range(6):                                            # 与笼体拉杆孔
        plate = plate - at_polar(C(PLATE_T + 2, PLATE_SCREW_D / 2), 135.0 / 2 + 3.5, i * 60)
    return plate


if __name__ == "__main__":
    print("generating v20 direct-drive cage parts ...")
    save(spider_body(), "spider_body_v20.stl")
    save(clamp_plate(), "cradle_clamp_v20.stl")
    save(side_plate(), "side_plate_v20.stl")
    print("done ->", OUT_DIR)
