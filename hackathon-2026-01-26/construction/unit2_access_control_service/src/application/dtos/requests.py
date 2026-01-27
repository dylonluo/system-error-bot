"""Request DTOs - Data transfer objects for incoming requests."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class LoginRequest(BaseModel):
    """Request DTO for login."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Request DTO for token refresh."""
    refresh_token: str = Field(..., min_length=1)


class CreateUserRequest(BaseModel):
    """Request DTO for creating a user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(end_user|administrator)$")


class UpdateUserRequest(BaseModel):
    """Request DTO for updating a user."""
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    role: Optional[str] = Field(None, pattern="^(end_user|administrator)$")


class FilterDocumentsRequest(BaseModel):
    """Request DTO for filtering documents."""
    documents: List[Dict[str, Any]] = Field(..., min_items=0)
