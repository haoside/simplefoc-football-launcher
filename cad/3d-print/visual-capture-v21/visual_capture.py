"""
Football Launcher 视觉捕捉 + 控制调节 + 弧线模拟
- 3D 发射器渲染
- 控制参数面板（3 电机 RPM、发射角、初始压力）
- 球弧线轨迹模拟（5 种模式对比）
"""

import numpy as np
from manifold3d import Manifold
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.widgets import Slider, Button
import math
import os

# ============================================================
# 物理参数（与 v18 / tangent_roller_model.py 一致）
# ============================================================
BALL_D = 0.22
BALL_R = BALL_D / 2
BALL_MASS = 0.43
G = 9.81
RHO = 1.225
CD = 0.25
BALL_AREA = math.pi * BALL_R ** 2

# 切向滚轮参数（v18 物理）
N_MOTORS = 3
CAN_R = 0.0315
NORMAL_N = 30.0
MU = 0.5
MOTOR_EFF = 0.85
PRESS_TIME_S = 0.040

# Magnus 系数
K_LAT = 0.42
K_VERT = 0.30

# 推进来源（可调）
PROPULSION = {
    'tangent_friction': {
        'v_exit_factor': 0.42,    # 切向滚轮效率
        'description': '3×6374 tangent rollers',
    },
    'pneumatic_8bar': {
        'v_exit': 63.0,           # 8 bar 气压
        'description': '8 bar / 5 L / 200 mm',
    },
    'pneumatic_8bar_50m': {
        'v_exit': 90.0,
        'description': '8 bar / 20 L / 400 mm (50m target)',
    },
    'manual': {
        'v_exit': 25.0,
        'description': 'Manual set (m/s)',
    },
}


# ============================================================
# 控制参数（可调）
# ============================================================
class ControlState:
    def __init__(self):
        self.rpm_w1 = 2500      # Motor 1 RPM @ 0°
        self.rpm_w2 = 2500      # Motor 2 RPM @ 120°
        self.rpm_w3 = 2500      # Motor 3 RPM @ 240°
        self.angle_deg = 8.0    # 发射角
        self.propel_mode = 'tangent_friction'

    def avg_rpm(self):
        return (self.rpm_w1 + self.rpm_w2 + self.rpm_w3) / 3.0

    def spin_magnitude(self):
        """差速 → 球自旋（rps）"""
        deltas = [self.rpm_w1 - self.avg_rpm(),
                  self.rpm_w2 - self.avg_rpm(),
                  self.rpm_w3 - self.avg_rpm()]
        avg_delta = sum(abs(d) for d in deltas) / 3.0
        return avg_delta / 60.0 * (CAN_R / BALL_R) * MOTOR_EFF

    def can_surface_speed(self, rpm):
        return rpm / 60.0 * (2 * math.pi * CAN_R)

    def exit_speed(self):
        if self.propel_mode == 'tangent_friction':
            v_can = self.can_surface_speed(self.avg_rpm())
            slip = min(1.0, MU * math.sqrt(NORMAL_N / 30.0))
            return v_can * slip * MOTOR_EFF
        elif self.propel_mode in PROPULSION:
            return PROPULSION[self.propel_mode]['v_exit']
        else:
            return 25.0

    def spin_axis(self):
        """由差速决定旋转方向"""
        deltas = [self.rpm_w1 - self.avg_rpm(),
                  self.rpm_w2 - self.avg_rpm(),
                  self.rpm_w3 - self.avg_rpm()]
        # 找到最快的电机
        max_i = np.argmax(deltas)
        # 旋转方向（粗略）
        # 如果 w1 > w2,w3 → 球向左转（左旋 → 向右偏）
        # 如果 w2 > w1,w3 → 球向右转（右旋 → 向左偏）
        spin_lr = 0.0
        spin_ud = 0.0
        # 上旋/下旋（topspin/backspin）：w1 vs w2,w3 的差
        if deltas[0] > 50:
            spin_ud = +1.0  # w1 更快 → 上旋（球加速向下，球下落更快）
        elif deltas[0] < -50:
            spin_ud = -1.0
        # 左/右曲线：w2 vs w3
        if deltas[1] > 50:
            spin_lr = -1.0  # w2 更快 → 球向右偏
        elif deltas[2] > 50:
            spin_lr = +1.0
        return spin_lr, spin_ud


# ============================================================
# 球轨迹模拟
# ============================================================
def simulate_trajectory(state: ControlState, n_frames=120):
    v0 = state.exit_speed()
    angle = math.radians(state.angle_deg)
    spin_lr, spin_ud = state.spin_axis()
    spin_rps = state.spin_magnitude() * max(abs(spin_lr), abs(spin_ud))

    x = y = 0.0
    z = 0.30
    vx = v0 * math.cos(angle)
    vy = 0.0
    vz = v0 * math.sin(angle)

    dt = 0.015
    t = 0.0
    xs, ys, zs, ts = [x], [y], [z], [t]
    peak_z = z
    ays = spin_lr * K_LAT * spin_rps
    azs = -spin_ud * K_VERT * spin_rps

    for _ in range(n_frames):
        v = math.sqrt(vx**2 + vy**2 + vz**2)
        drag = 0.5 * RHO * CD * BALL_AREA * v * v / BALL_MASS
        if v > 1e-6:
            vx -= drag * vx / v * dt
            vy -= drag * vy / v * dt
            vz -= drag * vz / v * dt
        vx += 0
        vy += ays * dt
        vz += (azs - G) * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        peak_z = max(peak_z, z)
        t += dt
        xs.append(x); ys.append(y); zs.append(z); ts.append(t)
        if z < 0 and t > 0.2:
            break

    return np.array(xs), np.array(ys), np.array(zs), np.array(ts), peak_z


# ============================================================
# 3D 发射器渲染（与 v18 一致）
# ============================================================
def C(h, r):
    return Manifold.cylinder(h, r, r, 48)


def manifold_to_mesh(body):
    m = body.to_mesh()
    v = np.array(m.vert_properties)[:, :3]
    f = np.array(m.tri_verts)
    return v, f


def render_launcher_3d(ax, show_traj=None, state=None):
    """渲染发射器 3D + 可选轨迹"""
    TUBE_IR = BALL_R * 1000 + 3
    TUBE_OR = TUBE_IR + 8
    TUBE_LEN = 200
    MOTOR_CENTER_R = BALL_R * 1000 - 1 + CAN_R * 1000

    body = C(TUBE_LEN, TUBE_OR) - C(TUBE_LEN + 0.4, TUBE_IR)

    for i in range(3):
        angle = math.radians(i * 120)
        cradle_hub = C(74 + 10, 75/2) - C(74 + 10.4, 63/2 + 0.5)
        cradle_hub = cradle_hub.rotate([0, 0, angle])
        cradle_hub = cradle_hub.translate([MOTOR_CENTER_R * math.cos(angle),
                                            MOTOR_CENTER_R * math.sin(angle),
                                            TUBE_LEN/2])
        spokes = Manifold()
        for j in range(3):
            sa = math.radians(j * 120)
            spoke = Manifold.cube((30, 18, 10), center=True)
            spoke = spoke.rotate([0, 0, sa])
            spoke = spoke.translate([MOTOR_CENTER_R * math.cos(angle) + 30 * math.cos(sa) * math.cos(angle),
                                     MOTOR_CENTER_R * math.sin(angle) + 30 * math.cos(sa) * math.sin(angle),
                                     TUBE_LEN/2])
            spokes = spokes + spoke
        rim = C(10, 80) - C(11, 70)
        rim = rim.rotate([0, math.pi/2, 0])
        rim = rim.translate([MOTOR_CENTER_R * math.cos(angle),
                             MOTOR_CENTER_R * math.sin(angle),
                             TUBE_LEN/2])
        body = body + cradle_hub + spokes + rim

    # 渲染壳体
    v, f = manifold_to_mesh(body)
    triangles = v[f]
    mc = Poly3DCollection(triangles, alpha=0.85, facecolor='#ff8c00',
                          edgecolor='#cc5500', linewidth=0.05)
    ax.add_collection3d(mc)

    # 球
    ball = Manifold.sphere(BALL_R * 1000, 32)
    v, f = manifold_to_mesh(ball)
    triangles = v[f]
    mc = Poly3DCollection(triangles, alpha=0.5, facecolor='#00cc00',
                          edgecolor='#008800', linewidth=0.3)
    ax.add_collection3d(mc)

    # 轨迹
    if show_traj is not None and state is not None:
        x, y, z, t, peak = simulate_trajectory(state)
        # 转换单位：米 → 毫米（与场景一致）
        ax.plot(x * 1000, y * 1000, z * 1000 + 100,  # +100 是 z 起点偏移
                color='#cc0000', linewidth=2, alpha=0.8,
                label=f'Trajectory (range={x[-1]*1000:.1f}m, peak={peak*1000:.1f}m)')

        # 球当前位置（沿轨迹的第 n 个点）
        step = max(1, len(x) // 8)
        for i in range(0, len(x), step):
            ax.scatter([x[i] * 1000], [y[i] * 1000], [z[i] * 1000 + 100],
                       color='#cc0000', s=20, alpha=0.6)


# ============================================================
# 主视图：4 面板 + 控制面板
# ============================================================
def make_visual_capture(state: ControlState, save_path):
    """完整视觉捕捉图"""
    fig = plt.figure(figsize=(20, 12))

    # ====== 主 3D 视图（占据左上） ======
    ax_3d = fig.add_subplot(2, 3, 1, projection='3d')
    ax_3d.set_title('A. 3D Launcher + Live Trajectory', fontsize=12, fontweight='bold')
    render_launcher_3d(ax_3d, show_traj=True, state=state)
    ax_3d.set_xlim(-300, 800)
    ax_3d.set_ylim(-300, 300)
    ax_3d.set_zlim(0, 500)
    ax_3d.set_xlabel('X (mm)')
    ax_3d.set_ylabel('Y (mm)')
    ax_3d.set_zlabel('Z (mm) — Height')
    ax_3d.legend(loc='upper right', fontsize=8)

    # ====== 控制面板（右上） ======
    ax_ctrl = fig.add_subplot(2, 3, 2)
    ax_ctrl.axis('off')
    ax_ctrl.set_title('B. Control State (current)', fontsize=12, fontweight='bold')

    spin_lr, spin_ud = state.spin_axis()
    spin_name_lr = 'Right' if spin_lr < 0 else 'Left' if spin_lr > 0 else '—'
    spin_name_ud = 'Topspin' if spin_ud > 0 else 'Backspin' if spin_ud < 0 else '—'
    spin_mode_str = f"{spin_name_lr} + {spin_name_ud}".strip(' +')

    x0, y0, peak = simulate_trajectory(state)[0], None, None
    _, _, _, _, peak = simulate_trajectory(state)

    v_exit = state.exit_speed()
    spin_rps = state.spin_magnitude()

    info_text = (
        f"Motor RPM:\n"
        f"  W1 (0°)   = {state.rpm_w1:4d}\n"
        f"  W2 (120°) = {state.rpm_w2:4d}\n"
        f"  W3 (240°) = {state.rpm_w3:4d}\n"
        f"  Avg       = {state.avg_rpm():4.0f}\n"
        f"\n"
        f"Launch:\n"
        f"  Angle    = {state.angle_deg:.1f}°\n"
        f"  v_exit   = {v_exit:.1f} m/s\n"
        f"  Spin     = {spin_rps:.2f} rps\n"
        f"  Spin mode = {spin_mode_str}\n"
        f"  Mode     = {state.propel_mode}\n"
        f"\n"
        f"Result:\n"
        f"  Range    = {x0[-1]:.1f} m\n"
        f"  Peak h   = {peak:.1f} m\n"
        f"  Flight   = {len(x0) * 0.015:.2f} s"
    )
    ax_ctrl.text(0.05, 0.95, info_text, transform=ax_ctrl.transAxes,
                  fontsize=11, verticalalignment='top', family='monospace',
                  bbox=dict(boxstyle='round,pad=0.5', facecolor='#f0f0f0',
                            edgecolor='#888888', linewidth=1))

    # ====== 5 种模式对比轨迹（右下大） ======
    ax_traj = fig.add_subplot(2, 1, 2)
    ax_traj.set_title('C. Trajectory Comparison — 5 Spin Modes (3-motor differential)',
                     fontsize=12, fontweight='bold')

    # 5 种模式
    modes = [
        ('STRAIGHT',    (2500, 2500, 2500), '+',  '#00aa00', 'Straight'),
        ('LEFT_CURVE',  (2300, 2700, 2500), '↙', '#0066cc', 'Left curve'),
        ('RIGHT_CURVE', (2700, 2500, 2300), '↘', '#cc6600', 'Right curve'),
        ('TOPSPIN',     (2800, 2400, 2300), '↓', '#cc0066', 'Topspin (low arc)'),
        ('BACKSPIN',    (2300, 2400, 2800), '↑', '#6600cc', 'Backspin (high arc)'),
    ]

    for mode_name, rpms, symbol, color, label in modes:
        s = ControlState()
        s.rpm_w1, s.rpm_w2, s.rpm_w3 = rpms
        s.angle_deg = 12
        s.propel_mode = 'pneumatic_8bar'
        x, y, z, t, peak = simulate_trajectory(s)
        ax_traj.plot(x, z, color=color, linewidth=2, alpha=0.85,
                      label=f'{label}: range={x[-1]:.1f}m, peak={peak:.1f}m')

    # 地面
    ax_traj.axhline(0, color='#444444', linewidth=0.8, linestyle='--', alpha=0.5)
    ax_traj.set_xlabel('Range (m)')
    ax_traj.set_ylabel('Height (m)')
    ax_traj.set_xlim(0, 70)
    ax_traj.set_ylim(0, 30)
    ax_traj.grid(True, alpha=0.3)
    ax_traj.legend(loc='upper right', fontsize=10)

    plt.suptitle('Football Launcher — Visual Capture + Control + Arc Simulation',
                  fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================
# 5 模式独立图（清晰大图）
# ============================================================
def make_individual_modes(save_dir):
    """5 种模式的独立大图"""
    modes = [
        ('straight',    (2500, 2500, 2500), 'Straight Shot',          '#00aa00', 0),
        ('left_curve',  (2300, 2700, 2500), 'Left Curve (差速 w2+)',  '#0066cc', 5),
        ('right_curve', (2700, 2500, 2300), 'Right Curve (差速 w1+)', '#cc6600', -5),
        ('topspin',     (2800, 2400, 2300), 'Topspin (w1+++，球加速下坠)','#cc0066', 0),
        ('backspin',    (2300, 2400, 2800), 'Backspin (w3+++，球上飘)','#6600cc', 0),
    ]

    for mode_name, rpms, title, color, lat_offset in modes:
        fig = plt.figure(figsize=(14, 8))
        ax = fig.add_subplot(111, projection='3d')

        s = ControlState()
        s.rpm_w1, s.rpm_w2, s.rpm_w3 = rpms
        s.angle_deg = 12
        s.propel_mode = 'pneumatic_8bar'

        # 3D launcher
        render_launcher_3d(ax, show_traj=True, state=s)

        # X-Y 偏置
        x, y, z, t, peak = simulate_trajectory(s)
        # 加横向偏移（for curve visualization）
        y_plot = y + lat_offset * 0.5 + (lat_offset / 50.0) * x  # 渐变偏置

        ax.plot(x * 1000, y_plot * 1000, z * 1000 + 100,
                color=color, linewidth=3, alpha=0.85)
        # 球当前位置
        for i in range(0, len(x), max(1, len(x) // 10)):
            ax.scatter([x[i] * 1000], [y_plot[i] * 1000], [z[i] * 1000 + 100],
                       color=color, s=80, alpha=0.7, edgecolors='black', linewidth=0.5)

        ax.set_xlim(-300, 800)
        ax.set_ylim(-200, 200)
        ax.set_zlim(0, 400)
        ax.set_xlabel('X (mm) — Range')
        ax.set_ylabel('Y (mm) — Lateral')
        ax.set_zlabel('Z (mm) — Height')
        ax.set_title(f'{title}\nRPM: W1={rpms[0]}  W2={rpms[1]}  W3={rpms[2]}',
                     fontsize=12, fontweight='bold')

        plt.tight_layout()
        out = os.path.join(save_dir, f'arc_{mode_name}.png')
        plt.savefig(out, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  ✓ {out} — {os.path.getsize(out)//1024}KB")


# ============================================================
# 主程序
# ============================================================
def main():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assembly")
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print("Visual Capture + Control Adjustment + Arc Simulation")
    print("=" * 60)

    # 默认状态：直线球
    state = ControlState()

    # 综合图
    print("\n[1] 综合视觉捕捉...")
    out_path = os.path.join(output_dir, 'visual_capture_v21.png')
    make_visual_capture(state, out_path)
    print(f"  ✓ {out_path}")

    # 5 模式独立图
    print("\n[2] 5 模式独立轨迹...")
    make_individual_modes(output_dir)

    # 控制面板调整版（不同的控制参数）
    print("\n[3] 控制调节对比（左/右曲线）...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    cases = [
        ('默认直线', (2500, 2500, 2500), 0, axes[0]),
        ('左曲线 w2+', (2300, 2700, 2500), 1, axes[1]),
        ('右曲线 w3+', (2500, 2300, 2700), -1, axes[2]),
    ]

    for title, rpms, dirn, ax in cases:
        s = ControlState()
        s.rpm_w1, s.rpm_w2, s.rpm_w3 = rpms
        s.propel_mode = 'pneumatic_8bar'
        x, y, z, t, peak = simulate_trajectory(s)
        ax.plot(x, z, color='#cc0000', linewidth=2)
        ax.plot(x, y * 5 + z, color='#0066cc', linewidth=2, alpha=0.7,
                label=f'Y × 5 (lateral)')  # 放大 lateral
        ax.axhline(0, color='gray', linewidth=0.5, linestyle='--')
        ax.set_title(f'{title} (RPM: {rpms[0]}, {rpms[1]}, {rpms[2]})', fontsize=11)
        ax.set_xlabel('Range (m)')
        ax.set_ylabel('Height (m)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_xlim(0, 70)

    plt.suptitle('Control Adjustment Comparison — Lateral deflection visualization (Y × 5)',
                  fontsize=13, fontweight='bold')
    plt.tight_layout()
    out = os.path.join(output_dir, 'control_adjustment_v21.png')
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {out}")

    print("\n✓ 全部完成")


if __name__ == "__main__":
    main()