"""IDocumentRepository interface."""

from abc import ABC, abstractmethod
from typing import List, Optional


class IDocumentRepository(ABC):
    """Repository interface for Document aggregate."""

    @abstractmethod
    def save(self, document) -> None:
        """Save a document."""
        pass

    @abstractmethod
    def find_by_id(self, document_id) -> Optional:
        """Find document by ID."""
        pass

    @abstractmethod
    def find_by_url(self, url) -> Optional:
        """Find document by URL."""
        pass

    @abstractmethod
    def find_by_source(self, source, limit: int = 100) -> List:
        """Find documents by source."""
        pass

    @abstractmethod
    def search(self, query: str, filters) -> List:
        """Search documents."""
        pass

    @abstractmethod
    def find_stale(self, days: int) -> List:
        """Find stale documents."""
        pass

    @abstractmethod
    def update_metadata(self, document_id, metadata) -> None:
        """Update document metadata."""
        pass

    @abstractmethod
    def delete(self, document_id) -> None:
        """Delete a document."""
        pass

    @abstractmethod
    def get_all(self) -> List:
        """Get all documents."""
        pass
