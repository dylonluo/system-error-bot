from pydantic import BaseModel
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime


class DocumentationLinkResponse(BaseModel):
    """A documentation link in the response."""
    title: str
    url: str
    description: str
    category: str
    relevance: float = 0.0  # Similarity score from semantic search


class ProcessQueryResponse(BaseModel):
    """Response from processing an AI query."""
    query_id: UUID
    response: str
    documentation_links: List[DocumentationLinkResponse]
    confidence: float
    suggest_escalation: bool
    processing_time_ms: int
    intent: str


class DetectIntentResponse(BaseModel):
    """Response from intent detection."""
    intent: str
    confidence: float
    entities: Dict[str, str]


class QueryDetailsResponse(BaseModel):
    """Detailed query information."""
    query_id: UUID
    conversation_id: UUID
    query_text: str
    intent: Optional[str]
    response: Optional[str]
    confidence: Optional[float]
    suggest_escalation: bool
    created_at: datetime
    completed_at: Optional[datetime]
    processing_time_ms: Optional[int]
