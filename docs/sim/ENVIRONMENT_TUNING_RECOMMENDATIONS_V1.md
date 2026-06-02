# 基于环境仿真结果的参数修正建议 v1

## 前提
基于：
- `docs/sim/ENVIRONMENT_SIM_RESULTS_V1.md`
- `sim/curve_ball_sim_v1.py`

目标：在不同风环境下，给出更接近训练落点的 preset 修正口径。

## 1. 无风 / 实验室基线（E0 + W0）
### straight_pass
- 保持：`baseRpm = 2100`
- `deltaRpm = 0`
- 发射角：`10°`

### standard_left_curve / standard_right_curve
- 保持：`baseRpm = 2400`
- 保持：`deltaRpm = 250`
- 发射角：`14°`

> 结论：无风下不需要额外补偿，当前 preset 可以直接作为标定基线。

## 2. 常规训练环境（E1 + 无风）
### straight_pass
- 不调

### light_left/right_curve
- 不调或只做小修正：`deltaRpm ±20`

### standard_left/right_curve
- 不调

> 结论：温度/湿度变化对当前近似结果影响不大，可沿用基线参数。

## 3. 2m/s 侧风环境
### 左侧风 + left_curve
仿真现象：弧线被放大（0.49m -> 0.64m）

建议：
- `deltaRpm` 从 `250` 下调到 `220 ~ 230`
- 或发射角从 `14°` 降到 `13°`

### 右侧风 + left_curve
仿真现象：弧线被削弱（0.49m -> 0.35m）

建议：
- `deltaRpm` 从 `250` 上调到 `270 ~ 290`
- 或 `baseRpm` 小幅上调 `+50 ~ +100`

### 左侧风 + right_curve
仿真现象：右弧被削弱

建议：
- `deltaRpm` 从 `250` 上调到 `270 ~ 290`

### 右侧风 + right_curve
仿真现象：右弧被放大

建议：
- `deltaRpm` 从 `250` 下调到 `220 ~ 230`

> 结论：**2m/s 侧风优先修 deltaRpm，不优先大改 baseRpm。**

## 4. 4m/s 侧风 / 不利环境（E2）
### straight_pass
仿真现象：无弧线也会出现 0.15m 级横向漂移

建议：
- 可保持 `baseRpm = 2100`
- 训练端通过站位/瞄准做补偿

### standard_left_curve（左侧风）
仿真现象：弧线被明显放大到 `0.80m`

建议：
- `deltaRpm` 从 `250` 下调到 `180 ~ 210`
- 必要时将发射角从 `14°` 下调到 `12° ~ 13°`

### standard_right_curve（左侧风）
仿真现象：右弧被明显削弱到 `0.19m`

建议：
- `deltaRpm` 从 `250` 上调到 `300 ~ 330`
- `baseRpm` 上调 `+50 ~ +100` 仅作为第二优先

> 结论：**4m/s 侧风下，单靠固定 preset 很难保证对称效果，建议分环境预设。**

## 5. 建议新增环境修正预设
### `standard_left_curve_wind_left`
- `baseRpm = 2400`
- `deltaRpm = 220`
- `spinMode = LEFT_CURVE`

### `standard_left_curve_wind_right`
- `baseRpm = 2400`
- `deltaRpm = 280`
- `spinMode = LEFT_CURVE`

### `standard_right_curve_wind_left`
- `baseRpm = 2400`
- `deltaRpm = 280`
- `spinMode = RIGHT_CURVE`

### `standard_right_curve_wind_right`
- `baseRpm = 2400`
- `deltaRpm = 220`
- `spinMode = RIGHT_CURVE`

## 6. 工程建议优先级
1. 先在无风下把基线 preset 跑稳
2. 再做 2m/s 侧风修正
3. 最后再考虑 4m/s 侧风环境专用 preset
4. 先改 `deltaRpm`，后改 `baseRpm`，最后才改发射角

## 7. 当前建议
- P0 现场主用：基线 preset
- 有风环境：增加“wind-left / wind-right” 修正 preset
- 不建议在 P0 就把温度、湿度、风速全部自动补偿到实时控制闭环里，先做人工可切换 preset 更稳
