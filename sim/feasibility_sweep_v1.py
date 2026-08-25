#!/usr/bin/env python3
"""可行域扫描 v1 — 回答'这套三轮结构能否打到 20m 长传'

扫描维度: 摩擦系数 mu x 预紧 preload x 接触弧长 L x 轮径 D
判据: 出球速度 >= 20 m/s (对应 20m 级长传, 含空气阻力)
输出: 满足判据的参数组合 + 推荐设计点
"""
import math
import os
import sys

try:
    import sim.odrive_launch_sim_v1 as S
except ModuleNotFoundError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import odrive_launch_sim_v1 as S


def run():
    target = 20.0
    rows = []
    for d_mm in (110, 130):
        S.WHEEL_R = d_mm / 2000.0
        for mu in (0.6, 0.85, 0.95):
            for pl in (10, 12, 14, 16):
                for L in (0.10, 0.14, 0.18, 0.22):
                    S.CONTACT_LEN = L
                    cfg = S.MechConfig(preload_mm=pl, friction_mu=mu,
                                       wheel_rpm=3400, launch_angle_deg=14)
                    r = S.simulate(cfg)
                    if r.exit_speed_mps >= target:
                        rows.append((d_mm, mu, pl, L, r))
    print(f"满足出球>={target}m/s 的组合共 {len(rows)} 组:")
    print(f"{'D_mm':>5}{'mu':>6}{'pl_mm':>7}{'L_m':>6}{'exit':>7}{'range':>7}{'A@24V':>7}")
    for d, mu, pl, L, r in sorted(rows, key=lambda x: (x[0], -x[4].exit_speed_mps)):
        print(f"{d:>5}{mu:>6.2f}{pl:>7}{L:>6.2f}"
              f"{r.exit_speed_mps:>7.1f}{r.range_m:>7.1f}{r.odrive_current_a:>7.0f}")

    # 推荐点: 最保守预紧下达到目标的组合
    ok = [r for r in rows if r[2] <= 12]
    if ok:
        d, mu, pl, L, res = ok[0]
        print(f"\n推荐设计点: φ{d}轮 mu={mu} 预紧{pl}mm 弧长{L}m "
              f"-> 出球{res.exit_speed_mps}m/s 射程{res.range_m}m "
              f"补能电流{res.odrive_current_a:.0f}A@24V 轮速跌落{res.rpm_sag_pct:.1f}%")
    else:
        print("\n结论: 预紧<=12mm 内无解, 需要 16mm 级压紧或加长接触弧(双段轮)")
    if not rows:
        print("结论: 全域无解 -> 必须改架构(升轮速电压/换大KV电机)")


if __name__ == "__main__":
    run()
