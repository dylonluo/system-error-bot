from abc import ABC, abstractmethod
from typing import List, Optional
from ..aggregates import Metric
from ..value_objects import MetricId, MetricType, TimePeriod


class IMetricRepository(ABC):
    """Repository interface for Metric aggregate."""
    
    @abstractmethod
    def save(self, metric: Metric) -> None:
        """Save a metric."""
        pass
    
    @abstractmethod
    def find_by_id(self, metric_id: MetricId) -> Optional[Metric]:
        """Find metric by ID."""
        pass
    
    @abstractmethod
    def find_by_type(self, metric_type: MetricType) -> Optional[Metric]:
        """Find the latest metric by type."""
        pass
    
    @abstractmethod
    def find_by_type_and_period(self, metric_type: MetricType, time_period: TimePeriod) -> Optional[Metric]:
        """Find metric by type and time period."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Metric]:
        """Find all metrics."""
        pass
