// SimpleFOC football launcher - launch tube with side windows for outrunner direct contact v1.1
// Concept: 3x 6354 outrunners are fixed by END FACE brackets; tube body has 3 side openings so the outer shells contact the ball directly.
// Freeze constraints kept: same-plane centerlines, equilateral-triangle layout, direct shell contact, bottom-side fixed logic, rigidity before appearance.
// Units: mm

$fn = 128;

// ---------- Primary parameters ----------
ball_d                  = 220;    // size-5 football nominal OD
ball_clearance          = 12;     // keep v1 tube ID boundary unless test proves otherwise
inner_d                 = ball_d + ball_clearance;   // 232

tube_wall               = 5;
tube_len                = 260;
flare_len               = 35;
flare_extra_d           = 34;

// 6354 baseline - must stay parameterized until real motor is measured
motor_d                 = 63;
motor_len               = 54;
contact_sink            = 2.5;    // target adjustable squeeze, keep within 2-3 mm
contact_sink_min        = 2.0;
contact_sink_max        = 3.0;
motor_clearance         = 3;
rubber_sleeve_t         = 1.5;    // replaceable friction sleeve nominal thickness

window_margin_d         = 14;
window_margin_l         = 16;
window_z_len            = motor_d + window_margin_d;
window_tangent_w        = motor_len + window_margin_l;
window_corner_r         = 10;     // explicit rounded window corners
window_inner_relief     = 6;      // soften inner opening edge
window_relief_r         = 4;

end_plate_thickness     = 8;
end_plate_margin_y      = 16;
end_plate_margin_z      = 16;
end_plate_offset        = 16;
end_face_center_hole_d  = 24;     // bearing-boss / shaft clearance only, not drive feature
mount_hole_d            = 5.5;    // default M5 clearance
mount_hole_x_spacing    = 30;     // placeholder for 6354, verify by measurement
mount_hole_z_spacing    = 30;     // placeholder for 6354, verify by measurement
mount_slot_extra        = 4;      // keep adapter plate compatible with measured pattern drift
mount_plate_fillet_r    = 5;

rib_w                   = 16;
rib_t                   = 8;
rib_z_offset            = 8;
rib_frame_extra         = 16;
longitudinal_rib_t      = 5;
longitudinal_rib_h      = 12;

shield_hole_d           = 4.5;    // M4/M4.5 clearance depending fastener strategy
shield_standoff_t       = 6;
shield_hole_pair_dx     = window_tangent_w + 20;
shield_hole_pair_dz     = window_z_len + 18;
shield_tab_w            = 14;
shield_tab_h            = 10;
shield_tab_t            = shield_standoff_t;

adjust_slot_len         = 18;     // localized radial adjustment travel expression near base side
adjust_slot_w           = 6;
adjust_block_t          = 10;
adjust_block_w          = 18;

show_motors             = true;
show_ball_path          = true;
show_contact_patches    = true;
show_shield_tabs        = true;
show_adjust_blocks      = true;

// ---------- Derived ----------
inner_r = inner_d/2;
outer_r = inner_r + tube_wall;
contact_sink_safe = min(max(contact_sink, contact_sink_min), contact_sink_max);
motor_center_r = inner_r + motor_d/2 - contact_sink_safe;
window_radial_depth = tube_wall + motor_d + 18;
end_plate_w = motor_len + 2*end_plate_margin_y;
end_plate_h = motor_d + 2*end_plate_margin_z;
bridge_y = motor_center_r + motor_d/2 + motor_clearance + 12;

// ---------- Helpers ----------
module rounded_rect_2d(w, h, r=6) {
  rr = min(r, min(w,h)/2 - 0.01);
  hull() {
    translate([-w/2+rr, -h/2+rr]) circle(r=rr);
    translate([ w/2-rr, -h/2+rr]) circle(r=rr);
    translate([-w/2+rr,  h/2-rr]) circle(r=rr);
    translate([ w/2-rr,  h/2-rr]) circle(r=rr);
  }
}

module slot_2d(len, w) {
  hull() {
    translate([-len/2+w/2,0]) circle(d=w);
    translate([ len/2-w/2,0]) circle(d=w);
  }
}

module side_window_cut() {
  translate([0, outer_r - window_radial_depth/2 + 3, 0])
    linear_extrude(height=window_radial_depth, center=true)
      rounded_rect_2d(window_tangent_w, window_z_len, window_corner_r);
}

module side_window_inner_relief() {
  translate([0, inner_r + window_inner_relief/2, 0])
    rotate([90,0,0])
      linear_extrude(height=window_inner_relief, center=true)
        rounded_rect_2d(window_tangent_w - 8, window_z_len - 8, window_relief_r);
}

module shield_mount_tabs() {
  for (sx=[-1,1])
    for (sz=[-1,1])
      translate([sx*shield_hole_pair_dx/2, outer_r + shield_tab_t/2, sz*shield_hole_pair_dz/2])
        difference() {
          cube([shield_tab_w, shield_tab_t, shield_tab_h], center=true);
          rotate([90,0,0]) cylinder(d=shield_hole_d, h=shield_tab_t + 2, center=true);
        }
}

module longitudinal_ribs() {
  for (sz=[-1,1])
    translate([0, outer_r + longitudinal_rib_t/2, sz*(window_z_len/2 + rib_z_offset)])
      cube([window_tangent_w + rib_frame_extra, longitudinal_rib_t, longitudinal_rib_h], center=true);
}

module perimeter_ribs() {
  for (z=[-window_z_len/2-rib_w/2, window_z_len/2+rib_w/2])
    translate([0, outer_r+rib_t/2, z]) cube([window_tangent_w+2*rib_w, rib_t, rib_w], center=true);
  for (x=[-window_tangent_w/2-rib_w/2, window_tangent_w/2+rib_w/2])
    translate([x, outer_r+rib_t/2, 0]) cube([rib_w, rib_t, window_z_len+2*rib_w], center=true);
}

module tube_body() {
  difference() {
    union() {
      difference() {
        cylinder(h=tube_len, r=outer_r, center=true);
        cylinder(h=tube_len+2, r=inner_r, center=true);
      }

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

      for (a=[-90,30,150]) rotate([0,0,a]) {
        perimeter_ribs();
        longitudinal_ribs();
        if (show_shield_tabs) shield_mount_tabs();
      }
    }

    for (a=[-90,30,150]) rotate([0,0,a]) side_window_cut();
    for (a=[-90,30,150]) rotate([0,0,a]) side_window_inner_relief();
  }
}

module motor_shell_envelope() {
  rotate([0,90,0]) cylinder(d=motor_d, h=motor_len, center=true);
}

module mount_pattern_cut(x_pos) {
  // Adapter-plate style parameterized slot pattern: keeps geometry valid before measured hole pitch is locked.
  for (yy=[-mount_hole_x_spacing/2, mount_hole_x_spacing/2])
    for (zz=[-mount_hole_z_spacing/2, mount_hole_z_spacing/2])
      translate([x_pos, motor_center_r + yy, zz])
        rotate([0,90,0])
          linear_extrude(height=end_plate_thickness + 2, center=true)
            slot_2d(mount_slot_extra + mount_hole_d, mount_hole_d);
}

module end_face_mount_plate(side=1) {
  x = side * (motor_len/2 + end_plate_offset + end_plate_thickness/2);
  difference() {
    translate([x, motor_center_r, 0])
      rotate([0,90,0])
        linear_extrude(height=end_plate_thickness, center=true)
          rounded_rect_2d(end_plate_h, end_plate_w, mount_plate_fillet_r);

    translate([x, motor_center_r, 0])
      rotate([0,90,0]) cylinder(d=end_face_center_hole_d, h=end_plate_thickness+2, center=true);

    mount_pattern_cut(x);
  }
}

module end_face_bridge() {
  union() {
    end_face_mount_plate(-1);
    end_face_mount_plate(1);
    translate([0, bridge_y, 0])
      cube([motor_len + 2*end_plate_offset + end_plate_thickness, 14, end_plate_h], center=true);
  }
}

module adjuster_expression() {
  if (show_adjust_blocks) {
    for (side=[-1,1]) {
      x = side * (motor_len/2 + end_plate_offset + end_plate_thickness + adjust_block_t/2 + 2);
      difference() {
        translate([x, bridge_y - 10, 0])
          cube([adjust_block_t, adjust_block_w, end_plate_h*0.62], center=true);
        translate([x, bridge_y - 10, 0])
          rotate([0,90,0])
            linear_extrude(height=adjust_block_t+2, center=true)
              slot_2d(adjust_slot_len, adjust_slot_w);
      }
    }
  }
}

module one_motor_module() {
  color([1.0,0.72,0.76,1]) end_face_bridge();
  color([0.96,0.70,0.82,1]) adjuster_expression();

  if (show_motors)
    color([0.92,0.96,1.0,0.44]) translate([0, motor_center_r, 0]) motor_shell_envelope();

  if (show_contact_patches)
    color([1.0,0.86,0.18,0.85]) translate([0, inner_r - contact_sink_safe/2, 0]) cube([motor_len*0.84, contact_sink_safe, window_z_len*0.70], center=true);
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

// ---------- Verification notes ----------
// Required real-world checks before manufacturing:
// - actual 6354 shell OD and shell length
// - actual end-face mounting hole pattern / bearing boss diameter
// - rubber sleeve thickness and resulting final squeeze
// - rotor dynamic balance / safe speed after adding sleeve
// - heat dissipation path around side-window opening and shield installation clearance
