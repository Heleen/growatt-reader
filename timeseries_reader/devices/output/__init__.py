"""
Usage:

from devices.output import output_devices
device = output_devices.get('csv')
device.write(readings)
"""

from timeseries_reader.devices.output._factory import ObjectFactory
from timeseries_reader.devices.output.csv import CSVWriter


output_devices = ObjectFactory()
output_devices.register('csv', CSVWriter)
