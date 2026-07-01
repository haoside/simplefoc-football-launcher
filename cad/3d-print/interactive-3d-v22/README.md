# Interactive 3D Display — v22

## 用途

用 **Plotly** 生成可独立运行的交互式 3D HTML：
- 鼠标拖动旋转
- 滚轮缩放
- 点击按钮切换模式
- Hover 查看数据

无需 Python / 服务器，本地浏览器直接打开。

## 3 个 HTML

| 文件 | 用途 |
|------|------|
| `interactive_5modes.html` | **主交互**：5 模式按钮切换轨迹（STRAIGHT / LEFT_CURVE / RIGHT_CURVE / TOPSPIN / BACKSPIN）|
| `interactive_default.html` | 默认直线球 3D 视图 |
| `propulsion_comparison.html` | 3 推进方式对比（tangent_friction / 8bar / 50m pneumatic）|

## 物理模型

- 球轨迹 = 抛物线 + 空气阻力（Cd=0.25）+ Magnus 效应
- Magnus 系数 k_lat=0.42（侧向）, k_vert=0.30（上下）
- 旋转 = 3 电机 RPM 差速
- 出膛速度 = 取决于推进方式：
  - `tangent_friction`：3 切向滚轮摩擦（≈3-5 m/s）
  - `pneumatic_8bar`：8 bar / 5 L / 200 mm（≈63 m/s）
  - `pneumatic_50m`：8 bar / 20 L / 400 mm（≈90 m/s）

## 重新生成

```bash
pip install plotly manifold3d
cd football-launcher-3d
python3 scripts/build_interactive_3d.py
```

## 本地查看

直接浏览器打开 HTML：

```bash
open cad/3d-print/interactive-3d-v22/interactive_5modes.html
```

## 控制操作

- 鼠标左键拖动：旋转视角
- 鼠标右键拖动：平移
- 滚轮：缩放
- 左上角按钮：切换模式 / 视角

## 已知限制

- Plotly HTML 单文件包含 Plotly.js（CDN）— 首次打开需联网
- 中文不在 Plotly 默认字体中（用英文标签）
- 旋转动画需要 JS（不在本版本）

## 进阶（未做）

- [ ] Slider 实时调 RPM
- [ ] 球沿轨迹动画（按帧）
- [ ] 视频导出
- [ ] 实测数据导入做校准

## 依赖

```bash
pip install plotly manifold3d matplotlib numpy
```