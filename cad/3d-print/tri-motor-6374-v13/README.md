# Tri-Motor 6374 3D Printed Parts — v13 (Pure Visual Mimicry)

## 设计哲学

**不考虑 90°/180° 几何关系争议** — 纯视觉模仿参考图。

参考图核心视觉特征：
- 橙色盘状 cradle（垂直于管轴）
- 3 条辐条
- 外圈 4 颗 M5 螺栓
- 电机在中心 hub
- 安装在管上

## 几何（按球径比例放大）

```
球:        220mm
管:        IR 113 / OR 140 / L 180mm
盘外径:    187mm（≈ 球径 0.85×）
盘厚:      14mm
Hub OD:    71mm
Hub 长度:   82mm（沿 Z 轴）
辐条:      3 条 120°
外圈螺栓:   4×M5
电机螺栓:   4×M4
Cradle 中心: 125mm 半径（管外 55mm）
```

## 零件清单

| 文件 | 用途 | 数量 |
|------|------|------|
| `spider_body_v13.stl` | **★ 一体化主结构** | 1 |
| `motor_can_v13.stl` | 电机外壳 | 3 |
| `side_plate_v13.stl` | 端板 | 2 |

## 打印

- 材料：PETG / ABS
- 方向：管长方向竖直
- 支撑：cradle 外圈下方

## 依赖

```bash
pip install manifold3d matplotlib
```