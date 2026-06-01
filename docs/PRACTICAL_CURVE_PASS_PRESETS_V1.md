# 实战型弧线助攻球参数草案 v1

## 项目目标口径
替代人力喂球/传球，面向真实足球训练场景，稳定、可重复地输出实战型边路弧线传球。

## P0 验收导向
- 稳定出球
- 可重复
- 有可区分的直传 / 轻弧线 / 标准弧线
- 落点偏差可记录、可调参

## 预设参数
| 名称 | baseRpm | deltaRpm | spinMode | 发射角 | 目标距离 | 横向偏移 |
|---|---:|---:|---|---:|---:|---:|
| straight_pass | 2100 | 0 | STRAIGHT | 10° | 15m | 0m |
| light_left_curve | 2100 | 150 | LEFT_CURVE | 12° | 16m | 1.0m |
| light_right_curve | 2100 | 150 | RIGHT_CURVE | 12° | 16m | 1.0m |
| standard_left_curve | 2400 | 250 | LEFT_CURVE | 14° | 20m | 2.0m |
| standard_right_curve | 2400 | 250 | RIGHT_CURVE | 14° | 20m | 2.0m |
| curve_drop_left | 2300 | 220 | LEFT_CURVE | 15° | 18m | 1.5m |
| curve_drop_right | 2300 | 220 | RIGHT_CURVE | 15° | 18m | 1.5m |

## 解释
- `baseRpm` 决定主前向速度
- `deltaRpm` 决定侧旋强度
- `spinMode` 决定 wheel1/2/3 的目标 rpm 分配
- `发射角` 是整机俯仰角建议，不是轮速参数

## 轨迹稳定关键点
1. 三轮接触一致
2. 预压一致
3. 轮面材料一致
4. actualRpm 能稳定跟踪 targetRpm
5. 短导向筒只做短导向，不明显摩擦球面
