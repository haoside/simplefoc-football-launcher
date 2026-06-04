# 固件 Bring-up 计划 v1

> 目标：让硬件首版上电流程和固件动作一一对应，先跑通单电机闭环，再扩到三节点联调。

## Phase 0 - Host 板最小固件
### 目标
- ESP32-S3 可启动
- 串口日志正常
- 传感器 GPIO 可读
- CAN 初始化成功

### 固件动作
1. 上电打印版本号
2. 初始化 GPIO / UART / CAN
3. 轮询 `ball_present / exit_detect / estop`
4. 周期输出状态帧

### 验收
- 串口可见 boot log
- GPIO 状态变化可见
- CAN 控制器进入正常模式

---

## Phase 1 - Motor Node 最小固件（无电机）
### 目标
- STM32G431 可下载
- Driver 使能脚受控
- Driver fault 可读
- ADC 可读 VBUS

### 固件动作
1. 初始化时钟 / GPIO / ADC / CAN
2. 默认 `DRV_EN=0`
3. 读取 `DRV_FAULT_N`
4. 读取 `VBUS_SENSE`
5. 上报基础 `STATUS`

### 验收
- SWD 下载正常
- 串口/调试口可看状态
- Driver 不误报 fault
- VBUS 读数合理

---

## Phase 2 - Hall 读取
### 目标
- Hall A/B/C 相序正确
- 手转电机时能输出转速/方向

### 固件动作
1. 配置 Hall 输入中断/捕获
2. 输出原始 Hall 状态
3. 计算 electrical state / rpm
4. 上报 `actualRpm`

### 验收
- 手转电机时 Hall 状态变化正确
- 转速数值连续、无明显乱跳

---

## Phase 3 - Driver PWM 输出（脱开电机负载谨慎验证）
### 目标
- PWM 波形正常
- enable/fault 联锁正常

### 固件动作
1. 初始化 PWM timer
2. 仅在安全条件满足时拉高 `DRV_EN`
3. 输出低占空测试 PWM
4. fault 触发即关断

### 验收
- 示波器看到 3 路 PWM
- `DRV_EN` 可控
- fault 后 PWM 关闭

---

## Phase 4 - 单电机开环低速
### 目标
- 电机可低速平稳转动
- Hall 与方向一致

### 固件动作
1. 初始化 SimpleFOC 基础对象
2. 使用开环/低风险模式启动
3. 限速、限流、限加速度
4. 实时打印 rpm / fault

### 验收
- 电机低速可控
- 无异常发热、无明显振动

---

## Phase 5 - 单电机速度闭环
### 目标
- 达到 P0 单轮闭环范围 `500~3000 rpm`
- 空载误差满足预期

### 固件动作
1. 切换到 velocity loop
2. 配置基础 PID
3. 支持 `SET_RPM`
4. 周期上报 `STATUS`

### 验收
- 目标转速可跟踪
- 空载稳态误差约 `±3%`

---

## Phase 6 - Host ↔ 单 Node 联调
### 目标
- Host 可下发目标 RPM
- Node 可回传状态
- 通信超时可保护

### 固件动作
1. Host 发 `SET_RPM`
2. Node 收到后更新目标
3. Node 定期发 `STATUS/HEARTBEAT`
4. Host 监测超时转 `FAULT`

### 验收
- Host 改目标时 Node 行为正确
- 拔掉通信后系统进入保护

---

## Phase 7 - 三 Node 联调
### 目标
- 三轮同步启动
- 120° RPM mixer 生效

### 固件动作
1. Host 下发三节点不同目标 RPM
2. 检查同步启动时延
3. 记录轮间偏差

### 验收
- 三轮 90% 目标转速时间差 `< 150ms`

---

## Phase 8 - 单球手动上球 / 发射状态机
### 目标
- 手动放球后才允许发射
- 无球不发
- 出球检测 / 超时保护完整

### 固件动作
1. Host 状态机接入 `ball_present / exit_detect / estop`
2. `IDLE -> SPINUP -> READY -> FIRE -> COOLDOWN -> IDLE`
3. `ball_present=0` 时禁止进入 `FIRE`
4. 发射超时 / 出球未检测进入 `FAULT`

### 验收
- 手动上球检测正确
- 无球不能发射
- 出球检测或超时保护有效
