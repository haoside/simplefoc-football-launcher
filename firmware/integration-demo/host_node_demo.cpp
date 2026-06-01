#include "../common/protocol.h"
#include <stdio.h>
#include <stdint.h>

enum DemoSpinMode {
  DEMO_STRAIGHT = 0,
  DEMO_TOPSPIN = 1,
  DEMO_LEFT_CURVE = 2,
};

struct DemoWheel {
  uint8_t nodeId;
  int targetRpm;
  int actualRpm;
};

struct DemoHost {
  int baseRpm;
  int deltaRpm;
  DemoSpinMode spinMode;
  DemoWheel wheel1;
  DemoWheel wheel2;
  DemoWheel wheel3;
};

static int clamp_rpm(int rpm) {
  if (rpm < 0) return 0;
  if (rpm > 3000) return 3000;
  return rpm;
}

static void demo_apply_mixer(DemoHost* h) {
  int base = h->baseRpm;
  int d = h->deltaRpm;
  int w1 = base, w2 = base, w3 = base;

  switch (h->spinMode) {
    case DEMO_TOPSPIN:
      w1 = base + d;
      w2 = base - d / 2;
      w3 = base - d / 2;
      break;
    case DEMO_LEFT_CURVE:
      w1 = base;
      w2 = base - d;
      w3 = base + d;
      break;
    case DEMO_STRAIGHT:
    default:
      break;
  }

  h->wheel1.targetRpm = clamp_rpm(w1);
  h->wheel2.targetRpm = clamp_rpm(w2);
  h->wheel3.targetRpm = clamp_rpm(w3);
}

static void demo_send_set_rpm(uint8_t nodeId, int rpm) {
  printf("HOST -> node=0x%02X SET_RPM=%d\n", nodeId, rpm);
}

static void demo_node_step(DemoWheel* w) {
  if (w->actualRpm < w->targetRpm) w->actualRpm += 100;
  else if (w->actualRpm > w->targetRpm) w->actualRpm -= 100;
}

static void demo_report(const DemoHost* h, int tick) {
  printf("tick=%d spinMode=%d w1=%d/%d w2=%d/%d w3=%d/%d\n",
         tick,
         (int)h->spinMode,
         h->wheel1.actualRpm, h->wheel1.targetRpm,
         h->wheel2.actualRpm, h->wheel2.targetRpm,
         h->wheel3.actualRpm, h->wheel3.targetRpm);
}

int main() {
  DemoHost h = {
    2100,
    250,
    DEMO_STRAIGHT,
    {NODE_ID_WHEEL_A, 0, 0},
    {NODE_ID_WHEEL_B, 0, 0},
    {NODE_ID_WHEEL_C, 0, 0},
  };

  for (int tick = 0; tick < 12; ++tick) {
    if (tick == 4) h.spinMode = DEMO_TOPSPIN;
    if (tick == 8) h.spinMode = DEMO_LEFT_CURVE;

    demo_apply_mixer(&h);
    demo_send_set_rpm(h.wheel1.nodeId, h.wheel1.targetRpm);
    demo_send_set_rpm(h.wheel2.nodeId, h.wheel2.targetRpm);
    demo_send_set_rpm(h.wheel3.nodeId, h.wheel3.targetRpm);

    demo_node_step(&h.wheel1);
    demo_node_step(&h.wheel2);
    demo_node_step(&h.wheel3);
    demo_report(&h, tick);
  }

  return 0;
}
