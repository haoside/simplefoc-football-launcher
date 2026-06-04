// Friction wheel placeholder v1
// Units: mm
// Supports 110mm / 130mm variants for P0-A/P0-B layout.

$fn = 128;
wheel_d = 110;       // set to 130 for P0-B candidate
wheel_w = 45;
bore_d = 8;
hub_d = 36;
hub_w = 18;

module friction_wheel(d=wheel_d, w=wheel_w) {
  difference() {
    union() {
      color("#111827") cylinder(h=w, d=d, center=true);
      color("#475569") cylinder(h=hub_w, d=hub_d, center=true);
    }
    cylinder(h=w+2, d=bore_d, center=true);
  }
}

friction_wheel();
