#include "../../common/config.h"
#include "../../common/protocol.h"
#include "hal/host_hal.h"
#include "host_fault.h"
#include "host_state.h"
#include "feed_state.h"

static FeedControllerState g_feed = {FEED_IDLE, 0, 0, FEED_FAULT_NONE};

static void feed_enter(FeedState next) {
  HostState* hs = host_state_get();
  g_feed.state = next;
  g_feed.stateEnterMs = host_hal_millis();
  hs->telemetry.feedState = (uint8_t)next;
}

static uint32_t feed_elapsed_ms() {
  return host_hal_millis() - g_feed.stateEnterMs;
}

static void feed_raise_fault(uint8_t reason, uint8_t hostFaultCode) {
  HostState* hs = host_state_get();
  g_feed.jamFault = 1;
  g_feed.faultReason = reason;
  hs->telemetry.feedFaultReason = reason;
  host_fault_raise(hostFaultCode, 0xF0);
  feed_enter(FEED_JAM);
}

FeedControllerState* feed_state_get() {
  return &g_feed;
}

void feed_state_reset() {
  HostState* hs = host_state_get();
  g_feed.state = FEED_IDLE;
  g_feed.stateEnterMs = host_hal_millis();
  g_feed.jamFault = 0;
  g_feed.faultReason = FEED_FAULT_NONE;
  hs->telemetry.feedState = FEED_IDLE;
  hs->telemetry.feedFaultReason = FEED_FAULT_NONE;
}

int feed_fault_active() {
  return g_feed.jamFault ? 1 : 0;
}

uint8_t feed_fault_reason() {
  return g_feed.faultReason;
}

int feed_is_ready() {
  return g_feed.state == FEED_READY;
}

void feed_request_one_ball() {
  HostState* hs = host_state_get();
  if (!hs->sensors.tubeBallPresent) {
    feed_raise_fault(FEED_FAULT_NO_BALL, FAULT_NO_BALL_AT_CHAMBER);
    return;
  }
  if (g_feed.state == FEED_READY) {
    host_hal_feed_request();
    feed_enter(FEED_WAIT_CHAMBER);
  }
}

void feed_state_step() {
  HostState* hs = host_state_get();
  hs->sensors.tubeBallPresent = (uint8_t)host_hal_sensor_tube_ball_present();
  hs->sensors.chamberReady = (uint8_t)host_hal_sensor_chamber_ready();
  hs->sensors.exitDetected = (uint8_t)host_hal_sensor_exit_detected();

  switch (g_feed.state) {
    case FEED_IDLE:
      if (hs->sensors.tubeBallPresent) feed_enter(FEED_READY);
      else feed_enter(FEED_WAIT_TUBE_BALL);
      break;
    case FEED_WAIT_TUBE_BALL:
      if (hs->sensors.tubeBallPresent) feed_enter(FEED_READY);
      break;
    case FEED_ACTUATING:
      feed_enter(FEED_WAIT_CHAMBER);
      break;
    case FEED_WAIT_CHAMBER:
      if (hs->sensors.chamberReady) {
        feed_enter(FEED_SHOT_EXIT);
      } else if (feed_elapsed_ms() > FEED_TO_CHAMBER_TIMEOUT_MS) {
        feed_raise_fault(FEED_FAULT_CHAMBER_TIMEOUT, FAULT_BALL_JAM);
      }
      break;
    case FEED_READY:
      if (!hs->sensors.tubeBallPresent) feed_enter(FEED_WAIT_TUBE_BALL);
      break;
    case FEED_SHOT_EXIT:
      if (hs->sensors.exitDetected) {
        feed_enter(FEED_RELOAD_DELAY);
      } else if (feed_elapsed_ms() > FIRE_TO_EXIT_TIMEOUT_MS) {
        feed_raise_fault(FEED_FAULT_EXIT_TIMEOUT, FAULT_BALL_JAM);
      }
      break;
    case FEED_RELOAD_DELAY:
      if (feed_elapsed_ms() > RELOAD_DELAY_MS) {
        feed_enter(FEED_WAIT_TUBE_BALL);
      }
      break;
    case FEED_JAM:
    default:
      break;
  }
}
