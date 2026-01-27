from typing import Optional
from uuid import UUID

from ...domain.repositories import IAIQueryRepository
from ...domain.value_objects import QueryId
from ..dtos import QueryDetailsResponse


class GetQueryDetailsService:
    """Application service for retrieving query details."""

    def __init__(self, repository: IAIQueryRepository):
        self._repository = repository

    def execute(self, query_id: str) -> Optional[QueryDetailsResponse]:
        """Get details of a processed query."""
        ai_query = self._repository.find_by_id(QueryId.from_string(query_id))
        
        if not ai_query:
            return None

        return QueryDetailsResponse(
            query_id=ai_query.query_id.value,
            conversation_id=ai_query.conversation_id,
            query_text=str(ai_query.query_text),
            intent=ai_query.intent.intent_type.value if ai_query.intent else None,
            response=ai_query.ai_response.content if ai_query.ai_response else None,
            confidence=ai_query.confidence_score.value if ai_query.confidence_score else None,
            suggest_escalation=ai_query.should_escalate(),
            created_at=ai_query.created_at,
            completed_at=ai_query.completed_at,
            processing_time_ms=ai_query.metrics.total_time_ms if ai_query.metrics else None,
        )
