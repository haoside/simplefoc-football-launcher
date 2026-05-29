# Host 三节点控制链 v1

## 目标
把 `HostCommand -> 120° RPM Mixer -> per-node target -> CAN SET_RPM -> 节点执行` 串起来。

## 当前链路
1. `HostState.cmd` 保存 `baseRpm / ux / uy / fireRequest / estop`
2. `launch_state_machine_step()` 推进发射状态
3. `host_update_targets_from_command()` 调用 `mix120deg()`
4. 生成 `Wheel A/B/C` 目标 RPM
5. `host_can_control_tick()` 向三节点发送 `SET_RPM`
6. 节点回传 `STATUS`

## 当前文件
- `src/host_state.h`
- `src/host_state.cpp`
- `src/rpm_mixer_120.h`
- `src/rpm_mixer_120.cpp`
- `src/launch_state_machine.cpp`
- `src/feed_controller.cpp`
- `src/can_host_loop.cpp`
- `src/app_main.cpp`

## 当前边界
- 传感器还是本地 stub
- feed actuator 还是占位实现
- 还没接真实 TWAI/CAN HAL
- 但三节点目标分发主干已形成
