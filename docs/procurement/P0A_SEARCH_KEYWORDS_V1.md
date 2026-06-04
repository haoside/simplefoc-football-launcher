# P0-A 采购搜索关键词 v1

## 原则

- 先买能跑 P0-A 台架 bring-up 的物料。
- 不买多球仓 / 供球管道 / 闸门。
- 高电流驱动和电池包先做预研，不立即下单。

## 搜索关键词

### 控制与通信

| 物料 | 中文关键词 | 英文关键词 | 备注 |
|---|---|---|---|
| ESP32-S3 DevKit | `ESP32-S3 开发板 USB` | `ESP32-S3 DevKit USB` | Host 控制板 |
| B-G431B-ESC1 | `B-G431B-ESC1` | `B-G431B-ESC1 motor control` | P0-A 低功率 SimpleFOC 台架 |
| CAN 模块 | `SN65HVD230 CAN 模块 3.3V` | `SN65HVD230 CAN transceiver module` | ESP32-S3 / G431 通信 |
| 调试器 | `ST-Link V2 STM32 下载器` | `ST-Link V2 STM32 programmer` | G431 调试 |
| USB-UART | `USB TTL 串口模块 3.3V` | `USB UART 3.3V adapter` | Host / Node 日志 |

### 电机与轮组

| 物料 | 中文关键词 | 英文关键词 | 备注 |
|---|---|---|---|
| 6374 Hall BLDC | `6374 无刷电机 带霍尔 170KV 8mm轴` | `6374 BLDC Hall sensor 170KV 8mm shaft` | 3 个，优先同批次 |
| 110mm 摩擦轮 | `110mm 聚氨酯包胶轮 高摩擦 8mm孔` | `110mm polyurethane rubber wheel high friction` | P0-A 默认 |
| 130mm 摩擦轮 | `130mm 聚氨酯包胶轮 高摩擦 8mm孔` | `130mm polyurethane rubber wheel high friction` | P0-B 候选 |
| 联轴器 | `8mm 联轴器 刚性/弹性` | `8mm shaft coupler flexible rigid` | 按电机轴和轮轴确认 |
| 轴承座 | `8mm 轴承座 法兰轴承座` | `8mm bearing block flange bearing` | 轮轴支撑 |

### 电源与保护

| 物料 | 中文关键词 | 英文关键词 | 备注 |
|---|---|---|---|
| 24V 限流电源 | `24V 可调限流 开关电源 20A 40A` | `24V current limiting power supply 20A 40A` | P0-A 台架优先 |
| 急停按钮 | `自锁蘑菇头急停按钮 常闭` | `latching mushroom emergency stop NC` | 硬切链路 |
| DC 保险 | `直流保险座 保险片 40A 150A` | `DC fuse holder 40A 150A` | 总线/分路 |
| 接触器 | `24V DC 接触器 150A` | `24V DC contactor 150A` | P0-B 预研 |
| XT90 | `XT90 防打火 插头` | `XT90 anti spark connector` | 中等电流连接 |
| 动力线 | `10AWG 硅胶线 12AWG 硅胶线` | `10AWG silicone wire 12AWG silicone wire` | 支路动力线 |

### 安全与结构

| 物料 | 中文关键词 | 英文关键词 | 备注 |
|---|---|---|---|
| PC 板 | `6mm 透明 PC 板 聚碳酸酯板` | `6mm polycarbonate sheet clear` | 防护罩 |
| 铝型材 | `2020 3030 铝型材` | `2020 3030 aluminum extrusion` | 台架/支架 |
| 标准足球 | `5号足球 标准 比赛训练` | `size 5 football soccer ball training` | 3–5 个 |

## 下单检查

1. 电机必须带 Hall。
2. 电机轴径、轮孔、联轴器必须匹配。
3. 摩擦轮至少买 3 个工作件 + 备件。
4. 急停必须有常闭触点。
5. PC 防护罩材料必须先于实球高速测试到位。
