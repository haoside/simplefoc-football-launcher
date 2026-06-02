# Host 风环境修正 preset v1

## 新增 preset
- `standard_left_curve_wind_left`
- `standard_left_curve_wind_right`
- `standard_right_curve_wind_left`
- `standard_right_curve_wind_right`

## 参数
| preset | baseRpm | deltaRpm | spinMode | 用途 |
|---|---:|---:|---|---|
| standard_left_curve_wind_left | 2400 | 220 | LEFT_CURVE | 左侧风下抑制弧线过大 |
| standard_left_curve_wind_right | 2400 | 280 | LEFT_CURVE | 右侧风下补偿弧线被削弱 |
| standard_right_curve_wind_left | 2400 | 280 | RIGHT_CURVE | 左侧风下补偿右弧被削弱 |
| standard_right_curve_wind_right | 2400 | 220 | RIGHT_CURVE | 右侧风下抑制右弧过大 |

## 当前建议
- 2m/s 侧风优先改 `deltaRpm`
- 4m/s 侧风先用这组作为起点，再现场微调
- 先不做自动风补偿，先用人工切 preset

## 调试命令
直接使用：
- `preset standard_left_curve_wind_left`
- `preset standard_left_curve_wind_right`
- `preset standard_right_curve_wind_left`
- `preset standard_right_curve_wind_right`
