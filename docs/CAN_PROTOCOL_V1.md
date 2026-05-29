# CAN 协议 v1

> 用于 `ESP32-S3 Host` 与 `STM32G431 Motor Node` 之间通信。P0 先冻结最小报文集，满足单节点闭环、三节点联调、状态回传与故障保护。

## 1. 总线参数
- Bus: `CAN 2.0A`（11-bit standard ID）
- Bitrate: `500 kbps`
- 终端：总线两端各 `120Ω`
- 节点：
  - Host：广播 / 控制中心
  - Node A：`0x11`
  - Node B：`0x12`
  - Node C：`0x13`

## 2. ID 规则

### Host -> Node
| CAN ID | Meaning |
|---|---|
| `0x100 + nodeId` | `SET_RPM` |
| `0x110 + nodeId` | `SET_PARAM` |
| `0x120 + nodeId` | `CLEAR_FAULT` |
| `0x12F` | `ESTOP_BROADCAST` |

### Node -> Host
| CAN ID | Meaning |
|---|---|
| `0x180 + nodeId` | `STATUS` |
| `0x190 + nodeId` | `HEARTBEAT` |
| `0x1A0 + nodeId` | `FAULT` |

## 3. Payload 定义

### 3.1 SET_RPM
**CAN ID**: `0x100 + nodeId`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0 | `seq` | `u8` | 帧序号 |
| 1-2 | `targetRpm` | `i16` | 目标转速 |
| 3-4 | `rampMs` | `u16` | 斜坡时间 |
| 5 | `enable` | `u8` | 0/1 |
| 6 | `reserved` | `u8` | 保留 |
| 7 | `reserved` | `u8` | 保留 |

### 3.2 SET_PARAM
**CAN ID**: `0x110 + nodeId`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0 | `paramId` | `u8` | 参数编号 |
| 1-4 | `value` | `i32` | 定点值 / 原始值 |
| 5-7 | `reserved` | `u8[3]` | 保留 |

#### Param IDs
- `1` = `kp_x1000`
- `2` = `ki_x1000`
- `3` = `kd_x1000`
- `4` = `rpmLimit`
- `5` = `currentLimit_x10`
- `6` = `accelLimit`

### 3.3 CLEAR_FAULT
**CAN ID**: `0x120 + nodeId`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0 | `magic` | `u8` | 固定 `0xA5` |
| 1-7 | `reserved` | `u8[7]` | 保留 |

### 3.4 ESTOP_BROADCAST
**CAN ID**: `0x12F`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0 | `code` | `u8` | 急停原因 |
| 1 | `source` | `u8` | 0=Host, 1=HW, 2=Safety |
| 2-7 | `reserved` | `u8[6]` | 保留 |

### 3.5 STATUS
**CAN ID**: `0x180 + nodeId`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0-1 | `actualRpm` | `i16` | 当前转速 |
| 2-3 | `targetRpm` | `i16` | 当前目标 |
| 4-5 | `busVoltage_x10` | `u16` | 例如 245 = 24.5V |
| 6-7 | `phaseCurrent_x10` | `u16` | 例如 123 = 12.3A |

### 3.6 HEARTBEAT
**CAN ID**: `0x190 + nodeId`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0 | `state` | `u8` | 运行状态 |
| 1 | `faultCode` | `u8` | 当前故障 |
| 2-3 | `temp_x10` | `i16` | 例如 356 = 35.6°C |
| 4 | `aliveCounter` | `u8` | 递增计数 |
| 5-7 | `reserved` | `u8[3]` | 保留 |

### 3.7 FAULT
**CAN ID**: `0x1A0 + nodeId`

| Byte | Field | Type | Notes |
|---|---|---|---|
| 0 | `faultCode` | `u8` | 故障码 |
| 1 | `state` | `u8` | 故障发生时状态 |
| 2-3 | `actualRpm` | `i16` | 故障时转速 |
| 4-5 | `phaseCurrent_x10` | `u16` | 故障时相电流 |
| 6-7 | `busVoltage_x10` | `u16` | 故障时母线电压 |

## 4. 状态码
- `0` = `IDLE`
- `1` = `SPINUP`
- `2` = `RUNNING`
- `3` = `READY`
- `4` = `FAULT`
- `5` = `ESTOP`

## 5. 故障码
- `0` = none
- `1` = overcurrent
- `2` = overvoltage
- `3` = undervoltage
- `4` = overtemp
- `5` = hall_error
- `6` = stall
- `7` = comms_timeout
- `8` = no_ball_at_chamber
- `9` = ball_jam

## 6. 周期建议
- Host `SET_RPM`: `20ms`
- Node `STATUS`: `20ms`
- Node `HEARTBEAT`: `100ms`
- `COMMS_TIMEOUT`: `200ms`

## 7. P0 约束
- Host 丢失 Node `STATUS/HEARTBEAT` 超时 -> 全局 `FAULT`
- Node 连续丢失 Host `SET_RPM` -> 本地降速并停机
- `ESTOP_BROADCAST` 收到后立即关 `DRV_EN`
