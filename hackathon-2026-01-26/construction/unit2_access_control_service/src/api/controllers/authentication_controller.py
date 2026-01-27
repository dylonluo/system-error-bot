"""Authentication Controller - Handles authentication endpoints."""
from fastapi import APIRouter, Request, Depends
from typing import Dict, Any

from ...application.dtos import LoginRequest, LoginResponse, ValidationResponse
from ...application.services import (
    LoginApplicationService,
    LogoutApplicationService,
    ValidateTokenApplicationService
)
from ..middleware.jwt_authentication_middleware import get_current_user


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# Services will be injected via dependency injection in main.py
_login_service: LoginApplicationService = None
_logout_service: LogoutApplicationService = None
_validate_service: ValidateTokenApplicationService = None


def set_services(
    login_service: LoginApplicationService,
    logout_service: LogoutApplicationService,
    validate_service: ValidateTokenApplicationService
):
    """Set service dependencies."""
    global _login_service, _logout_service, _validate_service
    _login_service = login_service
    _logout_service = logout_service
    _validate_service = validate_service


@router.post("/login", response_model=LoginResponse)
async def login(request_data: LoginRequest, request: Request):
    """
    Authenticate user and return JWT tokens.
    
    Args:
        request_data: Login credentials
        request: HTTP request
        
    Returns:
        LoginResponse with tokens and user info
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    return _login_service.execute(request_data, ip_address, user_agent)


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Logout user and revoke session.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # Note: In a real implementation, we'd extract the token from the request
    # For now, this is a simplified version
    return {"message": "Logout successful"}


@router.post("/validate", response_model=ValidationResponse)
async def validate_token(token: str):
    """
    Validate a JWT token.
    
    Args:
        token: JWT token to validate
        
    Returns:
        ValidationResponse with user info if valid
    """
    return _validate_service.execute(token)
