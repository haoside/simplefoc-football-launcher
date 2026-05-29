# Host 板原理图分页结构 v1

## 建议分页

### Page H1 - Power Input & Regulators
**内容**
- J_PWR
- F1
- TVS1
- Buck 24V -> 5V
- LDO/Buck 5V -> 3.3V
- 电源指示灯

**页间导出网络**
- `VIN_24V`
- `+5V`
- `+3V3`
- `PGND`
- `GND`

---

### Page H2 - ESP32-S3 Core
**内容**
- ESP32-S3 模组
- EN / BOOT
- 下载 / 调试串口
- 基础去耦

**页间导入网络**
- `+3V3`
- `GND`

**页间导出网络**
- `CAN_TX`
- `CAN_RX`
- `SIG_TUBE`
- `SIG_CHAMBER`
- `SIG_EXIT`
- `SIG_ESTOP`
- `PWM_FEED`
- `FEED_DIR`
- `LED_STATUS`
- `BUZZER_CTL`
- `UART0_TX`
- `UART0_RX`

---

### Page H3 - CAN & Debug
**内容**
- CAN transceiver
- 终端电阻选择
- CAN 接口
- Debug Header

**页间导入网络**
- `+3V3`
- `GND`
- `CAN_TX`
- `CAN_RX`
- `UART0_TX`
- `UART0_RX`

**页间导出网络**
- `CAN_H`
- `CAN_L`

---

### Page H4 - Sensor Inputs
**内容**
- 管道有球传感器接口
- 发射位到球传感器接口
- 出球传感器接口
- 急停反馈接口
- 输入滤波 / 上拉 / ESD

**页间导入网络**
- `+5V`
- `GND`
- `SIG_TUBE`
- `SIG_CHAMBER`
- `SIG_EXIT`
- `SIG_ESTOP`

---

### Page H5 - Feed Actuator & Indicators
**内容**
- 舵机接口 或 电磁闸门驱动
- MOSFET + flyback
- 状态灯 / 蜂鸣器

**页间导入网络**
- `VIN_24V`
- `+5V`
- `GND`
- `PWM_FEED`
- `FEED_DIR`
- `LED_STATUS`
- `BUZZER_CTL`
