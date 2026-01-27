from datetime import datetime, timedelta
from typing import List, Optional, Dict
from ...domain.aggregates import EscalationEmail
from ...domain.value_objects import EmailId, EmailStatus
from ...domain.repositories import IEscalationEmailRepository


class InMemoryEscalationEmailRepository(IEscalationEmailRepository):
    """In-memory implementation of EscalationEmail repository."""
    
    def __init__(self):
        self._emails: Dict[str, EscalationEmail] = {}
    
    def save(self, email: EscalationEmail) -> None:
        """Save an escalation email."""
        self._emails[str(email.email_id)] = email
    
    def find_by_id(self, email_id: EmailId) -> Optional[EscalationEmail]:
        """Find escalation email by ID."""
        return self._emails.get(str(email_id))
    
    def find_by_conversation_id(self, conversation_id: str) -> Optional[EscalationEmail]:
        """Find escalation email by conversation ID."""
        for email in self._emails.values():
            if email.conversation_id == conversation_id:
                return email
        return None
    
    def find_by_user_id(self, user_id: str, limit: int = 10) -> List[EscalationEmail]:
        """Find escalation emails by user ID."""
        emails = [email for email in self._emails.values() if email.user_id == user_id]
        # Sort by created_at descending
        emails.sort(key=lambda e: e.created_at, reverse=True)
        return emails[:limit]
    
    def find_queued(self) -> List[EscalationEmail]:
        """Find all queued emails."""
        return [email for email in self._emails.values() if email.status == EmailStatus.QUEUED]
    
    def find_failed(self) -> List[EscalationEmail]:
        """Find all failed emails."""
        return [email for email in self._emails.values() if email.status == EmailStatus.FAILED]
    
    def delete_older_than(self, days: int) -> int:
        """Delete emails older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        to_delete = [
            email_id for email_id, email in self._emails.items()
            if email.created_at < cutoff_date
        ]
        for email_id in to_delete:
            del self._emails[email_id]
        return len(to_delete)
