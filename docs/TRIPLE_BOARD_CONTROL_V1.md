# 三板协同控制方案 — MKS XDRIVE Mini ×2 + ESP32-S3 主控

> 参考仓库: github.com/justlovescience/MKS-XDRIVE-MINI
> 架构: 3 电机由 **2 块 XDRIVE Mini**（每块双轴）驱动，ESP32-S3 通过 CAN 总线统一调度。
> 硬件版本对应 CAD v27（`cad/3d-print/direct-drive-cage-v27`）。

## 0. 双轴能力确认（2026-08-25 验证）

**MKS XDRIVE Mini 确为双轴控制器**，证据：

1. 官方固件 bin 分析：JSON 配置树含 **2 套完整 `motor`/`controller`/`encoder` object**
   （axis1 与 axis0 结构对称，非占位符）
2. 固件含 2 处 DRV8301 引用（双通道栅极驱动 = 双路功率级）
3. 参考仓库明示 "acts like a dual-axis ODrive"，多板 ghost 轴冲突即为此故
4. Hackaday 作者以同款板搭建多轴机器人系统验证过 CAN 协同

**意外收获**: AS5047P 为**板载集成**（Makerbase 官方规格 "with AS5047P on board"），
无需外置编码器小板；磁铁装电机轴外端对准板上编码器窗口即可。
CAD v27 的外置 AS5047 角位可简化或留作备用。

## 1. CAN 节点分配（防 ghost 冲突）

XDRIVE Mini 出厂即"双轴 ODrive"，一块板占两个 node_id。三电机分配：

| 板 | 物理轴 | CAN node_id | 驱动对象 |
|---|---|---|---|
| XDRIVE #1 | axis0 | **0** | WheelA (12点) |
| XDRIVE #1 | axis1 | **1** | WheelB (4点) |
| XDRIVE #2 | axis0 | **2** | WheelC (8点) |
| XDRIVE #2 | axis1 | **63** | 无电机 → listen-only 幽灵轴 |

关键命令（每板刷固件后执行一次）:

```python
# XDRIVE #1
odrv0.axis0.config.can_node_id = 0
odrv0.axis1.config.can_node_id = 1
# XDRIVE #2
odrv0.axis0.config.can_node_id = 2
odrv0.axis1.config.can_node_id = 63   # 幽灵轴让出总线
odrv0.can.set_baud_rate(500000)
```

## 2. 每轴配置（适配本项目 6374 + 板载 AS5047P）

在参考 `my_config.txt` 基础上修改为**速度模式**（发射器需求）：

```python
odrv0.axis0.motor.config.pole_pairs = 7        # 6374=14极
odrv0.axis0.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT
odrv0.axis0.motor.config.current_lim = 40      # 发射峰值
odrv0.axis0.motor.config.calibration_current = 10
odrv0.axis0.motor.config.requested_current_range = 60
odrv0.axis0.encoder.config.mode = ENCODER_MODE_SPI_ABS_AMS   # 板载 AS5047P
odrv0.axis0.encoder.config.abs_spi_cs_gpio_pin = 7
odrv0.axis0.encoder.config.cpr = 16384
odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
odrv0.axis0.controller.config.vel_limit = 100          # turns/s ≈ 6000rpm
odrv0.axis0.controller.config.vel_gain = 0.08
odrv0.axis0.controller.config.vel_integrator_gain = 0.4
odrv0.axis0.config.startup_closed_loop_control = True
```

> AS5047P 板载：磁铁装电机轴外端（径向磁化），对准板上编码器芯片窗口，气隙 1~2mm。

## 3. 总线拓扑

```
ESP32-S3 ──TWAI(SN65HVD230)──┬── XDRIVE#1 (node 0,1)
                             ├── XDRIVE#2 (node 2,63)
                       120Ω ×2 终端电阻 (总线两端)
CAN: TX=GPIO5 RX=GPIO4 @500kbps
```

⚠️ SN65HVD230 常见坑（Hackaday 实测）：模块 RS 引脚电阻过大 → 收发器进入
listen-only。需将该电阻短接改 0Ω，保证双向通信。

## 4. 固件纪律（防砖）

- 全部 XDRIVE 锁 **v0.5.1** 原厂 bin（仓库 Firmwares/XDRIVE_MINI_original_FW.bin）
- **禁止 odrivetool `upgrade`**
- 变更配置只走 `erase_configuration() → save_configuration()` 流程
- 备好 ST-Link V2 以便万一砖掉重刷

## 5. 主控侧软件（ESP32-S3）

复用参考仓库 `Arduino/src/ODriveEsp32Twai.hpp`（TWAI 适配 ODriveCAN 库），本项目新增发射状态机：

```cpp
// 轴映射
ODriveCAN odrvA {wrap_can_intf(can_intf), 0};   // WheelA
ODriveCAN odrvB {wrap_can_intf(can_intf), 1};   // WheelB
ODriveCAN odrvC {wrap_can_intf(can_intf), 2};   // WheelC

enum State { IDLE, SPINUP, READY, LAUNCH, COOLDOWN };
// SPINUP : Set_Velocity 三轴到目标 rpm (mixer 输出)
// READY  : 球在位 + 三轮速差 <1% → 允许上球
// LAUNCH : 保持速度 2s 接球通过
// COOLDOWN: 补能 3s (轮速跌落后恢复)
```

指令帧：ODrive 标准 `Set_Velocity`(0x00D)，100Hz 下发；遥测订阅 `Get_Encoder_Estimates`(0x009)。

## 6. 上电/安全时序

1. 主控先上电 → CAN 就绪 → 再合电机动力电（预充电路）
2. 各轴自动 `startup_closed_loop_control` 进入闭环
3. 急停按钮：硬断 XDRIVE enable + 广播 ESTOP，`Clear_Errors` 前拒绝再使能
4. 任一轴 heartbeats 超 200ms 未收到 → 全队回 IDLE

## 7. 功率实测参考（Hackaday 同款板数据）

LA8308 170KV：50A 出 ~2 Nm，25A 出 ~1.2 Nm；先过热的是电机而非驱动 MOSFET。
→ XDRIVE 对 6374 功率档位有余量；散热仍需基座铝板+风冷（CAD v27 预留抬高空间）。

## 8. 与仿真参数的衔接

`sim/odrive_launch_sim_v1.py` 的 `MechConfig.wheel_rpm` 直接映射
`Set_Velocity(turns_per_sec) = wheel_rpm / 60`；
裸壳 φ63 后线速度 = rpm/60 × π×0.063 —— 20m 长传需 ~6000rpm，
24V 下 170KV 达不到，需按 README v27 供电方案复核（12S 或换 KV）。
