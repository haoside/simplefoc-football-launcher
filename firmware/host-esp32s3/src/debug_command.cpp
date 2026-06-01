#include "debug_command.h"
#include "host_fault.h"
#include "host_state.h"
#include "shot_presets.h"
#include <stdio.h>
#include <string.h>

static int parse_int(const char* s, int fallback) {
  int v = fallback;
  if (s) sscanf(s, "%d", &v);
  return v;
}

static void apply_preset_by_name(const char* name) {
  HostState* s = host_state_get();
  int count = 0;
  const ShotPreset* presets = host_get_shot_presets(&count);
  for (int i = 0; i < count; ++i) {
    if (strcmp(presets[i].name, name) == 0) {
      s->cmd.baseRpm = presets[i].baseRpm;
      s->cmd.deltaRpm = presets[i].deltaRpm;
      s->cmd.spinMode = presets[i].spinMode;
      s->debugOverride.enabled = 0;
      return;
    }
  }
}

void host_debug_apply_text_command(const char* line) {
  HostState* s = host_state_get();
  if (!line || !line[0]) return;

  if (strncmp(line, "preset ", 7) == 0) {
    apply_preset_by_name(line + 7);
    return;
  }
  if (strncmp(line, "set base ", 9) == 0) {
    s->cmd.baseRpm = parse_int(line + 9, s->cmd.baseRpm);
    return;
  }
  if (strncmp(line, "set delta ", 10) == 0) {
    s->cmd.deltaRpm = parse_int(line + 10, s->cmd.deltaRpm);
    return;
  }
  if (strncmp(line, "spin straight", 13) == 0) {
    s->cmd.spinMode = STRAIGHT;
    s->debugOverride.enabled = 0;
    return;
  }
  if (strncmp(line, "spin topspin", 12) == 0) {
    s->cmd.spinMode = TOPSPIN;
    s->debugOverride.enabled = 0;
    return;
  }
  if (strncmp(line, "spin backspin", 13) == 0) {
    s->cmd.spinMode = BACKSPIN;
    s->debugOverride.enabled = 0;
    return;
  }
  if (strncmp(line, "spin left", 9) == 0) {
    s->cmd.spinMode = LEFT_CURVE;
    s->debugOverride.enabled = 0;
    return;
  }
  if (strncmp(line, "spin right", 10) == 0) {
    s->cmd.spinMode = RIGHT_CURVE;
    s->debugOverride.enabled = 0;
    return;
  }
  if (strncmp(line, "jog wheel1 ", 11) == 0) {
    s->debugOverride.enabled = 1;
    s->debugOverride.wheel1Rpm = parse_int(line + 11, s->debugOverride.wheel1Rpm);
    return;
  }
  if (strncmp(line, "jog wheel2 ", 11) == 0) {
    s->debugOverride.enabled = 1;
    s->debugOverride.wheel2Rpm = parse_int(line + 11, s->debugOverride.wheel2Rpm);
    return;
  }
  if (strncmp(line, "jog wheel3 ", 11) == 0) {
    s->debugOverride.enabled = 1;
    s->debugOverride.wheel3Rpm = parse_int(line + 11, s->debugOverride.wheel3Rpm);
    return;
  }
  if (strncmp(line, "jog off", 7) == 0) {
    s->debugOverride.enabled = 0;
    s->debugOverride.wheel1Rpm = 0;
    s->debugOverride.wheel2Rpm = 0;
    s->debugOverride.wheel3Rpm = 0;
    return;
  }
  if (strncmp(line, "fire", 4) == 0) {
    s->cmd.fireRequest = 1;
    return;
  }
  if (strncmp(line, "estop", 5) == 0) {
    s->cmd.estop = 1;
    return;
  }
  if (strncmp(line, "clear fault", 11) == 0) {
    host_fault_clear();
    s->cmd.estop = 0;
    if (s->state == FAULT || s->state == ESTOP) s->state = IDLE;
    return;
  }
  if (strncmp(line, "ball loaded", 11) == 0) {
    s->sensors.ballLoaded = 1;
    return;
  }
  if (strncmp(line, "ball empty", 10) == 0) {
    s->sensors.ballLoaded = 0;
    return;
  }
}
