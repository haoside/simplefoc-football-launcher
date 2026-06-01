# Host preset 调试命令 v1

## 新增命令
- `preset straight_pass`
- `preset light_left_curve`
- `preset light_right_curve`
- `preset standard_left_curve`
- `preset standard_right_curve`
- `preset curve_drop_left`
- `preset curve_drop_right`

## 作用
直接把实战型弧线助攻球参数草案写进 Host 调试命令，现场不用每次手动改：
- `baseRpm`
- `deltaRpm`
- `spinMode`

## 当前实现
- `debug_command.cpp` 新增 `preset <name>`
- 依赖：
  - `shot_presets.h`
  - `shot_presets.cpp`

## 推荐用法
1. `preset straight_pass`
2. `preset standard_left_curve`
3. `preset standard_right_curve`
4. `fire`

## 与 jog 的关系
- `preset` 用于正常训练球模式
- `jog wheel1/2/3` 用于单轮排障
- 一旦使用 `preset`，会自动退出 wheel jog override
