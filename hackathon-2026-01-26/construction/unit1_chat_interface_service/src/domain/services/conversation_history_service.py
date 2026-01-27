"""Conversation history domain service"""
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from ..aggregates.conversation import Conversation
from ..value_objects.conversation_id import ConversationId
from ..repositories.conversation_repository import IConversationRepository


class ConversationHistoryService:
    """Domain service for managing conversation history"""

    def __init__(self, repository: IConversationRepository):
        self._repository = repository

    def get_conversation_history(self, user_id: UUID, limit: int = 10) -> List[Conversation]:
        """Get conversation history for a user"""
        return self._repository.find_by_user_id(user_id, limit=limit, offset=0)

    def cleanup_old_conversations(self, retention_days: int = 30) -> int:
        """Delete conversations older than retention period"""
        return self._repository.delete_older_than(retention_days)

    def can_continue_conversation(self, conversation_id: ConversationId, user_id: UUID) -> bool:
        """Check if user can continue a conversation"""
        conversation = self._repository.find_by_id(conversation_id)
        if conversation is None:
            return False

        # Check ownership
        if not conversation.is_owned_by(user_id):
            return False

        # Check if conversation can accept messages
        return conversation.can_add_message()
