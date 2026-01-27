"""Response DTOs for Document Repository Service."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentMetadataResponse(BaseModel):
    """Response DTO for document metadata."""

    author: Optional[str] = None
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    file_size: Optional[int] = None
    tags: List[str] = []
    category: Optional[str] = None


class DocumentResponse(BaseModel):
    """Response DTO for a document."""

    id: str
    title: str
    url: str
    source: str
    platform_id: str
    document_type: str
    format: str
    access_level: str
    snippet: str
    relevance_score: Optional[float] = None
    metadata: Optional[DocumentMetadataResponse] = None
    last_modified: Optional[datetime] = None
    access_count: int = 0


class SearchResultsResponse(BaseModel):
    """Response DTO for search results."""

    query: str
    total_results: int
    results: List[DocumentResponse]
    execution_time_ms: int = 0
