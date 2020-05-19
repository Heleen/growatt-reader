#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service to periodically read from a Growatt inverter connected on a serial port
with the Modbus protocol and write the results to a CSV file.


socat /dev/ttyUSB0,raw,echo=0 SYSTEM:'tee in.txt |socat - \
    "PTY,link=/tmp/ttyUSB0,raw,echo=0,waitslave"|tee out.txt'
"""

import argparse
import logging
import time

from .reader import reader
from .utils import get_lock
from .utils import GracefulKiller


try:
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename='/var/log/growatt/growatt_reader.log',
        level=logging.INFO)
except FileNotFoundError:
    logging.basicConfig()
logging.info('Enter Growatt Reader Script')


if __name__ == '__main__':
    """
    Set up a connection with the inverter. When the connection is broken try
    to reconnect every X seconds.
    While connection with inverter is live, periodically read from the inverter
    and write the results to a CSV.
    """

    parser = argparse.ArgumentParser(
        description='Start the Serial Port Reader')
    parser.add_argument(
        '-p',
        '--port',
        type=str,
        default='/dev/ttyUSB0',
        dest='port',
        help="The port on which the inverter is connected, default: "
             "'/dev/ttyUSB0'.")
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        default='growatt-inverter',
        dest='input',
        help="The input device name (growatt-inverter or p1-port),"
             " default: 'growatt-inverter'.")
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='csv',
        dest='output',
        help="The output device name, efault: csv")
    parser.add_argument(
        '-r',
        '--read-interval',
        type=int,
        default=1,
        dest='read_interval',
        help="Read interval in seconds, default: 1.")
    parser.add_argument(
        '-w',
        '--write-interval',
        type=int,
        default=600,
        dest='write_interval',
        help="Write cached data interval in seconds, default: 600.")
    parser.add_argument(
        '-c',
        '--reconnect-wait',
        type=int,
        default=60,
        dest='reconnect_wait',
        help="Attempt reconnect to serial port in seconds, default: 60.")

    args = parser.parse_args()

    get_lock('reading_device')
    killer = GracefulKiller()
    while True:
        reader(
            killer,
            args.input,
            args.output,
            args.read_interval,
            args.write_interval)
        if killer.kill_now:
            break
        logging.info(
            "Trying to reconnect to the %s in %i seconds.",
            args.device,
            args.reconnect_wait)
        time.sleep(args.reconnect_wait)
        logging.info("Trying to reconnect to the %s...", args.device)
    logging.warning("Killed by external source. Gracefully exited.")
