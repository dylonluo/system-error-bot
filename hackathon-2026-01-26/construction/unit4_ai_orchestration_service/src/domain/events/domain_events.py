from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional


@dataclass
class DomainEvent:
    """Base class for domain events."""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryProcessed(DomainEvent):
    """Event raised when a query is successfully processed."""
    query_id: UUID = field(default_factory=uuid4)
    conversation_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    intent: str = ""
    confidence: float = 0.0
    processing_time_ms: int = 0


@dataclass
class LowConfidenceDetected(DomainEvent):
    """Event raised when confidence is below threshold."""
    query_id: UUID = field(default_factory=uuid4)
    confidence: float = 0.0
    threshold: float = 0.5


@dataclass
class IntentDetected(DomainEvent):
    """Event raised when intent is detected."""
    query_id: UUID = field(default_factory=uuid4)
    intent: str = ""
    confidence: float = 0.0


@dataclass
class OffTopicQueryDetected(DomainEvent):
    """Event raised when an off-topic query is detected."""
    query_id: UUID = field(default_factory=uuid4)
    query_text: str = ""


@dataclass
class AIServiceError(DomainEvent):
    """Event raised when AI service fails."""
    query_id: UUID = field(default_factory=uuid4)
    error_message: str = ""
    provider: str = ""
