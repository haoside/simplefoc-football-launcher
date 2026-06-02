#include "env_profiles.h"
#include <string.h>

static const EnvProfile g_profiles[] = {
  {"e0", 20, 50, 0, "none"},
  {"e1", 16, 60, 20, "none"},
  {"e1_leftwind", 16, 60, 20, "left"},
  {"e1_rightwind", 16, 60, 20, "right"},
  {"e2", 6, 45, 40, "none"},
  {"e2_leftwind", 6, 45, 40, "left"},
};

const EnvProfile* host_get_env_profiles(int* count) {
  if (count) *count = (int)(sizeof(g_profiles) / sizeof(g_profiles[0]));
  return g_profiles;
}

const EnvProfile* host_find_env_profile(const char* name) {
  int count = 0;
  const EnvProfile* p = host_get_env_profiles(&count);
  for (int i = 0; i < count; ++i) {
    if (strcmp(p[i].name, name) == 0) return &p[i];
  }
  return 0;
}
