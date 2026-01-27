"""Mock Access Control client."""

from typing import Any, Dict, List

from ...domain.ports.access_control_client import IAccessControlClient


class MockAccessControlClient(IAccessControlClient):
    """Mock implementation of Access Control client."""

    def __init__(self):
        # Mock users database
        self._users = {
            "user-123": {"user_id": "user-123", "username": "end_user", "role": "End User", "access_level": "basic"},
            "admin-456": {"user_id": "admin-456", "username": "admin_user", "role": "Administrator", "access_level": "all"},
        }

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate user token and return user info."""
        # Mock token validation - extract user_id from token
        # In real implementation, this would decode JWT
        if token.startswith("Bearer "):
            token = token[7:]

        # Simple mock: token is the user_id
        user = self._users.get(token)
        if not user:
            raise ValueError("Invalid token")

        return user

    def filter_documents(self, documents: List, user_id: str) -> List:
        """Filter documents based on user access level."""
        user = self._users.get(user_id)
        if not user:
            return []

        user_access_level = user["access_level"]
        filtered = []

        for doc in documents:
            if doc.is_accessible_by(user_access_level):
                filtered.append(doc)

        return filtered
