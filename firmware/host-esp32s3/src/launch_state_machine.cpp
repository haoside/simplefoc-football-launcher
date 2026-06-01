#include "../../common/config.h"
#include "hal/host_hal.h"
#include "host_fault.h"
#include "host_state.h"

static int wheel_ready(int actual, int target) {
  const int tol = 80;
  int diff = actual - target;
  if (diff < 0) diff = -diff;
  return diff <= tol;
}

static int system_ready(const HostState* s) {
  return wheel_ready(s->wheel1.actualRpm, s->wheel1.targetRpm) &&
         wheel_ready(s->wheel2.actualRpm, s->wheel2.targetRpm) &&
         wheel_ready(s->wheel3.actualRpm, s->wheel3.targetRpm);
}

void launch_state_machine_step() {
  HostState* s = host_state_get();
  uint32_t now = host_hal_millis();

  if (s->cmd.estop) {
    s->state = ESTOP;
    return;
  }
  if (host_fault_is_active()) {
    s->state = FAULT;
    return;
  }

  switch (s->state) {
    case IDLE:
      if (s->cmd.baseRpm > 0) {
        s->state = SPINUP;
        s->stateEnterMs = now;
      }
      break;
    case SPINUP:
      if (s->sensors.ballLoaded && system_ready(s)) {
        s->state = READY;
        s->stateEnterMs = now;
      }
      break;
    case READY:
      if (!s->sensors.ballLoaded) {
        s->state = SPINUP;
        s->stateEnterMs = now;
      } else if (s->cmd.fireRequest) {
        host_hal_trigger_launch();
        s->state = FIRE;
        s->stateEnterMs = now;
      }
      break;
    case FIRE:
      s->cmd.fireRequest = 0;
      s->state = COOLDOWN;
      s->stateEnterMs = now;
      break;
    case COOLDOWN:
      if ((now - s->stateEnterMs) >= RELOAD_DELAY_MS) {
        s->state = s->cmd.baseRpm > 0 ? SPINUP : IDLE;
        s->stateEnterMs = now;
      }
      break;
    case FAULT:
    case ESTOP:
    default:
      break;
  }
}
