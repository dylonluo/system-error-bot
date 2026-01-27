from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class EscalationEmailResponse(BaseModel):
    """Response DTO for escalation email."""
    email_id: str = Field(..., description="Email ID")
    status: str = Field(..., description="Email status")
    sent_to: str = Field(..., description="Recipient email address")
    sent_at: Optional[str] = Field(None, description="Timestamp when sent")
    message: str = Field(..., description="Response message")


class EventRecordedResponse(BaseModel):
    """Response DTO for recorded event."""
    event_id: str = Field(..., description="Event ID")
    recorded: bool = Field(True, description="Whether event was recorded")
    message: str = Field("Event recorded successfully", description="Response message")


class DashboardDataResponse(BaseModel):
    """Response DTO for dashboard data."""
    period: Dict[str, Any] = Field(..., description="Time period information")
    metrics: Dict[str, Any] = Field(..., description="Calculated metrics")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Generation timestamp")


class ErrorResponse(BaseModel):
    """Response DTO for errors."""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Error timestamp")
