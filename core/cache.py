# core/cache.py
import time
from typing import Dict, Any

class Cache:
    """
    A simple in-memory cache with a time-to-live (TTL) for each entry.
    """

    def __init__(self, ttl: int = 3600):
        """
        Initializes the cache.

        Args:
            ttl: The time-to-live for each cache entry, in seconds.
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def get(self, key: str) -> Any:
        """
        Gets an entry from the cache.

        Args:
            key: The key of the entry to get.

        Returns:
            The value of the entry, or None if the entry is not found or has expired.
        """
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["value"]
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Sets an entry in the cache.

        Args:
            key: The key of the entry to set.
            value: The value of the entry to set.
        """
        self.cache[key] = {
            "value": value,
            "timestamp": time.time(),
        }
