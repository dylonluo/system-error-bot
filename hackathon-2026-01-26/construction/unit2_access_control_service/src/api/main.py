"""Main FastAPI Application - Access Control Service."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..domain.aggregates import User
from ..domain.value_objects import UserId, Username, Email, Role, AccessLevel
from ..domain.services import AuthenticationService, AuthorizationService, PasswordPolicyService
from ..domain.repositories import IUserRepository, ISessionRepository
from ..infrastructure.repositories import InMemoryUserRepository, InMemorySessionRepository
from ..infrastructure.security import PasswordHasher, JWTProvider, RateLimiter
from ..infrastructure.events import InMemoryEventPublisher
from ..application.services import (
    LoginApplicationService,
    LogoutApplicationService,
    ValidateTokenApplicationService,
    FilterDocumentsApplicationService,
    CreateUserApplicationService,
    GetUserApplicationService,
    UpdateUserApplicationService,
    DeactivateUserApplicationService
)
from .controllers import auth_router, user_router, authz_router
from .middleware import setup_error_handlers
from . import controllers
from . import middleware


def load_config():
    """Load configuration from config.txt file."""
    config = {
        'jwt_secret': 'demo-secret-key-change-in-production',
        'max_failed_attempts': 5,
        'rate_limit_window_minutes': 15,
        'access_token_expiry_seconds': 300,  # 5 minutes
        'refresh_token_expiry_seconds': 3600  # 1 hour
    }
    
    try:
        with open('config.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Convert to appropriate types
                    if key in ['max_failed_attempts', 'rate_limit_window_minutes', 
                              'access_token_expiry_seconds', 'refresh_token_expiry_seconds']:
                        config[key] = int(value)
                    else:
                        config[key] = value
    except FileNotFoundError:
        print("Config file not found, using defaults")
    
    return config


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Access Control Service",
        description="Authentication and Authorization Service",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Load configuration
    config = load_config()
    
    # Initialize infrastructure
    password_hasher = PasswordHasher()
    jwt_provider = JWTProvider(
        secret_key=config['jwt_secret'],
        access_token_expiry_seconds=config['access_token_expiry_seconds'],
        refresh_token_expiry_seconds=config['refresh_token_expiry_seconds']
    )
    rate_limiter = RateLimiter(
        max_attempts=config['max_failed_attempts'],
        window_minutes=config['rate_limit_window_minutes']
    )
    event_publisher = InMemoryEventPublisher()
    
    # Initialize repositories
    user_repository = InMemoryUserRepository()
    session_repository = InMemorySessionRepository()
    
    # Initialize domain services
    password_policy_service = PasswordPolicyService(password_hasher)
    auth_service = AuthenticationService(
        user_repository,
        password_hasher,
        jwt_provider,
        rate_limiter
    )
    authz_service = AuthorizationService(user_repository)
    
    # Initialize application services
    login_service = LoginApplicationService(
        auth_service,
        session_repository,
        event_publisher
    )
    logout_service = LogoutApplicationService(
        session_repository,
        event_publisher
    )
    validate_service = ValidateTokenApplicationService(
        user_repository,
        session_repository,
        jwt_provider
    )
    filter_documents_service = FilterDocumentsApplicationService(authz_service)
    create_user_service = CreateUserApplicationService(
        user_repository,
        password_policy_service,
        authz_service,
        event_publisher
    )
    get_user_service = GetUserApplicationService(user_repository)
    update_user_service = UpdateUserApplicationService(
        user_repository,
        authz_service
    )
    deactivate_user_service = DeactivateUserApplicationService(
        user_repository,
        session_repository,
        authz_service,
        event_publisher
    )
    
    # Set services in controllers
    controllers.authentication_controller.set_services(
        login_service,
        logout_service,
        validate_service
    )
    controllers.user_controller.set_services(
        create_user_service,
        get_user_service,
        update_user_service,
        deactivate_user_service
    )
    controllers.authorization_controller.set_services(filter_documents_service)
    
    # Set up JWT middleware
    middleware.jwt_authentication_middleware.get_current_user = (
        middleware.jwt_authentication_middleware.create_get_current_user(validate_service)
    )
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(authz_router)
    
    # Create initial admin user
    _create_initial_admin(user_repository, password_policy_service)
    
    # Store services in app state for access in demo
    app.state.user_repository = user_repository
    app.state.session_repository = session_repository
    app.state.event_publisher = event_publisher
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "service": "Access Control Service",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app


def _create_initial_admin(
    user_repository: IUserRepository,
    password_policy_service: PasswordPolicyService
):
    """Create initial administrator user if none exists."""
    admin_username = Username("admin")
    
    if not user_repository.exists_by_username(admin_username):
        admin_password = password_policy_service.hash_password("admin123")
        admin_user = User(
            user_id=UserId.generate(),
            username=admin_username,
            password=admin_password,
            email=Email("admin@example.com"),
            role=Role.administrator(),
            access_level=AccessLevel.all(),
            is_active=True
        )
        user_repository.save(admin_user)
        print("✓ Initial admin user created: username='admin', password='admin123'")


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
