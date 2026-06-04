# P0-A 测试看板 v1

## 当前目标

从采购到低速单球射出，形成最小闭环。

## 状态栏

### TODO

| ID | 任务 | 负责人 | 阻塞 |
|---|---|---|---|
| P0A-01 | P0-A 物料下单 | owner / PM | 采购确认 |
| P0A-02 | 台架电源与急停链路接线 | engineering | 物料到货 |
| P0A-03 | 单个 B-G431B-ESC1 上电 | engineering | 物料到货 |
| P0A-04 | 单电机 Hall 读取 | engineering | 电机到货 |
| P0A-05 | 单电机 500/1000/2000rpm | engineering | P0A-04 |
| P0A-06 | 三电机 CAN 通信 | engineering | P0A-03 |
| P0A-07 | 三轮同步空载 | engineering | P0A-05/P0A-06 |
| P0A-08 | 防护罩安装 | mechanical | PC 板到货 |
| P0A-09 | 急停硬切验证 | engineering | P0A-02 |
| P0A-10 | 低速单球 B1/B2/B3 | engineering | P0A-07/P0A-08/P0A-09 |
| P0A-11 | 轻弧线 C1 | engineering | P0A-10 稳定 |
| P0A-12 | 实测数据回填仿真 | PM / engineering | P0A-10/P0A-11 |

### DOING

| ID | 任务 | 备注 |
|---|---|---|
|  |  |  |

### DONE

| ID | 任务 | 证据 |
|---|---|---|
| DOC-01 | P0-A 仿真模型 | `sim/football_launch_model.py` |
| DOC-02 | P0-A 采购清单 | `docs/procurement/P0A_PURCHASE_CHECKLIST_V1.md` |
| DOC-03 | P0-A 测试记录表 | `docs/P0A_TEST_LOG_TEMPLATE_V1.md` |

## 升级条件

只有满足以下条件，才进入 P0-B 高电流/现场测试：

1. 三轮空载同步通过。
2. 急停硬切通过。
3. 低速单球出球稳定。
4. 电流峰值有记录。
5. 防护罩完整。
6. 仿真参数完成第一次回填。
