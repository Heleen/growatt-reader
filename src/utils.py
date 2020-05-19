import logging
import signal
import socket
import sys


logger = logging.getLogger(__name__)


class GracefulKiller:
    """
    Class to gracefully handle interrupts.
    """
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


def get_lock(process_name):
    """
    Without holding a reference to our socket somewhere it gets garbage
    collected when the function exits.
    """
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        get_lock._lock_socket.bind('\0' + process_name)
        logger.info("I got the lock.")
    except socket.error:
        # TODO LOG PID
        logger.warning("Lock already exists, exiting script.")
        sys.exit()
