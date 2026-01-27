from typing import Dict, List, Optional
from uuid import UUID

from ...domain.aggregates import AIQuery
from ...domain.repositories import IAIQueryRepository
from ...domain.value_objects import QueryId


class InMemoryAIQueryRepository(IAIQueryRepository):
    """In-memory implementation of AI query repository."""

    def __init__(self):
        self._queries: Dict[str, AIQuery] = {}

    def save(self, ai_query: AIQuery) -> None:
        self._queries[str(ai_query.query_id)] = ai_query

    def find_by_id(self, query_id: QueryId) -> Optional[AIQuery]:
        return self._queries.get(str(query_id))

    def find_by_conversation_id(self, conversation_id: UUID) -> List[AIQuery]:
        return [
            q for q in self._queries.values()
            if q.conversation_id == conversation_id
        ]

    def find_by_user_id(self, user_id: UUID, limit: int = 10) -> List[AIQuery]:
        queries = [q for q in self._queries.values() if q.user_id == user_id]
        return sorted(queries, key=lambda q: q.created_at, reverse=True)[:limit]

    def find_low_confidence(self, threshold: float = 0.5) -> List[AIQuery]:
        return [
            q for q in self._queries.values()
            if q.confidence_score and q.confidence_score.value < threshold
        ]
