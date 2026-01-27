import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAddress:
    """Value object representing an email address with validation."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Email address cannot be empty")
        if not self.is_valid():
            raise ValueError(f"Invalid email format: {self.value}")
    
    def is_valid(self) -> bool:
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.value))
    
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if not isinstance(other, EmailAddress):
            return False
        return self.value.lower() == other.value.lower()
    
    def __hash__(self):
        return hash(self.value.lower())
