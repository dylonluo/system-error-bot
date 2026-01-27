from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ContextMessage:
    """A message from conversation context."""
    message_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime

    @classmethod
    def create(cls, role: MessageRole, content: str) -> "ContextMessage":
        return cls(
            message_id=uuid4(),
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
        )

    def is_user_message(self) -> bool:
        return self.role == MessageRole.USER

    def is_assistant_message(self) -> bool:
        return self.role == MessageRole.ASSISTANT

    def get_content(self) -> str:
        return self.content
