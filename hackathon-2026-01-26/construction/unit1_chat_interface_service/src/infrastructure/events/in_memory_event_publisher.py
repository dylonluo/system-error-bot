"""In-memory event publisher implementation"""
from typing import List
from ...domain.events.domain_events import DomainEvent


class InMemoryEventPublisher:
    """In-memory event publisher for testing"""

    def __init__(self):
        self._events: List[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event"""
        self._events.append(event)
        print(f"[EVENT] {event.__class__.__name__}: {event}")

    def get_events(self) -> List[DomainEvent]:
        """Get all published events"""
        return self._events.copy()

    def get_events_of_type(self, event_type: type) -> List[DomainEvent]:
        """Get events of specific type"""
        return [e for e in self._events if isinstance(e, event_type)]

    def clear(self) -> None:
        """Clear all events (for testing)"""
        self._events.clear()

    def count(self) -> int:
        """Count total events"""
        return len(self._events)
