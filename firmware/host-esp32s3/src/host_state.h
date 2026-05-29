#pragma once

#include <stdint.h>

enum LaunchState {
  IDLE,
  SPINUP,
  FEED_READY,
  BALL_IN_POSITION,
  FIRE,
  RELOAD,
  FAULT,
  ESTOP,
};

struct HostCommand {
  int baseRpm;
  float ux;
  float uy;
  uint8_t fireRequest;
  uint8_t estop;
};

struct HostSensors {
  uint8_t tubeBallPresent;
  uint8_t chamberReady;
  uint8_t exitDetected;
};

struct HostState {
  LaunchState state;
  HostCommand cmd;
  HostSensors sensors;
};

HostState* host_state_get();
