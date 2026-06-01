# B-G431B-ESC1 三节点实例化配置 v1

## 固定映射
- `wheel1` -> `NODE_ID_WHEEL_A (0x11)` -> `12:00`
- `wheel2` -> `NODE_ID_WHEEL_B (0x12)` -> `4:00`
- `wheel3` -> `NODE_ID_WHEEL_C (0x13)` -> `8:00`

## 已生成文件
- `firmware/node-bg431b-esc1/include/node_profile.h`
- `firmware/node-bg431b-esc1/src/node_profile.cpp`
- `firmware/node-bg431b-esc1/config/wheel1_config.h`
- `firmware/node-bg431b-esc1/config/wheel2_config.h`
- `firmware/node-bg431b-esc1/config/wheel3_config.h`

## 用法
- 每块 B-G431B-ESC1 烧录时选择对应 `NODE_DEFAULT_ID`
- 或在构建时替换为对应 wheel 配置
- Host 侧按固定 wheel1/2/3 方位做 rpm mixer

## 调试建议
- 三块板先分别烧录并验证 `STATUS / HEARTBEAT`
- 再接入 Host 联调
- 记录 wheel1/2/3 与物理位置是否一致，避免方向接反
