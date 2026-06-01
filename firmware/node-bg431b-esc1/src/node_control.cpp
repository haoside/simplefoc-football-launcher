#include "../hal/node_hal_bg431b.h"
#include "../include/board_config.h"
#include "../include/node_state.h"
#include "../../common/protocol.h"

static int clamp_rpm(int rpm) {
  if (rpm <= 0) return 0;
  if (rpm < NODE_RPM_MIN) return NODE_RPM_MIN;
  if (rpm > NODE_RPM_MAX) return NODE_RPM_MAX;
  return rpm;
}

void bg_node_control_step(void) {
  BgNodeState* s = bg_node_state_get();
  if (!s->enabled || s->state == STATE_FAULT || s->state == STATE_ESTOP) {
    bg_hal_set_target_rpm(0);
    bg_hal_motor_enable(0);
    if (s->state != STATE_FAULT && s->state != STATE_ESTOP) s->state = STATE_IDLE;
    return;
  }

  s->targetRpm = (int16_t)clamp_rpm(s->targetRpm);
  bg_hal_motor_enable(1);
  bg_hal_set_target_rpm(s->targetRpm);
  s->state = (s->actualRpm < (s->targetRpm - 100)) ? STATE_SPINUP : STATE_RUNNING;
}
