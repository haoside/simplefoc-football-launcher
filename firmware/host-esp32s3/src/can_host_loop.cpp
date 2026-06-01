#include "../../common/config.h"
#include "../../common/protocol.h"
#include "../../common/protocol_codec.h"
#include "hal/host_hal.h"
#include "host_fault.h"
#include "host_state.h"
#include <stdint.h>

static int clamp_rpm(int rpm) {
  if (rpm <= 0) return 0;
  if (rpm < RPM_MIN) return RPM_MIN;
  if (rpm > RPM_MAX) return RPM_MAX;
  return rpm;
}

static void compute_targets(HostState* s) {
  const int base = s->cmd.baseRpm;
  const int d = s->cmd.deltaRpm;
  int w1 = base, w2 = base, w3 = base;

  switch ((SpinMode)s->cmd.spinMode) {
    case TOPSPIN:
      w1 = base + d;
      w2 = base - d / 2;
      w3 = base - d / 2;
      break;
    case BACKSPIN:
      w1 = base - d;
      w2 = base + d / 2;
      w3 = base + d / 2;
      break;
    case LEFT_CURVE:
      w1 = base;
      w2 = base - d;
      w3 = base + d;
      break;
    case RIGHT_CURVE:
      w1 = base;
      w2 = base + d;
      w3 = base - d;
      break;
    case STRAIGHT:
    default:
      break;
  }

  s->wheel1.targetRpm = (int16_t)clamp_rpm(w1);
  s->wheel2.targetRpm = (int16_t)clamp_rpm(w2);
  s->wheel3.targetRpm = (int16_t)clamp_rpm(w3);
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

static void apply_status_to_wheel(WheelTelemetry* wheel, const CanStatusFrame* st) {
  wheel->actualRpm = st->actualRpm;
  wheel->targetRpm = st->targetRpm;
}

void host_can_control_tick(void) {
  HostState* s = host_state_get();
  compute_targets(s);

  if (host_fault_is_active() || s->state == ESTOP || s->state == FAULT) {
    s->state = (s->state == ESTOP) ? ESTOP : FAULT;
    host_can_send_estop_broadcast(host_fault_code(), host_fault_source());
    host_can_send_set_rpm(NODE_ID_WHEEL_A, 0, 0, 0);
    host_can_send_set_rpm(NODE_ID_WHEEL_B, 0, 0, 0);
    host_can_send_set_rpm(NODE_ID_WHEEL_C, 0, 0, 0);
    return;
  }

  host_can_send_set_rpm(NODE_ID_WHEEL_A, s->wheel1.targetRpm, 1000, 1);
  host_can_send_set_rpm(NODE_ID_WHEEL_B, s->wheel2.targetRpm, 1000, 1);
  host_can_send_set_rpm(NODE_ID_WHEEL_C, s->wheel3.targetRpm, 1000, 1);
}

void host_can_poll_rx(void) {
  HostCanFrame rx = {0};
  HostState* s = host_state_get();
  while (host_hal_can_recv(&rx) == 0) {
    if (rx.canId == CAN_ID_STATUS(NODE_ID_WHEEL_A)) {
      CanStatusFrame st = {0};
      if (protocol_decode_status(&st, rx.data, rx.dlc) > 0) apply_status_to_wheel(&s->wheel1, &st);
    } else if (rx.canId == CAN_ID_STATUS(NODE_ID_WHEEL_B)) {
      CanStatusFrame st = {0};
      if (protocol_decode_status(&st, rx.data, rx.dlc) > 0) apply_status_to_wheel(&s->wheel2, &st);
    } else if (rx.canId == CAN_ID_STATUS(NODE_ID_WHEEL_C)) {
      CanStatusFrame st = {0};
      if (protocol_decode_status(&st, rx.data, rx.dlc) > 0) apply_status_to_wheel(&s->wheel3, &st);
    } else if (rx.canId == CAN_ID_HEARTBEAT(NODE_ID_WHEEL_A) || rx.canId == CAN_ID_HEARTBEAT(NODE_ID_WHEEL_B) || rx.canId == CAN_ID_HEARTBEAT(NODE_ID_WHEEL_C)) {
      CanHeartbeatFrame hb = {0};
      if (protocol_decode_heartbeat(&hb, rx.data, rx.dlc) > 0) {
        if (hb.faultCode != FAULT_NONE || hb.state == STATE_FAULT || hb.state == STATE_ESTOP) {
          uint8_t src = (rx.canId == CAN_ID_HEARTBEAT(NODE_ID_WHEEL_A)) ? NODE_ID_WHEEL_A : (rx.canId == CAN_ID_HEARTBEAT(NODE_ID_WHEEL_B) ? NODE_ID_WHEEL_B : NODE_ID_WHEEL_C);
          host_fault_raise(hb.faultCode ? hb.faultCode : FAULT_COMMS_TIMEOUT, src);
        }
      }
    } else if (rx.canId == CAN_ID_FAULT(NODE_ID_WHEEL_A) || rx.canId == CAN_ID_FAULT(NODE_ID_WHEEL_B) || rx.canId == CAN_ID_FAULT(NODE_ID_WHEEL_C)) {
      CanFaultFrame ff = {0};
      if (protocol_decode_fault(&ff, rx.data, rx.dlc) > 0) {
        uint8_t src = (rx.canId == CAN_ID_FAULT(NODE_ID_WHEEL_A)) ? NODE_ID_WHEEL_A : (rx.canId == CAN_ID_FAULT(NODE_ID_WHEEL_B) ? NODE_ID_WHEEL_B : NODE_ID_WHEEL_C);
        host_fault_raise(ff.faultCode, src);
      }
    }
  }
}
