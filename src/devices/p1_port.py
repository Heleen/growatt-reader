import re
import logging

from serial import Serial

from .base import BaseDevice


logger = logging.getLogger(__name__)


SERIAL_SETTINGS = {
    'baudrate': 115200,
    'timeout': 20,
    'port': "/dev/ttyUSB0",
}


class P1Port(BaseDevice):
    client = Serial
    settings = SERIAL_SETTINGS

    @staticmethod
    def readline(p1_port):
        telegram = []
        checksum_line = False
        while not checksum_line:
            try:
                telegram_line = p1_port.readline()
            except Exception as e:
                logger.error("Could not read from P1 port, error: %s.", e)
                raise e
            else:
                telegram.append(telegram_line.decode('ascii').strip())
                if re.match(b'(?=!)', telegram_line):
                    checksum_line = True
        return ','.join(telegram)
