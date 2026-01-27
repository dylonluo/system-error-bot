"""Domain Events - Events that represent significant domain occurrences."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..value_objects import UserId, SessionId, Username


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all domain events."""
    occurred_at: datetime
    
    def __post_init__(self):
        """Ensure occurred_at is set."""
        if self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class UserAuthenticated(DomainEvent):
    """Event raised when a user successfully authenticates."""
    user_id: UserId
    session_id: SessionId
    ip_address: Optional[str] = None
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class UserAuthenticationFailed(DomainEvent):
    """Event raised when a user authentication attempt fails."""
    username: Username
    reason: str
    ip_address: Optional[str] = None
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class SessionCreated(DomainEvent):
    """Event raised when a new session is created."""
    session_id: SessionId
    user_id: UserId
    expires_at: datetime
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class SessionExpired(DomainEvent):
    """Event raised when a session expires."""
    session_id: SessionId
    user_id: UserId
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class SessionRevoked(DomainEvent):
    """Event raised when a session is revoked."""
    session_id: SessionId
    user_id: UserId
    reason: str
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class UserCreated(DomainEvent):
    """Event raised when a new user is created."""
    user_id: UserId
    username: Username
    role: str
    created_by: UserId
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())


@dataclass(frozen=True)
class UserDeactivated(DomainEvent):
    """Event raised when a user is deactivated."""
    user_id: UserId
    deactivated_by: UserId
    reason: str
    
    def __post_init__(self):
        """Initialize with current time if not provided."""
        if not hasattr(self, 'occurred_at') or self.occurred_at is None:
            object.__setattr__(self, 'occurred_at', datetime.utcnow())
