#include "feed_state.h"
#include "host_fault.h"
#include "host_state.h"

void launch_state_machine_step() {
  HostState* s = host_state_get();
  if (s->cmd.estop) {
    s->state = ESTOP;
    return;
  }
  if (host_fault_is_active() || feed_fault_active()) {
    s->state = FAULT;
    return;
  }

  switch (s->state) {
    case IDLE:
      if (s->cmd.baseRpm > 0) s->state = SPINUP;
      break;
    case SPINUP:
      if (feed_is_ready()) s->state = FEED_READY;
      break;
    case FEED_READY:
      if (s->cmd.fireRequest) {
        feed_request_one_ball();
        s->state = BALL_IN_POSITION;
      }
      break;
    case BALL_IN_POSITION:
      if (s->sensors.chamberReady) s->state = FIRE;
      break;
    case FIRE:
      if (s->sensors.exitDetected) s->state = RELOAD;
      break;
    case RELOAD:
      if (feed_is_ready()) {
        s->cmd.fireRequest = 0;
        s->state = SPINUP;
      }
      break;
    case FAULT:
    case ESTOP:
    default:
      break;
  }
}
