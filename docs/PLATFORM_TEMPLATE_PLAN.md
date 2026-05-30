# 平台真实实现模板 v1

## Host / ESP32-S3
### 文件
- `firmware/host-esp32s3/src/hal/espidf/host_hal_espidf_twai.cpp`

### 已给出模板内容
- TWAI 初始化位置
- CAN 发送/接收模板
- GPIO 读取传感器模板
- 急停读取模板
- 供球 actuator 占位
- 毫秒时基占位

### 目标平台
- ESP-IDF
- `driver/twai.h`
- `driver/gpio.h`
- `esp_timer.h`

## Node / STM32G431
### 文件
- `firmware/motor-node-g431/App/hal/stm32/node_hal_stm32_template.cpp`

### 已给出模板内容
- FDCAN 初始化位置
- CAN 发送/接收模板
- PWM enable / UVW 输出模板
- Hall 读取模板
- VBUS / Current / Temp 采样模板
- Driver fault 读取模板

### 目标平台
- STM32 HAL / LL
- `fdcan.h`
- `adc.h`
- `tim.h`
- `gpio.h`

## 当前作用
- 把“后面怎么接真实平台”从口头说明，变成仓库内可直接展开的模板文件
- 后续工程实现只需要把模板中的注释位置替换成真实 API 调用
