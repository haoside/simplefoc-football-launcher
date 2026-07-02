// Arduino framework bridge — forwards setup()/loop() to our main entry point.
// Only compiled when framework = arduino.
#ifdef ARDUINO
#include <Arduino.h>

extern "C" void app_entry();

void setup() {
  app_entry();
}

void loop() {
  // app_entry() contains the main while(1) loop, so this is never reached.
  // Arduino requires loop() to exist.
}
#endif
