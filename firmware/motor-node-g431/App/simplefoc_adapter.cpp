#include "simplefoc_adapter.h"
#include "hal/node_hal.h"
#include "sensor_reader.h"

static int g_targetRpm = 0;
static int g_pwmEnabled = 0;

void simplefoc_adapter_init(void) {
  g_targetRpm = 0;
  g_pwmEnabled = 0;
  node_hal_pwm_enable(0);
}

void simplefoc_adapter_set_target_rpm(int rpm) {
  g_targetRpm = rpm;
  g_pwmEnabled = (rpm > 0) ? 1 : 0;
  node_hal_pwm_enable(g_pwmEnabled);
}

int simplefoc_adapter_get_actual_rpm(void) {
  if (!g_pwmEnabled) return 0;
  return read_hall_rpm();
}

int simplefoc_adapter_get_bus_voltage_x10(void) {
  return (int)node_hal_read_vbus_x10();
}

int simplefoc_adapter_get_phase_current_x10(void) {
  return (int)node_hal_read_current_x10();
}

int simplefoc_adapter_get_temp_x10(void) {
  return (int)node_hal_read_temp_x10();
}

int simplefoc_adapter_has_fault(void) {
  return node_hal_driver_fault_active();
}
