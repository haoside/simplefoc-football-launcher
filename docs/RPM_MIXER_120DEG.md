# 120° 三轮 RPM 分配说明 v1

> 目标：给上位控制板一个简单、可调的三轮目标 RPM 生成方式，用于 P0 的直射 / 上旋 / 下旋 / 侧旋验证。

## 1. 三轮定义
- `Wheel A`：0°
- `Wheel B`：120°
- `Wheel C`：240°

## 2. 输入参数
- `baseRpm`：基础发射转速
- `spinX`：左右侧旋分量
- `spinY`：上下旋分量

## 3. 一阶混合模型
可先用线性模型：

```text
rpmA = baseRpm + spinX
rpmB = baseRpm - 0.5 * spinX + 0.866 * spinY
rpmC = baseRpm - 0.5 * spinX - 0.866 * spinY
```

其中：
- `0.866 ≈ sin(60°)`
- 该模型适合 P0 的方向性验证，不代表最终物理最优解

## 4. 模式建议
### 直射
```text
spinX = 0
spinY = 0
```

### 上 / 下旋
```text
spinX = 0
spinY = +/- delta
```

### 侧旋
```text
spinY = 0
spinX = +/- delta
```

## 5. 限制
- 每个 `rpmX` 需要做上下限裁剪
- 任一路超出驱动能力时，整体按比例缩放
- 进入 `READY` 前，三轮都需达到目标转速阈值

## 6. P0 目标
- 先验证“旋转方向可区分”
- 不追求高精度落点
- 不追求复杂轨迹控制
