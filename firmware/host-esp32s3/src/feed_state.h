#pragma once

#include <stdint.h>

enum FeedState {
  FEED_IDLE,
  FEED_WAIT_TUBE_BALL,
  FEED_ACTUATING,
  FEED_WAIT_CHAMBER,
  FEED_READY,
  FEED_SHOT_EXIT,
  FEED_RELOAD_DELAY,
  FEED_JAM,
};

enum FeedFaultReason {
  FEED_FAULT_NONE = 0,
  FEED_FAULT_NO_BALL = 1,
  FEED_FAULT_CHAMBER_TIMEOUT = 2,
  FEED_FAULT_EXIT_TIMEOUT = 3,
  FEED_FAULT_JAM = 4,
};

struct FeedControllerState {
  FeedState state;
  uint32_t stateEnterMs;
  uint8_t jamFault;
  uint8_t faultReason;
};

FeedControllerState* feed_state_get();
void feed_state_reset();
void feed_state_step();
int feed_is_ready();
void feed_request_one_ball();
int feed_fault_active();
uint8_t feed_fault_reason();
