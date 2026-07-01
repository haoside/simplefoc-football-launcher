# Control Panel V1 — 升级到 HIFI Spec

## v23 → v24 升级

按设计师 `DISPLAY_UI_HIFI_SPEC_V1` 重新校准：

### 颜色规范（§2）
- 背景主色 `#080B0F` / 面板 `#121821` / 高亮 `#1B2430`
- 文字 `#F4F7FA` / `#AAB4C0` / `#6F7A86`
- 状态色：`#21C55D` 绿 / `#FACC15` 黄 / `#EF4444` 红
- 轨迹色：`#38BDF8` 预测蓝 / `#FB923C` 实测橙

### 字号（1024×600）
- 页面标题 28px / 主状态 36-44px / 按钮 24px / 标签 18px

### 触控尺寸（§2）
- 主按钮 64px 高 / 普通按钮 52px / 急停 120×56
- 滑条 40px 高 / 拖拽点 32px 直径

### 布局栅格（§1）
- 顶部状态栏 56px
- 主内容区 472px
- 底部安全栏 72px（含 4 Tab）

### 组件规范（§4）
- 状态卡：左 6px 状态条（绿/黄/红/灰）
- 模式按钮：默认 / 选中（蓝）/ 待确认（黄）/ 禁用（灰）
- 滑条：待确认时变黄，超限时变红
- 急停栏：固定底部，永不覆盖
- 轨迹图例：4 种元素清晰区分
- 错误卡：黄色警告 / 红色全局 Banner

### 自动锁定规则（§7）
```javascript
if emergency_stop == true:
  safety_locked = true
if system_errors contains severity == critical:
  safety_locked = true
if pressure > max_pressure:
  safety_locked = true
if motor rpm drift exceeds threshold:
  launch_ready = false
```

## v24 改进

| 改进 | v23 → v24 |
|------|-----------|
| 配色 | 通用色 → HIFI 规范色 |
| 字号 | 通用 → 28/36/44 大字号 |
| 触控 | 32px → 64px 主按钮 |
| 栅格 | 自由 → 56/472/72 固定 |
| 状态卡 | 普通边框 → 6px 左侧状态条 |
| 滑条 | 静态 → 待确认变黄 |
| 顶部栏 | 简单 → 完整信息（模式/电量/温度/视觉）|
| 状态联动 | 简单 → 5 种状态独立检查 |
| 发射按钮 | 仅 lock 判断 | 5 条件联动（lock + 急停 + 待确认 + 参数 + 故障）|
| 错误处理 | 单错误 | 红色全局 Banner + 自动 disable |
| 急停确认 | 直接触发 | 模态确认 + 全屏红锁 |

## 文件

- `control_panel_v24.html` — 重新生成的主交付文件（46 KB）

## 字段对齐

完全沿用 `DISPLAY_UI_WIREFRAME_V1` + `CONTROL_SYSTEM_ARCHITECTURE_V1` 字段集：

```
mode, launch_ready, safety_locked, emergency_stop, param_pending_confirm
pressure, propulsion_type, valve_delay, piston_force
motor_a/b/c_rpm, motor_a/b/c_temp
camera_status, camera_fps, vision_confidence
predicted_landing_x/y, actual_landing_x/y, distance_error, lateral_error
battery_percent, battery_voltage, system_errors[]
```

## 打开

```bash
open cad/3d-print/control-panel-v24/control_panel_v24.html
```

## 验证 PM 4 项要求

| 要求 | 实现 |
|------|------|
| 急停锁定 | ✓ 模态确认 + 全屏红锁 + 所有页底部栏同步 |
| 参数待确认 | ✓ 滑条变黄 + Banner + 模式按钮变黄 |
| 预测 vs 实测偏差 | ✓ SVG 双色轨迹 + 距离/横向分别显示 + 偏差颜色编码 |
| 故障自动锁定 | ✓ 错误列表 + 发射按钮 disable + 诊断页红条 |

## 依赖

无（纯 HTML/CSS/JS）。