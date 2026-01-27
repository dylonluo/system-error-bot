from typing import List, Callable, Dict, Type
from ...domain.events import DomainEvent


class InMemoryEventPublisher:
    """Simple in-memory event publisher."""

    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = {}
        self._published_events: List[DomainEvent] = []

    def subscribe(self, event_type: Type[DomainEvent], handler: Callable) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        self._published_events.append(event)
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)

    def get_published_events(self) -> List[DomainEvent]:
        """Get all published events (for testing)."""
        return self._published_events.copy()

    def clear(self) -> None:
        """Clear all published events."""
        self._published_events.clear()
