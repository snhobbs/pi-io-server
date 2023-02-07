#include "dac.h"
//#include "adc.h"
#include <bcm2835.h>
#include <EmitterBoard/Hardware.h>
#include <stdbool.h>


void SetupOutputPin(const uint8_t pin) {
  bcm2835_gpio_fsel(pin, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_set_pud(pin, BCM2835_GPIO_PUD_UP);
}

void SetOutputPin(const uint8_t pin, const bool setting) {
  if (setting) {
    bcm2835_gpio_set(pin);
  } else {
    bcm2835_gpio_clr(pin);
  }
}


