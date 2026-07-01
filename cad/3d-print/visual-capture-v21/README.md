# Visual Capture + Control + Arc Simulation — v21

## 用途

一体化展示：
1. **3D 发射器渲染** + 实时轨迹
2. **控制参数面板**（3 电机 RPM、发射角、推进方式）
3. **5 种旋转模式弧线对比**（直线/左曲线/右曲线/上旋/下旋）

## 文件清单

| 文件 | 内容 |
|------|------|
| `visual_capture_v21.png` | **主综合图**：3D 发射器 + 控制面板 + 5 模式轨迹 |
| `control_adjustment_v21.png` | 控制调节对比（直线/左曲线/右曲线）|
| `arc_straight.png` | 直线球轨迹（独立大图）|
| `arc_left_curve.png` | 左曲线球轨迹 |
| `arc_right_curve.png` | 右曲线球轨迹 |
| `arc_topspin.png` | 上旋球轨迹（低平）|
| `arc_backspin.png` | 下旋球轨迹（高抛）|
| `visual_capture.py` | 重新生成脚本 |

## 5 模式配置

| 模式 | W1 RPM | W2 RPM | W3 RPM | 效果 |
|------|--------|--------|--------|------|
| STRAIGHT    | 2500 | 2500 | 2500 | 直线 |
| LEFT_CURVE  | 2300 | 2700 | 2500 | 向左偏 |
| RIGHT_CURVE | 2700 | 2500 | 2300 | 向右偏 |
| TOPSPIN     | 2800 | 2400 | 2300 | 球加速下坠（低平）|
| BACKSPIN    | 2300 | 2400 | 2800 | 球上飘（高抛）|

## 推进方式

- `tangent_friction`：3 切向滚轮摩擦驱动（v18 物理）
- `pneumatic_8bar`：8 bar 气压（主推）
- `pneumatic_8bar_50m`：8 bar / 20 L / 400 mm（50 m 目标）
- `manual`：手动设置出膛速度

## 控制参数

- 3 电机 RPM（每个独立）
- 发射角（默认 8°，轨迹图用 12°）
- 推进方式选择
- 出膛速度自动计算

## 重新生成

```bash
cd football-launcher-3d
python3 scripts/visual_capture.py
```

## 物理模型

球轨迹 = 抛物线 + 空气阻力 + Magnus 效应

```python
F_drag = 0.5 × ρ × Cd × A × v²
F_magnus_lat = k_lat × ω × v  (侧向)
F_magnus_vert = k_vert × ω × v  (上下)
```

系数（需现场校准）：
- ρ = 1.225 kg/m³
- Cd = 0.25（球）
- k_lat = 0.42, k_vert = 0.30

## 局限

- 中文字符显示为方框（matplotlib 缺中文字体）— 用英文标识
- Magnus 系数是经验值，需要实际校准
- 3D 渲染中轨迹和发射器比例可能不完美

## 后续

- 加交互式 HTML（Plotly）
- 加现场校准工作流
- 加视频帧序列（球动画）

## 依赖

```bash
pip install manifold3d matplotlib numpy
```