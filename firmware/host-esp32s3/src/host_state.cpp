#include "host_state.h"

static HostState g_hostState = {
  IDLE,
  {0, 250, STRAIGHT, 0, 0},
  {0},
  {0, 0, 0, 0},
  {0, 0, 0, 0},
  {0, 0, 0, 0},
  {0, 0, 0, 0},
  {0, 20, 50, 0, 0},
  0,
};

HostState* host_state_get() {
  return &g_hostState;
}
