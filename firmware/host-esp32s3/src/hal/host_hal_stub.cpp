#include "host_hal.h"
#include <stdio.h>

void host_hal_init(void) {
  printf("host_hal_init\n");
}

void host_hal_delay_ms(uint32_t ms) {
  (void)ms;
}

uint32_t host_hal_millis(void) {
  return 0;
}

int host_hal_can_init(void) {
  printf("host_hal_can_init\n");
  return 0;
}

int host_hal_can_send(const HostCanFrame* frame) {
  printf("host_hal_can_send id=0x%03X dlc=%u\n", frame->canId, frame->dlc);
  return 0;
}

int host_hal_can_recv(HostCanFrame* frame) {
  (void)frame;
  return -1;
}

int host_hal_sensor_tube_ball_present(void) { return 0; }
int host_hal_sensor_chamber_ready(void) { return 0; }
int host_hal_sensor_exit_detected(void) { return 0; }
int host_hal_estop_active(void) { return 0; }

void host_hal_feed_request(void) {
  printf("host_hal_feed_request\n");
}

void host_hal_set_status_led(int on) {
  (void)on;
}

void host_hal_set_buzzer(int on) {
  (void)on;
}
