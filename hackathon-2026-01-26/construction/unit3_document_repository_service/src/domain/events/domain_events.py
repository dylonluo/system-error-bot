"""Domain events for Document Repository Context."""

from datetime import datetime
from typing import Any, Dict


class DomainEvent:
    """Base class for domain events."""

    def __init__(self):
        self._occurred_at = datetime.now()

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {"event_type": self.__class__.__name__, "occurred_at": self._occurred_at.isoformat()}


class DocumentDiscovered(DomainEvent):
    """Event raised when a new document is discovered."""

    def __init__(self, document_id, source, title):
        super().__init__()
        self._document_id = document_id
        self._source = source
        self._title = title

    @property
    def document_id(self):
        return self._document_id

    @property
    def source(self):
        return self._source

    @property
    def title(self):
        return self._title

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"document_id": str(self._document_id), "source": str(self._source), "title": str(self._title)})
        return data


class DocumentAccessed(DomainEvent):
    """Event raised when a document is accessed."""

    def __init__(self, document_id, user_id: str, source):
        super().__init__()
        self._document_id = document_id
        self._user_id = user_id
        self._source = source

    @property
    def document_id(self):
        return self._document_id

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def source(self):
        return self._source

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({"document_id": str(self._document_id), "user_id": self._user_id, "source": str(self._source)})
        return data


class DocumentMetadataUpdated(DomainEvent):
    """Event raised when document metadata is updated."""

    def __init__(self, document_id, previous_version: int, new_version: int):
        super().__init__()
        self._document_id = document_id
        self._previous_version = previous_version
        self._new_version = new_version

    @property
    def document_id(self):
        return self._document_id

    @property
    def previous_version(self) -> int:
        return self._previous_version

    @property
    def new_version(self) -> int:
        return self._new_version

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "document_id": str(self._document_id),
                "previous_version": self._previous_version,
                "new_version": self._new_version,
            }
        )
        return data


class SearchExecuted(DomainEvent):
    """Event raised when a search query is executed."""

    def __init__(self, query_id, query_text: str, user_id: str, result_count: int, execution_time: int):
        super().__init__()
        self._query_id = query_id
        self._query_text = query_text
        self._user_id = user_id
        self._result_count = result_count
        self._execution_time = execution_time

    @property
    def query_id(self):
        return self._query_id

    @property
    def query_text(self) -> str:
        return self._query_text

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def result_count(self) -> int:
        return self._result_count

    @property
    def execution_time(self) -> int:
        return self._execution_time

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "query_id": str(self._query_id),
                "query_text": self._query_text,
                "user_id": self._user_id,
                "result_count": self._result_count,
                "execution_time": self._execution_time,
            }
        )
        return data


class DocumentMarkedStale(DomainEvent):
    """Event raised when a document is marked as stale."""

    def __init__(self, document_id, last_accessed: datetime):
        super().__init__()
        self._document_id = document_id
        self._last_accessed = last_accessed

    @property
    def document_id(self):
        return self._document_id

    @property
    def last_accessed(self) -> datetime:
        return self._last_accessed

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update(
            {
                "document_id": str(self._document_id),
                "last_accessed": self._last_accessed.isoformat() if self._last_accessed else None,
            }
        )
        return data
