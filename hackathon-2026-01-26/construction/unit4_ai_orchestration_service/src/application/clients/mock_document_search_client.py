from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import uuid4

from ...domain.services.response_generation_service import DocumentLink


class IDocumentSearchClient(ABC):
    """Interface for document search client."""

    @abstractmethod
    def search(self, query: str, filters: Optional[dict] = None) -> List[DocumentLink]:
        pass


class MockDocumentSearchClient(IDocumentSearchClient):
    """Mock document search client with sample NetSuite/TMS documents."""

    SAMPLE_DOCS = [
        DocumentLink(
            document_id=str(uuid4()),
            title="NetSuite Error Codes Reference",
            url="https://docs.example.com/netsuite/error-codes",
            description="Complete list of NetSuite error codes and their meanings",
            category="Error Reference",
            relevance=0.95,
        ),
        DocumentLink(
            document_id=str(uuid4()),
            title="TMS Troubleshooting Guide",
            url="https://docs.example.com/tms/troubleshooting",
            description="Step-by-step troubleshooting for common TMS issues",
            category="Troubleshooting",
            relevance=0.90,
        ),
        DocumentLink(
            document_id=str(uuid4()),
            title="NetSuite Workflow Configuration",
            url="https://docs.example.com/netsuite/workflows",
            description="How to create and configure workflows in NetSuite",
            category="Configuration",
            relevance=0.85,
        ),
        DocumentLink(
            document_id=str(uuid4()),
            title="TMS Carrier Setup Guide",
            url="https://docs.example.com/tms/carrier-setup",
            description="Configure carriers and shipping methods in TMS",
            category="Configuration",
            relevance=0.80,
        ),
        DocumentLink(
            document_id=str(uuid4()),
            title="SuiteScript 2.0 API Reference",
            url="https://docs.example.com/netsuite/suitescript-api",
            description="Complete API reference for SuiteScript 2.0",
            category="API Reference",
            relevance=0.75,
        ),
    ]

    def search(self, query: str, filters: Optional[dict] = None) -> List[DocumentLink]:
        """Return sample documents based on query keywords."""
        query_lower = query.lower()
        results = []

        for doc in self.SAMPLE_DOCS:
            # Simple keyword matching
            if any(kw in query_lower for kw in ["error", "troubleshoot", "failed"]):
                if "Error" in doc.category or "Troubleshooting" in doc.category:
                    results.append(doc)
            elif any(kw in query_lower for kw in ["configure", "setup", "create"]):
                if "Configuration" in doc.category:
                    results.append(doc)
            elif "api" in query_lower or "script" in query_lower:
                if "API" in doc.category:
                    results.append(doc)

        # If no specific matches, return top 3 docs
        if not results:
            results = self.SAMPLE_DOCS[:3]

        return results
