"""Document Repository Service client (Unit 3)"""
import requests
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DocumentResult:
    """Document search result from Unit 3"""
    id: str
    title: str
    url: str
    source: str
    document_type: str
    format: str
    snippet: str
    relevance_score: float
    category: str
    tags: List[str]


class DocumentRepositoryClient:
    """Client for Document Repository Service (Unit 3)"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self._base_url = base_url
        self._available = False
        self._check_availability()
    
    def _check_availability(self):
        """Check if Unit 3 service is available"""
        try:
            response = requests.get(f"{self._base_url}/health", timeout=2)
            self._available = response.status_code == 200
        except Exception:
            self._available = False
    
    def is_available(self) -> bool:
        """Check if service is available"""
        return self._available
    
    def search_documents(self, query: str, user_id: str = "user-123", limit: int = 5) -> List[DocumentResult]:
        """Search for documents matching the query"""
        if not self._available:
            self._check_availability()
            if not self._available:
                return []
        
        try:
            response = requests.get(
                f"{self._base_url}/api/v1/documents/search",
                params={"query": query, "limit": limit},
                headers={"Authorization": user_id},
                timeout=10
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            results = []
            
            for item in data.get("results", [])[:limit]:
                results.append(DocumentResult(
                    id=item.get("id", ""),
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    source=item.get("source", "s3"),
                    document_type=item.get("document_type", "guide"),
                    format=item.get("format", "pdf"),
                    snippet=item.get("snippet", ""),
                    relevance_score=item.get("relevance_score", 0.5),
                    category=item.get("metadata", {}).get("category", "General"),
                    tags=item.get("metadata", {}).get("tags", [])
                ))
            
            return results
            
        except Exception as e:
            print(f"[DocumentRepositoryClient] Error searching: {e}")
            return []
