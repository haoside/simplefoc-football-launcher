// Mobile base frame v1 placeholder
// Units: mm
// Football-field movable chassis envelope.

base_l = 1000;
base_w = 800;
rail = 40;
height = 60;
rear_wheel_d = 300;  // 10~12 inch pneumatic wheel placeholder
front_wheel_d = 200; // 8 inch caster placeholder

module rail_box(x,y,z){ cube([x,y,z], center=true); }

module mobile_base_frame(){
  color("#334155") union(){
    translate([0, base_w/2-rail/2, height/2]) rail_box(base_l, rail, height);
    translate([0,-base_w/2+rail/2, height/2]) rail_box(base_l, rail, height);
    translate([ base_l/2-rail/2,0,height/2]) rail_box(rail, base_w, height);
    translate([-base_l/2+rail/2,0,height/2]) rail_box(rail, base_w, height);
    translate([0,0,height/2]) rail_box(base_l*0.72, rail, height);
  }
  // wheels visual
  color("#111827") {
    translate([-base_l/2+120, base_w/2+30, rear_wheel_d/2]) rotate([90,0,0]) cylinder(h=70,d=rear_wheel_d,center=true);
    translate([ base_l/2-120, base_w/2+30, rear_wheel_d/2]) rotate([90,0,0]) cylinder(h=70,d=rear_wheel_d,center=true);
    translate([-base_l/2+120,-base_w/2-25, front_wheel_d/2]) rotate([90,0,0]) cylinder(h=50,d=front_wheel_d,center=true);
    translate([ base_l/2-120,-base_w/2-25, front_wheel_d/2]) rotate([90,0,0]) cylinder(h=50,d=front_wheel_d,center=true);
  }
}

mobile_base_frame();
