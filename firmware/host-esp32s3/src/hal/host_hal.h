#pragma once

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  uint16_t canId;
  uint8_t dlc;
  uint8_t data[8];
} HostCanFrame;

void host_hal_init(void);
void host_hal_delay_ms(uint32_t ms);
uint32_t host_hal_millis(void);

int host_hal_can_init(void);
int host_hal_can_send(const HostCanFrame* frame);
int host_hal_can_recv(HostCanFrame* frame);

int host_hal_sensor_ball_loaded(void);
int host_hal_estop_active(void);
void host_hal_trigger_launch(void);
void host_hal_set_status_led(int on);
void host_hal_set_buzzer(int on);

#ifdef __cplusplus
}
#endif
