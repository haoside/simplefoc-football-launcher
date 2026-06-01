#include "../hal/node_hal_bg431b.h"
#include "../include/node_state.h"
#include "../../common/protocol.h"
#include "../../common/protocol_codec.h"

static void bg_apply_set_rpm(const CanSetRpmFrame* cmd) {
  BgNodeState* s = bg_node_state_get();
  s->targetRpm = cmd->targetRpm;
  s->enabled = cmd->enable;
  s->lastCommandMs = bg_hal_millis();
  s->state = cmd->enable ? STATE_SPINUP : STATE_IDLE;
}

void bg_node_comm_poll_rx(void) {
  BgCanFrame rx = {0};
  BgNodeState* s = bg_node_state_get();
  while (bg_hal_can_recv(&rx) == 0) {
    if (rx.canId == CAN_ID_SET_RPM(s->nodeId)) {
      CanSetRpmFrame cmd = {0};
      if (protocol_decode_set_rpm(&cmd, rx.data, rx.dlc) > 0) {
        bg_apply_set_rpm(&cmd);
      }
    } else if (rx.canId == CAN_ID_ESTOP_BROADCAST) {
      s->enabled = 0;
      s->state = STATE_ESTOP;
    }
  }
}

void bg_node_comm_send_status(void) {
  BgNodeState* s = bg_node_state_get();
  BgCanFrame tx = {0};
  CanStatusFrame st = {0};
  tx.canId = CAN_ID_STATUS(s->nodeId);
  tx.dlc = sizeof(CanStatusFrame);
  st.actualRpm = s->actualRpm;
  st.targetRpm = s->targetRpm;
  st.busVoltage_x10 = s->busVoltage_x10;
  st.phaseCurrent_x10 = s->phaseCurrent_x10;
  protocol_encode_status(tx.data, &st);
  bg_hal_can_send(&tx);
}

void bg_node_comm_send_heartbeat(void) {
  static uint8_t aliveCounter = 0;
  BgNodeState* s = bg_node_state_get();
  BgCanFrame tx = {0};
  CanHeartbeatFrame hb = {0};
  tx.canId = CAN_ID_HEARTBEAT(s->nodeId);
  tx.dlc = sizeof(CanHeartbeatFrame);
  hb.state = s->state;
  hb.faultCode = s->faultCode;
  hb.temp_x10 = s->temp_x10;
  hb.aliveCounter = aliveCounter++;
  protocol_encode_heartbeat(tx.data, &hb);
  bg_hal_can_send(&tx);
}

void bg_node_comm_send_fault_if_needed(void) {
  BgNodeState* s = bg_node_state_get();
  if (s->faultCode == FAULT_NONE) return;
  BgCanFrame tx = {0};
  CanFaultFrame ff = {0};
  tx.canId = CAN_ID_FAULT(s->nodeId);
  tx.dlc = sizeof(CanFaultFrame);
  ff.faultCode = s->faultCode;
  ff.state = s->state;
  ff.actualRpm = s->actualRpm;
  ff.phaseCurrent_x10 = s->phaseCurrent_x10;
  ff.busVoltage_x10 = s->busVoltage_x10;
  protocol_encode_fault(tx.data, &ff);
  bg_hal_can_send(&tx);
}
