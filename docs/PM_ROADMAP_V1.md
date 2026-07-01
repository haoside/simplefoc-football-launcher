# PM 路线图 v1

> 由 Mia｜PM 整理，基于 bring-up plan、BOM、仿真和现有文档。
> 最后更新：2026-07-01

## 项目状态总览

| 阶段 | 状态 | 说明 |
|------|------|------|
| P0 方案冻结 | ✅ 完成 | 技术方案、BOM、CAN 协议、固件架构已定义 |
| 结构 CAD 定型 | ✅ 完成 | v12 三轮 6374 + 220mm 球通道 `cad/3d-print/tri-motor-6374-v12/` |
| 固件代码 | ✅ 代码库完成 | Host ESP32-S3 + Node B-G431B-ESC1 完整代码 |
| P0-A 台架验证 | 🔄 等待物料 | 物料采购中，bring-up 执行手册已就绪 |
| P0-B 实球发射 | ⏳ 待启动 | 依赖 P0-A 通过 + 高电流驱动板 |
| P0 现场测试 | ⏳ 待启动 | 依赖 P0-B 通过 |

## P0 里程碑

| M# | 里程碑 | 关键交付 | 依赖 |
|----|--------|---------|------|
| M1 | 台架最小闭环 | 单电机速度闭环 + Host↔Node CAN 通信 | 物料到货 |
| M2 | 三轮同步 + 低速射球 | 三电机同步预转 + 单次稳定出球 | M1 |
| M3 | 完整发射状态机 | 球检测 + 状态机 + 急停保护联调 | M2 |
| M4 | 15~20m 长传验证 | 目标射程 + 精度 + 数据回填仿真 | M3 + 结构定型 |

## 任务拆解

### Firmware（固件）

| ID | 任务 | 里程碑 | 状态 | 前置 |
|----|------|--------|------|------|
| FW-00 | Phase 0 · ESP32-S3 Host 最小固件 | M1 | TODO | — |
| FW-01 | Phase 1 · STM32G431 Node 最小固件 | M1 | TODO | — |
| FW-02 | Phase 2 · Hall 读取 | M1 | TODO | FW-01 |
| FW-03 | Phase 3 · Driver PWM 输出 | M2 | TODO | FW-02 |
| FW-04 | Phase 4 · 单电机开环低速 | M2 | TODO | FW-03 |
| FW-05 | Phase 5 · 单电机速度闭环 | M2 | TODO | FW-04 |
| FW-06 | Phase 6 · Host ↔ 单 Node 联调 | M2 | TODO | FW-00 + FW-05 |
| FW-07 | Phase 7 · 三 Node 联调 | M3 | TODO | FW-06 |
| FW-08 | Phase 8 · 发射状态机 | M3 | TODO | FW-07 |

### Hardware（硬件）

| ID | 任务 | 里程碑 | 状态 | 前置 |
|----|------|--------|------|------|
| HW-00 | ESP32-S3 Host PCB 设计 | M1 | TODO | — |
| HW-01 | B-G431B-ESC1 Node 适配 | M1 | TODO | — |
| HW-02 | 电源方案 · 24V LiFePO4 | M2 | TODO | — |
| HW-03 | CAN 总线拓扑 | M2 | TODO | HW-00 + HW-01 |
| HW-04 | 传感器集成 | M3 | TODO | FW-08 |

### Mechanical（机械）

| ID | 任务 | 里程碑 | 状态 | 前置 |
|----|------|--------|------|------|
| MC-00 | 120° 三轮布局机架 | M1 | TODO | 结构定型 |
| MC-01 | 导管 v1 3D 打印 | M2 | TODO | MC-00 |
| MC-02 | 电机安装板钣金 | M2 | TODO | MC-00 |
| MC-03 | 可移动底盘 + 电池仓 | M3 | TODO | MC-00 |

### Integration（集成）

| ID | 任务 | 里程碑 | 状态 | 前置 |
|----|------|--------|------|------|
| IG-00 | 急停 / 过流 / 堵转 / 过热保护 | M3 | TODO | HW-04 + FW-08 |
| IG-01 | 单球手动上球测试 | M3 | TODO | MC-01 + FW-08 |
| IG-02 | 15~20m 长传实测 | M4 | TODO | IG-00 + IG-01 |
| IG-03 | 自动捡球接口预留 | M4 | TODO | MC-03 |

## 关键路径

```
FW-00 + FW-01 (并行)
  → FW-02 → FW-03 → FW-04 → FW-05 → FW-06 → FW-07 → FW-08
                                                          ↓
MC-00 (结构定型) → MC-01 ─────────────────────────→ IG-01
MC-00 → MC-02 ────────────────────────────────────→ IG-00
HW-00 + HW-01 (并行) → HW-03 → HW-04 ────────────→ IG-00
                                                          ↓
                                                     IG-02 (15~20m 长传)
```

## 结构定型 ✅ 已确认

| 参数 | 决定 | 说明 |
|------|------|------|
| 传动方式 | 6374 外转子直驱 | 无齿轮/皮带，摩擦轮直装电机轴 |
| 中心通道 | 标准 5 号球 (216–226mm) | 通道内径 = 球径 + 轮面压缩量 + 公差 |
| 摩擦轮直径 | 由结构约束确定 | 建议 90–130mm，待结构设计后细化 |
| 支架材料 | 按结构强度确定 | 以强度为唯一判据，不限定工艺 |

详细参数见 `docs/PM_STRUCTURAL_DECISIONS_V1.md`

## 参考文档索引

| 文档 | 路径 |
|------|------|
| 固件 Bring-up Plan | `docs/FIRMWARE_BRINGUP_PLAN.md` |
| 固件 Bring-up Checklist | `docs/FIRMWARE_BRINGUP_CHECKLIST.md` |
| BOM 草案 | `docs/BOM_DRAFT.md` |
| CAN 协议 | `docs/CAN_PROTOCOL_V1.md` |
| 传感器布局 | `docs/SENSOR_LAYOUT.md` |
| 轮径规则 | `docs/WHEEL_DIAMETER_RULES.md` |
| P0-A 测试看板 | `docs/P0A_TEST_KANBAN_V1.md` |
| P0-A 下一步动作 | `docs/P0A_NEXT_ACTIONS.md` |
| 采购清单 | `docs/procurement/P0A_PURCHASE_CHECKLIST_V1.md` |
| 机械文档索引 | `docs/mechanical/SKETCH_INDEX.md` |
| 仿真模型 | `sim/football_launch_model.py` |
| Bring-up 执行手册 | `docs/PM_BRINGUP_EXECUTION_V1.md` |
