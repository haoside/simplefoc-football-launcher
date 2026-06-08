// Launcher ring focus model v2
// Isolated head-only concept for reviewing ring cutouts, remaining webs,
// and ring-to-support connection ears.

$fn = 96;

ball_d = 220;
ring_clearance = 16;
ring_wall = 10;
ring_h = 56;
cutout_w = 52;
cutout_extra = 12;
motor_body_d = 63;
residual_web_t = 14;
ear_w = 34;
ear_l = 36;
ear_t = 12;
ear_hole_d = 6.6;    // M6 clearance-style visual

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

module support_ear(){
  difference(){
    hull(){
      translate([0,0,0]) cube([ear_l, ear_w, ear_t], center=true);
      translate([ear_l/2 + 8,0,0]) cylinder(h=ear_t, d=ear_w, center=true);
    }
    translate([ear_l/2 + 8,0,0]) cylinder(h=ear_t+2, d=ear_hole_d, center=true);
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

  // residual webs between cutouts
  color([0.65,0.70,0.78,0.55])
    for(a=[30,150,270])
      rotate([0,0,a])
        translate([ring_od/2 - ring_wall/2 - 4, 0, 0])
          cube([residual_web_t, 40, ring_h], center=true);

  // three support ears around the outer ring
  color([0.70,0.73,0.80,0.75])
    for(a=[30,150,270])
      rotate([0,0,a])
        translate([ring_od/2 + ear_l/2 - 2, 0, 0])
          support_ear();
}

football();
ring();
