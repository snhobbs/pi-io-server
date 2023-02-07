import subprocess, os
from subprocess import TimeoutExpired
import datetime as dt
import datetime
import tempfile
import ctypes
import serial
import serial.rs485
import serial.serialutil

# import spidev
# import smbus
from enum import IntEnum
from time import sleep
from . import EmitterBoardHardware, AnalogInputs, LedEmitters


def ReadAdcValues(prog_std_out):
    if type(prog_std_out) is bytes:
        prog_std_out = prog_std_out.decode("utf-8")

    values = []
    for line in prog_std_out.strip().split("\n"):
        if line.count(",") == 3:
            split = line.split(",")
            values.append([int(pt) for pt in split])
    return values


"""
- I2C EEPROM
- SPI ADC
- Output Power GPIO
- LED GPIO
- DAC SPI
- DAC GPIO Clear
- RS485
"""


class RS485Serial(serial.rs485.RS485):
    def __init__(self, *args, **kwargs):
        clib = kwargs.pop("clib")
        self.clib = clib
        super().__init__(*args, **kwargs)

    def write(self, b):
        d = serial.serialutil.to_bytes(b)
        r = self.clib.writec(self.fileno(), d, len(d))
        return r


class AdcData(ctypes.Array):
    _length_ = 4
    _type_ = ctypes.c_uint16


class EmitterBoardSerial(EmitterBoardHardware):
    def __init__(self, clib=None):
        self.clib = clib
        if self.clib == None:
            self.clib = ctypes.cdll.LoadLibrary("/home/pi/libemitterboard.so")

    def get_rs485_socket(self, baudrate=9600):
        parity = "N"
        bytesize = 8
        stopbits = 1
        method = "rtu"
        timeout_seconds = 0.5
        self.clib.init_rs485()

        socket = RS485Serial(
            clib=self.clib,
            port=self.serial_port,
            parity=parity,
            timeout=timeout_seconds,
            bytesize=bytesize,
            stopbits=stopbits,
            baudrate=baudrate,
        )
        return socket


class EmitterBoard(EmitterBoardHardware):
    def __init__(self):
        self.clib = ctypes.cdll.LoadLibrary("/home/pi/libemitterboard.so")
        self.clib.bcm2835_init()
        self.init_gpios()
        self.serial = EmitterBoardSerial(self.clib)
        self.serial_port = self.serial.serial_port

    def get_rs485_socket(self, *args, **kwargs):
        return self.serial.get_rs485_socket(*args, **kwargs)

    def reset(self):
        self.set_sensor_power(False)
        self.turn_on_pi_leds()
        self.reset_emitters()

    def reset_emitters(self):
        for i in range(self.kDacChannels):
            self.dac_write_channel(i, 0)
            self.set_led_sw(False)

    def turn_off_pi_leds(self):
        os.system('sudo sh -c "echo none > /sys/class/leds/led0/trigger"')
        os.system('sudo sh -c "echo 0 > /sys/class/leds/led0/brightness"')
        os.system('sudo sh -c "echo none > /sys/class/leds/led1/trigger"')
        os.system('sudo sh -c "echo 0 > /sys/class/leds/led1/brightness"')

    def turn_on_pi_leds(self):
        os.system('sudo sh -c "echo mmc0 > /sys/class/leds/led0/trigger"')
        os.system('sudo sh -c "echo input > /sys/class/leds/led1/trigger"')

    def init_gpios(self):
        self.clib.SetupOutputPin(self.pins["spwr"])
        self.clib.SetupOutputPin(self.pins["adc_cs"])
        self.clib.SetupOutputPin(self.pins["dac_cs"])
        self.clib.SetupOutputPin(self.pins["dac_clr"])
        self.clib.SetupOutputPin(self.pins["led_sw"])
        self.clib.SetupOutputPin(self.pins["tx_en"])

    def deinit_gpios(self):
        pass

    def dac_setup(self):
        self.clib.DacSetup()

    def dac_write_blocking(self, code, value):
        self.clib.DacWrite(code, value)

    def dac_write_channel(self, channel, value):
        self.clib.DacWriteChannel(channel, value)

    def setup_adc(self):
        self.clib.AdcSetup()

    def adc_read_blocking(self):
        data = AdcData()
        self.clib.AdcReadAllChannels(ctypes.pointer(data))
        return data

    def i2c_write_blocking(self, slave_address, data):
        pass

    def i2c_read_blocking(self, slave_address, points):
        pass

    def set_led_sw(self, enable):
        self.clib.SetOutputPin(self.pins["led_sw"], enable)

    def set_adc_cs(self, enable):
        self.clib.SetOutputPin(self.pins["adc_cs"], enable)

    def set_sensor_power(self, enable):
        self.clib.SetOutputPin(self.pins["spwr"], enable)

    def set_dac_clear(self, enable):
        self.clib.SetOutputPin(self.pins["dac_clr"], enable)

    def set_dac_cs(self, enable):
        self.clib.SetOutputPin(self.pins["dac_cs"], enable)

    def set_tx_en(self, enable):
        self.clib.SetOutputPin(self.pins["tx_en"], enable)

    def read_analog_channels(self, channels=AnalogInputs, npoints=64, frequency=1000):
        data = []
        for i in range(npoints):
            sleep(1.0 / frequency)
            data.append(self.adc_read_blocking())

        data = [[line[ch] for ch in channels] for line in data]
        return data

    def SetEmitter(self, emitter, setting):
        self.dac_write_channel(int(emitter), setting)


"""
class EmitterBoard:
    def __call__(self, run_config):
        return self.run(run_config)

    def thread(self, run_config, q, output_file=None):
        data = self.run(run_config, output_file)
        q.put(data)

    def SetEmitter(self, emitter, setting):
        kProgram = "/home/pi/.local/bin/emitter_control"
        call = ["sudo", kProgram, emitter.name.strip("k").lower(), str(setting)]
        # print(" ".join(call))
        subprocess.call(call)

    def read_analog_channels(self, channels=AnalogInputs, npoints=64, frequency=1000):

        kProgram = "/home/pi/.local/bin/emitter_board_read_analog_channels"
        output_id, output_file = tempfile.mkstemp(suffix=None, prefix="TestJig_emitter_board_read_analog_channels_output")
        with subprocess.Popen(["sudo", kProgram, str(npoints), str(frequency), output_file], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            try:
                outs, errs = proc.communicate(timeout=30)
                #print(outs)
                #print(errs)
            except TimeoutExpired as e:
                pass

            proc.wait(timeout = 30)
            if proc.poll() == None:
                # still alive
                print("Process is still alive")
                proc.kill()

        data = None
        with open(output_file, 'r') as f:
            data = ReadAdcValues(f.read())
        data = [[line[ch] for ch in channels] for line in data]
        return data

    def run(self, run_config, output_file=None):
        kProgram = "/home/pi/.local/bin/emitter_board_data_run"

        tmp_file = tempfile.mkstemp(suffix=None, prefix="TestJig_run_config")
        config_id, config_file = tmp_file
        with open(config_file, "w") as f:
            f.write(str(run_config))

        if output_file is None:
            output_id, output_file = tempfile.mkstemp(suffix=None, prefix="TestJig_emitter_control_output")

        #try:
        #    os.mkfifo(output_file)
        #except OSError as e:
        #    pass
        #print("Failed to create FIFO: %s"%e)

        with open(output_file, 'w') as f:
            f.write(str(run_config))

        with subprocess.Popen(["sudo", kProgram, config_file, output_file], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            try:
                outs, errs = proc.communicate(timeout=30)
                #print(outs)
                #print(errs)
            except TimeoutExpired as e:
                pass

            proc.wait(timeout = 30)
            if proc.poll() == None:
                # still alive
                print("Process is still alive")
                proc.kill()

        data = None
        with open(output_file, 'r') as f:
            read = f.read()
            data = ReadAdcValues(read)
        assert(len(data) > 0)
        data_file = EmitterBoardDataFile(run_config, data, datetime.datetime.now(), run_id=0, file_name=output_file)
        data_file.save()
        try:
            os.remove(config_file)
        except FileNotFoundError:
            pass
        return data
"""

"""
from RPi import GPIO
class RS485Serial(serial.Serial):
#class RPiRs485Serial(serial.Serial):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setup(17, GPIO.OUT)
        self.mode = True
        #GPIO.output(17, not self.mode)
        self.set_output_flow_control(True)
        self.set_input_flow_control(True)

    def read(self, *args, **kwargs):
        #GPIO.output(17, not self.mode)
        print("recv")
        rec = super().read(*args, **kwargs)
        print(rec)
        return rec

    def write(self, *args, **kwargs):
        print("sending", __class__)
        #GPIO.output(17, self.mode)
        try:
            #super().write(*args, **kwargs)
            #self._write_timeout = 10
            super().write(args[0])
        finally:
            pass
            #GPIO.output(17, not self.mode)
"""


"""
class RS485Serial(serial.rs485.RS485):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=False,
            rts_level_for_rx=True,
            loopback=None,
            delay_before_tx=None,
            delay_before_rx=None)
        #self.setRTS(True)
        self.write(''.encode('utf-8')) # required

    def write(self, *args, **kwargs):
        try:
            print("write", args)
            #super().write(*args, **kwargs)
            super().write(args[0])
        except:
            print("Write failed")
            raise

        finally:
            pass
            #self.setRTS(True)
"""
