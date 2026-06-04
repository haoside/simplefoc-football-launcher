// P0 single-ball football launcher assembly placeholder v2
// Units: mm
// Layout model for clearance/design review, not final manufacturing CAD.
// Coordinate convention: X = left/right, Y = front/back, Z = vertical.

$fn = 96;

// Core parameters
ball_d = 220;
wheel_d = 110;       // P0-A default. Use 130 for P0-B candidate clearance check.
wheel_w = 45;
preload = 10;
wheel_r_from_center = ball_d/2 + wheel_d/2 - preload;
head_z = 620;        // ball center height from base top
base_l = 1000;
base_w = 800;
base_h = 60;

module ball(){
  color("white") sphere(d=ball_d);
}

module friction_wheel(){
  difference(){
    color("#111827") cylinder(h=wheel_w, d=wheel_d, center=true);
    cylinder(h=wheel_w+2, d=8, center=true);
  }
  color("#475569") cylinder(h=18, d=36, center=true);
}

module motor_6374(){
  // approximate 6374 envelope, axis along Y after placement
  color("#374151") union(){
    cylinder(h=74, d=63, center=false);
    translate([0,0,74]) cylinder(h=24, d=8, center=false);
  }
}

module motor_plate(){
  color("#94a3b8") difference(){
    cube([180,8,140], center=true); // X/Y/Z, plate is vertical
    rotate([90,0,0]) cylinder(h=12, d=24, center=true);
    for(x=[-35,35]) for(z=[-35,35]) translate([x,0,z]) rotate([90,0,0]) cylinder(h=12, d=5.5, center=true);
    hull(){
      translate([-50,0,0]) rotate([90,0,0]) cylinder(h=12,d=20,center=true);
      translate([ 50,0,0]) rotate([90,0,0]) cylinder(h=12,d=20,center=true);
    }
  }
}


module radial_adjust_visual(angle){
  // Radial slide plate between support arm and motor plate.
  rotate([0,0,angle]) translate([0, wheel_r_from_center+92, 0]) {
    color("#94a3b8") cube([220,10,80],center=true);
    color("#64748b") translate([0,-18,0]) cube([170,10,52],center=true);
    color("#111827") for(x=[-45,45]) for(z=[-22,22]) translate([x,-30,z]) rotate([90,0,0]) cylinder(h=22,d=6,center=true);
  }
}

module wheel_module(x,z,rot=0){
  translate([x,0,z]) {
    // Wheel axis along Y, wheel face visible from front.
    rotate([90,0,0]) friction_wheel();
    translate([0,70,0]) motor_plate();
    translate([0,116,0]) rotate([90,0,0]) motor_6374();
  }
}

module short_guide_tube(){
  // Based on short_guide_tube_v1.scad: L=200, ID=232, wall=4, flange OD=270.
  // Axis along X; placed as short manual-entry stabilizer, not a feed tube.
  color("#e5e7eb",0.72)
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
  // Transparent guard envelope with front output clearance.
  color("#7dd3fc",0.20)
  translate([0,18,head_z]) scale([1.05,0.58,1.05]) sphere(d=560);
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
  // wheels visual
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
    translate([-325,410,520]) rotate([0,0,0]) cylinder(h=260,d=24,center=false);
    translate([ 325,410,520]) rotate([0,0,0]) cylinder(h=260,d=24,center=false);
  }
}


module head_support_ring(){
  // Physical-looking support ring/triangular carrier for wheel modules.
  color("#64748b") {
    translate([0,8,head_z]) rotate([90,0,0]) difference(){
      cylinder(h=28,d=560,center=true);
      cylinder(h=32,d=380,center=true);
    }
    // three radial motor support arms in X/Z plane
    for(a=[90,-30,210]) {
      x = cos(a)*260;
      z = sin(a)*260;
      translate([x/2,10,head_z+z/2]) rotate([0,0,a]) cube([260,32,48],center=true);
    }
  }
}

module guide_tube_bracket(){
  color("#94a3b8") {
    translate([-280,0,head_z-150]) cube([180,28,280],center=true);
    translate([-240,0,head_z-285]) cube([260,36,42],center=true);
  }
}

module guard_supports(){
  color("#94a3b8") {
    translate([-260,-225,head_z+210]) cube([520,22,28],center=true);
    translate([ 260,-225,head_z+210]) cube([22,22,360],center=true);
    translate([-260,-225,head_z+210]) cube([22,22,360],center=true);
    translate([0,-238,head_z-35]) cube([650,18,22],center=true);
  }
}


module chassis_detail_v1(){
  // More realistic mobile-base details: cross rails, diagonal braces, wheel brackets, battery tray.
  color("#475569") {
    // cross rails on base
    for(x=[-320,0,320]) translate([x,0,105]) cube([42,760,42],center=true);
    for(y=[-300,0,300]) translate([0,y,115]) cube([880,36,36],center=true);
    // diagonal braces on top plane
    translate([0,0,155]) rotate([0,0,33]) cube([960,28,32],center=true);
    translate([0,0,155]) rotate([0,0,-33]) cube([960,28,32],center=true);
    // rear wheel fork plates
    for(x=[-380,380]) translate([x,455,150]) cube([34,24,260],center=true);
    // front caster fork plates
    for(x=[-380,380]) translate([x,-455,100]) cube([30,24,190],center=true);
    // battery tray under middle-rear
    translate([0,145,92]) cube([420,260,24],center=true);
    translate([-220,145,145]) cube([24,260,90],center=true);
    translate([ 220,145,145]) cube([24,260,90],center=true);
  }
}

module motor_gussets_v1(){
  // Visual gussets behind the three motor plates.
  color("#64748b") {
    for(a=[90,-30,210]) {
      x = cos(a)*260;
      z = head_z + sin(a)*260;
      translate([x,84,z-55]) rotate([0,0,a]) cube([110,18,92],center=true);
      translate([x,84,z+55]) rotate([0,0,a]) cube([110,18,92],center=true);
    }
  }
}

module guide_tube_fasteners_v1(){
  // Small fastener pads around guide tube flange.
  color("#334155") {
    for(a=[0:60:300]) translate([-360,0,head_z]) rotate([a,0,0]) translate([0,126,0]) sphere(d=14);
  }
}

module assembly(){
  base_frame();
  chassis_detail_v1();
  battery_and_control();
  push_handle();
  head_support_ring();
  guide_tube_bracket();
  guide_tube_fasteners_v1();
  motor_gussets_v1();
  guard_supports();

  // launcher head
  translate([0,0,head_z]) {
    ball();
    radial_adjust_visual(0);
    radial_adjust_visual(120);
    radial_adjust_visual(240);
    // wheel positions in the vertical X/Z plane: 12:00, 4:00, 8:00
    wheel_module(0,  wheel_r_from_center, 0);      // wheel1 @ 12:00
    wheel_module( wheel_r_from_center*0.866, -wheel_r_from_center*0.5, 0); // wheel2 @ 4:00
    wheel_module(-wheel_r_from_center*0.866, -wheel_r_from_center*0.5, 0); // wheel3 @ 8:00
  }

  // manual short guide entry from left into launcher head
  translate([-360,0,head_z]) short_guide_tube();
  pc_guard_envelope();

  // simple output direction marker / window zone
  color("#f59e0b",0.35) translate([330,0,head_z]) rotate([0,90,0]) cylinder(h=80,d=170,center=true);
}

assembly();
