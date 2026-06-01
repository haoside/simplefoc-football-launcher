# Host 单轮点动调试命令 v1

## 新增能力
在 Host 调试命令里增加单独 wheel 点动/覆盖目标 rpm：
- `jog wheel1 800`
- `jog wheel2 800`
- `jog wheel3 800`
- `jog off`

## 用途
1. 校验 wheel1/2/3 与物理轮位映射
2. 单独检查某一路 node 是否正常响应
3. 不经过 spinMode/mixer，直接给单轮目标 rpm
4. bring-up 时更快定位 wiring / nodeId / node fault

## 当前实现
- `host_state` 新增 `debugOverride`
- `debug_command.cpp` 新增 `jog wheel1/2/3` 与 `jog off`
- `can_host_loop.cpp` 在 debugOverride 打开时直接使用单轮目标 rpm
