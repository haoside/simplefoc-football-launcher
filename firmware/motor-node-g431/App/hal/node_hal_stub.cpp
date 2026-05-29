#include "node_hal.h"
#include <stdio.h>

void node_hal_init(void) {
  printf("node_hal_init\n");
}

uint32_t node_hal_millis(void) {
  return 0;
}

int node_hal_can_init(void) {
  printf("node_hal_can_init\n");
  return 0;
}

int node_hal_can_send(const NodeCanFrame* frame) {
  printf("node_hal_can_send id=0x%03X dlc=%u\n", frame->canId, frame->dlc);
  return 0;
}

int node_hal_can_recv(NodeCanFrame* frame) {
  (void)frame;
  return -1;
}

void node_hal_pwm_enable(int enable) {
  printf("node_hal_pwm_enable=%d\n", enable);
}

void node_hal_pwm_set_uvw(float u, float v, float w) {
  (void)u; (void)v; (void)w;
}

int node_hal_read_hall_a(void) { return 0; }
int node_hal_read_hall_b(void) { return 0; }
int node_hal_read_hall_c(void) { return 0; }

uint16_t node_hal_read_vbus_x10(void) { return 240; }
uint16_t node_hal_read_current_x10(void) { return 0; }
int16_t node_hal_read_temp_x10(void) { return 250; }
int node_hal_driver_fault_active(void) { return 0; }
