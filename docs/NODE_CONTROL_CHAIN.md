# 单电机节点控制链 v1

## 目标
把 `node_comm -> node_state -> velocity_loop -> simplefoc_adapter` 串起来，形成最小控制闭环骨架。

## 当前链路
1. Host 发 `SET_RPM`
2. `node_comm_on_rx()` 解包并更新 `node_state.targetRpm`
3. `velocity_loop_step()` 读取 `node_state`
4. `simplefoc_adapter_set_target_rpm()` 接收目标
5. adapter 返回 `actualRpm / busVoltage / current / temp`
6. `node_state` 更新后由 `node_comm_poll()` 回传 `STATUS/HEARTBEAT`

## 当前文件
- `App/node_state.h`
- `App/node_state.cpp`
- `App/node_comm.cpp`
- `App/velocity_loop.cpp`
- `App/simplefoc_init.cpp`
- `App/simplefoc_adapter.h`
- `App/simplefoc_adapter.cpp`
- `App/driver_protection.cpp`

## 当前边界
- adapter 还是占位实现
- 还没接真实 SimpleFOC 对象
- 还没接 STM32 HAL/FDCAN/ADC/TIM
- 但数据流和状态流已经连上

## 下一步
1. 用真实 SimpleFOC motor/driver/sensor 替换 adapter stub
2. 接 FDCAN HAL
3. 接 ADC/TIM/Hall 实际采样
