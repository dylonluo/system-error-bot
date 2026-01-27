from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class SendEscalationEmailRequest(BaseModel):
    """Request DTO for sending escalation email."""
    conversation_id: str = Field(..., description="Conversation ID to escalate")
    user_id: str = Field(..., description="User ID requesting escalation")
    reason: str = Field(..., description="Reason for escalation")
    token: str = Field(..., description="Authentication token")


class RecordEventRequest(BaseModel):
    """Request DTO for recording analytics event."""
    event_type: str = Field(..., description="Type of event")
    user_id: str = Field(..., description="User ID associated with event")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")


class GetDashboardRequest(BaseModel):
    """Request DTO for getting dashboard data."""
    token: str = Field(..., description="Authentication token (admin only)")
    time_period_days: Optional[int] = Field(30, description="Time period in days")
