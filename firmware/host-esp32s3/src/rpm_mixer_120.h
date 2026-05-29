#pragma once

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

WheelRpm mix120deg(const RpmCommand& in, float kx, float ky);
