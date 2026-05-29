# 原理图分页页间接口表 v1

## Host 板页间接口
| Page | Export Nets |
|---|---|
| H1 Power | `VIN_24V`, `+5V`, `+3V3`, `PGND`, `GND` |
| H2 ESP32 Core | `CAN_TX`, `CAN_RX`, `SIG_TUBE`, `SIG_CHAMBER`, `SIG_EXIT`, `SIG_ESTOP`, `PWM_FEED`, `FEED_DIR`, `LED_STATUS`, `BUZZER_CTL`, `UART0_TX`, `UART0_RX` |
| H3 CAN/Debug | `CAN_H`, `CAN_L` |
| H4 Sensors | 输入页，主要消费传感器信号 |
| H5 Feed/Indicators | 执行器与指示器页 |

## Motor Node 板页间接口
| Page | Export Nets |
|---|---|
| M1 Power | `VIN_24V`, `VDRV`, `+3V3`, `PGND`, `AGND`, `GND` |
| M2 MCU Core | `PWM_U`, `PWM_V`, `PWM_W`, `DRV_EN`, `DRV_FAULT_N`, `HALL_A`, `HALL_B`, `HALL_C`, `ISENSE_A`, `ISENSE_B`, `VBUS_SENSE`, `TEMP_SENSE`, `CAN_TX`, `CAN_RX`, `SWDIO`, `SWCLK`, `NRST` |
| M3 Gate Driver | `GH_U/GL_U`, `GH_V/GL_V`, `GH_W/GL_W`, `SH_U`, `SH_V`, `SH_W` |
| M4 Power Stage | `PHASE_U`, `PHASE_V`, `PHASE_W`, `ISENSE_A`, `ISENSE_B` |
| M5 Sense | Hall / VBUS / TEMP 感知页 |
| M6 CAN | `CAN_H`, `CAN_L` |

## 命名规则
- 页间全局网统一用大写下划线风格
- 功率网与逻辑网不要混名
- `PGND / AGND / GND` 明确分开，单点策略在 PCB 实现
