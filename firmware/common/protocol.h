#pragma once

#include <stdint.h>

#define NODE_ID_WHEEL_A 0x11
#define NODE_ID_WHEEL_B 0x12
#define NODE_ID_WHEEL_C 0x13

#define CAN_ID_SET_RPM(nodeId)       (0x100u + (nodeId))
#define CAN_ID_SET_PARAM(nodeId)     (0x110u + (nodeId))
#define CAN_ID_CLEAR_FAULT(nodeId)   (0x120u + (nodeId))
#define CAN_ID_ESTOP_BROADCAST       (0x12Fu)
#define CAN_ID_STATUS(nodeId)        (0x180u + (nodeId))
#define CAN_ID_HEARTBEAT(nodeId)     (0x190u + (nodeId))
#define CAN_ID_FAULT(nodeId)         (0x1A0u + (nodeId))

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
  STATE_IDLE = 0,
  STATE_SPINUP = 1,
  STATE_RUNNING = 2,
  STATE_READY = 3,
  STATE_FAULT = 4,
  STATE_ESTOP = 5,
} NodeState;

typedef enum {
  PARAM_KP_X1000 = 1,
  PARAM_KI_X1000 = 2,
  PARAM_KD_X1000 = 3,
  PARAM_RPM_LIMIT = 4,
  PARAM_CURRENT_LIMIT_X10 = 5,
  PARAM_ACCEL_LIMIT = 6,
} ParamId;

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

#pragma pack(push, 1)
typedef struct {
  uint8_t seq;
  int16_t targetRpm;
  uint16_t rampMs;
  uint8_t enable;
  uint8_t reserved0;
  uint8_t reserved1;
} CanSetRpmFrame;

typedef struct {
  uint8_t paramId;
  int32_t value;
  uint8_t reserved0;
  uint8_t reserved1;
  uint8_t reserved2;
} CanSetParamFrame;

typedef struct {
  uint8_t magic;
  uint8_t reserved[7];
} CanClearFaultFrame;

typedef struct {
  uint8_t code;
  uint8_t source;
  uint8_t reserved[6];
} CanEstopFrame;

typedef struct {
  int16_t actualRpm;
  int16_t targetRpm;
  uint16_t busVoltage_x10;
  uint16_t phaseCurrent_x10;
} CanStatusFrame;

typedef struct {
  uint8_t state;
  uint8_t faultCode;
  int16_t temp_x10;
  uint8_t aliveCounter;
  uint8_t reserved[3];
} CanHeartbeatFrame;

typedef struct {
  uint8_t faultCode;
  uint8_t state;
  int16_t actualRpm;
  uint16_t phaseCurrent_x10;
  uint16_t busVoltage_x10;
} CanFaultFrame;
#pragma pack(pop)

static inline int protocol_is_valid_node(uint8_t nodeId) {
  return nodeId == NODE_ID_WHEEL_A || nodeId == NODE_ID_WHEEL_B || nodeId == NODE_ID_WHEEL_C;
}
