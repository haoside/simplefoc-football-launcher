struct RpmCommand {
  float baseRpm;
  float ux;
  float uy;
};

struct WheelRpm {
  float a;
  float b;
  float c;
};

WheelRpm mix120deg(const RpmCommand& in, float kx, float ky) {
  WheelRpm out;
  out.a = in.baseRpm + kx * in.ux;
  out.b = in.baseRpm - 0.5f * kx * in.ux + 0.866f * ky * in.uy;
  out.c = in.baseRpm - 0.5f * kx * in.ux - 0.866f * ky * in.uy;
  return out;
}
