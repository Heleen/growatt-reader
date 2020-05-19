import configparser
import os

config_file = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__))),
    'config.ini')

config = configparser.ConfigParser()
config.read(config_file)
