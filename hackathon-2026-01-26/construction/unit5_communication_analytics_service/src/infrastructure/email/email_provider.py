from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class EmailResult:
    """Result of email sending operation."""
    success: bool
    message: str
    error: Optional[str] = None


class IEmailProvider(ABC):
    """Interface for email providers."""
    
    @abstractmethod
    def send(self, to: str, subject: str, body: str) -> EmailResult:
        """Send an email."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if email provider is available."""
        pass
