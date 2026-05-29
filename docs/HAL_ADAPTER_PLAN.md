# HAL 适配层计划 v1

## 目标
把当前 Host / Node 控制骨架和未来真实底层驱动解耦，便于分别接入 ESP32-S3 与 STM32G431 平台能力。

## Host HAL
### 文件
- `firmware/host-esp32s3/src/hal/host_hal.h`
- `firmware/host-esp32s3/src/hal/host_hal_stub.cpp`

### 接口范围
- TWAI/CAN 初始化 / 收发
- 传感器读取
- 急停输入
- 供球执行器触发
- LED / Buzzer
- 毫秒时基

### 后续真实实现
- ESP-IDF `TWAI`
- GPIO input/output
- LEDC PWM / GPIO drive
- FreeRTOS tick / esp_timer

## Node HAL
### 文件
- `firmware/motor-node-g431/App/hal/node_hal.h`
- `firmware/motor-node-g431/App/hal/node_hal_stub.cpp`

### 接口范围
- FDCAN 初始化 / 收发
- PWM 使能与三相输出
- Hall 读取
- VBUS / Current / Temp ADC 采样
- Driver fault 输入
- 毫秒时基

### 后续真实实现
- STM32 HAL / LL
- FDCAN
- TIM PWM
- ADC injected/regular conversion
- EXTI / timer capture for Hall

## 当前策略
- 先提供 stub 版本，保证上层状态机、协议、控制链可以先跑
- 后续逐个替换为真实硬件适配
