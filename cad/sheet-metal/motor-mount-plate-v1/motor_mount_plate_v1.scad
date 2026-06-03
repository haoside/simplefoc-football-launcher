// Motor Mount Plate v1
// 2D/flat plate draft for CNC / waterjet / laser reference
// Units: mm

plate_w = 180;
plate_h = 140;
plate_t = 8;
corner_r = 8;
center_hole_d = 24;
motor_hole_d = 5.5;
frame_hole_d = 6.0;
slot_w = 20;
slot_len = 120;

// Default provisional motor pattern around center.
// Must be re-checked with actual 6374 motor drawing after purchase.
motor_dx = 35;
motor_dy = 35;
frame_dx = 65;
frame_dy = 45;

module rounded_rect_2d(w, h, r) {
    hull() {
        translate([-(w/2-r), -(h/2-r)]) circle(r=r, $fn=64);
        translate([ (w/2-r), -(h/2-r)]) circle(r=r, $fn=64);
        translate([-(w/2-r),  (h/2-r)]) circle(r=r, $fn=64);
        translate([ (w/2-r),  (h/2-r)]) circle(r=r, $fn=64);
    }
}

module plate_2d() {
    difference() {
        rounded_rect_2d(plate_w, plate_h, corner_r);

        // center shaft hole
        circle(d=center_hole_d, $fn=96);

        // provisional motor mounting holes
        for (x=[-motor_dx, motor_dx])
            for (y=[-motor_dy, motor_dy])
                translate([x, y]) circle(d=motor_hole_d, $fn=48);

        // frame mounting holes
        for (x=[-frame_dx, frame_dx])
            for (y=[-frame_dy, frame_dy])
                translate([x, y]) circle(d=frame_hole_d, $fn=48);

        // horizontal adjustment slot region
        hull() {
            translate([-(slot_len/2-slot_w/2), 0]) circle(d=slot_w, $fn=48);
            translate([ (slot_len/2-slot_w/2), 0]) circle(d=slot_w, $fn=48);
        }
    }
}

linear_extrude(height=plate_t)
    plate_2d();
