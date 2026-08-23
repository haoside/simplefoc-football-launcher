#!/usr/bin/env python3
"""ODrive 三轮发射器 · 三维弹道仿真 v1

物理链路: 轮组几何 -> 轮-球接触(摩擦+压紧) -> 出球速度/旋转向量
        -> 马格努斯 + 空气阻力 3D 弹道积分
配套: docs/MECH_REDESIGN_ODRIVE_V1.md, widgets/odrive_sim_3d.html
用法: python3 sim/odrive_launch_sim_v1.py            # 跑预设工况表
      python3 -c "from sim.odrive_launch_sim_v1 import *; ..."
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, asdict, field

G = 9.81
RHO = 1.225          # 海平面空气密度 kg/m^3
CD = 0.25            # 足球阻力系数(亚临界雷诺数近似)
CL_MAX = 0.35        # Magnus 升力系数上限 (spin factor 上限保护)

# ---- 球 ----
BALL_MASS = 0.43     # kg (FIFA 5号)
BALL_R = 0.11        # m
BALL_AREA = math.pi * BALL_R ** 2

# ---- 新结构轮组 (Candidate A: 外置三轮铰接预紧) ----
WHEEL_R = 0.055      # 摩擦轮半径 φ110mm
WHEEL_MASS = 0.35    # kg (PU包胶铝芯)
MOTOR_KV = 170.0     # 6374 170KV
VBUS = 24.0
RPM_MIN, RPM_MAX = 500.0, 3600.0   # ODrive S1 + 6374@24V: 空载4080, 负载3600可稳
CONTACT_LEN = 0.10                 # 加速段有效接触弧长 m (三轮包角, 可调)


@dataclass
class MechConfig:
    """新机械结构可调参数 — 与 3D 可视化页共用同一套数值"""
    preload_mm: float = 10.0     # 单轮压紧深度(球径方向侵入量)
    friction_mu: float = 0.6     # PU-皮革摩擦系数
    launch_angle_deg: float = 12.0
    wheel_rpm: float = 2000.0    # 基准轮速(三轮同速时)
    spin_bias_rpm: float = 0.0   # 左右差速幅值(弧线量)
    topspin_bias_rpm: float = 0.0  # 上轮与下轮差速(前后旋)
    yaw_deg: float = 0.0         # 发射偏航


@dataclass
class LaunchResult:
    exit_speed_mps: float
    spin_rps: float                 # 合成旋转 rps (带符号分量见 spin_vec)
    spin_vec: tuple
    exit_pos: tuple
    exit_vel: tuple
    range_m: float
    lateral_m: float
    apex_m: float
    flight_s: float
    slip_ratio: float
    recharge_watts: float           # 冷却期平均补能功率
    odrive_current_a: float         # 24V 母线补能电流
    rpm_sag_pct: float              # 单次发射轮速跌落 %
    timeline: list = field(default_factory=list)


# ---------- 几何: 三轮位置(Candidate A 外置臂) ----------
def wheel_positions(preload_mm: float):
    """三轮接触点在球截面圆上的方位角。12点=上, 4点, 8点。
    压紧使有效球半径缩小, 接触方位随之微调——此处一阶近似忽略,
    只返回名义方位。返回单位法向向量列表(指向球心)。"""
    angles_deg = (90.0, 90.0 - 120.0, 90.0 + 120.0)  # 12点/4点/8点
    return [(math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0)
            for a in angles_deg]


def contact_normal_force(preload_mm: float) -> float:
    """单轮法向预紧力 N —— 碟簧丝杠标定曲线的一阶线性模型。
    设计目标: mu*N*3 >= m*a_launch 所需抓地, 且球变形 < 15% 直径。
    标定基准: 10mm 压紧 ≈ 300N (碟簧丝杠标定曲线一阶值, 待台架实测修正)"""
    return max(0.0, preload_mm) * 30.0


def accel_of_ball(preload_mm: float, mu: float) -> float:
    """三轮联合最大加速 a = Σ mu*N / m (不打滑上限)"""
    return 3.0 * mu * contact_normal_force(preload_mm) / BALL_MASS


# ---------- 出球解算 ----------
def solve_exit(cfg: MechConfig):
    """轮速向量 -> 球出射速度 + 旋转向量。
    模型: 接触点无滑移时球表面速度=轮缘线速度;
    三轮合成: 平动 = 三轮切向贡献均值, 旋转 = 差速项。"""
    w = cfg.wheel_rpm
    d_side = cfg.spin_bias_rpm     # B/C 差 -> 侧旋
    d_top = cfg.topspin_bias_rpm   # A vs (B+C)/2 差 -> 上/下旋

    rpm = (w, w + d_side, w - d_side)          # A(12点), B(4点), C(8点)

    # 轮缘线速度 m/s
    v = [r / 60.0 * 2 * math.pi * WHEEL_R for r in rpm]
    slip_protect = accel_of_ball(cfg.preload_mm, cfg.friction_mu)
    v_wheel_cap = min(v) * 0.98                 # 最慢轮限制(防单轮拖拽)
    v_friction_cap = math.sqrt(2 * slip_protect * CONTACT_LEN)
    v_ball = min(v_wheel_cap, v_friction_cap)
    if v_friction_cap >= v_wheel_cap:
        slip_ratio = 1.0                        # 摩擦上限≥轮缘: 无打滑
    else:
        slip_ratio = round(v_ball / max(v_wheel_cap, 1e-6), 3)

    # 自转角速度: 侧旋来自左右差速, 前后旋来自上下差速 (标定系数 k_spin)
    k_spin = 1.05                               # 滑移修正, 台架标定项
    omega_y_z = k_spin * (v[1] - v[2]) / BALL_R / 2.0   # 绕竖直轴 (侧旋) rad/s
    omega_x = -k_spin * (d_top / 60.0 * 2 * math.pi * WHEEL_R) / BALL_R / 2.0
    spin_vec = (omega_x, 0.0, omega_y_z)        # 世界系: x右 y前 z上
    spin_rps = math.sqrt(sum(c * c for c in spin_vec)) / (2 * math.pi)

    # 功率/电流核算 —— 飞轮能量模型(正确物理):
    # 发射能量主要来自预旋轮组动能, 电池只在 COOLDOWN 内补能。
    I_wheel = 0.5 * WHEEL_MASS * WHEEL_R ** 2            # 轮≈均质盘
    I_rotor = 1.8e-4                                     # 6374 转子典型值
    omega = max(v[0], 1e-6) / WHEEL_R                    # 基准轮角速度
    ke_wheels = 3 * 0.5 * (I_wheel + I_rotor) * omega ** 2
    e_ball = 0.5 * BALL_MASS * v_ball ** 2
    e_spin = 0.5 * (2 / 3 * BALL_MASS * BALL_R ** 2) * (spin_rps * 2 * math.pi) ** 2
    sag_frac = min((e_ball + e_spin) / ke_wheels, 1.0) if ke_wheels > 0 else 1.0
    rpm_sag_pct = (1 - math.sqrt(max(1 - sag_frac, 0.02))) * 100.0
    p_recharge = (e_ball + e_spin) / 0.80 / 3.0          # 3s 冷却内补回(效率0.8)
    i_dc = p_recharge / VBUS                             # 补能电流(持续)
    i_dc = max(i_dc, 2.0)                                # 空载维持下限
    return v_ball, spin_vec, spin_rps, slip_ratio, p_recharge, i_dc, rpm_sag_pct


# ---------- 飞行弹道 (RK4, 阻力+Magnus) ----------
def _accel(v, w):
    speed = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if speed < 1e-6:
        return (0.0, -G, 0.0), speed
    fd = -0.5 * RHO * CD * BALL_AREA / BALL_MASS * speed      # 标量因子
    drag = (fd * v[0], fd * v[1], fd * v[2])
    # Magnus: F = S*w×v ; 用 CL 因子近似
    s_magnus = 0.5 * RHO * BALL_AREA * BALL_R / BALL_MASS * 0.6
    wxv = (w[1] * v[2] - w[2] * v[1],
           w[2] * v[0] - w[0] * v[2],
           w[0] * v[1] - w[1] * v[0])
    magnus = tuple(s_magnus * c for c in wxv)
    return ((drag[0] + magnus[0],
             drag[1] + magnus[1],
             drag[2] + magnus[2] - G), speed)


def fly(v0, w, dt=0.002, t_max=6.0, h0=0.9):
    """从出射点积分到落地。返回采样轨迹与落点统计。v0 已是世界系速度矢量。"""
    pos = [0.0, 0.0, h0]
    vel = list(v0)
    traj = [(pos[0], pos[1], pos[2])]
    t = 0.0
    while t < t_max:
        acc, spd = _accel(vel, w)
        for i in range(3):
            vel[i] += acc[i] * dt
            pos[i] += vel[i] * dt
        t += dt
        traj.append((pos[0], pos[1], pos[2]))
        if pos[2] <= 0 and t > 0.15:
            break
    apex = max(p[2] for p in traj)
    rng = math.hypot(traj[-1][0], traj[-1][1])
    lat = traj[-1][0]
    return traj, rng, lat, apex, t


def simulate(cfg: MechConfig, h0=0.9) -> LaunchResult:
    v_ball, w, spin_rps, slip, p_rec, i_dc, sag = solve_exit(cfg)
    a = math.radians(cfg.launch_angle_deg)
    yaw = math.radians(cfg.yaw_deg)
    vel0 = (v_ball * math.cos(a) * math.sin(yaw),         # x=横向
            v_ball * math.cos(a) * math.cos(yaw),         # y=前进
            v_ball * math.sin(a))                         # z=竖直
    traj, rng, lat, apex, tf = fly(list(vel0), w, h0=h0)
    step = max(1, len(traj) // 120)
    timeline = [{"t_s": round(i * 0.002, 3),
                 "x": round(p[0], 3), "y": round(p[1], 3), "z": round(p[2], 3)}
                for i, p in enumerate(traj[::step])]
    return LaunchResult(
        exit_speed_mps=round(v_ball, 2), spin_rps=round(spin_rps, 2),
        spin_vec=tuple(round(c, 2) for c in w),
        exit_pos=(0, 0, h0), exit_vel=tuple(round(c, 2) for c in vel0),
        range_m=round(rng, 2), lateral_m=round(lat, 2), apex_m=round(apex, 2),
        flight_s=round(tf, 2), slip_ratio=round(slip, 3),
        recharge_watts=round(p_rec, 1), odrive_current_a=round(i_dc, 1),
        rpm_sag_pct=round(sag, 1),
        timeline=timeline)


PRESETS = {
    "straight_15m": MechConfig(wheel_rpm=2400, launch_angle_deg=10),
    "long_pass_20m": MechConfig(wheel_rpm=3200, launch_angle_deg=14),
    "curve_left_16m": MechConfig(wheel_rpm=2800, spin_bias_rpm=350,
                                 launch_angle_deg=13, yaw_deg=-4),
    "topspin_drive": MechConfig(wheel_rpm=3000, topspin_bias_rpm=300,
                                launch_angle_deg=8),
}


def main():
    rows = []
    for name, cfg in PRESETS.items():
        r = simulate(cfg)
        rows.append((name, cfg, r))
    print(f"{'case':<16}{'exit':>7}{'spin':>7}{'range':>8}{'lat':>7}"
          f"{'apex':>7}{'fly':>6}{'sag%':>6}{'W_rec':>7}{'A@24V':>7}")
    for name, cfg, r in rows:
        print(f"{name:<16}{r.exit_speed_mps:>7.1f}{r.spin_rps:>7.1f}"
              f"{r.range_m:>8.1f}{r.lateral_m:>7.2f}{r.apex_m:>7.2f}"
              f"{r.flight_s:>6.2f}{r.rpm_sag_pct:>6.1f}"
              f"{r.recharge_watts:>7.0f}{r.odrive_current_a:>7.1f}")
    out = os.path.join(os.path.dirname(__file__), "odrive_sim_results_v1.json")
    with open(out, "w") as f:
        json.dump({n: {"config": asdict(c), "result": asdict(r)}
                   for n, c, r in rows}, f, ensure_ascii=False, indent=1)
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
