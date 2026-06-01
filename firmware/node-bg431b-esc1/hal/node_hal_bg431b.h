#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  uint16_t canId;
  uint8_t dlc;
  uint8_t data[8];
} BgCanFrame;

void bg_hal_init(void);
uint32_t bg_hal_millis(void);
int bg_hal_can_init(void);
int bg_hal_can_send(const BgCanFrame* frame);
int bg_hal_can_recv(BgCanFrame* frame);

void bg_hal_motor_enable(int enable);
void bg_hal_set_target_rpm(int rpm);
int bg_hal_get_actual_rpm(void);
uint16_t bg_hal_get_bus_voltage_x10(void);
uint16_t bg_hal_get_phase_current_x10(void);
int16_t bg_hal_get_temp_x10(void);
int bg_hal_driver_fault_active(void);

#ifdef __cplusplus
}
#endif
