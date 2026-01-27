from dataclasses import dataclass
from datetime import datetime
from ..value_objects import EmailId, EventId, MetricId, MetricType, MetricValue


@dataclass
class EscalationEmailSent:
    """Domain event: Escalation email was successfully sent."""
    email_id: EmailId
    conversation_id: str
    user_id: str
    sent_at: datetime
    
    def __str__(self):
        return f"EscalationEmailSent({self.email_id}, {self.sent_at.isoformat()})"


@dataclass
class EscalationEmailFailed:
    """Domain event: Escalation email failed to send."""
    email_id: EmailId
    conversation_id: str
    failure_reason: str
    retry_count: int
    failed_at: datetime
    
    def __str__(self):
        return f"EscalationEmailFailed({self.email_id}, retry={self.retry_count})"


@dataclass
class AnalyticsEventRecorded:
    """Domain event: Analytics event was recorded."""
    event_id: EventId
    event_type: str
    occurred_at: datetime
    
    def __str__(self):
        return f"AnalyticsEventRecorded({self.event_id}, {self.event_type})"


@dataclass
class MetricCalculated:
    """Domain event: Metric was calculated or updated."""
    metric_id: MetricId
    metric_type: MetricType
    value: MetricValue
    calculated_at: datetime
    
    def __str__(self):
        return f"MetricCalculated({self.metric_type}, {self.value})"
