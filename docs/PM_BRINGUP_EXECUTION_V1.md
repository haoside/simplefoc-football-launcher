# P0-A Bring-up 执行手册 v1

> 由 Mia｜PM 整合，基于 firmware bring-up plan、hardware docs、procurement checklist。
> 最后更新：2026-07-01

## 前置条件

| # | 条件 | 状态 |
|---|------|------|
| 1 | P0-A 物料到位 | ⏳ 采购中 |
| 2 | 固件代码编译通过 | ✅ 代码库已有 |
| 3 | 结构 v12 CAD 定型 | ✅ `cad/3d-print/tri-motor-6374-v12/` |
| 4 | PCB 打样完成 | ⏳ 待打样 |

## 执行顺序

### 阶段 1：最小 Host 固件（无外设）

**目标**：ESP32-S3 跑起来，串口能打印，CAN 能初始化

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 1.1 | 烧录 host-esp32s3 固件 | SWD 下载成功 | `firmware/host-esp32s3/` |
| 1.2 | 连接串口查看 boot log | 打印版本号 + 初始化日志 | `docs/DEBUG_GUIDE_V1.md` |
| 1.3 | 检查 CAN 初始化 | CAN 控制器进入正常模式 | `docs/CAN_PROTOCOL_V1.md` |
| 1.4 | GPIO 轮询传感器输入 | ball_present / exit_detect / estop 状态可见 | `docs/SENSOR_LAYOUT.md` |

**通过标准**：串口有 boot log，GPIO 状态变化可见，CAN 正常模式。

### 阶段 2：最小 Node 固件（无电机）

**目标**：STM32G431 跑起来，Driver 不报错，ADC 能读

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 2.1 | 烧录 node-bg431b-esc1 固件 | SWD 下载成功 | `firmware/node-bg431b-esc1/` |
| 2.2 | 上电检查 3.3V / VBUS | 电压值合理 | `hardware/pinout/MOTOR_NODE_PINOUT.md` |
| 2.3 | 检查 Driver FAULT_N | 无误报 fault | `docs/FIRMWARE_BRINGUP_CHECKLIST.md` |
| 2.4 | 检查 VBUS_SENSE ADC | 读数合理 | — |

**通过标准**：下载正常，Driver 无 fault，VBUS 读数合理。

### 阶段 3：Hall 读取

**目标**：手转电机时能读到正确的 Hall 状态和转速

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 3.1 | 连接 Hall 线束到 Node | 物理连接完成 | `hardware/pinout/CONNECTOR_TABLE.md` |
| 3.2 | 手转电机，观察 Hall 状态 | A/B/C 相序正确变化 | `docs/FIRMWARE_BRINGUP_PLAN.md` Phase 2 |
| 3.3 | 验证转速计算 | rpm 数值连续、无乱跳 | — |

**通过标准**：手转电机时 Hall 状态正确，转速连续。

### 阶段 4：Driver PWM + 单电机开环

**目标**：PWM 波形正常，电机能低速转动

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 4.1 | 脱开电机负载，验证 PWM | 示波器看到 3 路 PWM | `docs/FIRMWARE_BRINGUP_PLAN.md` Phase 3 |
| 4.2 | 验证 enable/fault 联锁 | DRV_EN 可控，fault 后 PWM 关断 | — |
| 4.3 | 接上电机，开环低速测试 | 电机低速平稳转动 | Phase 4 |
| 4.4 | 检查限流/限速 | 无异常发热、无明显振动 | — |

**通过标准**：PWM 正常，电机低速可控，无异常。

### 阶段 5：单电机速度闭环

**目标**：500–3000rpm 速度闭环稳定

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 5.1 | 切换到 velocity loop | SET_RPM 生效 | `docs/FIRMWARE_BRINGUP_PLAN.md` Phase 5 |
| 5.2 | 500rpm 测试 | 稳态误差 ±3% | — |
| 5.3 | 1000/2000/3000rpm 递增 | 各转速稳定 | — |
| 5.4 | 急停测试 | 急停后安全停机 | `docs/FAULT_SAFETY_CHAIN.md` |

**通过标准**：目标转速可跟踪，稳态误差 ±3%，急停有效。

### 阶段 6：Host ↔ Node 联调

**目标**：Host 可下发 RPM，Node 回传状态，超时保护生效

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 6.1 | Host 发 SET_RPM，Node 响应 | Node 转速跟随 Host 指令 | `docs/CAN_PROTOCOL_V1.md` |
| 6.3 | Node 周期发 STATUS/HEARTBEAT | Host 收到状态帧 | `docs/FIRMWARE_COMM_LOOP.md` |
| 6.3 | 拔掉 CAN 线 | 系统进入 FAULT 保护 | `docs/FAULT_SAFETY_CHAIN.md` |

**通过标准**：通信正常，超时保护生效。

### 阶段 7：三 Node 联调

**目标**：三轮同步启动，轮间偏差 < 150ms

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 7.1 | 三节点同时上线 | 三节点 CAN 帧均可见 | `docs/HOST_3NODE_INTEGRATION_DEMO_V1.md` |
| 7.2 | 三轮同步启动 | 90% 目标转速时间差 < 150ms | `docs/RPM_MIXER_120DEG.md` |
| 7.3 | 轮间偏差记录 | 偏差在目标范围内 | — |

**通过标准**：三轮同步，偏差 < 150ms。

### 阶段 8：发射状态机 + 低速射球

**目标**：手动上球 → 检测 → 发射 → 出球完整链路

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 8.1 | 状态机代码验证 | IDLE→SPINUP→READY→FIRE→COOLDOWN 跑通 | `firmware/host-esp32s3/src/launch_state_machine.cpp` |
| 8.2 | 球检测传感器验证 | 手动放球检测正确 | `docs/SENSOR_LAYOUT.md` |
| 8.3 | 无球禁止发射 | ball_present=0 时禁止 FIRE | `docs/FEED_STATE_MACHINE_V1.md` |
| 8.4 | 低速单球射出 | 单次稳定射出标准 5 号球 | — |
| 8.5 | 出球超时保护 | 超时后进入 FAULT | — |

**通过标准**：手动上球可稳定射出，无球不能发射，超时保护有效。

### 阶段 9：15~20m 长传验证

**目标**：达到目标射程，记录数据回填仿真

| 步骤 | 动作 | 验收 | 参考 |
|------|------|------|------|
| 9.1 | 逐步提升转速 | 500→1000→1500→2000rpm | — |
| 9.2 | 记录射程/精度 | 每档转速至少 5 次 | `docs/P0_FIELD_TEST_LOG_TEMPLATE_V2.md` |
| 9.3 | 数据回填仿真 | `sim/football_launch_model.py` 参数更新 | `sim/` |
| 9.4 | 安全件全程到位 | 防护罩 + 急停 + 人员远离射出方向 | `docs/SAFETY` |

**通过标准**：15~20m 射程达成，数据有记录。

## 关键文档索引

| 文档 | 用途 |
|------|------|
| `docs/FIRMWARE_BRINGUP_PLAN.md` | 固件分阶段计划 |
| `docs/FIRMWARE_BRINGUP_CHECKLIST.md` | 固件验收清单 |
| `docs/CAN_PROTOCOL_V1.md` | CAN 通信协议 |
| `docs/FAULT_SAFETY_CHAIN.md` | 故障保护链路 |
| `docs/SENSOR_LAYOUT.md` | 传感器布局 |
| `docs/DEBUG_GUIDE_V1.md` | 调试指南 |
| `docs/P0A_TEST_KANBAN_V1.md` | P0-A 测试看板 |
| `docs/procurement/PROCUREMENT_P0A_V2.md` | 采购清单 |
| `cad/3d-print/tri-motor-6374-v12/` | 结构 CAD v12 |
| `hardware/FIRST_SPIN_BRINGUP.md` | 首版上电注意事项 |
