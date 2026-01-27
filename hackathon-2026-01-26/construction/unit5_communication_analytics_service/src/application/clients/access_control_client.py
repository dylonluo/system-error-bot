from typing import Dict, Any, Optional


class AccessControlClient:
    """Mock client for Access Control Context."""
    
    def __init__(self):
        # Mock users database
        self._users = {
            'user-123': {
                'user_id': 'user-123',
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'role': 'end_user'
            },
            'admin-456': {
                'user_id': 'admin-456',
                'name': 'Admin User',
                'email': 'admin@example.com',
                'role': 'administrator'
            }
        }
        
        # Mock tokens
        self._valid_tokens = {
            'token-user-123': 'user-123',
            'token-admin-456': 'admin-456'
        }
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate authentication token and return user."""
        user_id = self._valid_tokens.get(token)
        if user_id:
            return self._users.get(user_id)
        return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile by user ID."""
        return self._users.get(user_id)
    
    def is_admin(self, user: Dict[str, Any]) -> bool:
        """Check if user is an administrator."""
        return user.get('role') == 'administrator'
