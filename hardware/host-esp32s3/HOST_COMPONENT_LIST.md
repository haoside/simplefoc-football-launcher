# Host 板最小器件级原理图清单 v1

## 电源
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `F1` | 输入保护 | 24V Fuse / Resettable Fuse | 输入保护 |
| `TVS1` | 输入保护 | SMBJ33A / 同级 | 24V TVS |
| `U1` | Buck | MP1584 / LM2596 / 同级 | 24V -> 5V |
| `U2` | LDO | AMS1117-3.3 / MPM3833 / 同级 | 5V -> 3.3V |
| `CIN1/CIN2` | 输入滤波 | 47uF + 0.1uF | 近电源入口 |
| `COUT1/COUT2` | 输出滤波 | 22uF + 0.1uF | 稳压输出 |

## 主控
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `U3` | MCU | ESP32-S3-WROOM-1 | Host 控制核心 |
| `R_EN` | 启动 | 10k | EN 上拉 |
| `R_BOOT` | 启动 | 10k | BOOT 配置 |
| `C_EN` | 复位 | 0.1uF | EN RC |

## 通信
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `U4` | CAN | SN65HVD230 / TJA1051 / 同级 | CAN transceiver |
| `R_TERM` | CAN | 120R | 跳帽可选终端 |
| `D_CAN` | ESD | PESD / 同级 | CAN 口防护 |

## 传感器输入
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `R_TUBE_PU` | Tube Sensor | 10k | 上拉/下拉 |
| `R_CHAMBER_PU` | Chamber Sensor | 10k | 上拉/下拉 |
| `R_EXIT_PU` | Exit Sensor | 10k | 上拉/下拉 |
| `C_TUBE/C_CHAMBER/C_EXIT` | RC Filter | 100nF | 去抖 / 抗干扰 |

## 执行器输出
### 舵机方案
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `J_FEED_SERVO` | Servo | JST-VH / XH | 5V servo 接口 |

### 电磁闸门方案
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `Q1` | Solenoid Driver | AO3400 / 同级 N-MOS | 低边驱动 |
| `D1` | Flyback | SS14 / FR107 / 同级 | 续流 |
| `R_G1` | Gate | 100R | 栅极限流 |
| `R_PD1` | Gate | 10k | 栅极下拉 |

## 指示与调试
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `D2` | Status LED | 0603 LED | 运行状态 |
| `D3` | Fault LED | 0603 LED | 故障状态 |
| `BZ1` | Buzzer | 5V Active | 可选 |
| `J_DEBUG` | Debug | 6Pin Header | UART 下载/日志 |
