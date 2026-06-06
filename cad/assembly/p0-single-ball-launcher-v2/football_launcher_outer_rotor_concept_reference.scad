// Concept 3D model: 3x 6374 outer-rotor motors around a football
// Intent: outer rotor cylindrical shell directly contacts the ball.
// This is a geometry concept model for CAD refinement, not production-ready.

$fn = 96;

// ---------------- Parameters ----------------
ball_d = 220;              // football diameter (concept)
ball_r = ball_d / 2;

motor_can_d = 63;          // 6374 class outer rotor can diameter (concept)
motor_can_r = motor_can_d / 2;
motor_len = 74;
endcap_t = 5;
shaft_d = 8;
shaft_h = 10;
rubber_t = 2;              // thin friction sleeve
contact_r = motor_can_r + rubber_t;

preload = 4;               // radial preload into the ball
axis_tilt = 28;            // inward tilt toward ball center (deg)
base_z = -115;
mount_plate_t = 8;

// Distance from ball center to each motor axis
axis_offset = ball_r + contact_r - preload;

// ---------------- Helpers ----------------
module ball() {
    color([0.94,0.94,0.94])
        sphere(r = ball_r);
}

module rotor_can() {
    // local axis = +Z; cylindrical shell contacts ball near mid-body
    color([0.75,0.76,0.78])
        cylinder(h = motor_len, r = motor_can_r, center = true);

    // thin rubber sleeve on outer shell working zone
    color([0.42,0.42,0.42])
        cylinder(h = motor_len*0.58, r = motor_can_r + rubber_t, center = true);

    color([0.10,0.35,0.85]) {
        translate([0,0,motor_len/2 - endcap_t/2])
            cylinder(h = endcap_t, r = motor_can_r + 1.5, center = true);
        translate([0,0,-motor_len/2 + endcap_t/2])
            cylinder(h = endcap_t, r = motor_can_r + 1.5, center = true);
    }

    // shaft/top stub
    color([0.82,0.82,0.84])
        translate([0,0,motor_len/2 + shaft_h/2 - endcap_t/2])
            cylinder(h = shaft_h, r = shaft_d/2, center = true);
}

module stator_mount() {
    // simplified fixed bracket + base plate; kept away from contact zone
    color([0.65,0.12,0.12]) {
        translate([0,0,-motor_len*0.48])
            hull() {
                translate([-18,0,0]) cube([8,36,8], center=true);
                translate([-26,0,-55]) cube([12,44,8], center=true);
            }
        translate([-26,0,-72]) cube([46,54,8], center=true);
    }
}

module one_motor() {
    rotor_can();
    stator_mount();
}

module placed_motor(az=0) {
    // Position axis around the ball in XY plane, then tilt inward.
    rotate([0,0,az])
        translate([axis_offset, 0, 0])
            rotate([0, axis_tilt, 0])
                one_motor();
}

module guide_ring() {
    // recessed guide ring only, intentionally not the main contact surface
    ring_thick = 10;
    ring_h = 40;
    inner_r = ball_r + 18;
    outer_r = inner_r + ring_thick;
    color([0.85,0.85,0.88,0.35])
    difference() {
        translate([0,0,-10]) cylinder(h=ring_h, r=outer_r, center=true);
        translate([0,0,-10]) cylinder(h=ring_h+2, r=inner_r, center=true);
        // front opening for discharge
        translate([0,outer_r,0]) cube([outer_r*2, outer_r*1.4, ring_h+4], center=true);
    }
}

module base_frame() {
    color([0.12,0.12,0.12]) {
        translate([0,0,base_z]) cube([260,260,mount_plate_t], center=true);
        translate([0,0,base_z-18]) cube([220,220,6], center=true);
    }
}

// ---------------- Assembly ----------------
base_frame();
placed_motor(0);
placed_motor(120);
placed_motor(240);
guide_ring();
translate([0,0,0]) ball();
