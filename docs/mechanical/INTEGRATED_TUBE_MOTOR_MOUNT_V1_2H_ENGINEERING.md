# Integrated Tube + Three Motor Mount V1.2H Engineering Focus

## 指令
停止继续更新仿真，主线切换为：

**专注改进发射圆管兼三电机固定一体结构。**

本版不改 widget、不扩展轨迹仿真，只推进机械一体件。

---

## 当前结构目标

参考图口径保持：

```text
中心短发射管 + 三个电机嵌入口袋 + 端面压板 + 加强筋 + 线束/工具避让 = 一体结构
```

不是：
- 外挂电机板
- 独立保护罩
- 圆管与电机座分离
- 单纯仿真展示件

---

## CAD 新增

新增文件：

- `cad/assembly/p0-single-ball-launcher-v3/outrunner_integrated_tube_motor_mount_v1_2h.scad`

v1.2h 基于 v1.2g，但进入工程结构细化。

### 新增参数

```scad
structure_only_focus = true;
show_wire_channels = true;
show_tool_access = true;
show_rotor_clearance = true;
rotor_clearance_min = 3.0;
wire_channel_w = 13;
wire_channel_h = 8;
wire_channel_len = 52;
tool_access_d = 11;
tool_access_offset = 22;
split_service_gap = 2.0;
```

---

## 结构改进点

### 1. 线束出口
每个电机口袋新增线束通道占位：

- 宽度：`13mm`
- 高度：`8mm`
- 长度：`52mm`

目的：
- 避免一体口袋把三相线夹死
- 给电机翻转 90° 后的出线留路径
- 后续可改成后侧缺口或侧向线槽

### 2. 工具进入空间
每个电机口袋新增工具孔/工具包络：

- 工具直径：`11mm`
- 偏移：`22mm`

目的：
- 给内六角/螺丝刀进入端面压板
- 避免口袋一体化后无法拆电机
- 为端压板螺丝维护留空间

### 3. 转子包络
新增外转子旋转包络显示：

```scad
motor_d + 2 * rotor_clearance_min
```

当前最小目标间隙：`3mm`

用途：
- 检查转子与口袋内壁
- 检查端压板
- 检查加强筋
- 检查线束通道附近是否干涉

### 4. 服务分型线
新增 `split_service_gap = 2.0mm` 的分型线标记。

用途：
- 暂时作为视觉标记
- 后续可转成可拆压盖 / 分体夹具
- 避免一体件不可装配

---

## 工程结论

v1.2h 不再扩展仿真功能，当前主线是机械结构闭环：

1. 发射圆管和三电机固定座一体化
2. 三个电机口袋贴近参考图
3. 端压板、加强筋、线束出口、工具空间必须并入一体结构
4. 转子包络和维护空间作为下一轮重点验证

---

## 下一轮建议

1. 把 6354 真实端面孔距参数化
2. 将端面压板做成可拆压盖，而不是完全一体封死
3. 根据线束实际方向确定左/右/后侧出线槽
4. 输出 2D 端面三视图 / SVG，给设计师做结构复核
