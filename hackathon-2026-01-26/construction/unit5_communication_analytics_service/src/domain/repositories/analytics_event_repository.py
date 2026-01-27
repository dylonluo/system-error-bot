from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from ..aggregates import AnalyticsEvent
from ..value_objects import EventId, EventType


class IAnalyticsEventRepository(ABC):
    """Repository interface for AnalyticsEvent aggregate."""
    
    @abstractmethod
    def save(self, event: AnalyticsEvent) -> None:
        """Save an analytics event."""
        pass
    
    @abstractmethod
    def find_by_id(self, event_id: EventId) -> Optional[AnalyticsEvent]:
        """Find analytics event by ID."""
        pass
    
    @abstractmethod
    def find_by_type(self, event_type: EventType, start_date: datetime, end_date: datetime) -> List[AnalyticsEvent]:
        """Find analytics events by type within date range."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str, start_date: datetime, end_date: datetime) -> List[AnalyticsEvent]:
        """Find analytics events by user ID within date range."""
        pass
    
    @abstractmethod
    def count_by_type(self, event_type: EventType, start_date: datetime, end_date: datetime) -> int:
        """Count analytics events by type within date range."""
        pass
    
    @abstractmethod
    def delete_older_than(self, days: int) -> int:
        """Delete events older than specified days. Returns count deleted."""
        pass
