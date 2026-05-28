# 固件模块划分

## 1. Core / App
- `main`
- 系统初始化
- 状态机调度
- 命令分发

## 2. Motor Control
- `motor_a_controller`
- `motor_b_controller`
- `motor_c_controller`
- SimpleFOC 参数初始化
- 目标 RPM 下发
- 闭环更新

## 3. Sensor
- Hall 采样
- 入球检测
- 电压 / 电流 / 温度采样（若硬件具备）

## 4. Launch State Machine
- `IDLE`
- `PRESPIN`
- `READY`
- `SHOOT`
- `FAULT`
- `ESTOP`

## 5. Safety
- 急停处理
- 限速
- 故障联锁
- 上电安全空闲态
- 看门狗（建议）

## 6. Telemetry / Debug
- 串口日志
- RPM / faultCode 输出
- 调试参数打印

## 7. Config
- 电机参数
- Hall 极对数 / 方向配置
- 目标 RPM 档位
- 加减速曲线
- 故障阈值

## 8. 后续可扩展（非 P0）
- 参数持久化
- 上位机调参
- CAN / BLE / Wi-Fi 通信桥
- 多球供给控制
