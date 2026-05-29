# Motor Node 板最小器件级原理图清单 v1

## 电源输入与保护
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `F1` | Input Fuse | 5A~10A Fuse / PTC | 节点保护 |
| `TVS1` | Surge | SMBJ33A / 同级 | 24V TVS |
| `CIN1/CIN2` | Bulk Input | 100uF + 1uF | 靠近输入 |
| `U1` | Regulator | Buck 24V -> 12V/10V | Driver 供电 |
| `U2` | Regulator | 3.3V LDO/Buck | MCU/Hall 供电 |

## MCU
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `U3` | MCU | STM32G431CBT6 / G431KBT6 | 电机控制核心 |
| `Y1` | Clock | 8MHz/16MHz Crystal | 可选 |
| `Cdec_*` | Decoupling | 100nF x n | 每电源脚就近 |
| `J_SWD` | Debug | 5Pin Header | SWD |

## Gate Driver
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `U4` | Driver | DRV8353 / DRV8302 | 三相驱动 |
| `C_BOOT_*` | Bootstrap | datasheet 推荐值 | 每相 bootstrap |
| `R_GATE_*` | Gate Resistor | 5R~22R | 依据 MOSFET 调整 |
| `R_EN` | Enable Pull | 10k | 使能默认态 |

## 功率级
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `QH_U/QH_V/QH_W` | High-side MOSFET | 40V~60V N-MOS | 三相上桥 |
| `QL_U/QL_V/QL_W` | Low-side MOSFET | 40V~60V N-MOS | 三相下桥 |
| `RSHUNT_A/RSHUNT_B` | Shunt | 5mΩ~20mΩ | 电流采样 |
| `C_BUS1/C_BUS2` | DC Link | 100uF + 1uF | 贴近功率桥 |

## 采样与反馈
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `R_VBUS_TOP/BOT` | VBUS Divider | 依 ADC 量程选值 | 分压 |
| `C_VBUS_F` | VBUS Filter | 1nF~100nF | RC 滤波 |
| `R_HALL_PU*` | Hall Pull-up | 4.7k~10k | 视传感器而定 |
| `NTC1` | Temp | 10k NTC | 可选 |

## 通信
| Ref | Block | Suggested Part | Notes |
|---|---|---|---|
| `U5` | CAN | SN65HVD230 / TJA1051 / 同级 | CAN transceiver |
| `R_TERM` | CAN | 120R | 仅总线末端装 |
| `D_CAN` | ESD | PESD / 同级 | CAN 口防护 |

## 接口
| Ref | Purpose |
|---|---|
| `J_PWR` | 24V 输入 |
| `J_MOTOR` | 电机三相输出 |
| `J_HALL` | Hall 反馈 |
| `J_CAN` | CAN 总线 |
| `J_SWD` | SWD 调试 |
