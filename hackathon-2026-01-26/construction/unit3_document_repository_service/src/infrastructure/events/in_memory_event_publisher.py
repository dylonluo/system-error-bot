"""In-memory event publisher."""

from datetime import datetime
from typing import List


class InMemoryEventPublisher:
    """Simple in-memory event publisher that logs events."""

    def __init__(self):
        self._events: List = []

    def publish(self, event) -> None:
        """Publish a domain event."""
        self._events.append(event)
        # Log the event
        print(f"[EVENT] {event.__class__.__name__} at {datetime.now().isoformat()}")
        print(f"        {event.to_dict()}")

    def get_events(self) -> List:
        """Get all published events."""
        return self._events

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()
