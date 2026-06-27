# Tri-Motor 6374 3D Printed Parts — v6 (RADIAL Motor Axes)

## 关键修正（vs v5）

**v5 错误**：电机轴向**平行**于管长 → 只能让球原地打转
**v6 修正**：电机轴向**垂直于管长**（径向）→ 3 个电机 can 夹持球，沿管轴方向射出

## 机制说明（足球传中/弧线球）

```
                  Z（发射方向）
                   ↑
                   │
        ┌──────────┼──────────┐
        │   tube   │   tube   │   ← 球通道
        │  ╲   │   ╱          │
        │   motor  │  motor  motor   ← 电机径向（can 沿径向旋转）
        │   can  │  can    can
        │   (径向)  │  (径向) (径向)
        └──────────┼──────────┘
                   │
                   ↓ 发射方向
```

3 个电机 can 沿径向旋转：
- **同速**：球直线射出
- **差速**：球带旋转 → 弧线球/传中效果
- **方向控制**：单边加速 → 球左右偏移

## 零件清单

| 文件 | 用途 | 数量 |
|------|------|------|
| `launch_tube_v6.stl` | 球通道管（200mm 长，球通过+加速距离）| 1 |
| `motor_cradle_v6.stl` | **径向辐条轮电机座** | 3 |
| `motor_can_v6.stl` | 径向电机外壳套（V 槽） | 3 |
| `side_plate_v6.stl` | 端板 | 2 |

## 辐条轮（径向平面）

每个 cradle 的辐条轮平面**包含径向轴**（不再垂直于管）：
- 中心 hub：容纳 6374，电机轴沿径向
- 3 条辐条：120° 间隔，在径向平面内
- 外圈：M5 螺栓固定到管

## 几何参数

```
管内径:     113mm（球通过 6mm 间隙）
管外径:     130mm
管长:       200mm（球加速距离）
电机中心:   140mm 半径
电机 can 径: 33.5mm
3 电机:     120° 均布
can 接触球: 球面切线（向内伸入）
```

## 打印建议

- 材料：PETG / ABS
- 层高：0.2mm
- 填充：40-50%
- 方向：管长竖直打印（z 轴），电机轴水平（径向）
- 支撑：cradle 内圈需要支撑

## 控制逻辑（固件侧）

```c
// 3 电机协调控制
// 同速发射直线球
wheel_rpm = target_rpm;
rpm_mixer_120(wheel_rpm, wheel_rpm, wheel_rpm);

// 差速产生旋转（弧线球）
rpm_mixer_120(wheel_rpm + delta, wheel_rpm, wheel_rpm - delta);
```

详细算法参考 `firmware/host-esp32s3/src/rpm_mixer_120.cpp`。

## 文件

- `params.py` — 参数化 STL 生成
- `render.py` — 组装图渲染
- `assembly_v6_iso.png` — 等轴测
- `assembly_v6_top.png` — 俯视

## 依赖

```bash
pip install manifold3d matplotlib
```