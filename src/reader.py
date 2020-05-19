import time
import logging

from .devices.input import input_devices
from .devices.output import output_devices
from .readings_store import ReadingsStore

logger = logging.getLogger(__name__)


def reader(
        killer,
        input_device_name,
        output_device_name,
        read_interval,
        write_interval):
    """
    Read from the specified input device every X seconds while the connection
    is not broken.
    Write the results to the specified output device every Y seconds.
    """
    InputDevice = input_devices.get(input_device_name)
    OutputDevice = output_devices.get(output_device_name)
    readings_store = ReadingsStore(write_interval, OutputDevice)

    with InputDevice.connect() as device_conn:
        while True:
            if killer.kill_now:
                logger.warning(
                    "Killed by external source. "
                    "Write readings buffer and stop.")
                readings_store.write()
                break

            try:
                reading = InputDevice.readline(device_conn)
            except Exception as e:
                # Write one last time in case connection is lost.
                logger.error(e)
                logger.warning(
                    "Something went wrong, writing readings one last time.")
                readings_store.write()
                logger.info("Finished writing final results.")
                break
            else:
                # Add a unix timestamp to the reading
                reading.append(round(time.time()*1000.0))
                # Add reading to readings store in memory
                readings_store.add(reading)
                # Read the inverter every READ_INTERVAL_SECS second
                time.sleep(read_interval)
    return None