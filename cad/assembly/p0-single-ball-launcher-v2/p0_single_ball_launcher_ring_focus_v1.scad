// Launcher ring focus model v1
// Isolated head-only concept for reviewing ring cutouts and remaining webs.

$fn = 96;

ball_d = 220;
ring_clearance = 16;
ring_wall = 10;
ring_h = 56;
cutout_w = 52;
cutout_extra = 12;
motor_body_d = 63;
residual_web_t = 14;

ring_id = ball_d + ring_clearance;
ring_od = ring_id + 2 * ring_wall;

module football(){
  color("white") sphere(d=ball_d);
}

module cutout_slot(){
  hull(){
    translate([-cutout_w/2 + 10, 0, 0]) cylinder(h=ring_h+6, d=20, center=true);
    translate([ cutout_w/2 - 10, 0, 0]) cylinder(h=ring_h+6, d=20, center=true);
    cube([cutout_w - 20, motor_body_d + cutout_extra, ring_h+6], center=true);
  }
}

module ring(){
  color([0.87,0.89,0.93,0.45])
  difference(){
    cylinder(h=ring_h, d=ring_od, center=true);
    cylinder(h=ring_h+2, d=ring_id, center=true);
    for(a=[90,210,330])
      rotate([0,0,a])
        translate([ring_od/2 - cutout_w/2 + 8, 0, 0])
          cutout_slot();
  }

  color([0.65,0.70,0.78,0.55])
    for(a=[30,150,270])
      rotate([0,0,a])
        translate([ring_od/2 - ring_wall/2 - 4, 0, 0])
          cube([residual_web_t, 40, ring_h], center=true);
}

football();
ring();
