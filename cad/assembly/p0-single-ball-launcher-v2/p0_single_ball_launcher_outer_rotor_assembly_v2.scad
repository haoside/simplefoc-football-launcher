// P0 single-ball football launcher outer-rotor assembly placeholder v2
// Units: mm
// Concept model for geometry / clearance review only.
// Coordinate convention: X = left/right, Y = front/back, Z = vertical.
// This revision switches from 3 parallel friction wheels to 3 tilted 6374 outer-rotor cans
// whose cylindrical outer shell surfaces directly contact the football.

$fn = 96;

// ---------------- Core parameters ----------------
ball_d = 220;
ball_r = ball_d/2;

motor_can_d = 63;
motor_can_r = motor_can_d/2;
motor_len = 74;
endcap_t = 5;
shaft_d = 8;
shaft_len = 16;
rubber_t = 2.0;
contact_r = motor_can_r + rubber_t;

preload = 4;
axis_tilt_deg = 28;                 // each motor axis tilts inward toward ball center
axis_r = ball_r + contact_r - preload;

head_z = 620;                       // ball center height from base top
base_l = 1000;
base_w = 800;
base_h = 60;

frame_post_h = 470;
mount_plate_w = 160;
mount_plate_t = 8;
mount_plate_h = 140;

// ---------------- Helpers ----------------
module ball(){
  color("white") sphere(d=ball_d);
}

module rotor_motor_6374(){
  // local axis = +Z, rotor can centered at origin
  color("#c7cdd4") cylinder(h=motor_len, d=motor_can_d, center=true);

  // thin friction sleeve on working contact band only
  color("#4b5563") cylinder(h=motor_len*0.56, d=motor_can_d + 2*rubber_t, center=true);

  color("#1d4ed8") {
    translate([0,0, motor_len/2-endcap_t/2]) cylinder(h=endcap_t, d=motor_can_d+5, center=true);
    translate([0,0,-motor_len/2+endcap_t/2]) cylinder(h=endcap_t, d=motor_can_d+5, center=true);
  }

  color("#d1d5db") {
    translate([0,0, motor_len/2 + shaft_len/2]) cylinder(h=shaft_len, d=shaft_d, center=true);
    translate([0,0,-motor_len/2 - shaft_len/2 + 2]) cylinder(h=shaft_len-4, d=shaft_d, center=true);
  }
}

module stator_mount_bracket(){
  // fixed bracket visually attached away from ball contact zone
  color("#9ca3af") {
    translate([0,0,-motor_len*0.38]) cube([mount_plate_w, mount_plate_t, mount_plate_h], center=true);
    translate([0,-34,-78]) cube([92,60,12], center=true);
  }
  color("#7c2d12") {
    hull(){
      translate([-46,-24,-74]) cube([12,12,120], center=true);
      translate([-70,-52,-150]) cube([12,12,14], center=true);
    }
    hull(){
      translate([ 46,-24,-74]) cube([12,12,120], center=true);
      translate([ 70,-52,-150]) cube([12,12,14], center=true);
    }
  }
}

module one_motor_module(){
  rotor_motor_6374();
  stator_mount_bracket();
}

module placed_motor(az=0){
  // motors distributed 120° in XY around ball center, then tilted inward
  rotate([0,0,az])
    translate([axis_r,0,0])
      rotate([0,axis_tilt_deg,0])
        one_motor_module();
}

module recessed_guide_ring(){
  // guide only, intentionally not the main contact surface
  inner_d = ball_d + 30;
  outer_d = inner_d + 12;
  h = 40;
  color([0.87,0.89,0.93,0.35])
  difference(){
    translate([0,0,-12]) cylinder(h=h, d=outer_d, center=true);
    translate([0,0,-12]) cylinder(h=h+2, d=inner_d, center=true);
    // front discharge opening
    translate([0, outer_d*0.40, 0]) cube([outer_d*1.8, outer_d*0.95, h+6], center=true);
  }
}

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

module chassis_detail_v1(){
  color("#475569") {
    for(x=[-320,0,320]) translate([x,0,105]) cube([42,760,42],center=true);
    for(y=[-300,0,300]) translate([0,y,115]) cube([880,36,36],center=true);
    translate([0,0,155]) rotate([0,0,33]) cube([960,28,32],center=true);
    translate([0,0,155]) rotate([0,0,-33]) cube([960,28,32],center=true);
    for(x=[-380,380]) translate([x,455,150]) cube([34,24,260],center=true);
    for(x=[-380,380]) translate([x,-455,100]) cube([30,24,190],center=true);
    translate([0,145,92]) cube([420,260,24],center=true);
    translate([-220,145,145]) cube([24,260,90],center=true);
    translate([ 220,145,145]) cube([24,260,90],center=true);
  }
  color("#111827") {
    translate([-base_l/2+120, base_w/2+35,150]) rotate([90,0,0]) cylinder(h=70,d=300,center=true);
    translate([ base_l/2-120, base_w/2+35,150]) rotate([90,0,0]) cylinder(h=70,d=300,center=true);
    translate([-base_l/2+120,-base_w/2-25,100]) rotate([90,0,0]) cylinder(h=50,d=200,center=true);
    translate([ base_l/2-120,-base_w/2-25,100]) rotate([90,0,0]) cylinder(h=50,d=200,center=true);
  }
}

module battery_and_control(){
  color("#111827") translate([0,120,125]) cube([360,220,120], center=true);
  color("#475569") translate([300,-260,500]) cube([260,160,120], center=true);
  color("red") translate([430,-350,550]) sphere(d=55);
}

module push_handle(){
  color("#334155") union(){
    translate([0,455,760]) rotate([90,0,90]) cylinder(h=650,d=28,center=true);
    translate([-325,410,520]) cylinder(h=260,d=24,center=false);
    translate([ 325,410,520]) cylinder(h=260,d=24,center=false);
  }
}

module head_support_ring(){
  color("#64748b") {
    translate([0,0,head_z]) rotate([90,0,0]) difference(){
      cylinder(h=28,d=540,center=true);
      cylinder(h=32,d=360,center=true);
    }
    for(a=[0,120,240]) {
      rotate([0,0,a]) translate([160,-26,head_z-120]) cube([180,36,18],center=true);
    }
  }
}

module pc_guard_envelope(){
  color([0.49,0.83,0.99,0.16])
    translate([0,16,head_z+5]) scale([1.0,0.62,0.96]) sphere(d=560);
}

module front_output_marker(){
  color([0.96,0.62,0.04,0.32])
    translate([0,250,head_z]) rotate([90,0,0]) cylinder(h=90,d=170,center=true);
}

module assembly(){
  base_frame();
  chassis_detail_v1();
  battery_and_control();
  push_handle();
  head_support_ring();
  pc_guard_envelope();
  front_output_marker();

  translate([0,0,head_z]) {
    ball();
    recessed_guide_ring();
    placed_motor(0);
    placed_motor(120);
    placed_motor(240);
  }
}

assembly();
