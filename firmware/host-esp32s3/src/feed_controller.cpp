#include "host_state.h"
#include <stdio.h>

void feed_request_one_ball() {
  printf("feed: request one ball\n");
}

int feed_is_ready() {
  HostState* s = host_state_get();
  return s->sensors.tubeBallPresent ? 1 : 0;
}
