// Side support plate concept v1
// Isolated concept file for reviewing outer mount plate transition into side support plates.

$fn = 64;

plate_w = 120;
plate_h = 180;
plate_t = 8;
hole_dx = 34;
hole_dz = 40;
hole_d = 6.6;
brace_leg = 70;

module side_support_plate(){
  difference(){
    hull(){
      cube([plate_t, plate_w, plate_h], center=true);
      translate([brace_leg/2,0,-plate_h/4]) cube([plate_t, plate_w*0.7, plate_h*0.5], center=true);
    }

    for(y=[-hole_dx/2, hole_dx/2])
      for(z=[-hole_dz/2, hole_dz/2])
        translate([0,y,z]) rotate([0,90,0]) cylinder(h=plate_t+2, d=hole_d, center=true);
  }
}

color([0.55,0.58,0.66,0.95]) side_support_plate();
