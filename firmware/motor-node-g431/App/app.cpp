#include "../Core/Inc/main.h"
#include "hal/node_hal.h"

extern void simplefoc_init();
extern void velocity_loop_step();
extern int check_driver_fault();
extern void node_comm_poll();

void app_init(void) {
  node_hal_init();
  node_hal_can_init();
  simplefoc_init();
}

void app_loop(void) {
  node_comm_poll();
  (void)check_driver_fault();
  velocity_loop_step();
}
