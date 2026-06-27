# Tri-Motor 6374 3D Printed Parts — v9 (Modular)

## 设计哲学变更

**v8**：一体式（cradle 嵌入管壁）
**v9**：模块化（管与 cradle 完全分离）

参考图显示 cradle 是**外挂件**，用螺栓固定到管外。v9 还原这种结构。

## 零件清单

| 文件 | 用途 | 数量 |
|------|------|------|
| `launch_tube_v9.stl` | 管（含 3 个 can 孔 + 4 条球导轨）| 1 |
| `motor_cradle_v9.stl` | 外挂辐条轮（带内圈连接环）| 3 |
| `motor_can_v9.stl` | 长 can（穿过管壁接触球）| 3 |
| `side_plate_v9.stl` | 端板 | 2 |

## 关键几何

```
管:   IR 113mm / OR 130mm / L 200mm
Can 孔: 67mm 直径（管壁）
球导轨: 4 条 6mm 宽 / 4mm 高 凸筋（管内）
Cradle: 中心 165mm 半径（管外 +35mm）
Can 长: 104mm（74mm 电机 + 30mm 穿过管壁）
```

## 装配逻辑

```
       ┌──────────┐
       │ Cradle外圈 │ ← 6×M5 固定到管外壁
       │ ╱──────╲  │
       │ │ spoke │ │ ← 3 条辐条
       │ │ hub   │ │
       │ │ 电机  │ │ ← 4×M4 端面螺栓
       │ │ can   │ │ ← can 穿过管壁孔
       ╰─┴──────┴─╯
            ↕
   ──────────────────  ← 管（PVC）
       ↑ 球导轨
       ↑ 4 条凸筋让球居中
       ↑
       球通道
```

## 优势（vs v8 一体式）

| | v8 | v9 |
|---|----|----|
| 打印 | 一件大，需大量支撑 | 多件小，分别打印 |
| 调试 | 整体重打 | 单件替换 |
| 装配 | 一体 | 螺栓连接 |
| 运输 | 大件 | 分件小 |

## 打印

- 管：标准 PVC 管 130mm 外径（或者 3D 打印带 can 孔）
- Cradle：PETG / ABS，3 件
- Can：3 件
- 球导轨在管内一次性成型

## 文件

- `params.py` / `render.py`
- `assembly_v9_iso.png` / `assembly_v9_top.png`

## 依赖

```bash
pip install manifold3d matplotlib
```