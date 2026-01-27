"""Conversation repository interface"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..aggregates.conversation import Conversation
from ..value_objects.conversation_id import ConversationId


class IConversationRepository(ABC):
    """Interface for conversation repository"""

    @abstractmethod
    def save(self, conversation: Conversation) -> None:
        """Save a conversation"""
        pass

    @abstractmethod
    def find_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """Find conversation by ID"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: UUID, limit: int, offset: int) -> List[Conversation]:
        """Find conversations by user ID"""
        pass

    @abstractmethod
    def find_recent_by_user_id(self, user_id: UUID, days: int) -> List[Conversation]:
        """Find recent conversations by user ID"""
        pass

    @abstractmethod
    def delete(self, conversation_id: ConversationId) -> None:
        """Delete a conversation"""
        pass

    @abstractmethod
    def delete_older_than(self, days: int) -> int:
        """Delete conversations older than specified days"""
        pass
