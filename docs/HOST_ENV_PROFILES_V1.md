# Host 环境 profile v1

## 新增 profile
- `e0` -> 20°C / 50% / 0m/s / none
- `e1` -> 16°C / 60% / 2m/s / none
- `e1_leftwind` -> 16°C / 60% / 2m/s / left
- `e1_rightwind` -> 16°C / 60% / 2m/s / right
- `e2` -> 6°C / 45% / 4m/s / none
- `e2_leftwind` -> 6°C / 45% / 4m/s / left

## 用途
用于把环境口径统一成 Host 侧可识别 profile，便于现场记录和后续扩展：
- 先选环境 profile
- 再选 shot preset
- 再做发射测试

## 当前定位
当前先提供 profile 数据结构与查询接口。
下一步可继续接：
- `env e0`
- `env e1`
- `env e2`
这类调试命令
