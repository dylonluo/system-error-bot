"""Create User Application Service - Creates new users."""
from ...domain.aggregates import User
from ...domain.value_objects import UserId, Username, Email, Role, AccessLevel
from ...domain.services import PasswordPolicyService, AuthorizationService
from ...domain.repositories import IUserRepository
from ...domain.events import UserCreated
from ...infrastructure.events import InMemoryEventPublisher
from ..dtos import CreateUserRequest, UserResponse


class CreateUserApplicationService:
    """Application service for creating users."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_policy_service: PasswordPolicyService,
        authorization_service: AuthorizationService,
        event_publisher: InMemoryEventPublisher
    ):
        """
        Initialize CreateUserApplicationService.
        
        Args:
            user_repository: User repository
            password_policy_service: Password policy service
            authorization_service: Authorization service
            event_publisher: Event publisher
        """
        self._user_repository = user_repository
        self._password_policy_service = password_policy_service
        self._authorization_service = authorization_service
        self._event_publisher = event_publisher
    
    def execute(
        self,
        request: CreateUserRequest,
        created_by_user_id: str
    ) -> UserResponse:
        """
        Execute user creation.
        
        Args:
            request: Create user request
            created_by_user_id: ID of user creating this user (must be admin)
            
        Returns:
            UserResponse with created user info
            
        Raises:
            ValueError: If validation fails or user already exists
        """
        # Check if creator is administrator
        creator_id = UserId(created_by_user_id)
        if not self._authorization_service.is_administrator(creator_id):
            raise ValueError("Only administrators can create users")
        
        # Validate username and email uniqueness
        username = Username(request.username)
        email = Email(request.email)
        
        if self._user_repository.exists_by_username(username):
            raise ValueError(f"Username '{request.username}' already exists")
        
        if self._user_repository.exists_by_email(email):
            raise ValueError(f"Email '{request.email}' already exists")
        
        # Hash password
        password = self._password_policy_service.hash_password(request.password)
        
        # Create role and access level
        role = Role.from_string(request.role)
        if role.is_administrator():
            access_level = AccessLevel.all()
        else:
            access_level = AccessLevel.basic()
        
        # Create user
        user = User(
            user_id=UserId.generate(),
            username=username,
            password=password,
            email=email,
            role=role,
            access_level=access_level,
            is_active=True
        )
        
        # Save user
        self._user_repository.save(user)
        
        # Publish event
        self._event_publisher.publish(
            UserCreated(
                user_id=user.user_id,
                username=user.username,
                role=str(user.role),
                created_by=creator_id,
                occurred_at=None
            )
        )
        
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
