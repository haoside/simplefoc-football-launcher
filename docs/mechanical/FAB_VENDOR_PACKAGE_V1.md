# 加工厂交付包清单 v1

## 目标
给 3D 打印厂 / 钣金加工厂一套可直接接收的文件包口径，避免现场口头沟通遗漏。

## 1. 3D 打印件交付包
### 件
- `short_guide_tube_v1`

### 应提供文件
- 源文件：`cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad`
- 导出文件：`short_guide_tube_v1.stl`
- 说明文件：`cad/3d-print/short-guide-tube-v1/README.md`
- 图纸说明：`docs/mechanical/SHORT_GUIDE_TUBE_DRAWING_V1.md`

### 口径
- 材料：PETG / 尼龙优先
- 颜色：任意，优先浅色便于观察磨损
- 内壁尽量光滑
- 若打印体积不够，允许拆半壳打印后螺栓拼接

## 2. 钣金 / 平板件交付包
### 件
- motor_mount_plate_v1
- guard_bracket_v1
- control_bay_plate_v1
- power_bay_plate_v1
- battery_clamp_v1
- estop_panel_v1

### 每件应提供文件
- 源文件：对应 `.scad`
- 导出文件：对应 `.dxf`
- 说明文件：对应 `README.md`
- 图纸说明（如有）：对应机械文档

## 3. 推荐交付目录结构
```text
fab-package-v1/
  3d-print/
    short_guide_tube_v1/
      short_guide_tube_v1.stl
      README.md
  sheet-metal/
    motor_mount_plate_v1/
      motor_mount_plate_v1.dxf
      README.md
    guard_bracket_v1/
      guard_bracket_v1.dxf
      README.md
    control_bay_plate_v1/
      control_bay_plate_v1.dxf
      README.md
    power_bay_plate_v1/
      power_bay_plate_v1.dxf
      README.md
    battery_clamp_v1/
      battery_clamp_v1.dxf
      README.md
    estop_panel_v1/
      estop_panel_v1.dxf
      README.md
  docs/
    MANUFACTURING_FILESET_V1.md
    CAD_EXPORT_GUIDE_V1.md
    PRE_FAB_CHECKLIST_V1.md
```

## 4. 给加工厂的备注
- 当前是 P0 原型件，不是量产件
- 孔位与实物采购件仍可能有小修正
- 优先保证：
  1. 尺寸一致
  2. 平面度
  3. 孔位准确
  4. 边缘去毛刺

## 5. 当前缺口
- 仓库内当前已具备源文件与说明文件
- `STL / DXF` 作为导出件还需在具备 OpenSCAD / CAD 导出环境时生成并放入交付包
