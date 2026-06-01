# 调试手册 v1

> 目标：让 `ESP32-S3 Host + B-G431B-ESC1 ×3` 的单球三轮发射器在 P0 阶段更容易定位问题。

## 1. 先看什么
### 第一优先
1. Host 是否启动
2. 3 个 Node 是否都在线
3. nodeId 是否和物理轮位一致
4. `SET_RPM` 是否发出
5. `STATUS / HEARTBEAT` 是否回传

### 第二优先
1. wheel1/2/3 的 `targetRpm`
2. wheel1/2/3 的 `actualRpm`
3. `faultCode`
4. `busVoltage`
5. `phaseCurrent`
6. `temp`

## 2. 轮位映射检查
固定映射：
- wheel1 -> 12:00 -> `NODE_ID_WHEEL_A (0x11)`
- wheel2 -> 4:00  -> `NODE_ID_WHEEL_B (0x12)`
- wheel3 -> 8:00  -> `NODE_ID_WHEEL_C (0x13)`

### 检查方法
1. 只给 `wheel1` 一个低速目标 rpm
2. 看转的是不是 12 点钟那一路
3. 再分别测 wheel2 / wheel3

如果转错：
- 先检查板子烧录的 nodeId
- 再检查 Host 物理接线记录
- 不先改 mixer 公式

## 3. 最小 bring-up 顺序
### Step 1
Host 上电：
- 看 boot log
- 看 CAN init

### Step 2
单个 Node 上电：
- 看 `STATUS`
- 看 `HEARTBEAT`
- 看 `faultCode == 0`

### Step 3
三节点同时在线：
- A/B/C 都能回包
- nodeId 不冲突

### Step 4
单轮低速目标：
- `500 rpm`
- 再 `1000 rpm`
- 再 `2000 rpm`

### Step 5
三轮同 rpm：
- 先 `STRAIGHT`
- 再 `TOPSPIN`
- 再 `LEFT_CURVE`

## 4. 常见故障定位
### A. Host 发了，Node 不动
先查：
1. CAN 收发
2. nodeId 是否匹配
3. Node 是否进入 `ESTOP/FAULT`
4. `enabled` 是否被拉低

### B. targetRpm 正常，actualRpm 不上来
先查：
1. 电机相线 / Hall 线
2. Node 当前限流
3. 驱动故障脚
4. 轮组是否机械卡滞

### C. 三轮转了但球偏航严重
先查：
1. 轮位映射是否搞错
2. 三轮预压是否一致
3. 轮面材料是否一致
4. 实际 rpm 偏差是否过大

### D. 一启动就 fault
先查：
1. 电源压降
2. 总保险 / 支路保险
3. 驱动过流 / 过温
4. 急停链路是否误触发

## 5. 推荐日志字段
### Host
- `state`
- `spinMode`
- `ballLoaded`
- `wheel1 actual/target`
- `wheel2 actual/target`
- `wheel3 actual/target`
- `hostFault`

### Node
- `nodeId`
- `state`
- `enabled`
- `targetRpm`
- `actualRpm`
- `busVoltage`
- `phaseCurrent`
- `temp`
- `faultCode`

## 6. 调试原则
1. 一次只改一个变量
2. 先单轮，再三轮
3. 先低 rpm，再高 rpm
4. 先直射，再旋转
5. 先看日志，再改参数
