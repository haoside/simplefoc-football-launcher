// 63xx outer-rotor BLDC motor placeholder v2
// Units: mm
// Purpose: layout clearance + bottom-face mounting placeholder only.
// Default values reflect the currently preferred 6354-class direction.

$fn = 96;

motor_d = 63;
motor_len = 53.5;        // 6354 placeholder length
shaft_d = 10;
shaft_len = 29.5;
mount_face_t = 4;

// hole systems from current reference drawing
mount_top_pcd_outer = 44;
mount_top_pcd_inner = 30;
mount_bottom_pcd = 22;
mount_hole_d = 4.2;      // M4 clearance-style visual

module outer_rotor_motor_63xx_bottom_mount(){
  color("#374151")
  union() {
    cylinder(h=motor_len, d=motor_d);
    translate([0,0,motor_len]) cylinder(h=shaft_len, d=shaft_d);
    translate([0,0,-mount_face_t]) cylinder(h=mount_face_t, d=motor_d+4);
  }

  // top-side visual hole sets
  color("#111827") {
    for (a=[45:90:315])
      translate([(mount_top_pcd_outer/2)*cos(a),(mount_top_pcd_outer/2)*sin(a),motor_len-mount_face_t])
        cylinder(h=mount_face_t+0.4, d=mount_hole_d);
    for (a=[0:90:270])
      translate([(mount_top_pcd_inner/2)*cos(a),(mount_top_pcd_inner/2)*sin(a),motor_len-mount_face_t])
        cylinder(h=mount_face_t+0.4, d=mount_hole_d);
  }

  // bottom mounting holes visual (current preferred installation face)
  color("#1f2937")
    for (a=[0:90:270])
      translate([(mount_bottom_pcd/2)*cos(a),(mount_bottom_pcd/2)*sin(a),-0.2])
        cylinder(h=mount_face_t+0.4, d=mount_hole_d);
}

outer_rotor_motor_63xx_bottom_mount();
