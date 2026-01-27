from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from ..value_objects import EventId, EventType, EventMetadata


@dataclass
class AnalyticsEvent:
    """Aggregate root representing an analytics event."""
    
    event_id: EventId
    event_type: EventType
    user_id: str
    conversation_id: Optional[str]
    metadata: EventMetadata
    occurred_at: datetime = field(default_factory=datetime.now)
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata value by key."""
        return self.metadata.get(key)
    
    def has_metadata(self, key: str) -> bool:
        """Check if metadata has a key."""
        return self.metadata.has(key)
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return self.metadata.to_json()
    
    def __eq__(self, other):
        if not isinstance(other, AnalyticsEvent):
            return False
        return self.event_id == other.event_id
    
    def __hash__(self):
        return hash(self.event_id)
    
    def __str__(self):
        return f"AnalyticsEvent({self.event_id}, {self.event_type}, {self.occurred_at.isoformat()})"
