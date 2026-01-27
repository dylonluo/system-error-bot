from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from ..value_objects import (
    QueryId,
    QueryText,
    Intent,
    ConfidenceScore,
    AIResponse,
    ProcessingMetrics,
)
from ..entities import ContextMessage


@dataclass
class AIQuery:
    """Aggregate root for AI query processing."""
    query_id: QueryId
    conversation_id: UUID
    user_id: UUID
    query_text: QueryText
    created_at: datetime
    context_messages: List[ContextMessage] = field(default_factory=list)
    intent: Optional[Intent] = None
    ai_response: Optional[AIResponse] = None
    confidence_score: Optional[ConfidenceScore] = None
    metrics: Optional[ProcessingMetrics] = None
    completed_at: Optional[datetime] = None

    @classmethod
    def create(cls, conversation_id: UUID, user_id: UUID, query_text: str) -> "AIQuery":
        return cls(
            query_id=QueryId.generate(),
            conversation_id=conversation_id,
            user_id=user_id,
            query_text=QueryText(query_text),
            created_at=datetime.utcnow(),
        )

    def add_context(self, messages: List[ContextMessage], max_messages: int = 5) -> None:
        """Add conversation context (max 5 messages)."""
        self.context_messages = messages[:max_messages]

    def set_intent(self, intent: Intent) -> None:
        self.intent = intent

    def set_ai_response(self, response: AIResponse) -> None:
        self.ai_response = response

    def set_confidence(self, score: ConfidenceScore) -> None:
        self.confidence_score = score

    def record_metrics(self, metrics: ProcessingMetrics) -> None:
        self.metrics = metrics
        self.completed_at = datetime.utcnow()

    def should_escalate(self, threshold: float = 0.5) -> bool:
        """Check if query should be escalated to human support."""
        if self.confidence_score is None:
            return False
        return self.confidence_score.should_escalate(threshold)

    def is_off_topic(self) -> bool:
        """Check if query is off-topic."""
        return self.intent is not None and self.intent.is_off_topic()
