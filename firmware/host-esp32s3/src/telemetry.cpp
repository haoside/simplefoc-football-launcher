#include "feed_state.h"
#include "host_fault.h"
#include "host_state.h"
#include <stdio.h>

void telemetry_publish() {
  HostState* s = host_state_get();
  FeedControllerState* f = feed_state_get();
  printf(
    "telemetry state=%u baseRpm=%d tube=%u chamber=%u exit=%u feedState=%u feedFault=%u hostFault=%u\n",
    (unsigned)s->state,
    s->cmd.baseRpm,
    s->sensors.tubeBallPresent,
    s->sensors.chamberReady,
    s->sensors.exitDetected,
    (unsigned)f->state,
    (unsigned)s->telemetry.feedFaultReason,
    (unsigned)host_fault_code()
  );
}
