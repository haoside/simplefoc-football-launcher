#include "simplefoc_adapter.h"

static int g_targetRpm = 0;
static int g_actualRpm = 0;
static int g_busVoltage_x10 = 240;
static int g_phaseCurrent_x10 = 0;
static int g_temp_x10 = 250;
static int g_fault = 0;

void simplefoc_adapter_init(void) {
  g_targetRpm = 0;
  g_actualRpm = 0;
  g_fault = 0;
}

void simplefoc_adapter_set_target_rpm(int rpm) {
  g_targetRpm = rpm;
}

int simplefoc_adapter_get_actual_rpm(void) {
  if (g_actualRpm < g_targetRpm) g_actualRpm += 50;
  else if (g_actualRpm > g_targetRpm) g_actualRpm -= 50;
  return g_actualRpm;
}

int simplefoc_adapter_get_bus_voltage_x10(void) {
  return g_busVoltage_x10;
}

int simplefoc_adapter_get_phase_current_x10(void) {
  g_phaseCurrent_x10 = (g_targetRpm > 0) ? 30 : 0;
  return g_phaseCurrent_x10;
}

int simplefoc_adapter_get_temp_x10(void) {
  return g_temp_x10;
}

int simplefoc_adapter_has_fault(void) {
  return g_fault;
}
