#include "app_config.h"
#include "hal/host_hal.h"
#include "host_state.h"
#include <stdio.h>

extern void host_can_control_tick(void);
extern void host_can_poll_rx(void);
extern void launch_state_machine_step(void);
extern void telemetry_publish(void);

int main() {
  HostState* s = host_state_get();
  printf("%s boot\n", HOST_FIRMWARE_NAME);

  host_hal_init();
  host_hal_can_init();

  s->cmd.baseRpm = 2100;
  s->cmd.deltaRpm = 250;
  s->cmd.spinMode = STRAIGHT;
  s->cmd.fireRequest = 0;
  s->stateEnterMs = host_hal_millis();

  while (1) {
    s->cmd.estop = (uint8_t)host_hal_estop_active();
    s->sensors.ballLoaded = (uint8_t)host_hal_sensor_ball_loaded();
    host_can_poll_rx();
    launch_state_machine_step();
    host_can_control_tick();
    telemetry_publish();
    break; // placeholder for task loop
  }
  return 0;
}
