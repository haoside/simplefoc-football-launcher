#include "host_fault.h"

static uint8_t g_faultActive = 0;
static uint8_t g_faultCode = 0;
static uint8_t g_faultSource = 0;

void host_fault_raise(uint8_t faultCode, uint8_t sourceNodeId) {
  g_faultActive = 1;
  g_faultCode = faultCode;
  g_faultSource = sourceNodeId;
}

int host_fault_is_active(void) {
  return g_faultActive;
}

uint8_t host_fault_code(void) {
  return g_faultCode;
}

uint8_t host_fault_source(void) {
  return g_faultSource;
}

void host_fault_clear(void) {
  g_faultActive = 0;
  g_faultCode = 0;
  g_faultSource = 0;
}
