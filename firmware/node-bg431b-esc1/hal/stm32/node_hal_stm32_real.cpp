// STM32 real HAL implementation for Motor Node (B-G431B-ESC1)
// Replaces node_hal_bg431b_stub.cpp when targeting real hardware.
//
// Pin assignments — match B-G431B-ESC1 discovery board:
//   FDCAN_TX = PA12, FDCAN_RX = PA11
//   TIM1_CH1 = PA8  (PWM U high-side)
//   TIM1_CH2 = PA9  (PWM V high-side)
//   TIM1_CH3 = PA10 (PWM W high-side)
//   TIM1_CH1N = PB13 (PWM U low-side)
//   TIM1_CH2N = PB14 (PWM V low-side)
//   TIM1_CH3N = PB15 (PWM W low-side)
//   HALL_A = PB6, HALL_B = PB7, HALL_C = PB8
//   DRV_EN = PB12, DRV_FAULT_N = PB11
//   VBUS_SENSE = PA0 (ADC1_IN1)
//   ISENSE_A = PA1 (ADC1_IN2)
//   TEMP_SENSE = PA4 (ADC1_IN6)

#include "node_hal_bg431b.h"

// STM32 HAL includes (provided by STM32Cube framework)
#include "main.h"
#include "fdcan.h"
#include "adc.h"
#include "tim.h"
#include "gpio.h"

// --- Pin definitions (B-G431B-ESC1) ---
#define PIN_DRV_EN          GPIO_PIN_12
#define PIN_DRV_EN_PORT     GPIOB
#define PIN_DRV_FAULT       GPIO_PIN_11
#define PIN_DRV_FAULT_PORT  GPIOB

#define PIN_HALL_A          GPIO_PIN_6
#define PIN_HALL_A_PORT     GPIOB
#define PIN_HALL_B          GPIO_PIN_7
#define PIN_HALL_B_PORT     GPIOB
#define PIN_HALL_C          GPIO_PIN_8
#define PIN_HALL_C_PORT     GPIOB

// ADC channel assignments
#define ADC_CH_VBUS         ADC_CHANNEL_1   // PA0
#define ADC_CH_ISENSE       ADC_CHANNEL_2   // PA1
#define ADC_CH_TEMP         ADC_CHANNEL_6   // PA4

// ADC scaling constants
#define VBUS_DIVIDER_RATIO  11.0f   // 24V through voltage divider
#define VBUS_ADC_REF_MV     3300.0f
#define CURRENT_SENSE_RATIO 0.01f   // shunt resistor ratio (adjust per board)
#define TEMP_NTC_NOMINAL    10000   // NTC nominal resistance at 25°C
#define TEMP_NTC_B_COEFF    3950    // NTC beta coefficient
#define TEMP_SERIES_R       10000   // series resistor

// PWM configuration
#define PWM_FREQ_HZ         20000   // 20kHz switching frequency
#define PWM_PERIOD          4199    // TIM1 clock 84MHz / 20kHz - 1

// ============================================================
// Internal state
// ============================================================

static volatile uint32_t g_tick_ms = 0;

// ============================================================
// HAL interface implementation
// ============================================================

void bg_hal_init(void) {
    // Enable GPIO clocks
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    // Configure DRV_EN as output (default: disabled)
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = PIN_DRV_EN;
    gpio.Mode = GPIO_MODE_OUTPUT_PP;
    gpio.Pull = GPIO_NOPULL;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(PIN_DRV_EN_PORT, &gpio);
    HAL_GPIO_WritePin(PIN_DRV_EN_PORT, PIN_DRV_EN, GPIO_PIN_RESET);

    // Configure DRV_FAULT_N as input with pull-up
    gpio.Pin = PIN_DRV_FAULT;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(PIN_DRV_FAULT_PORT, &gpio);

    // Configure Hall sensor inputs
    gpio.Pin = PIN_HALL_A | PIN_HALL_B | PIN_HALL_C;
    gpio.Mode = GPIO_MODE_INPUT;
    gpio.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(PIN_HALL_A_PORT, &gpio);

    // Configure ADC
    MX_ADC1_Init();

    // Configure TIM1 for 3-phase PWM
    MX_TIM1_Init();

    // Configure FDCAN
    MX_FDCAN1_Init();

    printf("[node_hal] init complete (B-G431B-ESC1)\n");
}

uint32_t bg_hal_millis(void) {
    return HAL_GetTick();
}

// --- CAN (FDCAN) ---

int bg_hal_can_init(void) {
    if (HAL_FDCAN_Start(&hfdcan1) != HAL_OK) {
        printf("[node_hal] FDCAN start failed\n");
        return -1;
    }
    if (HAL_FDCAN_ActivateNotification(&hfdcan1,
            FDCAN_IT_RX_FIFO0_NEW_MESSAGE | FDCAN_IT_RX_FIFO1_NEW_MESSAGE,
            0) != HAL_OK) {
        printf("[node_hal] FDCAN notification activate failed\n");
        return -1;
    }
    printf("[node_hal] FDCAN ready\n");
    return 0;
}

int bg_hal_can_send(const BgCanFrame* frame) {
    FDCAN_TxHeaderTypeDef tx_header = {
        .Identifier = frame->canId,
        .DataLength = frame->dlc << 16, // FDCAN_DLC_BYTES_x
        .TxFrameType = FDCAN_FRAME_CLASSIC,
        .DataLength = frame->dlc == 8 ? FDCAN_DLC_BYTES_8 :
                      frame->dlc == 7 ? FDCAN_DLC_BYTES_7 :
                      frame->dlc == 6 ? FDCAN_DLC_BYTES_6 :
                      frame->dlc == 5 ? FDCAN_DLC_BYTES_5 :
                      frame->dlc == 4 ? FDCAN_DLC_BYTES_4 :
                      frame->dlc == 3 ? FDCAN_DLC_BYTES_3 :
                      frame->dlc == 2 ? FDCAN_DLC_BYTES_2 :
                      FDCAN_DLC_BYTES_1,
        .IdType = FDCAN_STANDARD_ID,
        .BitState = FDCAN_CALC_BITPOINT,
    };
    return (HAL_FDCAN_AddMessageToTxFifoQ(&hfdcan1, &tx_header,
                                            (uint8_t*)frame->data) == HAL_OK)
           ? 0 : -1;
}

int bg_hal_can_recv(BgCanFrame* frame) {
    FDCAN_RxHeaderTypeDef rx_header;
    if (HAL_FDCAN_GetRxFifoFillLevel(&hfdcan1, FDCAN_RX_FIFO0) > 0) {
        if (HAL_FDCAN_GetRxMessage(&hfdcan1, FDCAN_RX_FIFO0,
                                    &rx_header, frame->data) == HAL_OK) {
            frame->canId = (uint16_t)rx_header.Identifier;
            frame->dlc = (uint8_t)(rx_header.DataLength >> 16);
            return 0;
        }
    }
    return -1;
}

// --- Motor control ---

void bg_hal_motor_enable(int enable) {
    HAL_GPIO_WritePin(PIN_DRV_EN_PORT, PIN_DRV_EN,
                      enable ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

void bg_hal_set_target_rpm(int rpm) {
    // Convert RPM to PWM duty cycle
    // Max RPM for 6374 at 24V is roughly 3000rpm
    // TIM1 ARR is PWM_PERIOD, so duty = (rpm / RPM_MAX) * PWM_PERIOD
    if (rpm <= 0) {
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, 0);
        __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, 0);
        return;
    }
    uint32_t duty = (uint32_t)((uint32_t)rpm * PWM_PERIOD / 3000);
    if (duty > PWM_PERIOD) duty = PWM_PERIOD;
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_1, duty);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_2, duty);
    __HAL_TIM_SET_COMPARE(&htim1, TIM_CHANNEL_3, duty);
}

// --- Sensor reads ---

int bg_hal_get_actual_rpm(void) {
    // TODO: implement Hall-based RPM calculation
    // For now, return 0 — real implementation uses Hall state transitions
    // and timer capture to compute RPM.
    return 0;
}

uint16_t bg_hal_get_bus_voltage_x10(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint32_t adc_val = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    // Convert: adc_val -> millivolts -> real voltage (with divider) -> x10
    float mv = (float)adc_val * VBUS_ADC_REF_MV / 4095.0f;
    float v_real = mv * VBUS_DIVIDER_RATIO / 1000.0f;
    return (uint16_t)(v_real * 10.0f);
}

uint16_t bg_hal_get_phase_current_x10(void) {
    // TODO: implement ADC-based current sensing
    // Requires injected ADC conversion triggered by PWM for同步采样
    return 0;
}

int16_t bg_hal_get_temp_x10(void) {
    HAL_ADC_Start(&hadc1);
    HAL_ADC_PollForConversion(&hadc1, 10);
    uint32_t adc_val = HAL_ADC_GetValue(&hadc1);
    HAL_ADC_Stop(&hadc1);
    // NTC thermistor calculation
    float v_adc = (float)adc_val * VBUS_ADC_REF_MV / 4095.0f;
    float r_ntc = v_adc * TEMP_SERIES_R / (VBUS_ADC_REF_MV - v_adc);
    float temp_k = 1.0f / (1.0f / 298.15f + (1.0f / TEMP_NTC_B_COEFF) *
                   (r_ntc / TEMP_NTC_NOMINAL - 1.0f));
    float temp_c = temp_k - 273.15f;
    return (int16_t)(temp_c * 10.0f);
}

int bg_hal_driver_fault_active(void) {
    // DRV_FAULT_N is active-low
    return (HAL_GPIO_ReadPin(PIN_DRV_FAULT_PORT, PIN_DRV_FAULT) == GPIO_PIN_RESET);
}
