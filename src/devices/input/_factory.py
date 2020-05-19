from ._base import DeviceManager


class DeviceManagerFactory:

    def __init__(self):
        self._devices = {}

    def register(self, key, device):
        self._creators[key] = device

    def get(self, key):
        device = self._devices.get(key)
        if not device:
            raise ValueError(key)
        return DeviceManager(device)
