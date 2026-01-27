"""Update User Application Service - Updates user information."""
from ...domain.repositories import IUserRepository
from ...domain.services import AuthorizationService
from ...domain.value_objects import UserId, Email, Role, AccessLevel
from ..dtos import UpdateUserRequest, UserResponse


class UpdateUserApplicationService:
    """Application service for updating users."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        authorization_service: AuthorizationService
    ):
        """
        Initialize UpdateUserApplicationService.
        
        Args:
            user_repository: User repository
            authorization_service: Authorization service
        """
        self._user_repository = user_repository
        self._authorization_service = authorization_service
    
    def execute(
        self,
        user_id: str,
        request: UpdateUserRequest,
        updated_by_user_id: str
    ) -> UserResponse:
        """
        Execute user update.
        
        Args:
            user_id: ID of user to update
            request: Update user request
            updated_by_user_id: ID of user performing update (must be admin)
            
        Returns:
            UserResponse with updated user info
            
        Raises:
            ValueError: If validation fails or user not found
        """
        # Check if updater is administrator
        updater_id = UserId(updated_by_user_id)
        if not self._authorization_service.is_administrator(updater_id):
            raise ValueError("Only administrators can update users")
        
        # Find user to update
        user_id_obj = UserId(user_id)
        user = self._user_repository.find_by_id(user_id_obj)
        
        if user is None:
            raise ValueError(f"User not found: {user_id}")
        
        # Update email if provided
        if request.email is not None:
            new_email = Email(request.email)
            # Check if email already exists for another user
            existing_user = self._user_repository.find_by_email(new_email)
            if existing_user is not None and existing_user.user_id != user.user_id:
                raise ValueError(f"Email '{request.email}' already exists")
            user.update_email(new_email)
        
        # Update role if provided
        if request.role is not None:
            new_role = Role.from_string(request.role)
            if new_role.is_administrator():
                new_access_level = AccessLevel.all()
            else:
                new_access_level = AccessLevel.basic()
            user.update_role(new_role, new_access_level)
        
        # Save user
        self._user_repository.save(user)
        
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
