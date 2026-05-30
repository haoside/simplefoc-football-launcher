# Host 遥测输出 v1

## 目标
先把 Host 侧关键状态统一输出，便于 bring-up / 联调 / 故障定位。

## 当前输出字段
- `state`
- `baseRpm`
- `tube`
- `chamber`
- `exit`
- `feedState`
- `feedFault`
- `hostFault`

## 当前实现
- `firmware/host-esp32s3/src/telemetry.h`
- `firmware/host-esp32s3/src/telemetry.cpp`
- `app_main.cpp` 中已接入 `telemetry_publish()`

## 当前形式
- 先走 stdout / 串口日志
- 适合 P0 bring-up 与现场联调

## 后续可扩展
1. 转成 CAN debug frame
2. 接 Wi-Fi / WebSerial / 上位机
3. 接 UI 调试页
