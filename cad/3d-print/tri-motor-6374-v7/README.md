# Tri-Motor 6374 3D Printed Parts — v7 (Refined Disc Cradle)

## 与 v6 差异

v7 优化细节贴近参考图：
- **更紧凑**：cradle 从长筒改为盘状（厚 12mm）
- **can 明显伸出**：电机外壳朝向球方向伸出 cradle
- **辐条更明显**：3 条径向辐条，120° 间隔
- **螺栓孔可见**：4 个 M4 电机孔 + 6 个 M5 固定孔

## 关键机制（保留 v6 修正）

电机轴向**垂直于管长**（径向）→ 3 个 can 夹持球 → 沿管轴方向射出 → 差速产生弧线球。

## 零件清单

| 文件 | 用途 | 数量 |
|------|------|------|
| `launch_tube_v7.stl` | 球通道管（180mm 长） | 1 |
| `motor_cradle_v7.stl` | 径向盘状电机座（带辐条） | 3 |
| `motor_can_v7.stl` | 径向电机外壳（伸出 cradle） | 3 |
| `side_plate_v7.stl` | 端板 | 2 |

## Cradle 详细结构

```
                ╭─────╮       ← 外圈（环状，6×M5）
              ──/─────\──
             /  spoke  \      ← 3 条辐条（120° 间隔）
            /  spoke  \
           /  spoke  \
           │   ┌──┐   │       ← 中心 hub（容纳 6374）
           │   │mo│   │         4×M4 端面螺栓
           │   │to│   │
           │   │r │   │
           │   └──┘   │
            \        /
             \      /
              ──────
              ▲ can 端      ← 电机 can 伸出朝向球
```

## 与参考图对应

| 参考图特征 | v7 实现 |
|-----------|---------|
| 橙色辐条轮 | ✅ 3 辐条 + 外圈 |
| 电机 can 朝球 | ✅ can 伸出 cradle |
| 4 个电机螺栓 | ✅ 端面 4×M4 |
| 6 个固定螺栓 | ✅ 外圈 6×M5 |
| 紧凑盘状 | ✅ 厚 12mm |

## 打印

- 材料：PETG / ABS
- 方向：管长方向竖直（z）
- 支撑：cradle 内圈需要支撑

## 文件

- `params.py` / `render.py` — 参数化和渲染脚本
- `assembly_v7_iso.png` / `assembly_v7_top.png` — 组装图

## 依赖

```bash
pip install manifold3d matplotlib
```