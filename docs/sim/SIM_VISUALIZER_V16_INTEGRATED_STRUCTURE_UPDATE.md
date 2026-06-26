# SIM_VISUALIZER_V16_INTEGRATED_STRUCTURE_UPDATE

## Owner 修正
本轮要求：

> 继续改进发射圆管兼三电机固定一体结构，必须贴近图片

---

## Widget 更新
Widget：`仿真验证交互可视化`

版本：v16

文件：
- `widgets/sim-visualizer.html`

---

## 主要改动

### 1. 顶层口径切换到 v1.2g
更新为：

```text
发射圆管兼三电机固定一体结构
```

不再把圆管、电机座、端压板、加强筋分开理解。

### 2. 新增“一体固定结构截面”
新增截面 SVG：

- 中心短发射管
- 三个电机口袋
- 端面压板 / 螺丝孔
- 管壁到电机座的加强筋
- 一体件边界

### 3. 3D 结构强化
3D 中增加：

- 前后橙色夹持环
- 三个电机嵌入口袋外壳
- 端面压板
- 从圆管到电机座的加强筋

目标是更贴近参考图里的橙色一体打印结构。

### 4. 合力方向保持不变
保持 v15 决策：

- 初始合力方向直接指向目标方向
- A/B/C 差速只负责侧旋 / 弧线

---

## 新增 CAD / 文档

新增 CAD：
- `cad/assembly/p0-single-ball-launcher-v3/outrunner_integrated_tube_motor_mount_v1_2g.scad`

新增机械说明：
- `docs/mechanical/INTEGRATED_TUBE_MOTOR_MOUNT_V1_2G.md`

---

## 下一步

1. 继续细化一体件 3D：线束出口、工具进入空间、端压板孔位
2. 加真实 6354 外形 / 孔距占位
3. 加转子包络与口袋最小间隙热区
4. 加 A/B/C 独立压紧校准输入
