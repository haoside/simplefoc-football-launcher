#include "../include/node_state.h"

static BgNodeState g_node;

BgNodeState* bg_node_state_get(void) {
  return &g_node;
}

void bg_node_state_reset(uint8_t nodeId) {
  g_node.nodeId = nodeId;
  g_node.state = STATE_IDLE;
  g_node.enabled = 0;
  g_node.faultCode = FAULT_NONE;
  g_node.targetRpm = 0;
  g_node.actualRpm = 0;
  g_node.busVoltage_x10 = 240;
  g_node.phaseCurrent_x10 = 0;
  g_node.temp_x10 = 250;
  g_node.lastCommandMs = 0;
}
