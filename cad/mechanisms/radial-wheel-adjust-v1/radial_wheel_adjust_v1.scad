// Radial wheel adjustment mechanism v1
// Units: mm
// Purpose: support 110/130mm wheel swap and 5~15mm ball preload tuning.

$fn = 64;

base_w = 220;
base_h = 80;
base_t = 8;
slide_w = 170;
slide_h = 52;
slide_t = 8;
slot_len = 70;
slot_w = 10;
lock_hole_d = 6;
scale_marks = true;

module slot(len=slot_len, w=slot_w, h=base_t+2){
  hull(){
    translate([-len/2+w/2,0,0]) cylinder(h=h,d=w,center=true);
    translate([ len/2-w/2,0,0]) cylinder(h=h,d=w,center=true);
  }
}

module radial_adjust_base(){
  color("#94a3b8") difference(){
    cube([base_w,base_t,base_h],center=true);
    // two long radial slots
    translate([0,0,22]) rotate([90,0,0]) slot();
    translate([0,0,-22]) rotate([90,0,0]) slot();
  }
}

module radial_adjust_slider(){
  color("#64748b") difference(){
    translate([0,-12,0]) cube([slide_w,slide_t,slide_h],center=true);
    // motor shaft center clearance
    translate([0,-12,0]) rotate([90,0,0]) cylinder(h=slide_t+2,d=24,center=true);
    // provisional 6374 mounting holes
    for(x=[-35,35]) for(z=[-35,35])
      translate([x,-12,z]) rotate([90,0,0]) cylinder(h=slide_t+2,d=5.5,center=true);
  }
}

module locking_bolts(){
  color("#111827") for(x=[-45,45]) for(z=[-22,22])
    translate([x,-22,z]) rotate([90,0,0]) cylinder(h=24,d=lock_hole_d,center=true);
}

module preload_scale(){
  if (scale_marks) color("#111827") {
    for(i=[-20:10:20]) translate([i, -18, 42]) cube([1.5,2,10],center=true);
    translate([-35,-18,55]) linear_extrude(height=1) text("-20", size=8, halign="center");
    translate([  0,-18,55]) linear_extrude(height=1) text("0", size=8, halign="center");
    translate([ 35,-18,55]) linear_extrude(height=1) text("+20", size=8, halign="center");
  }
}

module radial_wheel_adjust(){
  radial_adjust_base();
  radial_adjust_slider();
  locking_bolts();
  preload_scale();
}

radial_wheel_adjust();
