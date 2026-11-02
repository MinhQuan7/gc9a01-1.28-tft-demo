#pragma once

#include <Arduino.h>

/* Wi-Fi-only stub. DTG headers include PPP.h; this firmware does not use cellular. */

enum ppp_modem_model_t
{
  PPP_MODEM_GENERIC = 0
};

#ifndef ESP_MODEM_MODE_COMMAND
#define ESP_MODEM_MODE_COMMAND 0
#endif

class PPPClass
{
public:
  void begin(int) {}
  void setResetPin(int, bool, uint32_t) {}
  void mode(int) {}
  String cmd(const char *, int) { return String(); }
};
