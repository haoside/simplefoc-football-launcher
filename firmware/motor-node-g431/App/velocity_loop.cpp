#include "node_state.h"
#include "simplefoc_adapter.h"

void velocity_loop_step() {
  MotorNodeState* s = node_state_get();
  if (!s->enabled || s->state == STATE_ESTOP || s->state == STATE_FAULT) {
    simplefoc_adapter_set_target_rpm(0);
    s->actualRpm = simplefoc_adapter_get_actual_rpm();
    return;
  }

  simplefoc_adapter_set_target_rpm(s->targetRpm);
  s->actualRpm = simplefoc_adapter_get_actual_rpm();
  s->busVoltage_x10 = (uint16_t)simplefoc_adapter_get_bus_voltage_x10();
  s->phaseCurrent_x10 = (uint16_t)simplefoc_adapter_get_phase_current_x10();
  s->temp_x10 = (int16_t)simplefoc_adapter_get_temp_x10();

  if (simplefoc_adapter_has_fault()) {
    s->faultCode = FAULT_OVERCURRENT;
    s->state = STATE_FAULT;
    s->enabled = 0;
    return;
  }

  if (s->targetRpm > 0 && s->actualRpm < s->targetRpm - 100) {
    s->state = STATE_SPINUP;
  } else if (s->targetRpm > 0) {
    s->state = STATE_RUNNING;
  } else {
    s->state = STATE_IDLE;
  }
}
