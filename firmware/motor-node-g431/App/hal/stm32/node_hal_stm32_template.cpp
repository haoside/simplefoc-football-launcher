#include "../node_hal.h"

// Template only: replace with real STM32 HAL/LL includes in target project.
// Suggested includes:
// #include "main.h"
// #include "fdcan.h"
// #include "adc.h"
// #include "tim.h"
// #include "gpio.h"

void node_hal_init(void) {
  // MX_GPIO_Init();
  // MX_ADC1_Init();
  // MX_TIM1_Init();
  // MX_FDCAN1_Init();
}

uint32_t node_hal_millis(void) {
  // return HAL_GetTick();
  return 0;
}

int node_hal_can_init(void) {
  // HAL_FDCAN_Start(&hfdcan1);
  // HAL_FDCAN_ActivateNotification(...);
  return 0;
}

int node_hal_can_send(const NodeCanFrame* frame) {
  (void)frame;
  // FDCAN_TxHeaderTypeDef tx = {...};
  // HAL_FDCAN_AddMessageToTxFifoQ(&hfdcan1, &tx, (uint8_t*)frame->data);
  return 0;
}

int node_hal_can_recv(NodeCanFrame* frame) {
  (void)frame;
  // poll or IRQ-driven RX FIFO fetch
  return -1;
}

void node_hal_pwm_enable(int enable) {
  (void)enable;
  // set DRV_EN GPIO and start/stop PWM outputs
}

void node_hal_pwm_set_uvw(float u, float v, float w) {
  (void)u; (void)v; (void)w;
  // map normalized duty to TIM compare registers
}

int node_hal_read_hall_a(void) {
  // return HAL_GPIO_ReadPin(HALL_A_GPIO_Port, HALL_A_Pin);
  return 0;
}

int node_hal_read_hall_b(void) {
  // return HAL_GPIO_ReadPin(HALL_B_GPIO_Port, HALL_B_Pin);
  return 0;
}

int node_hal_read_hall_c(void) {
  // return HAL_GPIO_ReadPin(HALL_C_GPIO_Port, HALL_C_Pin);
  return 0;
}

uint16_t node_hal_read_vbus_x10(void) {
  // ADC + divider conversion
  return 240;
}

uint16_t node_hal_read_current_x10(void) {
  // ADC + shunt conversion
  return 0;
}

int16_t node_hal_read_temp_x10(void) {
  // ADC + NTC conversion
  return 250;
}

int node_hal_driver_fault_active(void) {
  // return HAL_GPIO_ReadPin(DRV_FAULT_GPIO_Port, DRV_FAULT_Pin) == GPIO_PIN_RESET;
  return 0;
}
