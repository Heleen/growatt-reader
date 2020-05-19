import logging

from contextlib import ContextDecorator


logger = logging.getLogger(__name__)


class BaseDevice:
    client = NotImplementedError
    settings = NotImplementedError

    def __init__(self):
        self._conn = None

    def readline(self):
        raise NotImplementedError

    def open(self):
        try:
            self._conn = self.client(**self.settings)
        except Exception as e:
            logging.warning(
                "Did not manage to obtain a connection with the device.", e)
        else:
            logging.info('Connected, start reading from device...')
        return self

    def close(self):
        self.__conn.close()
        logging.warning("Lost connection with device.")


class DeviceManager(ContextDecorator):
    def __init__(self, Device):
        self._Device = Device

    def __enter__(self):
        self.object = self._Device()
        self.object.open()
        return self.object

    def __exit__(self):
        return self.object.close()
