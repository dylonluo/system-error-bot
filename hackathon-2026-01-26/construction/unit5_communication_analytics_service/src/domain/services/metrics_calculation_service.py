from typing import List, Dict, Tuple
from ..value_objects import TimePeriod, EventType
from ..repositories import IAnalyticsEventRepository


class MetricsCalculationService:
    """Domain service for calculating analytics metrics."""
    
    def __init__(self, event_repository: IAnalyticsEventRepository):
        self.event_repository = event_repository
    
    def calculate_total_queries(self, time_period: TimePeriod) -> int:
        """Calculate total number of queries submitted."""
        return self.event_repository.count_by_type(
            EventType.QUERY_SUBMITTED,
            time_period.start_date,
            time_period.end_date
        )
    
    def calculate_resolution_rate(self, time_period: TimePeriod) -> float:
        """Calculate resolution rate as percentage."""
        feedback_events = self.event_repository.find_by_type(
            EventType.FEEDBACK_SUBMITTED,
            time_period.start_date,
            time_period.end_date
        )
        
        if not feedback_events:
            return 0.0
        
        solved_count = sum(
            1 for event in feedback_events
            if event.get_metadata('problem_solved') is True
        )
        
        total_count = len(feedback_events)
        return (solved_count / total_count) * 100 if total_count > 0 else 0.0
    
    def calculate_escalation_count(self, time_period: TimePeriod) -> int:
        """Calculate total number of escalations."""
        return self.event_repository.count_by_type(
            EventType.ESCALATION_TRIGGERED,
            time_period.start_date,
            time_period.end_date
        )
    
    def calculate_active_users(self, time_period: TimePeriod) -> int:
        """Calculate number of active users (distinct users with queries)."""
        query_events = self.event_repository.find_by_type(
            EventType.QUERY_SUBMITTED,
            time_period.start_date,
            time_period.end_date
        )
        
        unique_users = set(event.user_id for event in query_events)
        return len(unique_users)
    
    def calculate_top_queries(self, time_period: TimePeriod, limit: int = 10) -> List[Tuple[str, int]]:
        """Calculate top N most frequent queries."""
        query_events = self.event_repository.find_by_type(
            EventType.QUERY_SUBMITTED,
            time_period.start_date,
            time_period.end_date
        )
        
        # Count query occurrences
        query_counts: Dict[str, int] = {}
        for event in query_events:
            query_text = event.get_metadata('query')
            if query_text:
                query_counts[query_text] = query_counts.get(query_text, 0) + 1
        
        # Sort by count descending and return top N
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_queries[:limit]
    
    def recalculate_all_metrics(self, time_period: TimePeriod) -> Dict[str, any]:
        """Recalculate all metrics for the given time period."""
        return {
            'total_queries': self.calculate_total_queries(time_period),
            'resolution_rate': self.calculate_resolution_rate(time_period),
            'escalation_count': self.calculate_escalation_count(time_period),
            'active_users': self.calculate_active_users(time_period),
            'top_queries': self.calculate_top_queries(time_period, 10)
        }
