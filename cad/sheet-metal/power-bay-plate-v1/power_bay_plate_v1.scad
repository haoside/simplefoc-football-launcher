plate_w = 320;
plate_h = 220;
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
    for (x=[-135,135]) for (y=[-90,90]) translate([x,y]) circle(d=6.0,$fn=36);
    // power block holes provisional
    for (x=[-60,60]) for (y=[20,70]) translate([x,y]) circle(d=5.0,$fn=30);
    // accessory holes provisional
    for (x=[90,120]) for (y=[-20,20,60]) translate([x,y]) circle(d=4.5,$fn=30);
  }
