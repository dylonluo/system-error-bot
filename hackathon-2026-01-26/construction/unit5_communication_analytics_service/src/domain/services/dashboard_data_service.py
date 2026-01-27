from typing import Dict, List, Any
from ..value_objects import TimePeriod, MetricType
from ..repositories import IMetricRepository


class DashboardDataService:
    """Domain service for preparing dashboard data."""
    
    def __init__(self, metric_repository: IMetricRepository):
        self.metric_repository = metric_repository
    
    def get_dashboard_data(self, time_period: TimePeriod = None) -> Dict[str, Any]:
        """Get dashboard data for the specified time period."""
        if time_period is None:
            time_period = TimePeriod.last_30_days()
        
        metrics = self.get_metrics_by_type([
            MetricType.TOTAL_QUERIES,
            MetricType.RESOLUTION_RATE,
            MetricType.ESCALATION_COUNT,
            MetricType.ACTIVE_USERS,
            MetricType.TOP_QUERIES
        ])
        
        return self.format_for_display(metrics, time_period)
    
    def get_metrics_by_type(self, metric_types: List[MetricType]) -> Dict[MetricType, Any]:
        """Get metrics by type."""
        metrics = {}
        for metric_type in metric_types:
            metric = self.metric_repository.find_by_type(metric_type)
            if metric:
                metrics[metric_type] = metric
        return metrics
    
    def format_for_display(self, metrics: Dict[MetricType, Any], time_period: TimePeriod) -> Dict[str, Any]:
        """Format metrics for dashboard display."""
        dashboard_data = {
            'period': {
                'start_date': time_period.start_date.isoformat(),
                'end_date': time_period.end_date.isoformat(),
                'days': time_period.get_days()
            },
            'metrics': {}
        }
        
        for metric_type, metric in metrics.items():
            dashboard_data['metrics'][str(metric_type)] = {
                'value': self._format_metric_value(metric.value),
                'trend': metric.get_trend(),
                'calculated_at': metric.calculated_at.isoformat()
            }
        
        return dashboard_data
    
    def _format_metric_value(self, metric_value) -> Any:
        """Format metric value for display."""
        try:
            # Try to get as appropriate type
            if metric_value.unit == 'count':
                return metric_value.as_integer()
            elif metric_value.unit == 'percentage':
                return round(metric_value.as_float(), 2)
            elif metric_value.unit == 'list':
                return metric_value.as_list()
            else:
                return str(metric_value.value)
        except:
            return str(metric_value.value)
