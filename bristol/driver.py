import logging
import asyncio
from telnetlib import Telnet
import time
import serial
#from highfinesse import wlm_constants as wlm
#from enum import IntEnum
try:  # permits running in simulation mode on linux
    from ctypes import windll, c_double, c_ushort, c_long, c_bool, byref, c_short
    from ctypes import c_char_p, create_string_buffer, pointer
except ImportError:
    pass

logger = logging.getLogger(__name__)

class WMException(Exception):
    """ Raised on errors involving the WLM interface library (windata.dll) """
    def __init__(self, value):
        s = 'WMException: {}'.format(value)
        logger.warning(s)


class Bristol:
    def __init__(self, simulation = False):
        self.simulation = simulation
        if self.simulation:
            logger.info('simulation mode active')
            return
        else:
            self.tn = Telnet("192.168.1.88")
            self.ser = serial.Serial()
            self.ser.baudrate = 57600
            self.ser.port = '/dev/ttyUSB0'
            self.ser.timeout = None
            print(self.ser)
            self.ser.open()


    async def _ser_send(self, cmd, get_response=True):
        #Send a string to the serial port.

        # Low-level routine for sending serial commands to device. It sends
        # strings and listens for a response terminated by a carriage return.
        # example:
        # ser_send("F0 1.0") # sets the freq of channel 0 to 1.0 MHz

        if self.simulation:
            logger.info("simulation _ser_send(\"%s\")", cmd)
        else:
            logger.debug("_ser_send(\"%s\")", cmd)
            await self.tn.write((cmd + "\n").encode())
            if get_response:
                result = (await self.tn.read_very_eager()).rstrip().decode()
                logger.debug("got response from device: %s", result)
                """if result != "OK":
                    errstr = self.error_codes.get(result, "Unrecognized reply")
                    s = "Erroneous reply from device: {ec}, {ecs}".format(
                        ec=result, ecs=errstr)
                    raise ValueError(s)"""
                return result

            pass

    async def get_status(self):
        """Hook for async loop."""
        # TODO implement this
        pass

    async def ping(self):
        if self.simulation:
            logger.debug('ping simulation')
            return
        try:
            await self.get_status()
        except asyncio.CancelledError:
            raise
        except Exception:
            raise WMException('ping failed')
            return
        logger.debug("ping successful")

    async def get_freq(self):
        """ Returns the temperature of the wavemeter in C """
        if self.simulation:
            return 25.0


        freq = await self._ser_send(":MEAS:FREQ?")

        if freq < 0:
            raise WMException(
                "Error reading WLM temperature: {}".format(freq))
            return 0
        return freq

    async def get_power(self):
        """ Returns the temperature of the wavemeter in C """
        if self.simulation:
            return 25.0

        power = await self._ser_send(":MEAS:POWer?")

        if power < 0:
            raise WMException(
                "Error reading WLM temperature: {}".format(power))
            return 0
        return power

    async def change_channel(self, ch):
        if self.simulation:
            return ch
        if ch in [0, 1, 2, 3, 4, 5, 6, 7]:
            command = "ch" + str(ch) + "\r\n"
            self.ser.write(command.encode())
            self.ser.write(b'ch?\r\n')
            ret = await self.ser.read(size=3)
            print(ret.decode())
        else:
            raise WMException(
                "Error reading WLM temperature: {}".format(ch))
            return 0

    async def reset(self):
        self._ser_send("*RST", get_response= False)



