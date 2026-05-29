#include "protocol_codec.h"
#include <string.h>

static int copy_exact(void* out, const void* in, int len, int expected) {
  if (len != expected) return -1;
  memcpy(out, in, (size_t)expected);
  return expected;
}

int protocol_encode_set_rpm(uint8_t* out, const CanSetRpmFrame* frame) {
  memcpy(out, frame, sizeof(CanSetRpmFrame));
  return (int)sizeof(CanSetRpmFrame);
}

int protocol_encode_status(uint8_t* out, const CanStatusFrame* frame) {
  memcpy(out, frame, sizeof(CanStatusFrame));
  return (int)sizeof(CanStatusFrame);
}

int protocol_encode_heartbeat(uint8_t* out, const CanHeartbeatFrame* frame) {
  memcpy(out, frame, sizeof(CanHeartbeatFrame));
  return (int)sizeof(CanHeartbeatFrame);
}

int protocol_encode_fault(uint8_t* out, const CanFaultFrame* frame) {
  memcpy(out, frame, sizeof(CanFaultFrame));
  return (int)sizeof(CanFaultFrame);
}

int protocol_decode_set_rpm(CanSetRpmFrame* out, const uint8_t* in, int len) {
  return copy_exact(out, in, len, (int)sizeof(CanSetRpmFrame));
}

int protocol_decode_status(CanStatusFrame* out, const uint8_t* in, int len) {
  return copy_exact(out, in, len, (int)sizeof(CanStatusFrame));
}

int protocol_decode_heartbeat(CanHeartbeatFrame* out, const uint8_t* in, int len) {
  return copy_exact(out, in, len, (int)sizeof(CanHeartbeatFrame));
}

int protocol_decode_fault(CanFaultFrame* out, const uint8_t* in, int len) {
  return copy_exact(out, in, len, (int)sizeof(CanFaultFrame));
}
