"""Access Control Context client (mock)"""
from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass
class User:
    """User model"""
    user_id: UUID
    username: str
    email: str
    role: str


class AccessControlClient:
    """Mock client for Access Control Context"""

    def validate_token(self, token: str) -> User:
        """Validate JWT token and return user"""
        # Mock implementation - accept any token
        if not token:
            raise ValueError("Token is required")

        # Return mock user
        return User(
            user_id=UUID('12345678-1234-5678-1234-567812345678'),
            username='demo_user',
            email='demo@example.com',
            role='user'
        )

    def get_user_profile(self, user_id: UUID) -> User:
        """Get user profile"""
        # Mock implementation
        return User(
            user_id=user_id,
            username='demo_user',
            email='demo@example.com',
            role='user'
        )
