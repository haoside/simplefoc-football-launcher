# PCB 布局关键约束 v1

## Host 板
### 1. 电源
- 24V 输入、保险、TVS、DCDC 放在板边同一区域
- Buck 高 di/dt 回路尽量小
- 5V 与 3.3V 分区明显

### 2. MCU / 通信
- ESP32-S3 天线朝外，周围净空
- CAN 收发器靠近 CAN 接口
- 调试口靠板边

### 3. 传感器 / 执行器
- 传感器口成排放置，便于线束
- 舵机/闸门驱动靠近接口，避免大电流绕行 MCU
- 急停反馈与状态灯放近边缘便于维护

## Motor Node 板
### 1. 功率区优先
- `VIN_24V -> DC Link -> Half Bridge -> Motor Connector` 路径最短
- Gate Driver 紧贴 MOSFET
- Bootstrap 电容紧贴 Driver 脚位

### 2. 采样优先
- Shunt Kelvin 采样单独引出
- `VBUS_SENSE` 远离开关节点
- 模拟采样线不穿越相线区

### 3. 控制 / 通信
- STM32G431 放在 Driver 边缘但远离功率热区
- CAN 收发器靠近接口
- SWD 靠板边
- Hall 接口远离三相输出端子

### 4. 热与机械
- MOSFET 散热铜皮充分
- 功率区预留散热片/风道空间
- 电机三相接口用大焊盘、大电流端子
- 板安装孔避免穿过敏感回流路径
