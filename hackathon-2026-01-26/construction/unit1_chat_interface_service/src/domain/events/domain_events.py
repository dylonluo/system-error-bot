"""Domain events for Chat Interface Context"""
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from ..value_objects.conversation_id import ConversationId
from ..value_objects.message_id import MessageId
from ..value_objects.message_role import MessageRole


@dataclass
class DomainEvent:
    """Base class for domain events"""
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConversationCreated(DomainEvent):
    """Event: Conversation was created"""
    conversation_id: ConversationId = field(default=None)
    user_id: UUID = field(default=None)


@dataclass
class MessageAdded(DomainEvent):
    """Event: Message was added to conversation"""
    conversation_id: ConversationId = field(default=None)
    message_id: MessageId = field(default=None)
    role: MessageRole = field(default=None)
    has_screenshot: bool = field(default=False)


@dataclass
class FeedbackSubmitted(DomainEvent):
    """Event: User submitted feedback on a message"""
    conversation_id: ConversationId = field(default=None)
    message_id: MessageId = field(default=None)
    answered_question: bool = field(default=False)
    problem_solved: bool = field(default=False)


@dataclass
class ConversationResolved(DomainEvent):
    """Event: Conversation was marked as resolved"""
    conversation_id: ConversationId = field(default=None)
    user_id: UUID = field(default=None)


@dataclass
class ConversationEscalated(DomainEvent):
    """Event: Conversation was escalated to human support"""
    conversation_id: ConversationId = field(default=None)
    user_id: UUID = field(default=None)
    reason: str = field(default="")
