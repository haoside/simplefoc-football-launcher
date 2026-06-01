#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  const char* name;
  int baseRpm;
  int deltaRpm;
  int launchAngleDeg;
  int targetDistanceM;
  int lateralOffsetDm;
  uint8_t spinMode;
} ShotPreset;

const ShotPreset* host_get_shot_presets(int* count);

#ifdef __cplusplus
}
#endif
