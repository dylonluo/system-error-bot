"""Document aggregate root."""

from datetime import datetime, timedelta
from typing import List, Optional


class Document:
    """Aggregate root for Document."""

    def __init__(
        self,
        document_id,
        title,
        url,
        source,
        document_type,
        format,
        access_level,
        snippet: str = "",
        metadata=None,
        last_modified: Optional[datetime] = None,
        last_accessed: Optional[datetime] = None,
        access_count: int = 0,
        is_stale: bool = False,
    ):
        self._document_id = document_id
        self._title = title
        self._url = url
        self._source = source
        self._document_type = document_type
        self._format = format
        self._access_level = access_level
        self._snippet = snippet[:200] if snippet else ""  # Limit to 200 chars
        self._metadata = metadata
        self._last_modified = last_modified or datetime.now()
        self._last_accessed = last_accessed
        self._access_count = access_count
        self._is_stale = is_stale
        self._versions: List = []

    @property
    def document_id(self):
        return self._document_id

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url

    @property
    def source(self):
        return self._source

    @property
    def document_type(self):
        return self._document_type

    @property
    def format(self):
        return self._format

    @property
    def access_level(self):
        return self._access_level

    @property
    def snippet(self) -> str:
        return self._snippet

    @property
    def metadata(self):
        return self._metadata

    @property
    def last_modified(self) -> datetime:
        return self._last_modified

    @property
    def last_accessed(self) -> Optional[datetime]:
        return self._last_accessed

    @property
    def access_count(self) -> int:
        return self._access_count

    @property
    def is_stale(self) -> bool:
        return self._is_stale

    @property
    def versions(self) -> List:
        return self._versions

    def update_metadata(self, metadata) -> None:
        """Update document metadata."""
        self._metadata = metadata
        self._last_modified = datetime.now()

    def mark_as_accessed(self) -> None:
        """Mark document as accessed and increment count."""
        self._last_accessed = datetime.now()
        self._access_count += 1

    def is_accessible_by(self, user_access_level: str) -> bool:
        """Check if user can access this document."""
        return self._access_level.is_accessible_by(user_access_level)

    def calculate_relevance(self, query: str):
        """Calculate relevance score for a query (placeholder)."""
        from ..value_objects.relevance_score import RelevanceScore

        # Simple keyword matching
        query_lower = query.lower()
        title_lower = str(self._title).lower()
        snippet_lower = self._snippet.lower()

        score = 0.0
        if query_lower in title_lower:
            score += 0.6
        if query_lower in snippet_lower:
            score += 0.3

        return RelevanceScore(min(score, 1.0))

    def refresh_from_source(self) -> None:
        """Refresh document data from source (placeholder)."""
        self._last_modified = datetime.now()

    def mark_as_stale(self) -> None:
        """Mark document as stale."""
        self._is_stale = True

    def needs_metadata_refresh(self, hours: int = 24) -> bool:
        """Check if metadata needs refresh."""
        if not self._last_modified:
            return True
        delta = datetime.now() - self._last_modified
        return delta > timedelta(hours=hours)

    def add_version(self, version) -> None:
        """Add a new version to the document."""
        # Mark all existing versions as not latest
        for v in self._versions:
            v.mark_as_old()
        # Mark new version as latest
        version.mark_as_latest()
        self._versions.append(version)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Document):
            return False
        return self._document_id == other._document_id

    def __hash__(self) -> int:
        return hash(self._document_id)

    def __repr__(self) -> str:
        return f"Document(id={self._document_id}, title={self._title})"
