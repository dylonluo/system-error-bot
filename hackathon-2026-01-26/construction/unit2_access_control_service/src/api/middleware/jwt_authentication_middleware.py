"""JWT Authentication Middleware - Validates JWT tokens on requests."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from ...application.services import ValidateTokenApplicationService


security = HTTPBearer()


def create_get_current_user(validate_token_service: ValidateTokenApplicationService):
    """
    Create a dependency function for getting current user from JWT.
    
    Args:
        validate_token_service: Token validation service
        
    Returns:
        Dependency function
    """
    
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """
        Extract and validate JWT token from request.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            User information from token
            
        Raises:
            HTTPException: If token is invalid
        """
        token = credentials.credentials
        
        # Validate token
        result = validate_token_service.execute(token)
        
        if not result.valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.error or "Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "user_id": result.user.id,
            "username": result.user.username,
            "role": result.user.role,
            "access_level": result.user.access_level
        }
    
    return get_current_user


# This will be set in main.py after services are initialized
get_current_user = None
