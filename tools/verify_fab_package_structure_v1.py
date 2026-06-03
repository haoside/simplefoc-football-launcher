from pathlib import Path
required = [
    'fab-package-v1/MANIFEST.md',
    'fab-package-v1/3d-print/short_guide_tube_v1',
    'fab-package-v1/sheet-metal/motor_mount_plate_v1',
    'fab-package-v1/sheet-metal/guard_bracket_v1',
    'fab-package-v1/sheet-metal/control_bay_plate_v1',
    'fab-package-v1/sheet-metal/power_bay_plate_v1',
    'fab-package-v1/sheet-metal/battery_clamp_v1',
    'fab-package-v1/sheet-metal/estop_panel_v1',
    'fab-package-v1/docs',
]
missing = []
for rel in required:
    p = Path(rel)
    if not p.exists():
        missing.append(rel)
print('required_entries=', len(required))
print('missing=', len(missing))
for x in missing:
    print('MISSING', x)
print('status=', 'OK' if not missing else 'FAIL')
