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

struct HostTelemetry {
  uint8_t feedState;
  uint8_t feedFaultReason;
  uint8_t hostFaultCode;
};

struct HostState {
  LaunchState state;
  HostCommand cmd;
  HostSensors sensors;
  HostTelemetry telemetry;
};

HostState* host_state_get();
