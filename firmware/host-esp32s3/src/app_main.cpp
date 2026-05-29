#include "app_config.h"
#include "../../common/config.h"
#include <stdio.h>

extern void host_can_control_tick(void);

int main() {
  printf("%s boot\n", HOST_FIRMWARE_NAME);
  printf("host init: gpio / can / sensors\n");
  while (1) {
    host_can_control_tick();
    break; // placeholder for RTOS/task loop
  }
  return 0;
}
