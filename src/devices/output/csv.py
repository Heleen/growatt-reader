import csv
import logging
import time

from ._base import BaseWriter
from ...utils.config import config

logger = logging.getLogger(__name__)

OUTPUT_FILE = config.get('output', {}).get(
    'csv', '/home/pi/growatt/results/readings.csv')


class CSVWriter(BaseWriter):
    @staticmethod
    def write(readings):
        """Append readings to a CSV file.
        """
        if not readings:
            logging.info(
                "There are currently no readings in memory. "
                "Skip writing readings to CSV."
            )
        else:
            logging.info('Writing %i readings to file.' % len(readings))
            time1 = time.time()
            try:
                with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(readings)
            except Exception as e:
                logging.error("Could not write to CSV. %s", e)
            else:
                time2 = time.time()
                logging.info(
                    "Writing readings to file took: %0.3f ms" % (
                        (time2 - time1) * 1000.0))
