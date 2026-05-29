# Motor Node 子电路说明 v1

## 1. 电源子电路
### 输入
- `VIN_24V`
- `PGND`

### 结构
- 输入保险
- TVS 钳位
- 大电容 + 小电容滤波
- Buck 到 `VDRV`
- LDO/Buck 到 `+3V3`

### 设计要点
- `VIN_24V` 与 `PGND` 走线加宽
- Buck 回路面积最小
- `+3V3` 单独净化供给 MCU / Hall / CAN

## 2. 驱动子电路
### 输入
- MCU 输出 `PWM_U/PWM_V/PWM_W`
- `DRV_EN`
- `DRV_FAULT_N`

### 输出
- Gate Driver -> MOSFET 栅极
- Driver 感知电流 / 故障

### 设计要点
- Bootstrap 电容贴近驱动脚
- Gate 电阻对称
- FAULT 线远离功率区

## 3. MCU 子电路
### 必要信号
- `HALL_A/B/C`
- `ISENSE_A/B`
- `VBUS_SENSE`
- `CAN_TX/RX`
- `SWDIO/SWCLK`
- `DRV_EN/DRV_FAULT_N`

### 设计要点
- 去耦紧贴 VDD/VSS
- ADC 参考与模拟地处理干净
- SWD 口靠板边

## 4. 功率级子电路
### 结构
- U/V/W 三相半桥
- 每相上/下 MOSFET
- 相电流采样（至少两相）
- 母线电容靠近功率桥

### 设计要点
- 大电流环路最短
- 相线端子靠板边
- Shunt Kelvin 引出
- 功率地回流清晰

## 5. Hall / CAN 子电路
### Hall
- 3.3V 供电
- A/B/C 三路输入
- 近接口加保护与上拉

### CAN
- MCU -> 收发器 -> `CAN_H/CAN_L`
- 末端节点选装 120R
- 差分对并行走线
