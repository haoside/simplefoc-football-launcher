#pragma once

#ifdef __cplusplus
extern "C" {
#endif

void simplefoc_adapter_init(void);
void simplefoc_adapter_set_target_rpm(int rpm);
int simplefoc_adapter_get_actual_rpm(void);
int simplefoc_adapter_get_bus_voltage_x10(void);
int simplefoc_adapter_get_phase_current_x10(void);
int simplefoc_adapter_get_temp_x10(void);
int simplefoc_adapter_has_fault(void);

#ifdef __cplusplus
}
#endif
