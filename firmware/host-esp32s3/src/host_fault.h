#pragma once

#include <stdint.h>

void host_fault_raise(uint8_t faultCode, uint8_t sourceNodeId);
int host_fault_is_active(void);
uint8_t host_fault_code(void);
uint8_t host_fault_source(void);
void host_fault_clear(void);
