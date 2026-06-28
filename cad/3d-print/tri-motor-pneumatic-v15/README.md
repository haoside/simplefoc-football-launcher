# Tri-Motor Pneumatic Launcher — v15

## 架构基础

按 `PROPULSION_ARCHITECTURE_REVIEW_V1.md` 锁定的主线方案：

- **压缩空气** = 主轴向推进（不再是三电机摩擦）
- **3 电机径向 cradle + 飞轮盘** = 控旋模块
- 阀、罐、压力表等 = 外购件，不 3D 打印

## 零件清单

| 文件 | 用途 | 数量 |
|------|------|------|
| `tube_body_v15.stl` | 主发射管（400mm + 4 条球导轨 + 装球口）| 1 |
| `pressure_end_v15.stl` | 压力端（封闭 + 进气口 + 爆破片槽）| 1 |
| `motor_cradle_v15.stl` | 控旋模块（盘状 cradle + 飞轮盘）| 3 |
| `output_end_v15.stl` | 前端出球口 + 安全网固定位 | 1 |

## 几何参数

```
球:           220mm
发射管:       IR 113 / OR 140 / L 400mm
管内:         4 条球导轨（让球居中）
装球口:       1/4 管长位置，侧面凸缘 + 闸门预留
压力端:       OR 155，法兰螺栓 8×M5
进气口:       φ25mm（接电磁阀）
爆破片槽:     环形槽（安全）
Cradle 中心:  125mm 半径（管外 55mm）
Cradle:       3 条辐条 120°，盘厚 10mm
飞轮盘:       φ50×8mm（接触球面）
出球端:       OR 160 + 外缘环
```

## 仿真支撑（`sim/pneumatic_launch_model.py`）

| 配置 | 出膛速度 | 射程 |
|------|---------|------|
| 5 bar / 5 L / 200mm | 51 m/s | 48 m |
| 8 bar / 5 L / 200mm | 63 m/s | 68 m |
| **8 bar / 20 L / 400mm** | **90 m/s** | **80+ m** (50m目标) |
| 12 bar / 5 L / 200mm | 76 m/s | OVER-RATED |

## 安全边界（外购件配置）

- 工作压力 ≤ 8 bar
- 爆破片 @ 9.6 bar (1.2× 工作)
- 泄压阀 @ 8.8 bar (1.1× 工作)
- 急停按钮（硬件切断气源）
- 球装载互锁（球未到位禁加压）
- 操作员距离 ≥ 3m

## 3D 打印注意

- **不能 3D 打印压力容器** — 压力端仅作端盖，气罐外购
- 主体用 PETG / ABS / CF-PETG
- 球导轨需要支撑打印
- 飞轮盘精度高，需 0.15mm 层高

## 依赖

```bash
pip install manifold3d matplotlib
```

## 文件

- `params.py` — 参数化 STL 生成
- `render.py` — 组装图渲染
- `assembly_v15_iso.png` / `assembly_v15_side.png` — 组装图