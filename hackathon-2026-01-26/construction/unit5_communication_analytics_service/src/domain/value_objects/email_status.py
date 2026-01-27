from enum import Enum


class EmailStatus(Enum):
    """Email delivery status."""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    
    def is_queued(self) -> bool:
        return self == EmailStatus.QUEUED
    
    def is_sent(self) -> bool:
        return self == EmailStatus.SENT
    
    def is_failed(self) -> bool:
        return self == EmailStatus.FAILED
    
    def can_transition_to(self, new_status: 'EmailStatus') -> bool:
        """Check if transition to new status is valid."""
        valid_transitions = {
            EmailStatus.QUEUED: [EmailStatus.SENT, EmailStatus.FAILED],
            EmailStatus.FAILED: [EmailStatus.QUEUED],  # Retry
            EmailStatus.SENT: []  # Terminal state
        }
        return new_status in valid_transitions.get(self, [])
    
    def __str__(self):
        return self.value
