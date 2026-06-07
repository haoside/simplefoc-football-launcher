// P0 single-ball football launcher outer-rotor assembly placeholder v2
// Units: mm
// Concept model for geometry / clearance review only.
// Coordinate convention: X = left/right, Y = front/back, Z = vertical.
// Current frozen direction:
// - 3 short 63-series outer-rotor BLDC motors (6354 placeholder)
// - bottom-face mounted only
// - motors arranged around a central launch ring / barrel
// - outer cylindrical shells pass through three barrel wall cutouts to contact the ball
// - do NOT treat the motor axes as a star converging to one point
// - use a triangular relationship around the central ring for the 3 motor axes

$fn = 96;

// ---------------- Core parameters ----------------
ball_d = 220;
ball_r = ball_d/2;

motor_can_d = 63;
motor_can_r = motor_can_d/2;
motor_len = 53.5;         // 6354 placeholder
endcap_t = 5;
shaft_d = 10;
shaft_len = 14;
rubber_t = 2.0;
contact_r = motor_can_r + rubber_t;

preload = 4;
ring_wall = 10;
ring_id = ball_d + 16;
ring_od = ring_id + 2 * ring_wall;
ring_h = 56;

// radial placement around central ring
axis_r = ring_od/2 + motor_can_r - 8;
head_z = 620;

base_l = 1000;
base_w = 800;
base_h = 60;
mount_plate_w = 120;
mount_plate_t = 8;
mount_plate_h = 92;

// ---------------- Helpers ----------------
module ball(){
  color("white") sphere(d=ball_d);
}

module rotor_motor_6354(){
  // local axis = +Z, rotor can centered at origin
  color("#c7cdd4") cylinder(h=motor_len, d=motor_can_d, center=true);
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

module bottom_face_mount(){
  // simplified bottom-face-only support; support comes from the lower end of the motor
  color("#9ca3af") {
    translate([0,0,-motor_len/2 - 10]) cube([72,72,8], center=true);
    translate([0,-20,-motor_len/2 - 42]) cube([18,40,56], center=true);
    translate([0, 20,-motor_len/2 - 42]) cube([18,40,56], center=true);
  }
  color("#7c2d12") {
    translate([0,0,-motor_len/2 - 74]) cube([88,82,10], center=true);
  }
}

module one_motor_module(){
  rotor_motor_6354();
  bottom_face_mount();
}

module placed_motor(az=0, tilt=0){
  // distribute the 3 motors around the ring; slight local yaw gives a triangular axis relationship
  rotate([0,0,az])
    translate([axis_r,0,0])
      rotate([0, tilt, 0])
        one_motor_module();
}

module launch_ring_with_cutouts(){
  color([0.87,0.89,0.93,0.35])
  difference(){
    translate([0,0,0]) cylinder(h=ring_h, d=ring_od, center=true);
    translate([0,0,0]) cylinder(h=ring_h+2, d=ring_id, center=true);

    // three radial cutouts for outer shell contact windows
    for(a=[90,210,330]) {
      rotate([0,0,a])
        translate([ring_od/2 - 18, 0, 0])
          cube([52, motor_can_d + 12, ring_h + 6], center=true);
    }
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
    translate([0,145,92]) cube([420,260,24],center=true);
  }
}

module battery_and_control(){
  color("#111827") translate([0,120,125]) cube([360,220,120], center=true);
  color("#475569") translate([300,-260,500]) cube([260,160,120], center=true);
}

module push_handle(){
  color("#334155") union(){
    translate([0,455,760]) rotate([90,0,90]) cylinder(h=650,d=28,center=true);
    translate([-325,410,520]) cylinder(h=260,d=24,center=false);
    translate([ 325,410,520]) cylinder(h=260,d=24,center=false);
  }
}

module simple_head_carrier(){
  color("#64748b") {
    translate([0,0,head_z]) rotate([90,0,0]) difference(){
      cylinder(h=24,d=ring_od+150,center=true);
      cylinder(h=28,d=ring_od+40,center=true);
    }
  }
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
  simple_head_carrier();
  front_output_marker();

  translate([0,0,head_z]) {
    ball();
    launch_ring_with_cutouts();

    // use 3 positions around the ring; avoid center-converging visual language
    placed_motor(90, 0);
    placed_motor(210, 0);
    placed_motor(330, 0);
  }
}

assembly();
