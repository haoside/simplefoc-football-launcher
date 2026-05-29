# ESP32-S3 Host 板电路图说明 v1

> 角色：上位控制板。负责 CAN 通信、供球机构控制、传感器采集、状态指示，不承担三路 FOC 实时闭环。

## 1. 电源
- 输入：`VIN_24V`
- 降压：`24V -> 5V` DCDC
- LDO：`5V -> 3V3`
- 电源网：
  - `VIN_24V`
  - `+5V`
  - `+3V3`
  - `PGND`
  - `GND`

### 关键器件
- `U1`：Buck Converter 24V->5V
- `U2`：LDO 5V->3V3
- `F1`：输入保险
- `TVS1`：24V 输入 TVS
- `CIN/COUT`：输入输出滤波电容

## 2. 主控
- `U3`：ESP32-S3-WROOM / WROOM-1
- 预留：`EN`、`BOOT`、`UART0_TX/RX`
- 调试口：USB-UART 或 6Pin Header

## 3. 通信
### CAN
- `U4`：CAN Transceiver
- ESP32-S3：
  - `CAN_TX`
  - `CAN_RX`
- CAN 侧：
  - `CAN_H`
  - `CAN_L`
- 终端电阻：`R_TERM`（跳帽可选）

## 4. 传感器输入
- `J1`：Tube Ball Sensor
  - `+5V`
  - `GND`
  - `SIG_TUBE`
- `J2`：Chamber Ball Sensor
  - `+5V`
  - `GND`
  - `SIG_CHAMBER`
- `J3`：Exit Sensor
  - `+5V`
  - `GND`
  - `SIG_EXIT`
- 每路建议：
  - 上拉/下拉电阻
  - RC 滤波
  - ESD 保护

## 5. 供球执行器输出
### 方案 A：舵机
- `J4`：SERVO
  - `+5V_SERVO`
  - `GND`
  - `PWM_FEED`

### 方案 B：电磁闸门
- `Q1`：N-MOSFET
- `D1`：续流二极管
- `J5`：SOLENOID
  - `VIN_24V`
  - `SOLENOID_LOW`

## 6. 急停与状态指示
- `J6`：ESTOP feedback input
  - `SIG_ESTOP`
- `D2/D3`：状态 LED
- `BZ1`：蜂鸣器（可选）

## 7. 建议 GPIO 映射
- `GPIO_CAN_TX` / `GPIO_CAN_RX`
- `GPIO_TUBE_SENSOR`
- `GPIO_CHAMBER_SENSOR`
- `GPIO_EXIT_SENSOR`
- `GPIO_FEED_PWM`
- `GPIO_ESTOP_IN`
- `GPIO_LED_STATUS`
- `GPIO_BUZZER`

## 8. 连接器建议
- 电源：3.81mm / 5.08mm 端子台
- CAN：4Pin（CANH/CANL/5V/GND）
- 传感器：JST-XH 3Pin
- 调试：1.27mm / 2.54mm 排针
