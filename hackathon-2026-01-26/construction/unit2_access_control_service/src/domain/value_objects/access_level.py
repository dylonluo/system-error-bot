"""AccessLevel Value Object - Represents document access levels."""
from enum import Enum


class AccessLevelType(Enum):
    """Enumeration of access levels."""
    BASIC = "basic"
    ALL = "all"


class DocumentAccessLevel(Enum):
    """Enumeration of document access levels."""
    PUBLIC = "public"
    BASIC = "basic"
    ADVANCED = "advanced"


class AccessLevel:
    """Value object representing a user's access level for documents."""
    
    def __init__(self, level_type: AccessLevelType):
        """
        Initialize AccessLevel.
        
        Args:
            level_type: Type of access level
            
        Raises:
            ValueError: If level_type is not valid
        """
        if not isinstance(level_type, AccessLevelType):
            raise ValueError(f"Invalid access level type: {level_type}")
        
        self._level_type = level_type
    
    @classmethod
    def basic(cls) -> 'AccessLevel':
        """Create a BASIC access level."""
        return cls(AccessLevelType.BASIC)
    
    @classmethod
    def all(cls) -> 'AccessLevel':
        """Create an ALL access level."""
        return cls(AccessLevelType.ALL)
    
    @classmethod
    def from_string(cls, value: str) -> 'AccessLevel':
        """
        Create AccessLevel from string value.
        
        Args:
            value: String representation of access level
            
        Returns:
            AccessLevel instance
            
        Raises:
            ValueError: If value is not valid
        """
        try:
            level_type = AccessLevelType(value.lower())
            return cls(level_type)
        except ValueError:
            raise ValueError(f"Invalid access level: {value}")
    
    @property
    def value(self) -> AccessLevelType:
        """Get the access level type."""
        return self._level_type
    
    def is_basic(self) -> bool:
        """Check if this is BASIC access level."""
        return self._level_type == AccessLevelType.BASIC
    
    def is_all(self) -> bool:
        """Check if this is ALL access level."""
        return self._level_type == AccessLevelType.ALL
    
    def can_access(self, document_access_level: str) -> bool:
        """
        Check if this access level can access a document.
        
        Args:
            document_access_level: Document's access level (public, basic, advanced)
            
        Returns:
            True if can access the document
        """
        try:
            doc_level = DocumentAccessLevel(document_access_level.lower())
        except ValueError:
            return False
        
        # ALL access can access everything
        if self.is_all():
            return True
        
        # BASIC access can only access public and basic documents
        if self.is_basic():
            return doc_level in [DocumentAccessLevel.PUBLIC, DocumentAccessLevel.BASIC]
        
        return False
    
    def __eq__(self, other) -> bool:
        """Check equality with another AccessLevel."""
        if not isinstance(other, AccessLevel):
            return False
        return self._level_type == other._level_type
    
    def __hash__(self) -> int:
        """Return hash of the AccessLevel."""
        return hash(self._level_type)
    
    def __str__(self) -> str:
        """Return string representation."""
        return self._level_type.value
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"AccessLevel({self._level_type.value})"
