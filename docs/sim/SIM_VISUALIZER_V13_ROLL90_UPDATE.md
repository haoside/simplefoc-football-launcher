# SIM_VISUALIZER_V13_ROLL90_UPDATE

## Owner 修正
本轮口径变更：

- 三电机倾斜布置整体 **翻转 / roll 90°**
- 继续保持无保护罩
- 继续保持三电机嵌入短发射管
- 继续按三电机共同作用合力方向直接向上发射

---

## Widget 更新
Widget：`仿真验证交互可视化`

版本：v13

文件：
- `widgets/sim-visualizer.html`

---

## 主要改动

### 1. 3D 三电机组 roll 90°
3D 中短发射管 + 三电机组整体翻转 90°：

```js
launcherGroup.rotation.x = Math.PI / 2
```

再叠加倾斜发射角：

```js
launcherGroup.rotation.z = tiltRad * 0.75
```

用于表达：

**三电机倾斜布置翻转 90° 后，直接形成向上发射合力。**

### 2. 电机方位同步重排
A/B/C 分力箭头的站位 clocking 调整为 roll 90° 后的口径：

```js
motorAngles = [0, -120°, +120°]
```

### 3. 文案同步 v1.2d
Widget 顶部、提示、合力图标注均更新为：

- v1.2d
- 翻转 90°
- 三电机倾斜嵌入
- 直接向上发射

---

## CAD v1.2d
新增：

- `cad/assembly/p0-single-ball-launcher-v3/outrunner_embedded_tilted_roll90_tube_v1_2d.scad`

相对 v1.2c：

- 新增 `station_roll_deg = 90`
- 装配输出执行 `roll 90° + launch_tilt_deg`
- 保留无保护罩
- 保留三电机嵌入短发射管
- 发射方向按 roll 后的三电机合力方向

---

## 当前结论
v13 主线口径：

**三电机倾斜嵌入短发射管 → 整体翻转 90° → 合力方向直接向上发射 → A/B/C 差速叠加实战弧线。**

下一步继续：

1. 加 roll 90° 后的 A/B/C 方位说明图
2. 加倾角 / roll / RPM 推荐表
3. 加落点云和不可控区间热区
4. 加 A/B/C 独立压紧校准输入
