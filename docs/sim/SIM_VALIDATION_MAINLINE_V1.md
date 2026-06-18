# SIM_VALIDATION_MAINLINE_V1

## 定位
从现在开始，`v1.2` 阶段以 **仿真验证** 作为主线推进，机械验证与结构修正围绕仿真结论服务。

当前口径不是继续发散几何，而是先把下面这条链条跑顺：

```text
几何冻结参数 -> 仿真输入 -> RPM / preload / friction 窗口 -> 实测回填 -> 再修结构
```

---

## 主线目标
在当前 6354 / 三工位 / 232 内径 / 可调压紧的冻结约束下，优先回答 4 个问题：

1. 当前方案的 **安全起转窗口** 是多少
2. 哪组 `RPM / preload / friction` 组合适合作为首轮实测
3. 哪些参数对出球速度 / 弧线 / 射程最敏感
4. 哪些机械变量必须回填到仿真里，否则继续做结构会失真

---

## 当前仿真基础
当前仓库已具备：
- `sim/football_launch_model.py`
- `sim/optimization_sweep_v1.py`
- `sim/params_p0.yaml`
- `sim/results_p0.md`
- `docs/sim/P0_SIM_RECOMMENDATIONS_V2.md`

当前模型可用于筛选：
- wheel RPM 组合
- preload 对耦合效率的影响
- friction 对出球速度的影响
- spin bias 对弧线的影响
- ramp 时间对电流风险的粗筛

---

## 这轮主线结论

### 1. 仿真验证应先于进一步结构发散
原因很直接：
- 当前机械主线已经冻结到 `v1.1 / v1.2`
- 但 `preload`、`rubber`、`friction`、`actual exit speed` 还没有闭环
- 如果继续画结构而不先把这些变量收口，后面很容易出现“结构按错目标优化”

所以当前主线应改成：
**先用仿真把实测窗口和参数敏感度锁出来，再决定结构只改哪些点。**

### 2. 当前模型里，摩擦系数和预压量是第一批主敏感参数
基于 `sim/football_launch_model.py` 的批量筛选结果：

#### straight_validation
- 发射速度范围：`9.83 ~ 14.10 m/s`
- 射程范围：`4.6 ~ 8.0 m`

#### light_curve_validation
- 发射速度范围：`9.83 ~ 14.10 m/s`
- 射程范围：`5.0 ~ 9.0 m`
- 横向偏移范围：`0.17 ~ 0.38 m`

#### standard_curve_validation
- 发射速度范围：`10.42 ~ 14.94 m/s`
- 射程范围：`6.0 ~ 10.9 m`
- 横向偏移范围：`0.25 ~ 0.60 m`

这说明在当前模型里：
- `friction_coeff`
- `preload_mm`
- `spin_bias_rpm`

会直接决定首轮实测是否落在可控窗口。

### 3. 仿真先行时，首轮实测不该一上来追大弧线
建议先按这条顺序：
1. `straight_validation`
2. `light_curve_validation`
3. `standard_curve_validation`

也就是：
- 先验证直球速度是否能闭环
- 再验证轻弧线是否稳定
- 最后再上标准弧线

这比先冲高 preload / 高 spin bias 更稳。

---

## 当前推荐的仿真主线测试窗口

### A. 首轮安全窗口
作为第一轮实测起点，优先用：
- `RPM_CAP = 3000`
- `ramp = 5s`
- `preload = 8 ~ 10 mm`
- `friction_coeff` 按 `0.55 ~ 0.65` 作为初始估计

目的：
- 先证明系统可重复发球
- 先拿到 exit speed / current / wheel slip 的一批数据
- 避免过早被高压紧、高摩擦带偏

### B. 弧线测试窗口
当直球闭环后，再进：
- `spin_bias_rpm = 250` 做轻弧线
- `spin_bias_rpm = 450` 做标准弧线
- `ramp = 6s` 用于更保守的高差速验证

### C. 当前不建议直接当默认值的组合
不建议一开始默认：
- 高 preload
- 高包胶厚度
- 高 spin bias

原因：
这些组合会把机械不确定性、动平衡风险和电流风险叠在一起，失去排障顺序。

---

## 与机械验证的接口关系
仿真主线不替代机械验证，但会重新排序：

### 机械验证继续保留
仍然要做：
- 6354 实测外径 / 长度 / 端面孔距
- 包胶厚度与压紧量联动
- 包胶后动平衡
- 防护罩散热 / 装配 / 维护空间
- 工具进入空间

### 但推进顺序改成
1. **先把仿真输入边界锁出来**
2. **再让机械验证去填这些输入**
3. **最后只修正真正影响仿真结果的结构变量**

换句话说：
机械验证不再平均推进，而是优先服务仿真回填。

---

## 当前新增输出
这轮新增：
- `docs/sim/SIM_VALIDATION_MAINLINE_V1.md`
- `docs/sim/SIM_SENSITIVITY_MATRIX_V1.csv`

其中 `SIM_SENSITIVITY_MATRIX_V1.csv` 用于记录：
- `friction_coeff`
- `preload_mm`
- `launch_mps`
- `range_m`
- `lateral_m`
- `current_risk`

便于后面把实测数据一项项回填对比。

---

## 下一步
接下来主线继续补两块：

1. **仿真实测回填模板**
   - 把 radar / slow-motion / current log / wheel rpm 实测值接到 sim 输出上

2. **仿真参数冻结表**
   - 明确哪些参数现在允许调，哪些参数必须冻结，不让现场测试时乱漂

---

## 结论
当前阶段，主线正式切到：

**仿真验证优先，机械验证围绕仿真输入与实测回填服务。**

后续结构修正只处理两类问题：
1. 影响仿真输入边界的
2. 被实测证明会导致仿真失真的
