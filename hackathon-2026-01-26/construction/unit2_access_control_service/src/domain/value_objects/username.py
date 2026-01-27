"""Username Value Object - Represents a validated username."""
import re


class Username:
    """Value object representing a username with validation rules."""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
    
    def __init__(self, value: str):
        """
        Initialize Username.
        
        Args:
            value: Username string
            
        Raises:
            ValueError: If username doesn't meet requirements
        """
        if not value:
            raise ValueError("Username cannot be empty")
        
        if len(value) < self.MIN_LENGTH:
            raise ValueError(f"Username must be at least {self.MIN_LENGTH} characters")
        
        if len(value) > self.MAX_LENGTH:
            raise ValueError(f"Username must not exceed {self.MAX_LENGTH} characters")
        
        if not self.PATTERN.match(value):
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        
        self._value = value
    
    @property
    def value(self) -> str:
        """Get the username value."""
        return self._value
    
    def to_lower(self) -> str:
        """Return lowercase version for case-insensitive comparison."""
        return self._value.lower()
    
    def __eq__(self, other) -> bool:
        """Check equality (case-insensitive)."""
        if not isinstance(other, Username):
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
        return f"Username('{self._value}')"
