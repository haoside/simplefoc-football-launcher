# SIM_VISUALIZER_V12_TILTED_DIRECT_LAUNCH_UPDATE

## Owner 修正
本轮口径变更：

- 改向上发射
- 三电机倾斜布置
- 由三电机倾斜夹持后的共同合力直接发射
- 不再按水平短管 + 后续轨迹抬升理解

---

## Widget 更新
Widget：`仿真验证交互可视化`

版本：v12

文件：
- `widgets/sim-visualizer.html`

---

## 主要改动

### 1. 发射角改为三电机倾斜角
控制项从普通“发射角”改为：

```text
三电机倾斜发射角
```

含义：
- 不是后处理轨迹角
- 是三电机嵌入短发射管后的整体倾斜夹持角
- 出球初始方向直接带向上分量

### 2. 3D 合力箭头加入向上分量
合力方向从水平偏转改为三维向量：

```text
force_dir = [cos(tilt) * cos(heading), sin(tilt), cos(tilt) * sin(heading)]
```

其中：
- `heading` 来自 A/B/C 左右合力
- `tilt` 来自三电机倾斜发射角

### 3. 三电机组视觉倾斜
3D 中短发射管 + 三电机组同步倾斜，表达“倾斜布置直接发射”。

### 4. CAD v1.2c
新增：

- `cad/assembly/p0-single-ball-launcher-v3/outrunner_embedded_tilted_tube_v1_2c.scad`

相对 v1.2b：
- 新增 `launch_tilt_deg = 18`
- 整个三电机嵌入短管组件整体倾斜
- 去除保护罩表达保持不变
- 发射方向按倾斜三电机合力方向

---

## 当前结论
v12 之后仿真主线为：

**三电机倾斜嵌入短发射管 → 共同合力方向直接向上发射 → A/B/C 差速叠加侧旋轨迹族。**

下一步继续：

1. 加三电机倾斜安装角/短管倾角推荐表
2. 加不同倾角下 50m 达成窗口
3. 加落点云 / 不可控热区
4. 加 A/B/C 独立压紧校准输入
