# Host 板引脚网表 / Pinout v1

> 目标：直接给 KiCad 原理图录入使用。

## U3 - ESP32-S3 逻辑分配

| Signal | Direction | Function | Notes |
|---|---|---|---|
| `GPIO_CAN_TX` | OUT | CAN TX 到收发器 | Host -> CAN transceiver |
| `GPIO_CAN_RX` | IN | CAN RX 来自收发器 | CAN transceiver -> Host |
| `GPIO_TUBE_SENSOR` | IN | 管道有球检测 | 建议加 RC 滤波 |
| `GPIO_CHAMBER_SENSOR` | IN | 发射位到球检测 | 发射前关键联锁 |
| `GPIO_EXIT_SENSOR` | IN | 出球检测 | 用于 shot result |
| `GPIO_ESTOP_IN` | IN | 急停状态反馈 | 硬件切断后的状态读取 |
| `GPIO_FEED_PWM` | OUT | 供球舵机 PWM / 门控控制 | 若用舵机方案 |
| `GPIO_FEED_DIR` | OUT | 供球电机方向/使能 | 若用电机/闸门方案 |
| `GPIO_GATE_HOME` | IN | 分离机构原点 | 可选 |
| `GPIO_GATE_READY` | IN | 分离机构到位 | 可选 |
| `GPIO_LED_STATUS` | OUT | 状态灯 | 可选 |
| `GPIO_BUZZER` | OUT | 蜂鸣器 | 可选 |
| `UART0_TX` | OUT | 调试串口 | 下载/日志 |
| `UART0_RX` | IN | 调试串口 | 下载/日志 |
| `EN` | IN | 芯片使能 | 上拉 |
| `BOOT` | IN | 启动模式 | 下载模式 |

## 连接器定义

### J_PWR - 电源输入
| Pin | Net | Notes |
|---|---|---|
| 1 | `VIN_24V` | 24V 输入 |
| 2 | `PGND` | 动力地 |

### J_CAN - CAN 总线
| Pin | Net | Notes |
|---|---|---|
| 1 | `CAN_H` | |
| 2 | `CAN_L` | |
| 3 | `GND` | |
| 4 | `+5V_AUX` | 可选对外辅助供电 |

### J_TUBE_SENSOR
| Pin | Net |
|---|---|
| 1 | `+5V_SENSOR` |
| 2 | `GND` |
| 3 | `SIG_TUBE` |

### J_CHAMBER_SENSOR
| Pin | Net |
|---|---|
| 1 | `+5V_SENSOR` |
| 2 | `GND` |
| 3 | `SIG_CHAMBER` |

### J_EXIT_SENSOR
| Pin | Net |
|---|---|
| 1 | `+5V_SENSOR` |
| 2 | `GND` |
| 3 | `SIG_EXIT` |

### J_FEED
#### 舵机方案
| Pin | Net |
|---|---|
| 1 | `+5V_SERVO` |
| 2 | `GND` |
| 3 | `PWM_FEED` |

#### 电磁闸门方案
| Pin | Net |
|---|---|
| 1 | `VIN_24V` |
| 2 | `SOLENOID_LOW` |

### J_ESTOP_FB
| Pin | Net |
|---|---|
| 1 | `SIG_ESTOP` |
| 2 | `GND` |

### J_DEBUG
| Pin | Net |
|---|---|
| 1 | `3V3` |
| 2 | `GND` |
| 3 | `UART0_TX` |
| 4 | `UART0_RX` |
| 5 | `EN` |
| 6 | `BOOT` |

## 电源网
- `VIN_24V`
- `+5V`
- `+3V3`
- `+5V_SENSOR`
- `+5V_SERVO`
- `PGND`
- `GND`
