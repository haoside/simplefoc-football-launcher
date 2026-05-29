#include "node_state.h"
#include "simplefoc_adapter.h"

int check_driver_fault() {
  MotorNodeState* s = node_state_get();
  if (simplefoc_adapter_has_fault()) {
    s->faultCode = FAULT_OVERCURRENT;
    s->state = STATE_FAULT;
    s->enabled = 0;
    return -1;
  }
  return 0;
}
