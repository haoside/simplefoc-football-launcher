#include "hal/node_hal.h"
#include "node_state.h"
#include "../../common/protocol.h"
#include "../../common/protocol_codec.h"
#include <stdint.h>

static void node_apply_set_rpm(const CanSetRpmFrame* cmd) {
  MotorNodeState* s = node_state_get();
  s->targetRpm = cmd->targetRpm;
  s->enabled = cmd->enable;
  s->state = cmd->enable ? STATE_SPINUP : STATE_IDLE;
}

void node_comm_on_rx(uint16_t canId, const uint8_t* data, int len) {
  MotorNodeState* s = node_state_get();
  if (canId == CAN_ID_SET_RPM(s->nodeId)) {
    CanSetRpmFrame cmd = {0};
    if (protocol_decode_set_rpm(&cmd, data, len) > 0) {
      node_apply_set_rpm(&cmd);
    }
  } else if (canId == CAN_ID_ESTOP_BROADCAST) {
    s->enabled = 0;
    s->state = STATE_ESTOP;
  }
}

static void node_send_status(void) {
  MotorNodeState* s = node_state_get();
  NodeCanFrame tx = {0};
  CanStatusFrame st = {0};
  tx.canId = CAN_ID_STATUS(s->nodeId);
  tx.dlc = sizeof(CanStatusFrame);
  st.actualRpm = s->actualRpm;
  st.targetRpm = s->targetRpm;
  st.busVoltage_x10 = s->busVoltage_x10;
  st.phaseCurrent_x10 = s->phaseCurrent_x10;
  protocol_encode_status(tx.data, &st);
  node_hal_can_send(&tx);
}

static void node_send_heartbeat(void) {
  static uint8_t aliveCounter = 0;
  MotorNodeState* s = node_state_get();
  NodeCanFrame tx = {0};
  CanHeartbeatFrame hb = {0};
  tx.canId = CAN_ID_HEARTBEAT(s->nodeId);
  tx.dlc = sizeof(CanHeartbeatFrame);
  hb.state = s->state;
  hb.faultCode = s->faultCode;
  hb.temp_x10 = s->temp_x10;
  hb.aliveCounter = aliveCounter++;
  protocol_encode_heartbeat(tx.data, &hb);
  node_hal_can_send(&tx);
}

static void node_send_fault(void) {
  MotorNodeState* s = node_state_get();
  if (s->faultCode == FAULT_NONE) return;
  NodeCanFrame tx = {0};
  CanFaultFrame ff = {0};
  tx.canId = CAN_ID_FAULT(s->nodeId);
  tx.dlc = sizeof(CanFaultFrame);
  ff.faultCode = s->faultCode;
  ff.state = s->state;
  ff.actualRpm = s->actualRpm;
  ff.phaseCurrent_x10 = s->phaseCurrent_x10;
  ff.busVoltage_x10 = s->busVoltage_x10;
  protocol_encode_fault(tx.data, &ff);
  node_hal_can_send(&tx);
}

void node_comm_poll_rx(void) {
  NodeCanFrame rx = {0};
  while (node_hal_can_recv(&rx) == 0) {
    node_comm_on_rx(rx.canId, rx.data, rx.dlc);
  }
}

void node_comm_poll() {
  node_comm_poll_rx();
  node_send_status();
  node_send_heartbeat();
  node_send_fault();
}
