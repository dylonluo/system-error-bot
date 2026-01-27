"""Mock S3 search adapter with sample documents."""

from datetime import datetime, timedelta
from typing import List, Optional

from ...domain.aggregates.document import Document
from ...domain.ports.document_search_provider import IDocumentSearchProvider
from ...domain.value_objects.document_access_level import (
    AccessLevel,
    DocumentAccessLevel,
)
from ...domain.value_objects.document_format import DocFormat, DocumentFormat
from ...domain.value_objects.document_id import DocumentId
from ...domain.value_objects.document_metadata import DocumentMetadata
from ...domain.value_objects.document_source import DocumentSource, Source
from ...domain.value_objects.document_title import DocumentTitle
from ...domain.value_objects.document_type import DocType, DocumentType
from ...domain.value_objects.document_url import DocumentUrl


class MockS3SearchAdapter(IDocumentSearchProvider):
    """Mock adapter for S3 document search with pre-populated data."""

    def __init__(self):
        self._documents = self._create_sample_documents()
        self._available = True

    def _create_sample_documents(self) -> List[Document]:
        """Create sample documents for testing."""
        now = datetime.now()

        documents = [
            Document(
                document_id=DocumentId.generate(),
                title=DocumentTitle("NetSuite Error Troubleshooting Guide"),
                url=DocumentUrl("https://s3.example.com/docs/netsuite-errors.pdf"),
                source=DocumentSource(Source.S3, "company-docs-bucket"),
                document_type=DocumentType(DocType.GUIDE),
                format=DocumentFormat(DocFormat.PDF),
                access_level=DocumentAccessLevel(AccessLevel.BASIC),
                snippet="Complete guide for troubleshooting common NetSuite errors including connection issues, data sync problems, and API errors.",
                metadata=DocumentMetadata(
                    author="IT Support Team",
                    created_at=now - timedelta(days=60),
                    last_modified=now - timedelta(days=10),
                    file_size=2048000,
                    tags=["netsuite", "troubleshooting", "errors"],
                    category="Technical Documentation",
                ),
                access_count=45,
            ),
            Document(
                document_id=DocumentId.generate(),
                title=DocumentTitle("TMS Integration Standard Operating Procedure"),
                url=DocumentUrl("https://s3.example.com/docs/tms-integration-sop.pdf"),
                source=DocumentSource(Source.S3, "company-docs-bucket"),
                document_type=DocumentType(DocType.SOP),
                format=DocumentFormat(DocFormat.PDF),
                access_level=DocumentAccessLevel(AccessLevel.ADVANCED),
                snippet="Standard operating procedures for TMS system integration, including setup, configuration, and maintenance guidelines.",
                metadata=DocumentMetadata(
                    author="Operations Team",
                    created_at=now - timedelta(days=120),
                    last_modified=now - timedelta(days=30),
                    file_size=1536000,
                    tags=["tms", "integration", "sop"],
                    category="Operations",
                ),
                access_count=23,
            ),
            Document(
                document_id=DocumentId.generate(),
                title=DocumentTitle("NetSuite API Integration Guide"),
                url=DocumentUrl("https://s3.example.com/docs/netsuite-api-guide.pdf"),
                source=DocumentSource(Source.S3, "company-docs-bucket"),
                document_type=DocumentType(DocType.GUIDE),
                format=DocumentFormat(DocFormat.PDF),
                access_level=DocumentAccessLevel(AccessLevel.BASIC),
                snippet="Comprehensive guide for integrating with NetSuite API, including authentication, endpoints, and best practices.",
                metadata=DocumentMetadata(
                    author="Development Team",
                    created_at=now - timedelta(days=90),
                    last_modified=now - timedelta(days=5),
                    file_size=3072000,
                    tags=["netsuite", "api", "integration"],
                    category="Development",
                ),
                access_count=67,
            ),
            Document(
                document_id=DocumentId.generate(),
                title=DocumentTitle("TMS User Manual"),
                url=DocumentUrl("https://s3.example.com/docs/tms-user-manual.pdf"),
                source=DocumentSource(Source.S3, "company-docs-bucket"),
                document_type=DocumentType(DocType.GUIDE),
                format=DocumentFormat(DocFormat.PDF),
                access_level=DocumentAccessLevel(AccessLevel.PUBLIC),
                snippet="User manual for Transportation Management System covering basic operations, reporting, and common tasks.",
                metadata=DocumentMetadata(
                    author="Product Team",
                    created_at=now - timedelta(days=180),
                    last_modified=now - timedelta(days=45),
                    file_size=4096000,
                    tags=["tms", "user-manual", "guide"],
                    category="User Documentation",
                ),
                access_count=102,
            ),
            Document(
                document_id=DocumentId.generate(),
                title=DocumentTitle("System Architecture PRD"),
                url=DocumentUrl("https://s3.example.com/docs/system-architecture-prd.pdf"),
                source=DocumentSource(Source.S3, "company-docs-bucket"),
                document_type=DocumentType(DocType.PRD),
                format=DocumentFormat(DocFormat.PDF),
                access_level=DocumentAccessLevel(AccessLevel.ADVANCED),
                snippet="Product requirements document for the system architecture including technical specifications and design decisions.",
                metadata=DocumentMetadata(
                    author="Architecture Team",
                    created_at=now - timedelta(days=200),
                    last_modified=now - timedelta(days=60),
                    file_size=2560000,
                    tags=["architecture", "prd", "technical"],
                    category="Product",
                ),
                access_count=15,
            ),
        ]

        return documents

    def search(self, query: str) -> List[Document]:
        """Search for documents matching the query."""
        if not self._available:
            raise Exception("S3 adapter is not available")

        query_lower = query.lower()
        results = []

        for doc in self._documents:
            title_lower = str(doc.title).lower()
            snippet_lower = doc.snippet.lower()
            tags = [tag.lower() for tag in doc.metadata.tags]

            # Check if query matches title, snippet, or tags
            if query_lower in title_lower or query_lower in snippet_lower or any(query_lower in tag for tag in tags):
                results.append(doc)

        return results

    def get_document(self, document_id) -> Optional[Document]:
        """Get a specific document by ID."""
        doc_id_str = str(document_id)
        for doc in self._documents:
            if str(doc.document_id) == doc_id_str:
                return doc
        return None

    def get_metadata(self, document_id) -> Optional[DocumentMetadata]:
        """Get metadata for a document."""
        doc = self.get_document(document_id)
        return doc.metadata if doc else None

    def is_available(self) -> bool:
        """Check if the provider is available."""
        return self._available

    def set_available(self, available: bool) -> None:
        """Set availability status (for testing)."""
        self._available = available
