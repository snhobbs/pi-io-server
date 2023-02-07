#pragma once
#include <stdint.h>
#include <bcm2835.h>
#include <stdio.h>
#include <stdbool.h>

#define PRINT_LOCATION() {printf("%s: %s: %s\t%s\n", __FILE__, __func__, __LINE__, __TIME__);}
enum Pins {
spwr = 13,
dac_clr = 16,
dac_cs = 26,
adc_cs = 8,
led_sw = 7,
};

enum Emitter {
  kWhiteLed,
  kGreenLed,
  kRedLed,
  kBlueLed,
  kIrLed,
  kBulb24,
  kBulb12,
};


enum AdcChannel {
  kNone,
  kCh0,
  kCh1,
  kCh2,
  kCh3,
};

void SetupOutputPin(const uint8_t pin);
void SetOutputPin(const uint8_t pin, const bool setting);
