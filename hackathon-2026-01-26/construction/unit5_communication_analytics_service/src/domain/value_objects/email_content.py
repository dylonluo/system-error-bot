from dataclasses import dataclass
from enum import Enum


class EmailFormat(Enum):
    """Email content format."""
    PLAIN_TEXT = "plain_text"
    HTML = "html"


@dataclass(frozen=True)
class EmailContent:
    """Value object representing email content."""
    
    body: str
    format: EmailFormat = EmailFormat.PLAIN_TEXT
    
    def __post_init__(self):
        if not self.body or not self.body.strip():
            raise ValueError("Email body cannot be empty")
    
    def get_body(self) -> str:
        """Get the email body."""
        return self.body
    
    def is_plain_text(self) -> bool:
        """Check if content is plain text."""
        return self.format == EmailFormat.PLAIN_TEXT
    
    def is_html(self) -> bool:
        """Check if content is HTML."""
        return self.format == EmailFormat.HTML
    
    def __str__(self):
        return f"{self.format.value}: {self.body[:50]}..."
