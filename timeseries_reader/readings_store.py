class ReadingsStore:
    """
    Class to hold readings in memory and periodically save them to file.
    """

    def __init__(self, write_interval, writer):
        self._write_interval = write_interval
        self._Writer = writer

        self._readings = []

    def _empty_readings(self):
        self._readings = []

    def add(self, reading):
        self._readings.append(reading)
        # Write to CSV every WRITE_AT_SECS seconds
        if (len(self._readings) % self._write_interval) == 0:
            self.write()

    def write(self):
        self._Writer.write(self._readings)
        self._empty_readings()
