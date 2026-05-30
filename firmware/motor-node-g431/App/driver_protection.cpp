#include "hal/node_hal.h"
#include "node_state.h"
#include "simplefoc_adapter.h"

int check_driver_fault() {
  MotorNodeState* s = node_state_get();
  if (simplefoc_adapter_has_fault() || node_hal_driver_fault_active()) {
    s->faultCode = FAULT_OVERCURRENT;
    s->state = STATE_FAULT;
    s->enabled = 0;
    return -1;
  }
  return 0;
}
