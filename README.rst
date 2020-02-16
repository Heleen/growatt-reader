===================================
Growatt Inverter Serial Port Reader
===================================

Read data from a Growatt inverter serial port and periodically write it to
a CSV file.

Includes a logrotate example config to compress and rotate the results CSV.
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

2. Copy ``growatt.logrotate.dist`` to ``growatt.logrotate`` and
   ``growatt.service.dist`` to ``growatt.service`` and adjust them to your Pi's
   setup. Note that the script uses ``argparse`` to configure some settings.
   Run ``./read_growatt_inverter.py --help`` to see a list of options to add to
   the service command::
    
    cp growatt.logrotate.dist growatt.logrotate
    cp growatt.service.dist growatt.service
    ./read_growatt_inverter.py --help

3. Copy ``growatt.logrotate`` to ``/etc/logrotate.d/growatt``::

    cp growatt.logrotate /etc/logrotate.d/growatt

4. Copy ``growatt.service`` to ``/etc/systemd/system/growatt.service``::

    cp growatt.service /etc/systemd/system/growatt.service

5. Enable the service::

    systemctl enable --now growatt

-----
Notes
-----

- Tested (v1.0) on a Raspberry Pi 2B connected to a
  Growatt 3000 MTL-S inverter via serial (RS232) to USB cable.
- If you want proper logging: create
  ``/var/log/growatt/growatt_reader.log`` and it will write logging
  to it.
- The script currently reads registers 0-45. According to the documentation
  there should be more than 45 registers, however during testing I couldn't
  read more than the first 45 registers.
