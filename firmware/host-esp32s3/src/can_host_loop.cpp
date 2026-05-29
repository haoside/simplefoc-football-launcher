#include "../../common/config.h"
#include "../../common/protocol.h"
#include "../../common/protocol_codec.h"
#include "host_state.h"
#include "rpm_mixer_120.h"
#include <stdint.h>
#include <stdio.h>

struct HostNodeState {
  uint8_t nodeId;
  int16_t targetRpm;
  int16_t actualRpm;
  uint16_t lastSeenMs;
  uint8_t faultCode;
};

static HostNodeState g_nodes[3] = {
  {NODE_ID_WHEEL_A, 0, 0, 0, FAULT_NONE},
  {NODE_ID_WHEEL_B, 0, 0, 0, FAULT_NONE},
  {NODE_ID_WHEEL_C, 0, 0, 0, FAULT_NONE},
};

static int clamp_rpm(float rpm) {
  if (rpm < RPM_MIN) return (rpm <= 0) ? 0 : RPM_MIN;
  if (rpm > RPM_MAX) return RPM_MAX;
  return (int)rpm;
}

static void host_update_targets_from_command() {
  HostState* s = host_state_get();
  RpmCommand cmd = {(float)s->cmd.baseRpm, s->cmd.ux, s->cmd.uy};
  WheelRpm w = mix120deg(cmd, 1.0f, 1.0f);
  g_nodes[0].targetRpm = clamp_rpm(w.a);
  g_nodes[1].targetRpm = clamp_rpm(w.b);
  g_nodes[2].targetRpm = clamp_rpm(w.c);
}

static void host_can_send_set_rpm(uint8_t nodeId, int16_t targetRpm, uint16_t rampMs, uint8_t enable) {
  CanSetRpmFrame frame = {0};
  uint8_t payload[8] = {0};
  frame.seq = 0;
  frame.targetRpm = targetRpm;
  frame.rampMs = rampMs;
  frame.enable = enable;
  protocol_encode_set_rpm(payload, &frame);
  printf("CAN TX id=0x%03X target=%d enable=%u\n", CAN_ID_SET_RPM(nodeId), targetRpm, enable);
}

static void host_handle_status(uint8_t nodeId, const CanStatusFrame* st) {
  for (unsigned i = 0; i < 3; ++i) {
    if (g_nodes[i].nodeId == nodeId) {
      g_nodes[i].actualRpm = st->actualRpm;
      g_nodes[i].targetRpm = st->targetRpm;
      break;
    }
  }
}

void host_can_control_tick(void) {
  HostState* s = host_state_get();
  host_update_targets_from_command();
  uint8_t enable = (s->state != ESTOP && s->state != FAULT) ? 1 : 0;
  for (unsigned i = 0; i < 3; ++i) {
    host_can_send_set_rpm(g_nodes[i].nodeId, g_nodes[i].targetRpm, 200, enable);
  }
}

void host_can_on_rx(uint16_t canId, const uint8_t* data, int len) {
  for (unsigned i = 0; i < 3; ++i) {
    if (canId == CAN_ID_STATUS(g_nodes[i].nodeId)) {
      CanStatusFrame st = {0};
      if (protocol_decode_status(&st, data, len) > 0) {
        host_handle_status(g_nodes[i].nodeId, &st);
      }
      return;
    }
  }
}
