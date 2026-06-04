#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-build/cad-exports}"
mkdir -p "$OUT_DIR"

if ! command -v openscad >/dev/null 2>&1; then
  echo "openscad not found; install OpenSCAD before running exports" >&2
  exit 127
fi

export_png() {
  local src="$1"
  local out="$2"
  local camera="$3"
  openscad \
    --imgsize=1600,1000 \
    --camera="$camera" \
    --colorscheme=Tomorrow \
    -o "$out" "$src" || true
}

export_one() {
  local src="$1"
  local name="$2"
  local dir="$OUT_DIR/$name"
  mkdir -p "$dir"
  echo "Exporting $src -> $dir"
  openscad -o "$dir/${name}.stl" "$src"
  # Default PNG preview. If PNG export is unsupported, keep STL.
  export_png "$src" "$dir/${name}.png" "500,500,420,60,0,135,850"
}

export_assembly_views() {
  local src="$1"
  local name="$2"
  local dir="$OUT_DIR/$name"
  mkdir -p "$dir"
  echo "Exporting assembly views $src -> $dir"
  openscad -o "$dir/${name}.stl" "$src"
  export_png "$src" "$dir/${name}_isometric.png" "900,850,760,65,0,135,1200"
  export_png "$src" "$dir/${name}_front.png"     "0,-1400,620,70,0,0,1300"
  export_png "$src" "$dir/${name}_side.png"      "1400,0,620,70,0,90,1300"
  export_png "$src" "$dir/${name}_top.png"       "0,0,1800,0,0,0,1450"
  # Compatibility name for consumers expecting the old path.
  cp "$dir/${name}_isometric.png" "$dir/${name}.png" 2>/dev/null || true
}

export_one "cad/3d-print/short-guide-tube-v1/short_guide_tube_v1.scad" "short_guide_tube_v1"
export_one "cad/3d-print/friction-wheel-v1/friction_wheel_v1.scad" "friction_wheel_v1"
export_one "cad/vendor-placeholders/6374-motor-v1/6374_motor_placeholder_v1.scad" "6374_motor_placeholder_v1"
export_one "cad/frame/mobile-base-v1/mobile_base_frame_v1.scad" "mobile_base_frame_v1"
export_one "cad/mechanisms/radial-wheel-adjust-v1/radial_wheel_adjust_v1.scad" "radial_wheel_adjust_v1"
export_assembly_views "cad/assembly/p0-single-ball-launcher-v1/p0_single_ball_launcher_assembly_v1.scad" "p0_single_ball_launcher_assembly_v1"

cat > "$OUT_DIR/MANIFEST.md" <<MANIFEST
# CAD Export Manifest

Generated from OpenSCAD sources.

## Files

- short_guide_tube_v1
- friction_wheel_v1
- 6374_motor_placeholder_v1
- mobile_base_frame_v1
- radial_wheel_adjust_v1
- p0_single_ball_launcher_assembly_v1 (STL + isometric/front/side/top PNG views)

## Notes

These are P0 layout / placeholder exports. The 6374 motor, friction wheel, and mobile base require vendor/fabrication data before final manufacturing.
MANIFEST
