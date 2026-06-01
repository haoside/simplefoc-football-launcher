#include "../include/node_debug.h"
#include "../include/node_profile.h"
#include "../include/node_state.h"
#include <stdio.h>

void bg_node_debug_boot(void) {
  const BgNodeProfile* p = bg_node_profile_get();
  printf("[BOOT] board=%s node=%s id=0x%02X dir=%d hall=%d\n",
         "B-G431B-ESC1",
         p->name,
         p->nodeId,
         p->motorDirection,
         p->hallPolarity);
}

void bg_node_debug_status(void) {
  BgNodeState* s = bg_node_state_get();
  printf("[STATUS] id=0x%02X state=%u en=%u target=%d actual=%d vbus=%.1fV current=%.1fA temp=%.1fC fault=%u\n",
         s->nodeId,
         s->state,
         s->enabled,
         s->targetRpm,
         s->actualRpm,
         s->busVoltage_x10 / 10.0f,
         s->phaseCurrent_x10 / 10.0f,
         s->temp_x10 / 10.0f,
         s->faultCode);
}

void bg_node_debug_fault(void) {
  BgNodeState* s = bg_node_state_get();
  if (s->faultCode == 0) return;
  printf("[FAULT] id=0x%02X state=%u fault=%u actual=%d current=%.1fA temp=%.1fC\n",
         s->nodeId,
         s->state,
         s->faultCode,
         s->actualRpm,
         s->phaseCurrent_x10 / 10.0f,
         s->temp_x10 / 10.0f);
}
