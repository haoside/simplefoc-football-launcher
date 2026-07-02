// ESP-IDF real HAL implementation for Host (ESP32-S3)
// Replaces host_hal_stub.cpp when targeting real hardware.
//
// Pin assignments — adjust to match final PCB:
//   TWAI_TX = GPIO 5, TWAI_RX = GPIO 4
//   SENSOR_BALL_LOADED = GPIO 6, SENSOR_TUBE_BALL = GPIO 7
//   SENSOR_CHAMBER = GPIO 15, SENSOR_EXIT = GPIO 16
//   ESTOP_IN = GPIO 17, LAUNCH_TRIGGER = GPIO 18
//   FEED_ACTUATOR = GPIO 8, STATUS_LED = GPIO 48, BUZZER = GPIO 47

#include "host_hal.h"
#include "driver/twai.h"
#include "driver/gpio.h"
#include "esp_timer.h"
#include <stdio.h>
#include <string.h>

// --- Pin definitions ---
#define PIN_TWAI_TX         GPIO_NUM_5
#define PIN_TWAI_RX         GPIO_NUM_4
#define PIN_SENSOR_BALL     GPIO_NUM_6
#define PIN_SENSOR_TUBE     GPIO_NUM_7
#define PIN_SENSOR_CHAMBER  GPIO_NUM_15
#define PIN_SENSOR_EXIT     GPIO_NUM_16
#define PIN_ESTOP           GPIO_NUM_17
#define PIN_LAUNCH          GPIO_NUM_18
#define PIN_FEED_ACTUATOR   GPIO_NUM_8
#define PIN_STATUS_LED      GPIO_NUM_48
#define PIN_BUZZER          GPIO_NUM_47

// --- Millisecond timer ---
static volatile uint32_t g_millis = 0;

static void millis_timer_cb(void* arg) {
    (void)arg;
    g_millis++;
}

static esp_timer_handle_t g_millis_timer;

// ============================================================
// HAL interface implementation
// ============================================================

void host_hal_init(void) {
    // Sensor inputs (active-low, pull-up)
    gpio_config_t in_conf = {
        .pin_bit_mask = (1ULL << PIN_SENSOR_BALL) |
                        (1ULL << PIN_SENSOR_TUBE) |
                        (1ULL << PIN_SENSOR_CHAMBER) |
                        (1ULL << PIN_SENSOR_EXIT) |
                        (1ULL << PIN_ESTOP),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&in_conf);

    // Outputs
    gpio_config_t out_conf = {
        .pin_bit_mask = (1ULL << PIN_LAUNCH) |
                        (1ULL << PIN_FEED_ACTUATOR) |
                        (1ULL << PIN_STATUS_LED) |
                        (1ULL << PIN_BUZZER),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&out_conf);
    gpio_set_level(PIN_LAUNCH, 0);
    gpio_set_level(PIN_FEED_ACTUATOR, 0);
    gpio_set_level(PIN_STATUS_LED, 0);
    gpio_set_level(PIN_BUZZER, 0);

    // 1ms tick timer
    esp_timer_create_args_t timer_args = {
        .callback = millis_timer_cb,
        .name = "millis",
    };
    esp_timer_create(&timer_args, &g_millis_timer);
    esp_timer_start_periodic(g_millis_timer, 1000);

    printf("[host_hal] init complete\n");
}

void host_hal_delay_ms(uint32_t ms) {
    vTaskDelay(pdMS_TO_TICKS(ms));
}

uint32_t host_hal_millis(void) {
    return g_millis;
}

// --- CAN (TWAI 500kbps) ---

int host_hal_can_init(void) {
    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(
        (gpio_num_t)PIN_TWAI_TX, (gpio_num_t)PIN_TWAI_RX, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) != ESP_OK) {
        printf("[host_hal] TWAI install failed\n");
        return -1;
    }
    if (twai_start() != ESP_OK) {
        printf("[host_hal] TWAI start failed\n");
        return -1;
    }
    printf("[host_hal] CAN 500kbps ready\n");
    return 0;
}

int host_hal_can_send(const HostCanFrame* frame) {
    twai_message_t msg = {
        .identifier = frame->canId,
        .data_length_code = frame->dlc,
    };
    memcpy(msg.data, frame->data, frame->dlc);
    return (twai_transmit(&msg, pdMS_TO_TICKS(5)) == ESP_OK) ? 0 : -1;
}

int host_hal_can_recv(HostCanFrame* frame) {
    twai_message_t msg;
    if (twai_receive(&msg, 0) != ESP_OK) return -1;
    frame->canId = (uint16_t)msg.identifier;
    frame->dlc = msg.data_length_code;
    memcpy(frame->data, msg.data, msg.data_length_code);
    return 0;
}

// --- Sensor reads ---

int host_hal_sensor_ball_loaded(void) {
    return (int)gpio_get_level(PIN_SENSOR_BALL);
}

int host_hal_sensor_tube_ball_present(void) {
    return (int)gpio_get_level(PIN_SENSOR_TUBE);
}

int host_hal_sensor_chamber_ready(void) {
    return (int)gpio_get_level(PIN_SENSOR_CHAMBER);
}

int host_hal_sensor_exit_detected(void) {
    return (int)gpio_get_level(PIN_SENSOR_EXIT);
}

int host_hal_estop_active(void) {
    return (int)gpio_get_level(PIN_ESTOP);
}

// --- Actuators ---

void host_hal_trigger_launch(void) {
    gpio_set_level(PIN_LAUNCH, 1);
    vTaskDelay(pdMS_TO_TICKS(50));
    gpio_set_level(PIN_LAUNCH, 0);
}

void host_hal_feed_request(void) {
    gpio_set_level(PIN_FEED_ACTUATOR, 1);
    vTaskDelay(pdMS_TO_TICKS(100));
    gpio_set_level(PIN_FEED_ACTUATOR, 0);
}

void host_hal_set_status_led(int on) {
    gpio_set_level(PIN_STATUS_LED, on ? 1 : 0);
}

void host_hal_set_buzzer(int on) {
    gpio_set_level(PIN_BUZZER, on ? 1 : 0);
}
