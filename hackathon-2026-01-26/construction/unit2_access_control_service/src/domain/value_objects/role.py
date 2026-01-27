"""Role Value Object - Represents user roles with permissions."""
from enum import Enum
from typing import List


class RoleType(Enum):
    """Enumeration of available user roles."""
    END_USER = "end_user"
    ADMINISTRATOR = "administrator"


class Role:
    """Value object representing a user role with associated permissions."""
    
    def __init__(self, role_type: RoleType):
        """
        Initialize Role.
        
        Args:
            role_type: Type of role
            
        Raises:
            ValueError: If role_type is not a valid RoleType
        """
        if not isinstance(role_type, RoleType):
            raise ValueError(f"Invalid role type: {role_type}")
        
        self._role_type = role_type
    
    @classmethod
    def end_user(cls) -> 'Role':
        """Create an END_USER role."""
        return cls(RoleType.END_USER)
    
    @classmethod
    def administrator(cls) -> 'Role':
        """Create an ADMINISTRATOR role."""
        return cls(RoleType.ADMINISTRATOR)
    
    @classmethod
    def from_string(cls, value: str) -> 'Role':
        """
        Create Role from string value.
        
        Args:
            value: String representation of role
            
        Returns:
            Role instance
            
        Raises:
            ValueError: If value is not a valid role
        """
        try:
            role_type = RoleType(value.lower())
            return cls(role_type)
        except ValueError:
            raise ValueError(f"Invalid role: {value}")
    
    @property
    def value(self) -> RoleType:
        """Get the role type."""
        return self._role_type
    
    def is_end_user(self) -> bool:
        """Check if this is an END_USER role."""
        return self._role_type == RoleType.END_USER
    
    def is_administrator(self) -> bool:
        """Check if this is an ADMINISTRATOR role."""
        return self._role_type == RoleType.ADMINISTRATOR
    
    def can_access_feature(self, feature: str) -> bool:
        """
        Check if role can access a specific feature.
        
        Args:
            feature: Feature name
            
        Returns:
            True if role can access feature
        """
        # Administrators can access all features
        if self.is_administrator():
            return True
        
        # End users have limited access
        end_user_features = {
            "submit_query",
            "view_own_conversations",
            "provide_feedback",
            "escalate_to_support"
        }
        
        return feature in end_user_features
    
    def get_permissions(self) -> List[str]:
        """
        Get list of permissions for this role.
        
        Returns:
            List of permission strings
        """
        if self.is_administrator():
            return [
                "conversations:read_all",
                "conversations:write",
                "analytics:read",
                "users:read",
                "users:write",
                "users:delete",
                "documents:read_all"
            ]
        else:  # END_USER
            return [
                "conversations:read_own",
                "conversations:write_own",
                "feedback:write",
                "documents:read_basic"
            ]
    
    def __eq__(self, other) -> bool:
        """Check equality with another Role."""
        if not isinstance(other, Role):
            return False
        return self._role_type == other._role_type
    
    def __hash__(self) -> int:
        """Return hash of the Role."""
        return hash(self._role_type)
    
    def __str__(self) -> str:
        """Return string representation."""
        return self._role_type.value
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Role({self._role_type.value})"
