#!/usr/bin/env python3
"""裸壳φ63 可行域: 扫 preload/mu/接触弧长, 找各供电下的最大射程"""
import odrive_launch_sim_v1 as S

print('=== 裸壳 phi63: 参数空间扫描 (每供电取最优) ===')
for vbus, rpm_max in [(24.0, 3600), (44.4, 6000)]:
    S.VBUS = vbus
    best = (0, None, None)
    for pl in (10, 14, 16):
        for L in (0.10, 0.14, 0.18):
            S.CONTACT_LEN = L
            cfg = S.MechConfig(preload_mm=pl, friction_mu=.95,
                               wheel_rpm=rpm_max, launch_angle_deg=18)
            r = S.simulate(cfg)
            if r.range_m > best[0]:
                best = (r.range_m, r, (pl, L))
    rng, r, (pl, L) = best
    print(f"{vbus:.0f}V: 最优 射程{rng:.1f}m 出球{r.exit_speed_mps:.1f}m/s "
          f"(preload={pl}mm L={L}m @{rpm_max}rpm)")
