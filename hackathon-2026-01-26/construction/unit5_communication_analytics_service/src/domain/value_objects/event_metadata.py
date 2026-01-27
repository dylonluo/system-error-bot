import json
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class EventMetadata:
    """Value object representing event metadata as JSON."""
    
    data: Dict[str, Any]
    
    def __post_init__(self):
        if not isinstance(self.data, dict):
            raise ValueError("Metadata must be a dictionary")
        # Validate that data is JSON serializable
        try:
            json.dumps(self.data)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Metadata must be JSON serializable: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get metadata value by key."""
        return self.data.get(key)
    
    def has(self, key: str) -> bool:
        """Check if metadata has a key."""
        return key in self.data
    
    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.data)
    
    @staticmethod
    def from_json(json_str: str) -> 'EventMetadata':
        """Create EventMetadata from JSON string."""
        try:
            data = json.loads(json_str)
            return EventMetadata(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @staticmethod
    def empty() -> 'EventMetadata':
        """Create empty metadata."""
        return EventMetadata({})
    
    def __str__(self):
        return self.to_json()
