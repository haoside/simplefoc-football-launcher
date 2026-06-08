// P0 single-ball football launcher outer-rotor assembly placeholder v5 (parametric)
// Units: mm
// Purpose: parameterized concept model for clearance / geometry review.
// Frozen concept:
// 1) 3 short 63-series outer-rotor motors around central launch ring
// 2) motors are bottom-face mounted only
// 3) ring / barrel has 3 cutouts so outer cylindrical shells can pass through and touch the ball
// 4) do NOT read the axis relationship as a star converging to one center point

$fn = 96;

// =====================
// Adjustable parameters
// =====================
ball_d = 220;                 // size-5 football nominal
motor_series = "6354";        // "6354" | "6360" | "6374"
motor_body_d = 63;            // 63-series outer rotor body diameter
motor_shaft_d = 10;
motor_shaft_len = 14;
rubber_t = 2.0;               // friction sleeve thickness on outer shell
contact_band_h = 22;          // visible shell-to-ball contact band height
preload = 4;                  // conceptual radial preload
ring_clearance = 16;          // ring ID oversize vs. ball
ring_wall = 10;               // barrel/ring wall thickness
ring_h = 56;                  // axial height of ring
cutout_w = 52;                // radial cutout width
cutout_extra = 12;            // tangential allowance beyond motor diameter
residual_web_t = 14;          // remaining material web between cutouts
head_z = 620;                 // ball center height above base
carrier_d_margin = 150;       // support carrier margin beyond ring OD
base_l = 1000;
base_w = 800;
base_h = 60;
mount_plate_w = 72;           // motor bottom-face mount pad
mount_plate_t = 8;
mount_post_sep = 40;          // post separation for bottom-face support
mount_post_h = 56;
mount_base_w = 88;
mount_base_d = 82;
mount_base_t = 10;
brace_len = 34;
brace_t = 8;

// =====================
// Derived values / presets
// =====================
function motor_len_for(series) =
  series == "6374" ? 74 :
  series == "6360" ? 60 :
  53.5;   // default 6354

motor_body_len = motor_len_for(motor_series);
ball_r = ball_d/2;
motor_r = motor_body_d/2;
contact_r = motor_r + rubber_t;
ring_id = ball_d + ring_clearance;
ring_od = ring_id + 2 * ring_wall;
axis_r = ring_od/2 + motor_r - 8;      // conceptual placement around ring
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
  // more realistic bottom-face support with base plate + two posts + braces
  color("#9ca3af") {
    translate([0,0,-motor_body_len/2 - mount_plate_t/2 - 2])
      cube([mount_plate_w, mount_plate_w, mount_plate_t], center=true);

    translate([0,-mount_post_sep/2,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h/2])
      cube([18,18,mount_post_h], center=true);
    translate([0, mount_post_sep/2,-motor_body_len/2 - 2 - mount_plate_t - mount_post_h/2])
      cube([18,18,mount_post_h], center=true);

    // side braces
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
  // softened cutout shape approximation using hull of two cylinders + bridge
  hull(){
    translate([-cutout_w/2 + 10, 0, 0]) cylinder(h=ring_h+6, d=20, center=true);
    translate([ cutout_w/2 - 10, 0, 0]) cylinder(h=ring_h+6, d=20, center=true);
    cube([cutout_w - 20, motor_body_d + cutout_extra, ring_h+6], center=true);
  }
}

module ring_with_three_cutouts(){
  color([0.87,0.89,0.93,0.35])
  difference(){
    cylinder(h=ring_h, d=ring_od, center=true);
    cylinder(h=ring_h+2, d=ring_id, center=true);

    // three windows aligned with the three motor bodies
    for(a=[90,210,330]) {
      rotate([0,0,a])
        translate([ring_od/2 - cutout_w/2 + 8, 0, 0])
          cutout_slot();
    }
  }

  // residual webs kept between cutouts for barrel stiffness reading
  color([0.76,0.79,0.84,0.45])
    for(a=[30,150,270])
      rotate([0,0,a])
        translate([ring_od/2 - ring_wall/2 - 4, 0, 0])
          cube([residual_web_t, 40, ring_h], center=true);
}

module placed_motor(az=0){
  // distribute 3 motors around ring; no center-converging axis graphics here
  rotate([0,0,az])
    translate([axis_r,0,0])
      motor_module();
}

module contact_zone_visual(){
  // simple visual ball contact envelope at launcher head
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

module output_marker(){
  color([0.96,0.62,0.04,0.32])
    translate([0,250,head_z]) rotate([90,0,0]) cylinder(h=90,d=170,center=true);
}

// =====================
// Assembly
// =====================
module assembly(){
  base_frame();
  base_detail();
  battery_and_control();
  head_carrier();
  output_marker();

  translate([0,0,head_z]) {
    football();
    contact_zone_visual();
    ring_with_three_cutouts();
    placed_motor(90);
    placed_motor(210);
    placed_motor(330);
  }
}

assembly();
