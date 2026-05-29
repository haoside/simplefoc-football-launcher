#pragma once

#include <stdint.h>
#include "../../common/protocol.h"

typedef struct {
  uint8_t nodeId;
  int16_t targetRpm;
  int16_t actualRpm;
  uint16_t busVoltage_x10;
  uint16_t phaseCurrent_x10;
  int16_t temp_x10;
  uint8_t enabled;
  uint8_t faultCode;
  uint8_t state;
} MotorNodeState;

MotorNodeState* node_state_get(void);
