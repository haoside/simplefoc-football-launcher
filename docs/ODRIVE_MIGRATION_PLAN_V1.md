# ODRIVE_MIGRATION_PLAN_V1

> 决策：P0-B 功率链路由 SimpleFOC 自建板切换为 **ODrive S1 ×3** 方案。
> 状态：已采纳（Owner 2026-08 指令），本文档取代 `ARCH_DECISION_BG431B_ESC1.md` 中的功率链路部分。
> B-G431B-ESC1 仍保留用于 P0-A 算法验证，不再进入实球功率链路。

## 1. 为什么切 ODrive（决策依据）

| 维度 | 原 SimpleFOC 多节点方案 | ODrive S1 方案 |
|---|---|---|
| 单轮 6374@24V 功率能力 | 需自研 DRV8353 板，硬件风险高 | 成熟产品，40A+ 连续（S1 标称 48A 峰值可配） |
| 电流环/速度环 | 自己调 SimpleFOC PID + 电流采样 | 出厂自带电流环，`vel_gain/integrator` 调参路径成熟 |
| Hall 支持 | 需自己适配 | ODrive 支持霍尔编码器（`ENCODER_MODE_HALL`） |
| 三机同步 | ESP32 上位机自己做 mixer 下发 | 同样 CAN 下发，但每轴有本地 20kHz 电流环，同步质量更高 |
| 保护链 | 自研过流/过温逻辑 | 内置 overcurrent / undervoltage / overtemp / stall |
| 固件开发量 | 3 套电机节点固件 | 零电机节点固件，全部配置态 |
| 成本 | 3×(~¥150 板) + 自研周期 | 3× S1 (~$200/块) 换掉整个硬件研发阶段 |

**核心论点**：项目瓶颈从来不是 FOC 算法，是"三个 40A 级功率级可靠地跑起来"。ODrive 把这部分变成货架产品。

## 2. 新系统架构

```
                 ┌────────────────────┐
                 │   ESP32-S3 主控     │  ← 保留：状态机 / 上球检测 / 急停仲裁 / UI
                 │   (host, 不变)      │
                 └─────────┬──────────┘
                           │ CAN 2.0FD? — 否, 经典 CAN 1Mbps
              ┌────────────┼────────────┐
        ┌─────┴─────┐ ┌────┴──────┐ ┌────┴──────┐
        │ ODrive S1 #1│ │ ODrive S1 #2│ │ ODrive S1 #3│
        │ axis0=WheelA│ │ axis0=WheelB│ │ axis0=WheelC│
        └─────┬──────┘ └────┬──────┘ └────┬──────┘
              │              │              │
           6374 A         6374 B         6374 C    (Hall 各自带)
```

- **CAN ID 分配**（沿用 `CAN_PROTOCOL_V1` 语义层，底层换 odrivetool/CANcmd）:
  - WheelA = 0x001, WheelB = 0x002, WheelC = 0x003
  - 主控命令帧使用 ODrive CAN 协议 `Set_Velocity` (0x00D)，反馈帧用 `Get_Encoder_Estimates` (0x009)
- **主控职责变化**：从"生成 PWM/FOC 命令"降级为"纯 CAN 发送器 + 安全状态机"，大幅简化 host 固件。

## 3. 电气与供电（复核后更新）

| 项 | 值 | 说明 |
|---|---|---|
| 电池 | 24V LiFePO4 60~80Ah | 3×6374@3000rpm 工作电流约 3×25A，峰值瞬时 3×50A |
| 总保险 | 150A ANL/MIDI | 主回路 |
| 预充 | 30Ω 10W + 继电器 | 必需！ODrive 上电涌电流大 |
| 每路分支保险 | 60A ×3 | |
| DC-LINK 电容 | ODrive 板载 | 无需外加 |
| 急停链路 | 物理按钮 → 主控 GPIO → CAN 广播 STOP + 硬件使能断路 | 双通道：软件急停 + 使能线硬断 |

## 4. 电机参数映射

```python
# odrivetool 配置（每个轴）
odrv0.axis0.config.motor.motor_type = MOTOR_TYPE_HIGH_CURRENT
odrv0.axis0.config.motor.poles = 14            # 6374 典型 14 极
odrv0.axis0.config.motor.resistance_calib_max_voltage = 2
odrv0.axis0.config.motor.requested_current_range = 60  # A
odrv0.axis0.config.motor.current_control_bandwidth = 1000
odrv0.axis0.encoder.config.mode = ENCODER_MODE_HALL
odrv0.axis0.encoder.config.cpr = 42             # 14 poles * 3 hall states
odrv0.controller.config.vel_limit = 350         # turns/s ≈ 3300RPM 机械极对数换算
odrv0.controller.config.vel_limit_tolerance = 1.2
odrv0.axis0.config.calibration_lockin.spin = False
odrv0.can.node_id = <1|2|3>
```

## 5. 迁移路线图

### Phase M1: 单轴台架复现（对应原 Milestone 1）
- [ ] ODrive S1 + 1×6374 + Hall，odrivetool 走完 calibration
- [ ] vel 模式阶跃响应记录（目标 500~3000 RPM 全范围扫）
- [ ] 过流/欠压保护实测触发
- 完成标准：3000 RPM 稳态 ±1%，突加负载恢复 <200ms

### Phase M2: 三轴 CAN 组网（对应原 Milestone 2）
- [ ] 3 台 ODrive 同一总线，node_id 1/2/3
- [ ] ESP32-S3 主控发送 `Set_Velocity` 帧 @100Hz
- [ ] 三轮转速差 <0.5% 稳态
- 完成标准：mixer 公式下发后三轮表面线速度一致

### Phase M3: 整机集成（合并原 Milestone 3、4、5）
- [ ] 新机械结构装机（见 MECH_REDESIGN_ODRIVE_V1.md）
- [ ] 状态机接入：IDLE → SPINUP → READY → LAUNCH → COOLDOWN
- [ ] 全故障注入测试（拔 Hall / 断 CAN / 堵转 / 急停）

## 6. BOM 变更

| 项 | 原 | 新 | Δ |
|---|---|---|---|
| 电机控制器 | B-G431B-ESC1 ×3 (~¥450) | **ODrive S1 ×3 (~¥4300)** | +¥3850 |
| 6374 电机 | ×3 保留 | ×3 保留 | 0 |
| Hall 线束 | 保留 | 保留（改接 ODrive JST） | ~0 |
| 主控 | ESP32-S3 保留 | 保留 | 0 |
| CAN 收发器 | 保留 | 保留 | 0 |
| 预充电路 | 无 | 新增 | +¥80 |
| 总计 | | | **约 ¥4000 增量** |

> 结论：花约 ¥4000 买掉"自研高电流 FOC 板"的整个硬件风险与 2~3 个月周期。P0-B 阶段这是正确交易；若未来量产 >100 台再评估自研。

## 7. 风险

| 风险 | 缓解 |
|---|---|
| ODrive S1 缺货/涨价 | 备选 Pro 版或 ODrive v3.6 56V 版（24V 下兼容） |
| Hall 精度不足导致低速抖动 | P0 只做高速预转，低速抖动不影响发射；后续可升级 AS5048A |
| CAN 总线 3 节点 @100Hz 负载 | 经典 CAN 1Mbps 余量充足，<15% 占用率 |
| ODrive 固件版本碎片 | 全部统一刷 ax v0.6.11+ 或 S1 出厂固件并冻结版本 |

## 8. 与现有文档的关系

- 取代：`ARCH_DECISION_BG431B_ESC1.md` 中"P0-B 用 SimpleFOC 高电流板"的结论
- 保留：`CAN_PROTOCOL_V1` 的语义层定义（速度指令/遥测/故障码），物理帧格式改为 ODrive CAN Protocol
- 保留：`FIRMWARE_BRINGUP_*` 的主机端流程，删除 motor-node-g431 固件目录的后续投入
- 新增：`MECH_REDESIGN_ODRIVE_V1.md`（机械结构重建）、`sim/odrive_launch_sim_v1.py`（仿真）
