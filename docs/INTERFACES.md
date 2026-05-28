# P0 接线与接口定义

## 1. 系统拓扑
- 主控：STM32G431
- 电机：BLDC_A / BLDC_B / BLDC_C
- 驱动：DRV_A / DRV_B / DRV_C
- 反馈：Hall_A / Hall_B / Hall_C
- 传感器：BALL_SENSOR
- 安全：ESTOP

## 2. 主控接口分组
### 电机控制输出
- `PWM_A_U / PWM_A_V / PWM_A_W`
- `PWM_B_U / PWM_B_V / PWM_B_W`
- `PWM_C_U / PWM_C_V / PWM_C_W`

### 反馈输入
- `HALL_A_1 / HALL_A_2 / HALL_A_3`
- `HALL_B_1 / HALL_B_2 / HALL_B_3`
- `HALL_C_1 / HALL_C_2 / HALL_C_3`

### 控制 / 安全输入
- `BALL_SENSOR_IN`
- `ESTOP_IN`
- `ENABLE_IN`

### 调试 / 通信
- `UART_DBG_TX / UART_DBG_RX`
- 预留 `CAN / USB / UART bridge`

## 3. 逻辑关系
- `ESTOP_IN = active` -> 全局立即停机，状态切 `ESTOP`
- `BALL_SENSOR_IN = ready` 且三轮已达到目标转速 -> 允许进入 `READY`
- 任一路驱动故障 -> 全局切 `FAULT`

## 4. 上电默认行为
1. 上电进入 `IDLE`
2. 所有 PWM disabled
3. 急停状态先自检
4. 仅在收到预转命令后开启三轮控制

## 5. P0 最小指令集
- `set_target_rpm(wheel, rpm)`
- `prespin(speedProfile)`
- `shoot(spinMode, speedLevel)`
- `stop_all()`
- `clear_fault()`

## 6. P0 最小状态回传
- `systemState`
- `wheelA.targetRpm / actualRpm`
- `wheelB.targetRpm / actualRpm`
- `wheelC.targetRpm / actualRpm`
- `faultCode`
- `ballDetected`
