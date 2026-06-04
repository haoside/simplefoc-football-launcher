// 6374 BLDC motor placeholder v1
// Units: mm
// Purpose: layout clearance only, not manufacturing geometry.

$fn = 96;
motor_d = 63;
motor_len = 74;
shaft_d = 8;
shaft_len = 24;
mount_pcd = 44;
mount_hole_d = 5.5;
mount_face_t = 4;

module motor_6374_placeholder() {
  color("#374151")
  union() {
    cylinder(h=motor_len, d=motor_d);
    translate([0,0,motor_len]) cylinder(h=shaft_len, d=shaft_d);
    translate([0,0,-mount_face_t]) cylinder(h=mount_face_t, d=motor_d+4);
  }
  // mount holes visual
  color("#111827")
  for (a=[0:90:270])
    translate([(mount_pcd/2)*cos(a),(mount_pcd/2)*sin(a),-mount_face_t-0.2])
      cylinder(h=mount_face_t+0.4, d=mount_hole_d);
}

motor_6374_placeholder();
