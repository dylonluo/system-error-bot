"""ConversationStatus value object"""
from enum import Enum


class ConversationStatus(Enum):
    """Status of a conversation"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

    def is_active(self) -> bool:
        return self == ConversationStatus.ACTIVE

    def is_resolved(self) -> bool:
        return self == ConversationStatus.RESOLVED

    def is_escalated(self) -> bool:
        return self == ConversationStatus.ESCALATED

    def can_transition_to(self, new_status: 'ConversationStatus') -> bool:
        """Check if transition to new status is valid"""
        valid_transitions = {
            ConversationStatus.ACTIVE: [ConversationStatus.RESOLVED, ConversationStatus.ESCALATED],
            ConversationStatus.RESOLVED: [],
            ConversationStatus.ESCALATED: []
        }
        return new_status in valid_transitions.get(self, [])
