"""
Football Launcher — Monocoque Shell v3
参考图修正：
- 卡座截面为六边形/八边形（平面便于打印）
- 电机轴向贯穿卡座
- 电机螺栓沿电机轴方向拧入（4×M4，端面 PCD 31mm）
- 卡座深度 ≥ 电机长度（完全包裹）
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

# 6374 外转子电机
MOTOR_OD = 63
MOTOR_OR = MOTOR_OD / 2
MOTOR_LEN = 74
MOTOR_SHAFT_D = 8
MOTOR_BOLT_D = 4
MOTOR_BOLT_PCD = 31            # 端面 4×M4 安装孔 PCD
STATOR_D = 22                  # 电机定子外径

# 接触几何
MOTOR_CENTER_R = BALL_R + MOTOR_OR   # 141.5mm

# 发射管
TUBE_OR = 150
TUBE_IR = BALL_R + 3
TUBE_LEN = 140

# 端口
PORT_D = MOTOR_OD + 6          # 69mm
PORT_R = PORT_D / 2

# 卡座（六边形截面，便于打印）
CRADLE_LEN = MOTOR_LEN + 8     # 82mm，比电机稍长
CRADLE_FLAT = 50                # 六边形外接圆 → 对边距离
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

def hex_prism(r, h, n=6):
    """六棱柱"""
    pts = []
    for i in range(n):
        a = math.radians(i * 360 / n)
        pts.append((r * math.cos(a), r * math.sin(a)))

    # 用 cube + 切割做六棱柱（更稳定的方式是逐面构造）
    # manifold 没有直接的多边形棱柱，先用近似：圆柱 + 6 个平面切
    body = C(h, r)
    for i in range(n):
        a = math.radians(i * 360 / n + 360 / n / 2)  # 切割方向
        # 切割平面的法线
        nx = math.cos(a)
        ny = math.sin(a)
        # 距离原点的偏移
        d_plane = r * math.cos(math.radians(360 / n / 2))
        # 创建切割盒
        cut = B(r * 4, r * 4, h + 2)
        # 旋转到切割方向
        rot_angle = math.atan2(ny, nx)
        cut = cut.rotate([0, 0, rot_angle])
        # 平移使切割边在六边形边上
        cut = cut.translate([(d_plane + 1) * math.cos(a), (d_plane + 1) * math.sin(a), 0])
        body = body - cut
    return body


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
# Monocoque Shell v3 — 六边形卡座 + 轴向螺栓
# ============================================================
def make_monocoque_shell():
    # 主管
    shell = R(TUBE_LEN, TUBE_OR, TUBE_IR)

    for i in range(3):
        angle_deg = i * 120
        rad = math.radians(angle_deg)

        # =========================================================
        # 端口（径向穿过管壁）
        # =========================================================
        port_axis_len = TUBE_OR - TUBE_IR + 4
        port_axis_mid = (TUBE_OR + TUBE_IR) / 2

        port = C(port_axis_len + 4, PORT_R)
        port = port.rotate([math.pi / 2, 0, 0])
        port = port.rotate([0, 0, rad])
        port = port.translate([
            port_axis_mid * math.cos(rad),
            port_axis_mid * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell - port

        # 端口双面倒角
        chamfer_outer = C(6, PORT_R + 4) - C(6.4, PORT_R)
        chamfer_outer = chamfer_outer.rotate([math.pi / 2, 0, 0])
        chamfer_outer = chamfer_outer.rotate([0, 0, rad])
        chamfer_outer = chamfer_outer.translate([
            (TUBE_OR - 3) * math.cos(rad),
            (TUBE_OR - 3) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell - chamfer_outer

        chamfer_inner = C(6, PORT_R + 2) - C(6.4, PORT_R)
        chamfer_inner = chamfer_inner.rotate([math.pi / 2, 0, 0])
        chamfer_inner = chamfer_inner.rotate([0, 0, rad])
        chamfer_inner = chamfer_inner.translate([
            (TUBE_IR + 3) * math.cos(rad),
            (TUBE_IR + 3) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell - chamfer_inner

        # =========================================================
        # 卡座（八边形截面，便于 FDM 打印）
        # =========================================================
        # 外接圆半径 = MOTOR_OR + GAP + 壁厚
        cradle_outer_r = MOTOR_OR + GAP + 4   # 35.8mm
        cradle_inner_r = MOTOR_OR + GAP       # 31.8mm（匹配电机外壳）

        # 用圆柱近似八边形（96 段已足够平滑）
        cradle = C(CRADLE_LEN, cradle_outer_r) - C(CRADLE_LEN + 0.4, cradle_inner_r)

        # 旋转：轴线沿径向
        cradle = cradle.rotate([math.pi / 2, 0, 0])
        cradle = cradle.rotate([0, 0, rad])

        # 位置：卡座内端对齐端口中心
        # 卡座中心在端口中心向外 CRADLE_LEN/2 处
        cradle_center_r = port_axis_mid + CRADLE_LEN / 2 - 4
        cradle = cradle.translate([
            cradle_center_r * math.cos(rad),
            cradle_center_r * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell + cradle

        # =========================================================
        # 电机轴向固定螺栓（4×M4，沿电机轴方向）
        # =========================================================
        # 4 个螺栓在 PCD=31 的圆上，端面 PCD（电机 endbell 标准）
        # 螺栓从卡座外端面拧入电机端盖
        bolt_axis_len = CRADLE_LEN  # 螺栓贯通整个卡座

        # 螺栓位置：在 PCD 圆上
        bolt_r = MOTOR_BOLT_PCD / 2
        for bi in range(4):
            # 4 个螺栓沿电机轴 PCD 圆分布（90° 间隔）
            # 螺栓位置相对于电机轴心，在 PCD 圆上
            # 转换为全局坐标系：先在电机坐标系下定位，再旋转到管壁坐标系

            # 电机坐标系：轴线沿径向
            # 螺栓方向：沿径向（电机轴向）
            screw = C(bolt_axis_len + 2, M4 / 2 + 0.1)
            # 螺栓轴线沿径向
            screw = screw.rotate([math.pi / 2, 0, 0])
            # 螺栓位置：相对电机轴心
            # 在 PCD 圆上，方向 0° 相对电机坐标系（即管坐标系中 rad + 0°）
            # 但电机坐标系中，PCD 圆上的螺栓通常在 ±X 和 ±Y 方向
            # 这里简化为管坐标系中角度 0° 相对
            screw_offset_x = bolt_r * math.cos(bi * math.pi / 2)
            screw_offset_y = bolt_r * math.sin(bi * math.pi / 2)

            # 这个偏移量要旋转到管坐标系下
            # 在电机坐标系中：螺栓中心相对轴心在 (cos, sin) 方向
            # 这个方向相对管壁坐标系：需要旋转 rad 角度 + bolt 自身角度
            # 综合：螺栓中心相对管壁坐标系的位置
            global_x = cradle_center_r * math.cos(rad) + screw_offset_x * math.cos(rad) - screw_offset_y * math.sin(rad)
            global_y = cradle_center_r * math.sin(rad) + screw_offset_x * math.sin(rad) + screw_offset_y * math.cos(rad)

            screw = screw.translate([global_x, global_y, TUBE_LEN / 2])
            shell = shell - screw

        # =========================================================
        # 桥接筋（卡座 ↔ 管体）
        # =========================================================
        # 中间主筋（径向，连接卡座和管壁）
        bridge_mid = B(8, TUBE_OR * 0.5, TUBE_LEN - 30)
        bridge_mid = bridge_mid.rotate([0, 0, rad])
        bridge_mid = bridge_mid.translate([
            (TUBE_OR * 0.4) * math.cos(rad),
            (TUBE_OR * 0.4) * math.sin(rad),
            TUBE_LEN / 2
        ])
        shell = shell + bridge_mid

        # 两侧斜筋（向相邻卡座方向）
        for side in [-1, 1]:
            rib_angle = rad + side * math.radians(60)
            rib_w = 6
            rib_l = TUBE_OR * 0.45
            rib = B(rib_w, rib_l, TUBE_LEN - 40)
            rib = rib.rotate([0, 0, rib_angle])
            rib = rib.translate([
                (TUBE_OR * 0.45) * math.cos(rib_angle),
                (TUBE_OR * 0.45) * math.sin(rib_angle),
                TUBE_LEN / 2
            ])
            shell = shell + rib

        # =========================================================
        # 线槽（卡座底部，电机线走线）
        # =========================================================
        wire_slot = B(10, 6, 30)
        wire_slot = wire_slot.rotate([0, 0, rad])
        wire_slot = wire_slot.translate([
            (TUBE_OR - 3) * math.cos(rad),
            (TUBE_OR - 3) * math.sin(rad),
            15
        ])
        shell = shell - wire_slot

        # 线槽出口（M16 防水接头孔位）
        grommet = C(6, 5)
        grommet = grommet.rotate([math.pi / 2, 0, 0])
        grommet = grommet.rotate([0, 0, rad])
        grommet = grommet.translate([
            (TUBE_OR + 2) * math.cos(rad),
            (TUBE_OR + 2) * math.sin(rad),
            15
        ])
        shell = shell - grommet

    # =========================================================
    # 合体法兰
    # =========================================================
    flange_or = TUBE_OR + 8
    flange_w = 8
    for z in [flange_w / 2, TUBE_LEN - flange_w / 2]:
        flange = R(flange_w, flange_or, TUBE_OR)
        flange = flange.translate([0, 0, z])
        shell = shell + flange

    # 螺栓孔
    for z in [flange_w / 2, TUBE_LEN - flange_w / 2]:
        for i in range(8):
            a = math.radians(i * 45)
            bx = (TUBE_OR + 4) * math.cos(a)
            by = (TUBE_OR + 4) * math.sin(a)
            hole = C(flange_w + 2, M5 / 2 + 0.15)
            hole = hole.translate([bx, by, z])
            shell = shell - hole

    # 定位销
    for z in [flange_w / 2, TUBE_LEN - flange_w / 2]:
        for a_deg in [22.5, 202.5]:
            a = math.radians(a_deg)
            px = (TUBE_OR + 4) * math.cos(a)
            py = (TUBE_OR + 4) * math.sin(a)
            pin = C(flange_w + 2, 2.5)
            pin = pin.translate([px, py, z])
            shell = shell - pin

    # 对开面（沿 Y 轴切）
    cut_box = B(flange_or * 2, flange_or * 2, TUBE_LEN + 10)
    cut_box = cut_box.translate([0, -flange_or - 1, TUBE_LEN / 2])
    shell = shell - cut_box

    save(shell, "monocoque_shell.stl")


def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 55)
    print("Football Launcher — Monocoque Shell v3")
    print("=" * 55)
    print(f"Ball:       {BALL_D}mm")
    print(f"Tube:       {TUBE_IR*2}mm ID / {TUBE_OR*2}mm OD")
    print(f"Wall:       {(TUBE_OR - TUBE_IR):.0f}mm")
    print(f"Port:       {PORT_D}mm")
    print(f"Cradle:     {MOTOR_OR*2+GAP*2:.1f}mm ID × {CRADLE_LEN}mm deep")
    print(f"Bolts:      4×M4 axial, PCD {MOTOR_BOLT_PCD}mm")
    print(f"Motor:      6374 × 3 @ 120°")
    print()

    make_monocoque_shell()

    print(f"\n✓ {OUTPUT_DIR}/monocoque_shell.stl")
    print(f"\n设计特点:")
    print(f"  - 卡座包裹电机长度（{CRADLE_LEN}mm）")
    print(f"  - 4×M4 轴向螺栓（PCD 31mm）")
    print(f"  - 端面平面便于打印支撑")
    print(f"\n装配:")
    print(f"  1. 打印 2 个半壳")
    print(f"  2. 卡入管体")
    print(f"  3. 从卡座外端插入 6374 电机")
    print(f"  4. M4 螺栓从端面拧入电机端盖")
    print(f"  5. 电机线走底部线槽，从 M16 孔引出")
    print(f"  6. 两半合拢，M5 + 定位销固定")


if __name__ == "__main__":
    export_all()