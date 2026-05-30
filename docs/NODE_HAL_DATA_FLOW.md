# Node HAL 数据流 v1

## 目标
把 `simplefoc_adapter` 从内部模拟数据，推进到通过 `node_hal_*` 获取底层信号。

## 当前链路
1. `simplefoc_adapter_set_target_rpm()`
   - 调 `node_hal_pwm_enable()`
2. `simplefoc_adapter_get_actual_rpm()`
   - 调 `read_hall_rpm()`
3. `read_hall_rpm()`
   - 调 `node_hal_read_hall_a/b/c()`
4. `simplefoc_adapter_get_bus_voltage_x10()`
   - 调 `node_hal_read_vbus_x10()`
5. `simplefoc_adapter_get_phase_current_x10()`
   - 调 `node_hal_read_current_x10()`
6. `simplefoc_adapter_get_temp_x10()`
   - 调 `node_hal_read_temp_x10()`
7. `simplefoc_adapter_has_fault()`
   - 调 `node_hal_driver_fault_active()`

## 当前边界
- Hall RPM 仍是占位算法
- 还没接真实 TIM/捕获计算
- 还没接真实 `node_hal_pwm_set_uvw()`
- 但数据来源已从 adapter 私有假值切到 HAL 接口
