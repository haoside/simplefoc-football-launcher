#include "../hal/node_hal_bg431b.h"
#include "../include/board_config.h"
#include "../include/node_state.h"
#include "../include/node_profile.h"

extern void bg_node_comm_poll_rx(void);
extern void bg_node_comm_send_status(void);
extern void bg_node_comm_send_heartbeat(void);
extern void bg_node_comm_send_fault_if_needed(void);
extern void bg_node_control_step(void);
extern void bg_node_telemetry_refresh(void);
extern void bg_node_safety_step(void);

int main(void) {
  bg_hal_init();
  bg_hal_can_init();
  bg_node_profile_select(NODE_DEFAULT_ID);
  bg_node_state_reset(bg_node_profile_get()->nodeId);

  while (1) {
    bg_node_comm_poll_rx();
    bg_node_telemetry_refresh();
    bg_node_safety_step();
    bg_node_control_step();
    bg_node_comm_send_status();
    bg_node_comm_send_heartbeat();
    bg_node_comm_send_fault_if_needed();
    break; // placeholder loop for integration
  }
  return 0;
}
