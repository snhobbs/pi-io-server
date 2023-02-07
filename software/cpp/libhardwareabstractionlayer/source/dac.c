#include "dac.h"
#include <unistd.h>  //  sleep
#include <bcm2835.h>
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/mman.h>

#include <EmitterBoard/Hardware.h>

void DacSetup(void) {
  //  bcm2835_spi_end();
  bcm2835_aux_spi_begin();
  bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);
  bcm2835_spi_setDataMode(BCM2835_SPI_MODE3);  //  Clock rest high, data out valid on falling edge, data in on rising

  bcm2835_spi_chipSelect(BCM2835_SPI_CS_NONE); //  bit bang
  bcm2835_aux_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_512); // 1.95MHz, ADC has max of 3.5MHz

  //  ATTENTION PIN SETUP HAS TO HAPPEN AFTER PERIPHERAL SETUP... for some reason
  SetupOutputPin(dac_clr);
  SetupOutputPin(dac_cs);

  SetOutputPin(dac_clr, true);
  SetOutputPin(dac_cs, true);
}

void DacWrite(const uint16_t write_code, const uint8_t value) {
  DacSetup();
  SetOutputPin(dac_cs, false);
  usleep(10);
  const uint16_t shifted_value = ((uint16_t)value)<<4;
  bcm2835_aux_spi_write((write_code + shifted_value)&0xfff0);
  usleep(10);
  SetOutputPin(dac_cs, true);
}

void DacWriteChannel(const uint16_t channel, const uint8_t value) {
  const uint16_t write_code = ((channel + 1) << 12);
  DacWrite(write_code, value);
  //  usleep(1e5);
}
