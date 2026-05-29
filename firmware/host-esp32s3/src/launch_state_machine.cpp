#include "host_state.h"

extern void feed_request_one_ball();
extern int feed_is_ready();

void launch_state_machine_step() {
  HostState* s = host_state_get();
  if (s->cmd.estop) {
    s->state = ESTOP;
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
      s->state = RELOAD;
      break;
    case RELOAD:
      s->cmd.fireRequest = 0;
      s->state = SPINUP;
      break;
    case FAULT:
    case ESTOP:
    default:
      break;
  }
}
