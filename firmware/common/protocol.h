#pragma once

#include <stdint.h>

#define NODE_ID_WHEEL_A 0x11
#define NODE_ID_WHEEL_B 0x12
#define NODE_ID_WHEEL_C 0x13

typedef enum {
  MSG_SET_RPM = 0x01,
  MSG_ESTOP = 0x02,
  MSG_CLEAR_FAULT = 0x03,
  MSG_SET_PARAM = 0x04,
  MSG_STATUS = 0x81,
  MSG_HEARTBEAT = 0x82,
  MSG_FAULT = 0x83,
} MessageType;

typedef enum {
  FAULT_NONE = 0,
  FAULT_OVERCURRENT = 1,
  FAULT_OVERVOLTAGE = 2,
  FAULT_UNDERVOLTAGE = 3,
  FAULT_OVERTEMP = 4,
  FAULT_HALL = 5,
  FAULT_STALL = 6,
  FAULT_COMMS_TIMEOUT = 7,
  FAULT_NO_BALL_AT_CHAMBER = 8,
  FAULT_BALL_JAM = 9,
} FaultCode;

typedef struct {
  uint8_t nodeId;
  int16_t targetRpm;
  uint16_t rampMs;
  uint8_t enable;
} SetRpmFrame;

typedef struct {
  uint8_t nodeId;
  int16_t actualRpm;
  int16_t targetRpm;
  uint16_t busVoltage_x10;
  uint16_t phaseCurrent_x10;
  int16_t temp_x10;
  uint8_t faultCode;
} StatusFrame;
