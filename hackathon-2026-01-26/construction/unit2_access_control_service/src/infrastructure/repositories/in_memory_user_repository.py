"""In-Memory User Repository - In-memory implementation for testing/demo."""
from typing import Dict, List, Optional

from ...domain.aggregates import User
from ...domain.value_objects import UserId, Username, Email
from ...domain.repositories import IUserRepository


class InMemoryUserRepository(IUserRepository):
    """In-memory implementation of user repository."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._users: Dict[str, User] = {}  # Key: user_id string
        self._username_index: Dict[str, str] = {}  # Key: lowercase username, Value: user_id
        self._email_index: Dict[str, str] = {}  # Key: lowercase email, Value: user_id
    
    def save(self, user: User) -> None:
        """Save or update a user."""
        user_id_str = str(user.user_id)
        
        # Update indexes
        self._username_index[user.username.to_lower()] = user_id_str
        self._email_index[user.email.to_lower()] = user_id_str
        
        # Save user
        self._users[user_id_str] = user
    
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        return self._users.get(str(user_id))
    
    def find_by_username(self, username: Username) -> Optional[User]:
        """Find user by username (case-insensitive)."""
        user_id_str = self._username_index.get(username.to_lower())
        if user_id_str is None:
            return None
        return self._users.get(user_id_str)
    
    def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email (case-insensitive)."""
        user_id_str = self._email_index.get(email.to_lower())
        if user_id_str is None:
            return None
        return self._users.get(user_id_str)
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Find all users with pagination."""
        all_users = list(self._users.values())
        return all_users[offset:offset + limit]
    
    def exists_by_username(self, username: Username) -> bool:
        """Check if username exists."""
        return username.to_lower() in self._username_index
    
    def exists_by_email(self, email: Email) -> bool:
        """Check if email exists."""
        return email.to_lower() in self._email_index
    
    def delete(self, user_id: UserId) -> None:
        """Delete a user."""
        user_id_str = str(user_id)
        user = self._users.get(user_id_str)
        
        if user is not None:
            # Remove from indexes
            self._username_index.pop(user.username.to_lower(), None)
            self._email_index.pop(user.email.to_lower(), None)
            
            # Remove user
            del self._users[user_id_str]
    
    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._users.clear()
        self._username_index.clear()
        self._email_index.clear()
