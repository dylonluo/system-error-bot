"""MessageRole value object"""
from enum import Enum


class MessageRole(Enum):
    """Role of a message sender"""
    USER = "user"
    ASSISTANT = "assistant"

    def is_user(self) -> bool:
        return self == MessageRole.USER

    def is_assistant(self) -> bool:
        return self == MessageRole.ASSISTANT
