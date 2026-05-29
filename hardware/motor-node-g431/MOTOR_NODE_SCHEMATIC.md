# STM32G431 电机节点电路图说明 v1

> 角色：单路电机闭环控制节点。每个节点负责 1 个 BLDC + 1 个三相驱动 + 1 组 Hall 反馈。

## 1. 电源
- 输入：`VIN_24V`
- Buck：`24V -> 12V/10V`（按驱动器需求）
- LDO/Buck：`12V/5V -> 3V3`
- 电源网：
  - `VIN_24V`
  - `VDRV`
  - `+3V3`
  - `PGND`
  - `AGND`
  - `GND`

### 关键器件
- `F1`：节点输入保险/可恢复保险
- `TVS1`：24V TVS
- `U1`：Driver supply regulator
- `U2`：3.3V regulator

## 2. MCU
- `U3`：STM32G431CB / G431KB（按 IO 数量）
- 调试：SWD
  - `SWDIO`
  - `SWCLK`
  - `NRST`
  - `3V3`
  - `GND`

## 3. 三相驱动
- `U4`：DRV8353 / DRV8302 级驱动
- MCU -> Driver
  - `PWM_UH / PWM_UL`
  - `PWM_VH / PWM_VL`
  - `PWM_WH / PWM_WL`
  - 或按 3PWM 模式：`PWM_U / PWM_V / PWM_W`
  - `DRV_EN`
  - `DRV_FAULT_N`
- Driver -> MOSFET / Power Stage
  - `GH_x / GL_x`
  - `SH_x / PHASE_x`

## 4. 功率级
- 3 相半桥 ×3
- 分流电阻：
  - `SHUNT_A`
  - `SHUNT_B`
  - `SHUNT_C`（可选）
- 采样：
  - `ISENSE_A`
  - `ISENSE_B`
- 母线电压采样：`VBUS_SENSE`

## 5. 电机接口
- `J1`：Motor Phases
  - `U`
  - `V`
  - `W`
- `J2`：Hall Sensor
  - `3V3`
  - `GND`
  - `HALL_A`
  - `HALL_B`
  - `HALL_C`

## 6. 通信
- `U5`：CAN Transceiver
- MCU:
  - `CAN_TX`
  - `CAN_RX`
- Connector:
  - `CAN_H`
  - `CAN_L`
  - `GND`

## 7. 保护
- `DRV_FAULT_N` -> MCU EXTI
- `VBUS_SENSE` -> ADC
- `ISENSE_A/B` -> ADC
- NTC / TEMP -> ADC（可选）

## 8. 连接器建议
- 电源输入：大电流端子
- 电机相线：螺丝端子 / XT30 级别
- Hall：JST-XH 5Pin
- CAN：JST-GH / XT30 小信号分离
- SWD：1.27mm 5Pin
