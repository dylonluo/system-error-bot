"""SearchQuery aggregate root."""

from datetime import datetime
from typing import List, Optional


class SearchQuery:
    """Aggregate root for SearchQuery."""

    def __init__(
        self,
        query_id,
        query_text,
        filters,
        requested_by: str,
        executed_at: Optional[datetime] = None,
        result_count: int = 0,
        execution_time: int = 0,
    ):
        self._query_id = query_id
        self._query_text = query_text
        self._filters = filters
        self._requested_by = requested_by
        self._executed_at = executed_at or datetime.now()
        self._result_count = result_count
        self._execution_time = execution_time  # milliseconds
        self._results: List = []

    @property
    def query_id(self):
        return self._query_id

    @property
    def query_text(self):
        return self._query_text

    @property
    def filters(self):
        return self._filters

    @property
    def requested_by(self) -> str:
        return self._requested_by

    @property
    def executed_at(self) -> datetime:
        return self._executed_at

    @property
    def result_count(self) -> int:
        return self._result_count

    @property
    def execution_time(self) -> int:
        return self._execution_time

    @property
    def results(self) -> List:
        return self._results

    def execute(self) -> List:
        """Execute the search query (returns results)."""
        return self._results

    def add_result(self, document, relevance_score) -> None:
        """Add a search result."""
        from ..entities.search_result import ResultId, SearchResult

        # Extract keywords from query for matched terms
        matched_terms = str(self._query_text).lower().split()

        result = SearchResult(
            result_id=ResultId.generate(),
            query_id=self._query_id,
            document=document,
            relevance_score=relevance_score,
            matched_terms=matched_terms,
            position=len(self._results) + 1,
        )
        self._results.append(result)
        self._result_count = len(self._results)

    def rank_results(self) -> None:
        """Rank results by relevance score (descending)."""
        self._results.sort(key=lambda r: r.relevance_score.value, reverse=True)
        # Update positions after sorting
        for i, result in enumerate(self._results):
            result._position = i + 1

    def get_cached_results(self) -> List:
        """Get cached results."""
        return self._results

    def limit_results(self, max_results: int = 50) -> None:
        """Limit results to maximum count."""
        if len(self._results) > max_results:
            self._results = self._results[:max_results]
            self._result_count = len(self._results)

    def set_execution_time(self, milliseconds: int) -> None:
        """Set the execution time."""
        self._execution_time = milliseconds

    def __eq__(self, other) -> bool:
        if not isinstance(other, SearchQuery):
            return False
        return self._query_id == other._query_id

    def __hash__(self) -> int:
        return hash(self._query_id)

    def __repr__(self) -> str:
        return f"SearchQuery(id={self._query_id}, text={self._query_text}, results={self._result_count})"
