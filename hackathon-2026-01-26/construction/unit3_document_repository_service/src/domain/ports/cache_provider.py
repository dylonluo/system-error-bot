"""ICacheProvider interface."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ICacheProvider(ABC):
    """Interface for caching provider."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache with TTL (seconds)."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
