# Hardware Design Package v1

当前仓库已补硬件设计基线，用于进入原理图与 PCB 设计阶段。

## 文件
- `host-esp32s3/HOST_SCHEMATIC.md`
- `motor-node-g431/MOTOR_NODE_SCHEMATIC.md`
- `host-esp32s3/HOST_COMPONENT_LIST.md`
- `motor-node-g431/MOTOR_NODE_COMPONENT_LIST.md`
- `motor-node-g431/MOTOR_NODE_SUBCIRCUITS.md`
- `PCB_RULES.md`
- `HOST_PCB_LAYOUT.svg`
- `MOTOR_NODE_PCB_LAYOUT.svg`
- `pinout/HOST_PINOUT.md`
- `pinout/MOTOR_NODE_PINOUT.md`
- `pinout/CONNECTOR_TABLE.md`
- `pinout/HOST_NETS.csv`
- `pinout/MOTOR_NODE_NETS.csv`
- `host-esp32s3/HOST_NET_BY_NET.md`
- `motor-node-g431/MOTOR_NODE_NET_BY_NET.md`
- `PCB_LAYOUT_CONSTRAINTS.md`
- `host-esp32s3/HOST_SCHEMATIC_PAGES.md`
- `motor-node-g431/MOTOR_NODE_SCHEMATIC_PAGES.md`
- `SCHEMATIC_PAGE_INTERFACES.md`
- `host-esp32s3/HOST_FOOTPRINT_GUIDE.md`
- `motor-node-g431/MOTOR_NODE_FOOTPRINT_GUIDE.md`
- `FIRST_SPIN_BRINGUP.md`

## 当前设计策略
- Host 与 Motor Node 分板
- Motor Node 一板一电机
- CAN 作为 Host ↔ Node 总线
- 24V P0 联调，预留 36V 升级
- 急停硬件切驱动使能/主回路

## 下一步
1. 按上述网表与接口在 KiCad 建原理图
2. 先完成 Host 板与单个 Motor Node 板
3. 用单电机闭环先验证功率级与 Hall 反馈
