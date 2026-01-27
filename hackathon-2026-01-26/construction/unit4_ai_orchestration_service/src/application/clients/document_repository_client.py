"""Real Document Repository Client connecting to Unit 3"""
import requests
from typing import List, Optional
from uuid import uuid4

from .mock_document_search_client import IDocumentSearchClient
from ...domain.services.response_generation_service import DocumentLink


class DocumentRepositoryClient(IDocumentSearchClient):
    """Client for Document Repository Service (Unit 3)."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self._base_url = base_url
        self._available = False
        self._check_availability()

    def _check_availability(self):
        """Check if Unit 3 is available."""
        try:
            response = requests.get(f"{self._base_url}/health", timeout=2)
            self._available = response.status_code == 200
            if self._available:
                print(f"[Document Client] Connected to Unit 3 at {self._base_url}")
        except Exception as e:
            print(f"[Document Client] Unit 3 not available: {e}")
            self._available = False

    def is_available(self) -> bool:
        """Check if service is available."""
        return self._available

    def search(self, query: str, filters: Optional[dict] = None) -> List[DocumentLink]:
        """Search for documents using Unit 3."""
        if not self._available:
            self._check_availability()
            if not self._available:
                return []

        try:
            response = requests.get(
                f"{self._base_url}/api/v1/documents/search",
                params={"query": query, "limit": 5},
                headers={"Authorization": "user-123"},
                timeout=10
            )

            if response.status_code != 200:
                return []

            data = response.json()
            results = []

            for item in data.get("results", [])[:5]:
                results.append(DocumentLink(
                    document_id=item.get("id", str(uuid4())),
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    description=item.get("snippet", ""),
                    category=item.get("metadata", {}).get("category", "General"),
                    relevance=item.get("relevance_score", 0.5),
                ))

            return results

        except Exception as e:
            print(f"[Document Client] Error searching: {e}")
            return []
