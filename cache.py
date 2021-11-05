

import time


class SimpleMemoryCache:

    class Item:
        def __init__(self, value, ttl):
            self.value = value
            self.ttl = ttl
            self.created = time.time()
        def expired(self):
            return (time.time() - self.created) > self.ttl

    def __init__(self):
        self.items = {}

    def get(self, key):
        if item := self.items.get(key):
            if item.expired():
                del(self.items[key])
                return None
            return item.value

    def set(self, key, value, ttl):
        self.items[key] = self.Item(value, ttl)

    def expire(self):
        for key in self.items.keys():
            if self.items[key].expired():
                del(self.items[key])

