// P0 single-ball football launcher outer-rotor assembly placeholder v10 (parametric)
// Units: mm
// Purpose: parameterized concept model for clearance / geometry review.
// Current frozen branch:
// - short 63-series outer-rotor motors, default 6354
// - bottom-face mounted only
// - central launch ring / barrel
// - 3 shell-contact cutouts
// - non-star interpretation
// - ring ears + stubs + link plates + outer mount plates
// - selectable outer frame support mode: radial side plates or triangular bracket

$fn = 96;

// =====================
// Adjustable parameters
// =====================
ball_d = 220;
motor_series = "6354";       // "6354" | "6360" | "6374"
motor_body_d = 63;
motor_shaft_d = 10;
motor_shaft_len = 14;
rubber_t = 2.0;
contact_band_h = 22;
preload = 4;
ring_clearance = 16;
ring_wall = 10;
ring_h = 56;
cutout_w = 52;
cutout_extra = 12;
residual_web_t = 14;
head_z = 620;
carrier_d_margin = 150;
base_l = 1000;
base_w = 800;
base_h = 60;
mount_plate_w = 72;
mount_plate_t = 8;
mount_post_sep = 40;
mount_post_h = 56;
mount_base_w = 88;
mount_base_d = 82;
mount_base_t = 10;
brace_len = 34;
brace_t = 8;
use_ring_ears = true;
ear_w = 34;
ear_l = 36;
ear_t = 12;
ear_hole_d = 6.6;
frame_stub_l = 70;
frame_stub_w = 22;
frame_stub_t = 10;
link_plate_w = 26;
link_plate_t = 8;
link_hole_d = 6.6;
outer_plate_w = 64;
outer_plate_h = 72;
outer_plate_t = 8;
outer_plate_hole_dx = 34;
outer_plate_hole_dz = 40;
outer_plate_hole_d = 6.6;
frame_support_mode = "triangular_bracket";   // "radial_plate" | "triangular_bracket"
head_to_frame_gap = 26;      // nominal spacing from outer mount plate to frame-side support
side_plate_w = 120;
side_plate_h = 180;
side_plate_t = 8;
side_plate_hole_dx = 34;
side_plate_hole_dz = 40;
side_plate_hole_d = 6.6;
side_plate_leg = 70;
tri_bracket_span = 110;
tri_bracket_h = 120;
tri_bracket_t = 8;
tri_bracket_hole_d = 6.6;

// =====================
// Derived values / presets
// =====================
function motor_len_for(series) =
  series == "6374" ? 74 :
  series == "6360" ? 60 :
  53.5;

motor_body_len = motor_len_for(motor_series);
ball_r = ball_d/2;
motor_r = motor_body_d/2;
contact_r = motor_r + rubber_t;
ring_id = ball_d + ring_clearance;
ring_od = ring_id + 2 * ring_wall;
axis_r = ring_od/2 + motor_r - 8;
carrier_d = ring_od + carrier_d_margin;

// =====================
// Core modules
// =====================
module football(){
  color("white") sphere(d=ball_d);
}

module motor_63_outer_rotor(){
  color("#c7cdd4") cylinder(h=motor_body_len, d=motor_body_d, center=true);
  color("#4b5563") cylinder(h=motor_body_len*0.56, d=motor_body_d + 2*rubber_t, center=true);
  color([0.20,0.20,0.20,0.65]) cylinder(h=contact_band_h, d=motor_body_d + 2*rubber_t + 0.6, center=true);
  color("#1d4ed8") {
    translate([0,0, motor_body_len/2-2.5]) cylinder(h=5, d=motor_body_d+5, center=true);
    translate([0,0,-motor_body_len/2+2.5]) cylinder(h=5, d=motor_body_d+5, center=true);
  }
  color("#d1d5db") {
    translate([0,0, motor_body_len/2 + motor_shaft_len/2]) cylinder(h=motor_shaft_len, d=motor_shaft_d, center=true);
    translate([0,0,-motor_body_len/2 - motor_shaft_len/2 + 2]) cylinder(h=motor_shaft_len-4, d=motor_shaft_d, center=true);
  }
}

module bottom_face_mount(){
  color("#9ca3af") {
    translate([0,0,-motor_body_len/2 - mount_plate_t/2 - 2])
      cube([mount_plate_w, mount_plate_w, mount_plate_t], center=true);

    translate([0,-mount_post_sep/2,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h/2])
      cube([18,18,mount_post_h], center=true);
    translate([0, mount_post_sep/2,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h/2])
      cube([18,18,mount_post_h], center=true);

    hull() {
      translate([0,-mount_post_sep/2,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h + 8]) cube([18,18,brace_t], center=true);
      translate([-brace_len/2,0,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h - mount_base_t/2 + 4]) cube([brace_t,mount_base_d,brace_t], center=true);
    }
    hull() {
      translate([0, mount_post_sep/2,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h + 8]) cube([18,18,brace_t], center=true);
      translate([ brace_len/2,0,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h - mount_base_t/2 + 4]) cube([brace_t,mount_base_d,brace_t], center=true);
    }
  }

  color("#7c2d12")
    translate([0,0,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h - mount_base_t/2])
      cube([mount_base_w, mount_base_d, mount_base_t], center=true);
}

module motor_module(){
  motor_63_outer_rotor();
  bottom_face_mount();
}

module cutout_slot(){
  hull(){
    translate([-cutout_w/2 + 10, 0, 0]) cylinder(h=ring_h+6, d=20, center=true);
    translate([ cutout_w/2 - 10, 0, 0]) cylinder(h=ring_h+6, d=20, center=true);
    cube([cutout_w - 20, motor_body_d + cutout_extra, ring_h+6], center=true);
  }
}

module support_ear(){
  difference(){
    hull(){
      translate([0,0,0]) cube([ear_l, ear_w, ear_t], center=true);
      translate([ear_l/2 + 8,0,0]) cylinder(h=ear_t, d=ear_w, center=true);
    }
    translate([ear_l/2 + 8,0,0]) cylinder(h=ear_t+2, d=ear_hole_d, center=true);
  }
}

module frame_stub(){
  color([0.45,0.48,0.55,0.85])
    cube([frame_stub_l, frame_stub_w, frame_stub_t], center=true);
}

module head_link_plate(){
  difference(){
    hull(){
      translate([-18,0,0]) cube([36,link_plate_w,link_plate_t], center=true);
      translate([ 22,0,0]) cube([44,link_plate_w,link_plate_t], center=true);
    }
    translate([-10,0,0]) cylinder(h=link_plate_t+2, d=link_hole_d, center=true);
    translate([ 18,0,0]) cylinder(h=link_plate_t+2, d=link_hole_d, center=true);
  }
}

module outer_mount_plate(){
  difference(){
    cube([outer_plate_t, outer_plate_w, outer_plate_h], center=true);
    for(y=[-outer_plate_hole_dx/2, outer_plate_hole_dx/2])
      for(z=[-outer_plate_hole_dz/2, outer_plate_hole_dz/2])
        translate([0,y,z]) rotate([0,90,0]) cylinder(h=outer_plate_t+2, d=outer_plate_hole_d, center=true);
  }
}

module side_support_plate(){
  difference(){
    hull(){
      cube([side_plate_t, side_plate_w, side_plate_h], center=true);
      translate([side_plate_leg/2,0,-side_plate_h/4]) cube([side_plate_t, side_plate_w*0.7, side_plate_h*0.5], center=true);
    }
    for(y=[-side_plate_hole_dx/2, side_plate_hole_dx/2])
      for(z=[-side_plate_hole_dz/2, side_plate_hole_dz/2])
        translate([0,y,z]) rotate([0,90,0]) cylinder(h=side_plate_t+2, d=side_plate_hole_d, center=true);
  }
}

module triangular_support_bracket(){
  difference(){
    hull(){
      translate([0,0,tri_bracket_h/2 - 14]) cube([tri_bracket_t, tri_bracket_span, 28], center=true);
      translate([0,-tri_bracket_span/2 + 18,-tri_bracket_h/2 + 16]) cube([tri_bracket_t, 36, 32], center=true);
      translate([0, tri_bracket_span/2 - 18,-tri_bracket_h/2 + 16]) cube([tri_bracket_t, 36, 32], center=true);
    }
    translate([0,0,tri_bracket_h/2 - 14]) rotate([0,90,0]) cylinder(h=tri_bracket_t+2, d=tri_bracket_hole_d, center=true);
    translate([0,-tri_bracket_span/2 + 18,-tri_bracket_h/2 + 16]) rotate([0,90,0]) cylinder(h=tri_bracket_t+2, d=tri_bracket_hole_d, center=true);
    translate([0, tri_bracket_span/2 - 18,-tri_bracket_h/2 + 16]) rotate([0,90,0]) cylinder(h=tri_bracket_t+2, d=tri_bracket_hole_d, center=true);
  }
}

module ring_with_three_cutouts_and_ears(){
  color([0.87,0.89,0.93,0.35])
  difference(){
    cylinder(h=ring_h, d=ring_od, center=true);
    cylinder(h=ring_h+2, d=ring_id, center=true);

    for(a=[90,210,330]) {
      rotate([0,0,a])
        translate([ring_od/2 - cutout_w/2 + 8, 0, 0])
          cutout_slot();
    }
  }

  color([0.76,0.79,0.84,0.45])
    for(a=[30,150,270])
      rotate([0,0,a])
        translate([ring_od/2 - ring_wall/2 - 4, 0, 0])
          cube([residual_web_t, 40, ring_h], center=true);

  if (use_ring_ears) {
    color([0.70,0.73,0.80,0.75])
      for(a=[30,150,270]) {
        rotate([0,0,a]) {
          translate([ring_od/2 + ear_l/2 - 2, 0, 0]) support_ear();
          translate([ring_od/2 + ear_l + frame_stub_l/2 + 6, 0, 0]) frame_stub();
        }
      }
  }
}

module placed_motor(az=0){
  rotate([0,0,az])
    translate([axis_r,0,0])
      motor_module();
}

module contact_zone_visual(){
  color([0.95,0.30,0.30,0.18])
    intersection(){
      sphere(d=ball_d + preload*2);
      cylinder(h=ring_h+10, d=ring_id-8, center=true);
    }
}

// =====================
// Base / carrier visuals
// =====================
module base_frame(){
  color("#334155") union(){
    translate([0,0,base_h/2]) cube([base_l,base_w,base_h],center=true);
    translate([0,0,base_h+40]) cube([base_l*0.72,40,80],center=true);
    translate([0, base_w/2-30, 360]) cube([base_l*0.82,40,620],center=true);
    translate([0,-base_w/2+30, 360]) cube([base_l*0.82,40,620],center=true);
    translate([-base_l/2+40,0,360]) cube([40,base_w,620],center=true);
    translate([ base_l/2-40,0,360]) cube([40,base_w,620],center=true);
  }
}

module base_detail(){
  color("#475569") {
    for(x=[-320,0,320]) translate([x,0,105]) cube([42,760,42],center=true);
    for(y=[-300,0,300]) translate([0,y,115]) cube([880,36,36],center=true);
    translate([0,0,155]) rotate([0,0,33]) cube([960,28,32],center=true);
    translate([0,0,155]) rotate([0,0,-33]) cube([960,28,32],center=true);
    translate([0,145,92]) cube([420,260,24],center=true);
  }
}

module battery_and_control(){
  color("#111827") translate([0,120,125]) cube([360,220,120], center=true);
  color("#475569") translate([300,-260,500]) cube([260,160,120], center=true);
}

module head_carrier(){
  color("#64748b")
    translate([0,0,head_z]) rotate([90,0,0]) difference(){
      cylinder(h=24,d=carrier_d,center=true);
      cylinder(h=28,d=ring_od+40,center=true);
    }
}

module head_frame_links(){
  color([0.60,0.64,0.72,0.9])
    translate([0,0,head_z])
      for(a=[30,150,270])
        rotate([0,0,a])
          translate([ring_od/2 + ear_l + frame_stub_l + 26, 0, 0])
            head_link_plate();
}

module outer_head_mount_plates(){
  color([0.52,0.56,0.64,0.95])
    translate([0,0,head_z])
      for(a=[30,150,270])
        rotate([0,0,a])
          translate([ring_od/2 + ear_l + frame_stub_l + 62, 0, 0])
            outer_mount_plate();
}

module outer_frame_supports(){
  translate([0,0,head_z])
    for(a=[30,150,270])
      rotate([0,0,a])
        translate([ring_od/2 + ear_l + frame_stub_l + 62 + head_to_frame_gap, 0, 0])
          if (frame_support_mode == "triangular_bracket") {
            color([0.58,0.62,0.70,0.90]) triangular_support_bracket();
          } else {
            color([0.58,0.62,0.70,0.90]) side_support_plate();
          }
}

module output_marker(){
  color([0.96,0.62,0.04,0.32])
    translate([0,250,head_z]) rotate([90,0,0]) cylinder(h=90,d=170,center=true);
}

module assembly(){
  base_frame();
  base_detail();
  battery_and_control();
  head_carrier();
  head_frame_links();
  outer_head_mount_plates();
  outer_frame_supports();
  output_marker();

  translate([0,0,head_z]) {
    football();
    contact_zone_visual();
    ring_with_three_cutouts_and_ears();
    placed_motor(90);
    placed_motor(210);
    placed_motor(330);
  }
}

assembly();
