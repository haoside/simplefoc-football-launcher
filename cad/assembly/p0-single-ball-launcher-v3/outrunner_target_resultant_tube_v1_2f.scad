// SimpleFOC football launcher - target-resultant embedded 3-outrunner launch tube layout v1.2f
// Tightened from v1.2 per PM/new reference image:
// - center is a SHORT tilted tube/ring, not a long launch barrel
// - 3 outrunners wrap around the tube and contact the ball near the tube wall
// - motors are embedded/clamped into the tube-side structure, not external bolt-on modules
// - target-resultant: center short tube + embedded three motors; initial resultant force points directly to target
// Units: mm

$fn = 128;

// ---------- Core parameters ----------
ball_d                    = 220;
ball_clearance            = 12;
inner_d                   = ball_d + ball_clearance;   // 232 baseline
inner_r                   = inner_d/2;

short_tube_len            = 76;     // key change: short guide tube / short ring, not a long barrel
short_tube_wall           = 9;
launch_tilt_deg           = 18;      // three embedded motors tilted for direct upward launch
station_roll_deg          = 90;      // roll/flip tilted three-motor station by 90deg
photo_ref_embedded        = true;    // motors are embedded into tube-side cradle, not external add-ons
target_resultant_locked   = true;    // v1.2f: initial resultant direction is target direction; diff RPM creates spin/curve only
tube_outer_r              = inner_r + short_tube_wall;
front_lip_t               = 8;
rear_lip_t                = 8;
lip_extra_r               = 10;

// 6354 baseline
motor_d                   = 63;
motor_len                 = 54;
motor_flip_180            = true;
contact_sink              = 2.5;
contact_sink_min          = 2.0;
contact_sink_max          = 3.0;
contact_sink_safe         = min(max(contact_sink, contact_sink_min), contact_sink_max);
rubber_sleeve_t           = 1.5;
spin_clearance            = 3;

// Embedded motor pocket around short tube
motor_center_r            = inner_r + motor_d/2 - contact_sink_safe;
pocket_tangent_w          = motor_len + 18;
pocket_z_len              = motor_d + 18;
pocket_radial_depth       = short_tube_wall + motor_d + 20;
pocket_corner_r           = 10;
inner_relief_t            = 5;

// Clamp / saddle
saddle_back_t             = 10;
saddle_side_t             = 7;
saddle_z_margin           = 9;
end_clamp_t               = 8;
end_clamp_margin          = 10;
end_clamp_center_hole_d   = 24;
end_hole_d                = 5.5;
end_hole_pitch            = 45;
end_slot_extra            = 4;

// One-end 45x45 mount, offset to rear side of tube
main_mount_pitch          = 45;
main_mount_hole_d         = 5.5;
main_mount_pad_w          = 86;
main_mount_pad_h          = 86;
main_mount_pad_t          = 10;
main_mount_y              = tube_outer_r + motor_d + 30;
main_mount_z              = -short_tube_len/2 - 18;
main_mount_center_hole_d  = 14;

// Reinforcement only; protective shield removed per owner v1.2b
rib_t                     = 7;
rib_w                     = 15;
rib_extra                 = 14;
shield_hole_d             = 4.5;
shield_tab_t              = 5;
shield_tab_w              = 14;
shield_tab_z_gap          = 42;
shield_tab_x_gap          = motor_len + 24;

// Display toggles
show_ball_path            = true;
show_motors               = true;
show_contact_patches      = true;
show_mount                = true;
show_shield_tabs          = false;  // v1.2b: remove protective shield tabs from main baseline
show_launch_axis          = true;   // visualizes tilted three-motor resultant launch vector

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

module pocket_cut() {
  translate([0, tube_outer_r - pocket_radial_depth/2 + 3, 0])
    linear_extrude(height=pocket_radial_depth, center=true)
      rounded_rect_2d(pocket_tangent_w, pocket_z_len, pocket_corner_r);
}

module inner_relief_cut() {
  translate([0, inner_r + inner_relief_t/2, 0])
    rotate([90,0,0])
      linear_extrude(height=inner_relief_t+1, center=true)
        rounded_rect_2d(pocket_tangent_w - 8, pocket_z_len - 8, 5);
}

module short_tube_body() {
  difference() {
    union() {
      // short center tube / ring
      difference() {
        cylinder(h=short_tube_len, r=tube_outer_r, center=true);
        cylinder(h=short_tube_len+2, r=inner_r, center=true);
      }

      // inlet/outlet lips: launch axis is tube axis, outlet = +Z
      for (z=[-short_tube_len/2 + rear_lip_t/2, short_tube_len/2 - front_lip_t/2])
        difference() {
          translate([0,0,z]) cylinder(h=front_lip_t, r=tube_outer_r + lip_extra_r, center=true);
          translate([0,0,z]) cylinder(h=front_lip_t+2, r=inner_r, center=true);
        }

      // integrated reinforcements around the embedded pockets
      for (a=[-90,30,150]) rotate([0,0,a]) {
        for (z=[-pocket_z_len/2-rib_w/2, pocket_z_len/2+rib_w/2])
          translate([0, tube_outer_r + rib_t/2, z]) cube([pocket_tangent_w+2*rib_extra, rib_t, rib_w], center=true);
        for (x=[-pocket_tangent_w/2-rib_w/2, pocket_tangent_w/2+rib_w/2])
          translate([x, tube_outer_r + rib_t/2, 0]) cube([rib_w, rib_t, pocket_z_len+2*rib_extra], center=true);
      }
    }

    for (a=[-90,30,150]) rotate([0,0,a]) pocket_cut();
    for (a=[-90,30,150]) rotate([0,0,a]) inner_relief_cut();
  }
}

module motor_shell() {
  rotate([0,90,0]) cylinder(d=motor_d, h=motor_len, center=true);
}

module end_clamp(side=1) {
  fixed_side = motor_flip_180 ? -side : side;
  x = fixed_side * (motor_len/2 + end_clamp_t/2);
  difference() {
    translate([x, motor_center_r, 0]) cube([end_clamp_t, motor_d+2*end_clamp_margin, motor_d+2*end_clamp_margin], center=true);
    translate([x, motor_center_r, 0]) rotate([0,90,0]) cylinder(d=end_clamp_center_hole_d, h=end_clamp_t+2, center=true);
    for (yy=[-end_hole_pitch/2, end_hole_pitch/2])
      for (zz=[-end_hole_pitch/2, end_hole_pitch/2])
        translate([x, motor_center_r+yy, zz])
          rotate([0,90,0])
            linear_extrude(height=end_clamp_t+2, center=true)
              slot_2d(end_hole_d+end_slot_extra, end_hole_d);
  }
}

module embedded_saddle() {
  // saddle is nested into the tube-side structure; inner side remains open for rotor contact.
  translate([0, motor_center_r + motor_d/2 + spin_clearance + saddle_back_t/2, 0])
    cube([motor_len+2*end_clamp_t, saddle_back_t, motor_d+2*saddle_z_margin], center=true);
  for (sx=[-1,1])
    translate([sx*(motor_len/2+saddle_side_t/2), motor_center_r, 0])
      cube([saddle_side_t, motor_d+2*saddle_z_margin, motor_d+2*saddle_z_margin], center=true);
}

module one_motor_station() {
  color([1.0,0.62,0.08,1]) embedded_saddle();
  color([1.0,0.48,0.05,1]) end_clamp(1);

  if (show_motors)
    color([0.82,0.90,1.0,0.60]) translate([0,motor_center_r,0]) motor_shell();

  if (show_contact_patches)
    color([1.0,0.86,0.18,0.88]) translate([0, inner_r-contact_sink_safe/2, 0])
      cube([motor_len*0.82, contact_sink_safe, motor_d*0.64], center=true);

  if (show_shield_tabs)
    for (sx=[-1,1]) for (sz=[-1,1])
      translate([sx*shield_tab_x_gap/2, tube_outer_r+18+shield_tab_t/2, sz*shield_tab_z_gap/2])
        difference() {
          cube([shield_tab_w, shield_tab_t, 12], center=true);
          rotate([90,0,0]) cylinder(d=shield_hole_d, h=shield_tab_t+2, center=true);
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
  color([1,1,1,0.18]) cylinder(h=short_tube_len+8, r=ball_d/2, center=true);
}

module launch_axis_arrow() {
  if (show_launch_axis) {
    color([0.2,1,0.15,0.65]) translate([0,0,short_tube_len/2+42]) cylinder(d=8, h=84, center=true);
    color([0.2,1,0.15,0.65]) translate([0,0,short_tube_len/2+88]) cylinder(d1=28, d2=0, h=36, center=true);
  }
}

// ---------- Assembly ----------
module tilted_launch_cluster() {
  color([1.0,0.88,0.10,1]) short_tube_body();
  all_motor_stations();
  color([1.0,0.70,0.08,1]) rotate([0,0,-90]) main_mount_pad();
  if (show_ball_path) ball_path_envelope();
  launch_axis_arrow();
}

// v1.2c: tilt the whole embedded three-motor launch station for direct upward firing.
rotate([launch_tilt_deg, 0, 0]) tilted_launch_cluster();

// ---------- Notes ----------
// v1.2d rolls/flips the embedded three-motor station 90deg for direct upward launch.
// Launch direction is the three-motor resultant force vector; tube axis is tilted with the motor cluster.
