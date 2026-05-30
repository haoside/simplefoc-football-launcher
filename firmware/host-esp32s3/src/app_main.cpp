#include "app_config.h"
#include "feed_state.h"
#include "hal/host_hal.h"
#include "host_state.h"
#include <stdio.h>

extern void host_can_control_tick(void);
extern void host_can_poll_rx(void);
extern void launch_state_machine_step(void);

int main() {
  HostState* s = host_state_get();
  printf("%s boot\n", HOST_FIRMWARE_NAME);

  host_hal_init();
  host_hal_can_init();
  feed_state_reset();

  s->cmd.baseRpm = 1200;
  s->cmd.ux = 0.0f;
  s->cmd.uy = 0.0f;
  s->cmd.fireRequest = 0;

  while (1) {
    s->cmd.estop = (uint8_t)host_hal_estop_active();
    feed_state_step();
    host_can_poll_rx();
    launch_state_machine_step();
    host_can_control_tick();
    break; // placeholder for task loop
  }
  return 0;
}
