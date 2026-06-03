# CAD 导出规范 v1

## 目标
把当前 OpenSCAD / flat draft 文件收成可导出、可交付加工的统一口径。

## 1. 3D 打印件导出
### 文件
- `cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad`

### 导出格式
- `STL`：用于 3D 打印
- `3MF`：可选，保留更多打印参数

### 导出建议
- 文件命名：
  - `short_guide_tube_v1.stl`
- 打印材料：
  - `PETG` 优先
  - `Nylon` 次优先
- 若打印机尺寸不足：
  - 拆成左右半壳
  - 用法兰螺丝拼接

## 2. 钣金 / 平板件导出
### 文件
- `cad/sheet-metal/motor-mount-plate-v1/motor_mount_plate_v1.scad`
- `cad/sheet-metal/guard-bracket-v1/guard_bracket_v1.scad`
- `cad/sheet-metal/control-bay-plate-v1/control_bay_plate_v1.scad`
- `cad/sheet-metal/power-bay-plate-v1/power_bay_plate_v1.scad`
- `cad/sheet-metal/battery-clamp-v1/battery_clamp_v1.scad`
- `cad/sheet-metal/estop-panel-v1/estop_panel_v1.scad`

### 导出格式
- `DXF`：平面切割优先
- `STEP`：若后续转正式 CAD 建模
- `PDF`：给加工厂看尺寸标注

### 命名建议
- `motor_mount_plate_v1.dxf`
- `guard_bracket_v1.dxf`
- `control_bay_plate_v1.dxf`
- `power_bay_plate_v1.dxf`
- `battery_clamp_v1.dxf`
- `estop_panel_v1.dxf`

## 3. 当前边界
- 当前 SCAD 是 P0 可制造 draft，不是最终量产出图
- 与真实采购件相关孔位，导出前必须二次复核
