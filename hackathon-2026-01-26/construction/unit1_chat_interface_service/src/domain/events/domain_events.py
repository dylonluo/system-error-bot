"""Domain events for Chat Interface Context"""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from ..value_objects.conversation_id import ConversationId
from ..value_objects.message_id import MessageId
from ..value_objects.message_role import MessageRole


@dataclass
class DomainEvent:
    """Base class for domain events"""
    occurred_at: datetime

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass
class ConversationCreated(DomainEvent):
    """Event: Conversation was created"""
    conversation_id: ConversationId
    user_id: UUID
    occurred_at: datetime = None


@dataclass
class MessageAdded(DomainEvent):
    """Event: Message was added to conversation"""
    conversation_id: ConversationId
    message_id: MessageId
    role: MessageRole
    has_screenshot: bool
    occurred_at: datetime = None


@dataclass
class FeedbackSubmitted(DomainEvent):
    """Event: User submitted feedback on a message"""
    conversation_id: ConversationId
    message_id: MessageId
    answered_question: bool
    problem_solved: bool
    occurred_at: datetime = None


@dataclass
class ConversationResolved(DomainEvent):
    """Event: Conversation was marked as resolved"""
    conversation_id: ConversationId
    user_id: UUID
    occurred_at: datetime = None


@dataclass
class ConversationEscalated(DomainEvent):
    """Event: Conversation was escalated to human support"""
    conversation_id: ConversationId
    user_id: UUID
    reason: str
    occurred_at: datetime = None
