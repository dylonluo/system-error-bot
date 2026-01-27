from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..aggregates import AIQuery
from ..value_objects import QueryId


class IAIQueryRepository(ABC):
    """Repository interface for AI queries."""

    @abstractmethod
    def save(self, ai_query: AIQuery) -> None:
        """Save an AI query."""
        pass

    @abstractmethod
    def find_by_id(self, query_id: QueryId) -> Optional[AIQuery]:
        """Find a query by ID."""
        pass

    @abstractmethod
    def find_by_conversation_id(self, conversation_id: UUID) -> List[AIQuery]:
        """Find all queries for a conversation."""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: UUID, limit: int = 10) -> List[AIQuery]:
        """Find queries by user ID."""
        pass

    @abstractmethod
    def find_low_confidence(self, threshold: float = 0.5) -> List[AIQuery]:
        """Find queries with confidence below threshold."""
        pass
