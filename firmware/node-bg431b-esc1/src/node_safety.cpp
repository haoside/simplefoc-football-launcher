#include "../hal/node_hal_bg431b.h"
#include "../include/board_config.h"
#include "../include/node_state.h"
#include "../../common/protocol.h"

void bg_node_safety_step(void) {
  BgNodeState* s = bg_node_state_get();
  if (bg_hal_driver_fault_active()) {
    s->faultCode = FAULT_OVERCURRENT;
    s->state = STATE_FAULT;
    s->enabled = 0;
    bg_hal_motor_enable(0);
    return;
  }
  if (s->phaseCurrent_x10 > (NODE_CURRENT_LIMIT_PEAK_A * 10)) {
    s->faultCode = FAULT_OVERCURRENT;
    s->state = STATE_FAULT;
    s->enabled = 0;
    bg_hal_motor_enable(0);
    return;
  }
  if ((s->temp_x10 / 10) > NODE_TEMP_LIMIT_C) {
    s->faultCode = FAULT_OVERTEMP;
    s->state = STATE_FAULT;
    s->enabled = 0;
    bg_hal_motor_enable(0);
  }
}
