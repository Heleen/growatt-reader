import logging

from contextlib import contextmanager


logger = logging.getLogger(__name__)


class BaseDevice:
    client = NotImplementedError
    settings = NotImplementedError

    @staticmethod
    def readline(device_conn):
        raise NotImplementedError

    @contextmanager
    @classmethod
    def connect(cls):
        """
        Set up a connection with the inverter.
        """
        try:
            with cls.client(**cls.settings) as device:
                logging.info('Connected, start reading from device...')
                yield device
                logging.info("Stopped reading from device.")
        except Exception as e:
            logging.warning(
                "Did not manage to obtain a connection with the device.", e)
        finally:
            logging.warning("Lost connection with device.")

