"""
Football Launcher 3D Interactive Display — Plotly HTML
- 3D 发射器（mesh）
- 球轨迹（3D 曲线）
- 控制面板（滑块、按钮）
- 5 种旋转模式切换
- 实时动画（球沿轨迹飞行）
"""

import numpy as np
from manifold3d import Manifold
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import os

# 物理参数
BALL_D = 0.22
BALL_R = BALL_D / 2
BALL_MASS = 0.43
G = 9.81
RHO = 1.225
CD = 0.25
BALL_AREA = math.pi * BALL_R ** 2
K_LAT = 0.42
K_VERT = 0.30

# 切向滚轮
CAN_R = 0.0315
MU = 0.5
MOTOR_EFF = 0.85
NORMAL_N = 30.0


# ============================================================
# 3D 发射器（manifold3d）
# ============================================================
def C(h, r):
    return Manifold.cylinder(h, r, r, 48)


def manifold_to_mesh(body):
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    return v, f


def build_launcher_meshes():
    """返回发射器各部件的 mesh (vertices, faces, name)"""
    meshes = []
    TUBE_LEN = 200
    TUBE_OR = TUBE_IR = BALL_R * 1000 + 3 + 8
    TUBE_OR = TUBE_IR + 8
    MOTOR_CENTER_R = BALL_R * 1000 - 1 + CAN_R * 1000

    # 管
    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)
    v, f = manifold_to_mesh(body)
    meshes.append(('Tube (球通道)', v, f, '#ff8c00', 0.9))

    # 3 个 cradle（径向）
    for i in range(3):
        angle = math.radians(i * 120)
        cradle_hub = C(74 + 10, 75/2) - C(74 + 10.4, 63/2 + 0.5)
        cradle_hub = cradle_hub.rotate([0, 0, angle * 180 / math.pi])
        cradle_hub = cradle_hub.translate([MOTOR_CENTER_R * math.cos(angle),
                                            MOTOR_CENTER_R * math.sin(angle),
                                            TUBE_LEN/2])
        spokes = Manifold()
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((30, 18, 10), center=True)
            spoke = spoke.rotate([0, 0, sa * 180 / math.pi])
            spoke = spoke.translate([MOTOR_CENTER_R * math.cos(angle) + 30 * math.cos(sa) * math.cos(angle),
                                     MOTOR_CENTER_R * math.sin(angle) + 30 * math.cos(sa) * math.sin(angle),
                                     TUBE_LEN/2])
            spokes = spokes + spoke
        rim = C(10, 80) - C(11, 70)
        rim = rim.rotate([0, math.pi/2, 0])
        rim = rim.translate([MOTOR_CENTER_R * math.cos(angle),
                             MOTOR_CENTER_R * math.sin(angle),
                             TUBE_LEN/2])
        cradle_combined = cradle_hub + spokes + rim
        v, f = manifold_to_mesh(cradle_combined)
        meshes.append((f'Cradle {i+1} ({i*120}°)', v, f, '#ff6600', 0.95))

    # 球
    ball = Manifold.sphere(BALL_R * 1000, 32)
    v, f = manifold_to_mesh(ball)
    meshes.append(('Ball 220mm', v, f, '#00cc00', 0.6))

    # 端板
    for z_sign in [-1, 1]:
        plate = C(6, TUBE_OR + 5) - C(8, BALL_R * 1000 + 3)
        plate = plate.translate([0, 0, z_sign * (TUBE_LEN / 2 + 3)])
        v, f = manifold_to_mesh(plate)
        meshes.append((f'Plate {z_sign}', v, f, '#1f77b4', 0.7))

    return meshes


# ============================================================
# 球轨迹模拟
# ============================================================
def simulate_trajectory(rpms, angle_deg, propel_mode):
    """rpms = (w1, w2, w3), 返回 x, y, z 轨迹（米）"""
    avg_rpm = sum(rpms) / 3
    can_v = avg_rpm / 60 * (2 * math.pi * CAN_R)

    # 出膛速度
    if propel_mode == 'pneumatic_8bar':
        v0 = 63.0
    elif propel_mode == 'pneumatic_50m':
        v0 = 90.0
    elif propel_mode == 'tangent_friction':
        slip = min(1.0, MU * math.sqrt(NORMAL_N / 30.0))
        v0 = can_v * slip * MOTOR_EFF
    else:
        v0 = 25.0

    # 旋转（差速 → 自旋）
    deltas = [r - avg_rpm for r in rpms]
    spin_rps = sum(abs(d) for d in deltas) / 3 / 60 * (CAN_R / BALL_R) * MOTOR_EFF

    # 自旋方向
    spin_lr = 0.0
    spin_ud = 0.0
    if deltas[0] > 50:
        spin_ud = +1.0  # topspin
    elif deltas[0] < -50:
        spin_ud = -1.0  # backspin
    if deltas[1] > 50:
        spin_lr = -1.0
    elif deltas[2] > 50:
        spin_lr = +1.0

    a = math.radians(angle_deg)
    x = y = 0.0
    z = 0.30
    vx = v0 * math.cos(a)
    vy = 0.0
    vz = v0 * math.sin(a)

    dt = 0.015
    t = 0.0
    xs, ys, zs, ts = [x], [y], [z], [t]
    ays = spin_lr * K_LAT * spin_rps
    azs = -spin_ud * K_VERT * spin_rps

    for _ in range(150):
        v = math.sqrt(vx**2 + vy**2 + vz**2)
        if v < 0.1:
            break
        drag = 0.5 * RHO * CD * BALL_AREA * v * v / BALL_MASS
        if v > 1e-6:
            vx -= drag * vx / v * dt
            vy -= drag * vy / v * dt
            vz -= drag * vz / v * dt
        vy += ays * dt
        vz += (azs - G) * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        t += dt
        xs.append(x); ys.append(y); zs.append(z); ts.append(t)
        if z < 0 and t > 0.2:
            break

    return np.array(xs), np.array(ys), np.array(zs), np.array(ts)


# ============================================================
# Plotly 3D 渲染
# ============================================================
def mesh_to_plotly(vertices, faces, name, color, opacity):
    """manifold3d mesh → Plotly Mesh3d"""
    return go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1],
        z=vertices[:, 2],
        i=faces[:, 0],
        j=faces[:, 1],
        k=faces[:, 2],
        name=name,
        color=color,
        opacity=opacity,
        flatshading=True,
        showlegend=True,
    )


def build_html(state_dict, output_path):
    """构建 Plotly HTML（带交互控制）"""
    rpms = (state_dict['rpm_w1'], state_dict['rpm_w2'], state_dict['rpm_w3'])

    # 计算轨迹
    x, y, z, t = simulate_trajectory(rpms, state_dict['angle_deg'],
                                        state_dict['propel_mode'])
    # 转换：m → mm
    x_mm, y_mm, z_mm = x * 1000, y * 1000, z * 1000

    # 创建图
    fig = go.Figure()

    # 发射器 mesh
    for name, vertices, faces, color, opacity in build_launcher_meshes():
        fig.add_trace(mesh_to_plotly(vertices, faces, name, color, opacity))

    # 轨迹
    fig.add_trace(go.Scatter3d(
        x=x_mm, y=y_mm, z=z_mm + 100,
        mode='lines+markers',
        name=f'Trajectory (range={x[-1]:.1f}m, peak={z.max():.1f}m)',
        line=dict(color='#cc0000', width=6),
        marker=dict(size=3, color='#cc0000', opacity=0.7),
        hovertemplate='Range: %{x:.1f}mm<br>Height: %{z:.1f}mm<extra></extra>',
    ))

    # 地面
    ground_x = [-5000, 5000]
    ground_y = [-5000, 5000]
    for gx in ground_x:
        fig.add_trace(go.Scatter3d(
            x=[gx, gx], y=[-5000, 5000], z=[0, 0],
            mode='lines', showlegend=False,
            line=dict(color='#888888', width=1),
            hoverinfo='skip',
        ))

    # 控件（JavaScript sliders）
    # Plotly 3D 子图用 updatemenus 和 sliders 实现交互

    # 5 种模式按钮
    mode_buttons = [
        dict(label="STRAIGHT", method="animate",
             args=[None, {"frame": {"duration": 500, "redraw": True},
                          "fromcurrent": True}]),
        dict(label="LEFT_CURVE", method="animate",
             args=[None, {"frame": {"duration": 500, "redraw": True},
                          "fromcurrent": True}]),
        # 实际更新需要在 HTML 中用 JavaScript 重计算
    ]

    fig.update_layout(
        title=dict(
            text=f'<b>Football Launcher — 3D Interactive</b><br>'
                 f'<sub>RPM: ({rpms[0]}, {rpms[1]}, {rpms[2]}) | '
                 f'Angle: {state_dict["angle_deg"]}° | '
                 f'Propulsion: {state_dict["propel_mode"]} | '
                 f'Range: {x[-1]:.1f}m</sub>',
            x=0.5,
            xanchor='center',
        ),
        scene=dict(
            xaxis=dict(title='X (mm) — Range', range=[-300, max(3000, x_mm.max())]),
            yaxis=dict(title='Y (mm) — Lateral', range=[-300, 300]),
            zaxis=dict(title='Z (mm) — Height', range=[0, max(2000, z_mm.max() + 200)]),
            camera=dict(eye=dict(x=-400, y=-400, z=300),
                          center=dict(x=200, y=0, z=50)),
            aspectmode='manual',
            aspectratio=dict(x=2, y=1, z=1),
        ),
        width=1400,
        height=900,
        showlegend=True,
        legend=dict(x=0.02, y=0.98),
        updatemenus=[
            dict(
                type='buttons',
                showactive=False,
                buttons=[
                    dict(label='Reset View', method='relayout',
                         args=[{'scene.camera.eye': dict(x=-400, y=-400, z=300)}]),
                    dict(label='Top View', method='relayout',
                         args=[{'scene.camera.eye': dict(x=0, y=0, z=800)}]),
                    dict(label='Side View', method='relayout',
                         args=[{'scene.camera.eye': dict(x=-800, y=0, z=200)}]),
                ],
                x=0.02, y=0.5,
            ),
        ],
    )

    # 写 HTML
    fig.write_html(output_path, include_plotlyjs='cdn', full_html=True)


# ============================================================
# 简化版：固定模式交互（无 slider，5 个按钮切换）
# ============================================================
def build_interactive_5modes_html(output_path):
    """5 模式交互式 HTML（点击按钮切换）"""

    modes = [
        ('STRAIGHT',    (2500, 2500, 2500), 'pneumatic_8bar', '#00aa00'),
        ('LEFT_CURVE',  (2300, 2700, 2500), 'pneumatic_8bar', '#0066cc'),
        ('RIGHT_CURVE', (2700, 2500, 2300), 'pneumatic_8bar', '#cc6600'),
        ('TOPSPIN',     (2800, 2400, 2300), 'pneumatic_8bar', '#cc0066'),
        ('BACKSPIN',    (2300, 2400, 2800), 'pneumatic_8bar', '#6600cc'),
    ]

    traces = []
    for i, (mode_name, rpms, propel, color) in enumerate(modes):
        x, y, z, t = simulate_trajectory(rpms, 12, propel)
        x_mm, y_mm, z_mm = x * 1000, y * 1000, z * 1000

        # 5 模式轨迹（默认都显示但只激活一个）
        traces.append(go.Scatter3d(
            x=x_mm, y=y_mm, z=z_mm + 100,
            mode='lines',
            name=f'{mode_name}: range={x[-1]:.1f}m',
            line=dict(color=color, width=8),
            visible=(i == 0),  # 默认只显示第一个
            hovertemplate=f'<b>{mode_name}</b><br>'
                          f'Range: %{{x:.1f}}mm<br>Height: %{{z:.1f}}mm<extra></extra>',
        ))

    # 添加 3D 发射器 mesh（所有模式共享）
    meshes = build_launcher_meshes()
    for name, vertices, faces, color, opacity in meshes:
        traces.append(mesh_to_plotly(vertices, faces, name, color, opacity))

    fig = go.Figure(data=traces)

    # 5 模式切换按钮
    buttons = []
    for i, (mode_name, _, _, _) in enumerate(modes):
        # 创建 visibility array
        vis = [True] * 5  # 5 个轨迹
        # mesh visibility（始终可见）
        mesh_vis_count = len(meshes)
        full_vis = [True] * mesh_vis_count
        # 所有轨迹按钮 visibility（只激活第 i 个）
        traj_vis = [False] * 5
        traj_vis[i] = True

        full_visibility = traj_vis + [True] * mesh_vis_count

        buttons.append(dict(
            label=mode_name,
            method='update',
            args=[{'visible': full_visibility},
                  {'title': f'<b>Mode: {mode_name}</b><br>'
                            f'<sub>Range: {simulate_trajectory(modes[i][1], 12, modes[i][2])[0][-1]:.1f}m</sub>'}]
        ))

    fig.update_layout(
        title=dict(
            text='<b>Football Launcher — Interactive 3D</b><br>'
                 '<sub>Click mode buttons to switch trajectory</sub>',
            x=0.5, xanchor='center',
        ),
        scene=dict(
            xaxis=dict(title='X (mm) — Range', range=[-300, 3000]),
            yaxis=dict(title='Y (mm) — Lateral', range=[-300, 300]),
            zaxis=dict(title='Z (mm) — Height', range=[0, 2000]),
            camera=dict(eye=dict(x=-500, y=-500, z=400)),
        ),
        width=1400,
        height=900,
        showlegend=True,
        updatemenus=[dict(
            type='buttons',
            direction='right',
            buttons=buttons,
            x=0.02, y=1.0,
            xanchor='left', yanchor='top',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#888888',
        )],
    )

    fig.write_html(output_path, include_plotlyjs='cdn', full_html=True,
                    config={'displayModeBar': True})


# ============================================================
# 主程序
# ============================================================
def main():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Football Launcher — 3D Interactive (Plotly HTML)")
    print("=" * 60)

    # 5 模式交互 HTML
    print("\n[1] 生成 5 模式交互 HTML...")
    out_5modes = os.path.join(output_dir, 'interactive_5modes.html')
    build_interactive_5modes_html(out_5modes)
    print(f"  ✓ {out_5modes}")

    # 默认状态 HTML
    print("\n[2] 生成默认状态 HTML...")
    default_state = {
        'rpm_w1': 2500, 'rpm_w2': 2500, 'rpm_w3': 2500,
        'angle_deg': 12,
        'propel_mode': 'pneumatic_8bar',
    }
    out_default = os.path.join(output_dir, 'interactive_default.html')
    build_html(default_state, out_default)
    print(f"  ✓ {out_default}")

    # 不同推进方式对比
    print("\n[3] 生成推进方式对比 HTML...")
    fig_compare = go.Figure()
    for propel, v_exit_est in [('tangent_friction', 3.5),
                                 ('pneumatic_8bar', 63),
                                 ('pneumatic_50m', 90)]:
        for mode_name, rpms, _, color in [
            ('STRAIGHT', (2500, 2500, 2500), 'pneumatic_8bar', '#00aa00'),
            ('LEFT_CURVE', (2300, 2700, 2500), 'pneumatic_8bar', '#0066cc'),
            ('TOPSPIN', (2800, 2400, 2300), 'pneumatic_8bar', '#cc0066'),
        ]:
            x, y, z, t = simulate_trajectory(rpms, 12, propel)
            x_mm, y_mm, z_mm = x * 1000, y * 1000, z * 1000
            fig_compare.add_trace(go.Scatter3d(
                x=x_mm, y=y_mm, z=z_mm + 100,
                mode='lines', name=f'{propel} - {mode_name} ({x[-1]:.1f}m)',
                line=dict(color=color, width=4,
                          dash='solid' if propel == 'pneumatic_50m' else
                                'dash' if propel == 'pneumatic_8bar' else 'dot'),
                visible=(propel == 'pneumatic_8bar' and mode_name == 'STRAIGHT'),
            ))

    # 发射器 mesh
    for name, vertices, faces, color, opacity in build_launcher_meshes():
        fig_compare.add_trace(mesh_to_plotly(vertices, faces, name, color, opacity))

    fig_compare.update_layout(
        title='<b>Propulsion + Mode Comparison</b>',
        scene=dict(
            xaxis=dict(title='X (mm)', range=[-300, 5000]),
            yaxis=dict(title='Y (mm)', range=[-500, 500]),
            zaxis=dict(title='Z (mm)', range=[0, 5000]),
            camera=dict(eye=dict(x=-600, y=-600, z=500)),
        ),
        width=1400, height=900,
        showlegend=True,
    )
    out_compare = os.path.join(output_dir, 'propulsion_comparison.html')
    fig_compare.write_html(out_compare, include_plotlyjs='cdn', full_html=True)
    print(f"  ✓ {out_compare}")

    print("\n✓ 全部完成")


if __name__ == "__main__":
    main()