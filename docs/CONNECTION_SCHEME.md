# 连接方案 v1

详见：`docs/CONNECTION_DIAGRAM.md`

> 基于当前 BOM 草案：1 个上位控制板（ESP32-S3） + 3 个独立电机控制节点（STM32G431 + 三相驱动） + 多球管道供球。

## 1. 系统拓扑

```text
24V Power Input
 ├─ Main Switch
 ├─ Fuse / Breaker
 ├─ Emergency Stop (hardware cut-off for motor driver enable / power relay)
 ├─ 24V Bus -------------------------------------------------------------+
 │                                                                        |
 │   +--> Buck 24V->5V/3.3V --> ESP32-S3 Host                            |
 │   |                                                                    |
 │   +--> Motor Node A: STM32G431 -> DRV8353/DRV8302 -> BLDC A + Hall A  |
 │   |                                                                    |
 │   +--> Motor Node B: STM32G431 -> DRV8353/DRV8302 -> BLDC B + Hall B  |
 │   |                                                                    |
 │   +--> Motor Node C: STM32G431 -> DRV8353/DRV8302 -> BLDC C + Hall C  |
 │                                                                        |
 └─ Sensors: tube_ball_present / chamber_ball_ready / exit_ball_detect ---+
```

## 2. 电源连接

### 动力侧
- 24V DC 输入 -> 总开关 -> 总保险 -> 急停硬件回路 -> 三路驱动板 VM
- 三路驱动板共地，形成统一动力地
- 预留 36V 升级位，但 P0 仅按 24V 联调

### 逻辑侧
- 24V -> DCDC -> 5V/3.3V
- ESP32-S3 使用独立稳压输出
- 每个 STM32G431 节点可由本地 DCDC 或统一 5V 供电后再稳压到 3.3V
- 逻辑地与动力地单点共地，避免 Hall / 通信漂移

## 3. 主控与节点通信

### 推荐：CAN 总线
- ESP32-S3 通过 CAN Transceiver 接入总线
- Node A/B/C 各自一颗 CAN Transceiver
- 总线两端 120Ω 终端电阻
- 节点 ID：
  - Wheel A: `0x11`
  - Wheel B: `0x12`
  - Wheel C: `0x13`

### 最小消息
- Host -> Node
  - `SET_RPM(targetRpm, rampMs, enable)`
  - `ESTOP(code)`
  - `CLEAR_FAULT()`
  - `SET_PARAM(kp, ki, rpmLimit, currentLimit)`
- Node -> Host
  - `STATUS(actualRpm, targetRpm, busVoltage, phaseCurrent, temp, faultCode)`
  - `HEARTBEAT(aliveCounter)`
  - `FAULT(faultCode)`

## 4. 单个电机节点连接

### STM32G431 -> 三相驱动板
- `PWM_U / PWM_V / PWM_W` -> Driver INU / INV / INW
- `EN_GATE` -> Driver enable
- `FAULT_N` <- Driver fault output
- `CURRENT_SENSE` <- Driver / shunt output（若使用）
- `BUS_VOLTAGE_ADC` <- VM 分压采样

### STM32G431 -> Hall
- `HALL_A`
- `HALL_B`
- `HALL_C`
- `3V3`
- `GND`

### 驱动板 -> 电机
- `U / V / W` -> BLDC 三相线
- Hall 线束单独回 STM32，不走动力线束同束长距离并行

## 5. ESP32-S3 Host 连接

### 输入
- `tube_ball_present`：管道有球检测
- `chamber_ball_ready`：发射位到球检测
- `exit_ball_detect`：出球检测
- `estop_input`：急停状态反馈
- `gate_home / gate_ready`：单球分离机构到位（可选）

### 输出
- `feed_gate_pwm/dir` 或 `feed_gate_solenoid`
- `status_led`
- `buzzer`（可选）
- `can_tx/can_rx`

## 6. 单球分离机构连接

### 方案 A：舵机/减速电机拨叉
- Host PWM / DIR -> 分离机构驱动
- 原点/到位开关 -> Host GPIO
- 适合 P0 快速验证

### 方案 B：电磁闸门
- Host GPIO -> MOSFET -> Solenoid
- 回位弹簧复位
- 需要加续流保护

## 7. 安全联锁
- 急停必须硬件切断驱动使能或主接触器，不仅仅发总线命令
- `chamber_ball_ready=0` 时禁止进入 FIRE
- `tube_ball_present=0` 时禁止 RELOAD
- 任一 Node 上报 FAULT，Host 立即转 `FAULT`
- 通信超时 > 阈值，Host 拉低全部 enable

## 8. 线束建议
- 动力相线、Hall 线、CAN 线分开走线
- Hall 与 CAN 使用屏蔽或双绞线优先
- 星形配电，避免三路驱动共线过长导致压降不一致
- 传感器统一 5V 或 3.3V 制式，避免混压

## 9. P0 最小接线清单
- 24V 动力输入 ×1
- 主开关 ×1
- 急停 ×1
- DCDC ×1
- ESP32-S3 Host ×1
- STM32G431 + Driver Node ×3
- BLDC + Hall ×3
- 管道有球传感器 ×1
- 发射位到球传感器 ×1
- 出球检测传感器 ×1
- 分离机构执行器 ×1

