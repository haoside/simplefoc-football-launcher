#pragma once

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
  const char* name;
  int tempC;
  int humidityPct;
  int windSpeedDmps;
  const char* windDir;
} EnvProfile;

const EnvProfile* host_get_env_profiles(int* count);
const EnvProfile* host_find_env_profile(const char* name);

#ifdef __cplusplus
}
#endif
