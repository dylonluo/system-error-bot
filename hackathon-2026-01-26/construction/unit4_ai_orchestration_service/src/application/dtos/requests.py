from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class ProcessQueryRequest(BaseModel):
    """Request to process an AI query."""
    query: str = Field(..., min_length=2, max_length=2000)
    conversation_id: UUID
    user_id: UUID
    screenshot_url: Optional[str] = None


class DetectIntentRequest(BaseModel):
    """Request to detect intent from query."""
    query: str = Field(..., min_length=2, max_length=2000)
