// Short Guide Tube v1
// Single-ball 3-wheel launcher
// Units: mm

$fn = 180;

length_total = 200;
inner_d = 232;
wall = 4;
outer_d = inner_d + wall * 2;
flare_len = 35;
flare_entry_d = 255;
flange_d = 270;
flange_t = 6;
hole_d = 5.5;
hole_count = 6;
hole_pcd = 252;

module bolt_holes() {
    for (i = [0:hole_count-1]) {
        angle = 360 / hole_count * i;
        translate([
            (hole_pcd/2) * cos(angle),
            (hole_pcd/2) * sin(angle),
            0
        ])
        cylinder(h = flange_t + 2, d = hole_d, center = false);
    }
}

module main_tube() {
    difference() {
        union() {
            // straight tube
            translate([0,0,flange_t])
                cylinder(h = length_total - flare_len, d = outer_d);

            // flare section
            translate([0,0,length_total - flare_len + flange_t])
                cylinder(h = flare_len, d1 = outer_d, d2 = flare_entry_d + wall * 2);

            // front flange
            cylinder(h = flange_t, d = flange_d);
        }

        // inner bore straight + flare
        union() {
            translate([0,0,flange_t-0.1])
                cylinder(h = length_total - flare_len + 0.2, d = inner_d);

            translate([0,0,length_total - flare_len + flange_t])
                cylinder(h = flare_len + 0.2, d1 = inner_d, d2 = flare_entry_d);

            bolt_holes();
        }
    }
}

main_tube();
