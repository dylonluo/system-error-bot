"""Session Repository Interface - Contract for session persistence."""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..aggregates import Session
from ..value_objects import SessionId, UserId


class ISessionRepository(ABC):
    """Interface for session repository."""
    
    @abstractmethod
    def save(self, session: Session) -> None:
        """
        Save or update a session.
        
        Args:
            session: Session to save
        """
        pass
    
    @abstractmethod
    def find_by_id(self, session_id: SessionId) -> Optional[Session]:
        """
        Find session by ID.
        
        Args:
            session_id: Session ID to search for
            
        Returns:
            Session if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: UserId) -> List[Session]:
        """
        Find all sessions for a user.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            List of sessions
        """
        pass
    
    @abstractmethod
    def find_by_access_token(self, token: str) -> Optional[Session]:
        """
        Find session by access token.
        
        Args:
            token: Access token to search for
            
        Returns:
            Session if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_expired(self) -> int:
        """
        Delete all expired sessions.
        
        Returns:
            Number of sessions deleted
        """
        pass
    
    @abstractmethod
    def revoke_all_for_user(self, user_id: UserId) -> None:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: User ID
        """
        pass
