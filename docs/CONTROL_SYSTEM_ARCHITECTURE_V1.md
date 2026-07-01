# 控制系统架构 V1 — 车载显示器 + 控制器

> 状态：V1 初版
> 作者：全栈工程师
> 触发：PM 重新分配任务（2026-07-01）
> 关联：DISPLAY_UI_WIREFRAME_V1（设计师交付）
> 目标：可落地的车载人机控制方案，不只是展示图

---

## 0. 范围与边界

**包含**：
- 主控硬件选型（3 档对比）
- 显示器、摄像头、电机控制、推进控制、电源
- 软件模块划分
- 屏幕显示字段
- 控制输入设计
- 数据流 + MVP 清单

**不包含**（后续 V2+）：
- 具体 PCB 设计
- 真实 Gazebo / 仿真环境
- 安全认证（CE/UL）
- 详细成本报价

---

## 1. 硬件架构

### 1.1 主控选型（三档对比）

| 维度 | ESP32-S3 | Raspberry Pi 4B | Jetson Nano |
|------|---------|------------------|-------------|
| CPU | Xtensa LX7 双核 240 MHz | Cortex-A72 4 核 1.5 GHz | Cortex-A57 4 核 1.43 GHz + 128 CUDA |
| RAM | 512 KB SRAM + 8 MB PSRAM | 4 GB LPDDR4 | 4 GB LPDDR4 |
| 实时性 | ⭐⭐⭐ 硬实时 | ⭐⭐ 软实时（Linux） | ⭐⭐ 软实时（Linux）|
| 视觉推理 | ❌ 跑不动 ML | ⭐⭐ 基础 CNN/TF-Lite | ⭐⭐⭐ GPU 推理 |
| 视频输入 | 1× 摄像头 (小分辨率) | 2× CSI / USB | 2× CSI / USB |
| 显示器输出 | SPI/8080（小型）| HDMI 2× | HDMI + DP |
| 功耗 | 0.5 W | 5 W | 10 W |
| 价格 | ¥20 | ¥300 | ¥800 |
| 实时控制 3× 电机 | ⭐⭐⭐ 直接 PWM | ⭐⭐ 需要 RT-PREEMPT | ⭐⭐ 需要 RT-PREEMPT |
| **MVP 推荐** | ✅ **选这个** | 备选 | 长期升级 |

**MVP 选 ESP32-S3**：
- 硬实时满足 3 电机 1kHz 控制环
- 功耗低、发热少、车载电池友好
- 摄像头 + 视觉推理可通过外接 USB 摄像头 + 上传至云/手机
- 显示器接 SPI 5寸触摸屏（够用）

**长期升级路径**：
- ESP32 → Pi 4B（加本地视觉）
- Pi 4B → Jetson Nano（加 GPU 视觉）

### 1.2 显示器

| 选项 | 规格 | 优势 | 劣势 |
|------|------|------|------|
| **5 寸 HDMI 触屏** | 800×480 | 便宜、体积小 | 户外可视性一般 |
| 7 寸 HDMI 触屏 | 1024×600 | 大、信息多 | 体积大 |
| 7 寸高亮屏 | 1000 nits | 户外强光可读 | 贵、发热大 |
| **车载工业屏** | 7-10 寸，IP65 | 抗振防水 | ¥2000+ |

**MVP 选 5 寸 HDMI 触屏**（¥80-150）+ 遮光罩（户外）。

### 1.3 摄像头

| 方案 | 用途 | FPS | 延迟 |
|------|------|-----|------|
| USB 摄像头 (Logitech C270 等) | 球路捕捉 | 60 | 50 ms |
| Pi CSI 摄像头 (IMX219) | 球路捕捉 + 嵌入式 | 30 | 30 ms |
| 工业相机 (FLIR/Point Grey) | 高速捕捉 | 120+ | <10 ms |
| **手机 + WiFi 上传** | 慢速捕捉 | 30 | 200 ms |

**MVP 选 USB 摄像头**（最便宜、足够 MVP 验证）。

### 1.4 电机控制（3 路）

| 部件 | 选型 |
|------|------|
| 电机 | 3× 6374 BLDC（外转子当滚轮）|
| 驱动器 | 3× **SimpleFOC B-G431B-ESC1**（已选）|
| 通信 | SPI 或 CAN 总线 → 主控 ESP32 |
| 编码器 | AS5048A 磁编码器（已选）|
| 闭环 | FOC 扭矩/速度环，1 kHz |

**理由**：SimpleFOC 是项目已选方案，硬件 BOM 已确定，V1 沿用。

### 1.5 推进控制（气压主线）

| 部件 | 选型 |
|------|------|
| 气源 | 8 bar 压缩机 或 20L 钢瓶 |
| 储气罐 | 5-20L 不锈钢（带爆破片）|
| 电磁阀 | 12V 大流量两位三通阀（响应 <30 ms）|
| 压力传感器 | 0-1 MPa 模拟输出 |
| 阀门 | 手动截止阀（安全）|
| 爆破片 | 1.2× 工作压力（10 bar）|
| 泄压阀 | 1.1× 工作压力（9 bar）|
| 球挡位置 | 红外对射传感器（检测球到位）|

### 1.6 电源

| 用电器 | 电压 | 电流 | 电源 |
|--------|------|------|------|
| 主控 ESP32 | 5V | 0.5A | 5V DC-DC |
| 显示器 | 12V | 1A | 12V DC-DC |
| 3× ESC | 12-24V | 3× 30A 峰值 | 锂电池 24V |
| 电磁阀 | 12V | 1A | 12V DC-DC |
| USB 摄像头 | 5V | 0.5A | 5V |
| 风扇（散热）| 12V | 0.2A | 12V |

**主电源**：24V 锂电池组（10Ah 起）→ DCDC 隔离
- 控制电源（5V/12V）与动力电源（24V）**物理隔离**
- 加 TVS 防浪涌、保险丝

---

## 2. 软件模块

### 2.1 模块划分

```text
control_system/
├── main/                # 主控 ESP32 固件
│   ├── main.cpp         # FreeRTOS 主循环
│   ├── motor_ctrl.cpp   # 3× FOC 闭环控制
│   ├── valve_ctrl.cpp   # 电磁阀 + 压力传感器
│   ├── safety.cpp       # 急停 / 互锁
│   └── comm.cpp         # CAN/SPI 主从通信
├── vision/              # 视觉（Pi 或 ESP32-S3 USB）
│   ├── capture.cpp      # 摄像头采集
│   ├── track.cpp        # 球路识别（OpenCV）
│   └── predict.cpp      # 轨迹预测
├── ui/                  # 显示器界面（PyQt 或 LVGL）
│   ├── main_screen.py   # 主控首页
│   ├── arc_screen.py    # 弧线模拟页
│   ├── param_screen.py  # 参数调节页
│   └── diag_screen.py   # 诊断页
├── comm/                # 主从通信协议
│   ├── can_proto.md     # CAN 消息定义
│   └── serial_proto.md  # 串口消息定义
├── config/              # 配置
│   ├── mvp_params.yaml  # MVP 默认参数
│   └── presets/         # 发射预设
└── sim/                 # 仿真接口
    ├── trajectory.py    # 轨迹计算
    └── mux.py           # 3 电机混合
```

### 2.2 主控 ESP32 任务（FreeRTOS）

```c
// 任务优先级（数字越大越高）
void setup() {
  // Task 1: 电机控制循环 1kHz，优先级 10
  xTaskCreate(motor_ctrl_loop, "motor", 4096, NULL, 10, NULL);
  // Task 2: 阀门触发（紧急），优先级 12
  xTaskCreate(valve_trigger, "valve", 2048, NULL, 12, NULL);
  // Task 3: 通信接收，优先级 8
  xTaskCreate(comm_rx, "comm", 2048, NULL, 8, NULL);
  // Task 4: 安全监控，优先级 15（最高）
  xTaskCreate(safety_monitor, "safety", 1024, NULL, 15, NULL);
  // Task 5: 状态上报，优先级 5
  xTaskCreate(status_report, "status", 2048, NULL, 5, NULL);
}
```

### 2.3 显示器 UI（PyQt / LVGL）

**MVP 选 LVGL**（轻量，可在 ESP32-S3 上直接跑）：
- C 语言，资源占用小
- 支持触摸屏
- 可在 Pi 上用 Python binding

**完整版可换 PyQt**（在 Pi 4B 上）：
- Python 生态丰富
- 集成 OpenCV 视觉处理

### 2.4 视觉处理（轨迹捕捉）

```python
# vision/track.py 伪代码
def detect_ball_in_frame(frame):
    """在单帧中检测球位置（HSV 阈值 + 轮廓）"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, BALL_HSV_LOW, BALL_HSV_HIGH)
    contours, _ = cv2.findContours(mask, ...)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        return cv2.minEnclosingCircle(largest)
    return None

def track_trajectory(frames):
    """从多帧提取球位置，滤波后输出轨迹"""
    positions = []
    for f in frames:
        p = detect_ball_in_frame(f)
        if p:
            positions.append(kalman_filter(p))
    return fit_parabola(positions)
```

---

## 3. 屏幕显示内容（与 UI Wireframe 对齐）

### 3.1 主控首页字段

| 字段 | 数据源 | 刷新率 |
|------|-------|--------|
| `mode` | 用户选择 | 触发时 |
| `launch_ready` | 状态机 | 100 ms |
| `safety_locked` | 物理急停 + 软件锁 | 10 ms |
| `emergency_stop` | GPIO + 软件 | 10 ms |
| `battery_percent` | ADC | 1 s |
| `battery_voltage` | ADC | 1 s |
| `temperature` | DS18B20 | 5 s |
| `pressure` | 模拟输入 | 100 ms |
| `propulsion_type` | 配置文件 | 启动时 |
| `valve_delay_ms` | 实测 | 1 s |
| `piston_force` | 编码器 | 100 ms |
| `motor_a/b/c_rpm` | FOC 反馈 | 100 ms |
| `motor_a/b/c_temp` | NTC | 1 s |
| `camera_status` | OpenCV | 1 s |
| `camera_fps` | 帧率计数器 | 1 s |
| `vision_confidence` | 检测分数 | 100 ms |

### 3.2 弧线页字段

| 字段 | 公式/来源 |
|------|---------|
| `predicted_landing_x` | 物理模型（g, v0, angle）|
| `predicted_landing_y` | 物理模型 + Magnus |
| `actual_landing_x` | 视觉检测（球落点像素 → m）|
| `actual_landing_y` | 视觉检测 |
| `distance_error` | abs(pred - actual) |
| `lateral_error` | abs(pred_y - actual_y) |
| `landing_zone_heatmap` | 历史落点 2D 直方图 |
| `wind_estimate` | 多帧位移 → 速度差 |

### 3.3 参数页字段

| 参数 | 范围 | 单位 | 默认 |
|------|------|------|------|
| `motor_a_rpm` | 0-5000 | rpm | 2500 |
| `motor_b_rpm` | 0-5000 | rpm | 2500 |
| `motor_c_rpm` | 0-5000 | rpm | 2500 |
| `pressure` | 0-10 | bar | 8 |
| `valve_delay` | 0-100 | ms | 12 |
| `piston_force` | 0-100 | % | 75 |
| `curve_strength` | -50 to +50 | % | 0 |
| `topspin_strength` | -50 to +50 | % | 0 |

### 3.4 诊断页字段

| 字段 | 含义 | 颜色 |
|------|------|------|
| `system_status` | 整体 | 绿/黄/红 |
| `motor_a_temp` | 电机温度 | 绿<60°C / 黄<80°C / 红>80°C |
| `motor_rpm_drift` | RPM 偏差 % | <5%绿 / <10%黄 / >10%红 |
| `pressure_leak` | 压降速率 bar/s | <0.05 绿 |
| `valve_response_ms` | 阀门开闭时间 | <30 绿 |
| `battery_voltage` | 电池电压 | >22V 绿 |
| `cpu_temp` | 主控温度 | <70°C 绿 |
| `system_errors[]` | 错误码列表 | 详情面板 |

---

## 4. 控制输入

### 4.1 输入方式

| 输入 | 用途 | 优先级 |
|------|------|--------|
| 触摸屏 | 主要调节 | MVP |
| 实体旋钮 ×2 | 备用调节（戴手套） | 第二阶段 |
| 物理急停按钮 | 安全（硬急停） | **必须** |
| 物理模式旋钮 | 模式快速切换 | MVP |
| 手柄/遥控 | 远距离发射 | 可选 |
| 语音 | 解放双手 | 不推荐（噪音） |

### 4.2 安全互锁

```c
// 发射触发前必检
bool launch_check() {
    return pressure_ok()        // 气压 ≥ 设定值 ±5%
        && motors_synced()      // 3 电机 RPM 在 ±5% 范围
        && ball_loaded()        // 球挡传感器触发
        && safety_unlocked()    // 物理解锁
        && !emergency_stop()    // 急停未触发
        && camera_ready()       // 摄像头就绪
        && no_errors();         // 无系统错误
}
```

### 4.3 急停链路

```text
[物理急停] → [硬件切断电磁阀电源]
         → [GPIO 中断到主控]
         → [电机控制 0 PWM]
         → [UI 全屏红色]
         → [需人工复位]
```

**急停是硬切断**，不依赖软件。

---

## 5. 数据流图

```text
                       视觉捕捉
                          ↓
  摄像头 → Pi/Jetson ──→ 落点检测
       (USB/CSI)         ↓
                    实际落点 (x,y)
                          ↓
  物理参数 ───→  仿真引擎  ───→  预测落点
  (RPM, 压力)    (Python)        (x,y)
                          ↓
                  偏差 = 实际 - 预测
                          ↓
                  ┌────────┴────────┐
                  ↓                 ↓
              UI 显示          参数回填
          (车载显示器)    (推荐新 RPM/压力)
                              ↓
                          ESP32 主控
                              ↓
              ┌───────┬───────┬───────┐
              ↓       ↓       ↓       ↓
            电机 A  电机 B  电机 C  电磁阀
              (6374) (6374) (6374)   (气压)
              ↓       ↓       ↓       ↓
            can    can    can    球被发射
              └───────┴───────┘
                  ↓
                 球
```

---

## 6. MVP 版本清单

### 6.1 MVP V1.0（4 周内）

| 项目 | 描述 | 状态 |
|------|------|------|
| 硬件 | ESP32-S3 + 3× ESC + 5寸触屏 + USB 摄像头 | 采购 |
| 控制 | 3 电机 1kHz 闭环 + 阀门触发 | 实现 |
| 安全 | 物理急停 + 气压互锁 | 实现 |
| UI | LVGL 4 屏（首页/弧线/参数/诊断）| 实现 |
| 视觉 | 球路捕捉（简单阈值）| 简化 |
| 通信 | USB 串口（PC 调试）| 简化 |

### 6.2 V1.1（4-8 周）

- Pi 4B 替代 ESP32-S3（加本地视觉）
- 完整 4 屏 UI（PyQt）
- 历史发射记录数据库
- 预设管理

### 6.3 V2.0（8-12 周）

- Jetson Nano 升级
- 完整视觉推理（球速、落点预测）
- 自动参数校正
- 多发射器联网管理

---

## 7. 验收标准

按 PM 要求：

| 标准 | 回答 |
|------|------|
| 1. 人怎么操作 | 触摸屏 + 旋钮 + 急停。模式按钮 → 确认 → 装球 → 发射。详情见 UI Wireframe |
| 2. 机器怎么执行 | ESP32 → FOC ESC → 3 电机 + 电磁阀。闭环 1kHz。阀门响应 <30ms |
| 3. 球路怎么被预测/反馈 | 物理模型（抛物 + Magnus）预测 + 摄像头识别实际 → 偏差 → UI |
| 4. 异常怎么停机 | 物理急停硬切断 + 软件互锁 → 全屏红 → 诊断页 → 复位 |
| 5. 切回推进结构 | 气压主线（轴向）+ 三电机控旋，控制器对应有 推进源切换 + 三电机 RPM 控制 |

---

## 8. 与 UI Wireframe 的接口

按设计师 `DISPLAY_UI_WIREFRAME_V1` 的字段清单：

```python
# ui/interface.py 字段
@dataclass
class UIData:
    # Mode
    mode: str                           # "STRAIGHT" / "LEFT_CURVE" / ...
    launch_ready: bool
    safety_locked: bool
    emergency_stop: bool

    # Pressure
    pressure_mpa: float
    propulsion_type: str                # "pneumatic" / "tangent_friction"
    valve_delay_ms: float
    piston_force_pct: float

    # Motors
    motor_a_rpm: int
    motor_b_rpm: int
    motor_c_rpm: int
    motor_a_temp_c: float
    motor_b_temp_c: float
    motor_c_temp_c: float

    # Vision
    camera_status: str                  # "OK" / "ERROR" / "OFFLINE"
    camera_fps: float
    vision_confidence: float

    # Trajectory
    predicted_landing_x: float
    predicted_landing_y: float
    actual_landing_x: float
    actual_landing_y: float
    distance_error_m: float
    lateral_error_m: float

    # Power
    battery_percent: float
    battery_voltage: float
    system_errors: list[str]
```

主控（ESP32）和 UI（Pi 屏）通过 CAN 或 USB 串口交换 UIData。

---

## 9. 已知风险

| 风险 | 缓解 |
|------|------|
| ESP32 算力不够视觉 | MVP 用 USB 摄像头 + Pi 远端处理 |
| 5 寸屏户外可读性差 | 加遮光罩，后期换 7寸高亮 |
| 锂电池振动/温度 | 用工业级电池（带 BMS）|
| 电磁阀误触发 | 双路阀门 + 物理急停 + 软件互锁 |
| 视觉识别误判 | 加置信度阈值，低置信度禁用发射 |
| 急停响应时间 | 物理急停硬切断 < 10ms |

---

## 10. 交付物

- ✅ 本文档 `CONTROL_SYSTEM_ARCHITECTURE_V1.md`
- ⏭ `MVP_PARAMS_V1.yaml`（默认参数）
- ⏭ `CAN_PROTOCOL_V1.md`（如果需要）
- ⏭ `comm.proto`（主从通信协议）
- ⏭ `safety_checklist.md`（安全清单）

---

## 11. 变更日志

- V1：初版，2026-07-01，按 PM 重新分配任务交付
