# PCB 设计规则 v1

## 1. 分板建议
- **Host 板** 与 **Motor Node 板** 分开
- 不做三路一体功率板，P0 先以可调试、可替换为优先

## 2. Host 板
- 建议 4 层：`Signal / GND / 3V3_5V / Signal`
- 传感器与 CAN 靠近连接器放置
- DCDC 与 ESP32 天线区隔离
- 天线下方与前方保持净空

## 3. Motor Node 板
- 建议 4 层起步：`Signal / GND / Power / Signal`
- 功率回路最短：MOSFET、Driver、Shunt 紧凑布置
- Hall、CAN、SWD 远离三相开关节点
- 模拟采样地与功率地单点汇接
- 母线电容紧贴功率级

## 4. 关键布局约束
- Driver 到 MOSFET Gate 走线短且对称
- Shunt 到 ADC/放大器 Kelvin 引出
- VBUS 分压靠近 MCU ADC 输入并加 RC 滤波
- FAULT/ENABLE 线远离相线
- CANH/CANL 差分并行走线

## 5. 安全
- 24V 输入、功率级、逻辑区明确分区
- 预留测试点：3V3、5V、24V、VBUS_SENSE、ISENSE、FAULT、CAN
- 急停不要只依赖 MCU，PCB 需支持外部硬切
