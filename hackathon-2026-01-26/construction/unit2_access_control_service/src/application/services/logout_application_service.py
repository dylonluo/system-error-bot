"""Logout Application Service - Orchestrates user logout workflow."""
from ...domain.repositories import ISessionRepository
from ...domain.events import SessionRevoked
from ...infrastructure.events import InMemoryEventPublisher


class LogoutApplicationService:
    """Application service for user logout."""
    
    def __init__(
        self,
        session_repository: ISessionRepository,
        event_publisher: InMemoryEventPublisher
    ):
        """
        Initialize LogoutApplicationService.
        
        Args:
            session_repository: Session repository
            event_publisher: Event publisher
        """
        self._session_repository = session_repository
        self._event_publisher = event_publisher
    
    def execute(self, access_token: str) -> dict:
        """
        Execute logout workflow.
        
        Args:
            access_token: Access token to revoke
            
        Returns:
            Success confirmation
            
        Raises:
            ValueError: If session not found or already revoked
        """
        # Find session by token
        session = self._session_repository.find_by_access_token(access_token)
        
        if session is None:
            raise ValueError("Session not found")
        
        if session.is_revoked:
            raise ValueError("Session already revoked")
        
        # Revoke session
        session.revoke()
        self._session_repository.save(session)
        
        # Publish event
        self._event_publisher.publish(
            SessionRevoked(
                session_id=session.session_id,
                user_id=session.user_id,
                reason="user_logout",
                occurred_at=None
            )
        )
        
        return {"message": "Logout successful"}
