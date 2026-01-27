from enum import Enum


class EventType(Enum):
    """Types of analytics events."""
    QUERY_SUBMITTED = "query_submitted"
    FEEDBACK_SUBMITTED = "feedback_submitted"
    ESCALATION_TRIGGERED = "escalation_triggered"
    USER_AUTHENTICATED = "user_authenticated"
    DOCUMENT_ACCESSED = "document_accessed"
    
    def is_query_submitted(self) -> bool:
        return self == EventType.QUERY_SUBMITTED
    
    def is_feedback_submitted(self) -> bool:
        return self == EventType.FEEDBACK_SUBMITTED
    
    def is_escalation_triggered(self) -> bool:
        return self == EventType.ESCALATION_TRIGGERED
    
    def is_user_authenticated(self) -> bool:
        return self == EventType.USER_AUTHENTICATED
    
    def is_document_accessed(self) -> bool:
        return self == EventType.DOCUMENT_ACCESSED
    
    def __str__(self):
        return self.value
