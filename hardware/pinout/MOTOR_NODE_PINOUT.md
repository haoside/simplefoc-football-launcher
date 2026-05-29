# Motor Node 板引脚网表 / Pinout v1

> 单节点 = 单电机。用于 KiCad 原理图录入与 PCB 引脚定义。

## U3 - STM32G431 逻辑分配

| Signal | Direction | Function | Notes |
|---|---|---|---|
| `PWM_U` | OUT | Driver PWM U | 3PWM 模式 |
| `PWM_V` | OUT | Driver PWM V | 3PWM 模式 |
| `PWM_W` | OUT | Driver PWM W | 3PWM 模式 |
| `DRV_EN` | OUT | 驱动使能 | 急停时应可被上游切断 |
| `DRV_FAULT_N` | IN | 驱动故障输入 | EXTI |
| `HALL_A` | IN | Hall A | 定时器捕获/EXTI |
| `HALL_B` | IN | Hall B | 定时器捕获/EXTI |
| `HALL_C` | IN | Hall C | 定时器捕获/EXTI |
| `ISENSE_A` | ADC IN | 相电流采样 A | Kelvin 引出 |
| `ISENSE_B` | ADC IN | 相电流采样 B | Kelvin 引出 |
| `VBUS_SENSE` | ADC IN | 母线电压采样 | 分压+RC |
| `TEMP_SENSE` | ADC IN | 温度采样 | 可选 |
| `CAN_TX` | OUT | CAN TX | 到 CAN 收发器 |
| `CAN_RX` | IN | CAN RX | 来自 CAN 收发器 |
| `SWDIO` | BIDIR | SWD 调试 | |
| `SWCLK` | IN | SWD 调试 | |
| `NRST` | IN | Reset | |

## 连接器定义

### J_PWR
| Pin | Net | Notes |
|---|---|---|
| 1 | `VIN_24V` | 节点 24V 输入 |
| 2 | `PGND` | 功率地 |

### J_MOTOR
| Pin | Net |
|---|---|
| 1 | `PHASE_U` |
| 2 | `PHASE_V` |
| 3 | `PHASE_W` |

### J_HALL
| Pin | Net |
|---|---|
| 1 | `+3V3_HALL` |
| 2 | `GND` |
| 3 | `HALL_A` |
| 4 | `HALL_B` |
| 5 | `HALL_C` |

### J_CAN
| Pin | Net |
|---|---|
| 1 | `CAN_H` |
| 2 | `CAN_L` |
| 3 | `GND` |

### J_SWD
| Pin | Net |
|---|---|
| 1 | `3V3` |
| 2 | `SWDIO` |
| 3 | `SWCLK` |
| 4 | `NRST` |
| 5 | `GND` |

## 关键网络
- `VIN_24V`
- `VDRV`
- `+3V3`
- `PGND`
- `AGND`
- `GND`
- `PHASE_U / PHASE_V / PHASE_W`
- `HALL_A / HALL_B / HALL_C`
- `ISENSE_A / ISENSE_B`
- `VBUS_SENSE`
- `DRV_FAULT_N`
- `DRV_EN`
