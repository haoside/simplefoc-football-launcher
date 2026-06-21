// SimpleFOC football launcher - embedded 3-outrunner launch tube v1.2
// Visual target: reference images: 3 outer-rotor motors embedded around a launch tube, not a separate pink/yellow ring frame.
// Owner corrections included:
// - remove standalone ring visual; motors are embedded into launch tube wall
// - flip motors 180 deg vs prior v1.1a orientation
// - keep one-end 4-bolt 45x45 mounting interface
// - keep 6354 baseline, direct outer-rotor contact, 2-3mm squeeze
// - design toward 50m range and controllable 180deg launch arc via validation/simulation, not by cosmetic shape
// Units: mm

$fn = 128;

// ---------- Primary geometry ----------
ball_d                    = 220;
ball_clearance            = 12;
inner_d                   = ball_d + ball_clearance;   // 232
inner_r                   = inner_d/2;

tube_len                  = 190;    // shorter embedded launch tube; extend in engineering version if feed guidance requires
tube_wall                 = 8;
tube_outer_r              = inner_r + tube_wall;
front_lip_t               = 8;
rear_lip_t                = 8;
lip_extra_r               = 10;

// ---------- Motor / contact ----------
motor_d                   = 63;     // 6354 baseline OD
motor_len                 = 54;
motor_flip_180            = true;   // v1.2: terminals / fixed end flipped compared with v1.1a reference orientation
contact_sink              = 2.5;
contact_sink_min          = 2.0;
contact_sink_max          = 3.0;
contact_sink_safe         = min(max(contact_sink, contact_sink_min), contact_sink_max);
rubber_sleeve_t           = 1.5;
spin_clearance            = 3;

motor_center_r            = inner_r + motor_d/2 - contact_sink_safe;
embed_pocket_r_depth      = tube_wall + motor_d + 18;
embed_pocket_tangent_w    = motor_len + 18;
embed_pocket_z_len        = motor_d + 20;
pocket_corner_r           = 10;
inner_edge_relief         = 5;

// ---------- Embedded saddle / fixed brackets ----------
saddle_back_t             = 10;
saddle_side_t             = 7;
saddle_z_margin           = 10;
end_clamp_t               = 8;
end_clamp_margin          = 10;
end_clamp_center_hole_d   = 24;
motor_end_hole_d          = 5.5;
motor_end_hole_pitch      = 45;     // owner: one-end 4 screw 45x45 fixed pattern; also used as motor-end template until measured
motor_end_hole_slot_extra = 4;

// ---------- Main mount ----------
main_mount_hole_d         = 5.5;
main_mount_pitch          = 45;
main_mount_pad_w          = 86;
main_mount_pad_h          = 86;
main_mount_pad_t          = 10;
main_mount_y              = tube_outer_r + motor_d + 34;
main_mount_z              = -tube_len/2 + 38;  // one-end / rear-side mounting interface
main_mount_center_hole_d  = 14;

// ---------- Reinforcement / shield ----------
rib_t                     = 7;
rib_w                     = 16;
rib_extra                 = 14;
long_rib_h                = 10;
shield_hole_d             = 4.5;
shield_tab_t              = 5;
shield_tab_w              = 14;
shield_tab_z_gap          = 46;
shield_tab_x_gap          = motor_len + 24;

// ---------- Ballistics / simulation visual params ----------
target_range_m            = 50;
arc_control_deg           = 180;
trajectory_preview        = true;
trajectory_samples        = 16;
trajectory_scale          = 2.2;    // purely visual in this SCAD preview

show_ball_path            = true;
show_motors               = true;
show_contact_patches      = true;
show_shield_tabs          = true;
show_mount                = true;
show_trajectory_preview   = true;

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

module embedded_pocket_cut() {
  translate([0, tube_outer_r - embed_pocket_r_depth/2 + 3, 0])
    linear_extrude(height=embed_pocket_r_depth, center=true)
      rounded_rect_2d(embed_pocket_tangent_w, embed_pocket_z_len, pocket_corner_r);
}

module inner_relief_cut() {
  translate([0, inner_r + inner_edge_relief/2, 0])
    rotate([90,0,0])
      linear_extrude(height=inner_edge_relief + 1, center=true)
        rounded_rect_2d(embed_pocket_tangent_w - 8, embed_pocket_z_len - 8, 5);
}

module tube_shell() {
  difference() {
    union() {
      // main launch tube, not a standalone external ring
      difference() {
        cylinder(h=tube_len, r=tube_outer_r, center=true);
        cylinder(h=tube_len+2, r=inner_r, center=true);
      }

      // front/rear lips as tube features
      for (z=[-tube_len/2 + front_lip_t/2, tube_len/2 - rear_lip_t/2])
        difference() {
          translate([0,0,z]) cylinder(h=front_lip_t, r=tube_outer_r + lip_extra_r, center=true);
          translate([0,0,z]) cylinder(h=front_lip_t + 2, r=inner_r, center=true);
        }

      // integrated reinforcement around each embedded motor pocket
      for (a=[-90,30,150]) rotate([0,0,a]) {
        for (z=[-embed_pocket_z_len/2-rib_w/2, embed_pocket_z_len/2+rib_w/2])
          translate([0, tube_outer_r + rib_t/2, z]) cube([embed_pocket_tangent_w+2*rib_extra, rib_t, rib_w], center=true);
        for (x=[-embed_pocket_tangent_w/2-rib_w/2, embed_pocket_tangent_w/2+rib_w/2])
          translate([x, tube_outer_r + rib_t/2, 0]) cube([rib_w, rib_t, embed_pocket_z_len+2*rib_extra], center=true);
        translate([0, tube_outer_r + rib_t/2, 0]) cube([embed_pocket_tangent_w+2*rib_extra, rib_t, long_rib_h], center=true);
      }
    }

    for (a=[-90,30,150]) rotate([0,0,a]) embedded_pocket_cut();
    for (a=[-90,30,150]) rotate([0,0,a]) inner_relief_cut();
  }
}

module motor_shell() {
  rotate([0,90,0]) cylinder(d=motor_d, h=motor_len, center=true);
}

module motor_end_clamp(side=1) {
  // side=+1/-1 along tangential motor axis. v1.2 flips the shown fixed/terminal side by 180deg.
  flipped_side = motor_flip_180 ? -side : side;
  x = flipped_side * (motor_len/2 + end_clamp_t/2);
  difference() {
    translate([x, motor_center_r, 0]) cube([end_clamp_t, motor_d + 2*end_clamp_margin, motor_d + 2*end_clamp_margin], center=true);
    translate([x, motor_center_r, 0]) rotate([0,90,0]) cylinder(d=end_clamp_center_hole_d, h=end_clamp_t+2, center=true);
    for (yy=[-motor_end_hole_pitch/2, motor_end_hole_pitch/2])
      for (zz=[-motor_end_hole_pitch/2, motor_end_hole_pitch/2])
        translate([x, motor_center_r + yy, zz])
          rotate([0,90,0])
            linear_extrude(height=end_clamp_t+2, center=true)
              slot_2d(motor_end_hole_d + motor_end_hole_slot_extra, motor_end_hole_d);
  }
}

module embedded_saddle() {
  // U/backing saddle is part of tube module, motor appears nested into tube wall.
  translate([0, motor_center_r + motor_d/2 + spin_clearance + saddle_back_t/2, 0])
    cube([motor_len + 2*end_clamp_t, saddle_back_t, motor_d + 2*saddle_z_margin], center=true);
  for (sx=[-1,1])
    translate([sx*(motor_len/2 + saddle_side_t/2), motor_center_r, 0])
      cube([saddle_side_t, motor_d + 2*saddle_z_margin, motor_d + 2*saddle_z_margin], center=true);
}

module contact_patch() {
  color([1.0,0.86,0.18,0.85])
    translate([0, inner_r-contact_sink_safe/2, 0]) cube([motor_len*0.82, contact_sink_safe, motor_d*0.64], center=true);
}

module one_motor_station() {
  color([1.0,0.72,0.16,1]) embedded_saddle();
  color([1.0,0.58,0.12,1]) motor_end_clamp(1);

  if (show_motors)
    color([0.82,0.90,1.0,0.58]) translate([0, motor_center_r, 0]) motor_shell();
  if (show_contact_patches) contact_patch();

  if (show_shield_tabs) {
    for (sx=[-1,1])
      for (sz=[-1,1])
        translate([sx*shield_tab_x_gap/2, tube_outer_r + shield_tab_t/2 + 18, sz*shield_tab_z_gap/2])
          difference() {
            cube([shield_tab_w, shield_tab_t, 12], center=true);
            rotate([90,0,0]) cylinder(d=shield_hole_d, h=shield_tab_t+2, center=true);
          }
  }
}

module main_mount_pad() {
  if (show_mount)
    difference() {
      translate([0, main_mount_y, main_mount_z]) cube([main_mount_pad_w, main_mount_pad_t, main_mount_pad_h], center=true);
      translate([0, main_mount_y, main_mount_z]) rotate([90,0,0]) cylinder(d=main_mount_center_hole_d, h=main_mount_pad_t+2, center=true);
      for (x=[-main_mount_pitch/2, main_mount_pitch/2])
        for (z=[-main_mount_pitch/2, main_mount_pitch/2])
          translate([x, main_mount_y, main_mount_z+z]) rotate([90,0,0]) cylinder(d=main_mount_hole_d, h=main_mount_pad_t+2, center=true);
    }
}

module all_motor_stations() {
  for (a=[-90,30,150]) rotate([0,0,a]) one_motor_station();
}

module ball_path_envelope() {
  color([1,1,1,0.18]) cylinder(h=tube_len + 6, r=ball_d/2, center=true);
}

module trajectory_preview_arc() {
  if (show_trajectory_preview && trajectory_preview) {
    // visual only: shows controllable output arc envelope. Use physics sim for RPM/angle validation.
    for (i=[0:trajectory_samples]) {
      t = i/trajectory_samples;
      x = (t-0.5)*260;
      z = tube_len/2 + 20 + 110*sin(t*180);
      y = -inner_r - 30 - 80*t;
      color([0.2,1.0,0.1,0.25 + 0.35*t]) translate([x,y,z]) sphere(d=16 + 10*t);
    }
  }
}

// ---------- Assembly ----------
color([1.0,0.88,0.12,1]) tube_shell();
all_motor_stations();
color([1.0,0.70,0.10,1]) rotate([0,0,-90]) main_mount_pad();
if (show_ball_path) ball_path_envelope();
trajectory_preview_arc();

// ---------- Engineering targets ----------
// Range target: 50m. Needs RPM, contact time, rubber sleeve friction and ball mass validation.
// Arc target: controllable 0-180deg output envelope via speed differential / launch angle control; not guaranteed by static CAD.
// Simulation plan: start from rigid geometry -> kinematic contact -> RPM/friction sweep -> deformable ball / sleeve model.
