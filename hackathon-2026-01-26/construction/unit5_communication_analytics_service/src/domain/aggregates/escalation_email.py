from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..value_objects import (
    EmailId, EmailAddress, EmailContent, EmailStatus, ConversationSnapshot
)


@dataclass
class EscalationEmail:
    """Aggregate root representing an escalation email."""
    
    email_id: EmailId
    conversation_id: str
    user_id: str
    recipient_email: EmailAddress
    subject: str
    content: EmailContent
    conversation_snapshot: ConversationSnapshot
    screenshots: List[str] = field(default_factory=list)
    status: EmailStatus = EmailStatus.QUEUED
    sent_at: Optional[datetime] = None
    delivery_confirmed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    MAX_RETRIES = 3
    
    def send(self) -> None:
        """Mark email as being sent."""
        if not self.status.is_queued():
            raise ValueError(f"Cannot send email with status: {self.status}")
        # Status will be updated by mark_as_sent or mark_as_failed
    
    def mark_as_sent(self) -> None:
        """Mark email as successfully sent."""
        if not self.status.can_transition_to(EmailStatus.SENT):
            raise ValueError(f"Cannot transition from {self.status} to SENT")
        self.status = EmailStatus.SENT
        self.sent_at = datetime.now()
        self.failure_reason = None
    
    def mark_as_failed(self, reason: str) -> None:
        """Mark email as failed with reason."""
        if not self.status.can_transition_to(EmailStatus.FAILED):
            raise ValueError(f"Cannot transition from {self.status} to FAILED")
        self.status = EmailStatus.FAILED
        self.failure_reason = reason
        self.retry_count += 1
    
    def retry(self) -> None:
        """Retry sending the email."""
        if not self.can_retry():
            raise ValueError(f"Cannot retry: max retries ({self.MAX_RETRIES}) reached")
        if not self.status.is_failed():
            raise ValueError("Can only retry failed emails")
        self.status = EmailStatus.QUEUED
        self.failure_reason = None
    
    def can_retry(self) -> bool:
        """Check if email can be retried."""
        return self.status.is_failed() and self.retry_count < self.MAX_RETRIES
    
    def get_conversation_history(self) -> str:
        """Get formatted conversation history."""
        return self.conversation_snapshot.format_for_email()
    
    def __eq__(self, other):
        if not isinstance(other, EscalationEmail):
            return False
        return self.email_id == other.email_id
    
    def __hash__(self):
        return hash(self.email_id)
    
    def __str__(self):
        return f"EscalationEmail({self.email_id}, {self.status}, retry={self.retry_count})"
