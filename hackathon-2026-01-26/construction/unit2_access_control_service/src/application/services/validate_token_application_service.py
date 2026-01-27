"""Validate Token Application Service - Validates JWT tokens."""
from ...domain.repositories import IUserRepository, ISessionRepository
from ...domain.value_objects import UserId
from ..dtos import ValidationResponse, UserResponse


class ValidateTokenApplicationService:
    """Application service for token validation."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
        jwt_provider
    ):
        """
        Initialize ValidateTokenApplicationService.
        
        Args:
            user_repository: User repository
            session_repository: Session repository
            jwt_provider: JWT provider
        """
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._jwt_provider = jwt_provider
    
    def execute(self, token: str) -> ValidationResponse:
        """
        Execute token validation.
        
        Args:
            token: JWT token to validate
            
        Returns:
            ValidationResponse with user info if valid
        """
        # Validate token
        is_valid, payload = self._jwt_provider.validate_token(token)
        
        if not is_valid or payload is None:
            return ValidationResponse(
                valid=False,
                error="Invalid or expired token"
            )
        
        # Get user ID from payload
        user_id = UserId(payload['user_id'])
        
        # Check if session exists and is valid
        session = self._session_repository.find_by_access_token(token)
        if session is None or session.is_revoked:
            return ValidationResponse(
                valid=False,
                error="Session not found or revoked"
            )
        
        # Get user
        user = self._user_repository.find_by_id(user_id)
        if user is None or not user.is_active:
            return ValidationResponse(
                valid=False,
                error="User not found or inactive"
            )
        
        # Update session activity
        session.update_activity()
        self._session_repository.save(session)
        
        # Build response
        user_response = UserResponse(
            id=str(user.user_id),
            username=str(user.username),
            email=str(user.email),
            role=str(user.role),
            access_level=str(user.access_level),
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
        
        return ValidationResponse(
            valid=True,
            user=user_response
        )
