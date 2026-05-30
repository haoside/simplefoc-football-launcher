#include "../host_hal.h"

// Template only: replace stubs with real ESP-IDF includes in target project.
// Suggested includes:
// #include "driver/twai.h"
// #include "driver/gpio.h"
// #include "esp_timer.h"

void host_hal_init(void) {
  // gpio_config(...) for sensors / estop / leds / feed actuator
}

void host_hal_delay_ms(uint32_t ms) {
  (void)ms;
  // vTaskDelay(pdMS_TO_TICKS(ms));
}

uint32_t host_hal_millis(void) {
  // return (uint32_t)(esp_timer_get_time() / 1000ULL);
  return 0;
}

int host_hal_can_init(void) {
  // twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_GPIO, RX_GPIO, TWAI_MODE_NORMAL);
  // twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
  // twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();
  // twai_driver_install(&g_config, &t_config, &f_config);
  // twai_start();
  return 0;
}

int host_hal_can_send(const HostCanFrame* frame) {
  (void)frame;
  // twai_message_t msg = { .identifier = frame->canId, .data_length_code = frame->dlc };
  // memcpy(msg.data, frame->data, frame->dlc);
  // return twai_transmit(&msg, pdMS_TO_TICKS(5));
  return 0;
}

int host_hal_can_recv(HostCanFrame* frame) {
  (void)frame;
  // twai_message_t msg;
  // if (twai_receive(&msg, 0) != ESP_OK) return -1;
  // frame->canId = msg.identifier; frame->dlc = msg.data_length_code; memcpy(frame->data, msg.data, msg.data_length_code);
  return -1;
}

int host_hal_sensor_tube_ball_present(void) {
  // return gpio_get_level(GPIO_TUBE_SENSOR);
  return 0;
}

int host_hal_sensor_chamber_ready(void) {
  // return gpio_get_level(GPIO_CHAMBER_SENSOR);
  return 0;
}

int host_hal_sensor_exit_detected(void) {
  // return gpio_get_level(GPIO_EXIT_SENSOR);
  return 0;
}

int host_hal_estop_active(void) {
  // return gpio_get_level(GPIO_ESTOP_IN);
  return 0;
}

void host_hal_feed_request(void) {
  // servo pwm or solenoid pulse
}

void host_hal_set_status_led(int on) {
  (void)on;
}

void host_hal_set_buzzer(int on) {
  (void)on;
}
