// SimpleFOC football launcher - launch tube with side windows for outrunner direct contact v1
// Concept: motors are fixed by END FACE brackets; tube body has 3 side openings so 6374 outrunner shells contact the ball directly.
// No external friction wheel; motor shaft is ignored as a drive element.
// Units: mm

$fn = 128;

// ---------- Primary parameters ----------
ball_d                = 220;     // size-5 football nominal OD
ball_clearance        = 12;      // guide clearance; ID=232 follows previous short-guide boundary
inner_d               = ball_d + ball_clearance;
tube_wall             = 5;
tube_len              = 260;
flare_len             = 35;
flare_extra_d         = 34;

motor_d               = 74;      // 6374 outrunner shell OD; verify actual motor
motor_len             = 74;      // shell length along tangential axis
contact_sink          = 3;       // shell protrudes into tube ID by this amount for squeeze/contact
motor_clearance       = 3;       // non-contact safety clearance around spinning shell

window_z_len          = motor_d + 18;   // opening length along launch direction Z
window_tangent_w      = motor_len + 16; // opening width along tangent direction
window_corner_r       = 8;

end_plate_thickness   = 8;
end_plate_margin      = 14;
end_plate_w           = motor_len + 2*end_plate_margin;
end_plate_h           = motor_d + 2*end_plate_margin;
end_plate_offset      = 18;      // gap from spinning shell side to fixed end plate
mount_hole_d          = 5.5;     // M5 clearance
mount_hole_x_spacing  = 46;
mount_hole_z_spacing  = 46;

rib_w                 = 18;
rib_t                 = 8;
show_motors           = true;
show_ball_path        = true;
show_contact_patches  = true;

// ---------- Derived ----------
inner_r = inner_d/2;
outer_r = inner_r + tube_wall;
motor_center_r = inner_r + motor_d/2 - contact_sink;
window_radial_depth = tube_wall + motor_d + 16;

// ---------- Helpers ----------
module rounded_rect_2d(w, h, r=6) {
  hull() {
    translate([-w/2+r, -h/2+r]) circle(r=r);
    translate([ w/2-r, -h/2+r]) circle(r=r);
    translate([-w/2+r,  h/2-r]) circle(r=r);
    translate([ w/2-r,  h/2-r]) circle(r=r);
  }
}

module capsule_2d(len, w) {
  hull() {
    translate([-len/2+w/2,0]) circle(d=w);
    translate([ len/2-w/2,0]) circle(d=w);
  }
}

// Local coordinate for one motor/window sector:
// +Y radial outward from tube center; X tangent; Z launch direction.
module side_window_cut() {
  translate([0, outer_r - window_radial_depth/2 + 3, 0])
    cube([window_tangent_w, window_radial_depth, window_z_len], center=true);
}

module tube_body() {
  difference() {
    union() {
      // Main straight tube
      difference() {
        cylinder(h=tube_len, r=outer_r, center=true);
        cylinder(h=tube_len+2, r=inner_r, center=true);
      }

      // Front/back soft flares to help hand-feed and exit clearance
      for (z=[-tube_len/2 - flare_len/2, tube_len/2 + flare_len/2]) {
        difference() {
          hull() {
            translate([0,0,z - sign(z)*flare_len/2]) cylinder(h=1, r=outer_r, center=true);
            translate([0,0,z + sign(z)*flare_len/2]) cylinder(h=1, r=outer_r + flare_extra_d/2, center=true);
          }
          hull() {
            translate([0,0,z - sign(z)*flare_len/2]) cylinder(h=2, r=inner_r, center=true);
            translate([0,0,z + sign(z)*flare_len/2]) cylinder(h=2, r=inner_r + flare_extra_d/2, center=true);
          }
        }
      }

      // External ribs around the 3 openings; keeps tube stiff after window cuts.
      for (a=[-90,30,150]) rotate([0,0,a]) {
        for (z=[-window_z_len/2-rib_w/2, window_z_len/2+rib_w/2])
          translate([0, outer_r+rib_t/2, z]) cube([window_tangent_w+2*rib_w, rib_t, rib_w], center=true);
        for (x=[-window_tangent_w/2-rib_w/2, window_tangent_w/2+rib_w/2])
          translate([x, outer_r+rib_t/2, 0]) cube([rib_w, rib_t, window_z_len+2*rib_w], center=true);
      }
    }

    // 3 side openings for direct outrunner shell contact
    for (a=[-90,30,150]) rotate([0,0,a]) side_window_cut();

    // Reduce sharp internal edges near openings
    for (a=[-90,30,150]) rotate([0,0,a])
      translate([0, inner_r+1, 0]) cube([window_tangent_w-10, 8, window_z_len-10], center=true);
  }
}

module motor_shell_envelope() {
  // Tangential motor axis = local X. The visible cylinder penetrates the tube window.
  rotate([0,90,0]) cylinder(d=motor_d, h=motor_len, center=true);
}

module end_face_mount_plate(side=1) {
  // side = -1 / +1 along tangent X; fixed plate bolts to motor end face / adapter plate.
  x = side * (motor_len/2 + end_plate_offset + end_plate_thickness/2);
  difference() {
    translate([x, motor_center_r, 0])
      cube([end_plate_thickness, end_plate_w, end_plate_h], center=true);

    // Large center clearance / bearing-boss clearance. Not used as drive shaft.
    translate([x, motor_center_r, 0]) rotate([0,90,0]) cylinder(d=24, h=end_plate_thickness+2, center=true);

    // 4 mounting holes on end face adapter pattern, placeholder until real motor measured.
    for (yy=[-mount_hole_x_spacing/2, mount_hole_x_spacing/2])
      for (zz=[-mount_hole_z_spacing/2, mount_hole_z_spacing/2])
        translate([x, motor_center_r + yy, zz]) rotate([0,90,0]) cylinder(d=mount_hole_d, h=end_plate_thickness+2, center=true);
  }
}

module end_face_bridge() {
  // U cradle: two end plates connected back outside the spinning shell.
  union() {
    end_face_mount_plate(-1);
    end_face_mount_plate(1);
    translate([0, motor_center_r + motor_d/2 + motor_clearance + 14, 0])
      cube([motor_len + 2*end_plate_offset + end_plate_thickness, 14, end_plate_h], center=true);
  }
}

module one_motor_module() {
  // Bracket is outside tube; inner side remains open so shell can contact ball through window.
  color([1.0,0.72,0.76,1]) end_face_bridge();

  if (show_motors)
    color([0.92,0.96,1.0,0.44]) translate([0, motor_center_r, 0]) motor_shell_envelope();

  if (show_contact_patches)
    color([1.0,0.86,0.18,0.8]) translate([0, inner_r-1, 0]) cube([motor_len*0.82, 3, window_z_len*0.72], center=true);
}

module all_motor_modules() {
  for (a=[-90,30,150]) rotate([0,0,a]) one_motor_module();
}

module ball_path_envelope() {
  color([1,1,1,0.20]) cylinder(h=tube_len + 2*flare_len, r=ball_d/2, center=true);
}

// ---------- Assembly ----------
color([1.0,0.78,0.82,1]) tube_body();
all_motor_modules();
if (show_ball_path) ball_path_envelope();

// ---------- Export notes ----------
// OpenSCAD:
// - F5 preview to inspect openings and motor envelopes.
// - F6 render then export STL for prototype.
// - Set show_motors=false/show_ball_path=false before exporting printable tube-only body.
// Mechanical verification required:
// - actual 6374 shell OD/length/end-face screw pattern
// - safe gap around spinning shell
// - motor thermal path and replaceable high-friction sleeve
// - tube window edge chamfer / rubber liner to avoid cutting football surface
