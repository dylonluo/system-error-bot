"""UserId Value Object - Represents a unique user identifier."""
import uuid
from typing import Union


class UserId:
    """Value object representing a unique user identifier using UUID."""
    
    def __init__(self, value: Union[str, uuid.UUID]):
        """
        Initialize UserId.
        
        Args:
            value: UUID string or UUID object
            
        Raises:
            ValueError: If value is not a valid UUID
        """
        if isinstance(value, str):
            try:
                self._value = uuid.UUID(value)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {value}")
        elif isinstance(value, uuid.UUID):
            self._value = value
        else:
            raise ValueError(f"UserId must be string or UUID, got {type(value)}")
    
    @classmethod
    def generate(cls) -> 'UserId':
        """Generate a new random UserId."""
        return cls(uuid.uuid4())
    
    @property
    def value(self) -> uuid.UUID:
        """Get the UUID value."""
        return self._value
    
    def __eq__(self, other) -> bool:
        """Check equality with another UserId."""
        if not isinstance(other, UserId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Return hash of the UserId."""
        return hash(self._value)
    
    def __str__(self) -> str:
        """Return string representation."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"UserId('{self._value}')"
