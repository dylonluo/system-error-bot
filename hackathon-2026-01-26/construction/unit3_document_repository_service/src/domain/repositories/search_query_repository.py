"""ISearchQueryRepository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional


class ISearchQueryRepository(ABC):
    """Repository interface for SearchQuery aggregate."""

    @abstractmethod
    def save(self, search_query) -> None:
        """Save a search query."""
        pass

    @abstractmethod
    def find_by_id(self, query_id) -> Optional:
        """Find search query by ID."""
        pass

    @abstractmethod
    def find_recent(self, user_id: str, limit: int = 10) -> List:
        """Find recent queries by user."""
        pass

    @abstractmethod
    def find_cached(self, query_text: str, filters) -> Optional:
        """Find cached query results."""
        pass

    @abstractmethod
    def delete_older_than(self, minutes: int) -> int:
        """Delete queries older than specified minutes."""
        pass
