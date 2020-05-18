from contextlib import contextmanager


SERIAL_SETTINGS = {
    'baudrate': 115200,
    'timeout': 20,
    'port': "/dev/ttyUSB0",
}


def _read_telegram():
    telegram = ""
    checksum = False
    while not checksum:
        telegram_line = ser.readline()
        telegram += telegram_line.decode('ascii').strip()
        if re.match(b'(?=!)', telegram_line):
            checksum = True
    return telegram


def read_from_device():


@contextmanager
def connect_to_device(port):
    """
    Set up a connection with the inverter.
    """
    serial_settings = SERIAL_SETTINGS
    serial_settings['port'] = port

    ser = serial.Serial(port, 115200, 20)

    try:
        with serial.Serial(**serial_settings) as device:
            logging.info('Connected, start reading from p1 port...')
            yield device
            logging.info("Stopped reading from p1 port.")
    except ConnectionException as e:
        logging.warning(
            "Did not manage to obtain a connection with the p1 port.", e)
    finally:
        logging.warning("Lost connection with inverter.")

