# Host 板 net-by-net 原理图连接表 v1

## 1. 电源入口
| Net | From | To | Notes |
|---|---|---|---|
| `VIN_24V` | J_PWR.1 | F1 -> TVS1 -> U1.IN -> J_FEED(solenoid) | 24V 主输入 |
| `PGND` | J_PWR.2 | TVS1.GND -> U1.GND -> Power return | 动力地 |

## 2. 5V / 3.3V 电源
| Net | From | To | Notes |
|---|---|---|---|
| `+5V` | U1.OUT | U2.IN, J_TUBE_SENSOR.1, J_CHAMBER_SENSOR.1, J_EXIT_SENSOR.1, J_FEED_SERVO.1 | 5V 主供电 |
| `+3V3` | U2.OUT | U3.VDD, U4.VCC, J_DEBUG.1 | 3.3V 逻辑供电 |
| `GND` | U2.GND | U3.GND, U4.GND, Sensors GND, J_DEBUG.GND | 逻辑地 |

## 3. ESP32-S3 基础
| Net | From | To | Notes |
|---|---|---|---|
| `EN` | R_EN -> U3.EN | J_DEBUG.5 | 上拉 + 调试 |
| `BOOT` | R_BOOT -> U3.GPIO0 | J_DEBUG.6 | 下载模式 |
| `UART0_TX` | U3.U0TXD | J_DEBUG.3 | 调试输出 |
| `UART0_RX` | U3.U0RXD | J_DEBUG.4 | 调试输入 |

## 4. CAN
| Net | From | To | Notes |
|---|---|---|---|
| `CAN_TX` | U3.GPIO_CAN_TX | U4.TXD | Host -> transceiver |
| `CAN_RX` | U4.RXD | U3.GPIO_CAN_RX | transceiver -> Host |
| `CAN_H` | U4.CANH | J_CAN.1 | CAN 总线 |
| `CAN_L` | U4.CANL | J_CAN.2 | CAN 总线 |
| `CAN_GND` | GND | J_CAN.3 | 参考地 |
| `R_TERM_EN` | R_TERM | CAN_H <-> CAN_L | 末端选装 |

## 5. 传感器输入
| Net | From | To | Notes |
|---|---|---|---|
| `SIG_TUBE` | J_TUBE_SENSOR.3 | RC -> U3.GPIO_TUBE_SENSOR | 管道有球 |
| `SIG_CHAMBER` | J_CHAMBER_SENSOR.3 | RC -> U3.GPIO_CHAMBER_SENSOR | 发射位到球 |
| `SIG_EXIT` | J_EXIT_SENSOR.3 | RC -> U3.GPIO_EXIT_SENSOR | 出球检测 |
| `SIG_ESTOP` | J_ESTOP_FB.1 | RC / divider -> U3.GPIO_ESTOP_IN | 急停反馈 |
| `GND` | J_SENSOR_GND | U3.GND | 共地 |

## 6. 供球执行器
### 舵机方案
| Net | From | To | Notes |
|---|---|---|---|
| `PWM_FEED` | U3.GPIO_FEED_PWM | J_FEED_SERVO.3 | PWM 控制 |
| `+5V_SERVO` | +5V | J_FEED_SERVO.1 | 舵机电源 |
| `GND` | GND | J_FEED_SERVO.2 | 舵机地 |

### 电磁闸门方案
| Net | From | To | Notes |
|---|---|---|---|
| `SOLENOID_LOW` | Q1.D | J_FEED_SOL.2 | 低边开关 |
| `VIN_24V` | J_PWR.1 | J_FEED_SOL.1 | 24V 供电 |
| `GATE_Q1` | U3.GPIO_FEED_DIR | R_G1 -> Q1.G | MOS 驱动 |

## 7. 状态指示
| Net | From | To | Notes |
|---|---|---|---|
| `LED_STATUS` | U3.GPIO_LED_STATUS | R_LED1 -> D2 | 状态灯 |
| `BUZZER_CTL` | U3.GPIO_BUZZER | Driver -> BZ1 | 蜂鸣器 |
