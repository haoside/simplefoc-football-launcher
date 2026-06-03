# SimpleFOC Football Launcher

基于 SimpleFOC 的三无刷电机足球发射控制系统。

P0 目标：完成三路电机速度闭环、三轮同步预转、单次稳定射出标准 5 号足球，并具备基础安全保护与多球管道供球能力。

## Project Goal

构建一套用于足球训练的三轮摩擦发射原型，通过三路 BLDC 独立调速与转速差控制，验证足球的速度、方向与旋转控制能力。

## P0 Scope

- 单电机 SimpleFOC 闭环稳定
- 三电机独立速度闭环
- 三轮同步预转
- 入球检测
- 单次稳定射出标准 5 号足球
- 多球管道供球与单球分离
- 急停 / 过流 / 堵转 / 过热保护
- 面向专业足球运动员边路 `15~20m` 长传训练需求

## Out of Scope

- 自动瞄准
- 视觉识别
- 连续供球
- 高速发射
- 远程无人值守
- HA / Matter 接入

## Default Technical Direction

- 布局：`120° 均布三轮`
- 控制架构：`1 个上位控制板 + 3 个独立电机控制节点`
- 上位控制板：`ESP32-S3`
- 电机控制节点：`B-G431B-ESC1 ×3`
- Control Framework：`SimpleFOC`
- Motor：优先带 Hall 的 `6374 BLDC`，`170~190KV`
- Node 方案：每个轮子 1 块 `B-G431B-ESC1`，替代“STM32G431 开发板 + 单独三相驱动板”
- Feedback：P0 优先 Hall，增强方案可切 `AS5048A`
- Power：动力侧先按 `24V`、`40A+` 台架电源预估
- Control Target：P0 先做 `速度控制`

## P0 Milestones

1. 单电机闭环跑通
2. 三电机独立闭环跑通
3. 入球检测 + 发射状态机跑通
4. 单次低速稳定射球
5. 故障保护停机

## Suggested Repository Layout

```text
/docs
  P0_TECH_PLAN.md
  BOM_DRAFT.md
  INTERFACES.md
  CONNECTION_SCHEME.md
  CONNECTION_DIAGRAM.md
  FIRMWARE_MODULES.md
/firmware
  common/
  host-esp32s3/
  motor-node-g431/
/hardware
  README.md
  host-esp32s3/
  motor-node-g431/
  PCB_RULES.md
  HOST_PCB_LAYOUT.svg
  MOTOR_NODE_PCB_LAYOUT.svg
```

## Safety

> 该项目涉及高速旋转部件和射出机构，P0 仅允许低速测试。

- 必须先做低速测试
- 发射方向禁止站人
- 必须有物理急停按钮
- 必须安装摩擦轮防护罩
- 默认上电即安全空闲态
- 无人看护时禁止运行

## Status

当前阶段：`P0 方案冻结 / 硬件与固件拆分中`

## Bring-up

- `docs/FIRMWARE_BRINGUP_PLAN.md`
- `docs/FIRMWARE_BRINGUP_CHECKLIST.md`

- `docs/CAN_PROTOCOL_V1.md`
- `docs/FIRMWARE_COMM_LOOP.md`
- `docs/NODE_CONTROL_CHAIN.md`
- `docs/HOST_CONTROL_CHAIN.md`
- `docs/FAULT_SAFETY_CHAIN.md`
- `docs/HAL_ADAPTER_PLAN.md`
- `docs/HAL_INTEGRATION_STATUS.md`
- `docs/NODE_HAL_DATA_FLOW.md`
- `docs/PLATFORM_TEMPLATE_PLAN.md`
- `docs/FEED_STATE_MACHINE_V1.md`
- `docs/FEED_FAULT_MAPPING_V1.md`
- `docs/HOST_TELEMETRY_V1.md`
- `docs/ARCH_DECISION_BG431B_ESC1.md`
- `docs/CODEGEN_SINGLE_BALL_HOST_V1.md`
- `docs/CODEGEN_BG431B_NODE_V1.md`
- `docs/BG431B_NODE_INSTANTIATION_V1.md`
- `docs/HOST_3NODE_INTEGRATION_DEMO_V1.md`
- `docs/DEBUG_GUIDE_V1.md`
- `docs/NODE_DEBUG_OUTPUT_V1.md`
- `docs/HOST_DEBUG_COMMANDS_V1.md`
- `docs/CURVE_BALL_CONTROL_V1.md`
- `docs/HOST_DEBUG_WHEEL_JOG_V1.md`
- `docs/PRACTICAL_CURVE_PASS_PRESETS_V1.md`
- `docs/SHORT_GUIDE_TUBE_V1.md`
- `docs/HOST_PRESET_COMMANDS_V1.md`
- `docs/SHORT_GUIDE_TUBE_TEST_MATRIX_V1.md`
- `docs/P0_AB_TEST_LOG_TEMPLATE_V1.md`
- `docs/ENVIRONMENT_SIM_PARAMS_V1.md`
- `docs/ENVIRONMENT_SIM_TEST_MATRIX_V1.md`
- `docs/P0_FIELD_TEST_LOG_TEMPLATE_V2.md`
- `docs/sim/ENVIRONMENT_TUNING_RECOMMENDATIONS_V1.md`
- `docs/HOST_WIND_PRESETS_V1.md`
- `docs/HOST_ENV_PROFILES_V1.md`
- `docs/HOST_ENV_COMMANDS_V1.md`
- `docs/HOST_ENV_PRESET_COMMAND_MATRIX_V1.md`
- `docs/OPERATOR_QUICK_CARD_V1.md`
- `cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad`
- `docs/mechanical/SHORT_GUIDE_TUBE_DRAWING_V1.md`
- `cad/sheet-metal/motor-mount-plate-v1/motor_mount_plate_v1.scad`
- `docs/mechanical/MOTOR_MOUNT_PLATE_DRAWING_V1.md`
