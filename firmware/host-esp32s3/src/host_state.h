#pragma once

#include <stdint.h>

enum LaunchState {
  IDLE,
  SPINUP,
  READY,
  FIRE,
  COOLDOWN,
  FAULT,
  ESTOP,
};

enum SpinMode {
  STRAIGHT = 0,
  TOPSPIN = 1,
  BACKSPIN = 2,
  LEFT_CURVE = 3,
  RIGHT_CURVE = 4,
};

struct HostCommand {
  int baseRpm;
  int deltaRpm;
  uint8_t spinMode;
  uint8_t fireRequest;
  uint8_t estop;
};

struct HostSensors {
  uint8_t ballLoaded;
};

struct WheelTelemetry {
  int16_t targetRpm;
  int16_t actualRpm;
  uint8_t faultCode;
  uint8_t state;
};

struct DebugOverride {
  uint8_t enabled;
  int16_t wheel1Rpm;
  int16_t wheel2Rpm;
  int16_t wheel3Rpm;
};

struct HostTelemetry {
  uint8_t hostFaultCode;
};

struct HostState {
  LaunchState state;
  HostCommand cmd;
  HostSensors sensors;
  WheelTelemetry wheel1;
  WheelTelemetry wheel2;
  WheelTelemetry wheel3;
  DebugOverride debugOverride;
  HostTelemetry telemetry;
  uint32_t stateEnterMs;
};

HostState* host_state_get();
