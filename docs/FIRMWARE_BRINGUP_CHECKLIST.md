# 固件 Bring-up Checklist v1

## Host
- [ ] 可下载
- [ ] 串口日志正常
- [ ] CAN 初始化正常
- [ ] 传感器输入可读
- [ ] 急停输入可读

## Single Motor Node
- [ ] 可下载
- [ ] 3.3V/VBUS 采样正常
- [ ] Driver fault 可读
- [ ] Hall 读数正常
- [ ] PWM 输出正常
- [ ] 单电机低速开环正常
- [ ] 单电机速度闭环正常

## Host + Single Node
- [ ] `SET_RPM` 生效
- [ ] `STATUS` 回传正常
- [ ] `HEARTBEAT` 正常
- [ ] 通信超时保护正常

## 3 Nodes
- [ ] 三节点可同时在线
- [ ] 三轮同步启动正常
- [ ] 轮间偏差在目标范围内

## Feed / Launch
- [ ] 管道有球检测正常
- [ ] 发射位到球检测正常
- [ ] 出球检测正常
- [ ] 单球分离逻辑正常
- [ ] 状态机完整跑通
