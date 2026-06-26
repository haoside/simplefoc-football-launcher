"""
Football Launcher 3D Printed Parts — 3 Motor, 120° Layout
标准5号足球 + 6374 电机 × 3，120° 环形排布
"""

import numpy as np
from stl import mesh
import os
import math

# ============================================================
# 参数
# ============================================================
BALL_DIA = 220
CHANNEL_ID = BALL_DIA + 5          # 225mm
MOTOR_DIA = 63
WALL = 4
FRAME_W = 80
ROLLER_DIA = 60
ROLLER_W = 20
ROLLER_BORE = 8
ARM_LEN = 120
ARM_W = 25
ARM_H = 8
N_MOTORS = 3
SEGMENTS = 48

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stls")


# ============================================================
# 工具函数
# ============================================================
def make_cylinder_faces(radius, height, n=SEGMENTS, z0=0):
    """实心圆柱三角面片"""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xs = radius * np.cos(angles)
    ys = radius * np.sin(angles)
    zt, zb = z0 + height, z0
    top = np.column_stack([xs, ys, np.full(n, zt)])
    bot = np.column_stack([xs, ys, np.full(n, zb)])
    ct = np.array([0.0, 0.0, zt])
    cb = np.array([0.0, 0.0, zb])
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append([ct, top[i], top[j]])
        faces.append([cb, bot[j], bot[i]])
        faces.append([top[i], bot[i], bot[j]])
        faces.append([top[i], bot[j], top[j]])
    return np.array(faces, dtype=np.float32)


def make_tube_faces(or_, ir, height, n=SEGMENTS, z0=0):
    """空心圆柱（管）"""
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    cos_a, sin_a = np.cos(angles), np.sin(angles)
    zt, zb = z0 + height, z0
    ot = np.column_stack([or_ * cos_a, or_ * sin_a, np.full(n, zt)])
    ob = np.column_stack([or_ * cos_a, or_ * sin_a, np.full(n, zb)])
    it = np.column_stack([ir * cos_a, ir * sin_a, np.full(n, zt)])
    ib = np.column_stack([ir * cos_a, ir * sin_a, np.full(n, zb)])
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.append([ot[i], ob[i], ob[j]])
        faces.append([ot[i], ob[j], ot[j]])
        faces.append([it[i], it[j], ib[j]])
        faces.append([it[i], ib[j], ib[i]])
        faces.append([ot[i], it[i], it[j]])
        faces.append([ot[i], it[j], ot[j]])
        faces.append([ob[i], ob[j], ib[j]])
        faces.append([ob[i], ib[j], ib[i]])
    return np.array(faces, dtype=np.float32)


def make_box_faces(w, h, d):
    """长方体"""
    x, y, z = w / 2, h / 2, d / 2
    v = np.array([
        [-x, -y, -z], [x, -y, -z], [x, y, -z], [-x, y, -z],
        [-x, -y, z],  [x, -y, z],  [x, y, z],  [-x, y, z]
    ], dtype=np.float32)
    tris = np.array([
        [0,3,1],[1,3,2],[4,5,7],[5,6,7],
        [0,1,5],[0,5,4],[2,3,7],[2,7,6],
        [0,4,7],[0,7,3],[1,2,6],[1,6,5]
    ])
    return v[tris]


def rotate_faces(faces, angle_deg, axis='z'):
    """绕指定轴旋转面片"""
    rad = math.radians(angle_deg)
    if axis == 'z':
        c, s = math.cos(rad), math.sin(rad)
        rot = np.array([[c,-s,0],[s,c,0],[0,0,1]], dtype=np.float32)
    elif axis == 'x':
        c, s = math.cos(rad), math.sin(rad)
        rot = np.array([[1,0,0],[0,c,-s],[0,s,c]], dtype=np.float32)
    elif axis == 'y':
        c, s = math.cos(rad), math.sin(rad)
        rot = np.array([[c,0,s],[0,1,0],[-s,0,c]], dtype=np.float32)
    else:
        return faces
    return (faces @ rot.T).astype(np.float32)


def translate_faces(faces, tx=0, ty=0, tz=0):
    """平移面片"""
    offset = np.array([tx, ty, tz], dtype=np.float32)
    return (faces + offset).astype(np.float32)


def save_stl(faces_array, filename):
    """保存 STL"""
    data = np.zeros(len(faces_array), dtype=[
        ('vectors', np.float32, (3, 3)),
        ('normals', np.float32, (3,)),
        ('attributes', np.uint8, (4,))
    ])
    data['vectors'] = faces_array
    m = mesh.Mesh(data)
    path = os.path.join(OUTPUT_DIR, filename)
    m.save(path)
    print(f"  ✓ {filename} — {len(m.vectors)} faces, {os.path.getsize(path)//1024}KB")


# ============================================================
# Part 1: Frame Main Body（主框架 — 三电机安装位）
# ============================================================
def make_frame():
    """
    主框架：空心圆管 + 3个电机安装座凸台
    120° 均匀分布，每个凸台带 M4 电机安装孔位
    """
    id_r = CHANNEL_ID / 2      # 112.5
    od_r = id_r + WALL         # 116.5
    hub_h = 30                  # 安装凸台高度
    hub_w = MOTOR_DIA + 20     # 凸台宽度
    hub_d = WALL * 3           # 凸台厚度

    # 主管
    tube = make_tube_faces(od_r, id_r, FRAME_W)

    all_faces = [tube]

    # 3 个电机安装凸台，120° 间隔
    for i in range(N_MOTORS):
        angle = i * 120  # 0°, 120°, 240°
        rad = math.radians(angle)

        # 凸台位置：从管外壁向外延伸
        cx = od_r * math.cos(rad)
        cy = od_r * math.sin(rad)

        # 凸台方块
        hub = make_box_faces(hub_w, hub_d, hub_h)
        # 移动到管壁外侧
        hub = translate_faces(hub, tx=cx, ty=cy, tz=FRAME_W / 2)
        all_faces.append(hub)

        # 安装孔标记柱（M4 螺丝位，4个，90° 分布）
        hole_r = MOTOR_PCD / 2 if hasattr(__builtins__, 'MOTOR_PCD') else 15
        for hi in range(4):
            h_angle = math.radians(hi * 90 + angle)
            hx = cx + hole_r * math.cos(h_angle)
            hy = cy + hole_r * math.sin(h_angle)
            hole = make_cylinder_faces(2, hub_d + 2, n=16, z0=FRAME_W / 2 - 1)
            hole = translate_faces(hole, tx=hx, ty=hy)
            # 用深色面标记（实际应做布尔减，这里用细柱标记位置）
            all_faces.append(hole)

    # 加固环（管外壁凸起，3条，对应电机位置）
    for i in range(N_MOTORS):
        angle = i * 120
        rad = math.radians(angle)
        ring_w = hub_w + 10
        ring = make_box_faces(ring_w, 6, FRAME_W)
        ring = translate_faces(ring,
            tx=(od_r + 3) * math.cos(rad),
            ty=(od_r + 3) * math.sin(rad))
        all_faces.append(ring)

    combined = np.vstack(all_faces)
    save_stl(combined, "frame_main.stl")


# ============================================================
# Part 2: Motor Mount Bracket（电机安装座 — 单个）
# ============================================================
def make_motor_mount():
    """
    电机安装座：圆柱夹具 + 法兰板
    夹持 6374 电机，通过螺丝固定到框架凸台
    """
    outer_r = MOTOR_DIA / 2 + WALL * 2   # 75.5
    inner_r = MOTOR_DIA / 2 - 0.5        # 31
    h = 25

    body = make_tube_faces(outer_r, inner_r, h, n=SEGMENTS)

    # 法兰板（安装到框架的面）
    flange_w = MOTOR_DIA + 30
    flange = make_box_faces(flange_w, flange_w + 20, WALL)
    flange = translate_faces(flange, tz=h / 2)

    # M4 电机安装孔标记
    hole_r = 15  # PCD/2
    for hi in range(4):
        h_angle = math.radians(hi * 90)
        hx = hole_r * math.cos(h_angle)
        hy = hole_r * math.sin(h_angle)
        hole = make_cylinder_faces(2.2, WALL + 2, n=16, z0=h / 2)
        hole = translate_faces(hole, tx=hx, ty=hy)
        flange = np.vstack([flange, hole])

    combined = np.vstack([body, flange])
    save_stl(combined, "motor_mount.stl")


# ============================================================
# Part 3: Roller Wheel（滚轮）
# ============================================================
def make_roller_wheel():
    """滚轮：装在电机轴上，V 槽抓球"""
    r_out = ROLLER_DIA / 2      # 30
    r_in = ROLLER_BORE / 2      # 4
    body = make_tube_faces(r_out, r_in, ROLLER_W, n=SEGMENTS)

    # V 槽（中间凹陷增加抓球力）
    groove_depth = 3
    groove_r_out = r_out - groove_depth
    groove = make_tube_faces(r_out + 0.1, groove_r_out, ROLLER_W - 6, n=SEGMENTS, z0=3)
    body = np.vstack([body, groove])

    save_stl(body, "roller_wheel.stl")


# ============================================================
# Part 4: Structural Arm（结构臂）
# ============================================================
def make_structural_arm():
    """连接臂：框架凸台 ↔ 电机座"""
    arm = make_box_faces(ARM_LEN, ARM_W, ARM_H)

    # 两端安装孔标记
    for x_off in [-ARM_LEN / 2 + 10, ARM_LEN / 2 - 10]:
        for y_off in [-ARM_W / 4, ARM_W / 4]:
            hole = make_cylinder_faces(2.8, ARM_H + 2, n=12, z0=-1)
            hole = translate_faces(hole, tx=x_off, ty=y_off)
            arm = np.vstack([arm, hole])

    save_stl(arm, "structural_arm.stl")


# ============================================================
# Part 5: Connector Flange（连接法兰）
# ============================================================
def make_connector_flange():
    """法兰环：螺丝连接框架对开面"""
    id_r = CHANNEL_ID / 2
    od_r = id_r + WALL
    flange_r = od_r + 12
    h = 8

    ring = make_tube_faces(flange_r, id_r, h, n=SEGMENTS)

    # M5 连接螺栓孔标记（8 个均布）
    bolt_r = od_r + 6
    for i in range(8):
        b_angle = math.radians(i * 45)
        bx = bolt_r * math.cos(b_angle)
        by = bolt_r * math.sin(b_angle)
        hole = make_cylinder_faces(2.8, h + 2, n=12, z0=-1)
        hole = translate_faces(hole, tx=bx, ty=by)
        ring = np.vstack([ring, hole])

    save_stl(ring, "connector_flange.stl")


# ============================================================
# Part 6: Motor Side Plate（电机侧盖板）
# ============================================================
def make_motor_side_plate():
    """
    侧盖板：固定电机轴端，增加刚性
    三角形板，3 个安装孔对应 3 个电机位
    """
    # 三角形轮廓
    r = CHANNEL_ID / 2 + WALL + 15  # 略大于框架外径
    pts = []
    for i in range(3):
        angle = math.radians(i * 120 + 90)  # 从顶部开始
        pts.append([r * math.cos(angle), r * math.sin(angle)])

    # 简化为圆形板（更容易打印）
    plate = make_cylinder_faces(r, 4, n=48)

    # 中心孔（球通过）
    center_hole = make_cylinder_faces(CHANNEL_ID / 2 - 5, 6, n=48)
    plate = np.vstack([plate, center_hole])

    # 3 个电机轴通过孔
    motor_r = CHANNEL_ID / 2 + WALL - 5
    for i in range(3):
        angle = math.radians(i * 120)
        mx = motor_r * math.cos(angle)
        my = motor_r * math.sin(angle)
        motor_hole = make_cylinder_faces(MOTOR_DIA / 2 + 3, 6, n=24, z0=-1)
        motor_hole = translate_faces(motor_hole, tx=mx, ty=my)
        plate = np.vstack([plate, motor_hole])

    save_stl(plate, "motor_side_plate.stl")


# ============================================================
# 导出全部
# ============================================================
def export_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Football Launcher — 3 Motor 120° Layout")
    print(f"通道: {CHANNEL_ID}mm | 电机: {MOTOR_DIA}mm × 3 @ 120°\n")

    make_frame()
    make_motor_mount()
    make_roller_wheel()
    make_structural_arm()
    make_connector_flange()
    make_motor_side_plate()

    print(f"\n✓ 6 个零件 STL → {OUTPUT_DIR}/")
    print(f"每种打印 2-3 份（框架 2 半，其余按需）")


if __name__ == "__main__":
    export_all()
