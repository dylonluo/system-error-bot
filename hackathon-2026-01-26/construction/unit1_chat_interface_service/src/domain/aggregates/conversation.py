"""Conversation aggregate root"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from ..value_objects.conversation_id import ConversationId
from ..value_objects.conversation_status import ConversationStatus
from ..value_objects.message_id import MessageId
from ..value_objects.message_role import MessageRole
from ..value_objects.screenshot import Screenshot
from ..value_objects.documentation_link import DocumentationLink
from .message import Message


class Conversation:
    """Conversation aggregate root"""

    def __init__(
        self,
        conversation_id: ConversationId,
        user_id: UUID,
        status: ConversationStatus = ConversationStatus.ACTIVE,
        title: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_message_at: Optional[datetime] = None
    ):
        self._conversation_id = conversation_id
        self._user_id = user_id
        self._status = status
        self._title = title
        self._messages: List[Message] = []
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._last_message_at = last_message_at

    @property
    def conversation_id(self) -> ConversationId:
        return self._conversation_id

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def status(self) -> ConversationStatus:
        return self._status

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def messages(self) -> List[Message]:
        return sorted(self._messages, key=lambda m: m.timestamp)

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def last_message_at(self) -> Optional[datetime]:
        return self._last_message_at

    def add_message(
        self,
        content: str,
        role: MessageRole,
        screenshot: Optional[Screenshot] = None,
        documentation_links: Optional[List[DocumentationLink]] = None
    ) -> Message:
        """Add a message to the conversation"""
        if not self.can_add_message():
            raise ValueError(f"Cannot add message to conversation with status {self._status.value}")

        # Validate screenshot only for user messages
        if screenshot and not role.is_user():
            raise ValueError("Only user messages can have screenshots")

        # Validate documentation links only for assistant messages
        if documentation_links and not role.is_assistant():
            raise ValueError("Only assistant messages can have documentation links")

        # Create message
        message = Message(
            message_id=MessageId.generate(),
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            screenshot=screenshot,
            documentation_links=documentation_links
        )

        self._messages.append(message)
        self._last_message_at = message.timestamp
        self._updated_at = datetime.utcnow()

        # Auto-generate title from first message
        if self._title is None and role.is_user():
            self._title = content[:50] + ("..." if len(content) > 50 else "")

        return message

    def mark_as_resolved(self) -> None:
        """Mark conversation as resolved"""
        if len(self._messages) == 0:
            raise ValueError("Cannot resolve conversation with no messages")

        if not self._status.can_transition_to(ConversationStatus.RESOLVED):
            raise ValueError(f"Cannot transition from {self._status.value} to resolved")

        self._status = ConversationStatus.RESOLVED
        self._updated_at = datetime.utcnow()

    def escalate_to_support(self, reason: Optional[str] = None) -> None:
        """Escalate conversation to human support"""
        if not self._status.can_transition_to(ConversationStatus.ESCALATED):
            raise ValueError(f"Cannot escalate conversation with status {self._status.value}")

        self._status = ConversationStatus.ESCALATED
        self._updated_at = datetime.utcnow()

    def can_add_message(self) -> bool:
        """Check if messages can be added to this conversation"""
        return self._status.is_active()

    def is_owned_by(self, user_id: UUID) -> bool:
        """Check if conversation is owned by user"""
        return self._user_id == user_id

    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages"""
        sorted_messages = self.messages
        return sorted_messages[-limit:] if len(sorted_messages) > limit else sorted_messages

    def find_message(self, message_id: MessageId) -> Optional[Message]:
        """Find message by ID"""
        for message in self._messages:
            if message.message_id == message_id:
                return message
        return None
