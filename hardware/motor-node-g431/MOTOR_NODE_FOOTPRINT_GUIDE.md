# Motor Node 板器件封装建议 v1

## 电源与保护
| Ref | Suggested Package | Notes |
|---|---|---|
| Input Fuse | 1812 PTC / 插件保险 | 视功率而定 |
| TVS | SMB / SMC | 24V 母线防护 |
| Bulk Caps | 1210 + 电解/固态插件 | 靠近输入和功率桥 |
| 3.3V LDO/Buck | SOT-223 / QFN / SOIC | 依据热设计 |

## MCU 与驱动
| Ref | Suggested Package | Notes |
|---|---|---|
| STM32G431 | LQFP-48 优先 | P0 焊接/返修更友好 |
| DRV8353 / DRV8302 | HTSSOP / VQFN / datasheet 推荐 | 跟随驱动器方案 |
| Crystal | 3225 / 5032 | 若外部晶振 |
| Decoupling Caps | 0402 / 0603 | 近 MCU/Driver |

## 功率级
| Ref | Suggested Package | Notes |
|---|---|---|
| MOSFET | PowerPAK SO-8 / PDFN / TO-252 | 依据电流和散热 |
| Shunt | 2512 / 1206 四端 | Kelvin 采样优先 |
| Gate Resistor | 0603 | 靠近栅极 |
| Bootstrap Caps | 0603 / 0805 | 靠近 driver |

## 接口
| Ref | Suggested Package | Notes |
|---|---|---|
| Power Input | 5.08mm 端子台 | 24V 输入 |
| Motor Output | 大电流端子 / 螺丝端子 | 三相输出 |
| Hall | JST-XH 5Pin | P0 常用 |
| CAN | JST-GH / 3.81mm 端子 | 差分通信 |
| SWD | 1.27mm Tag-Connect / 排针 | 调试 |
