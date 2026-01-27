"""Demo Script - Demonstrates Access Control Service functionality."""
import sys
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from src.domain.aggregates import User
from src.domain.value_objects import UserId, Username, Email, Role, AccessLevel
from src.domain.services import AuthenticationService, AuthorizationService, PasswordPolicyService
from src.infrastructure.repositories import InMemoryUserRepository, InMemorySessionRepository
from src.infrastructure.security import PasswordHasher, JWTProvider, RateLimiter
from src.infrastructure.events import InMemoryEventPublisher
from src.application.services import (
    LoginApplicationService,
    CreateUserApplicationService,
    FilterDocumentsApplicationService,
    ValidateTokenApplicationService,
    DeactivateUserApplicationService
)
from src.application.dtos import LoginRequest, CreateUserRequest, FilterDocumentsRequest


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"✓ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"✗ {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ {message}")


def main():
    """Run the demo."""
    print_section("Access Control Service - Demo")
    
    # Initialize infrastructure
    print_info("Initializing services...")
    password_hasher = PasswordHasher()
    jwt_provider = JWTProvider(
        secret_key="demo-secret-key",
        access_token_expiry_seconds=300,  # 5 minutes
        refresh_token_expiry_seconds=3600  # 1 hour
    )
    rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)
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
    create_user_service = CreateUserApplicationService(
        user_repository,
        password_policy_service,
        authz_service,
        event_publisher
    )
    filter_documents_service = FilterDocumentsApplicationService(authz_service)
    validate_token_service = ValidateTokenApplicationService(
        user_repository,
        session_repository,
        jwt_provider
    )
    deactivate_user_service = DeactivateUserApplicationService(
        user_repository,
        session_repository,
        authz_service,
        event_publisher
    )
    
    print_success("Services initialized")
    
    # Demo 1: Create initial admin user
    print_section("Demo 1: Create Initial Admin User")
    
    admin_password = password_policy_service.hash_password("admin123")
    admin_user = User(
        user_id=UserId.generate(),
        username=Username("admin"),
        password=admin_password,
        email=Email("admin@example.com"),
        role=Role.administrator(),
        access_level=AccessLevel.all(),
        is_active=True
    )
    user_repository.save(admin_user)
    print_success(f"Admin user created: {admin_user.username}")
    print_info(f"  - User ID: {admin_user.user_id}")
    print_info(f"  - Role: {admin_user.role}")
    print_info(f"  - Access Level: {admin_user.access_level}")
    
    # Demo 2: Admin login
    print_section("Demo 2: Admin Login")
    
    login_request = LoginRequest(username="admin", password="admin123")
    login_response = login_service.execute(login_request, "127.0.0.1", "Demo Client")
    
    print_success("Admin logged in successfully")
    print_info(f"  - Access Token: {login_response.access_token[:50]}...")
    print_info(f"  - Expires In: {login_response.expires_in} seconds")
    print_info(f"  - User: {login_response.user.username} ({login_response.user.role})")
    
    admin_token = login_response.access_token
    admin_user_id = login_response.user.id
    
    # Demo 3: Token validation
    print_section("Demo 3: Token Validation")
    
    validation_response = validate_token_service.execute(admin_token)
    print_success(f"Token is valid: {validation_response.valid}")
    if validation_response.user:
        print_info(f"  - User: {validation_response.user.username}")
        print_info(f"  - Role: {validation_response.user.role}")
    
    # Demo 4: Create end user
    print_section("Demo 4: Create End User")
    
    create_user_request = CreateUserRequest(
        username="john_doe",
        email="john@example.com",
        password="password123",
        role="end_user"
    )
    
    user_response = create_user_service.execute(create_user_request, admin_user_id)
    print_success(f"End user created: {user_response.username}")
    print_info(f"  - User ID: {user_response.id}")
    print_info(f"  - Email: {user_response.email}")
    print_info(f"  - Role: {user_response.role}")
    print_info(f"  - Access Level: {user_response.access_level}")
    
    # Demo 5: End user login
    print_section("Demo 5: End User Login")
    
    user_login_request = LoginRequest(username="john_doe", password="password123")
    user_login_response = login_service.execute(user_login_request, "127.0.0.1", "Demo Client")
    
    print_success("End user logged in successfully")
    print_info(f"  - User: {user_login_response.user.username}")
    print_info(f"  - Access Level: {user_login_response.user.access_level}")
    
    user_token = user_login_response.access_token
    user_user_id = user_login_response.user.id
    
    # Demo 6: Document filtering - Admin (ALL access)
    print_section("Demo 6: Document Filtering - Admin (ALL Access)")
    
    documents = [
        {"id": "doc1", "title": "Public Document", "access_level": "public"},
        {"id": "doc2", "title": "Basic Document", "access_level": "basic"},
        {"id": "doc3", "title": "Advanced Document", "access_level": "advanced"},
    ]
    
    filter_request = FilterDocumentsRequest(documents=documents)
    admin_filtered = filter_documents_service.execute(filter_request, admin_user_id)
    
    print_success(f"Admin can access {len(admin_filtered.filtered_documents)}/{admin_filtered.total_count} documents")
    for doc in admin_filtered.filtered_documents:
        print_info(f"  - {doc['title']} ({doc['access_level']})")
    
    # Demo 7: Document filtering - End User (BASIC access)
    print_section("Demo 7: Document Filtering - End User (BASIC Access)")
    
    user_filtered = filter_documents_service.execute(filter_request, user_user_id)
    
    print_success(f"End user can access {len(user_filtered.filtered_documents)}/{user_filtered.total_count} documents")
    print_info(f"  - Removed: {user_filtered.removed_count} documents")
    for doc in user_filtered.filtered_documents:
        print_info(f"  - {doc['title']} ({doc['access_level']})")
    
    # Demo 8: Failed login attempts (rate limiting)
    print_section("Demo 8: Rate Limiting - Failed Login Attempts")
    
    print_info("Attempting 6 failed logins to trigger rate limit...")
    for i in range(6):
        try:
            bad_request = LoginRequest(username="john_doe", password="wrongpassword")
            login_service.execute(bad_request)
        except ValueError as e:
            if i < 5:
                print_info(f"  Attempt {i+1}: Failed (expected)")
            else:
                print_success(f"  Attempt {i+1}: Rate limit triggered!")
                print_info(f"    Error: {str(e)}")
    
    # Demo 9: Deactivate user
    print_section("Demo 9: Deactivate User")
    
    result = deactivate_user_service.execute(user_user_id, admin_user_id, "demo_deactivation")
    print_success(result["message"])
    
    # Try to login with deactivated user
    try:
        deactivated_login = LoginRequest(username="john_doe", password="password123")
        login_service.execute(deactivated_login)
        print_error("Deactivated user was able to login (unexpected!)")
    except ValueError as e:
        print_success("Deactivated user cannot login")
        print_info(f"  Error: {str(e)}")
    
    # Demo 10: Event summary
    print_section("Demo 10: Published Events Summary")
    
    events = event_publisher.get_events()
    print_success(f"Total events published: {len(events)}")
    
    event_counts = {}
    for event in events:
        event_type = event.__class__.__name__
        event_counts[event_type] = event_counts.get(event_type, 0) + 1
    
    for event_type, count in event_counts.items():
        print_info(f"  - {event_type}: {count}")
    
    # Final summary
    print_section("Demo Complete!")
    print_success("All features demonstrated successfully")
    print_info(f"Total users created: {len(user_repository.find_all())}")
    print_info(f"Total sessions created: {len(session_repository._sessions)}")
    print_info(f"Total events published: {event_publisher.count()}")
    
    print("\n" + "="*70)
    print("  To run the API server:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run server: python -m src.api.main")
    print("  3. Visit: http://localhost:8000/docs")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
