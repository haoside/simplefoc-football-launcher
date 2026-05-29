# 最小通信主循环说明 v1

## Host
- 文件：`firmware/host-esp32s3/src/can_host_loop.cpp`
- 功能：
  - 维护 A/B/C 三节点状态
  - 周期发送 `SET_RPM`
  - 接收 `STATUS`

## Motor Node
- 文件：
  - `firmware/motor-node-g431/App/node_state.h`
  - `firmware/motor-node-g431/App/node_state.cpp`
  - `firmware/motor-node-g431/App/node_comm.cpp`
- 功能：
  - 保存节点运行状态
  - 接收 `SET_RPM`
  - 响应 `ESTOP_BROADCAST`
  - 周期发送 `STATUS` 和 `HEARTBEAT`

## Common
- 文件：
  - `firmware/common/protocol_codec.h`
  - `firmware/common/protocol_codec.cpp`
- 功能：
  - 提供最小编解码辅助

## 当前边界
- 现在是最小可编译/可联调骨架
- 还未接具体 HAL / TWAI / FDCAN 驱动
- 还未接 SimpleFOC 实际对象
