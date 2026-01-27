import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MetricDataPoint:
    """Entity representing a single data point in a metric."""
    
    data_point_id: str
    metric_id: str
    value: float
    timestamp: datetime
    
    def __init__(self, metric_id: str, value: float, timestamp: datetime, data_point_id: str = None):
        self.data_point_id = data_point_id or str(uuid.uuid4())
        self.metric_id = metric_id
        self.value = value
        self.timestamp = timestamp
    
    def get_value(self) -> float:
        """Get the data point value."""
        return self.value
    
    def get_timestamp(self) -> datetime:
        """Get the data point timestamp."""
        return self.timestamp
    
    def __eq__(self, other):
        if not isinstance(other, MetricDataPoint):
            return False
        return self.data_point_id == other.data_point_id
    
    def __hash__(self):
        return hash(self.data_point_id)
    
    def __str__(self):
        return f"DataPoint({self.value} at {self.timestamp.isoformat()})"
