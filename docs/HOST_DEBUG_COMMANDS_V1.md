# Host 调试命令接口 v1

## 文件
- `firmware/host-esp32s3/src/debug_command.h`
- `firmware/host-esp32s3/src/debug_command.cpp`

## 目标
提供一个最小文本命令接口骨架，方便现场调试时手动改参数、触发发射、触发急停、清故障。

## 当前支持命令
- `set base 2100`
- `set delta 250`
- `spin straight`
- `spin topspin`
- `spin backspin`
- `spin left`
- `spin right`
- `fire`
- `estop`
- `clear fault`
- `ball loaded`
- `ball empty`

## 当前用途
- bring-up 阶段手动调 `baseRpm`
- 快速切换 `spinMode`
- 手动触发 `FIRE`
- 验证急停/故障恢复流程

## 下一步
- 接到串口命令行
- 接到 WebSerial / 上位机调试面板
- 增加单独 wheel 点动命令
