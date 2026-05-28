# 固件模块划分

## 1. Upper Controller / App
- `main`
- 参数接收
- `rpm_mixer_120deg`
- 发射状态机调度
- 命令分发

## 2. Motor Node Control
- `node_a_controller`
- `node_b_controller`
- `node_c_controller`
- SimpleFOC 参数初始化
- 目标 RPM 下发
- 单节点闭环更新

## 3. Sensor
- Hall 采样
- 管道有球检测
- 发射位到球检测
- 出球检测
- 电压 / 电流 / 温度采样（若硬件具备）

## 4. Launch State Machine
- `IDLE`
- `SPINUP`
- `FEED_READY`
- `BALL_IN_POSITION`
- `FIRE`
- `RELOAD`
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
