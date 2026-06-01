# 单球三轮 Host 代码骨架 v1

## 本次代码调整
已把 Host 主线从多球/供球字段改回单球手动上球模型：
- `ballLoaded`
- `wheel1 / wheel2 / wheel3`
- `spinMode`
- `baseRpm / deltaRpm`
- `IDLE -> SPINUP -> READY -> FIRE -> COOLDOWN -> FAULT / ESTOP`

## 关键文件
- `firmware/host-esp32s3/src/hal/host_hal.h`
- `firmware/host-esp32s3/src/hal/host_hal_stub.cpp`
- `firmware/host-esp32s3/src/host_state.h`
- `firmware/host-esp32s3/src/host_state.cpp`
- `firmware/host-esp32s3/src/launch_state_machine.cpp`
- `firmware/host-esp32s3/src/can_host_loop.cpp`
- `firmware/host-esp32s3/src/telemetry.cpp`
- `firmware/host-esp32s3/src/app_main.cpp`

## 当前边界
- 仍是平台无关骨架/stub
- 但已去掉多球供球主线依赖
- 下一步可继续把 B-G431B-ESC1 节点侧 pin/hardware 适配收口
