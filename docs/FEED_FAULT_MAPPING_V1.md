# 供球故障映射 v1

## 目标
把供球状态机里的 no-ball / chamber timeout / exit timeout，不再只停留在 feed 层，而是纳入 Host 统一故障链。

## 当前映射
| Feed Fault Reason | 场景 | Host Fault Code |
|---|---|---|
| `FEED_FAULT_NO_BALL` | 请求发球时管道无球 | `FAULT_NO_BALL_AT_CHAMBER` |
| `FEED_FAULT_CHAMBER_TIMEOUT` | 供球后长期未到发射位 | `FAULT_BALL_JAM` |
| `FEED_FAULT_EXIT_TIMEOUT` | 发射后长期未检测到出球 | `FAULT_BALL_JAM` |
| `FEED_FAULT_JAM` | 保留汇总态 | `FAULT_BALL_JAM` |

## 当前实现
- `feed_state.cpp`
  - `feed_raise_fault()`
  - `feed_request_one_ball()`
  - `feed_state_step()`
- `host_fault.cpp`
  - 同步写入 `HostState.telemetry.hostFaultCode`
- `host_state.h`
  - 新增 `HostTelemetry`

## 当前收益
- 供球异常进入统一 host fault
- 后续 CAN 遥测 / UI 展示可直接读 `HostTelemetry`
- jam fault 不再是散落逻辑
