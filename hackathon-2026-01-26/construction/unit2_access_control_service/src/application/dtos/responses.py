"""Response DTOs - Data transfer objects for outgoing responses."""
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class UserResponse(BaseModel):
    """Response DTO for user information."""
    id: str
    username: str
    email: str
    role: str
    access_level: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Response DTO for login."""
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserResponse


class ValidationResponse(BaseModel):
    """Response DTO for token validation."""
    valid: bool
    user: Optional[UserResponse] = None
    error: Optional[str] = None


class FilteredDocumentsResponse(BaseModel):
    """Response DTO for filtered documents."""
    filtered_documents: List[Dict[str, Any]]
    removed_count: int
    total_count: int
