"""In-Memory Event Publisher - Simple event publisher for demo."""
from typing import List
from ...domain.events import DomainEvent


class InMemoryEventPublisher:
    """In-memory event publisher that stores events for inspection."""
    
    def __init__(self):
        """Initialize event storage."""
        self._events: List[DomainEvent] = []
    
    def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.
        
        Args:
            event: Domain event to publish
        """
        self._events.append(event)
        print(f"[EVENT] {event.__class__.__name__}: {event}")
    
    def get_events(self) -> List[DomainEvent]:
        """Get all published events."""
        return self._events.copy()
    
    def get_events_by_type(self, event_type: type) -> List[DomainEvent]:
        """
        Get events of a specific type.
        
        Args:
            event_type: Type of event to filter
            
        Returns:
            List of events of the specified type
        """
        return [event for event in self._events if isinstance(event, event_type)]
    
    def clear(self) -> None:
        """Clear all events (for testing)."""
        self._events.clear()
    
    def count(self) -> int:
        """Get count of published events."""
        return len(self._events)
