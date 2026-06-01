# B-G431B-ESC1 节点代码骨架 v1

## 目标
为每个 wheel node 提供可调试优先的代码骨架，适配 `B-G431B-ESC1 ×3` 架构。

## 已生成文件
- `firmware/node-bg431b-esc1/include/board_config.h`
- `firmware/node-bg431b-esc1/include/node_state.h`
- `firmware/node-bg431b-esc1/src/node_state.cpp`
- `firmware/node-bg431b-esc1/hal/node_hal_bg431b.h`
- `firmware/node-bg431b-esc1/hal/node_hal_bg431b_stub.cpp`
- `firmware/node-bg431b-esc1/src/node_safety.cpp`
- `firmware/node-bg431b-esc1/src/node_telemetry.cpp`
- `firmware/node-bg431b-esc1/src/node_control.cpp`
- `firmware/node-bg431b-esc1/src/node_comm.cpp`
- `firmware/node-bg431b-esc1/src/app_main.cpp`

## 当前特点
- 状态清晰：IDLE / SPINUP / RUNNING / FAULT / ESTOP
- 遥测完整：targetRpm / actualRpm / busVoltage / current / temp / faultCode
- 通信完整：SET_RPM / STATUS / HEARTBEAT / FAULT / ESTOP
- 可调试优先：stub/HAL 分离、参数集中、模块解耦

## 下一步
- 将 `NODE_DEFAULT_ID` 按 wheel1/wheel2/wheel3 实例化
- 将 HAL stub 替换成 B-G431B-ESC1 实际板级实现
- 将 node 与 host 统一接入同一 build / platform 工程
