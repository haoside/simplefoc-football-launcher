#include "app_config.h"
#include "../../common/config.h"
#include <stdio.h>

int main() {
  printf("%s boot\n", HOST_FIRMWARE_NAME);
  // TODO: init GPIO / CAN / sensors / feed actuator
  // TODO: enter launch state machine loop
  return 0;
}
