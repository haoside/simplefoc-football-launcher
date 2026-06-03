// Guard Bracket v1
main_w = 220;
main_h = 40;
main_t = 4;
corner_r = 4;
mount_hole_d = 5.5;
guard_hole_d = 4.5;

module rounded_rect_2d(w,h,r){
  hull(){
    translate([-(w/2-r),-(h/2-r)]) circle(r=r,$fn=48);
    translate([ (w/2-r),-(h/2-r)]) circle(r=r,$fn=48);
    translate([-(w/2-r), (h/2-r)]) circle(r=r,$fn=48);
    translate([ (w/2-r), (h/2-r)]) circle(r=r,$fn=48);
  }
}

linear_extrude(height=main_t)
  difference(){
    rounded_rect_2d(main_w, main_h, corner_r);
    for (x=[-85,-35,35,85]) translate([x,0]) circle(d=mount_hole_d,$fn=36);
    for (x=[-60,0,60]) translate([x,10]) circle(d=guard_hole_d,$fn=36);
  }
