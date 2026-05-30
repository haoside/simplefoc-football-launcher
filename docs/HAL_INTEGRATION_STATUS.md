# HAL 接入状态 v1

## 已接上的位置
### Host
- `app_main.cpp`
  - `host_hal_init()`
  - `host_hal_can_init()`
  - `host_hal_estop_active()`
  - `host_hal_sensor_chamber_ready()`
  - `host_hal_sensor_exit_detected()`
- `feed_controller.cpp`
  - `host_hal_feed_request()`
  - `host_hal_sensor_tube_ball_present()`
- `can_host_loop.cpp`
  - `host_hal_can_send()`
  - `host_hal_can_recv()`

### Node
- `app.cpp`
  - `node_hal_init()`
  - `node_hal_can_init()`
- `node_comm.cpp`
  - `node_hal_can_send()`
  - `node_hal_can_recv()`
- `driver_protection.cpp`
  - `node_hal_driver_fault_active()`

## 当前仍是 stub 的位置
- Host TWAI 真正收发
- Host 真实 GPIO / Feed actuator
- Node FDCAN 真正收发
- Node ADC / PWM / Hall 真正读取

## 下一步
1. 用 ESP-IDF TWAI 替换 `host_hal_stub.cpp`
2. 用 STM32 HAL/FDCAN 替换 `node_hal_stub.cpp`
3. 把 SimpleFOC adapter 读取改成调用 `node_hal_*`
