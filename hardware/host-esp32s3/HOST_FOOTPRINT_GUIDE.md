# Host 板器件封装建议 v1

## 电源
| Ref | Suggested Package | Notes |
|---|---|---|
| Fuse / PTC | 1812 / 插件保险座 | 视电流而定 |
| TVS | SMB / SMC | 24V 输入浪涌 |
| Buck IC | SOIC / QFN / 模块封装 | P0 可先模块化 |
| LDO | SOT-223 / SOT-23-5 | 依据功耗选 |
| Bulk Caps | 1206 + 电解/固态插件 | 电源入口 |

## 主控与通信
| Ref | Suggested Package | Notes |
|---|---|---|
| ESP32-S3-WROOM | 模组封装 | 先用模组降低风险 |
| CAN Transceiver | SOIC-8 / SOT-23-8 | 常用封装 |
| ESD | SOT-23 / DFN | 接口旁布置 |
| Terminal / CAN Conn | 3.81mm 端子 / JST-GH | 看线束方案 |

## 传感器/执行器
| Ref | Suggested Package | Notes |
|---|---|---|
| RC Filter R/C | 0603 | 足够 |
| Status LED | 0603 | 统一贴片 |
| Buzzer Driver | SOT-23 | 若加驱动 |
| MOSFET for Solenoid | SOT-23 / PowerPAK | 视电流 |
| Flyback Diode | SMA / SMB | 电磁闸门 |

## 调试与连接器
| Ref | Suggested Package | Notes |
|---|---|---|
| Debug Header | 2.54mm 排针 / Tag-Connect | P0 用排针即可 |
| Sensor Connectors | JST-XH 2.54 | 便于手工接线 |
