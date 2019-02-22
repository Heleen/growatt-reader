#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
socat /dev/ttyUSB0,raw,echo=0 SYSTEM:'tee in.txt |socat - "PTY,link=/tmp/ttyUSB0,raw,echo=0,waitslave"|tee out.txt'
"""

#import MySQLdb
import subprocess
import logging
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pprint import pprint

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s',filename='debugger.log',level=logging.WARNING)
logging.info('Start Script')

pv_volts=0.0
pv_power=0.0
Wh_today=0.0
Wh_total=0.0
AC_volts=0.0
work_time_total_H=0
work_time_total_L=0
work_time_total=0.0
inverter_status=None

# Read data from inverter
port = '/dev/ttyUSB0'
#port = '/tmp/ttyUSB0'
try:
        inverter = ModbusClient(method='rtu', port=port, baudrate=9600, stopbits=1, parity='N', bytesize=8, timeout=1)
        connected = inverter.connect()
except:
        logging.error('Connect Failed')

if connected:
        logging.info('Connected')
        rr = inverter.read_input_registers(0, 45)
        inverter.close()
        succes = False
        for reg, value in enumerate(rr.registers, start=0):
            print("%s: %s" % (reg, value))
        try:
                value=rr.registers[0]
                inverter_status = value
                value=rr.registers[3]
                pv_volts=(float(value)/10) # dc volts
                value=rr.registers[12]
                pv_power=(float(value)/10) # power ac to net
                value=rr.registers[27]
                Wh_today=(float(value)/10) # total energy today
                value=rr.registers[29]
                Wh_total=(float(value)/10) # total energy all time
                value=rr.registers[30]
                work_time_total_H = value  # Total work time in hours
                value=rr.registers[31]
                work_time_total_L = value  # Total work time in hours
                work_time_total = work_time_total_L + (pow(2, 16) * work_time_total_H)
                work_time_total = float(work_time_total) / (2 * 60 * 60)
                succes = True
        except:
                logging.info('register empty')

        #value=rr.registers[13]
        #AC_volts=(float(value)/10) # volts ac

        print('pv_volts %s' % pv_volts)
        print('pv_power %s' % pv_power)
        print('kWh_today %s' % Wh_today)
        print('kWh_total %s' % Wh_total)
        print('AC_volts %s' % AC_volts)
        print('Work time H %s' % work_time_total_H)
        print('Work time L %s' % work_time_total_L)
        print('Work time %s hours' % work_time_total)
        print('Inverter status: %s' % inverter_status)

        # if (succes and  (Wh_total>1)):
        #         logging.info('add entry to db')
        #         #make connection with db
        #         db = MySQLdb.connect(host="localhost", user="u", passwd="pw", db="dbnaam")

        #         #create cursor
        #         cur = db.cursor()

        #         #insert values in db
        #         with db:
        #                 cur.execute ("""INSERT INTO Pv_data (currentpower,dag,totaal,voltage)
        #                         values(%s,%s,%s,%s)""",(pv_power,Wh_today,Wh_total,pv_volts))

        #         cur.close()

        #         db.close()
        # else:
        #         logging.info('No entry for db')
else:
        logging.warning('Not connected')

logging.info('Einde Script')
