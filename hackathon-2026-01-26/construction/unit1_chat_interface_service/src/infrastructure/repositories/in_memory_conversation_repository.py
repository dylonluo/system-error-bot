"""In-memory conversation repository implementation"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID
from ...domain.aggregates.conversation import Conversation
from ...domain.value_objects.conversation_id import ConversationId
from ...domain.repositories.conversation_repository import IConversationRepository


class InMemoryConversationRepository(IConversationRepository):
    """In-memory implementation of conversation repository"""

    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}

    def save(self, conversation: Conversation) -> None:
        """Save a conversation"""
        key = str(conversation.conversation_id)
        self._conversations[key] = conversation

    def find_by_id(self, conversation_id: ConversationId) -> Optional[Conversation]:
        """Find conversation by ID"""
        key = str(conversation_id)
        return self._conversations.get(key)

    def find_by_user_id(self, user_id: UUID, limit: int, offset: int) -> List[Conversation]:
        """Find conversations by user ID"""
        user_conversations = [
            conv for conv in self._conversations.values()
            if conv.user_id == user_id
        ]
        # Sort by last_message_at descending
        user_conversations.sort(
            key=lambda c: c.last_message_at or c.created_at,
            reverse=True
        )
        return user_conversations[offset:offset + limit]

    def find_recent_by_user_id(self, user_id: UUID, days: int) -> List[Conversation]:
        """Find recent conversations by user ID"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_conversations = [
            conv for conv in self._conversations.values()
            if conv.user_id == user_id and conv.created_at >= cutoff_date
        ]
        recent_conversations.sort(
            key=lambda c: c.last_message_at or c.created_at,
            reverse=True
        )
        return recent_conversations

    def delete(self, conversation_id: ConversationId) -> None:
        """Delete a conversation"""
        key = str(conversation_id)
        if key in self._conversations:
            del self._conversations[key]

    def delete_older_than(self, days: int) -> int:
        """Delete conversations older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        to_delete = [
            conv_id for conv_id, conv in self._conversations.items()
            if conv.created_at < cutoff_date
        ]
        for conv_id in to_delete:
            del self._conversations[conv_id]
        return len(to_delete)

    def clear(self) -> None:
        """Clear all conversations (for testing)"""
        self._conversations.clear()
