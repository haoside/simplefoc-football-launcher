# 运动系统 × 固件架构映射 v1

> 理清物理运动系统与固件模块的对应关系。
> 最后更新：2026-07-10

## 系统总览

```
┌─────────────────────────────────────────────────────────┐
│                    HOST (ESP32-S3)                       │
│  状态机 · 传感器 · CAN通信 · RPM计算 · 安全保护         │
└────────┬────────────┬────────────┬──────────────────────┘
         │ CAN        │ CAN        │ CAN
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │ NODE A  │  │ NODE B  │  │ NODE C  │
    │ (G431)  │  │ (G431)  │  │ (G431)  │
    │ 电机控制│  │ 电机控制│  │ 电机控制│
    └────┬────┘  └────┬────┘  └────┬────┘
         │ PWM         │ PWM         │ PWM
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │ 6374 A  │  │ 6374 B  │  │ 6374 C  │
    │ 12:00   │  │ 8:00    │  │ 4:00    │
    │ 摩擦轮  │  │ 摩擦轮  │  │ 摩擦轮  │
    └─────────┘  └─────────┘  └─────────┘
```

## 运动部件 → 固件模块

| 物理部件 | 规格 | 固件位置 | 职责 |
|---------|------|---------|------|
| **6374 BLDC ×3** | 170~190KV, Hall | Node `velocity_loop.cpp` | 速度闭环控制 |
| **摩擦轮 ×3** | 直驱电机轴 | Node `simplefoc_adapter.cpp` | PWM→电机转速 |
| **Hall传感器 ×3/电机** | 3相 | Node `sensor_reader.cpp` | 转速反馈 |
| **母线电压** | 24V LiFePO4 | Node `node_telemetry.cpp` ADC | 过压/欠压保护 |
| **相电流** | ADC采样 | Node `node_safety.cpp` | 过流保护 |
| **温度** | NTC热敏电阻 | Node `node_safety.cpp` | 过热保护 |
| **DRV_EN** | GPIO输出 | Node `node_control.cpp` | 驱动使能/急停 |
| **DRV_FAULT_N** | GPIO输入 | Node `node_safety.cpp` | 驱动故障检测 |
| **球检测传感器** | GPIO输入 | Host `feed_state.cpp` | 球到位检测 |
| **急停按钮** | GPIO输入 | Host `launch_state_machine.cpp` | 系统急停 |
| **CAN总线** | 500kbps | Host+Node `*_comm.cpp` | 主从通信 |
| **发射触发** | GPIO输出 | Host `launch_state_machine.cpp` | 触发发射 |
| **供球执行器** | GPIO输出 | Host `feed_controller.cpp` | 供球控制 |

## 控制流：从指令到运动

### 1. 发射指令 → 转速

```
用户输入 (baseRpm + spinMode + deltaRpm)
  │
  ▼
Host: can_host_loop.cpp → compute_targets()
  │  根据spinMode计算三轮目标RPM:
  │  STRAIGHT:  w1=w2=w3=base
  │  TOPSPIN:   w1=base+d, w2=w3=base-d/2
  │  LEFT_CURVE: w2=base+d, w3=base-d
  │
  ▼
Host → CAN SET_RPM → Node A/B/C
  │
  ▼
Node: node_control.cpp → clamp_rpm() → bg_hal_set_target_rpm()
  │
  ▼
Node: velocity_loop.cpp → simplefoc_adapter_set_target_rpm()
  │
  ▼
SimpleFOC → PWM输出 → 6374电机转动
```

### 2. 转速反馈 → 闭环

```
6374 Hall传感器
  │
  ▼
Node: sensor_reader.cpp → 读取Hall状态 → 计算转速
  │
  ▼
Node: velocity_loop.cpp → simplefoc_adapter_get_actual_rpm()
  │
  ▼
Node → CAN STATUS帧 → Host
  │
  ▼
Host: can_host_loop.cpp → apply_status_to_wheel()
  │  更新 wheel1/2/3.actualRpm
  ▼
Host: launch_state_machine.cpp → system_ready()判断
  │  三轮都达到目标转速±80rpm → 进入READY
```

### 3. 发射序列

```
IDLE
  │ baseRpm > 0
  ▼
SPINUP ─────────────────────────────────┐
  │ 三轮加速到目标转速                    │
  │ Host持续下发SET_RPM                  │
  │ Node反馈STATUS                       │
  │                                      │
  ▼                                      │
READY ←─── ballLoaded=1 && system_ready ─┘
  │ 等待fireRequest                      │
  │ 如果ballLoaded=0 → 回到SPINUP        │
  │                                      │
  ▼ fireRequest=1
FIRE
  │ host_hal_trigger_launch() → 发射触发
  │ 清除fireRequest
  │
  ▼
COOLDOWN
  │ 等待RELOAD_DELAY_MS (300ms)
  │
  ▼
SPINUP (如果baseRpm>0) 或 IDLE
```

## 数据帧格式

### Host → Node

| 帧类型 | CAN ID | 用途 | 周期 |
|--------|--------|------|------|
| SET_RPM | 0x100+nodeId | 目标转速 + 使能 | 20ms |
| SET_PARAM | 0x110+nodeId | PID参数调整 | 按需 |
| CLEAR_FAULT | 0x120+nodeId | 清除故障 | 按需 |
| ESTOP | 0x12F | 急停广播 | 按需 |

### Node → Host

| 帧类型 | CAN ID | 用途 | 周期 |
|--------|--------|------|------|
| STATUS | 0x180+nodeId | 实际转速/电压/电流 | 20ms |
| HEARTBEAT | 0x190+nodeId | 状态/故障码/温度 | 100ms |
| FAULT | 0x1A0+nodeId | 故障详情 | 触发式 |

## 安全保护链路

```
Node层 (本地保护, <1ms响应):
  过流 → FAULT_OVERCURRENT → 关闭PWM + 上报
  过热 → FAULT_OVERTEMP → 关闭PWM + 上报
  驱动故障 → FAULT_OVERCURRENT → 关闭PWM + 上报

Host层 (系统保护, <200ms响应):
  收到Node FAULT/HEARTBEAT异常 → host_fault_raise()
  通信超时 (200ms无HEARTBEAT) → FAULT_COMMS_TIMEOUT
  急停按钮 → 广播ESTOP → 所有Node停机
  状态机保护:
    无球禁止发射 (ballLoaded=0 → 不进FIRE)
    出球超时保护 (FIRE_TO_EXIT_TIMEOUT_MS)
    供球超时保护 (FEED_TO_CHAMBER_TIMEOUT_MS)
```

## 文件索引

### Host (ESP32-S3)

| 文件 | 运动相关职责 |
|------|------------|
| `src/app_main.cpp` | 主循环: 传感器→状态机→CAN→遥测 |
| `src/launch_state_machine.cpp` | IDLE/SPINUP/READY/FIRE/COOLDOWN |
| `src/can_host_loop.cpp` | RPM mixer + 三轮SET_RPM + STATUS解析 |
| `src/rpm_mixer_120.cpp` | 120°差速计算 (ux/uy → w1/w2/w3) |
| `src/host_state.h` | 系统状态模型 |
| `src/feed_state.cpp` | 供球状态机 (管→仓→发射位→出球) |
| `src/safety_manager.cpp` | 安全判断 (estop + chamberReady) |
| `src/host_fault.cpp` | 故障记录/清除 |
| `src/shot_presets.cpp` | 射门预设 (转速/角度/旋向) |
| `src/debug_command.cpp` | 调试命令 (直接控制RPM/旋向) |

### Node (STM32G431 ×3)

| 文件 | 运动相关职责 |
|------|------------|
| `src/app_main.cpp` | 主循环: 通信→安全→控制→上报 |
| `src/node_control.cpp` | 使能判断 + RPM钳位 + 状态切换 |
| `src/node_comm.cpp` | SET_RPM接收 + STATUS/HEARTBEAT发送 |
| `src/node_safety.cpp` | 过流/过热检测 + PWM关断 |
| `src/node_telemetry.cpp` | ADC采样: VBUS/电流/温度 |
| `src/node_state.cpp` | 节点状态模型 |
| `src/node_profile.cpp` | 节点身份 (wheel A/B/C) |
| `App/velocity_loop.cpp` | 速度闭环 (SimpleFOC适配) |
| `App/simplefoc_adapter.cpp` | SimpleFOC接口封装 |
| `App/sensor_reader.cpp` | Hall传感器读取 → RPM计算 |

### Common

| 文件 | 职责 |
|------|------|
| `protocol.h` | CAN帧定义 + 状态码 + 故障码 |
| `protocol_codec.cpp` | 帧编码/解码 |
| `config.h` | 全局常量 (RPM范围/超时/周期) |
| `fault_codes.h` | 故障码文本映射 |
