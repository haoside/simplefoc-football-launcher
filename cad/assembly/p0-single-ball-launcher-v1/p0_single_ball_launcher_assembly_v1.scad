// P0 single-ball football launcher assembly placeholder v1
// Units: mm
// This is a layout assembly for clearance/design review, not final manufacturing CAD.

$fn = 96;

// Core parameters
ball_d = 220;
wheel_d = 110;     // P0-A default. Test 130 for P0-B candidate.
wheel_w = 45;
preload = 10;
wheel_radius_from_center = ball_d/2 + wheel_d/2 - preload;

module ball(){ color("white") sphere(d=ball_d); }

module wheel(){
  difference(){
    color("#111827") cylinder(h=wheel_w, d=wheel_d, center=true);
    cylinder(h=wheel_w+2,d=8,center=true);
  }
}

module motor_placeholder(){
  color("#374151") union(){
    cylinder(h=74,d=63,center=false);
    translate([0,0,74]) cylinder(h=24,d=8,center=false);
  }
}

module motor_plate(){
  color("#94a3b8") difference(){
    cube([180,140,8],center=true);
    cylinder(h=10,d=24,center=true);
    for(x=[-35,35]) for(y=[-35,35]) translate([x,y,0]) cylinder(h=10,d=5.5,center=true);
  }
}

module wheel_module(angle){
  rotate([0,0,angle]) translate([0,wheel_radius_from_center,0]) {
    rotate([90,0,0]) wheel();
    translate([0,70,0]) rotate([90,0,0]) motor_plate();
    translate([0,150,-37]) rotate([90,0,0]) motor_placeholder();
  }
}

module short_guide_tube(){
  // Based on short_guide_tube_v1.scad: L=200, ID=232, wall=4, flange OD=270
  color("#e5e7eb",0.75)
  rotate([0,90,0]) difference(){
    union(){
      cylinder(h=165,d=240);
      translate([0,0,165]) cylinder(h=35,d1=240,d2=263);
      translate([0,0,-6]) cylinder(h=6,d=270);
    }
    translate([0,0,-8]) cylinder(h=210,d=232);
  }
}

module pc_guard_envelope(){
  color("#7dd3fc",0.22)
  translate([0,0,0]) scale([1.25,1.25,0.75]) sphere(d=520);
}

module base_frame(){
  color("#334155") {
    translate([0,0,-330]) cube([1000,800,60],center=true);
    translate([-380,430,-230]) rotate([90,0,0]) cylinder(h=70,d=300,center=true);
    translate([ 380,430,-230]) rotate([90,0,0]) cylinder(h=70,d=300,center=true);
    translate([-380,-430,-280]) rotate([90,0,0]) cylinder(h=50,d=200,center=true);
    translate([ 380,-430,-280]) rotate([90,0,0]) cylinder(h=50,d=200,center=true);
  }
}

module assembly(){
  base_frame();
  translate([0,0,40]) {
    ball();
    wheel_module(0);    // wheel1 @ 12:00
    wheel_module(120);  // wheel2 @ 4:00-ish in top view
    wheel_module(240);  // wheel3 @ 8:00-ish in top view
    translate([-315,0,0]) short_guide_tube();
    pc_guard_envelope();
  }
}

assembly();
