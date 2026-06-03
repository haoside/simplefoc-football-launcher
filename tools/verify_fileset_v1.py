from pathlib import Path

required = [
    'cad/3d-print/short-guide-tube-v1/README.md',
    'cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad',
    'cad/sheet-metal/motor-mount-plate-v1/README.md',
    'cad/sheet-metal/motor-mount-plate-v1/motor_mount_plate_v1.scad',
    'cad/sheet-metal/guard-bracket-v1/README.md',
    'cad/sheet-metal/guard-bracket-v1/guard_bracket_v1.scad',
    'cad/sheet-metal/control-bay-plate-v1/README.md',
    'cad/sheet-metal/control-bay-plate-v1/control_bay_plate_v1.scad',
    'cad/sheet-metal/power-bay-plate-v1/README.md',
    'cad/sheet-metal/power-bay-plate-v1/power_bay_plate_v1.scad',
    'cad/sheet-metal/battery-clamp-v1/README.md',
    'cad/sheet-metal/battery-clamp-v1/battery_clamp_v1.scad',
    'cad/sheet-metal/estop-panel-v1/README.md',
    'cad/sheet-metal/estop-panel-v1/estop_panel_v1.scad',
    'docs/mechanical/MANUFACTURING_FILESET_V1.md',
]

missing = []
empty = []
for rel in required:
    p = Path(rel)
    if not p.exists():
        missing.append(rel)
        continue
    if p.is_file() and p.stat().st_size == 0:
        empty.append(rel)

print('required_files=', len(required))
print('missing=', len(missing))
for x in missing:
    print('MISSING', x)
print('empty=', len(empty))
for x in empty:
    print('EMPTY', x)
print('status=', 'OK' if not missing and not empty else 'FAIL')
