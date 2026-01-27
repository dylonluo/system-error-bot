"""Authorization Service - Enforces access control and permissions."""
from typing import List, Dict, Any

from ..aggregates import User
from ..value_objects import UserId, Permission
from ..repositories import IUserRepository


class AuthorizationService:
    """Domain service for authorization and access control."""
    
    def __init__(self, user_repository: IUserRepository):
        """
        Initialize AuthorizationService.
        
        Args:
            user_repository: User repository
        """
        self._user_repository = user_repository
    
    def can_access_resource(
        self,
        user_id: UserId,
        resource: str,
        action: str
    ) -> bool:
        """
        Check if user can access a resource with specific action.
        
        Args:
            user_id: User ID
            resource: Resource name
            action: Action name
            
        Returns:
            True if user has permission
        """
        user = self._user_repository.find_by_id(user_id)
        if user is None or not user.is_active:
            return False
        
        permission = Permission(resource, action)
        return user.has_permission(permission)
    
    def filter_documents_by_access(
        self,
        documents: List[Dict[str, Any]],
        user_id: UserId
    ) -> List[Dict[str, Any]]:
        """
        Filter documents based on user's access level.
        
        Args:
            documents: List of documents with 'access_level' field
            user_id: User ID
            
        Returns:
            Filtered list of documents user can access
        """
        user = self._user_repository.find_by_id(user_id)
        if user is None or not user.is_active:
            return []
        
        filtered = []
        for doc in documents:
            access_level = doc.get('access_level', 'advanced')
            if user.can_access_document(access_level):
                filtered.append(doc)
        
        return filtered
    
    def has_permission(self, user_id: UserId, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user_id: User ID
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        user = self._user_repository.find_by_id(user_id)
        if user is None or not user.is_active:
            return False
        
        return user.has_permission(permission)
    
    def is_administrator(self, user_id: UserId) -> bool:
        """
        Check if user is an administrator.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user is administrator
        """
        user = self._user_repository.find_by_id(user_id)
        if user is None or not user.is_active:
            return False
        
        return user.role.is_administrator()
