#include "../include/node_profile.h"
#include "../../common/protocol.h"

static BgNodeProfile g_profile = {
  "wheel1",
  NODE_ID_WHEEL_A,
  1,
  1,
  500,
  3000,
};

const BgNodeProfile* bg_node_profile_get(void) {
  return &g_profile;
}

void bg_node_profile_select(uint8_t nodeId) {
  switch (nodeId) {
    case NODE_ID_WHEEL_A:
      g_profile.name = "wheel1";
      g_profile.nodeId = NODE_ID_WHEEL_A;
      g_profile.motorDirection = 1;
      g_profile.hallPolarity = 1;
      break;
    case NODE_ID_WHEEL_B:
      g_profile.name = "wheel2";
      g_profile.nodeId = NODE_ID_WHEEL_B;
      g_profile.motorDirection = 1;
      g_profile.hallPolarity = 1;
      break;
    case NODE_ID_WHEEL_C:
      g_profile.name = "wheel3";
      g_profile.nodeId = NODE_ID_WHEEL_C;
      g_profile.motorDirection = 1;
      g_profile.hallPolarity = 1;
      break;
    default:
      break;
  }
}
