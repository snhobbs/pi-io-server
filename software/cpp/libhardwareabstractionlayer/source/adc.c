/*
 * ADC124S021CIMM
 * Connected to SPI0
 * 4 inputs
 * 12 bit
 * 50-200ksps
 * 4.096V reference
 * 33pF sampling capacitance
 * ~500 Ohms input resistor
 * 1.6e4 * 1e-12 = 1.6e-8 = 16ns time constant -> 10x settling time -> 160ns minimum settling time
 * Input time constant should be << 16ns  
 *  - 1.7k impedance, 10N0 capacitance 17us time constant
 *  - Capacitance voltage divider - 10N into 33pf - 1 part in 30 or 100/4095...
 *  - Increase capacitance on input or decrease resistance 
 * Running at full speed has some crosstalk issues due to settling time
 *
 * Allow current scheme by decreasing clock rate to < 16/160ns
 *  - < 100MHz
 *
 * */
#include <EmitterBoard/Hardware.h>
#include "adc.h"
#include <unistd.h>  //  sleep
#include <bcm2835.h>
#include <assert.h>
#include <sys/mman.h>

int new_bcm2835_spi_begin(void) {
    volatile uint32_t* paddr;

    if (bcm2835_spi0 == MAP_FAILED)
      return 0; /* bcm2835_init() failed, or not root */
    
    /* Set the SPI0 pins to the Alt 0 function to enable SPI0 access on them */
    //  bcm2835_gpio_fsel(RPI_GPIO_P1_26, BCM2835_GPIO_FSEL_ALT0); /* CE1 */
    bcm2835_gpio_fsel(RPI_GPIO_P1_24, BCM2835_GPIO_FSEL_ALT0); /* CE0 */
    bcm2835_gpio_fsel(RPI_GPIO_P1_21, BCM2835_GPIO_FSEL_ALT0); /* MISO */
    bcm2835_gpio_fsel(RPI_GPIO_P1_19, BCM2835_GPIO_FSEL_ALT0); /* MOSI */
    bcm2835_gpio_fsel(RPI_GPIO_P1_23, BCM2835_GPIO_FSEL_ALT0); /* CLK */
    
    /* Set the SPI CS register to the some sensible defaults */
    paddr = bcm2835_spi0 + BCM2835_SPI0_CS/4;
    bcm2835_peri_write(paddr, 0); /* All 0s */
    
    /* Clear TX and RX fifos */
    bcm2835_peri_write_nb(paddr, BCM2835_SPI0_CS_CLEAR);

    return 1; // OK
}

uint16_t bytes_to_u16(const uint8_t upper, const uint8_t lower) {
    return (uint16_t)upper << 8 | (uint16_t)lower;
}

#if 0
void bcm2835_spi_end(void)
{  
    /* Set all the SPI0 pins back to input */
    //  bcm2835_gpio_fsel(RPI_GPIO_P1_26, BCM2835_GPIO_FSEL_INPT); /* CE1 */
    bcm2835_gpio_fsel(RPI_GPIO_P1_24, BCM2835_GPIO_FSEL_INPT); /* CE0 */
    bcm2835_gpio_fsel(RPI_GPIO_P1_21, BCM2835_GPIO_FSEL_INPT); /* MISO */
    bcm2835_gpio_fsel(RPI_GPIO_P1_19, BCM2835_GPIO_FSEL_INPT); /* MOSI */
    bcm2835_gpio_fsel(RPI_GPIO_P1_23, BCM2835_GPIO_FSEL_INPT); /* CLK */
}
#endif
void AdcSetup(void) {
  new_bcm2835_spi_begin();
  bcm2835_spi_setBitOrder(BCM2835_SPI_BIT_ORDER_MSBFIRST);
  bcm2835_spi_setDataMode(BCM2835_SPI_MODE0);  //  Clock rest high, data out valid on rising edge, data in on falling
  //  bcm2835_spi_setDataMode(BCM2835_SPI_MODE3);  //  Clock rest high, data out valid on rising edge, data in on falling
  bcm2835_spi_chipSelect(BCM2835_SPI_CS0);
  bcm2835_spi_setChipSelectPolarity(BCM2835_SPI_CS0, LOW);      // the default
  //  ADC 8-16MHz clock
  // bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_32); /*!< 32 = 7.8125MHz on Rpi2, 12.5MHz on RPI3 */
  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_128); /*!< 32 = 7.8125MHz on Rpi2, 12.5MHz on RPI3 */
  //  bcm2835_spi_setClockDivider(BCM2835_SPI_CLOCK_DIVIDER_16); /*!< 16 = 15.625MHz on Rpi2, 25MHz on RPI3 */
}

void GetAdcOrderArray (uint8_t* adc_order) {
  for (unsigned i=0; i<kChannels; i++) { 
    const unsigned index = 2*i;
    adc_order[index] = (uint8_t)(i << 3);
  }
  return adc_order;
}

#if 0
std::array<uint8_t, 2*kChannels> GetAdcOrderArray (void) {
  std::array<uint8_t, 2*kChannels> adc_order{};
  for (std::size_t i=0; i<kChannels; i++) { 
    const std::size_t index = 2*i;
    assert(index < adc_order.size());
    adc_order[index] = static_cast<uint8_t>(i << 3);
  }
  return adc_order;
}

#if 0
void ReadOneByOne(std::array<uint16_t, kChannels>* data, const std::size_t enabled_channels) {
  for (std::size_t i = 0; i < kChannels; i++) {
    std::array<uint8_t, 2> next_channel {i << 3, 0};
    std::array<uint8_t, 2> din {};
    bcm2835_spi_transfernb(reinterpret_cast<char*>(next_channel.data()), reinterpret_cast<char*>(din.data()), din.size());
    usleep(100);
    (*data)[i] = bytes_to_u16(din[0], din[1]);
  }
}
#endif
#endif
void AdcReadAllChannels(uint16_t* data) {
  const unsigned nbytes = kChannels*2;
  uint8_t adc_order[nbytes];
  uint8_t din[nbytes];
  GetAdcOrderArray(adc_order);
  //uint16_t kAdcOrderArray[] = {
  //  0, 1, 2, 3
  //};
  AdcSetup();
  bcm2835_spi_transfernb(adc_order, din, nbytes);
  usleep(100);
  for (unsigned i = 0; i < kChannels; i++) {
    data[i] = bytes_to_u16(din[i*2], din[i*2+1]);
  }
}

#if 0
void ReadAllChannels(std::array<uint16_t, kChannels>* data) {
  Setup();
  std::array<uint8_t, 2*kChannels> adc_order = GetAdcOrderArray();
  std::array<uint8_t, 2*kChannels> din {};
  bcm2835_spi_transfernb(reinterpret_cast<char*>(adc_order.data()), reinterpret_cast<char*>(din.data()), adc_order.size());
  usleep(100);
  for (std::size_t i = 0; i < kChannels; i++) {
    (*data)[i] = bytes_to_u16(din[i*2], din[i*2+1]);
  }
}
#if 0
//  FIXME ignores the enabled channels for now
void ReadContinuous(std::array<uint16_t, kChannels>* data, const std::size_t enabled_channels) {
  Setup();
  std::array<uint8_t, 2*kChannels> adc_order = GetAdcOrderArray();
  std::array<uint8_t, 2*kChannels> din {};
  bcm2835_spi_transfernb(reinterpret_cast<char*>(adc_order.data()), reinterpret_cast<char*>(din.data()), adc_order.size());
  usleep(100);
  for (std::size_t i = 0; i < kChannels; i++) {
    if (enabled_channels & (1<<i)) {
      (*data)[i] = bytes_to_u16(din[i*2], din[i*2+1]);
    } else {
      (*data)[i] = 0;
    }
  }
}
#endif
void Read(std::array<uint16_t, kChannels>* data) {
  //return ReadContinuous(data, enabled_channels);
  return ReadAllChannels(data);
}
}
#endif

