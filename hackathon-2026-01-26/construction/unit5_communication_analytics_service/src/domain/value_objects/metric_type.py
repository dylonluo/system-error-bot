from enum import Enum


class MetricType(Enum):
    """Types of analytics metrics."""
    TOTAL_QUERIES = "total_queries"
    RESOLUTION_RATE = "resolution_rate"
    ESCALATION_COUNT = "escalation_count"
    ACTIVE_USERS = "active_users"
    TOP_QUERIES = "top_queries"
    
    def is_total_queries(self) -> bool:
        return self == MetricType.TOTAL_QUERIES
    
    def is_resolution_rate(self) -> bool:
        return self == MetricType.RESOLUTION_RATE
    
    def is_escalation_count(self) -> bool:
        return self == MetricType.ESCALATION_COUNT
    
    def is_active_users(self) -> bool:
        return self == MetricType.ACTIVE_USERS
    
    def is_top_queries(self) -> bool:
        return self == MetricType.TOP_QUERIES
    
    def __str__(self):
        return self.value
