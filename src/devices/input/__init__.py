"""
Usage:

from devices.input import input_devices
with input_devices.get('growatt-inverter') as conn:
    conn.readline()
"""

from ._factory import DeviceManagerFactory
from .growatt_inverter import Inverter
from .p1_port import P1Port


input_devices = DeviceManagerFactory()
input_devices.register('p1-port', P1Port)
input_devices.register('growatt-inverter', Inverter)
