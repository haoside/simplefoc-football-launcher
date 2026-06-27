"""
Football Launcher — v3 增加电机辐条座（参考图橙色件）

参考图关键观察：
- 橙色 3D 打印件 = 带辐条的轮状电机座（独立件）
- 电机轴向平行于管长
- 电机外壳穿过管壁大圆孔接触球面
- 辐条轮外缘用螺栓固定到管壁
- 桥接筋连接相邻辐条轮保持刚性
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

# 6374 电机
MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管
TUBE_IR = BALL_R + 3           # 113mm
TUBE_OR = 140                  # 管外径
WALL = TUBE_OR - TUBE_IR       # 27mm
FRAME_LEN = 100                # 管长
MOTOR_HOLE_DIA = MOTOR_D + 2   # 65mm 管壁大圆孔

# 电机位置
MOTOR_CENTER_R = BALL_R + MOTOR_D / 2 + 5  # 146.5mm

# 辐条轮（电机座）
CRADLE_OD = MOTOR_CENTER_R + 15  # 161.5mm 轮外径（比凸台稍大）
CRADLE_THICK = 8                 # 轮厚
CRADLE_RIM_W = 8                 # 外缘宽度
CRADLE_HUB_OD = MOTOR_D + 8      # 71mm 中心轮毂外径
CRADLE_HUB_LEN = MOTOR_L + 10    # 84mm 中心轮毂长度
CRADLE_N_SPOKES = 4              # 辐条数
CRADLE_SPOKE_W = 6               # 辐条宽度
CRADLE_SPOKE_T = 6               # 辐条厚度

# 桥接筋
RIB_W = 8
RIB_T = 6

BOLT_D = 5
N_MOTORS = 3
SEGMENTS = 64

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
# Part 1: Launch Tube（发射管 — 简化为只有 3 个大圆孔）
# ============================================================
def make_launch_tube():
    """
    简化版发射管：
    - 整圆管（管内径 113mm 球通过）
    - 3 个大圆孔（让电机外壳穿过）
    - 3 组螺栓孔（用于固定辐条轮）
    - 两端加固环
    """
    # 主管
    tube = C(FRAME_LEN, TUBE_OR) - C(FRAME_LEN + 0.4, TUBE_IR)

    # 3 个电机位大圆孔（管壁上）
    hole_center_r = (TUBE_OR + TUBE_IR) / 2
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        cx = hole_center_r * math.cos(angle)
        cy = hole_center_r * math.sin(angle)

        hole = C(FRAME_LEN + 2, MOTOR_HOLE_DIA / 2)
        hole = hole.translate([cx, cy, 0])
        tube = tube - hole

    # 3 组辐条轮固定螺栓孔（每组 4 个 M4，围绕大圆孔）
    for i in range(N_MOTORS):
        angle = math.radians(i * 120)
        # 螺栓分布在 PCD = TUBE_OR + 5 处
        pcd = TUBE_OR + 5
        for j in range(4):
            ja = math.radians(j * 90 + 45)
            jx = pcd * math.cos(angle + ja)
            jy = pcd * math.sin(angle + ja)
            bolt = C(8, MOTOR_HOLE_D / 2 + 0.1, 16)
            bolt = bolt.translate([jx, jy, 0])
            tube = tube - bolt

    # 两端加固环
    for z in [8, FRAME_LEN - 8]:
        ring = C(5, TUBE_OR + 2) - C(6, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2.5])
        tube = tube + ring

    save(tube, "launch_tube.stl")


# ============================================================
# Part 2: Motor Cradle（电机辐条座 — 参考图橙色件）★ 关键新增
# ============================================================
def make_motor_cradle():
    """
    电机辐条座（参考图橙色件）：
    - 轮状：外缘 + 4 辐条 + 中心轮毂
    - 中心轮毂容纳 6374 电机
    - 电机轴向平行于管长
    - 电机外壳端朝向管内（穿过管壁大圆孔）
    - 辐条轮外缘用螺栓固定到管壁
    """
    # 中心轮毂（容纳电机，外径比电机大 4mm）
    hub = C(CRADLE_HUB_LEN, CRADLE_HUB_OD / 2)
    # 中心孔（电机穿入）
    hub = hub - C(CRADLE_HUB_LEN + 2, MOTOR_D / 2 + 0.5)
    # 电机轴孔
    shaft = C(CRADLE_HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    hub = hub - shaft

    # 电机端面螺栓孔（4 个 M4，固定电机）
    for i in range(4):
        a = math.radians(i * 90)
        hx = (MOTOR_HOLE_PCD / 2) * math.cos(a)
        hy = (MOTOR_HOLE_PCD / 2) * math.sin(a)
        hole = C(CRADLE_HUB_LEN + 2, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, 0])
        hub = hub - hole

    # 外缘环（轮缘，连接辐条）
    # 外径 = CRADLE_OD，内径 = CRADLE_OD - 2*CRADLE_RIM_W
    rim_outer = C(CRADLE_THICK, CRADLE_OD / 2)
    rim_inner = C(CRADLE_THICK + 0.4, CRADLE_OD / 2 - CRADLE_RIM_W)
    rim = rim_outer - rim_inner

    # 4 条辐条（从轮毂到外缘）
    spokes = Manifold()
    spoke_len = (CRADLE_OD - CRADLE_HUB_OD) / 2 - CRADLE_RIM_W / 2
    spoke_offset = (CRADLE_HUB_OD + CRADLE_OD) / 4
    for i in range(CRADLE_N_SPOKES):
        a = math.radians(i * 90)
        spoke = Manifold.cube((spoke_len, CRADLE_SPOKE_W, CRADLE_SPOKE_T), center=True)
        spoke = spoke.translate([spoke_offset, 0, 0])
        spoke = spoke.rotate([0, 0, a])
        spokes = spokes + spoke

    # 外缘螺栓孔（4 个 M5，固定到管壁）
    for i in range(4):
        a = math.radians(i * 90 + 45)
        bx = ((CRADLE_OD - CRADLE_RIM_W / 2) / 1) * math.cos(a)
        by = ((CRADLE_OD - CRADLE_RIM_W / 2) / 1) * math.sin(a)
        hole = C(CRADLE_THICK + 2, BOLT_D / 2 + 0.15, 16)
        hole = hole.translate([bx, by, 0])
        rim = rim - hole

    # 合并：轮毂 + 辐条 + 外缘
    cradle = hub + spokes + rim

    save(cradle, "motor_cradle.stl")


# ============================================================
# Part 3: Motor Can（电机外壳套）
# ============================================================
def make_motor_can():
    """
    电机外壳套：包裹电机外转子
    - 外表面 V 槽增加抓球
    - 法兰端固定
    """
    can_r_out = MOTOR_D / 2 + 1
    can_r_in = MOTOR_D / 2 + 0.3
    can_h = MOTOR_L

    can = C(can_h, can_r_out) - C(can_h + 0.4, can_r_in)

    # 法兰（连接到 cradle hub）
    flange = Manifold.cube((MOTOR_D + 20, MOTOR_D + 20, 4), center=True)
    flange = flange.translate([0, 0, can_h / 2 + 2])
    can = can + flange

    # 法兰 M4 孔
    for i in range(4):
        a = math.radians(i * 90)
        hx = (MOTOR_HOLE_PCD / 2) * math.cos(a)
        hy = (MOTOR_HOLE_PCD / 2) * math.sin(a)
        hole = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, can_h / 2 + 2])
        can = can - hole

    # V 槽（3 圈）
    for z_off in [-can_h / 2 + 8, 0, can_h / 2 - 8]:
        groove = C(3, can_r_out + 0.5) - C(3.4, can_r_out - 2)
        groove = groove.translate([0, 0, z_off])
        can = can - groove

    # 端盖（顶部）
    cap = C(2, can_r_out - 5) - C(3, can_r_in, SEGMENTS)
    cap = cap.translate([0, 0, -can_h / 2 + 1])
    can = can + cap

    save(can, "motor_can.stl")


# ============================================================
# Part 4: Side Plate（侧板）
# ============================================================
def make_side_plate():
    plate_r = TUBE_OR + 5
    h = 6

    plate = C(h, plate_r)
    plate = plate - C(h + 2, BALL_R + 3)
    plate = plate - C(h + 2, (TUBE_OR + 5) * 1)  # 外圆

    # 螺栓孔（8 个均布）
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 4) * math.cos(a)
        by = (plate_r - 4) * math.sin(a)
        hole = C(h + 2, BOLT_D / 2 + 0.15, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 减重孔
    for i in range(3):
        a = math.radians(i * 120 + 60)
        px = (plate_r / 2 + 10) * math.cos(a)
        py = (plate_r / 2 + 10) * math.sin(a)
        light = C(h + 2, 12, 32)
        light = light.translate([px, py, 0])
        plate = plate - light

    save(plate, "side_plate.stl")


# ============================================================
# Part 5: Stator Holder（管内定子固定座）
# ============================================================
def make_stator_holder():
    """
    管内电机定子固定座：
    - 防止电机定子随外壳一起旋转
    - 通过管壁螺栓固定
    """
    stator_d = 35
    stator_inner = 30
    h = 10

    body = C(h, stator_d) - C(h + 0.4, stator_inner)
    body = body - C(h + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)

    # 法兰（伸出管壁外）
    flange = Manifold.cube((stator_d + 20, stator_d + 20, 3), center=True)
    flange = flange.translate([0, 0, -h / 2 - 1.5])
    body = body + flange

    # 法兰 M4 孔（4 个）
    for i in range(4):
        a = math.radians(i * 90)
        hx = 12 * math.cos(a)
        hy = 12 * math.sin(a)
        hole = C(4, MOTOR_HOLE_D / 2 + 0.1, 16)
        hole = hole.translate([hx, hy, -h / 2 - 1.5])
        body = body - hole

    save(body, "stator_holder.stl")


# ============================================================
# Part 6: Bridge Rib（桥接筋 — 连接相邻电机座）
# ============================================================
def make_bridge_rib():
    """
    独立桥接筋：
    - 两端连接到相邻电机座的外缘
    - 跨过管外壁
    - 保持电机座之间刚性
    """
    rib_l = 60  # 长度
    rib_w = RIB_W
    rib_t = RIB_T

    body = Manifold.cube((rib_l, rib_w, rib_t), center=True)

    # 两端 M5 螺栓孔
    for x_off in [-rib_l / 2 + 8, rib_l / 2 - 8]:
        hole = C(rib_t + 2, BOLT_D / 2 + 0.15, 16)
        hole = hole.translate([x_off, 0, 0])
        body = body - hole

    save(body, "bridge_rib.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v3: 加电机辐条座（参考图橙色件）")
    print("=" * 50)

    make_launch_tube()
    make_motor_cradle()  # ★ 新增核心件
    make_motor_can()
    make_side_plate()
    make_stator_holder()
    make_bridge_rib()

    print(f"\n✓ 6 个零件 → {OUTPUT_DIR}/")
    print(f"\n打印数量:")
    print(f"  launch_tube:    1（管壁带 3 大圆孔 + 螺栓孔）")
    print(f"  motor_cradle:   3 ★（辐条轮电机座，参考图橙色件）")
    print(f"  motor_can:      3（电机外壳套，3 道 V 槽）")
    print(f"  side_plate:     2（端板）")
    print(f"  stator_holder:  3（管内定子固定座）")
    print(f"  bridge_rib:     3（连接相邻 cradle）")


if __name__ == "__main__":
    export_all()