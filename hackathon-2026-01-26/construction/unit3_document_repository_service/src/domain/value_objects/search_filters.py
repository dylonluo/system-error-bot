"""SearchFilters value object."""

from typing import List, Optional

from .document_access_level import AccessLevel
from .document_format import DocFormat
from .document_source import Source
from .document_type import DocType


class SearchFilters:
    """Filters for document search."""

    def __init__(
        self,
        sources: Optional[List[Source]] = None,
        document_types: Optional[List[DocType]] = None,
        formats: Optional[List[DocFormat]] = None,
        access_levels: Optional[List[AccessLevel]] = None,
    ):
        self._sources = sources or []
        self._document_types = document_types or []
        self._formats = formats or []
        self._access_levels = access_levels or []

    @property
    def sources(self) -> List[Source]:
        return self._sources

    @property
    def document_types(self) -> List[DocType]:
        return self._document_types

    @property
    def formats(self) -> List[DocFormat]:
        return self._formats

    @property
    def access_levels(self) -> List[AccessLevel]:
        return self._access_levels

    def is_empty(self) -> bool:
        """Check if no filters are specified."""
        return (
            len(self._sources) == 0
            and len(self._document_types) == 0
            and len(self._formats) == 0
            and len(self._access_levels) == 0
        )

    def matches(self, document) -> bool:
        """Check if document matches all specified filters."""
        # If no filters, match all
        if self.is_empty():
            return True

        # Check source filter
        if self._sources and document.source.value not in self._sources:
            return False

        # Check document type filter
        if self._document_types and document.document_type.value not in self._document_types:
            return False

        # Check format filter
        if self._formats and document.format.value not in self._formats:
            return False

        # Check access level filter
        if self._access_levels and document.access_level.value not in self._access_levels:
            return False

        return True

    def __repr__(self) -> str:
        return f"SearchFilters(sources={self._sources}, types={self._document_types}, formats={self._formats}, access_levels={self._access_levels})"
