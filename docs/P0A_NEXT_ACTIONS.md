# P0-A 下一步动作

## 立即动作

1. 按 `docs/procurement/P0A_PURCHASE_CHECKLIST_V1.md` 准备采购。
2. 用 `docs/procurement/P0A_SEARCH_KEYWORDS_V1.md` 搜索备选物料。
3. 物料到货后按 `docs/P0A_SINGLE_BALL_BRINGUP_V1.md` 执行台架测试。
4. 每次测试填 `docs/P0A_TEST_LOG_TEMPLATE_V1.md`。
5. 用实测数据回填 `sim/football_launch_model.py`。

## 当前不要做

- 不做多球仓 / 管道 / 闸门。
- 不做自动捡球机构，只保留接口。
- 不直接上 4000/5000rpm。
- 不在未装防护罩时做实球高速测试。
- 不把 B-G431B-ESC1 当最终高功率驱动。

## PM 临时决策

- P0-A：110mm 轮，3000rpm cap，5s ramp。
- P0-B 候选：130mm 轮，4000rpm cap，6s ramp。
- 采购优先级：安全件 > 控制件 > 电机轮组 > 结构件 > 高功率升级件。
