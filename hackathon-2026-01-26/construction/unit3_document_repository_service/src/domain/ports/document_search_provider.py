"""IDocumentSearchProvider interface."""

from abc import ABC, abstractmethod
from typing import List, Optional


class IDocumentSearchProvider(ABC):
    """Interface for document search providers (S3, Confluence, etc.)."""

    @abstractmethod
    def search(self, query: str) -> List:
        """Search for documents matching the query."""
        pass

    @abstractmethod
    def get_document(self, document_id) -> Optional:
        """Get a specific document by ID."""
        pass

    @abstractmethod
    def get_metadata(self, document_id):
        """Get metadata for a document."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
