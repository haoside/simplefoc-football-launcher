#pragma once

#include <stdint.h>
#include "../../common/protocol.h"

typedef struct {
  uint8_t nodeId;
  uint8_t state;
  uint8_t enabled;
  uint8_t faultCode;
  int16_t targetRpm;
  int16_t actualRpm;
  uint16_t busVoltage_x10;
  uint16_t phaseCurrent_x10;
  int16_t temp_x10;
  uint32_t lastCommandMs;
} BgNodeState;

BgNodeState* bg_node_state_get(void);
void bg_node_state_reset(uint8_t nodeId);
