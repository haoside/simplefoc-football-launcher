#pragma once

#include <stdint.h>

typedef struct {
  const char* name;
  uint8_t nodeId;
  int motorDirection;
  int hallPolarity;
  int rpmMin;
  int rpmMax;
} BgNodeProfile;

const BgNodeProfile* bg_node_profile_get(void);
void bg_node_profile_select(uint8_t nodeId);
