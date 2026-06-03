from pathlib import Path
required = [
    'docs/mechanical/FAB_VENDOR_PACKAGE_V1.md',
    'docs/mechanical/MANUFACTURING_FILESET_V1.md',
    'docs/mechanical/CAD_EXPORT_GUIDE_V1.md',
    'docs/mechanical/PRE_FAB_CHECKLIST_V1.md',
    'docs/mechanical/EXPORT_FILE_CHECKLIST_V1.md',
    'docs/mechanical/FILE_VERSION_MATRIX_V1.md',
]
missing = [x for x in required if not Path(x).exists()]
print('required_docs=', len(required))
print('missing=', len(missing))
for x in missing:
    print('MISSING', x)
print('status=', 'OK' if not missing else 'FAIL')
