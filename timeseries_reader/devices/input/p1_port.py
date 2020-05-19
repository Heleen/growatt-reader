import re
import logging

from serial import Serial

from timeseries_reader.devices.input._base import BaseDevice
from timeseries_reader.utils.config import config


logger = logging.getLogger(__name__)


DEFAULT_SERIAL_SETTINGS = {
    'baudrate': 115200,
    'timeout': 20,
    'port': "/dev/ttyUSB0",
}


class P1Port(BaseDevice):
    client = Serial
    settings = config.get('input', {}).get('p1-port', DEFAULT_SERIAL_SETTINGS)

    def readline(self):
        telegram = []
        checksum_line = False
        while not checksum_line:
            try:
                telegram_line = self._conn.readline()
            except Exception as e:
                logger.error("Could not read from P1 port, error: %s.", e)
                raise e
            else:
                telegram.append(telegram_line.decode('ascii').strip())
                if re.match(b'(?=!)', telegram_line):
                    checksum_line = True
        return ','.join(telegram)
