from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class TimePeriod:
    """Value object representing a time period."""
    
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
    
    def get_days(self) -> int:
        """Get the number of days in the period."""
        return (self.end_date - self.start_date).days
    
    def includes(self, timestamp: datetime) -> bool:
        """Check if timestamp is within the period."""
        return self.start_date <= timestamp <= self.end_date
    
    def is_last_30_days(self) -> bool:
        """Check if this is approximately the last 30 days."""
        return 28 <= self.get_days() <= 31
    
    @staticmethod
    def last_30_days() -> 'TimePeriod':
        """Create a TimePeriod for the last 30 days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        return TimePeriod(start_date, end_date)
    
    @staticmethod
    def last_n_days(n: int) -> 'TimePeriod':
        """Create a TimePeriod for the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=n)
        return TimePeriod(start_date, end_date)
    
    def __str__(self):
        return f"{self.start_date.date()} to {self.end_date.date()} ({self.get_days()} days)"
