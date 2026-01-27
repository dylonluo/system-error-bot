from typing import List, Optional, Dict
from ...domain.aggregates import Metric
from ...domain.value_objects import MetricId, MetricType, TimePeriod
from ...domain.repositories import IMetricRepository


class InMemoryMetricRepository(IMetricRepository):
    """In-memory implementation of Metric repository."""
    
    def __init__(self):
        self._metrics: Dict[str, Metric] = {}
        self._metrics_by_type: Dict[MetricType, Metric] = {}
    
    def save(self, metric: Metric) -> None:
        """Save a metric."""
        self._metrics[str(metric.metric_id)] = metric
        # Keep track of latest metric by type
        self._metrics_by_type[metric.metric_type] = metric
    
    def find_by_id(self, metric_id: MetricId) -> Optional[Metric]:
        """Find metric by ID."""
        return self._metrics.get(str(metric_id))
    
    def find_by_type(self, metric_type: MetricType) -> Optional[Metric]:
        """Find the latest metric by type."""
        return self._metrics_by_type.get(metric_type)
    
    def find_by_type_and_period(self, metric_type: MetricType, time_period: TimePeriod) -> Optional[Metric]:
        """Find metric by type and time period."""
        for metric in self._metrics.values():
            if (metric.metric_type == metric_type and
                metric.time_period.start_date == time_period.start_date and
                metric.time_period.end_date == time_period.end_date):
                return metric
        return None
    
    def find_all(self) -> List[Metric]:
        """Find all metrics."""
        return list(self._metrics.values())
