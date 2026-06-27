"""
Football Launcher — Monocoque Shell (Focused Refinement)
单一零件深化设计：管体 + 3 个径向穿孔 + 电机凸台 + 桥接筋

设计要点：
1. 管壁厚足够承受发射反冲
2. 端口周边加筋补强（消除薄壁应力集中）
3. 电机轴承位精确（公差 0.3mm）
4. 线槽集成到底部
5. 对开面避开电机位和端口
6. 可直接 FDM 打印（侧放，分模面向上）
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
BALL_R = BALL_D / 2              # 110mm

# 6374 外转子电机
MOTOR_OD = 63
MOTOR_OR = MOTOR_OD / 2          # 31.5mm
MOTOR_LEN = 74
# 电机定子外径（深沟球轴外径，电机内部非旋转部分）
STATOR_D = 22
STATOR_R = STATOR_D / 2
MOTOR_SHAFT_D = 8
MOTOR_BOLT_D = 4
MOTOR_BOLT_PCD = 31              # 安装孔中心圆

# 接触几何
# 球面 R=110，电机外 R=31.5，接触时电机中心距球心 141.5mm
# 但电机外壳穿过管壁 → 端口中心 = TUBE_OR 上
MOTOR_CENTER_R = BALL_R + MOTOR_OR   # 141.5mm

# 发射管
TUBE_OR = 150                    # mm（管外半径）
TUBE_IR = BALL_R + 3             # 113mm（球通过）
TUBE_LEN = 140                   # mm

# 端口
PORT_D = MOTOR_OD + 6            # 69mm（电机穿过 + 间隙）
PORT_R = PORT_D / 2              # 34.5mm

# 电机凸台（卡座）
BOSS_LEN = MOTOR_LEN + 10        # 84mm（容纳电机+余量）
BOSS_THICK = SHELL_WALL = 4

# 装配间隙
GAP = 0.3

# 螺栓
M4 = 4
M5 = 5
M3 = 3

SEGMENTS = 96
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)), )) + "/stls"


# ============================================================
# CSG 工具
# ============================================================
def C(h, r_bot, r_top=None, n=SEGMENTS):
    if r_top is None: r_top = r_bot
    return Manifold.cylinder(h, r_bot, r_top, n)

def R(h, r_out, r_in, n=SEGMENTS):
    return C(h, r_out, n=n) - C(h + 0.4, r_in, n=n)

def B(w, d, h):
    return Manifold.cube((w, d, h), center=True)

def cone(r1, r2, h, n=SEGMENTS):
    return Manifold.cone(r1, r2, h)

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
            n_ = np.cross(p1 - p0, p2 - p0)
            nl = np.linalg.norm(n_)
            n_ = n_ / nl if nl > 0 else [0, 0, 1]
            fh.write(struct.pack('<3f', *n_))
            fh.write(struct.pack('<3f', *p0))
            fh.write(struct.pack('<3f', *p1))
            fh.write(struct.pack('<3f', *p2))
            fh.write(struct.pack('<H', 0))
    print(f"  ✓ {name} — {len(f)} faces, {os.path.getsize(path)//1024}KB")


# ============================================================
# Monocoque Shell（一体壳体 — 深化版）
# ============================================================
def make_monocoque_shell():
    """
    一体壳体结构：
    ┌──────────────────────────────────────┐
    │   管体 + 端口 + 凸台 + 筋 + 线槽       │
    │                                       │
    │        ╭─电机1─╮    ╭─电机3─╮         │
    │       │  6374  │    │  6374  │        │
    │       ╰────────╯    ╰────────╯         │
    │              ╭─电机2─╮                 │
    │             │  6374  │                │
    │             ╰────────╯                 │
    └──────────────────────────────────────┘

    装配顺序：
    1. 打印 2 个半壳（对开）
    2. 卡入管体（管子本身是独立件）
    3. 嵌入 3 个 6374 电机
    4. 用 M4 螺栓锁紧电机
    5. 合体两半，螺栓拧紧
    """

    # ===========================================================
    # 1. 主管体（管子外壁，从内向外建）
    # ===========================================================
    # 设计选择：管体是个完整圆筒，凸台是外挂的
    # 对开面：沿 X 轴平面切（避开 3 个电机位的角度）

    # 主管（厚壁圆筒）
    shell = R(TUBE_LEN, TUBE_OR, TUBE_IR)

    # ===========================================================
    # 2. 3 个电机端口（径向穿过管壁）
    # ===========================================================
    for i in range(3):
        angle_deg = i * 120
        rad = math.radians(angle_deg)

        # ---- 端口中心（位于管壁中线上） ----
        # 端口要在径向贯穿：从管外壁到管内壁
        port_axis_len = TUBE_OR - TUBE_IR + 4   # 长度 = 壁厚 + 微小余量
        port_axis_mid = (TUBE_OR + TUBE_IR) / 2  # 端口中点位于管壁中心

        # 端口圆柱（沿径向轴线）
        port = C(port_axis_len + 4, PORT_R)
        # 旋转使轴线沿径向
        port = port.rotate([math.pi / 2, 0, 0])
        # 旋转到 120° 位置
        port = port.rotate([0, 0, rad])
        # 移到管壁上
        port = port.translate([
            port_axis_mid * math.cos(rad),
            port_axis_mid * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell - port

        # ---- 端口倒角（管外壁侧，避免应力集中） ----
        chamfer_outer = C(6, PORT_R + 4) - C(6.4, PORT_R)
        chamfer_outer = chamfer_outer.rotate([math.pi / 2, 0, 0])
        chamfer_outer = chamfer_outer.rotate([0, 0, rad])
        chamfer_outer = chamfer_outer.translate([
            (TUBE_OR - 3) * math.cos(rad),
            (TUBE_OR - 3) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell - chamfer_outer

        # ---- 端口倒角（管内壁侧，避免应力集中 + 球通过顺畅） ----
        chamfer_inner = C(6, PORT_R + 2) - C(6.4, PORT_R)
        chamfer_inner = chamfer_inner.rotate([math.pi / 2, 0, 0])
        chamfer_inner = chamfer_inner.rotate([0, 0, rad])
        chamfer_inner = chamfer_inner.translate([
            (TUBE_IR + 3) * math.cos(rad),
            (TUBE_IR + 3) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell - chamfer_inner

        # ---- 电机凸台（端口外围加厚卡座） ----
        # 卡座内径匹配电机外壳（带 0.3mm 间隙）
        cradle_r = MOTOR_OR + GAP     # 31.8mm
        cradle_wall = SHELL_WALL      # 4mm
        cradle_or = cradle_r + cradle_wall  # 35.8mm

        # 凸台从端口中心沿径向外延伸
        boss = C(BOSS_LEN, cradle_or) - C(BOSS_LEN + 0.4, cradle_r)
        boss = boss.rotate([math.pi / 2, 0, 0])
        boss = boss.rotate([0, 0, rad])
        boss = boss.translate([
            (TUBE_OR + BOSS_LEN / 2 - 4) * math.cos(rad),
            (TUBE_OR + BOSS_LEN / 2 - 4) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell + boss

        # ---- 电机定子轴承位（精确支撑电机非旋转部分） ----
        # 6374 的定子轴是中间穿过，外壳旋转
        # 我们需要一个"止挡"防止电机被拉出
        # 凸台远端做一个内凸台，匹配电机定子
        # 用更小圆周套在端口内侧，限制电机最大插入深度
        bearing_h = 8
        bearing = C(bearing_h, STATOR_R + GAP + 2) - C(bearing_h + 0.4, STATOR_R - 2)
        bearing = bearing.rotate([math.pi / 2, 0, 0])
        bearing = bearing.rotate([0, 0, rad])
        bearing = bearing.translate([
            (TUBE_IR + 5) * math.cos(rad),
            (TUBE_IR + 5) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell + bearing

        # ---- 电机固定 M4 螺栓孔（凸台端面，4 个 90°） ----
        bolt_r = MOTOR_BOLT_PCD / 2  # 15.5mm
        for bi in range(4):
            bolt_angle = math.radians(bi * 90)
            # 螺栓位置：在电机定子端面，径向穿透
            screw = C(MOTOR_LEN / 2 + 6, M4 / 2 + 0.1)
            screw = screw.rotate([math.pi / 2, 0, 0])
            screw = screw.rotate([0, 0, bolt_angle])
            screw = screw.translate([
                (TUBE_OR + BOSS_LEN / 2) * math.cos(rad) + bolt_r * math.cos(rad + bolt_angle),
                (TUBE_OR + BOSS_LEN / 2) * math.sin(rad) + bolt_r * math.sin(rad + bolt_angle),
                TUBE_LEN / 2
            ])
            shell = shell - screw

        # ===========================================================
        # 3. 桥接筋（卡座 ↔ 管体，加强刚性）
        # ===========================================================
        # 每个卡座 3 根筋（中间 1 根 + 两侧各 1 根，与下一个卡座连接）
        # 中间筋：从管壁到卡座的中部
        bridge_mid_w = 8
        bridge_mid_h = TUBE_LEN - 30
        bridge_mid = B(bridge_mid_w, TUBE_OR * 0.55, bridge_mid_h)
        bridge_mid = bridge_mid.rotate([0, 0, rad])
        bridge_mid = bridge_mid.translate([
            (TUBE_OR * 0.45) * math.cos(rad),
            (TUBE_OR * 0.45) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell + bridge_mid

        # 两侧斜筋：连接到相邻的卡座
        for side in [-1, 1]:
            # 偏移角度（向相邻卡座倾斜）
            neighbor_angle = rad + side * math.radians(120)
            # 实际筋的角度：在两个卡座中间
            rib_angle = rad + side * math.radians(60)
            # 筋从当前位置延伸到管壁
            rib_w = 6
            rib_l = TUBE_OR * 0.5
            rib_h = bridge_mid_h
            rib = B(rib_w, rib_l, rib_h)
            rib = rib.rotate([0, 0, rib_angle])
            # 放置位置：筋中心在管壁和卡座之间
            rib_mid_dist = TUBE_OR * 0.5
            rib = rib.translate([
                rib_mid_dist * math.cos(rib_angle),
                rib_mid_dist * math.sin(rib_angle),
                TUBE_LEN / 2
            ])
            shell = shell + rib

        # ===========================================================
        # 4. 线槽（卡座底部，电机线走线）
        # ===========================================================
        # 沿管体轴向的浅槽，从卡座底部到管体底部
        # 槽宽 8mm，深 5mm
        wire_slot_w = 10
        wire_slot_d = 6
        wire_slot_l = 30
        wire_slot = B(wire_slot_w, wire_slot_d, wire_slot_l)
        wire_slot = wire_slot.rotate([0, 0, rad])
        wire_slot = wire_slot.translate([
            (TUBE_OR - wire_slot_d / 2) * math.cos(rad),
            (TUBE_OR - wire_slot_d / 2) * math.sin(rad),
            15  # 靠近管体底部
        ])
        shell = shell - wire_slot

        # 线槽口（圆形，M16 防水接头孔位）
        grommet = C(wire_slot_d, 5)
        grommet = grommet.rotate([math.pi / 2, 0, 0])
        grommet = grommet.rotate([0, 0, rad])
        grommet = grommet.translate([
            (TUBE_OR + 2) * math.cos(rad),
            (TUBE_OR + 2) * math.sin(rad),
            15
        ])
        shell = shell - grommet

    # ===========================================================
    # 5. 合体法兰（对开面）
    # ===========================================================
    # 对开面：沿 X 轴（避开 3 个 120° 电机位中的 0° 位附近）
    # 法兰环从管外壁向外延伸
    flange_or = TUBE_OR + 8
    flange_w = 8  # 法兰宽度
    for z in [flange_w / 2, TUBE_LEN - flange_w / 2]:
        flange = R(flange_w, flange_or, TUBE_OR)
        flange = flange.translate([0, 0, z])
        shell = shell + flange

    # 合体螺栓孔（每端 8 个 M5）
    for z in [flange_w / 2, TUBE_LEN - flange_w / 2]:
        for i in range(8):
            a = math.radians(i * 45)
            bx = (TUBE_OR + 4) * math.cos(a)
            by = (TUBE_OR + 4) * math.sin(a)
            hole = C(flange_w + 2, M5 / 2 + 0.15)
            hole = hole.translate([bx, by, z])
            shell = shell - hole

    # 定位销孔（每端 2 个，对称）
    for z in [flange_w / 2, TUBE_LEN - flange_w / 2]:
        for a_deg in [22.5, 202.5]:
            a = math.radians(a_deg)
            px = (TUBE_OR + 4) * math.cos(a)
            py = (TUBE_OR + 4) * math.sin(a)
            pin = C(flange_w + 2, 2.5)
            pin = pin.translate([px, py, z])
            shell = shell - pin

    # ===========================================================
    # 6. 对开面切割（沿 Y 轴平面切两半）
    # ===========================================================
    # 切掉 y < 0 的部分（保留上半 y >= 0）
    # 用一个大 box 做减
    cut_box = B(flange_or * 2, flange_or * 2, TUBE_LEN + 10)
    cut_box = cut_box.translate([0, -flange_or - 1, TUBE_LEN / 2])
    shell = shell - cut_box

    save(shell, "monocoque_shell.stl")


# ============================================================
# 导出
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 55)
    print("Football Launcher — Monocoque Shell (Focused Design)")
    print("=" * 55)
    print(f"Ball:      {BALL_D}mm (R={BALL_R}mm)")
    print(f"Tube:      {TUBE_IR*2}mm ID / {TUBE_OR*2}mm OD")
    print(f"Wall:      {(TUBE_OR - TUBE_IR):.0f}mm")
    print(f"Port:      {PORT_D}mm diameter")
    print(f"Cradle:    {MOTOR_OR*2+GAP*2:.1f}mm ID, {BOSS_LEN}mm deep")
    print(f"Motor:     6374 × 3 @ 120°")
    print(f"Length:    {TUBE_LEN}mm")
    print(f"Split:     along Y plane (Y >= 0)")
    print()

    make_monocoque_shell()

    print(f"\n✓ {OUTPUT_DIR}/monocoque_shell.stl")
    print(f"\n打印:")
    print(f"  1. FDM 打印（侧放，分模面向下）")
    print(f"  2. PETG/ABS，层高 0.2mm，填充 40%+")
    print(f"  3. 打印 2 件，对开合体")
    print(f"\n装配:")
    print(f"  1. 卡入外购管子（PVC/碳纤维可选）")
    print(f"  2. 从管外壁塞入 3 个 6374 电机")
    print(f"  3. M4 螺栓穿过凸台端面锁紧电机")
    print(f"  4. 电机线走线槽，从底部圆孔引出")
    print(f"  5. 两半合拢，M5 螺栓 + 定位销固定")


if __name__ == "__main__":
    export_all()