# Node 日志输出骨架 v1

## 文件
- `firmware/node-bg431b-esc1/include/node_debug.h`
- `firmware/node-bg431b-esc1/src/node_debug.cpp`

## 当前输出
### BOOT
输出：
- 板卡名
- wheel 名称
- nodeId
- 电机方向
- Hall 极性

### STATUS
输出：
- nodeId
- state
- enabled
- targetRpm
- actualRpm
- busVoltage
- phaseCurrent
- temp
- faultCode

### FAULT
输出：
- nodeId
- state
- faultCode
- actualRpm
- current
- temp

## 目的
- 方便单板 bring-up
- 方便核对 wheel1/2/3 实例映射
- 方便快速判断是通信问题、控制问题还是硬件 fault
