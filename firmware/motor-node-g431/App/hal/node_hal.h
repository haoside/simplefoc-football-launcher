#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  uint16_t canId;
  uint8_t dlc;
  uint8_t data[8];
} NodeCanFrame;

void node_hal_init(void);
uint32_t node_hal_millis(void);

int node_hal_can_init(void);
int node_hal_can_send(const NodeCanFrame* frame);
int node_hal_can_recv(NodeCanFrame* frame);

void node_hal_pwm_enable(int enable);
void node_hal_pwm_set_uvw(float u, float v, float w);

int node_hal_read_hall_a(void);
int node_hal_read_hall_b(void);
int node_hal_read_hall_c(void);

uint16_t node_hal_read_vbus_x10(void);
uint16_t node_hal_read_current_x10(void);
int16_t node_hal_read_temp_x10(void);
int node_hal_driver_fault_active(void);

#ifdef __cplusplus
}
#endif
