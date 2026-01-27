from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from ...domain.entities import ContextMessage
from ...domain.entities.context_message import MessageRole


class IConversationContextClient(ABC):
    """Interface for conversation context client."""

    @abstractmethod
    def get_conversation_history(self, conversation_id: UUID, limit: int = 5) -> List[ContextMessage]:
        pass


class MockConversationContextClient(IConversationContextClient):
    """Mock conversation context client."""

    def get_conversation_history(self, conversation_id: UUID, limit: int = 5) -> List[ContextMessage]:
        """Returns sample conversation history."""
        # Return empty for new conversations, or sample for demo
        return [
            ContextMessage.create(
                role=MessageRole.USER,
                content="I'm having issues with my NetSuite integration",
            ),
            ContextMessage.create(
                role=MessageRole.ASSISTANT,
                content="I can help with that. What specific error are you seeing?",
            ),
        ][:limit]
