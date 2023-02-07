import datetime
from python_utilities import Range


class SystemSettings:
    ClearFaults = False
    CheckAnalogOutputs = False
    SetModbusAddress = False
    kDacBits = 10
    kAdcReadingCount = 255

    kDataDir = "/home/pi/data"
