"""User Controller - Handles user management endpoints."""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from ...application.dtos import CreateUserRequest, UpdateUserRequest, UserResponse
from ...application.services import (
    CreateUserApplicationService,
    GetUserApplicationService,
    UpdateUserApplicationService,
    DeactivateUserApplicationService
)
from ..middleware.jwt_authentication_middleware import get_current_user


router = APIRouter(prefix="/api/v1/auth/users", tags=["users"])

# Services will be injected via dependency injection in main.py
_create_user_service: CreateUserApplicationService = None
_get_user_service: GetUserApplicationService = None
_update_user_service: UpdateUserApplicationService = None
_deactivate_user_service: DeactivateUserApplicationService = None


def set_services(
    create_user_service: CreateUserApplicationService,
    get_user_service: GetUserApplicationService,
    update_user_service: UpdateUserApplicationService,
    deactivate_user_service: DeactivateUserApplicationService
):
    """Set service dependencies."""
    global _create_user_service, _get_user_service, _update_user_service, _deactivate_user_service
    _create_user_service = create_user_service
    _get_user_service = get_user_service
    _update_user_service = update_user_service
    _deactivate_user_service = deactivate_user_service


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        current_user: Current authenticated user
        
    Returns:
        UserResponse with user info
    """
    return _get_user_service.execute(user_id)


@router.post("", response_model=UserResponse)
async def create_user(
    request_data: CreateUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new user (admin only).
    
    Args:
        request_data: User creation data
        current_user: Current authenticated user (must be admin)
        
    Returns:
        UserResponse with created user info
    """
    return _create_user_service.execute(request_data, current_user["user_id"])


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request_data: UpdateUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user (admin only).
    
    Args:
        user_id: User ID to update
        request_data: Update data
        current_user: Current authenticated user (must be admin)
        
    Returns:
        UserResponse with updated user info
    """
    return _update_user_service.execute(user_id, request_data, current_user["user_id"])


@router.delete("/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Deactivate user (admin only).
    
    Args:
        user_id: User ID to deactivate
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Success message
    """
    return _deactivate_user_service.execute(user_id, current_user["user_id"])
