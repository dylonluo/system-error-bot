"""User Aggregate Root - Represents a user with authentication and authorization."""
from datetime import datetime
from typing import List, Optional

from ..value_objects import (
    UserId, Username, Password, Email, Role, AccessLevel, Permission
)
from .session import Session


class User:
    """Aggregate root representing a user."""
    
    def __init__(
        self,
        user_id: UserId,
        username: Username,
        password: Password,
        email: Email,
        role: Role,
        access_level: AccessLevel,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        last_login_at: Optional[datetime] = None
    ):
        """
        Initialize User.
        
        Args:
            user_id: Unique user identifier
            username: Username
            password: Hashed password
            email: Email address
            role: User role
            access_level: Access level for documents
            is_active: Whether user is active
            created_at: Creation timestamp
            last_login_at: Last login timestamp
        """
        self._user_id = user_id
        self._username = username
        self._password = password
        self._email = email
        self._role = role
        self._access_level = access_level
        self._is_active = is_active
        self._created_at = created_at or datetime.utcnow()
        self._last_login_at = last_login_at
        self._sessions: List[Session] = []
    
    @property
    def user_id(self) -> UserId:
        """Get user ID."""
        return self._user_id
    
    @property
    def username(self) -> Username:
        """Get username."""
        return self._username
    
    @property
    def password(self) -> Password:
        """Get password."""
        return self._password
    
    @property
    def email(self) -> Email:
        """Get email."""
        return self._email
    
    @property
    def role(self) -> Role:
        """Get role."""
        return self._role
    
    @property
    def access_level(self) -> AccessLevel:
        """Get access level."""
        return self._access_level
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self._is_active
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def last_login_at(self) -> Optional[datetime]:
        """Get last login timestamp."""
        return self._last_login_at
    
    @property
    def sessions(self) -> List[Session]:
        """Get all sessions."""
        return self._sessions.copy()
    
    def authenticate(self, password_hasher, plain_password: str) -> bool:
        """
        Authenticate user with plain password.
        
        Args:
            password_hasher: Password hasher service
            plain_password: Plain text password to verify
            
        Returns:
            True if authentication successful
            
        Raises:
            ValueError: If user is not active
        """
        if not self._is_active:
            raise ValueError("User is not active")
        
        return password_hasher.verify(plain_password, self._password.hashed_value)
    
    def change_password(self, password_hasher, old_password: str, new_password: str) -> None:
        """
        Change user password.
        
        Args:
            password_hasher: Password hasher service
            old_password: Current password
            new_password: New password
            
        Raises:
            ValueError: If old password is incorrect or new password is invalid
        """
        if not self.authenticate(password_hasher, old_password):
            raise ValueError("Current password is incorrect")
        
        # Validate new password
        Password.validate_plain_password(new_password)
        
        # Hash and set new password
        hashed = password_hasher.hash(new_password)
        self._password = Password(hashed)
        
        # Revoke all existing sessions for security
        for session in self._sessions:
            if not session.is_revoked:
                session.revoke()
    
    def add_session(self, session: Session) -> None:
        """
        Add a session to this user.
        
        Args:
            session: Session to add
            
        Raises:
            ValueError: If session belongs to different user
        """
        if session.user_id != self._user_id:
            raise ValueError("Session does not belong to this user")
        
        self._sessions.append(session)
    
    def update_last_login(self) -> None:
        """Update last login timestamp to now."""
        self._last_login_at = datetime.utcnow()
    
    def has_permission(self, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        user_permissions = self._role.get_permissions()
        permission_str = str(permission)
        return permission_str in user_permissions
    
    def can_access_document(self, document_access_level: str) -> bool:
        """
        Check if user can access a document with given access level.
        
        Args:
            document_access_level: Document's access level (public, basic, advanced)
            
        Returns:
            True if user can access the document
        """
        return self._access_level.can_access(document_access_level)
    
    def deactivate(self) -> None:
        """
        Deactivate this user.
        
        Raises:
            ValueError: If user is already inactive
        """
        if not self._is_active:
            raise ValueError("User is already inactive")
        
        self._is_active = False
        
        # Revoke all sessions
        for session in self._sessions:
            if not session.is_revoked:
                session.revoke()
    
    def activate(self) -> None:
        """
        Activate this user.
        
        Raises:
            ValueError: If user is already active
        """
        if self._is_active:
            raise ValueError("User is already active")
        
        self._is_active = True
    
    def update_email(self, new_email: Email) -> None:
        """
        Update user email.
        
        Args:
            new_email: New email address
        """
        self._email = new_email
    
    def update_role(self, new_role: Role, new_access_level: AccessLevel) -> None:
        """
        Update user role and access level.
        
        Args:
            new_role: New role
            new_access_level: New access level
        """
        self._role = new_role
        self._access_level = new_access_level
    
    def __eq__(self, other) -> bool:
        """Check equality based on user ID."""
        if not isinstance(other, User):
            return False
        return self._user_id == other._user_id
    
    def __hash__(self) -> int:
        """Return hash based on user ID."""
        return hash(self._user_id)
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return (f"User(id={self._user_id}, username={self._username}, "
                f"role={self._role}, active={self._is_active})")
