"""In-memory implementation of IDocumentRepository."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ...domain.repositories.document_repository import IDocumentRepository


class InMemoryDocumentRepository(IDocumentRepository):
    """In-memory repository for documents."""

    def __init__(self):
        self._documents: Dict = {}

    def save(self, document) -> None:
        """Save a document."""
        self._documents[str(document.document_id)] = document

    def find_by_id(self, document_id) -> Optional:
        """Find document by ID."""
        return self._documents.get(str(document_id))

    def find_by_url(self, url) -> Optional:
        """Find document by URL."""
        url_str = str(url)
        for doc in self._documents.values():
            if str(doc.url) == url_str:
                return doc
        return None

    def find_by_source(self, source, limit: int = 100) -> List:
        """Find documents by source."""
        results = []
        for doc in self._documents.values():
            if doc.source == source:
                results.append(doc)
                if len(results) >= limit:
                    break
        return results

    def search(self, query: str, filters) -> List:
        """Search documents."""
        query_lower = query.lower()
        results = []

        for doc in self._documents.values():
            # Simple text search in title and snippet
            title_lower = str(doc.title).lower()
            snippet_lower = doc.snippet.lower()

            if query_lower in title_lower or query_lower in snippet_lower:
                if filters.matches(doc):
                    results.append(doc)

        return results

    def find_stale(self, days: int) -> List:
        """Find stale documents."""
        cutoff_date = datetime.now() - timedelta(days=days)
        results = []

        for doc in self._documents.values():
            if doc.last_accessed and doc.last_accessed < cutoff_date:
                results.append(doc)

        return results

    def update_metadata(self, document_id, metadata) -> None:
        """Update document metadata."""
        doc = self.find_by_id(document_id)
        if doc:
            doc.update_metadata(metadata)

    def delete(self, document_id) -> None:
        """Delete a document."""
        doc_id_str = str(document_id)
        if doc_id_str in self._documents:
            del self._documents[doc_id_str]

    def get_all(self) -> List:
        """Get all documents."""
        return list(self._documents.values())
