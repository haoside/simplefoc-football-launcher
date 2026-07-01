# Control Panel V1 — 单页 HTML 原型

## 用途

按 PM 要求交付的可实现 UI 原型：
> "不是图片，不是概念图，而是能进入前端实现的 UI 规格 + mock 交互原型。"

单页 HTML + 内嵌 CSS/JS，**无需后端、无需构建工具**，浏览器直接打开即用。

## 文件

- `control_panel_v1.html` — 主交付文件（40 KB，1163 行）

## 4 个 Tab

| Tab | 内容 |
|-----|------|
| **首页** | 模式选择（6 个按钮）+ 发射准备状态 + 发射控制（发射/试射/锁定/解除/急停）|
| **弧线** | 预测 vs 实测轨迹（SVG 渲染）+ 落点数据 + 偏差分析 + 回填参数 |
| **参数** | 3 电机 RPM 滑条 + 气压/阀门/活塞 + 弧线/旋转强度 + 确认/保存/恢复 |
| **诊断** | 系统总览 + 错误码列表 + 7 个子系统诊断（摄像头/3 电机/气压/阀/电池）|

## 关键交互（PM 要求 4 项）

| 要求 | 实现 |
|------|------|
| ✅ 急停锁定状态 | 物理急停按钮 + 模态确认 + 全屏红状态 + 锁定所有发射 |
| ✅ 参数待确认状态 | 任何参数改动显示 ⚠ 待确认横幅 + "试射"按钮 |
| ✅ 预测 vs 实测偏差显示 | 弧线页 SVG 蓝虚线/橙实线 + 偏差数值 + 距离/横向分别显示 |
| ✅ 故障自动锁定 | 错误码列表显示 → 发射按钮自动 disable + 红色诊断状态 |

## 设计规范

- **5-7 寸横屏**（1024×600 / 800×480 兼容）
- **深色高对比**（黑底 + 白字 + 状态色）
- **大字号**：主状态 28px，参数 16px，标签 14px
- **少装饰**：仅必要的状态指示
- **固定状态栏**（页脚）：发射状态 + 锁定 + 急停 + 电量

## 数据字段（与 UI Wireframe V1 对齐）

```javascript
{
  mode, launch_ready, safety_locked, emergency_stop,
  pressure, propulsion_type, valve_delay, piston_force,
  motor_a/b/c_rpm, motor_a/b/c_temp,
  camera_status, camera_fps, vision_confidence,
  predicted_landing_x/y, actual_landing_x/y,
  distance_error, lateral_error,
  battery_percent, system_errors
}
```

## Mock 数据

- 实时刷新（1秒间隔）：电机 RPM 微抖动、温度、电池缓慢下降
- 5-8秒随机错误：MOTOR_C_RPM_DRIFT（演示故障自动锁定）
- 弧线轨迹：根据当前模式 + RPM 实时计算抛物线

## 打开方式

```bash
# 浏览器
open cad/3d-print/control-panel-v23/control_panel_v1.html

# 或本地服务器
cd cad/3d-print/control-panel-v23
python3 -m http.server 8080
# 打开 http://localhost:8080/control_panel_v1.html
```

## 下一步

- V1.1：接入真实数据（替换 mock 为 CAN 总线数据）
- V1.2：加滑条实时响应（拖动滑条时曲线实时更新）
- V2.0：替换为 React/Vue 实现，集成 OpenCV 视觉

## 依赖

无（纯 HTML/CSS/JS，浏览器原生支持）。