#include "debug_command.h"
#include "host_fault.h"
#include "host_state.h"
#include <stdio.h>
#include <string.h>

static int parse_int(const char* s, int fallback) {
  int v = fallback;
  if (s) sscanf(s, "%d", &v);
  return v;
}

void host_debug_apply_text_command(const char* line) {
  HostState* s = host_state_get();
  if (!line || !line[0]) return;

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
    return;
  }
  if (strncmp(line, "spin topspin", 12) == 0) {
    s->cmd.spinMode = TOPSPIN;
    return;
  }
  if (strncmp(line, "spin backspin", 13) == 0) {
    s->cmd.spinMode = BACKSPIN;
    return;
  }
  if (strncmp(line, "spin left", 9) == 0) {
    s->cmd.spinMode = LEFT_CURVE;
    return;
  }
  if (strncmp(line, "spin right", 10) == 0) {
    s->cmd.spinMode = RIGHT_CURVE;
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
