class ObjectFactory:

    def __init__(self):
        self._creators = {}

    def register(self, key, creator):
        self._creators[key] = creator

    def get(self, key):
        creator = self._creators.get(key)
        if not creator:
            raise ValueError(key)
        return creator()
