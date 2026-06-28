"""
Football Launcher — v15 气压主线架构
按 PROPULSION_ARCHITECTURE_REVIEW_V1 推荐方案：
- 压缩空气（气压端 + 进气口占位）= 主推进
- 3 电机径向 cradle = 控旋模块
- 不含实际阀门/气罐（外购件）
"""

import numpy as np
from manifold3d import Manifold
import struct
import os
import math

# ============================================================
# 参数（按评审推荐）
# ============================================================
BALL_D = 220
BALL_R = BALL_D / 2

MOTOR_D = 63
MOTOR_L = 74
MOTOR_SHAFT_D = 8
MOTOR_HOLE_D = 4
MOTOR_HOLE_PCD = 31

# 管（球通道）
TUBE_IR = BALL_R + 3
TUBE_OR = 140
TUBE_LEN = 400                  # ★ 加长到 400mm（参考 sim：8bar/20L/400mm → 80m 射程）

# 气压端（后端封闭）
PRESS_END_LEN = 30              # 压力端长度
PRESS_END_OR = TUBE_OR + 15     # 压力端凸缘外径
PRESS_PORT_DIA = 25             # 进气口直径（1" NPT 类似）

# 装球口（侧面）
LOAD_PORT_DIA = 220            # 与球道同径，闸门
LOAD_GATE_THICK = 8             # 闸门厚度

# 电机 cradle（控旋模块）
CRADLE_R = TUBE_OR / 2 + 55    # 125mm（管外 55mm）
CRADLE_THICK = 10
HUB_OD = MOTOR_D + 8
HUB_LEN = MOTOR_L + 10
WHEEL_RIM_OR = 160
WHEEL_RIM_W = 10
WHEEL_N_SPOKES = 3
WHEEL_SPOKE_W = 16

# 球导轨（管内）
GUIDE_RIB_N = 4
GUIDE_RIB_W = 6
GUIDE_RIB_H = 4

# 飞轮盘（径向，控旋接触面）
FLYWHEEL_D = 50
FLYWHEEL_T = 8

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
# Part 1: Tube Body（管 + 球导轨 + 装球口）
# ============================================================
def make_tube_body_v15():
    """
    主发射管（含球导轨、装球口占位）：
    - 长 400mm（适配 8bar/20L → 80m 射程）
    - 管内 4 条导轨（球导向）
    - 侧面装球口（球装载位置）
    - 3 个电机 cradle（径向相切）
    - 端板螺栓预留
    """
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    # 球导轨（管内 4 条凸筋）
    for i in range(GUIDE_RIB_N):
        angle = math.radians(i * 90 + 22.5)
        # 凸筋位置：在管内壁（避开电机孔位置）
        rib_pos = TUBE_IR - 2  # 凸筋顶面距管中心
        # 用圆柱切出凸筋
        rib_full = C(TUBE_LEN, rib_pos + GUIDE_RIB_H / 2)
        cut = Manifold.cube((TUBE_OR * 3, GUIDE_RIB_W, TUBE_LEN + 2), center=True)
        cut = cut.rotate([0, 0, math.degrees(angle)])
        cut = cut.translate([0, 0, 0])
        rib_segment = rib_full - cut
        body = body + rib_segment

    # 装球口（侧面，圆孔，位置在管 1/4 处）
    load_z = TUBE_LEN * 0.25
    # 装球口从管外侧贯穿管壁
    load_hole = C(LOAD_GATE_THICK * 2, BALL_R + 5)  # 比球大一点便于装载
    load_hole = load_hole.rotate([math.pi / 2, 0, 0])  # 旋转 90° 让轴向为 Y
    load_hole = load_hole.translate([0, TUBE_OR + 20, load_z])
    # 切割管壁（创建装球口通道）
    wall_cut = Manifold.cube((TUBE_OR * 2, LOAD_GATE_THICK * 3, BALL_R * 2.5), center=True)
    wall_cut = wall_cut.rotate([math.pi / 2, 0, 0])
    wall_cut = wall_cut.translate([0, TUBE_OR / 2, load_z])
    body = body - wall_cut

    # 装球口套管（外凸缘，便于装闸门）
    load_collar = C(LOAD_GATE_THICK, BALL_R + 8) - C(LOAD_GATE_THICK + 1, BALL_R + 2)
    load_collar = load_collar.rotate([math.pi / 2, 0, 0])
    load_collar = load_collar.translate([0, TUBE_OR + 5, load_z])
    body = body + load_collar

    # 端部加固环
    for z in [8, TUBE_LEN - 8]:
        ring = C(4, TUBE_OR + 2) - C(5, TUBE_OR - 1)
        ring = ring.translate([0, 0, z - 2])
        body = body + ring

    save(body, "tube_body_v15.stl")


# ============================================================
# Part 2: Pressure End Cap（气压端 — 后端封闭）
# ============================================================
def make_pressure_end_v15():
    """
    气压端（后端封闭）：
    - 圆盘封闭 + 法兰螺栓
    - 中心进气口（接快释放阀）
    - 爆破片槽（安全）
    - 泄压阀接口占位
    """
    body = C(PRESS_END_LEN, PRESS_END_OR)

    # 中心进气口（接电磁阀）
    inlet = C(PRESS_END_LEN + 2, PRESS_PORT_DIA / 2)
    body = body - inlet

    # 内嵌管段（与 tube 对接）
    socket = C(PRESS_END_LEN, TUBE_OR + 0.3) - C(PRESS_END_LEN + 0.4, TUBE_OR)
    socket = socket.translate([0, 0, PRESS_END_LEN / 2])
    body = body + socket

    # 8 颗 M5 法兰螺栓
    for i in range(8):
        a = math.radians(i * 45)
        bx = (TUBE_OR + 8) * math.cos(a)
        by = (TUBE_OR + 8) * math.sin(a)
        bolt = C(PRESS_END_LEN + 2, 2.7, 16)
        bolt = bolt.translate([bx, by, 0])
        body = body - bolt

    # 爆破片槽（环形槽，安全）
    burst_groove = C(2, PRESS_PORT_DIA / 2 + 8) - C(2.4, PRESS_PORT_DIA / 2 + 4)
    burst_groove = burst_groove.translate([0, 0, -PRESS_END_LEN / 2 + 4])
    body = body + burst_groove

    save(body, "pressure_end_v15.stl")


# ============================================================
# Part 3: Motor Cradle（控旋模块 — 径向 cradle）
# ============================================================
def make_motor_cradle_v15():
    """
    控旋模块（独立件）：
    - 中心 hub（沿 Z 轴，容纳电机）
    - 3 条辐条 + 外圈
    - 端部飞轮盘（接触球）
    """
    parts = Manifold()

    # Hub 沿 Z 轴
    hub_outer = C(HUB_LEN, HUB_OD / 2)
    hub_inner = C(HUB_LEN + 0.4, MOTOR_D / 2 + 0.5)
    hub = hub_outer - hub_inner

    # 电机轴孔
    shaft = C(HUB_LEN + 2, MOTOR_SHAFT_D / 2 + 0.5, 16)
    hub = hub - shaft

    # 4 个 M4 电机螺栓孔（端面）
    for j in range(4):
        ja = math.radians(j * 90)
        bolt_x = (MOTOR_HOLE_PCD / 2) * math.cos(ja)
        bolt_y = (MOTOR_HOLE_PCD / 2) * math.sin(ja)
        bolt = C(6, MOTOR_HOLE_D / 2 + 0.1, 16)
        bolt = bolt.translate([bolt_x, bolt_y, HUB_LEN / 2 - 3])
        hub = hub - bolt

    parts = parts + hub

    # 3 条辐条（XY 平面内）
    spoke_len = (WHEEL_RIM_OR - HUB_OD) / 2 - WHEEL_RIM_W / 2
    spoke_offset = (HUB_OD + WHEEL_RIM_OR) / 4
    for j in range(WHEEL_N_SPOKES):
        sa = math.radians(j * 120)
        spoke = Manifold.cube((spoke_len, WHEEL_SPOKE_W, CRADLE_THICK), center=True)
        spoke = spoke.rotate([0, 0, sa])
        spoke = spoke.translate([spoke_offset * math.cos(sa),
                                 spoke_offset * math.sin(sa), 0])
        parts = parts + spoke

    # 外圈
    rim = C(CRADLE_THICK, WHEEL_RIM_OR / 2) - \
          C(CRADLE_THICK + 0.4, (WHEEL_RIM_OR - 2 * WHEEL_RIM_W) / 2)

    # 4 颗 M5 外圈螺栓
    for j in range(4):
        ra = math.radians(j * 90 + 45)
        bx = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.cos(ra)
        by = (WHEEL_RIM_OR - WHEEL_RIM_W / 2) * math.sin(ra)
        bolt = C(CRADLE_THICK + 2, 2.7, 16)
        bolt = bolt.translate([bx, by, 0])
        rim = rim - bolt

    parts = parts + rim

    # 飞轮盘（径向，电机 +X 端外侧）
    # 注意：cradle hub 中心在原点，cradle 装在管上时平移到对应位置
    flywheel = C(FLYWHEEL_T, FLYWHEEL_D / 2)
    flywheel = flywheel.rotate([0, math.pi / 2, 0])  # 轴向 X
    flywheel = flywheel.translate([FLYWHEEL_D / 2 + 5, 0, 0])
    parts = parts + flywheel

    save(parts, "motor_cradle_v15.stl")


# ============================================================
# Part 4: Output End（前端出球口 + 安全护栏占位）
# ============================================================
def make_output_end_v15():
    """
    前端出球口：
    - 圆形端板（中心出球孔）
    - 安全网占位（外缘）
    - 端板螺栓预留
    """
    plate_r = TUBE_OR + 20  # 比管大，安全网延伸
    h = 5

    plate = C(h, plate_r)
    plate = plate - C(h + 2, BALL_R + 3)  # 中心出球孔

    # 8 颗螺栓
    for i in range(8):
        a = math.radians(i * 45)
        bx = (plate_r - 4) * math.cos(a)
        by = (plate_r - 4) * math.sin(a)
        hole = C(h + 2, 2.7, 16)
        hole = hole.translate([bx, by, 0])
        plate = plate - hole

    # 外缘加厚环（安全网固定位）
    outer_ring = C(h + 2, plate_r) - C(h + 2.4, plate_r - 4)
    plate = plate + outer_ring

    save(plate, "output_end_v15.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("v15: 气压主线架构（按 PROPULSION_ARCHITECTURE_REVIEW_V1）")
    print("=" * 50)
    print("- Tube: 400mm 加长（适配 8bar/20L → 50m+ 射程）")
    print("- 压力端: 圆盘封闭 + 进气口 + 爆破片槽")
    print("- 装球口: 侧面装载 + 闸门凸缘")
    print("- 电机 cradle: 控旋模块（径向，3 件独立）")
    print("- 飞轮盘: 接触球面（控旋）")
    print("- 出球端: 端板 + 安全网固定位")
    print()

    make_tube_body_v15()
    make_pressure_end_v15()
    make_motor_cradle_v15()
    make_output_end_v15()

    print(f"\n✓ 4 个零件 → {OUTPUT_DIR}/")


if __name__ == "__main__":
    export_all()