"""
socat /dev/ttyUSB0,raw,echo=0 SYSTEM:'tee in.txt |socat - \
    "PTY,link=/tmp/ttyUSB0,raw,echo=0,waitslave"|tee out.txt'
"""
import logging

from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

from ._base import BaseDevice


logger = logging.getLogger(__name__)

MODBUS_SETTINGS = {
    'method': 'rtu',
    'port': '/dev/ttyUSB0',
    'baudrate': 9600,
    'stopbits': 1,
    'parity': 'N',
    'bytesize': 8,
    'timeout': 1,
}


class Inverter(BaseDevice):
    client = ModbusSerialClient
    settings = MODBUS_SETTINGS

    @staticmethod
    def readline(inverter_conn):
        try:
            reading = inverter_conn.read_input_registers(0, 45)
            if isinstance(reading, Exception):
                # Fix for PyModbus 'returning' the Exception rather than
                # 'raising' it.
                raise reading
        except ModbusIOException as e:
            logger.error("Lost connection with inverter: %s.", e)
            raise e
        return reading.registers
