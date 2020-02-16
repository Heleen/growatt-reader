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

from contextlib import contextmanager

from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ConnectionException
from pymodbus.exceptions import ModbusIOException


try:
    logging.basicConfig(
        format='%(asctime)s %(levelname)s:%(message)s',
        filename='/var/log/growatt/growatt_reader.log',
        level=logging.INFO)
except FileNotFoundError:
    logging.basicConfig()
logging.info('Enter Growatt Reader Script')


MODBUS_SETTINGS = {
    'method': 'rtu',
    'port': '/dev/ttyUSB0',
    'baudrate': 9600,
    'stopbits': 1,
    'parity': 'N',
    'bytesize': 8,
    'timeout': 1,
}


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

    def __init__(self, output_file):
        self._readings = []
        self._output_file = output_file

    def _empty_readings(self):
        self._readings = []

    def add_reading(self, reading):
        self._readings.append(reading)

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


def read_from_inverter(
        inverter,
        killer,
        output_file,
        read_interval,
        write_interval):
    """
    Read from the inverter every X seconds while the connection is not
    broken.
    Write the results to CSV every Y seconds.
    """
    readings = Readings(output_file)

    no_readings = 0
    while True:  # i != NUM_OF_SECS_TO_RUN+1:
        if killer.kill_now:
            logging.warning(
                "Killed by external source. "
                "Writing readings buffer to CSV and stop.")
            readings.append_to_csv()
            break

        no_readings += 1
        try:
            reading = inverter.read_input_registers(0, 45)
            if isinstance(reading, Exception):
                raise reading
            else:
                reading = reading.registers
        except ModbusIOException as e:
            # Write one last time in case connection is lost.
            logging.error(e)
            logging.warning(
                "Lost connection with inverter, writing readings one last "
                "time.")
            readings.append_to_csv()
            logging.info("Finished writing final results to CSV.")
            break
        else:
            # Add a unix timestamp
            reading.append(round(time.time()*1000.0))
            # Add reading to readings in memory
            readings.add_reading(reading)
            # Write to CSV every WRITE_AT_SECS seconds
            if (no_readings % write_interval) == 0:
                readings.append_to_csv()
            # Read the inverter every READ_INTERVAL_SECS second
            time.sleep(read_interval)
    return None


@contextmanager
def connect_to_inverter(port):
    """
    Set up a connection with the inverter.
    """
    modbus_settings = MODBUS_SETTINGS
    modbus_settings['port'] = port
    try:
        with ModbusSerialClient(**modbus_settings) as inverter:
            logging.info('Connected, start reading from inverter...')
            yield inverter
            logging.info("Stopped reading from inverter.")
    except ConnectionException as e:
        logging.warning(
            "Did not manage to obtain a connection with the inverter.", e)
    finally:
        logging.warning("Lost connection with inverter.")


if __name__ == '__main__':
    """
    Set up a connection with the inverter. When the connection is broken try
    to reconnect every X seconds.
    While connection with inverter is live, periodically read from the inverter
    and write the results to a CSV.
    """

    parser = argparse.ArgumentParser(
        description='Start the Growatt Serial Port Reader')
    parser.add_argument(
        '-p',
        '--port',
        type=str,
        default='/dev/ttyUSB0',
        dest='port',
        help="The port on which the inverter is connected, default: "
             "'/dev/ttyUSB0'.")
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='/home/pi/growatt/results/inverter.csv',
        dest='output',
        help="The output CSV file, default: "
             "'/home/pi/growatt/results/inverter.csv'.")
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

    get_lock('reading_inverter')
    killer = GracefulKiller()
    while True:
        with connect_to_inverter(args.port) as inverter:
            read_from_inverter(
                inverter,
                killer,
                args.output,
                args.read_interval,
                args.write_interval)
        if killer.kill_now:
            break
        logging.info(
            "Trying to reconnect to the inverter in %i seconds." % (
                args.reconnect_wait))
        time.sleep(args.reconnect_wait)
        logging.info("Trying to reconnect to the inverter...")
    logging.warning("Killed by external source. Gracefully exited.")
