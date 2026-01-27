"""SearchResult entity."""

from typing import List
from uuid import UUID, uuid4


class ResultId:
    """Unique identifier for a search result."""

    def __init__(self, value: UUID):
        self._value = value

    @classmethod
    def generate(cls) -> "ResultId":
        return cls(uuid4())

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other) -> bool:
        if not isinstance(other, ResultId):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)


class SearchResult:
    """Entity representing a single search result."""

    def __init__(self, result_id: ResultId, query_id, document, relevance_score, matched_terms: List[str], position: int):
        self._result_id = result_id
        self._query_id = query_id
        self._document = document
        self._relevance_score = relevance_score
        self._matched_terms = matched_terms
        self._position = position
        self._was_clicked = False

    @property
    def result_id(self) -> ResultId:
        return self._result_id

    @property
    def query_id(self):
        return self._query_id

    @property
    def document(self):
        return self._document

    @property
    def relevance_score(self):
        return self._relevance_score

    @property
    def matched_terms(self) -> List[str]:
        return self._matched_terms

    @property
    def position(self) -> int:
        return self._position

    def get_document(self):
        """Get the document for this result."""
        return self._document

    def get_relevance_score(self):
        """Get the relevance score."""
        return self._relevance_score

    def was_clicked(self) -> bool:
        """Check if this result was clicked."""
        return self._was_clicked

    def mark_as_clicked(self) -> None:
        """Mark this result as clicked."""
        self._was_clicked = True

    def __eq__(self, other) -> bool:
        if not isinstance(other, SearchResult):
            return False
        return self._result_id == other._result_id

    def __repr__(self) -> str:
        return f"SearchResult(id={self._result_id}, position={self._position}, score={self._relevance_score})"
