# 三电机弧线球与稳定轨迹控制说明 v1

## 固定几何
- `wheel1 @ 12:00`
- `wheel2 @ 4:00`
- `wheel3 @ 8:00`
- 三轮围绕球心 120° 均布

## 基本原理
### 1. 直射
三轮同速：
- `wheel1 = base`
- `wheel2 = base`
- `wheel3 = base`

作用：
- 球主要获得前向速度
- 自旋最小
- 轨迹最接近直线

### 2. 上旋 / 下旋
通过上轮与下两轮形成速度差：
- `TOPSPIN`：wheel1 更快，wheel2/3 略慢
- `BACKSPIN`：wheel1 略慢，wheel2/3 更快

作用：
- 改变球的自旋方向
- 依赖 Magnus 效应改变飞行弧度

### 3. 左右弧线
通过 wheel2 / wheel3 左右不对称：
- `LEFT_CURVE`：wheel3 更快，wheel2 更慢
- `RIGHT_CURVE`：wheel2 更快，wheel3 更慢

作用：
- 让球产生侧向自旋
- 形成左/右弧线轨迹

## 为什么能稳定
稳定弧线不是只靠“转速差”，还要同时满足：
1. 三轮接触一致
2. 轮面材料一致
3. 三轮实际 rpm 跟目标差不要太大
4. 球进入三轮时姿态稳定
5. 预压一致，不让某一轮先打滑

## 控制策略建议
### P0
- 先固定 `baseRpm`
- 再逐级增加 `deltaRpm`
- 先测 `STRAIGHT`
- 再测 `TOPSPIN`
- 最后测 `LEFT_CURVE / RIGHT_CURVE`

### 稳定性要点
- `deltaRpm` 不要一步拉太大
- 三轮同步 ramp 启动
- 进入 `READY` 后再允许发射
- 如果某一轮 actualRpm 长期跟不上，先判为机械/摩擦问题，不盲目继续加 delta

## 当前实现落点
- Host 侧：`baseRpm + deltaRpm + spinMode`
- `rpm_mixer_120deg` / 当前 target 计算逻辑输出 wheel1/2/3 目标转速
- Node 侧：各自闭环跟踪目标 rpm
