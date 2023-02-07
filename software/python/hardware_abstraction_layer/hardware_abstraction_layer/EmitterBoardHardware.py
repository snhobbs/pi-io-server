from enum import IntEnum


class AnalogInputs(IntEnum):
    kChannel0 = 0
    kChannel1 = 1
    kChannel2 = 2
    kChannel3 = 3


class EmitterBoardPhotoDiode(IntEnum):
    kChannel0 = 0
    kChannel1 = 1


class EmitterBoardHardware:
    kI2cChannel = 1
    kAdcSpiChannel = 0
    kDacSpiChannel = 1
    kUartChannel = 0
    kNspwr_gpio = 13
    kNdac_clr_gpio = 16
    kNcs_dac_gpio = 26
    kNcs_adc_gpio = 8


class Emitters(IntEnum):
    kWhite = 0
    kRed = 1
    kGreen = 2
    kBlue = 3
    kIR = 4
    kBulbHigh = 5
    kBulbLow = 6
    kNone = 7


LedEmitters = (Emitters.kWhite, Emitters.kRed, Emitters.kBlue, Emitters.kGreen, Emitters.kIR)
ActiveEmitters = tuple([emitter for emitter in Emitters if emitter != Emitters.kNone])


class EmitterBoardHardware:
    serial_port = "/dev/ttyAMA0"
    kEmitterBoardAdcBits = 12
    kEmitterBoardAdcMaxValue = (1 << kEmitterBoardAdcBits) - 1
    kDacBits = 8
    kDacChannels = 8
    kDacOuputMax = (1 << kDacBits) - 1
    pins = {
        "dac_clr": 16,
        "adc_cs": 8,
        "dac_cs": 26,
        "spwr": 13,
        "tx_en": 17,
        "led_sw": 7,
    }
