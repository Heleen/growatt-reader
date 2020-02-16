===================================
Growatt Inverter Serial Port Reader
===================================

------------
Requirements
------------

* Python3
* Logrotate
* SystemCTL

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
   ``growatt.service.dist`` to ``gorwatt.service`` and adjust them to your PIs
   setup. Note that the script uses ``argparse`` to configure some settings.
   Run ``./read_growatt_inverter.py --help`` to see a list of options to add to
   the service command::
    
    cp growatt.logrotate.dist growatt.logrotate
    cp growatt.service.dist gorwatt.service
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

- Tested on the Growatt 3000 MTL-S
