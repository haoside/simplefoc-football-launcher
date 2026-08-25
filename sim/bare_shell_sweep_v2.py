#!/usr/bin/env python3
"""裸壳 φ63 供电扫描: 24V vs 12S, 检查 20m 长传可行性"""
import odrive_launch_sim_v1 as S

print('=== 裸壳 phi63 (R=31.5mm) 供电扫描: long_pass 目标 >=20m ===')
print(f"{'供电':<8}{'rpm上限':>8}{'出球':>7}{'射程':>7}{'sag%':>6}  工况")
for vbus, rpm_max in [(24.0, 3600), (36.0, 5400), (44.4, 6000)]:
    S.VBUS = vbus
    best = None
    for rpm in (2000, 3000, 4000, 5000, 6000):
        if rpm > rpm_max:
            break
        cfg = S.MechConfig(preload_mm=14, friction_mu=.85,
                           wheel_rpm=rpm, launch_angle_deg=16)
        r = S.simulate(cfg)
        best = (rpm, r)
        if r.range_m >= 20:
            break
    rpm, r = best
    ok = 'OK' if r.range_m >= 20 else 'X'
    print(f"{vbus:>4.0f}V {rpm_max:>8.0f}{r.exit_speed_mps:>7.1f}{r.range_m:>7.1f}"
          f"{r.rpm_sag_pct:>6.1f}  @{rpm}rpm {ok}")
