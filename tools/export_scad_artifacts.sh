#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-build/cad-exports}"
mkdir -p "$OUT_DIR"

if ! command -v openscad >/dev/null 2>&1; then
  echo "openscad not found; install OpenSCAD before running exports" >&2
  exit 127
fi

export_one() {
  local src="$1"
  local name="$2"
  local dir="$OUT_DIR/$name"
  mkdir -p "$dir"
  echo "Exporting $src -> $dir"
  openscad -o "$dir/${name}.stl" "$src"
  # PNG preview from a stable camera angle. If PNG export is unsupported, keep STL.
  openscad \
    --imgsize=1600,1000 \
    --camera=500,500,420,60,0,135,850 \
    --colorscheme=Tomorrow \
    -o "$dir/${name}.png" "$src" || true
}

export_one "cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad" "short_guide_tube_v1"
export_one "cad/3d-print/friction-wheel-v1/friction_wheel_v1.scad" "friction_wheel_v1"
export_one "cad/vendor-placeholders/6374-motor-v1/6374_motor_placeholder_v1.scad" "6374_motor_placeholder_v1"
export_one "cad/frame/mobile-base-v1/mobile_base_frame_v1.scad" "mobile_base_frame_v1"
export_one "cad/assembly/p0-single-ball-launcher-v1/p0_single_ball_launcher_assembly_v1.scad" "p0_single_ball_launcher_assembly_v1"

cat > "$OUT_DIR/MANIFEST.md" <<MANIFEST
# CAD Export Manifest

Generated from OpenSCAD sources.

## Files

- short_guide_tube_v1
- friction_wheel_v1
- 6374_motor_placeholder_v1
- mobile_base_frame_v1
- p0_single_ball_launcher_assembly_v1

## Notes

These are P0 layout / placeholder exports. The 6374 motor, friction wheel, and mobile base require vendor/fabrication data before final manufacturing.
MANIFEST
