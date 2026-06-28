import time
from config import Config

class InMemoryCache:
    def __init__(self):
        self._store = {}  

    def get(self, key):
        if key in self._store:
            value, expire_at = self._store[key]
            if time.time() < expire_at:
                return value
            else:
                del self._store[key]  # limpieza perezosa
        return None

    def set(self, key, value, expire_seconds=Config.CACHE_EXPIRE_SECONDS):
        expire_at = time.time() + expire_seconds
        self._store[key] = (value, expire_at)

# Instancia global (singleton)
cache = InMemoryCache()