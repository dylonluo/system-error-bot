"""Permission Value Object - Represents a resource-action permission pair."""


class Permission:
    """Value object representing a permission (resource + action)."""
    
    def __init__(self, resource: str, action: str):
        """
        Initialize Permission.
        
        Args:
            resource: Resource name (e.g., "conversations", "users")
            action: Action name (e.g., "read", "write", "delete")
            
        Raises:
            ValueError: If resource or action is empty
        """
        if not resource or not resource.strip():
            raise ValueError("Resource cannot be empty")
        
        if not action or not action.strip():
            raise ValueError("Action cannot be empty")
        
        self._resource = resource.strip().lower()
        self._action = action.strip().lower()
    
    @classmethod
    def from_string(cls, permission_string: str) -> 'Permission':
        """
        Create Permission from string format "resource:action".
        
        Args:
            permission_string: Permission in format "resource:action"
            
        Returns:
            Permission instance
            
        Raises:
            ValueError: If format is invalid
        """
        if ':' not in permission_string:
            raise ValueError(f"Invalid permission format: {permission_string}. Expected 'resource:action'")
        
        parts = permission_string.split(':', 1)
        return cls(parts[0], parts[1])
    
    @property
    def resource(self) -> str:
        """Get the resource."""
        return self._resource
    
    @property
    def action(self) -> str:
        """Get the action."""
        return self._action
    
    def matches(self, resource: str, action: str) -> bool:
        """
        Check if this permission matches the given resource and action.
        
        Args:
            resource: Resource to check
            action: Action to check
            
        Returns:
            True if matches
        """
        return (self._resource == resource.lower() and 
                self._action == action.lower())
    
    def __eq__(self, other) -> bool:
        """Check equality with another Permission."""
        if not isinstance(other, Permission):
            return False
        return self._resource == other._resource and self._action == other._action
    
    def __hash__(self) -> int:
        """Return hash of the Permission."""
        return hash((self._resource, self._action))
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"{self._resource}:{self._action}"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"Permission('{self._resource}', '{self._action}')"
