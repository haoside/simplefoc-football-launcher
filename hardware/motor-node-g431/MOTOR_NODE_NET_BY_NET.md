# Motor Node 板 net-by-net 原理图连接表 v1

## 1. 电源入口
| Net | From | To | Notes |
|---|---|---|---|
| `VIN_24V` | J_PWR.1 | F1 -> TVS1 -> U1.IN -> DC Link Caps | 节点主电源 |
| `PGND` | J_PWR.2 | TVS1.GND -> Power return -> Shunt return | 功率地 |

## 2. 驱动 / 逻辑供电
| Net | From | To | Notes |
|---|---|---|---|
| `VDRV` | U1.OUT | U4.VM / U4.VCP related rails | Driver 供电 |
| `+3V3` | U2.OUT | U3.VDD, U5.VCC, J_HALL.1 | MCU/CAN/Hall |
| `AGND` | Analog return | ADC front-end / divider / NTC | 模拟参考地 |
| `GND` | Logic ground | MCU / CAN / Hall return | 逻辑地 |

## 3. MCU 与 Driver
| Net | From | To | Notes |
|---|---|---|---|
| `PWM_U` | U3.TIMx_CH1 | U4.IN_U | 3PWM 模式 |
| `PWM_V` | U3.TIMx_CH2 | U4.IN_V | 3PWM 模式 |
| `PWM_W` | U3.TIMx_CH3 | U4.IN_W | 3PWM 模式 |
| `DRV_EN` | U3.GPIO_DRV_EN | U4.EN | 驱动使能 |
| `DRV_FAULT_N` | U4.FAULT_N | U3.GPIO_DRV_FAULT | 故障输入 |

## 4. Driver 与功率级
| Net | From | To | Notes |
|---|---|---|---|
| `GH_U/GL_U` | U4 | QH_U / QL_U | U 相栅极 |
| `GH_V/GL_V` | U4 | QH_V / QL_V | V 相栅极 |
| `GH_W/GL_W` | U4 | QH_W / QL_W | W 相栅极 |
| `SH_U` | Half-bridge U | U4.SH_U | 开关节点 |
| `SH_V` | Half-bridge V | U4.SH_V | 开关节点 |
| `SH_W` | Half-bridge W | U4.SH_W | 开关节点 |

## 5. 电机输出
| Net | From | To | Notes |
|---|---|---|---|
| `PHASE_U` | Half-bridge U | J_MOTOR.1 | 电机 U |
| `PHASE_V` | Half-bridge V | J_MOTOR.2 | 电机 V |
| `PHASE_W` | Half-bridge W | J_MOTOR.3 | 电机 W |

## 6. Hall 反馈
| Net | From | To | Notes |
|---|---|---|---|
| `+3V3_HALL` | +3V3 | J_HALL.1 | Hall 供电 |
| `GND` | GND | J_HALL.2 | Hall 地 |
| `HALL_A` | J_HALL.3 | U3.GPIO_HALL_A | Hall A |
| `HALL_B` | J_HALL.4 | U3.GPIO_HALL_B | Hall B |
| `HALL_C` | J_HALL.5 | U3.GPIO_HALL_C | Hall C |

## 7. 采样
| Net | From | To | Notes |
|---|---|---|---|
| `ISENSE_A` | RSHUNT_A Kelvin | U4 / U3.ADC_INx | 电流采样 A |
| `ISENSE_B` | RSHUNT_B Kelvin | U4 / U3.ADC_INy | 电流采样 B |
| `VBUS_SENSE` | Divider midpoint | U3.ADC_INz | 母线电压 |
| `TEMP_SENSE` | NTC divider | U3.ADC_INt | 可选温度采样 |

## 8. CAN
| Net | From | To | Notes |
|---|---|---|---|
| `CAN_TX` | U3.CAN_TX | U5.TXD | MCU -> transceiver |
| `CAN_RX` | U5.RXD | U3.CAN_RX | transceiver -> MCU |
| `CAN_H` | U5.CANH | J_CAN.1 | CAN 总线 |
| `CAN_L` | U5.CANL | J_CAN.2 | CAN 总线 |
| `CAN_GND` | GND | J_CAN.3 | 参考地 |

## 9. 调试
| Net | From | To | Notes |
|---|---|---|---|
| `SWDIO` | U3.SWDIO | J_SWD.2 | 调试 |
| `SWCLK` | U3.SWCLK | J_SWD.3 | 调试 |
| `NRST` | U3.NRST | J_SWD.4 | 复位 |
| `+3V3` | U2.OUT | J_SWD.1 | 调试参考电压 |
| `GND` | GND | J_SWD.5 | 调试地 |
