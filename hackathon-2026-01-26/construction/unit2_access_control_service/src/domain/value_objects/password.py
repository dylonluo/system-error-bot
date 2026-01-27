"""Password Value Object - Represents a hashed password with validation."""
import re


class Password:
    """Value object representing a hashed password."""
    
    MIN_LENGTH = 8
    
    def __init__(self, hashed_value: str):
        """
        Initialize Password with hashed value.
        
        Args:
            hashed_value: Bcrypt hashed password string
            
        Raises:
            ValueError: If hashed_value is empty
        """
        if not hashed_value:
            raise ValueError("Password hash cannot be empty")
        
        self._hashed_value = hashed_value
    
    @property
    def hashed_value(self) -> str:
        """Get the hashed password value."""
        return self._hashed_value
    
    @staticmethod
    def validate_plain_password(plain_password: str) -> None:
        """
        Validate plain password meets requirements.
        
        Args:
            plain_password: Plain text password
            
        Raises:
            ValueError: If password doesn't meet requirements
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")
        
        if len(plain_password) < Password.MIN_LENGTH:
            raise ValueError(f"Password must be at least {Password.MIN_LENGTH} characters")
        
        if not re.search(r'[a-zA-Z]', plain_password):
            raise ValueError("Password must contain at least one letter")
        
        if not re.search(r'\d', plain_password):
            raise ValueError("Password must contain at least one number")
    
    def __eq__(self, other) -> bool:
        """Check equality with another Password."""
        if not isinstance(other, Password):
            return False
        return self._hashed_value == other._hashed_value
    
    def __str__(self) -> str:
        """Return masked representation for security."""
        return "********"
    
    def __repr__(self) -> str:
        """Return masked representation for security."""
        return "Password(********)"
