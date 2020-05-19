"""
Usage:

from devices.input import input_devices
device = devices.get('growatt-inverter')
with device.connect() as conn:
    device.readline(conn)
"""

from .._factory import ObjectFactory
from .growatt_inverter import Inverter
from .p1_port import P1Port


input_devices = ObjectFactory()
input_devices.register('p1-port', P1Port)
input_devices.register('growatt-inverter', Inverter)
