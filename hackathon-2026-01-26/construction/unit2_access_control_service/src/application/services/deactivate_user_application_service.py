"""Deactivate User Application Service - Deactivates users."""
from ...domain.repositories import IUserRepository, ISessionRepository
from ...domain.services import AuthorizationService
from ...domain.value_objects import UserId
from ...domain.events import UserDeactivated
from ...infrastructure.events import InMemoryEventPublisher


class DeactivateUserApplicationService:
    """Application service for deactivating users."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        session_repository: ISessionRepository,
        authorization_service: AuthorizationService,
        event_publisher: InMemoryEventPublisher
    ):
        """
        Initialize DeactivateUserApplicationService.
        
        Args:
            user_repository: User repository
            session_repository: Session repository
            authorization_service: Authorization service
            event_publisher: Event publisher
        """
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._authorization_service = authorization_service
        self._event_publisher = event_publisher
    
    def execute(
        self,
        user_id: str,
        deactivated_by_user_id: str,
        reason: str = "admin_action"
    ) -> dict:
        """
        Execute user deactivation.
        
        Args:
            user_id: ID of user to deactivate
            deactivated_by_user_id: ID of user performing deactivation (must be admin)
            reason: Reason for deactivation
            
        Returns:
            Success confirmation
            
        Raises:
            ValueError: If validation fails or user not found
        """
        # Check if deactivator is administrator
        deactivator_id = UserId(deactivated_by_user_id)
        if not self._authorization_service.is_administrator(deactivator_id):
            raise ValueError("Only administrators can deactivate users")
        
        # Find user to deactivate
        user_id_obj = UserId(user_id)
        user = self._user_repository.find_by_id(user_id_obj)
        
        if user is None:
            raise ValueError(f"User not found: {user_id}")
        
        # Deactivate user (this also revokes all sessions)
        user.deactivate()
        
        # Save user
        self._user_repository.save(user)
        
        # Revoke all sessions in repository
        self._session_repository.revoke_all_for_user(user_id_obj)
        
        # Publish event
        self._event_publisher.publish(
            UserDeactivated(
                user_id=user.user_id,
                deactivated_by=deactivator_id,
                reason=reason,
                occurred_at=None
            )
        )
        
        return {"message": f"User {user_id} deactivated successfully"}
