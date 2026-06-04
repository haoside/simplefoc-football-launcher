# CAD Export Workflow v1

## Purpose

Automatically export OpenSCAD layout models into shareable CAD artifacts.

## Workflow

GitHub Actions file:

- `.github/workflows/cad-export.yml`

Trigger:

- manual `workflow_dispatch`
- push changes under `cad/**/*.scad`

## Exports

The script `tools/export_scad_artifacts.sh` exports:

1. `short_guide_tube_v1`
2. `friction_wheel_v1`
3. `6374_motor_placeholder_v1`
4. `mobile_base_frame_v1`
5. `p0_single_ball_launcher_assembly_v1`

Output artifact:

- `p0-cad-exports`

Expected files:

- STL files for CAD/printing review
- PNG preview if OpenSCAD image export succeeds
- `MANIFEST.md`

## Local usage

```bash
tools/export_scad_artifacts.sh build/cad-exports
```

Requires OpenSCAD installed locally.

## Product note

The assembly is a P0 layout/clearance model, not final manufacturing CAD. Vendor motor and wheel drawings must replace placeholders before fabrication freeze.
