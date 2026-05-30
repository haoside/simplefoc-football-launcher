# 多球供球状态机 v1

## 目标
把多球管道、发射位、出球检测串成完整供球状态机，而不是只做一个 `feed_request_one_ball()` 占位函数。

## 状态
- `FEED_IDLE`
- `FEED_WAIT_TUBE_BALL`
- `FEED_ACTUATING`
- `FEED_WAIT_CHAMBER`
- `FEED_READY`
- `FEED_SHOT_EXIT`
- `FEED_RELOAD_DELAY`
- `FEED_JAM`

## 当前逻辑
1. 管道有球 -> `FEED_READY`
2. 收到发球请求 -> `host_hal_feed_request()` -> `FEED_WAIT_CHAMBER`
3. 发射位到球 -> `FEED_SHOT_EXIT`
4. 检测到出球 -> `FEED_RELOAD_DELAY`
5. 延时后回 `FEED_WAIT_TUBE_BALL`
6. 若超时未到球 / 未出球 -> `FEED_JAM`

## 当前接入位置
- `feed_state.cpp`
- `launch_state_machine.cpp`
- `app_main.cpp`
- `config.h`

## 超时参数
- `FEED_TO_CHAMBER_TIMEOUT_MS`
- `FIRE_TO_EXIT_TIMEOUT_MS`
- `RELOAD_DELAY_MS`

## 当前收益
- 多球管道逻辑不再是空壳
- jam fault 有明确触发路径
- Host 发射状态机和供球状态机开始耦合
