#pragma once

#include "protocol.h"
#include <stdint.h>

int protocol_encode_set_rpm(uint8_t* out, const CanSetRpmFrame* frame);
int protocol_encode_status(uint8_t* out, const CanStatusFrame* frame);
int protocol_encode_heartbeat(uint8_t* out, const CanHeartbeatFrame* frame);
int protocol_encode_fault(uint8_t* out, const CanFaultFrame* frame);

int protocol_decode_set_rpm(CanSetRpmFrame* out, const uint8_t* in, int len);
int protocol_decode_status(CanStatusFrame* out, const uint8_t* in, int len);
int protocol_decode_heartbeat(CanHeartbeatFrame* out, const uint8_t* in, int len);
int protocol_decode_fault(CanFaultFrame* out, const uint8_t* in, int len);
