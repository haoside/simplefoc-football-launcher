#include "hal/node_hal.h"

int read_hall_state(void) {
  int a = node_hal_read_hall_a() ? 1 : 0;
  int b = node_hal_read_hall_b() ? 1 : 0;
  int c = node_hal_read_hall_c() ? 1 : 0;
  return (a << 2) | (b << 1) | c;
}

int read_hall_rpm(void) {
  static int simulatedRpm = 0;
  int hallState = read_hall_state();
  (void)hallState;
  // TODO: replace with timer-capture / edge-period computation
  if (simulatedRpm < 3000) simulatedRpm += 20;
  return simulatedRpm;
}
