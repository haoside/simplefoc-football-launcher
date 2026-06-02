# Host 环境 + preset 命令矩阵 v1

## 目标
把现场最常用的环境 profile 与 shot preset 组合成可直接执行的命令序列，减少现场切换成本。

## 推荐基线组合
### 1. 实验室直传基线
```text
env e0
preset straight_pass
fire
```
用途：直传基线 / 轮组一致性 / 导向筒 A/B 初始对比

### 2. 实验室标准左弧线
```text
env e0
preset standard_left_curve
fire
```
用途：无风下标准弧线基线

### 3. 常规训练直传
```text
env e1
preset straight_pass
fire
```
用途：常规训练环境直传

### 4. 常规训练标准左弧线
```text
env e1
preset standard_left_curve
fire
```
用途：常规训练环境左弧线

### 5. 常规训练标准右弧线
```text
env e1
preset standard_right_curve
fire
```
用途：常规训练环境右弧线

## 有风修正组合
### 6. 左侧风下标准左弧线
```text
env e1_leftwind
preset standard_left_curve_wind_left
fire
```
用途：左侧风放大左弧时的修正组合

### 7. 右侧风下标准左弧线
```text
env e1_rightwind
preset standard_left_curve_wind_right
fire
```
用途：右侧风削弱左弧时的修正组合

### 8. 左侧风下标准右弧线
```text
env e1_leftwind
preset standard_right_curve_wind_left
fire
```
用途：左侧风削弱右弧时的修正组合

### 9. 右侧风下标准右弧线
```text
env e1_rightwind
preset standard_right_curve_wind_right
fire
```
用途：右侧风放大右弧时的修正组合

## 不利环境组合
### 10. 低温/逆风前的直传检查
```text
env e2
preset straight_pass
fire
```
用途：不利环境下基线稳定性检查

### 11. 低温左侧风下标准左弧线
```text
env e2_leftwind
preset standard_left_curve_wind_left
fire
```
用途：不利环境主验证组合

## 现场建议顺序
1. `env e0 + preset straight_pass`
2. `env e0 + preset standard_left_curve`
3. `env e1 + preset standard_left_curve`
4. `env e1_leftwind + preset standard_left_curve_wind_left`
5. `env e1_rightwind + preset standard_left_curve_wind_right`
6. `env e2_leftwind + preset standard_left_curve_wind_left`

## 建议
- 先切 `env`
- 再切 `preset`
- 最后 `fire`
- 每次换环境或导向筒，都重新记录 wheel1/2/3 target/actual
