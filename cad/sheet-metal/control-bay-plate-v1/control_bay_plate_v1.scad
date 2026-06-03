plate_w = 250;
plate_h = 180;
plate_t = 4;
corner_r = 6;

module rr(w,h,r){
  hull(){
    translate([-(w/2-r),-(h/2-r)]) circle(r=r,$fn=48);
    translate([ (w/2-r),-(h/2-r)]) circle(r=r,$fn=48);
    translate([-(w/2-r), (h/2-r)]) circle(r=r,$fn=48);
    translate([ (w/2-r), (h/2-r)]) circle(r=r,$fn=48);
  }
}

linear_extrude(height=plate_t)
  difference(){
    rr(plate_w, plate_h, corner_r);
    for (x=[-105,105]) for (y=[-70,70]) translate([x,y]) circle(d=5.5,$fn=36);
    // ESP32-S3 provisional
    for (x=[-85,-45]) for (y=[20,50]) translate([x,y]) circle(d=3.2,$fn=30);
    // 3 x B-G431B-ESC1 provisional zones
    for (x=[20,65,110]) for (y=[25,-25]) translate([x-80,y]) circle(d=4.0,$fn=30);
  }
