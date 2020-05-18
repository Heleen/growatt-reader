from contextlib import contextmanager

from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ConnectionException
from pymodbus.exceptions import ModbusIOException

MODBUS_SETTINGS = {
    'method': 'rtu',
    'port': '/dev/ttyUSB0',
    'baudrate': 9600,
    'stopbits': 1,
    'parity': 'N',
    'bytesize': 8,
    'timeout': 1,
}


def readline(inverter):
    reading = inverter.read_input_registers(0, 45)
    if isinstance(reading, Exception):
        # Fix for PyModbus 'returning' the Exception rather than
        # 'raising' it.
        raise reading
    except ModbusIOException as e:
        logging.error("Lost connection with inverter: %s.", e)
        raise e
    return reading.registers


@contextmanager
def connect_to_device(port):
    """
    Set up a connection with the inverter.
    """
    modbus_settings = MODBUS_SETTINGS
    modbus_settings['port'] = port
    try:
        with ModbusSerialClient(**modbus_settings) as inverter:
            logging.info('Connected, start reading from inverter...')
            yield inverter
            logging.info("Stopped reading from inverter.")
    except ConnectionException as e:
        logging.warning(
            "Did not manage to obtain a connection with the inverter.", e)
    finally:
        logging.warning("Lost connection with inverter.")
