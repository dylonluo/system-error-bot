"""Login Application Service - Orchestrates user login workflow."""
from typing import Optional

from ...domain.services import AuthenticationService
from ...domain.repositories import ISessionRepository
from ...domain.value_objects import Username
from ...domain.events import UserAuthenticated, SessionCreated, UserAuthenticationFailed
from ...infrastructure.events import InMemoryEventPublisher
from ..dtos import LoginRequest, LoginResponse, UserResponse


class LoginApplicationService:
    """Application service for user login."""
    
    def __init__(
        self,
        auth_service: AuthenticationService,
        session_repository: ISessionRepository,
        event_publisher: InMemoryEventPublisher
    ):
        """
        Initialize LoginApplicationService.
        
        Args:
            auth_service: Authentication domain service
            session_repository: Session repository
            event_publisher: Event publisher
        """
        self._auth_service = auth_service
        self._session_repository = session_repository
        self._event_publisher = event_publisher
    
    def execute(
        self,
        request: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginResponse:
        """
        Execute login workflow.
        
        Args:
            request: Login request
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            LoginResponse with tokens and user info
            
        Raises:
            ValueError: If authentication fails
        """
        # Authenticate user
        username = Username(request.username)
        result = self._auth_service.authenticate(
            username,
            request.password,
            ip_address,
            user_agent
        )
        
        if not result.success:
            # Publish failed authentication event
            self._event_publisher.publish(
                UserAuthenticationFailed(
                    username=username,
                    reason=result.error_message,
                    ip_address=ip_address,
                    occurred_at=None
                )
            )
            raise ValueError(result.error_message)
        
        # Save session
        self._session_repository.save(result.session)
        
        # Publish events
        self._event_publisher.publish(
            UserAuthenticated(
                user_id=result.user.user_id,
                session_id=result.session.session_id,
                ip_address=ip_address,
                occurred_at=None
            )
        )
        
        self._event_publisher.publish(
            SessionCreated(
                session_id=result.session.session_id,
                user_id=result.user.user_id,
                expires_at=result.session.expires_at,
                occurred_at=None
            )
        )
        
        # Build response
        user_response = UserResponse(
            id=str(result.user.user_id),
            username=str(result.user.username),
            email=str(result.user.email),
            role=str(result.user.role),
            access_level=str(result.user.access_level),
            is_active=result.user.is_active,
            created_at=result.user.created_at,
            last_login_at=result.user.last_login_at
        )
        
        return LoginResponse(
            access_token=result.session.access_token.value,
            refresh_token=result.session.refresh_token.value,
            expires_in=result.session.access_token.get_remaining_time().seconds,
            user=user_response
        )
