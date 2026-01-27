"""DocumentMetadata value object."""

from datetime import datetime
from typing import List, Optional


class DocumentMetadata:
    """Metadata for a document."""

    def __init__(
        self,
        author: Optional[str] = None,
        created_at: Optional[datetime] = None,
        last_modified: Optional[datetime] = None,
        file_size: Optional[int] = None,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
    ):
        self._author = author
        self._created_at = created_at
        self._last_modified = last_modified or datetime.now()
        self._file_size = file_size
        self._tags = tags or []
        self._category = category

    @property
    def author(self) -> Optional[str]:
        return self._author

    @property
    def created_at(self) -> Optional[datetime]:
        return self._created_at

    @property
    def last_modified(self) -> datetime:
        return self._last_modified

    @property
    def file_size(self) -> Optional[int]:
        return self._file_size

    @property
    def tags(self) -> List[str]:
        return self._tags

    @property
    def category(self) -> Optional[str]:
        return self._category

    def has_tag(self, tag: str) -> bool:
        """Check if metadata has a specific tag."""
        return tag in self._tags

    def is_recent(self, days: int = 30) -> bool:
        """Check if document was modified within specified days."""
        if not self._last_modified:
            return False
        delta = datetime.now() - self._last_modified
        return delta.days <= days

    def __repr__(self) -> str:
        return f"DocumentMetadata(author={self._author}, modified={self._last_modified}, tags={self._tags})"
