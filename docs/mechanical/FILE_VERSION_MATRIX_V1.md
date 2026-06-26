# 文件版本管理表 v1

| 类别 | 文件 | 当前版本 | 备注 |
|---|---|---|---|
| 3D 打印 | short_guide_tube_v1.scad | v1 | 短导向筒 |
| 钣金 | motor_mount_plate_v1.scad | v1 | 电机安装板 |
| 钣金 | guard_bracket_v1.scad | v1 | 防护罩支架 |
| 钣金 | control_bay_plate_v1.scad | v1 | 控制仓安装板 |
| 钣金 | power_bay_plate_v1.scad | v1 | 电源仓安装板 |
| 钣金 | battery_clamp_v1.scad | v1 | 电池压板 |
| 钣金 | estop_panel_v1.scad | v1 | 急停面板 |
| 文档 | MANUFACTURING_FILESET_V1.md | v1 | 制造文件索引 |
| 文档 | CAD_EXPORT_GUIDE_V1.md | v1 | 导出规范 |
| 文档 | PRE_FAB_CHECKLIST_V1.md | v1 | 加工前复核 |
| 装配 CAD | outrunner_launch_tube_v1.scad | v1 | 端面固定发射筒，筒身开口，外转子直驱接触 |
| 文档 | OUTRUNNER_LAUNCH_TUBE_V1.md | v1 | 外转子直驱发射筒设计说明 |
| 渲染/三视图 | OUTRUNNER_LAUNCH_TUBE_THREE_VIEW_V1.svg | v1 | 发射筒三视图说明 |
| 装配 CAD | outrunner_launch_tube_v1_1.scad | v1.1 | 6354 外转子发射筒，2–3mm 可调压紧，防护罩孔位/加强肋补强 |
| 文档 | OUTRUNNER_LAUNCH_TUBE_V1_1.md | v1.1 | 外转子直驱发射筒 v1.1 设计说明 |
| 渲染/三视图 | OUTRUNNER_LAUNCH_TUBE_THREE_VIEW_V1_1.svg | v1.1 | 发射筒三视图说明 v1.1 |
| 文档 | MAINLINE_MODEL_ADJUSTMENT_V2.md | v2 | 主线并线检查、参数同步与工程验证入口结论 |
| 文档 | ENGINEERING_VALIDATION_V1_2.md | v1.2 | 工程验证总表、方法、通过标准、风险等级与失败修改路径 |

## 版本规则
- 尺寸修改：升小版本（v1 -> v2）
- 孔位/结构逻辑修改：直接升主版本（v1 -> v2）
- 采购件确认后再进入“rev-A”口径
| 文档 | MEASUREMENT_SHEET_6354_V1.md | v1 | 6354 实测接口记录表，用于锁外径/长度/端面孔距 |
| 文档 | PRELOAD_COUPLING_MATRIX_V1.md | v1 | 包胶厚度与压紧量联动矩阵，一阶风险筛选 |
| 文档 | SIM_VALIDATION_MAINLINE_V1.md | v1 | 仿真验证主线说明，明确当前推进口径转向仿真优先 |
| 数据 | SIM_SENSITIVITY_MATRIX_V1.csv | v1 | 仿真敏感度矩阵，记录 friction/preload 对输出的影响 |
| 装配 CAD | outrunner_embedded_launch_tube_v1_2.scad | v1.2 | 嵌入式 3 外转子发射圆管，45×45 单端安装，圆管出口为发射基准 |
| 文档 | OUTRUNNER_EMBEDDED_LAUNCH_TUBE_V1_2.md | v1.2 | 嵌入式发射圆管结构说明 |
| 文档 | ENGINEERING_SIMULATION_PLAN_V1_2.md | v1.2 | v1.2 几何干涉/运动包络/50m/RPM/180° 弧线仿真计划 |
| 渲染/三视图 | OUTRUNNER_EMBEDDED_LAUNCH_TUBE_V1_2.svg | v1.2 | 嵌入式发射圆管结构说明图 |
| 文档 | GEOMETRY_INTERFERENCE_REVIEW_V1_2.md | v1.2 | v1.2 主线并线几何干涉快速复核 |
| 装配 CAD | outrunner_embedded_short_tube_v1_2a.scad | v1.2a | 76mm 短圆管/短环，三外转子嵌入夹持，+Z 出口轴线为发射方向 |
| 文档 | OUTRUNNER_EMBEDDED_SHORT_TUBE_V1_2A.md | v1.2a | v1.2a 短圆管嵌入版结构说明 |
| 文档 | SHORT_TUBE_V1_2A_ENGINEERING_REVIEW.md | v1.2a | v1.2a 并线工程复核，覆盖短管导向/口袋干涉/旋转包络/45×45/出口轴线 |
| 装配 CAD | outrunner_embedded_short_tube_v1_2b.scad | v1.2b | 去除保护罩表达，突出三电机嵌入短发射管，发射方向按三电机合力方向 |
| 文档 | SIM_VISUALIZER_V10_RESULTANT_UPDATE.md | v10 | 仿真可视化改为三电机合力方向出球，无保护罩口径 |
| 装配 CAD | outrunner_embedded_tilted_tube_v1_2c.scad | v1.2c | 三电机倾斜嵌入短发射管，合力方向直接向上发射，无保护罩 |
| 文档 | SIM_VISUALIZER_V12_TILTED_DIRECT_LAUNCH_UPDATE.md | v12 | 仿真可视化改为三电机倾斜布置直接向上发射 |
| 装配 CAD | outrunner_embedded_tilted_roll90_tube_v1_2d.scad | v1.2d | 三电机倾斜布置整体翻转 90°，合力方向直接向上发射，无保护罩 |
| 文档 | SIM_VISUALIZER_V13_ROLL90_UPDATE.md | v13 | 仿真可视化改为三电机倾斜布置 roll 90° |
| 装配 CAD | outrunner_photo_ref_embedded_tube_v1_2e.scad | v1.2e | 参照实物图：中心短发射管开口，三电机嵌入发射管周向窗口，倾斜 roll 90° 后合力发射 |
| 文档 | SIM_VISUALIZER_V14_PHOTO_REFERENCE_UPDATE.md | v14 | 仿真可视化加入照片口径结构理解面板，强化三电机嵌入发射管 |
| 装配 CAD | outrunner_target_resultant_tube_v1_2f.scad | v1.2f | 初始合力方向直接锁定目标方向，A/B/C 差速只用于侧旋弧线 |
| 文档 | SIM_VISUALIZER_V15_TARGET_RESULTANT_UPDATE.md | v15 | 仿真可视化改为目标方向锁定初始合力，侧旋与瞄准解耦 |
| 装配 CAD | outrunner_integrated_tube_motor_mount_v1_2g.scad | v1.2g | 发射圆管兼三电机固定一体结构，贴近参考图橙色一体夹持件 |
| 文档 | INTEGRATED_TUBE_MOTOR_MOUNT_V1_2G.md | v1.2g | 圆管 + 三电机口袋 + 端压板 + 加强筋一体结构说明 |
| 文档 | SIM_VISUALIZER_V16_INTEGRATED_STRUCTURE_UPDATE.md | v16 | 仿真可视化加入一体固定结构截面和 3D 一体夹持件表达 |
