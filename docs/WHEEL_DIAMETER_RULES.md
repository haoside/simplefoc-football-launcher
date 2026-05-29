# WHEEL_DIAMETER_RULES.md

## 1. 输入约束
- 标准 5 号足球直径约：`220 mm`
- 轮径与球径联动设计，不先写死单一固定值

## 2. 设计变量
- `wheelDiameter`
- `compression / preload`
- `contactPatch`
- `wheelSpacing`

## 3. P0 规则
- P0 先保留 `90–130 mm` 试验区间
- 轮间距与压紧量可调
- 首要目标：
  - 不明显打滑
  - 不过度挤压球体
  - 可稳定形成接触补丁

## 4. 设计方法
建议按这条链路收敛：
`ballDiameter -> wheelDiameterRange -> preload -> contactPatch -> shot stability`

## 5. 当前原则
- 先保证稳定出球
- 再优化球速、旋转、轮面材料
- P0 不追单点最优轮径，先做可调范围验证
