# 操作员速查卡 v1

## 开机前
- 检查急停
- 检查电池电量
- 检查 3 个 Node 在线
- 检查 wheel1/2/3 映射
- 检查防护罩与导向筒安装

## 单轮映射检查
```text
jog wheel1 800
jog off
jog wheel2 800
jog off
jog wheel3 800
jog off
```

## 直传基线
```text
env e0
preset straight_pass
fire
```

## 常规训练左弧线
```text
env e1
preset standard_left_curve
fire
```

## 常规训练右弧线
```text
env e1
preset standard_right_curve
fire
```

## 左侧风修正
```text
env e1_leftwind
preset standard_left_curve_wind_left
fire
```

## 右侧风修正
```text
env e1_rightwind
preset standard_right_curve_wind_right
fire
```

## 低温/不利环境检查
```text
env e2
preset straight_pass
fire
```

## 故障处理
```text
estop
clear fault
```

## 记录最少要写
- 当前 env
- 当前 preset
- 球速
- 横向偏移
- 落点误差
- 是否打滑
- 是否削弱旋转

## 当前主验证顺序
1. `env e0 + preset straight_pass`
2. `env e0 + preset standard_left_curve`
3. `env e1 + preset standard_left_curve`
4. `env e1_leftwind + preset standard_left_curve_wind_left`
5. `env e1_rightwind + preset standard_right_curve_wind_right`
6. `env e2_leftwind + preset standard_left_curve_wind_left`
