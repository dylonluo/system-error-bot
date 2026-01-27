from datetime import datetime, timedelta
from typing import List, Optional, Dict
from ...domain.aggregates import AnalyticsEvent
from ...domain.value_objects import EventId, EventType
from ...domain.repositories import IAnalyticsEventRepository


class InMemoryAnalyticsEventRepository(IAnalyticsEventRepository):
    """In-memory implementation of AnalyticsEvent repository."""
    
    def __init__(self):
        self._events: Dict[str, AnalyticsEvent] = {}
    
    def save(self, event: AnalyticsEvent) -> None:
        """Save an analytics event."""
        self._events[str(event.event_id)] = event
    
    def find_by_id(self, event_id: EventId) -> Optional[AnalyticsEvent]:
        """Find analytics event by ID."""
        return self._events.get(str(event_id))
    
    def find_by_type(self, event_type: EventType, start_date: datetime, end_date: datetime) -> List[AnalyticsEvent]:
        """Find analytics events by type within date range."""
        return [
            event for event in self._events.values()
            if event.event_type == event_type
            and start_date <= event.occurred_at <= end_date
        ]
    
    def find_by_user_id(self, user_id: str, start_date: datetime, end_date: datetime) -> List[AnalyticsEvent]:
        """Find analytics events by user ID within date range."""
        return [
            event for event in self._events.values()
            if event.user_id == user_id
            and start_date <= event.occurred_at <= end_date
        ]
    
    def count_by_type(self, event_type: EventType, start_date: datetime, end_date: datetime) -> int:
        """Count analytics events by type within date range."""
        return len(self.find_by_type(event_type, start_date, end_date))
    
    def delete_older_than(self, days: int) -> int:
        """Delete events older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)
        to_delete = [
            event_id for event_id, event in self._events.items()
            if event.occurred_at < cutoff_date
        ]
        for event_id in to_delete:
            del self._events[event_id]
        return len(to_delete)
