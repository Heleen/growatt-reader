import re
import logging

from serial import Serial

from ._base import BaseDevice
from ...utils.config import config


logger = logging.getLogger(__name__)


DEFAULT_SERIAL_SETTINGS = {
    'baudrate': 115200,
    'timeout': 20,
    'port': "/dev/ttyUSB0",
}


class P1Port(BaseDevice):
    client = Serial
    settings = config.get('input', {}).get('p1-port', DEFAULT_SERIAL_SETTINGS)

    @staticmethod
    def readline(p1_port_conn):
        telegram = []
        checksum_line = False
        while not checksum_line:
            try:
                telegram_line = p1_port_conn.readline()
            except Exception as e:
                logger.error("Could not read from P1 port, error: %s.", e)
                raise e
            else:
                telegram.append(telegram_line.decode('ascii').strip())
                if re.match(b'(?=!)', telegram_line):
                    checksum_line = True
        return ','.join(telegram)
