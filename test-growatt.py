#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
socat /dev/ttyUSB0,raw,echo=0 SYSTEM:'tee in.txt |socat - "PTY,link=/tmp/ttyUSB0,raw,echo=0,waitslave"|tee out.txt'
"""

import csv
import logging
import os
import sys
import time

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ConnectionException


pid = str(os.getpid())
pidfile = "inverterdaemon.pid"


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    #filename='debugger.log',
    level=logging.INFO)
logging.info('Enter script')

# Read data from inverter
PORT = '/dev/ttyUSB0'
#port = '/tmp/ttyUSB0'

CSVFILE = 'inverter.csv'

NUM_OF_SECS_TO_RUN = 60*60
WRITE_AT_SECS = 60*10


class Readings:
    """Singleton class to hold readings in memory and periodically save them to file.
    """
    readings = []

    def add_reading(self, reading):
        self.readings.append(reading)

    def append_to_csv(self):
        logger.info('Writing %i readings to file.' % WRITE_AT_SECS)
        time1 = time.time()
        with open(CSVFILE, 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(self.readings)
        self.readings = []  # Empty readings
        time2 = time.time()
        logging.info("Writing readings to file took: %0.3f ms" % ((time2 - time1) * 1000.0))


def read_inverter(inverter):
    readings = Readings()

    i = 0
    while i != NUM_OF_SECS_TO_RUN+1:
        i += 1
        rr = inverter.read_input_registers(0, 45)
        copy_registers = rr.registers
        # Add a unix timestamp
        timestamp = time.time()
        copy_registers.append(round(time.time()*1000.0))
        # Add reading to readings in memory
        readings.add_reading(copy_registers)
        # Write to CSV every WRITE_AT_SECS seconds
        if (i%WRITE_AT_SECS) == 0:
            readings.append_to_csv()
        # Read the inverter every second
        time.sleep(1)

if __name__ == '__main__':
    try:
        with ModbusClient(
                method='rtu',
                port=PORT,
                baudrate=9600,
                stopbits=1,
                parity='N',
                bytesize=8,
                timeout=1) as inverter:
            logging.info('Connected, start reading from inverter...')
            read_inverter(inverter)
            logging.info("Stopped reading from inverter.")
    except ConnectionException as e:
        logging.error(e)
    finally:
        logging.info('Exciting script.')
