#include "host_fault.h"
#include "host_state.h"
#include <stdio.h>

void telemetry_publish() {
  HostState* s = host_state_get();
  printf(
    "telemetry state=%u ballLoaded=%u spinMode=%u w1=%d/%d w2=%d/%d w3=%d/%d hostFault=%u\n",
    (unsigned)s->state,
    s->sensors.ballLoaded,
    s->cmd.spinMode,
    s->wheel1.actualRpm, s->wheel1.targetRpm,
    s->wheel2.actualRpm, s->wheel2.targetRpm,
    s->wheel3.actualRpm, s->wheel3.targetRpm,
    (unsigned)host_fault_code()
  );
}
