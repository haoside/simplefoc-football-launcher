"""
Football Launcher — v20 修正外圈加强设计

参考图特征（核对清楚）：
1. 3 个独立 cradle 轮（不是连续外壳）
2. 每个轮：外圈轮辋 + 3 条辐条 + 中心 hub
3. 外圈厚环（加强轮辋）
4. 4 颗 M5 螺栓固定到管
5. 电机 can 端朝下接触球
6. 电机轴切向（v18 物理，+Z 推球）

修正 v19 错误：
- 删连续外壳
- 3 个独立轮盘（外圈 + 辐条 + hub）
- 简单管 + 3 轮辋螺栓固定
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
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

TUBE_IR = BALL_R + 3
TUBE_OR = TUBE_IR + 6    # 119mm
TUBE_LEN = 200

CONTACT_PRELOAD = 1
MOTOR_CENTER_R = BALL_R - CONTACT_PRELOAD + MOTOR_CAN_R  # 140.5mm

# 单个轮辋参数
CRADLE_RIM_OR = MOTOR_CENTER_R + 20  # 160.5mm（轮辋外径）
CRADLE_RIM_IR = MOTOR_CENTER_R - 25  # 115.5mm（轮辋内径 = 包管外侧）
CRADLE_RIM_THICK = 14            # 轮辋厚度（参考图：厚环，加强）
CRADLE_RIM_W = (CRADLE_RIM_OR - CRADLE_RIM_IR) / 2  # 22.5mm 环宽

# Hub 参数
CRADLE_HUB_OD = MOTOR_D + 8    # 71mm
CRADLE_HUB_LEN = MOTOR_L + 6   # 80mm
CRADLE_HUB_THICK = CRADLE_RIM_THICK

# 辐条参数
CRADLE_SPOKE_W = 18
CRADLE_SPOKE_T = CRADLE_RIM_THICK - 4

# 螺栓孔
CRADLE_BOLT_D = 5.5           # M5 通孔
CRADLE_BOLT_PCD = (CRADLE_RIM_OR + CRADLE_RIM_IR) / 2  # 138mm
CRADLE_BOLT_COUNT = 4

N_MOTORS = 3
SEGMENTS = 96
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


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
# Part 1: 单个独立 Cradle 轮（参考图风格）
# ============================================================
def make_single_cradle_v20():
    """
    单个 cradle 轮 — 匹配参考图：
    - 外圈轮辋（厚环，加强）
    - 3 条辐条（120° 间隔）
    - 中心 hub（容纳电机）
    - 4 颗 M5 螺栓孔
    - 轮辋内径 = 包管外侧
    """
    # 外圈轮辋（环形，YZ 平面内，垂直于电机轴 Z）
    # 这里我们做 XY 平面内的环（盘状）
    rim_outer = C(CRADLE_HUB_THICK, CRADLE_RIM_OR / 2)
    rim_inner = C(CRADLE_HUB_THICK + 0.4, CRADLE_RIM_IR / 2)
    rim = rim_outer - rim_inner

    # 4 颗 M5 螺栓孔（在外圈中线上）
    for j in range(CRADLE_BOLT_COUNT):
        ra = math.radians(j * 90 + 45)  # 45° 偏移，从辐条中间
        bx = CRADLE_BOLT_PCD / 2 * math.cos(ra)
        by = CRADLE_BOLT_PCD / 2 * math.sin(ra)
        bolt = C(CRADLE_HUB_THICK + 2, CRADLE_BOLT_D / 2, 16)
        bolt = bolt.translate([bx, by, 0])
        rim = rim - bolt

    body = rim

    # 中心 hub（沿 Z 轴，容纳电机 — can 切向放置，Z 方向是轮面法向）
    hub_outer = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2)
    hub_inner = C(CRADLE_HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    hub = hub_outer - hub_inner

    # 电机轴孔（沿 Z 轴）
    shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    hub = hub - shaft

    # 4 个 M4 电机螺栓孔（端面，XY 平面）
    for j in range(4):
        ja = math.radians(j * 90)
        bolt_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        bolt_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        bolt = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        bolt = bolt.translate([bolt_x, bolt_y, CRADLE_HUB_LEN / 2 - 3])
        hub = hub - bolt

    # 中心 hub 也加宽成圆盘（参考图：hub 和轮辋之间平滑过渡）
    # 在 hub 周围加一个加宽的过渡盘
    trans_outer = C(CRADLE_HUB_THICK, (CRADLE_HUB_OD + 8) / 2)
    trans_inner = C(CRADLE_HUB_THICK + 0.4, CRADLE_HUB_OD / 2)
    trans = trans_outer - trans_inner
    body = body + trans

    # 3 条辐条（XY 平面内）
    spoke_len = (CRADLE_RIM_OR - CRADLE_HUB_OD) / 2 - CRADLE_RIM_W / 2 - 3
    spoke_offset = (CRADLE_HUB_OD + CRADLE_RIM_OR) / 4

    for j in range(3):
        sa = math.radians(j * 120)
        spoke = Manifold.cube((spoke_len, CRADLE_SPOKE_W, CRADLE_SPOKE_T), center=True)
        # 旋转：长边沿径向方向
        spoke = spoke.rotate([0, 0, sa])
        spoke = spoke.translate([spoke_offset * math.cos(sa),
                                 spoke_offset * math.sin(sa), 0])
        body = body + spoke

    # 在轮辋外圈加额外的加强环（参考图：外圈明显厚）
    # 在外圈外侧再加一圈薄环作为视觉特征
    outer_band = C(CRADLE_HUB_THICK + 1.6, CRADLE_RIM_OR / 2 + 0.8) - \
                 C(CRADLE_HUB_THICK + 2.0, CRADLE_RIM_OR / 2)
    outer_band = outer_band.translate([0, 0, -0.8])
    body = body + outer_band

    save(body, "cradle_wheel_v20.stl")


# ============================================================
# Part 2: 简单管 + 3 轮辋螺栓固定孔
# ============================================================
def make_tube_v20():
    """
    简单管：
    - 球通道
    - 3 处轮辋安装面（每个带 4×M5 螺母孔 + can 通过孔）
    """
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 3 个 can 通过孔（管壁，让 can 接触球）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = (TUBE_OR + TUBE_IR) / 2 * math.cos(angle)
        cy = (TUBE_OR + TUBE_IR) / 2 * math.sin(angle)
        # can 通过孔（直径比 can 略大）
        can_hole = C(TUBE_LEN + 2, MOTOR_D / 2 + 4)
        can_hole = can_hole.translate([cx, cy, TUBE_LEN / 2])
        body = body - can_hole

    # 3 处轮辋安装位置（每处 4 颗 M5 螺母沉孔，对应 cradle 螺栓）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        for j in range(4):
            # 螺栓在轮辋安装面（沿管外壁，但对应 cradle 螺栓位置）
            ja = angle + math.radians(j * 90 + 45)
            bx = TUBE_OR * math.cos(ja) + 1
            by = TUBE_OR * math.sin(ja) + 1
            # 螺母沉孔
            nut = C(8, 5.0)  # M5 螺母外径
            nut = nut.translate([bx, by, TUBE_LEN / 2])
            body = body - nut

    # 加固环
    for z in [6, TUBE_LEN - 6]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "tube_v20.stl")


# ============================================================
# Part 3: 端板
# ============================================================
def make_side_plate_v20():
    plate_r = TUBE_OR + 5
    h = 6
    plate = C(h, plate_r)
    plate = plate - C(h + 2, BALL_R + 3)
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 4) * math.cos(a)
        by = (plate_r - 4) * math.sin(a)
        hole = C(h + 2, 2.7, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole
    save(plate, "side_plate_v20.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v20: 独立 Cradle 轮辋 + 简单管（修正 v19 外圈错误）")
    print("=" * 50)
    print("修正点（vs v19）：")
    print("- ❌ 删连续外壳（v19 错）")
    print("- ✅ 3 个独立 cradle 轮（参考图风格）")
    print("- ✅ 每个轮：外圈轮辋 + 3 辐条 + 中心 hub")
    print("- ✅ 外圈厚环加强（14mm 厚）")
    print("- ✅ 4×M5 螺栓固定到管")
    print("- ✅ 简单管 + 螺母沉孔")
    print()

    make_single_cradle_v20()
    make_tube_v20()
    make_side_plate_v20()

    print(f"\n✓ 3 个零件（3 轮 + 1 管 + 2 端板）→ {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()