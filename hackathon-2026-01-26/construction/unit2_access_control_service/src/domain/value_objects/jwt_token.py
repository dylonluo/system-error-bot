"""JWTToken Value Object - Represents a JWT token with expiration."""
from datetime import datetime, timedelta
from typing import Optional


class JWTToken:
    """Value object representing a JWT token with metadata."""
    
    def __init__(self, value: str, issued_at: datetime, expires_at: datetime):
        """
        Initialize JWTToken.
        
        Args:
            value: JWT token string
            issued_at: When token was issued
            expires_at: When token expires
            
        Raises:
            ValueError: If token is empty or expiration is invalid
        """
        if not value or not value.strip():
            raise ValueError("JWT token cannot be empty")
        
        if expires_at <= issued_at:
            raise ValueError("Token expiration must be after issuance")
        
        self._value = value.strip()
        self._issued_at = issued_at
        self._expires_at = expires_at
    
    @classmethod
    def create(cls, value: str, expires_in_seconds: int) -> 'JWTToken':
        """
        Create a new JWTToken with expiration from now.
        
        Args:
            value: JWT token string
            expires_in_seconds: Seconds until expiration
            
        Returns:
            JWTToken instance
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=expires_in_seconds)
        return cls(value, now, expires_at)
    
    @property
    def value(self) -> str:
        """Get the token value."""
        return self._value
    
    @property
    def issued_at(self) -> datetime:
        """Get the issuance time."""
        return self._issued_at
    
    @property
    def expires_at(self) -> datetime:
        """Get the expiration time."""
        return self._expires_at
    
    def is_expired(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if token is expired.
        
        Args:
            current_time: Time to check against (defaults to now)
            
        Returns:
            True if expired
        """
        if current_time is None:
            current_time = datetime.utcnow()
        return current_time >= self._expires_at
    
    def is_valid(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if token is valid (not expired).
        
        Args:
            current_time: Time to check against (defaults to now)
            
        Returns:
            True if valid
        """
        return not self.is_expired(current_time)
    
    def get_remaining_time(self, current_time: Optional[datetime] = None) -> timedelta:
        """
        Get remaining time until expiration.
        
        Args:
            current_time: Time to check against (defaults to now)
            
        Returns:
            Timedelta of remaining time (negative if expired)
        """
        if current_time is None:
            current_time = datetime.utcnow()
        return self._expires_at - current_time
    
    def __eq__(self, other) -> bool:
        """Check equality with another JWTToken."""
        if not isinstance(other, JWTToken):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Return hash of the JWTToken."""
        return hash(self._value)
    
    def __str__(self) -> str:
        """Return string representation (token value)."""
        return self._value
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"JWTToken(expires_at={self._expires_at.isoformat()})"
