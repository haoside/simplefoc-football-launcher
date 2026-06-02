#include "shot_presets.h"
#include "host_state.h"

static const ShotPreset g_presets[] = {
  {"straight_pass", 2100, 0, 10, 15, 0, STRAIGHT},
  {"light_left_curve", 2100, 150, 12, 16, 10, LEFT_CURVE},
  {"light_right_curve", 2100, 150, 12, 16, 10, RIGHT_CURVE},
  {"standard_left_curve", 2400, 250, 14, 20, 20, LEFT_CURVE},
  {"standard_right_curve", 2400, 250, 14, 20, 20, RIGHT_CURVE},
  {"curve_drop_left", 2300, 220, 15, 18, 15, LEFT_CURVE},
  {"curve_drop_right", 2300, 220, 15, 18, 15, RIGHT_CURVE},
  {"standard_left_curve_wind_left", 2400, 220, 14, 20, 20, LEFT_CURVE},
  {"standard_left_curve_wind_right", 2400, 280, 14, 20, 20, LEFT_CURVE},
  {"standard_right_curve_wind_left", 2400, 280, 14, 20, 20, RIGHT_CURVE},
  {"standard_right_curve_wind_right", 2400, 220, 14, 20, 20, RIGHT_CURVE},
};

const ShotPreset* host_get_shot_presets(int* count) {
  if (count) *count = (int)(sizeof(g_presets) / sizeof(g_presets[0]));
  return g_presets;
}
