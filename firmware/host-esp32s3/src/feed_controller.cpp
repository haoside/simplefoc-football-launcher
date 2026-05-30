#include "hal/host_hal.h"
#include "host_state.h"

void feed_request_one_ball() {
  host_hal_feed_request();
}

int feed_is_ready() {
  HostState* s = host_state_get();
  s->sensors.tubeBallPresent = (uint8_t)host_hal_sensor_tube_ball_present();
  return s->sensors.tubeBallPresent ? 1 : 0;
}
