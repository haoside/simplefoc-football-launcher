#include "node_hal_bg431b.h"
#include <stdio.h>

static int g_targetRpm = 0;
static int g_actualRpm = 0;
static uint32_t g_ms = 0;

void bg_hal_init(void) {
  printf("bg_hal_init\n");
}

uint32_t bg_hal_millis(void) {
  g_ms += 20;
  return g_ms;
}

int bg_hal_can_init(void) {
  printf("bg_hal_can_init\n");
  return 0;
}

int bg_hal_can_send(const BgCanFrame* frame) {
  printf("bg_hal_can_send id=0x%03X dlc=%u\n", frame->canId, frame->dlc);
  return 0;
}

int bg_hal_can_recv(BgCanFrame* frame) {
  (void)frame;
  return -1;
}

void bg_hal_motor_enable(int enable) {
  printf("bg_hal_motor_enable=%d\n", enable);
}

void bg_hal_set_target_rpm(int rpm) {
  g_targetRpm = rpm;
}

int bg_hal_get_actual_rpm(void) {
  if (g_actualRpm < g_targetRpm) g_actualRpm += 50;
  else if (g_actualRpm > g_targetRpm) g_actualRpm -= 50;
  return g_actualRpm;
}

uint16_t bg_hal_get_bus_voltage_x10(void) { return 240; }
uint16_t bg_hal_get_phase_current_x10(void) { return (g_targetRpm > 0) ? 30 : 0; }
int16_t bg_hal_get_temp_x10(void) { return 260; }
int bg_hal_driver_fault_active(void) { return 0; }
