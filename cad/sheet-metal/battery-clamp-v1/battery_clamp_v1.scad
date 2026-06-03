plate_w = 260;
plate_h = 35;
plate_t = 4;

linear_extrude(height=plate_t)
  difference(){
    square([plate_w, plate_h], center=true);
    translate([-100,0]) circle(d=6.0,$fn=30);
    translate([ 100,0]) circle(d=6.0,$fn=30);
    hull(){
      translate([-54,0]) circle(d=12,$fn=30);
      translate([ 54,0]) circle(d=12,$fn=30);
    }
  }
