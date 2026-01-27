"""Session Entity - Represents a user session with JWT tokens."""
from datetime import datetime, timedelta
from typing import Optional

from ..value_objects import SessionId, UserId, JWTToken


class Session:
    """Entity representing a user session."""
    
    def __init__(
        self,
        session_id: SessionId,
        user_id: UserId,
        access_token: JWTToken,
        refresh_token: JWTToken,
        created_at: Optional[datetime] = None,
        last_activity_at: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        is_revoked: bool = False
    ):
        """
        Initialize Session.
        
        Args:
            session_id: Unique session identifier
            user_id: User who owns this session
            access_token: JWT access token
            refresh_token: JWT refresh token
            created_at: When session was created
            last_activity_at: Last activity timestamp
            ip_address: IP address of the session
            user_agent: User agent string
            is_revoked: Whether session is revoked
        """
        self._session_id = session_id
        self._user_id = user_id
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._created_at = created_at or datetime.utcnow()
        self._last_activity_at = last_activity_at or self._created_at
        self._ip_address = ip_address
        self._user_agent = user_agent
        self._is_revoked = is_revoked
    
    @property
    def session_id(self) -> SessionId:
        """Get session ID."""
        return self._session_id
    
    @property
    def user_id(self) -> UserId:
        """Get user ID."""
        return self._user_id
    
    @property
    def access_token(self) -> JWTToken:
        """Get access token."""
        return self._access_token
    
    @property
    def refresh_token(self) -> JWTToken:
        """Get refresh token."""
        return self._refresh_token
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def expires_at(self) -> datetime:
        """Get expiration timestamp (based on refresh token)."""
        return self._refresh_token.expires_at
    
    @property
    def last_activity_at(self) -> datetime:
        """Get last activity timestamp."""
        return self._last_activity_at
    
    @property
    def ip_address(self) -> Optional[str]:
        """Get IP address."""
        return self._ip_address
    
    @property
    def user_agent(self) -> Optional[str]:
        """Get user agent."""
        return self._user_agent
    
    @property
    def is_revoked(self) -> bool:
        """Check if session is revoked."""
        return self._is_revoked
    
    def is_valid(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if session is valid (not expired and not revoked).
        
        Args:
            current_time: Time to check against (defaults to now)
            
        Returns:
            True if session is valid
        """
        if self._is_revoked:
            return False
        
        return not self.is_expired(current_time)
    
    def is_expired(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if session is expired.
        
        Args:
            current_time: Time to check against (defaults to now)
            
        Returns:
            True if expired
        """
        # Session is expired if refresh token is expired
        return self._refresh_token.is_expired(current_time)
    
    def is_access_token_expired(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if access token is expired.
        
        Args:
            current_time: Time to check against (defaults to now)
            
        Returns:
            True if access token is expired
        """
        return self._access_token.is_expired(current_time)
    
    def update_activity(self) -> None:
        """Update last activity timestamp to now."""
        self._last_activity_at = datetime.utcnow()
    
    def revoke(self) -> None:
        """Revoke this session."""
        if self._is_revoked:
            raise ValueError("Session is already revoked")
        
        self._is_revoked = True
    
    def refresh(self, new_access_token: JWTToken, new_refresh_token: JWTToken) -> None:
        """
        Refresh the session with new tokens.
        
        Args:
            new_access_token: New access token
            new_refresh_token: New refresh token
            
        Raises:
            ValueError: If session is revoked or expired
        """
        if self._is_revoked:
            raise ValueError("Cannot refresh revoked session")
        
        if self.is_expired():
            raise ValueError("Cannot refresh expired session")
        
        self._access_token = new_access_token
        self._refresh_token = new_refresh_token
        self.update_activity()
    
    def __eq__(self, other) -> bool:
        """Check equality based on session ID."""
        if not isinstance(other, Session):
            return False
        return self._session_id == other._session_id
    
    def __hash__(self) -> int:
        """Return hash based on session ID."""
        return hash(self._session_id)
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return (f"Session(id={self._session_id}, user_id={self._user_id}, "
                f"revoked={self._is_revoked}, expires_at={self.expires_at})")
