from abc import ABC, abstractmethod
from typing import List, Optional
from ..aggregates import EscalationEmail
from ..value_objects import EmailId


class IEscalationEmailRepository(ABC):
    """Repository interface for EscalationEmail aggregate."""
    
    @abstractmethod
    def save(self, email: EscalationEmail) -> None:
        """Save an escalation email."""
        pass
    
    @abstractmethod
    def find_by_id(self, email_id: EmailId) -> Optional[EscalationEmail]:
        """Find escalation email by ID."""
        pass
    
    @abstractmethod
    def find_by_conversation_id(self, conversation_id: str) -> Optional[EscalationEmail]:
        """Find escalation email by conversation ID."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str, limit: int = 10) -> List[EscalationEmail]:
        """Find escalation emails by user ID."""
        pass
    
    @abstractmethod
    def find_queued(self) -> List[EscalationEmail]:
        """Find all queued emails."""
        pass
    
    @abstractmethod
    def find_failed(self) -> List[EscalationEmail]:
        """Find all failed emails."""
        pass
    
    @abstractmethod
    def delete_older_than(self, days: int) -> int:
        """Delete emails older than specified days. Returns count deleted."""
        pass
