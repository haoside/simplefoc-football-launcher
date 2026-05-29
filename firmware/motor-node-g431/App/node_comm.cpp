#include "node_state.h"
#include "../../common/protocol.h"
#include "../../common/protocol_codec.h"
#include <stdint.h>
#include <stdio.h>

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
  CanStatusFrame st = {0};
  uint8_t payload[8] = {0};
  st.actualRpm = s->actualRpm;
  st.targetRpm = s->targetRpm;
  st.busVoltage_x10 = s->busVoltage_x10;
  st.phaseCurrent_x10 = s->phaseCurrent_x10;
  protocol_encode_status(payload, &st);
  printf("CAN TX id=0x%03X actual=%d target=%d\n", CAN_ID_STATUS(s->nodeId), st.actualRpm, st.targetRpm);
}

static void node_send_heartbeat(void) {
  MotorNodeState* s = node_state_get();
  CanHeartbeatFrame hb = {0};
  uint8_t payload[8] = {0};
  hb.state = s->state;
  hb.faultCode = s->faultCode;
  hb.temp_x10 = s->temp_x10;
  hb.aliveCounter++;
  protocol_encode_heartbeat(payload, &hb);
  printf("CAN TX id=0x%03X hb state=%u fault=%u\n", CAN_ID_HEARTBEAT(s->nodeId), hb.state, hb.faultCode);
}

void node_comm_poll() {
  node_send_status();
  node_send_heartbeat();
}
