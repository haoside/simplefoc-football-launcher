# Tri-Motor 6374 3D Printed Parts — v8

## 关键改进（vs v7）

- **单层薄盘 cradle**（8mm，参考图风格）vs v7 的 12mm 厚盘
- **Can 嵌入管壁**：电机中心在 125mm 处（管壁位置），不是管外侧
- **Can 端面十字凹槽**：参考图可见的细节
- **Can 接触球面**：can 内陷进球通道 17.5mm，与球面切线接触

## 几何参数（关键）

```
管内径:       113mm
管外径:       130mm
电机中心:     125mm（嵌入管壁 -5mm 处）
Can 中心:     125mm（同上）
Can 外缘:     92.5mm 半径（嵌入球通道 17.5mm）
球面:         110mm 半径
接触间隙:     ~17.5mm（can 深入球通道）
```

## 零件清单

| 文件 | 用途 | 数量 |
|------|------|------|
| `launch_tube_v8.stl` | 球通道管 | 1 |
| `motor_cradle_v8.stl` | 单层薄盘 cradle（径向平面）| 3 |
| `motor_can_v8.stl` | 电机外壳（端面十字凹槽 + V 槽）| 3 |
| `side_plate_v8.stl` | 端板 | 2 |

## Can 端面十字凹槽

参考图可见 can 朝球端有十字凹槽特征。v8 模拟：
- 凹槽深 3mm，宽 2.5mm
- 中心十字交叉
- 用于：
  - 增加 can 抓球摩擦（防滑）
  - 减重（轻微）
  - 视觉参考图一致性

## 打印

- 材料：PETG / ABS
- 方向：管长方向竖直
- 支撑：cradle 内圈需要支撑
- 注意：can 嵌入管壁，**管壁厚度 27mm 可能需要钻孔配合**

## 文件

- `params.py` / `render.py`
- `assembly_v8_iso.png` / `assembly_v8_top.png`

## 依赖

```bash
pip install manifold3d matplotlib
```