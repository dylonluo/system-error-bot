"""In-memory implementation of ISearchQueryRepository."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ...domain.repositories.search_query_repository import ISearchQueryRepository


class InMemorySearchQueryRepository(ISearchQueryRepository):
    """In-memory repository for search queries."""

    def __init__(self):
        self._queries: Dict = {}

    def save(self, search_query) -> None:
        """Save a search query."""
        self._queries[str(search_query.query_id)] = search_query

    def find_by_id(self, query_id) -> Optional:
        """Find search query by ID."""
        return self._queries.get(str(query_id))

    def find_recent(self, user_id: str, limit: int = 10) -> List:
        """Find recent queries by user."""
        user_queries = [q for q in self._queries.values() if q.requested_by == user_id]
        # Sort by execution time (most recent first)
        user_queries.sort(key=lambda q: q.executed_at, reverse=True)
        return user_queries[:limit]

    def find_cached(self, query_text: str, filters) -> Optional:
        """Find cached query results."""
        query_lower = query_text.lower()

        # Look for recent query with same text and filters
        for query in self._queries.values():
            if str(query.query_text).lower() == query_lower:
                # Check if query is still fresh (within 5 minutes)
                age = datetime.now() - query.executed_at
                if age < timedelta(minutes=5):
                    return query

        return None

    def delete_older_than(self, minutes: int) -> int:
        """Delete queries older than specified minutes."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        to_delete = []

        for query_id, query in self._queries.items():
            if query.executed_at < cutoff_time:
                to_delete.append(query_id)

        for query_id in to_delete:
            del self._queries[query_id]

        return len(to_delete)
