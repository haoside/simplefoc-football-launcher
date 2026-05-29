#include "node_state.h"

static MotorNodeState g_state = {
  NODE_ID_WHEEL_A,
  0,
  0,
  240,
  0,
  250,
  0,
  FAULT_NONE,
  STATE_IDLE,
};

MotorNodeState* node_state_get(void) {
  return &g_state;
}
