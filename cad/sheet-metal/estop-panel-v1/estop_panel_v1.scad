plate_w = 100;
plate_h = 80;
plate_t = 3;

linear_extrude(height=plate_t)
  difference(){
    square([plate_w, plate_h], center=true);
    circle(d=22.5,$fn=60);
    for (x=[-35,35]) for (y=[-25,25]) translate([x,y]) circle(d=5.0,$fn=30);
  }
