"""In-memory cache provider."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from ...domain.ports.cache_provider import ICacheProvider


class InMemoryCacheProvider(ICacheProvider):
    """In-memory implementation of cache provider."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None

        value, expiry_time = self._cache[key]

        # Check if expired
        if datetime.now() > expiry_time:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (seconds)."""
        expiry_time = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry_time)

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]

    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if key not in self._cache:
            return False

        # Check if expired
        _, expiry_time = self._cache[key]
        if datetime.now() > expiry_time:
            del self._cache[key]
            return False

        return True

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
