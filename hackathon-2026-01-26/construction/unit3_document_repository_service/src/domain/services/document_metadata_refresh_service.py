"""DocumentMetadataRefreshService domain service."""

from typing import Optional


class DocumentMetadataRefreshService:
    """Service for refreshing document metadata."""

    def __init__(self, document_repository, s3_adapter):
        self._document_repository = document_repository
        self._s3_adapter = s3_adapter

    def refresh_metadata(self, document_id) -> None:
        """Refresh metadata for a specific document."""
        document = self._document_repository.find_by_id(document_id)
        if not document:
            return

        # Fetch fresh metadata from source
        metadata = self.fetch_metadata_from_source(document)
        if metadata:
            document.update_metadata(metadata)
            self._document_repository.save(document)

    def refresh_stale_documents(self) -> int:
        """Refresh all stale documents. Returns count of refreshed documents."""
        stale_docs = self._document_repository.find_stale(days=90)
        refreshed_count = 0

        for doc in stale_docs:
            try:
                self.refresh_metadata(doc.document_id)
                refreshed_count += 1
            except Exception as e:
                print(f"Failed to refresh document {doc.document_id}: {e}")
                doc.mark_as_stale()
                self._document_repository.save(doc)

        return refreshed_count

    def fetch_metadata_from_source(self, document):
        """Fetch metadata from the document's source."""
        try:
            if document.source.is_s3():
                return self._s3_adapter.get_metadata(document.document_id)
            else:
                return None
        except Exception as e:
            print(f"Failed to fetch metadata: {e}")
            return None
