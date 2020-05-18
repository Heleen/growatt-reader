#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service to periodically read from a Growatt inverter connected on a serial port
with the Modbus protocol and write the results to a CSV file.


socat /dev/ttyUSB0,raw,echo=0 SYSTEM:'tee in.txt |socat - \
    "PTY,link=/tmp/ttyUSB0,raw,echo=0,waitslave"|tee out.txt'
"""

import argparse
import csv
import logging
import signal
import socket
import sys
import time

from .devices.growatt_inverter import Inverter
from .devices.p1_port import P1Port


try:
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename='/var/log/growatt/growatt_reader.log',
        level=logging.INFO)
except FileNotFoundError:
    logging.basicConfig()
logging.info('Enter Growatt Reader Script')


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
        logging.info("I got the lock.")
    except socket.error:
        # TODO LOG PID
        logging.warning("Lock already exists, exiting script.")
        sys.exit()


class Readings:
    """
    Class to hold readings in memory and periodically save them to file.
    """

    def __init__(self, output_file, write_interval):
        self._readings = []
        self._output_file = output_file
        self._write_interval = write_interval

    def _empty_readings(self):
        self._readings = []

    def add_reading(self, reading):
        self._readings.append(reading)
        # Write to CSV every WRITE_AT_SECS seconds
        if (len(self._readings) % self._write_interval) == 0:
            self.append_to_csv()

    def append_to_csv(self):
        if not self._readings:
            logging.info(
                "There are currently no readings in memory. "
                "Skip writing readings to CSV."
            )
        else:
            logging.info('Writing %i readings to file.' % len(self._readings))
            time1 = time.time()
            try:
                with open(self._output_file, 'a', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(self._readings)
            except Exception as e:
                logging.error("Could not write to CSV. %s", e)
            else:
                self._empty_readings()
                time2 = time.time()
                logging.info(
                    "Writing readings to file took: %0.3f ms" % (
                        (time2 - time1) * 1000.0))


def _get_device(device_name):
    if device_name == 'p1-port':
        return P1Port
    return Inverter


def read_from_device(
        killer,
        device_name,
        read_interval):
    """
    Read from the inverter every X seconds while the connection is not
    broken.
    Write the results to CSV every Y seconds.
    """
    readings = Readings(args.output, args.write_interval)
    device = _get_device(device_name)()

    with device.connect_to_device() as device_conn:
        while True:
            if killer.kill_now:
                logging.warning(
                    "Killed by external source. "
                    "Writing readings buffer to CSV and stop.")
                readings.append_to_csv()
                break

            try:
                reading = device.readline(device_conn)
            except Exception as e:
                # Write one last time in case connection is lost.
                logging.error(e)
                logging.warning(
                    "Something went wrong, writing readings one last time.")
                readings.append_to_csv()
                logging.info("Finished writing final results to CSV.")
                break
            else:
                # Add a unix timestamp
                reading.append(round(time.time()*1000.0))
                # Add reading to readings in memory
                readings.add_reading(reading)
                # Read the inverter every READ_INTERVAL_SECS second
                time.sleep(read_interval)
    return None


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
        '-d',
        '--device',
        type=str,
        default='growatt-inverter',
        dest='device',
        help="The type of device being read (growatt-inverter or p1-port),"
             " default: 'growatt-inverter'.")
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='/home/pi/growatt/results/readings.csv',
        dest='output',
        help="The output CSV file, default: "
             "'/home/pi/growatt/results/readings.csv'.")
    parser.add_argument(
        '-i',
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
        read_from_device(
            killer,
            args.device,
            args.read_interval)
        if killer.kill_now:
            break
        logging.info(
            "Trying to reconnect to the %s in %i seconds.",
            args.device,
            args.reconnect_wait)
        time.sleep(args.reconnect_wait)
        logging.info("Trying to reconnect to the %s...", args.device)
    logging.warning("Killed by external source. Gracefully exited.")
