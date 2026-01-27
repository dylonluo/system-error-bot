from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from ..value_objects import MetricId, MetricType, MetricValue, TimePeriod
from ..entities import MetricDataPoint


@dataclass
class Metric:
    """Aggregate root representing a calculated metric."""
    
    metric_id: MetricId
    metric_type: MetricType
    value: MetricValue
    time_period: TimePeriod
    calculated_at: datetime = field(default_factory=datetime.now)
    data_points: List[MetricDataPoint] = field(default_factory=list)
    
    def calculate(self) -> None:
        """Calculate the metric (placeholder for calculation logic)."""
        # Calculation logic would be implemented by domain services
        self.calculated_at = datetime.now()
    
    def add_data_point(self, value: float, timestamp: datetime) -> None:
        """Add a data point to the metric."""
        data_point = MetricDataPoint(
            metric_id=str(self.metric_id),
            value=value,
            timestamp=timestamp
        )
        self.data_points.append(data_point)
    
    def get_value(self) -> MetricValue:
        """Get the metric value."""
        return self.value
    
    def get_trend(self) -> str:
        """Get the trend based on data points."""
        if len(self.data_points) < 2:
            return "stable"
        
        # Simple trend calculation: compare first and last data points
        first_value = self.data_points[0].get_value()
        last_value = self.data_points[-1].get_value()
        
        if last_value > first_value * 1.1:  # 10% increase
            return "increasing"
        elif last_value < first_value * 0.9:  # 10% decrease
            return "decreasing"
        else:
            return "stable"
    
    def __eq__(self, other):
        if not isinstance(other, Metric):
            return False
        return self.metric_id == other.metric_id
    
    def __hash__(self):
        return hash(self.metric_id)
    
    def __str__(self):
        return f"Metric({self.metric_type}, {self.value}, trend={self.get_trend()})"
