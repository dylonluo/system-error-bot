from typing import List, Any
from datetime import datetime


class InMemoryEventPublisher:
    """In-memory event publisher for demo purposes."""
    
    def __init__(self):
        self._published_events: List[dict] = []
    
    def publish(self, event: Any) -> None:
        """Publish a domain event."""
        event_record = {
            'event': event,
            'event_type': type(event).__name__,
            'published_at': datetime.now(),
            'event_str': str(event)
        }
        self._published_events.append(event_record)
        print(f"[EVENT PUBLISHED] {event_record['event_type']}: {event_record['event_str']}")
    
    def get_published_events(self) -> List[dict]:
        """Get all published events (for testing)."""
        return self._published_events
    
    def clear_events(self) -> None:
        """Clear published events (for testing)."""
        self._published_events.clear()
    
    def get_events_by_type(self, event_type_name: str) -> List[dict]:
        """Get events by type name."""
        return [e for e in self._published_events if e['event_type'] == event_type_name]
