bool safety_can_fire(bool estop, bool chamberReady) {
  return !estop && chamberReady;
}
