# Host + 3 Node 联调示例代码 v1

## 文件
- `firmware/integration-demo/host_node_demo.cpp`

## 作用
提供一个最小联调示例，演示：
1. Host 设定 `baseRpm / deltaRpm / spinMode`
2. Host 通过 120° mixer 计算 `wheel1/2/3 targetRpm`
3. Host 向三节点下发 `SET_RPM`
4. 三节点回到自己的 `actualRpm`
5. Host 打印三轮目标/实际转速

## 当前演示流程
- Tick 0~3：`STRAIGHT`
- Tick 4~7：`TOPSPIN`
- Tick 8~11：`LEFT_CURVE`

## 当前定位
- 这是平台无关的最小联调示例
- 便于验证 rpm mixer 和三节点映射是否正确
- 后续可替换为真实 Host / B-G431B-ESC1 工程中的集成测试入口
