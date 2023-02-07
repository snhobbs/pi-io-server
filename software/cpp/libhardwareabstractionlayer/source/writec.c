#include <unistd.h>
#include <sys/ioctl.h>
#include <stdint.h>
#include <bcm2835.h>
#include <assert.h>

const uint8_t DE_PIN = 17;

int init_rs485() {
  //  PRINT_LOCATION();
  int result = bcm2835_init();
  assert(result >= 0);
  bcm2835_gpio_fsel(DE_PIN, BCM2835_GPIO_FSEL_OUTP);
  bcm2835_gpio_set_pud(DE_PIN, BCM2835_GPIO_PUD_UP);
  bcm2835_gpio_clr(DE_PIN);
  return result;
}

ssize_t writec(int fd, char *buf, size_t count) {
  bcm2835_gpio_set(DE_PIN);
  ssize_t r = write(fd, buf, count);
  uint8_t lsr;
  do {
    int r = ioctl(fd, TIOCSERGETLSR, &lsr);
  } while (!(lsr & TIOCSER_TEMT));
  bcm2835_gpio_clr(DE_PIN);
  return r;
}

#if 0
#include <wiringPi.h>

const uint8_t DE_PIN = 0;

int init() {
  wiringPiSetup();
  pinMode(DE_PIN, OUTPUT);
  digitalWrite(DE_PIN, LOW);
}

ssize_t writec(int fd, char *buf, size_t count) {
  digitalWrite(DE_PIN, HIGH);
  ssize_t r = write(fd, buf, count);
  uint8_t lsr;
  do {
    int r = ioctl(fd, TIOCSERGETLSR, &lsr);
  } while (!(lsr & TIOCSER_TEMT));
  digitalWrite(DE_PIN, LOW);
  return r;
}
#endif
    
