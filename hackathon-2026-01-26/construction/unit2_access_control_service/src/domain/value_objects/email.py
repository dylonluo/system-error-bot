"""Email Value Object - Represents a validated email address."""
import re


class Email:
    """Value object representing an email address with validation."""
    
    # Simplified email regex (RFC 5322 compliant would be much more complex)
    PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, value: str):
        """
        Initialize Email.
        
        Args:
            value: Email address string
            
        Raises:
            ValueError: If email format is invalid
        """
        if not value:
            raise ValueError("Email cannot be empty")
        
        if not self.PATTERN.match(value):
            raise ValueError(f"Invalid email format: {value}")
        
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the email value."""
        return self._value
    
    def to_lower(self) -> str:
        """Return lowercase version for case-insensitive comparison."""
        return self._value.lower()
    
    def __eq__(self, other) -> bool:
        """Check equality (case-insensitive)."""
        if not isinstance(other, Email):
            return False
        return self.to_lower() == other.to_lower()
    
    def __hash__(self) -> int:
        """Return hash (case-insensitive)."""
        return hash(self.to_lower())
    
    def __str__(self) -> str:
        """Return string representation."""
        return self._value
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Email('{self._value}')"
