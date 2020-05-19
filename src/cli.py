#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service to periodically read from a specified input device and write the
results to a specified output device.
"""

import argparse
import logging
import time

from .reader import reader
from .utils.service import get_lock
from .utils.service import GracefulKiller
from .utils.config import config

try:
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename=config.get('logging', {}).get('logfile', ''),
        level=getattr(
            logging,
            config.get('logging', {}).get('level', '').upper()))
except FileNotFoundError:
    logging.basicConfig()

logger = logging.getLogger(__name__)

logger.info('Enter Timeseries Reader Script')


if __name__ == '__main__':
    """
    Set up a connection with an input device. When the connection is broken try
    to reconnect every X seconds.
    While connection with the device is live, periodically read from the device
    and write the results to an output device.
    """

    parser = argparse.ArgumentParser(
        description='Start the Timeseries Reader')
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
        logger.info(
            "Trying to reconnect to the %s in %i seconds.",
            args.device,
            args.reconnect_wait)
        time.sleep(args.reconnect_wait)
        logger.info("Trying to reconnect to the %s...", args.device)
    logger.warning("Killed by external source. Gracefully exited.")
