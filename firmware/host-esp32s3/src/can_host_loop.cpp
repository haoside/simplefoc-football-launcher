#include "../../common/config.h"
#include "../../common/protocol.h"
#include "../../common/protocol_codec.h"
#include "hal/host_hal.h"
#include "host_fault.h"
#include "host_state.h"
#include "rpm_mixer_120.h"
#include <stdint.h>

struct HostNodeState {
  uint8_t nodeId;
  int16_t targetRpm;
  int16_t actualRpm;
  uint16_t lastSeenMs;
  uint8_t faultCode;
  uint8_t state;
};

static HostNodeState g_nodes[3] = {
  {NODE_ID_WHEEL_A, 0, 0, 0, FAULT_NONE, STATE_IDLE},
  {NODE_ID_WHEEL_B, 0, 0, 0, FAULT_NONE, STATE_IDLE},
  {NODE_ID_WHEEL_C, 0, 0, 0, FAULT_NONE, STATE_IDLE},
};

static int clamp_rpm(float rpm) {
  if (rpm < RPM_MIN) return (rpm <= 0) ? 0 : RPM_MIN;
  if (rpm > RPM_MAX) return RPM_MAX;
  return (int)rpm;
}

static void host_can_send_estop_broadcast(uint8_t code, uint8_t source) {
  HostCanFrame tx = {0};
  CanEstopFrame frame = {0};
  tx.canId = CAN_ID_ESTOP_BROADCAST;
  tx.dlc = sizeof(CanEstopFrame);
  frame.code = code;
  frame.source = source;
  for (unsigned i = 0; i < sizeof(frame); ++i) tx.data[i] = ((uint8_t*)&frame)[i];
  host_hal_can_send(&tx);
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
  HostCanFrame tx = {0};
  CanSetRpmFrame frame = {0};
  tx.canId = CAN_ID_SET_RPM(nodeId);
  tx.dlc = sizeof(CanSetRpmFrame);
  frame.seq = 0;
  frame.targetRpm = targetRpm;
  frame.rampMs = rampMs;
  frame.enable = enable;
  protocol_encode_set_rpm(tx.data, &frame);
  host_hal_can_send(&tx);
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

static void host_handle_heartbeat(uint8_t nodeId, const CanHeartbeatFrame* hb) {
  for (unsigned i = 0; i < 3; ++i) {
    if (g_nodes[i].nodeId == nodeId) {
      g_nodes[i].faultCode = hb->faultCode;
      g_nodes[i].state = hb->state;
      if (hb->faultCode != FAULT_NONE || hb->state == STATE_FAULT || hb->state == STATE_ESTOP) {
        host_fault_raise(hb->faultCode ? hb->faultCode : FAULT_COMMS_TIMEOUT, nodeId);
      }
      break;
    }
  }
}

static void host_handle_fault(uint8_t nodeId, const CanFaultFrame* ff) {
  host_fault_raise(ff->faultCode, nodeId);
}

void host_can_control_tick(void) {
  HostState* s = host_state_get();
  host_update_targets_from_command();

  if (host_fault_is_active() || s->state == ESTOP || s->state == FAULT) {
    s->state = (s->state == ESTOP) ? ESTOP : FAULT;
    host_can_send_estop_broadcast(host_fault_code(), host_fault_source());
    for (unsigned i = 0; i < 3; ++i) {
      host_can_send_set_rpm(g_nodes[i].nodeId, 0, 0, 0);
    }
    return;
  }

  for (unsigned i = 0; i < 3; ++i) {
    host_can_send_set_rpm(g_nodes[i].nodeId, g_nodes[i].targetRpm, 200, 1);
  }
}

void host_can_poll_rx(void) {
  HostCanFrame rx = {0};
  while (host_hal_can_recv(&rx) == 0) {
    for (unsigned i = 0; i < 3; ++i) {
      if (rx.canId == CAN_ID_STATUS(g_nodes[i].nodeId)) {
        CanStatusFrame st = {0};
        if (protocol_decode_status(&st, rx.data, rx.dlc) > 0) {
          host_handle_status(g_nodes[i].nodeId, &st);
        }
      } else if (rx.canId == CAN_ID_HEARTBEAT(g_nodes[i].nodeId)) {
        CanHeartbeatFrame hb = {0};
        if (protocol_decode_heartbeat(&hb, rx.data, rx.dlc) > 0) {
          host_handle_heartbeat(g_nodes[i].nodeId, &hb);
        }
      } else if (rx.canId == CAN_ID_FAULT(g_nodes[i].nodeId)) {
        CanFaultFrame ff = {0};
        if (protocol_decode_fault(&ff, rx.data, rx.dlc) > 0) {
          host_handle_fault(g_nodes[i].nodeId, &ff);
        }
      }
    }
  }
}
