"""Get User Application Service - Retrieves user information."""
from ...domain.repositories import IUserRepository
from ...domain.value_objects import UserId
from ..dtos import UserResponse


class GetUserApplicationService:
    """Application service for retrieving user information."""
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize GetUserApplicationService.
        
        Args:
            user_repository: User repository
        """
        self._user_repository = user_repository
    
    def execute(self, user_id: str) -> UserResponse:
        """
        Execute user retrieval.
        
        Args:
            user_id: User ID string
            
        Returns:
            UserResponse with user info
            
        Raises:
            ValueError: If user not found
        """
        # Find user
        user_id_obj = UserId(user_id)
        user = self._user_repository.find_by_id(user_id_obj)
        
        if user is None:
            raise ValueError(f"User not found: {user_id}")
        
        # Build response
        return UserResponse(
            id=str(user.user_id),
            username=str(user.username),
            email=str(user.email),
            role=str(user.role),
            access_level=str(user.access_level),
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at
        )
