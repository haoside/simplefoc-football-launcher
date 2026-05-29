#include "app_config.h"
#include "host_state.h"
#include <stdio.h>

extern void host_can_control_tick(void);
extern void launch_state_machine_step(void);

int main() {
  HostState* s = host_state_get();
  printf("%s boot\n", HOST_FIRMWARE_NAME);
  printf("host init: gpio / can / sensors\n");

  s->cmd.baseRpm = 1200;
  s->cmd.ux = 0.0f;
  s->cmd.uy = 0.0f;
  s->sensors.tubeBallPresent = 1;
  s->sensors.chamberReady = 0;

  while (1) {
    launch_state_machine_step();
    host_can_control_tick();
    break; // placeholder for RTOS/task loop
  }
  return 0;
}
