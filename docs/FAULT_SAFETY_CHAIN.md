# 故障安全链 v1

## 目标
把节点故障、Host 故障态、全局停机广播连成闭环。

## 当前链路
1. Node 本地产生 `faultCode`
2. Node 在 `HEARTBEAT` / `FAULT` 报文中上报
3. Host 在 `host_can_on_rx()` 中处理 `HEARTBEAT/FAULT`
4. Host 调用 `host_fault_raise()` 置全局故障
5. `launch_state_machine_step()` 将状态切到 `FAULT`
6. `host_can_control_tick()` 发送 `ESTOP_BROADCAST`
7. 所有 Node 收到后 `enabled=0`，状态切 `ESTOP`
8. Host 同时对三节点下发 `SET_RPM=0, enable=0`

## 当前文件
- `firmware/host-esp32s3/src/host_fault.h`
- `firmware/host-esp32s3/src/host_fault.cpp`
- `firmware/host-esp32s3/src/can_host_loop.cpp`
- `firmware/host-esp32s3/src/launch_state_machine.cpp`
- `firmware/motor-node-g431/App/node_comm.cpp`

## 当前边界
- 还是日志/stub 级实现
- 还未接真实硬件急停输入与 HAL CAN
- 但故障状态流已经打通
