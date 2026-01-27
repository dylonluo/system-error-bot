import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class MetricId:
    """Value object representing a unique metric identifier."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("MetricId cannot be empty")
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {self.value}")
    
    @staticmethod
    def generate():
        """Generate a new MetricId."""
        return MetricId(str(uuid.uuid4()))
    
    def __str__(self):
        return self.value
    
    def __eq__(self, other):
        if not isinstance(other, MetricId):
            return False
        return self.value == other.value
    
    def __hash__(self):
        return hash(self.value)
