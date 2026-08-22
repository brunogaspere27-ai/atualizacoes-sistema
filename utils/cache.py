"""
Cache em memória com TTL.
"""
import time
import threading


class CacheManager:
    """Cache thread-safe com expiração."""
    
    def __init__(self, default_ttl=300):
        self._cache = {}
        self._lock = threading.Lock()
        self._default_ttl = default_ttl
    
    def set(self, key, value, ttl=None):
        with self._lock:
            self._cache[key] = {
                "value": value,
                "expires": time.time() + (ttl or self._default_ttl)
            }
    
    def get(self, key):
        with self._lock:
            if key not in self._cache:
                return None
            item = self._cache[key]
            if time.time() > item["expires"]:
                del self._cache[key]
                return None
            return item["value"]
    
    def delete(self, key):
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()