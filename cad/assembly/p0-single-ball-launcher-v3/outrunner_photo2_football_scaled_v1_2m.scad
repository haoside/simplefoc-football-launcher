// SimpleFOC football launcher - photo2 matched football-scale 300mm embedded outrunner mount layout v1.2m
// Tightened from v1.2 per PM/new reference image:
// - photo2 matched: 300mm tube, front annular ring, top bridge motor cradle, two lower embedded motor cradles
// - 3 6354 outrunner cans remain outside-wall embedded; no center-axis insertion
// - motors are NOT inserted through the center axis; motor axes are tangential around the tube
// - photo focus: launch tube, three motor cradles, bridge straps, round relief holes, ribs and wire exits are one orange body
// Units: mm

$fn = 128;

// ---------- Core parameters ----------
project_scale_locked      = true;    // v1.2l: scale reference layout to football project size
reference_layout_note     = "scaled_from_small_reference_to_220mm_football";
ball_d                    = 220;
ball_clearance            = 12;
inner_d                   = ball_d + ball_clearance;   // 232 baseline
inner_r                   = inner_d/2;

launch_tube_len           = 300;     // v1.2k: 300mm launch tube length
short_tube_len            = launch_tube_len;
short_tube_wall           = 12;      // scaled up for 300mm football tube stiffness
launch_tilt_deg           = 18;      // three embedded motors tilted for direct upward launch
station_roll_deg          = 90;      // roll/flip tilted three-motor station by 90deg
photo_ref_embedded        = true;    // motors are embedded into tube-side cradle, not external add-ons
target_resultant_locked   = true;    // initial resultant direction is target direction; diff RPM creates spin/curve only
non_center_axis_motor     = true;    // v1.2k: outrunners embed from tube wall, never through center axis
motor_axis_layout         = "tangential_around_tube";
integrated_monocoque      = true;    // tube and three motor mounts are one integrated structure
photo_like_orange_body    = true;    // photo-reference orange printed body
structure_only_focus      = true;    // v1.2h: stop sim updates; focus mechanical integrated structure
show_wire_channels        = true;
show_tool_access          = true;
show_rotor_clearance      = true;
show_photo_side_plates    = true;
show_bridge_straps        = true;
show_round_relief_holes   = true;
show_lower_motor_shelf    = true;
show_45x45_4holes         = true;
show_front_annular_ring   = true;
show_top_bridge_cradle    = true;
show_lower_twin_cradles   = true;
show_four_screw_tabs      = true;
tube_outer_r              = inner_r + short_tube_wall;
project_outer_d           = 2 * tube_outer_r;
project_tube_aspect       = launch_tube_len / inner_d;  // 300 / 232 = 1.29 guide aspect
front_lip_t               = 14;
rear_lip_t                = 14;
lip_extra_r               = 18;

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
rotor_clearance_min       = 4.0;      // min target clearance around spinning outrunner can
wire_channel_w            = 16;
wire_channel_h            = 10;
wire_channel_len          = 72;
tool_access_d            = 13;        // screwdriver / hex key access envelope
tool_access_offset        = 26;
split_service_gap         = 2.0;      // optional split/service seam marker
photo_side_plate_t        = 12;
photo_side_plate_w        = 96;
photo_side_plate_h        = 128;
round_relief_d            = 30;
round_relief_pitch        = 52;
bridge_strap_w           = 28;
bridge_strap_t           = 12;
bridge_strap_len         = 118;
strap_screw_d            = 4.2;
lower_motor_shelf_t      = 12;
lower_motor_shelf_w      = 118;
lower_motor_shelf_d      = 46;
motor_station_z           = 95;      // scaled station closer to outlet while preserving guide length      // motor cluster sits near outlet section of 300mm tube
active_contact_zone_len   = 115;      // embedded motor/contact zone; rest remains guide tube
outlet_service_len        = 70;
mount_45_pitch           = 45;
mount_45_hole_d          = 5.5;
mount_45_boss_d          = 16;
mount_45_pad_w           = 82;
mount_45_pad_h           = 82;
mount_45_pad_t           = 12;
front_ring_t             = 18;
front_ring_extra_r       = 28;
front_ring_z             = motor_station_z + 32;
top_bridge_w             = 132;
top_bridge_d             = 42;
top_bridge_t             = 18;
lower_cradle_w           = 118;
lower_cradle_d           = 42;
lower_cradle_t           = 16;
four_screw_tab_w         = 58;
four_screw_tab_h         = 72;
four_screw_tab_t         = 12;
four_screw_tab_pitch_x   = 34;
four_screw_tab_pitch_z   = 42;
four_screw_tab_hole_d    = 5.0;

// Embedded motor pocket around short tube
motor_center_r            = inner_r + motor_d/2 - contact_sink_safe;
pocket_tangent_w          = motor_len + 38;   // scaled pocket wraps more of 6354 body   // wider photo-like motor pocket blended into tube
pocket_z_len              = motor_d + 36;    // taller pocket/end-plate envelope
pocket_radial_depth       = short_tube_wall + motor_d + 32;
pocket_corner_r           = 10;
inner_relief_t            = 5;

// Clamp / saddle
saddle_back_t             = 14;
saddle_side_t             = 10;
saddle_z_margin           = 14;
end_clamp_t               = 12;
end_clamp_margin          = 16;
end_clamp_center_hole_d   = 24;
end_hole_d                = 5.5;
end_hole_pitch            = mount_45_pitch;
end_slot_extra            = 4;

// One-end 45x45 mount, offset to rear side of tube
main_mount_pitch          = mount_45_pitch;
main_mount_hole_d         = 5.5;
main_mount_pad_w          = 96;
main_mount_pad_h          = 96;
main_mount_pad_t          = 14;
main_mount_y              = tube_outer_r + motor_d + 30;
main_mount_z              = -short_tube_len/2 - 18;
main_mount_center_hole_d  = 14;

// Reinforcement only; protective shield removed per owner v1.2b
rib_t                     = 14;
rib_w                     = 24;
rib_extra                 = 34;
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


module integrated_motor_pocket_body() {
  // Photo-reference monocoque: orange body grows from the tube wall into three motor pockets.
  for (a=[-90,30,150]) rotate([0,0,a]) {
    hull() {
      translate([0, tube_outer_r + 4, 0])
        cube([pocket_tangent_w*0.72, 12, pocket_z_len*0.72], center=true);
      translate([0, motor_center_r + motor_d/2 + 8, 0])
        cube([pocket_tangent_w, 18, pocket_z_len], center=true);
    }

    // End pressure plates with four screw bosses, visually close to the photo.
    for (sx=[-1,1]) {
      translate([sx*(motor_len/2+end_clamp_t/2), motor_center_r + motor_d/2 + 9, 0])
        difference() {
          cube([end_clamp_t+4, 20, motor_d+24], center=true);
          for (zz=[-end_hole_pitch/2, end_hole_pitch/2])
            translate([0, 0, zz]) rotate([90,0,0]) cylinder(d=end_hole_d, h=24, center=true);
        }
    }

    // Triangular-looking ribs from tube to motor pocket.
    for (sx=[-1,1])
      translate([sx*(pocket_tangent_w/2 + rib_w/3), tube_outer_r + rib_t/2, 0])
        cube([rib_w, rib_t, pocket_z_len + 2*rib_extra], center=true);
  }
}




module four_hole_45_pattern_holes(depth=20) {
  if (show_45x45_4holes)
    for (x=[-mount_45_pitch/2, mount_45_pitch/2])
      for (z=[-mount_45_pitch/2, mount_45_pitch/2])
        translate([x,0,z]) rotate([90,0,0]) cylinder(d=mount_45_hole_d, h=depth, center=true);
}

module four_hole_45_bosses() {
  if (show_45x45_4holes)
    for (a=[-90,30,150]) rotate([0,0,a])
      for (x=[-mount_45_pitch/2, mount_45_pitch/2])
        for (z=[-mount_45_pitch/2, mount_45_pitch/2])
          translate([x, motor_center_r + motor_d/2 + photo_side_plate_t + 8, z])
            rotate([90,0,0]) cylinder(d=mount_45_boss_d, h=mount_45_pad_t, center=true);
}

module four_hole_45_service_pad() {
  if (show_45x45_4holes)
    for (a=[-90,30,150]) rotate([0,0,a])
      translate([0, motor_center_r + motor_d/2 + photo_side_plate_t + 6, 0])
        difference() {
          cube([mount_45_pad_w, mount_45_pad_t, mount_45_pad_h], center=true);
          four_hole_45_pattern_holes(mount_45_pad_t + 3);
          rotate([90,0,0]) cylinder(d=motor_d + 2*rotor_clearance_min, h=mount_45_pad_t+4, center=true);
        }
}


module front_annular_ring_photo2() {
  if (show_front_annular_ring)
    translate([0,0,front_ring_z])
      difference() {
        cylinder(h=front_ring_t, r=tube_outer_r + front_ring_extra_r, center=true);
        cylinder(h=front_ring_t+2, r=inner_r, center=true);
        // three outside relief windows similar to the photo, not motor-axis holes.
        for (a=[-90,30,150]) rotate([0,0,a])
          translate([0, tube_outer_r + front_ring_extra_r*0.55, 0])
            rotate([90,0,0]) cylinder(d=round_relief_d, h=front_ring_extra_r+10, center=true);
      }
}

module top_bridge_motor_cradle_photo2() {
  if (show_top_bridge_cradle)
    translate([0,0,motor_station_z]) rotate([0,0,-90]) {
      // top motor is captured by a thick bridge over the tube, like the pink reference.
      translate([0, motor_center_r + motor_d/2 + 14, 0])
        difference() {
          cube([top_bridge_w, top_bridge_d, top_bridge_t], center=true);
          rotate([0,90,0]) cylinder(d=motor_d + 2*rotor_clearance_min, h=top_bridge_w+2, center=true);
          for (x=[-top_bridge_w/3, top_bridge_w/3])
            translate([x,0,0]) cylinder(d=strap_screw_d, h=top_bridge_t+2, center=true);
        }
      // back risers tying top bridge into tube body.
      for (x=[-top_bridge_w/2+16, top_bridge_w/2-16])
        translate([x, motor_center_r + motor_d/2 + 2, -top_bridge_t])
          cube([18, 28, 42], center=true);
    }
}

module lower_twin_cradles_photo2() {
  if (show_lower_twin_cradles)
    translate([0,0,motor_station_z])
      for (a=[30,150]) rotate([0,0,a])
        translate([0, motor_center_r + motor_d/2 + 8, -motor_d/2 - 14])
          difference() {
            cube([lower_cradle_w, lower_cradle_d, lower_cradle_t], center=true);
            for (x=[-lower_cradle_w/3, lower_cradle_w/3])
              translate([x,0,0]) cylinder(d=strap_screw_d, h=lower_cradle_t+2, center=true);
          }
}

module four_screw_side_tabs_photo2() {
  if (show_four_screw_tabs)
    translate([0,0,motor_station_z])
      for (a=[30,150]) rotate([0,0,a])
        translate([0, motor_center_r + motor_d/2 + four_screw_tab_t/2 + 28, 0])
          difference() {
            cube([four_screw_tab_w, four_screw_tab_t, four_screw_tab_h], center=true);
            for (x=[-four_screw_tab_pitch_x/2, four_screw_tab_pitch_x/2])
              for (z=[-four_screw_tab_pitch_z/2, four_screw_tab_pitch_z/2])
                translate([x,0,z]) rotate([90,0,0]) cylinder(d=four_screw_tab_hole_d, h=four_screw_tab_t+2, center=true);
          }
}

module photo_side_plate() {
  if (show_photo_side_plates)
    for (a=[-90,30,150]) rotate([0,0,a])
      translate([0, motor_center_r + motor_d/2 + photo_side_plate_t/2 + 4, 0])
        difference() {
          // Photo-like orange cheek plate integrated into tube body.
          cube([photo_side_plate_w, photo_side_plate_t, photo_side_plate_h], center=true);
          if (show_round_relief_holes)
            for (z=[-round_relief_pitch/2, round_relief_pitch/2])
              translate([0, 0, z]) rotate([90,0,0])
                cylinder(d=round_relief_d, h=photo_side_plate_t+2, center=true);
          // 45x45 four-hole mount pattern for motor/end-plate service.
          four_hole_45_pattern_holes(photo_side_plate_t + 3);
          // center motor can clearance
          rotate([90,0,0]) cylinder(d=motor_d + 2*rotor_clearance_min, h=photo_side_plate_t+3, center=true);
        }
}

module bridge_strap() {
  if (show_bridge_straps)
    for (a=[-90,30,150]) rotate([0,0,a]) {
      translate([0, motor_center_r + motor_d/2 + 16, motor_d/2 + 12])
        difference() {
          cube([bridge_strap_len, bridge_strap_w, bridge_strap_t], center=true);
          for (x=[-bridge_strap_len/3, 0, bridge_strap_len/3])
            translate([x,0,0]) cylinder(d=strap_screw_d, h=bridge_strap_t+2, center=true);
        }
    }
}

module lower_motor_shelf() {
  if (show_lower_motor_shelf)
    for (a=[-90,30,150]) rotate([0,0,a])
      translate([0, motor_center_r + motor_d/2 + lower_motor_shelf_d/2 - 6, -motor_d/2 - lower_motor_shelf_t/2 - 5])
        cube([lower_motor_shelf_w, lower_motor_shelf_d, lower_motor_shelf_t], center=true);
}

module wire_channel_cut() {
  if (show_wire_channels)
    for (a=[-90,30,150]) rotate([0,0,a])
      translate([0, motor_center_r + motor_d/2 + saddle_back_t + wire_channel_h/2, -motor_d/2 - 11])
        cube([wire_channel_len, wire_channel_h, wire_channel_w], center=true);
}

module tool_access_cut() {
  if (show_tool_access)
    for (a=[-90,30,150]) rotate([0,0,a])
      for (sx=[-1,1])
        translate([sx*tool_access_offset, motor_center_r + motor_d/2 + 23, 0])
          rotate([90,0,0]) cylinder(d=tool_access_d, h=38, center=true);
}

module rotor_clearance_envelope() {
  if (show_rotor_clearance)
    for (a=[-90,30,150]) rotate([0,0,a])
      color([0.2,0.9,1.0,0.18]) translate([0,motor_center_r,0]) rotate([0,90,0])
        cylinder(d=motor_d + 2*rotor_clearance_min, h=motor_len + 4, center=true);
}

module service_split_marker() {
  // visual seam marker only: suggests where a split clamp / removable cap can be defined later.
  color([0.05,0.05,0.05,0.20])
    for (a=[-90,30,150]) rotate([0,0,a])
      translate([0, motor_center_r + motor_d/2 + 19, 0])
        cube([pocket_tangent_w + 8, split_service_gap, pocket_z_len + 10], center=true);
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

      translate([0,0,motor_station_z]) if (integrated_monocoque) integrated_motor_pocket_body();
      translate([0,0,motor_station_z]) {
        photo_side_plate();
        four_hole_45_bosses();
        four_hole_45_service_pad();
        bridge_strap();
        lower_motor_shelf();
      }

      // integrated reinforcements around the embedded pockets
      translate([0,0,motor_station_z]) for (a=[-90,30,150]) rotate([0,0,a]) {
        for (z=[-pocket_z_len/2-rib_w/2, pocket_z_len/2+rib_w/2])
          translate([0, tube_outer_r + rib_t/2, z]) cube([pocket_tangent_w+2*rib_extra, rib_t, rib_w], center=true);
        for (x=[-pocket_tangent_w/2-rib_w/2, pocket_tangent_w/2+rib_w/2])
          translate([x, tube_outer_r + rib_t/2, 0]) cube([rib_w, rib_t, pocket_z_len+2*rib_extra], center=true);
      }
    }

    translate([0,0,motor_station_z]) {
      for (a=[-90,30,150]) rotate([0,0,a]) pocket_cut();
      for (a=[-90,30,150]) rotate([0,0,a]) inner_relief_cut();
      wire_channel_cut();
      tool_access_cut();
    }
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
  // v1.2k: motors are embedded from outside wall near outlet; no center-axis insertion.
  translate([0,0,motor_station_z])
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
  color([1.0,0.50,0.62,1]) front_annular_ring_photo2();
  color([1.0,0.50,0.62,1]) top_bridge_motor_cradle_photo2();
  color([1.0,0.50,0.62,1]) lower_twin_cradles_photo2();
  color([1.0,0.50,0.62,1]) four_screw_side_tabs_photo2();
  translate([0,0,motor_station_z]) {
    rotor_clearance_envelope();
    service_split_marker();
  }
  if (show_ball_path) ball_path_envelope();
  launch_axis_arrow();
}

// v1.2c: tilt the whole embedded three-motor launch station for direct upward firing.
rotate([launch_tilt_deg, 0, 0]) tilted_launch_cluster();

// ---------- Notes ----------
// v1.2d rolls/flips the embedded three-motor station 90deg for direct upward launch.
// Launch direction is the three-motor resultant force vector; tube axis is tilted with the motor cluster.
