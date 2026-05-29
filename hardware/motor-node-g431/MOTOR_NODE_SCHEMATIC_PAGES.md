# Motor Node 板原理图分页结构 v1

## 建议分页

### Page M1 - Power Input & Supplies
**内容**
- J_PWR
- F1
- TVS1
- 输入滤波
- Driver 电源 `VDRV`
- MCU 逻辑电源 `+3V3`

**页间导出网络**
- `VIN_24V`
- `VDRV`
- `+3V3`
- `PGND`
- `AGND`
- `GND`

---

### Page M2 - STM32G431 Core
**内容**
- STM32G431
- 时钟 / 复位
- SWD 接口
- 去耦电容

**页间导入网络**
- `+3V3`
- `GND`

**页间导出网络**
- `PWM_U`
- `PWM_V`
- `PWM_W`
- `DRV_EN`
- `DRV_FAULT_N`
- `HALL_A`
- `HALL_B`
- `HALL_C`
- `ISENSE_A`
- `ISENSE_B`
- `VBUS_SENSE`
- `TEMP_SENSE`
- `CAN_TX`
- `CAN_RX`
- `SWDIO`
- `SWCLK`
- `NRST`

---

### Page M3 - Gate Driver
**内容**
- DRV8353 / DRV8302
- bootstrap 电容
- gate 电阻
- 使能 / 故障脚

**页间导入网络**
- `VDRV`
- `PGND`
- `PWM_U`
- `PWM_V`
- `PWM_W`
- `DRV_EN`
- `DRV_FAULT_N`
- `ISENSE_A`
- `ISENSE_B`

**页间导出网络**
- `GH_U/GL_U`
- `GH_V/GL_V`
- `GH_W/GL_W`
- `SH_U`
- `SH_V`
- `SH_W`

---

### Page M4 - MOSFET Power Stage
**内容**
- 三相半桥
- DC Link 电容
- Shunt 电阻
- 电机接口

**页间导入网络**
- `VIN_24V`
- `PGND`
- `GH_U/GL_U`
- `GH_V/GL_V`
- `GH_W/GL_W`
- `SH_U`
- `SH_V`
- `SH_W`

**页间导出网络**
- `PHASE_U`
- `PHASE_V`
- `PHASE_W`
- `ISENSE_A`
- `ISENSE_B`

---

### Page M5 - Hall / Voltage / Temp Sense
**内容**
- Hall 接口
- 上拉 / 滤波
- VBUS 分压
- NTC 温度采样

**页间导入网络**
- `+3V3`
- `GND`
- `AGND`
- `HALL_A`
- `HALL_B`
- `HALL_C`
- `VBUS_SENSE`
- `TEMP_SENSE`

---

### Page M6 - CAN Interface
**内容**
- CAN transceiver
- 终端电阻选择
- CAN 接口

**页间导入网络**
- `+3V3`
- `GND`
- `CAN_TX`
- `CAN_RX`

**页间导出网络**
- `CAN_H`
- `CAN_L`
