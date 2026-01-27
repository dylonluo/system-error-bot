import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailId:
    """Value object representing a unique email identifier."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("EmailId cannot be empty")
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {self.value}")
    
    @staticmethod
    def generate():
        """Generate a new EmailId."""
        return EmailId(str(uuid.uuid4()))
    
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if not isinstance(other, EmailId):
            return False
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
