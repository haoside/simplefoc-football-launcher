#include "../hal/node_hal_bg431b.h"
#include "../include/node_state.h"

void bg_node_telemetry_refresh(void) {
  BgNodeState* s = bg_node_state_get();
  s->actualRpm = (int16_t)bg_hal_get_actual_rpm();
  s->busVoltage_x10 = bg_hal_get_bus_voltage_x10();
  s->phaseCurrent_x10 = bg_hal_get_phase_current_x10();
  s->temp_x10 = bg_hal_get_temp_x10();
}
