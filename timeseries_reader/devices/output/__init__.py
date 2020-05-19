"""
Usage:

from devices.output import output_devices
device = output_devices.get('csv')
device.write(readings)
"""

from ._factory import ObjectFactory
from .csv import CSVWriter


output_devices = ObjectFactory()
output_devices.register('csv', CSVWriter)
