"""User Repository Interface - Contract for user persistence."""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..aggregates import User
from ..value_objects import UserId, Username, Email


class IUserRepository(ABC):
    """Interface for user repository."""
    
    @abstractmethod
    def save(self, user: User) -> None:
        """
        Save or update a user.
        
        Args:
            user: User to save
        """
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """
        Find user by ID.
        
        Args:
            user_id: User ID to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_username(self, username: Username) -> Optional[User]:
        """
        Find user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """
        Find user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User if found, None otherwise
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """
        Find all users with pagination.
        
        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            List of users
        """
        pass
    
    @abstractmethod
    def exists_by_username(self, username: Username) -> bool:
        """
        Check if username exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists
        """
        pass
    
    @abstractmethod
    def exists_by_email(self, email: Email) -> bool:
        """
        Check if email exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists
        """
        pass
    
    @abstractmethod
    def delete(self, user_id: UserId) -> None:
        """
        Delete a user.
        
        Args:
            user_id: ID of user to delete
        """
        pass
