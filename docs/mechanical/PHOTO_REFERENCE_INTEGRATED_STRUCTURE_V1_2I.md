# Photo Reference Integrated Structure V1.2I

## 指令来源
用户补发参考图，当前继续暂停仿真更新，只改机械：

**发射圆管兼三电机固定一体结构，必须贴近图片。**

---

## 图片结构要点提取
从参考图抽象出的关键结构：

1. **中心圆管开口明显**
   - 圆管不是独立件，而是橙色一体结构的中心孔。
   - 电机座围绕圆管外壁生长。

2. **三电机不是外挂板固定**
   - 电机嵌在橙色打印件的口袋 / 卡座里。
   - 每个电机有侧向包络、底托、端部压板。

3. **侧板有圆形减重 / 工具孔**
   - 图中橙色侧板上有明显圆孔。
   - 这些孔不能理解成保护罩孔，而是减重、工具进入、观察/线束避让的一体结构孔。

4. **顶部桥接压条 / 螺丝排**
   - 图片中前侧电机上方有一条橙色桥接压条，并带黑色螺丝。
   - 该结构用于压住电机或固定端盖。

5. **底部托架 / 电机托台**
   - 电机下方有橙色托底，不是悬空安装。
   - 托架与圆管、侧板、加强筋连续成型。

6. **线束从口袋边缘引出**
   - 线束不能被一体座压死。
   - 必须预留后侧或下侧线槽。

---

## CAD 新增
新增文件：

- `cad/assembly/p0-single-ball-launcher-v3/outrunner_photo_integrated_mount_v1_2i.scad`

基于 v1.2h 继续机械细化，不更新仿真。

### 新增参数

```scad
show_photo_side_plates = true;
show_bridge_straps = true;
show_round_relief_holes = true;
show_lower_motor_shelf = true;
photo_side_plate_t = 8;
photo_side_plate_w = 78;
photo_side_plate_h = 108;
round_relief_d = 24;
round_relief_pitch = 42;
bridge_strap_w = 22;
bridge_strap_t = 9;
bridge_strap_len = 96;
strap_screw_d = 4.2;
lower_motor_shelf_t = 8;
lower_motor_shelf_w = 96;
lower_motor_shelf_d = 36;
```

---

## 本版新增结构

### 1. Photo-like cheek plate
新增每个电机口袋外侧的橙色侧板：

- 厚度 `8mm`
- 高度 `108mm`
- 宽度 `78mm`
- 与电机口袋和圆管一体

### 2. Round relief / tool holes
侧板加入双圆孔：

- 孔径 `24mm`
- 孔距 `42mm`

用途：
- 减重
- 工具进入
- 观察转子/间隙
- 线束避让预留

### 3. Bridge strap
每个电机上方新增桥接压条：

- 长度 `96mm`
- 宽度 `22mm`
- 厚度 `9mm`
- 三颗 `4.2mm` 螺丝孔占位

贴近图片中电机上方黑色螺丝压条。

### 4. Lower motor shelf
每个电机下方新增托台：

- 宽度 `96mm`
- 深度 `36mm`
- 厚度 `8mm`

用于表达图片中的电机底托，避免电机悬空。

---

## 当前工程判断
v1.2i 比 v1.2h 更贴近图片，但仍是结构占位版，下一步需要继续：

1. 把侧板圆孔与真实工具路径对齐
2. 桥接压条改成可拆压盖，而不是完全一体
3. 端部螺丝孔对齐真实 6354 端盖孔距
4. 线束出口按照片中的下侧/后侧路径固定
5. 输出三视图 SVG，给设计师按图继续修正

---

## 结论
当前机械主线：

**圆管开口 + 三电机口袋 + 侧板圆孔 + 顶部压条 + 底部托架 + 线束槽，全部并入同一个橙色一体固定结构。**
