"""Application DTOs - Data Transfer Objects for API communication."""

from .requests import (
    LoginRequest,
    RefreshTokenRequest,
    CreateUserRequest,
    UpdateUserRequest,
    FilterDocumentsRequest,
)
from .responses import (
    LoginResponse,
    UserResponse,
    ValidationResponse,
    FilteredDocumentsResponse,
)

__all__ = [
    'LoginRequest',
    'RefreshTokenRequest',
    'CreateUserRequest',
    'UpdateUserRequest',
    'FilterDocumentsRequest',
    'LoginResponse',
    'UserResponse',
    'ValidationResponse',
    'FilteredDocumentsResponse',
]
