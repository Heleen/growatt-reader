=================
Timeseries Reader
=================

Read data from a specified device and periodically write it to a specified
output.

Includes a logrotate example config to compress and rotate the results CSV if
you've chosen a CSV file output.
Also includes an example service file to run the script as a service.

------------
Requirements
------------

* Python 3
* Logrotate (optional)
* Systemd (optional)

-----
Usage
-----

0. (Optional) Create a Python virtualenv and activate
   it::

    python3 -m venv env
    source env/bin/activate

1. Install the Python requirements::

    pip install -r requirements

2. Copy ``timeseries-reader.logrotate.dist`` to ``timeseries-reader.logrotate``
   and ``timeseries-reader.service.dist`` to ``timeseries-reader.service``
   and adjust them to your Pi's setup. Note that the script uses ``argparse``
   to configure some settings.

   Run ``./src/cli.py --help`` to see a list of options to add to the service
   command::
    
    cp timeseries-reader.logrotate.dist timeseries-reader.logrotate
    cp timeseries-reader.service.dist timeseries-reader.service
    ./src/cli.py --help

3. Copy ``timeseries-reader.logrotate`` to
   ``/etc/logrotate.d/timeseries-reader``::

    cp timeseries-reader.logrotate /etc/logrotate.d/timeseries-reader

4. Copy ``timeseries-reader.service`` to
   ``/etc/systemd/system/timeseries-reader.service``::

    cp timeseries-reader.service /etc/systemd/system/timeseries-reader.service

5. Enable the service::

    systemctl enable --now timeseries-reader

-----
Notes
-----

- Tested (v1.0) on a Raspberry Pi 2B connected to a
  timeseries-reader 3000 MTL-S inverter via serial (RS232) to USB cable.
- If you want proper logging: create
  ``/var/log/timeseries-reader/reader.log`` and it will write logging
  to it.
- The script currently reads registers 0-45. According to the documentation
  there should be more than 45 registers, however during testing it appeared
  that I couldn't read more than the first 45 registers.
